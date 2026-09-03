# 70 · Prática — dez laboratórios

`Nível: todos` · `Atualizado: 11/08/2026`

Cada laboratório tem **objetivo**, **passos** e **critério de aprovação verificável**.
Não pule o critério — é ele que distingue "eu li" de "eu sei".

Ambiente: [03-instalacao.md](03-instalacao.md). Os labs 1–3 precisam só de `curl`.

| # | Laboratório | Trilha | Tempo |
|---|---|---|---|
| 1 | Engenharia reversa de uma API real | consumo | 1 h |
| 2 | Cliente robusto no terminal | consumo | 1,5 h |
| 3 | Diagnóstico: por que está lento? | consumo | 1 h |
| 4 | Sua primeira API, do zero | construção | 2 h |
| 5 | Contrato primeiro (design-first) | construção | 2 h |
| 6 | Idempotência e concorrência | construção | 2,5 h |
| 7 | Autenticação e autorização | construção | 2,5 h |
| 8 | Tempo real: SSE e webhook | construção | 2 h |
| 9 | Quebrar a própria API (segurança) | avançado | 2 h |
| 10 | Evolução sem quebrar | avançado | 2 h |

---

## Lab 1 — Engenharia reversa de uma API real

**Objetivo.** Aprender a ler uma API que você não escreveu, sem documentação.

**Passos.**

1. Abra um site que você usa (banco, e-commerce, rede social) no navegador.
2. `F12` → aba **Network** → filtre por **Fetch/XHR**.
3. Navegue, faça uma busca, abra um item. Observe as chamadas.
4. Escolha **uma** chamada interessante e responda por escrito:
   - Qual o método e a URL? Ela segue convenção de recurso ou é RPC?
   - Que cabeçalhos vão? Como é a autenticação?
   - Qual o formato da resposta? Envelopada ou array puro?
   - Como é a paginação? Offset, cursor, ou nenhuma?
   - Há `Cache-Control`? `ETag`?
   - Que nível de Richardson essa API atinge?
5. Botão direito → **Copy → Copy as cURL**. Cole no terminal e execute.
6. **Modifique** a chamada: mude um parâmetro, remova o token, mande um valor inválido.
   Anote os códigos de status.
7. Repita com uma API pública documentada (GitHub, ViaCEP, IBGE) e **compare**.

**Critério de aprovação.**
- [ ] Você reproduziu uma chamada do site no terminal, com sucesso.
- [ ] Você classificou a API no modelo de Richardson, com justificativa.
- [ ] Você provocou ao menos três códigos de erro diferentes.
- [ ] Você consegue apontar **uma** coisa que essa API faz bem e **uma** mal.

**Por que importa.** Na vida real, metade das APIs com que você trabalha não tem
documentação boa. Ler tráfego é a habilidade que resolve isso — e é a mais rápida de
adquirir.

---

## Lab 2 — Cliente robusto no terminal

**Objetivo.** Escrever um consumidor que sobrevive a erro, lentidão e limite de cota.

**Passos.**

1. Escolha uma API pública com paginação (ex.: `api.github.com/repos/{org}/{repo}/tags`).
2. Escreva um script que percorre **todas** as páginas seguindo o cabeçalho `Link`.
3. Adicione **cache com ETag**: se nada mudou, não rebaixe.
4. Adicione **timeout** e **retentativa com backoff exponencial e jitter**.
5. Trate `429` respeitando `Retry-After`.
6. Adicione um **circuit breaker**: após 5 falhas seguidas, pare por 1 minuto.
7. **Teste as falhas de propósito.** Se não tiver internet estável, use o servidor local do
   Exemplo 3 de [06-exemplos.md](06-exemplos.md) §3, que erra sob demanda.
8. Meça: quantas requisições você fez com e sem cache?

**Critério de aprovação.**
- [ ] O script percorre todas as páginas sem duplicar nem pular item.
- [ ] Na segunda execução, ele faz menos requisições (cache funcionando).
- [ ] Um `503` provoca retentativa; um `404` **não** provoca.
- [ ] Um `429` faz o script esperar o tempo do `Retry-After`.
- [ ] Após N falhas, o circuito abre e as chamadas param **sem** ir à rede.

