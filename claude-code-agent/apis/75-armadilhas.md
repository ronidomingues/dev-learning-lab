# 75 · Armadilhas, mitos e más práticas

`Nível: todos` · `Atualizado: 11/08/2026`

O que dá errado, por que dá errado, e **por que essas práticas persistem** apesar de todo
mundo saber que são ruins. A última parte é a mais importante: uma má prática que sobrevive
20 anos está resolvendo um problema real para alguém.

---

## 1. Armadilhas de design

### 1.1 A API que espelha o banco de dados

**O que é.** `GET /tabela_usuarios` devolvendo as colunas com os nomes do banco, incluindo
`fk_status_id`, `dt_cad` e `flag_ativo`.

**Por que dá errado.** A estrutura do banco é uma decisão de **armazenamento**, otimizada
para escrita, índice e normalização. Expô-la torna cada refatoração interna uma mudança
quebradora. O cliente também precisa reimplementar a sua regra de negócio, porque a API
expõe **estado**, não **intenção**.

**Por que persiste.** Porque é o caminho de menor esforço: um gerador de CRUD produz isso em
minutos, e no dia 1 funciona. O custo aparece no ano 2, quando quem gerou já saiu.

**Correção.** Modele o domínio. Reifique ações como recursos.
Ver [14-design-de-api-rest.md](14-design-de-api-rest.md) §3.

### 1.2 Verbos na URL

```http
❌ POST /criarUsuario · GET /getUsuarioPorId?id=42 · POST /deletarPedido
```

**Por que dá errado.** Você perde a semântica do HTTP inteira: cache, idempotência,
retentativa segura, e a capacidade de qualquer intermediário entender o tráfego.

**Por que persiste.** Porque o programador pensa em **funções**, não em recursos. E porque,
se o domínio é realmente orientado a ação, REST **é** desconfortável — nesse caso o problema
não é o programador, é a escolha do estilo. Ver [15](15-estilos-e-protocolos.md) §1.

### 1.3 Tudo em `POST`

**Por que dá errado.** Nada é cacheável, nada é retentável com segurança, e o significado da
operação fica escondido no corpo.

**Por que persiste.** Duas razões legítimas e uma preguiçosa: (a) `GET` tem limite de tamanho
de URL, e filtros complexos não cabem; (b) parâmetros em URL vazam para log de acesso; (c) é
mais fácil ter um só caminho de código.

**Correção.** `GET` para leitura. Quando o filtro não couber, é aceitável um
`POST /recursos/consultas` — **documentado como exceção**, não como padrão.

### 1.4 Ids sequenciais expostos

Vaza volume de negócio e permite enumeração. Ver
[14-design-de-api-rest.md](14-design-de-api-rest.md) §11.

**Por que persiste.** Porque o banco já gera `AUTO_INCREMENT` e trocar por UUID exige
migração, além de deixar as URLs feias. É uma decisão que parece estética e é de segurança.

### 1.5 Paginação por offset em coleção que cresce

Duplica e pula registros; custa O(offset) no banco.
**Por que persiste:** é o que o ORM faz por padrão (`LIMIT/OFFSET`), e o bug só aparece com
tráfego concorrente — que não existe em desenvolvimento.

### 1.6 Aninhamento profundo

`/clientes/9/pedidos/42/itens/7/produto/3/avaliacoes` acopla o cliente à hierarquia inteira.
Se qualquer nível mudar de relação, a URL mente.

---

## 2. Armadilhas de HTTP

### 2.1 `200 OK` com erro no corpo

```json
HTTP/1.1 200 OK
{"sucesso": false, "erro": "saldo insuficiente"}
```

**Por que dá errado.** Todo painel de monitoramento, alerta, proxy e cliente HTTP vê
sucesso. A taxa de erro fica em zero enquanto os usuários reclamam. E cada cliente precisa
inspecionar o corpo para saber se deu certo — o que ninguém lembra de fazer em todo lugar.

**Por que persiste.** Três razões reais: (a) alguns frameworks antigos e alguns clientes
móveis tratavam `4xx` de forma inconveniente; (b) times que vieram de SOAP, onde tudo é
`200` com fault no envelope; (c) a crença de que "erro de negócio não é erro de HTTP".

**Sobre (c):** é um argumento com alguma base. `422` é literalmente
"*Unprocessable Content*" — feito para isso. Use-o.

### 2.2 `500` para erro do cliente

```json
HTTP/1.1 500 Internal Server Error
{"erro": "CPF inválido"}
```
Faz o cliente retentar (é `5xx`), aciona o seu alerta de madrugada e polui a métrica de
erro do servidor. **Use `422`.**

**Por que persiste.** Porque um `catch` genérico devolvendo `500` é uma linha, e classificar
o erro exige pensar.

### 2.3 Ignorar `Retry-After`

Retentar imediatamente após `429` é a forma mais rápida de ser bloqueado — e agrava o
problema que o rate limit deveria conter.

### 2.4 `no-cache` achando que é `no-store`

`no-cache` **permite guardar**, exige revalidar. Quem quer proibir precisa de `no-store`.
Essa confusão já vazou dado sensível para cache de proxy corporativo.