**Por que importa.** Este é o código que separa integração de brinquedo de integração de
produção. É também o Exemplo 3 e 4 de [06-exemplos.md](06-exemplos.md) aplicado por você.

---

## Lab 3 — Diagnóstico: por que está lento?

**Objetivo.** Diagnosticar latência com evidência, não com palpite.

**Passos.**

1. Crie o alias de medição:
   ```bash
   alias curltime="curl -s -o /dev/null -w 'dns:%{time_namelookup} tcp:%{time_connect} tls:%{time_appconnect} ttfb:%{time_starttransfer} total:%{time_total} http/%{http_version}\n'"
   ```
2. Meça **cinco** APIs diferentes: uma nacional, uma internacional, uma atrás de CDN, uma
   sua local, e uma que você suspeita ser lenta.
3. Para cada uma, identifique **onde** o tempo foi: DNS, TCP, TLS, ou o servidor.
4. Compare `--http1.1` com `--http2` na mesma URL. Meça 10 vezes cada e compare a mediana.
5. Meça a **segunda** chamada seguida (conexão reaproveitada) contra a primeira.
6. Escreva um parágrafo por API: onde está o gargalo e o que o reduziria.

**Critério de aprovação.**
- [ ] Você tem uma tabela com os cinco tempos, para as cinco APIs.
- [ ] Você identificou pelo menos um caso em que o gargalo **não** é o servidor.
- [ ] Você mediu a diferença entre a primeira chamada e a segunda, e sabe explicá-la.
- [ ] Você usou **mediana**, não uma medição única.

**Por que importa.** "A API está lenta" não é diagnóstico. Número é. E o gargalo
frequentemente é DNS ou TLS, não o código do servidor — o que muda completamente a ação.

---

## Lab 4 — Sua primeira API, do zero

**Objetivo.** Construir uma API com semântica HTTP correta.

**Cenário.** Cadastro de **tarefas** (`id`, `titulo`, `concluida`, `prazo`, `criada_em`).

**Passos.**

1. Implemente, na linguagem que preferir:
   - `GET /tarefas` com paginação e filtro por `concluida`
   - `GET /tarefas/{id}`
   - `POST /tarefas` → `201` + `Location`
   - `PATCH /tarefas/{id}`
   - `DELETE /tarefas/{id}` → `204`, **idempotente**
2. Devolva os status corretos: `400`, `404`, `405` + `Allow`, `415`, `422`.
3. Erros no formato **RFC 9457**, com `type` estável.
4. Valide a entrada com schema; devolva **todos** os erros de uma vez.
5. Implemente `HEAD` (é de graça se você fizer certo).
6. `Cache-Control` explícito em toda resposta; `ETag` no recurso individual.
7. Escreva testes cobrindo **cada** código de status.

**Critério de aprovação.**
- [ ] `DELETE` duas vezes devolve `204` nas duas.
- [ ] `GET` num id inexistente devolve `404` com `application/problem+json`.
- [ ] `POST` com dois campos inválidos devolve **os dois** erros.
- [ ] Método errado devolve `405` **com o cabeçalho `Allow`**.
- [ ] `HEAD` devolve os mesmos cabeçalhos do `GET`, sem corpo.
- [ ] `If-None-Match` com o ETag correto devolve `304`.
- [ ] Existe um teste para cada status acima.

**Por que importa.** É a base. Use [07-projeto-modelo/](07-projeto-modelo/README.md) como
referência — **depois** de tentar sozinho.

---

## Lab 5 — Contrato primeiro

**Objetivo.** Sentir a diferença entre design-first e code-first.

**Passos.**

1. **Antes de escrever código**, escreva o `openapi.yaml` da API do Lab 4.
2. Valide: `npx @stoplight/spectral-cli lint openapi.yaml`. Corrija todos os erros.
3. Suba um **mock** a partir do contrato: `npx @stoplight/prism-cli mock openapi.yaml`.
4. Escreva um **cliente** que consome o mock, **antes** de o servidor existir.
5. Agora implemente o servidor real e aponte o cliente para ele. **Nada deveria mudar.**
6. Gere a documentação: `npx @redocly/cli build-docs openapi.yaml -o docs.html`.
7. Gere tipos: `npx openapi-typescript openapi.yaml -o tipos.d.ts`.
8. **Mude o contrato de propósito**, quebrando compatibilidade (remova um campo). Rode:
   `npx oasdiff breaking openapi-antigo.yaml openapi.yaml`.
9. Escreva um teste que valida **toda resposta** da sua suíte contra o schema do contrato.

**Critério de aprovação.**
- [ ] O Spectral passa sem erros.
- [ ] O cliente funcionou contra o mock **antes** de o servidor existir.
- [ ] Trocar mock por servidor real não exigiu mudança no cliente.
- [ ] O `oasdiff` **detectou** a mudança quebradora que você introduziu.
- [ ] O teste de validação de resposta pega uma divergência que você introduza de propósito.

**Por que importa.** Trabalhar em paralelo (front e back) e detectar quebra automaticamente
são os dois maiores retornos de ter contrato. Você só acredita depois de sentir.

---

## Lab 6 — Idempotência e concorrência

**Objetivo.** Implementar as duas garantias que separam API séria de API de tutorial.

**Passos.**

1. Adicione `POST /tarefas` com `Idempotency-Key` obrigatório.
2. Implemente: chave nova processa; chave repetida com mesmo corpo devolve a resposta
   original; corpo diferente devolve `422`.
3. **Prove** que funciona: dispare **10 requisições em paralelo** com a mesma chave.
   ```bash
   CH=$(cat /proc/sys/kernel/random/uuid)
   for i in $(seq 1 10); do
     curl -s -X POST localhost:3000/tarefas -H 'Content-Type: application/json' \
       -H "Idempotency-Key: $CH" -d '{"titulo":"teste"}' &
   done; wait
   ```
   **Quantas tarefas foram criadas?** Se for mais de uma, você tem uma condição de corrida.
4. Corrija usando uma **constraint de unicidade** no armazenamento, não um `if`.
5. Adicione `ETag` + `If-Match` obrigatório no `PATCH`.
6. Simule o *lost update*: dois clientes leem, um escreve, o outro tenta com o ETag velho.
7. Verifique: `428` sem `If-Match`, `412` com ETag velho.

**Critério de aprovação.**
- [ ] 10 requisições paralelas com a mesma chave criam **exatamente uma** tarefa.
- [ ] A garantia está numa constraint do armazenamento, e você consegue explicar por quê.
- [ ] Chave reusada com corpo diferente devolve `422`.
- [ ] `PATCH` sem `If-Match` devolve `428`; com ETag velho, `412`.
- [ ] Você demonstrou que a alteração do primeiro cliente **não** foi perdida.

**Por que importa.** O passo 3 é o coração deste laboratório. A maioria das implementações de
idempotência passa nos testes sequenciais e falha em paralelo — e falha silenciosamente, em
produção, com dinheiro real. Ver [60-teoria-avancada.md](60-teoria-avancada.md) §4.

---

## Lab 7 — Autenticação e autorização

**Objetivo.** Implementar as duas, separadamente, e provar que a autorização funciona.

**Passos.**

1. Adicione autenticação por Bearer token com dois usuários e escopos distintos.
2. Adicione `401` (sem token) com `WWW-Authenticate`, e `403` (sem escopo).
3. Faça as tarefas **pertencerem** a um usuário.
4. **Escreva primeiro o teste de BOLA:** o usuário A tenta ler a tarefa do usuário B.
   Ele deve receber `404` (não `403` — não revele a existência).
5. **Faça o teste falhar**, implementando ingenuamente (`findById` sem checar dono).
   Veja o vazamento acontecer.
6. Corrija **filtrando na consulta** (`WHERE id = ? AND dono = ?`), não com um `if`.
7. Tente **mass assignment**: mande `{"dono_id": "outro"}` no `PATCH`. Deve ser recusado.
8. Adicione rate limit com `429` + `Retry-After` + cabeçalhos de cota.
9. Escreva um teste que, **para toda rota**, tenta acesso cruzado e espera `404`.