### 2.5 Esquecer `Vary: Authorization`

Numa resposta cacheável e autenticada, sem `Vary`, uma CDN entrega os dados de um usuário
para outro. **É uma das piores falhas possíveis e é fácil de cometer**, porque o código
parece certo e o bug só aparece com cache em produção.

### 2.6 `GET` que altera estado

`GET /usuarios/42/desativar` será executado pelo pré-carregador do navegador, pelo antivírus
corporativo e pelo robô de indexação — **sem ninguém clicar**. Já derrubou dados de empresas
grandes.

---

## 3. Armadilhas de integração

### 3.1 Sem idempotência

**Por que persiste.** Porque em ambiente de teste a rede é perfeita e nunca duplica. O bug
aparece em produção, sob concorrência ou instabilidade — e como duplicata não gera erro,
ninguém percebe até o cliente reclamar da cobrança dobrada.

### 3.2 Idempotência só no código

`if (jaExiste) return;` seguido de `insert` tem uma janela. **Concorrência encontra
janelas.** A garantia precisa estar numa constraint do armazenamento. Ver
[60-teoria-avancada.md](60-teoria-avancada.md) §4.

**Por que persiste.** Porque passa nos testes, que são sequenciais.

### 3.3 Sem timeout

Uma requisição pendurada segura conexão, thread e memória indefinidamente. Com concorrência,
esgota o pool e derruba o **seu** serviço por causa da lentidão do outro.

**Por que persiste.** Porque quase toda biblioteca HTTP tem timeout **infinito** por padrão.
É o padrão errado, herdado, em praticamente todo ecossistema.

### 3.4 Retry sem circuit breaker

Quando a dependência cai, cada requisição vira 3 ou 5. Você **multiplica** a carga sobre um
sistema que já está caindo, exatamente quando ele precisa de folga.

### 3.5 Retry sem jitter

Mil clientes que falharam no mesmo instante retentam no mesmo instante. *Thundering herd*:
o servidor se recupera, é derrubado de novo, e o ciclo se repete.

### 3.6 Webhook sem verificação de assinatura

Sua URL é pública. **Qualquer um pode fazer `POST` nela.** Sem assinatura, qualquer pessoa
na internet confirma pagamentos no seu sistema.

**Por que persiste.** Porque funciona nos testes — você mesmo faz o POST e ele é aceito. A
falha é de omissão, e omissão não gera erro.

### 3.7 Webhook sem deduplicação

Entrega é *at-least-once*. Duplicata **é normal**, não exceção. Sem deduplicar por id, o
mesmo pedido é processado duas vezes.

### 3.8 Assinar o corpo desserializado

Fazer `JSON.parse` e depois `JSON.stringify` muda a ordem das chaves e os espaços. A
assinatura **nunca** vai bater, e o erro é incompreensível. **Assine o corpo bruto, em
bytes.** É o erro nº 1 de quem implementa webhook.

---

## 4. Armadilhas de segurança

| Armadilha | Consequência |
|---|---|
| Token na URL | vaza em log de acesso, `Referer`, histórico do navegador |
| Segredo no código | vai para o Git, e o histórico do Git é **para sempre** |
| Confiar na validação do cliente | qualquer um chama a API direto com curl |
| Esconder o botão como "autorização" | a autorização é do servidor |
| `Access-Control-Allow-Origin: *` com credenciais | a especificação proíbe, e por bom motivo |
| Stack trace na resposta | reconhecimento gratuito: versões, caminhos, estrutura |
| Mensagem que enumera usuários | "e-mail não cadastrado" confirma quais existem |
| Comparar segredo com `===` | vaza por *timing* |
| JWT sem fixar o algoritmo | `alg: none` ou confusão HS/RS = **token forjado** |
| JWT de 24 h | passe livre de 24 h para quem roubar; não há revogação |
| Rate limit por IP com autenticação | clientes atrás do mesmo NAT compartilham a cota |
| Ambiente de homologação exposto | com dados de produção e sem autenticação (OWASP API9) |

---

## 5. Mitos

| Mito | Realidade |
|---|---|
| "REST é o jeito certo de fazer API" | É *um* estilo, com trade-offs. Ver [19](19-como-escolher.md) |
| "Nossa API é RESTful" | Quase sempre significa nível 2 de Richardson, sem hipermídia |
| "GraphQL substitui REST" | Resolve outros problemas; cria seis novos |
| "gRPC é sempre mais rápido" | Em rede lenta com payload pequeno, a diferença some |
| "Microsserviços resolvem acoplamento" | Trocam acoplamento de código por acoplamento de rede, que é pior de depurar |
| "HTTPS resolve segurança" | Protege o transporte. Não protege contra BOLA, injeção ou lógica errada |
| "JWT é mais seguro que sessão" | É mais **escalável**. Revogação é pior |
| "Versionar é fácil, faço depois" | O primeiro consumidor congela o contrato |
| "Documentação eu escrevo no fim" | Diverge em semanas; documentação errada é pior que nenhuma |
| "O cliente vai ler a documentação" | Ele copia o exemplo. Faça o exemplo estar certo |
| "Se funciona no Postman, funciona" | O Postman não tem CORS, nem a rede do cliente |
| "200 significa que deu certo" | Significa que o HTTP funcionou |
| "Cache é otimização prematura" | É a diferença entre 1 e 100 servidores |
| "Rate limit é para quando crescer" | O primeiro bot chega antes do primeiro cliente |
| "É interno, não precisa de auth" | A rede interna não é confiável. Ver falácia nº 4 |
| "Vou usar UUID, então está seguro" | Id opaco é defesa em profundidade, não substitui autorização |