**Critério de aprovação.**
- [ ] Você **viu** o vazamento de BOLA acontecer antes de corrigi-lo.
- [ ] A correção é na consulta, não num `if` posterior.
- [ ] `401` e `403` são usados corretamente, com os cabeçalhos certos.
- [ ] Mass assignment é recusado.
- [ ] O teste de acesso cruzado cobre **todas** as rotas.
- [ ] Rate limit devolve `429` com `Retry-After`.

**Por que importa.** BOLA é a vulnerabilidade nº 1 do OWASP API Top 10. Ver o vazamento
acontecer nas suas mãos ensina mais que dez leituras.

---

## Lab 8 — Tempo real: SSE e webhook

**Objetivo.** Implementar os dois mecanismos de notificação e sentir a diferença.

**Passos.**

1. Adicione `GET /eventos` com **SSE**, emitindo `tarefa.criada` e `tarefa.concluida`.
2. Teste no terminal: `curl -N http://localhost:3000/eventos`. Em outro terminal, crie uma
   tarefa e veja o evento chegar.
3. Faça uma página HTML mínima com `EventSource` e veja funcionando no navegador.
4. **Mate o servidor** e suba de novo. Observe a **reconexão automática**.
5. Implemente `Last-Event-ID` para retomar de onde parou. Prove que funciona.
6. Agora implemente **webhook**: um endpoint para o cliente registrar uma URL, e o envio do
   evento com **assinatura HMAC** e timestamp.
7. Escreva o **receptor** do webhook, com verificação de assinatura, janela de tempo e
   deduplicação por id.
8. Teste os quatro casos: legítimo, duplicado, assinatura errada, timestamp antigo.
9. Adicione retentativa com backoff no emissor.

**Critério de aprovação.**
- [ ] O SSE reconecta sozinho após queda do servidor.
- [ ] O `Last-Event-ID` faz o cliente receber os eventos que perdeu.
- [ ] O receptor de webhook **rejeita** assinatura inválida e timestamp antigo.
- [ ] Uma entrega duplicada é detectada e ignorada, respondendo `200`.
- [ ] O emissor retenta com intervalos crescentes quando o receptor devolve `500`.

**Por que importa.** SSE é subutilizado e resolve a maioria dos casos de tempo real com
pouco custo. E webhook mal implementado (sem assinatura) é uma porta aberta na internet.

---

## Lab 9 — Quebrar a própria API

**Objetivo.** Atacar o que você construiu. É a única forma honesta de saber se está seguro.

**Passos — tente cada um contra a sua API dos labs anteriores:**

1. **BOLA:** acesse o recurso de outro usuário, variando o id.
2. **Mass assignment:** mande campos que não deveriam ser editáveis (`dono_id`, `papel`,
   `criado_em`, `id`).
3. **Injeção:** mande `{"titulo": {"$ne": null}}`, `'; DROP TABLE --`, `../../etc/passwd`.
4. **Corpo gigante:** `POST` com 100 MB. O processo sobrevive?
5. **JSON profundo:** `[[[[[...]]]]]` com 10.000 níveis. Estoura a pilha?
6. **Muitos campos:** um objeto com 100.000 chaves. Quanto tempo o parse leva?
7. **ReDoS:** se você tem regex de validação, teste uma entrada de retrocesso catastrófico.
8. **Enumeração por tempo:** meça a resposta de "usuário existe" vs. "não existe". Difere?
9. **Vazamento em erro:** force um `500` e leia a resposta. Tem stack trace? Nome de tabela?
10. **Rate limit:** dispare 10.000 requisições. Quando ele reage? Sobrecarrega antes?
11. **Cabeçalhos:** rode `curl -I` e veja o que você está revelando (`Server`, `X-Powered-By`).
12. Rode um scanner: `docker run --rm -t ghcr.io/zaproxy/zaproxy zap-baseline.py -t http://host.docker.internal:3000`

**Critério de aprovação.**
- [ ] Você encontrou **ao menos duas** falhas reais na sua própria API.
- [ ] Você corrigiu as duas e escreveu um teste que impede a regressão.
- [ ] Nenhuma resposta de erro contém stack trace, SQL ou caminho de arquivo.
- [ ] Corpo grande, JSON profundo e muitos campos são todos recusados **antes** de consumir
      memória.
- [ ] Você documentou o que encontrou, em uma página.

**Por que importa.** "Achei que estava seguro" não é uma posição defensável. Este é o
laboratório mais desconfortável e o mais útil.

---

## Lab 10 — Evolução sem quebrar

**Objetivo.** Mudar uma API em produção sem derrubar clientes.

**Passos.**

1. Publique a v1 da sua API e escreva um **cliente** que a consome.
2. Faça uma **mudança compatível**: adicione o campo `prioridade`. O cliente antigo continua
   funcionando? Prove com o teste do cliente antigo, sem alterá-lo.
3. Faça uma **mudança quebradora**: renomeie `titulo` para `nome`. Veja o cliente quebrar.
4. Agora faça a mesma mudança **de forma compatível**, com a técnica *expand/contract*:
   - **Fase 1:** devolva os **dois** campos; aceite os dois na entrada.
   - **Fase 2:** marque `titulo` como `deprecated` no contrato; envie os cabeçalhos
     `Deprecation` e `Sunset`.
   - **Fase 3:** meça quem ainda usa `titulo` (log por cliente).
   - **Fase 4:** remova, **só depois** que o uso zerar.
5. Rode `oasdiff` entre as versões em cada fase. O que ele acusa?
6. Implemente um **brownout**: por 5 minutos, `titulo` volta `null`. Documente o efeito.
7. Escreva a política de depreciação da sua API, em uma página.

**Critério de aprovação.**
- [ ] O teste do cliente antigo, **sem alteração**, passa após a mudança compatível.
- [ ] Você viu o cliente quebrar com a mudança direta.
- [ ] A versão expand/contract não quebrou o cliente antigo em nenhuma fase.
- [ ] Os cabeçalhos `Deprecation` e `Sunset` estão nas respostas.
- [ ] Você mede o uso do campo obsoleto, por cliente.
- [ ] A política de depreciação tem prazos e responsáveis.

**Por que importa.** Construir uma API é a parte fácil. **Mudá-la sem trair quem confiou
nela é o trabalho de verdade** — e é a habilidade que quase ninguém pratica antes de
precisar.

---

## Projeto final integrador

Escolha um domínio real (oficina, consultório, clube, ONG, biblioteca, controle de gastos) e
construa:

- [ ] contrato **OpenAPI 3.1+** escrito antes do código, validado no CI;
- [ ] API REST no nível 2 de Richardson, com hipermídia parcial;
- [ ] autenticação por token, autorização por escopo, **e** por dono do recurso;
- [ ] paginação por cursor, `ETag`, `If-Match`, `Idempotency-Key`;
- [ ] erros em RFC 9457, com catálogo de tipos documentado;
- [ ] rate limit, limites de tamanho, log estruturado com request-id;
- [ ] um endpoint SSE **ou** emissão de webhook assinado;
- [ ] suíte de testes cobrindo caminho feliz **e** todos os erros, incluindo acesso cruzado;
- [ ] documentação com guia de 5 minutos, exemplos `curl` testados no CI;
- [ ] `Dockerfile`, desligamento gracioso, sondas de saúde;
- [ ] README explicando **as decisões**, não só o uso.

**Critério:** outra pessoa clona o repositório, segue o README, e faz a primeira chamada
bem-sucedida em **menos de 10 minutos**, sem te perguntar nada.

Use [07-projeto-modelo/](07-projeto-modelo/README.md) como referência de estrutura.

---

## Autoteste

1. No Lab 1, que nível de Richardson você atribuiu à API analisada, e com que justificativa?
2. No Lab 2, quais erros você retenta e quais não? Por quê?
3. No Lab 3, em qual das cinco APIs o gargalo não era o servidor?
4. No Lab 4, por que `DELETE` devolve `204` mesmo quando o recurso não existe?
5. No Lab 5, o que o `oasdiff` acusou, e por que isso muda o processo de release?
6. No Lab 6, quantas tarefas foram criadas com 10 requisições paralelas? Se mais de uma, por quê?
7. No Lab 7, por que `404` e não `403` no acesso cruzado?
8. No Lab 8, o que o `Last-Event-ID` resolve?
9. No Lab 9, quais duas falhas você encontrou na sua própria API?
10. No Lab 10, descreva as quatro fases do expand/contract e o que acontece se pular uma.