---

## 6. Armadilhas de projeto e organização

### 6.1 Microsserviços desde o dia 1

**Por que dá errado.** Você paga latência, falha parcial, versionamento, tracing distribuído
e complexidade operacional **antes** de ter o problema que os microsserviços resolvem
(times independentes escalando em paralelo).

**Por que persiste.** Porque é o que se lê em blog de empresa grande — que tem o problema. E
porque "monólito" virou palavra pejorativa.

**Correção.** Monólito **modular**, com fronteiras claras internas. Quando um módulo precisar
de escala ou ciclo de release próprio, extraia-o. As fronteiras internas viram APIs sem
reescrever o domínio.

### 6.2 Uma API por tabela

Gerada automaticamente do banco. Ver §1.1 — é o mesmo erro, industrializado.

### 6.3 Nenhum dono do contrato

Cada time adiciona campo do seu jeito; em dois anos há três convenções de data, dois estilos
de nomenclatura e quatro formatos de erro na mesma API.

**Correção.** Um linter de contrato **no CI** (Spectral com as regras do time). Convenção
que não é verificada é sugestão.

### 6.4 Contrato escrito depois do código

Vira transcrição do que já existe, não decisão de produto. Perde-se a chance de perceber que
o desenho está errado **antes** de implementá-lo, que é quando corrigir é barato.

### 6.5 Nunca desligar versão antiga

Acumula até que manter custe mais que reescrever. Ver
[18-operacao-e-ciclo-de-vida.md](18-operacao-e-ciclo-de-vida.md) §10 para o porquê do
incentivo.

---

## 7. As dez frases que precedem um incidente

1. "É interno, não precisa de autenticação."
2. "Depois eu coloco o timeout."
3. "Esse campo ninguém usa, pode remover."
4. "Funciona no meu Postman."
5. "É só um `POST`, não precisa de idempotência."
6. "Vamos versionar quando precisar."
7. "O rate limit fica para a fase 2."
8. "Coloca `200` e o erro no corpo, é mais fácil para o front."
9. "A documentação está no código."
10. "Ninguém vai adivinhar essa URL."

---

## 8. Checklist de revisão de API

Use em toda revisão de código que toque a API.

**Semântica**
- [ ] Verbos corretos; `GET` não altera nada.
- [ ] Status corretos (`201`+`Location`, `204`, `404`, `409`, `422`, `429`).
- [ ] `405` com `Allow`; `429`/`503` com `Retry-After`.
- [ ] `HEAD` funciona onde `GET` funciona.
- [ ] `Cache-Control` explícito; `Vary: Authorization` onde couber.

**Contrato**
- [ ] Mudança refletida no `openapi.yaml`, no mesmo PR.
- [ ] `oasdiff` não acusa quebra não intencional.
- [ ] Erros novos documentados, com `type` estável.
- [ ] Exemplos atualizados.

**Robustez**
- [ ] `Idempotency-Key` em `POST` que muda estado relevante.
- [ ] Timeout em toda chamada externa.
- [ ] Retry só para erro retentável, com jitter.
- [ ] Limites: corpo, página, lote, profundidade.
- [ ] Paginação por cursor em coleção que cresce.

**Segurança**
- [ ] Autorização por **dono do objeto**, filtrando na consulta.
- [ ] Allowlist de campos na escrita.
- [ ] Nenhum segredo em código, URL ou log.
- [ ] Erro sem stack trace, SQL ou caminho.
- [ ] Entrada validada por schema, com `additionalProperties: false`.

**Operação**
- [ ] Log com request-id, sem dado sensível.
- [ ] Métrica da rota nova; alerta se for crítica.
- [ ] Teste do caminho de erro, não só do feliz.
- [ ] Teste de acesso cruzado (usuário A → recurso de B).

---

## Autoteste

1. Por que a API que espelha o banco parece boa no dia 1 e ruim no ano 2?
2. Dê as três razões pelas quais `200` com erro no corpo persiste. Qual delas tem alguma base?
3. Por que `500 {"erro": "CPF inválido"}` custa caro em três frentes distintas?
4. O que acontece se você esquecer `Vary: Authorization`? Por que é difícil de detectar?
5. Por que a falta de idempotência só aparece em produção?
6. Por que "sem timeout" persiste em tantos sistemas?
7. Por que retry sem circuit breaker piora a falha? E sem jitter?
8. Qual é o erro nº 1 de quem implementa recepção de webhook?
9. Escolha três mitos e explique por que cada um é falso.
10. Por que "microsserviços desde o dia 1" é caro? Qual é a alternativa?
11. Escolha quatro itens do checklist e descreva o incidente que cada um previne.
