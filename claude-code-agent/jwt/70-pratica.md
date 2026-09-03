# 70 · Prática — 12 laboratórios

> Nível: iniciante a avançado · Atualizado em 14/08/2026
> Ambiente: o do [03-instalacao.md](03-instalacao.md). Cada laboratório declara o que
> exige e como você sabe que acertou.

Teoria lida sem mão na massa evapora em uma semana. Faça na ordem — cada um depende
do anterior.

---

## Laboratório 1 · Fabricar e quebrar um token no terminal

**Nível:** iniciante · **Tempo:** 20 min · **Exige:** `openssl`, `node`

**Objetivo:** provar para si mesmo que um JWT é texto, e que a assinatura é o que
importa.

**Tarefas:**

1. Monte um token HS256 à mão, com `sub`, `iat` e `exp` de 5 minutos, seguindo
   [12.7](12-anatomia-do-token.md#127--montando-um-token-do-zero-à-mão).
2. Decodifique o payload de volta e confirme que bate.
3. Altere um caractere do payload **sem** recalcular a assinatura e verifique que a
   verificação falha.
4. Altere o payload **e** recalcule a assinatura com o segredo certo — funciona.
5. Altere o payload e recalcule com o segredo errado — falha.

**Como saber que acertou:**

```
passo 2: o JSON impresso é idêntico ao que você escreveu
passo 3: "assinatura confere: false"
passo 4: "assinatura confere: true"
passo 5: "assinatura confere: false"
```

**Pergunta para responder por escrito:** no passo 3, o servidor conseguiu **ler** o
payload adulterado. O que isso ensina sobre onde a segurança do JWT mora?

---

## Laboratório 2 · Do HMAC ao assimétrico

**Nível:** iniciante · **Tempo:** 30 min · **Exige:** `openssl`, Node com `jose`

**Objetivo:** sentir a diferença de arquitetura entre HS256 e ES256.

**Tarefas:**

1. Gere um par EC P-256 com `openssl` ([05.F](05-manual-de-uso.md#f--openssl-gerar-e-converter-chaves)).
2. Assine um token com a chave privada, usando `jose`.
3. Verifique com a chave **pública**.
4. Tente verificar com a chave **privada** e observe (funciona — a privada contém a
   pública).
5. Tente assinar com a chave **pública** e observe o erro.
6. Exporte a pública como JWK e calcule o `kid` por thumbprint.

**Como saber que acertou:** o passo 5 falha com erro de tipo de chave, e o `kid` do
passo 6 é sempre o mesmo para a mesma chave, mesmo rodando de novo.

**Pergunta:** você quer que um segundo serviço verifique esses tokens. O que você
entrega a ele em cada cenário — HS256 e ES256? Que poder cada entrega concede?

---

## Laboratório 3 · Executar os ataques clássicos

**Nível:** intermediário · **Tempo:** 45 min · **Exige:** o projeto-modelo

**Objetivo:** ver os ataques falharem contra uma implementação correta, e entender
por quê.

**Tarefas:**

1. Rode `node --test` no projeto-modelo e leia a saída do bloco `ataques`.
2. Abra [test/jwt.test.js](07-projeto-modelo/test/jwt.test.js) e leia o teste de
   confusão de algoritmo linha por linha.
3. **Quebre a defesa de propósito:** em `src/jwt.js`, troque a checagem
   `algoritmos.includes(cabecalho.alg)` por `true`. Rode os testes.
4. Anote quais testes falharam. Restaure o código.
5. Repita quebrando a resolução de `kid` (aceite qualquer `kid`, devolvendo a chave
   ativa). Quais testes falham?

**Como saber que acertou:** no passo 3, os testes `alg: none`, `nOnE` e confusão de
algoritmo passam a falhar — ou seja, o ataque passa a funcionar. Você acabou de
demonstrar que aquela única linha é a defesa.

**Pergunta:** por que a defesa correta não precisa listar `nOnE`, `NONE` e `" none"`?

---

## Laboratório 4 · Expiração e relógio

**Nível:** intermediário · **Tempo:** 30 min · **Exige:** o projeto-modelo

**Objetivo:** entender tolerância de relógio na prática.

**Tarefas:**

1. Emita um token com `exp` de 10 segundos. Use-o. Espere 11 s e use de novo.
2. Configure tolerância de 30 s e repita — ele passa a ser aceito por mais tempo.
3. Emita um token com `exp` **exatamente** igual ao instante atual. Ele vale?
4. Cometa o erro de propósito: `exp: Date.now() + 900`. Converta o `exp` resultante
   para data legível.
5. Implemente a checagem sanitária: recusar token com `exp - iat > 30 dias`.

**Como saber que acertou:** no passo 3, o token é recusado (a comparação é `>=`). No
passo 4, a data cai depois do ano 58.000.

**Pergunta:** por que o erro do passo 4 passa em todos os testes de unidade de um
projeto e ainda assim é uma falha crítica?

---

## Laboratório 5 · Rotação de chave sem downtime

**Nível:** intermediário · **Tempo:** 45 min · **Exige:** o projeto-modelo

**Objetivo:** executar a rotação completa e provocar os dois erros clássicos.

**Tarefas:**

1. Suba o servidor, faça login e guarde o `access_token` (chamado de token A).
2. `node src/ferramenta-chaves.js rotacionar`.
3. Reinicie o servidor e faça um novo login (token B).
4. Verifique que **os dois** tokens funcionam.
5. Confira o JWKS: ele tem duas chaves.
6. Aposente a chave antiga e verifique que o token A **para** de funcionar.
7. **Provoque o erro 1:** aposente a chave A com o token A ainda vivo. Observe o 401.
8. **Provoque o erro 2:** simule assinar com uma chave que não está no JWKS
   (adicione uma chave ao chaveiro sem publicá-la) e observe o erro do lado de quem
   verifica.

**Como saber que acertou:** no passo 4, ambos retornam 200. No passo 6, o token A
retorna `chave_desconhecida`.

**Pergunta:** escreva o procedimento de rotação com as duas esperas e diga como você
calcularia cada uma no seu sistema.

---

## Laboratório 6 · Ciclo completo de sessão

**Nível:** intermediário · **Tempo:** 1 h · **Exige:** o projeto-modelo

**Objetivo:** exercitar login, renovação, reuso e logout, e ver o efeito colateral da
queima de família.

**Tarefas:**

1. Login → guarde o par.
2. Renove três vezes seguidas, guardando cada refresh.
3. Tente usar o refresh da primeira renovação. Observe.
4. Tente usar o refresh **mais recente**, o legítimo. Observe.
5. Faça login de novo e desloge, conferindo que o access morre **na hora**.
6. Meça o tamanho da lista de negação com `GET /admin/sessoes` (crie um admin).
7. Chame `armazem.limpar()` com um tempo futuro e veja a lista esvaziar.

**Como saber que acertou:** no passo 3, `reuso_detectado`. No passo 4, **também**
falha — a família inteira caiu. No passo 5, `token_revogado`.

**Pergunta:** o passo 4 derruba um usuário legítimo. Por que isso é o comportamento
correto, e que mitigação existe? Qual é o custo dessa mitigação?

---

## Laboratório 7 · Concorrência derrubando a sessão

**Nível:** avançado · **Tempo:** 45 min · **Exige:** o projeto-modelo

**Objetivo:** reproduzir o falso positivo mais comum de produção.

**Tarefas:**

1. Escreva um script que dispara **10 chamadas paralelas** a `/auth/refresh` com o
   mesmo refresh token.
2. Observe o resultado: uma tem sucesso, nove disparam a detecção de reuso, e a
   sessão morre.
3. Implemente a deduplicação **no cliente** ([exemplo 8](06-exemplos.md#8--cliente-de-navegador-com-renovação-automática))
   e repita.
4. Implemente a **janela de graça** no servidor ([17.4](17-ciclo-de-vida-sessao.md#174--rotação-de-refresh-com-detecção-de-reuso))
   e repita sem a deduplicação do cliente.
5. Compare os dois resultados e escreva os trade-offs.

```js
// esqueleto do passo 1
const resultados = await Promise.all(
  Array.from({ length: 10 }, () =>
    fetch('http://localhost:3000/auth/refresh', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ refresh_token: RT }),
    }).then((r) => r.status)),
);
console.log(resultados);
```

**Como saber que acertou:** no passo 2, você vê `[200, 401, 401, ...]`. Nos passos 3
e 4, `[200, 200, ...]` ou uma única chamada de rede.

**Pergunta:** a janela de graça enfraquece a detecção de roubo. Quanto tempo você
escolheria e por quê?

---

## Laboratório 8 · Verificar token de um provedor real

**Nível:** avançado · **Tempo:** 1 h · **Exige:** Docker

**Objetivo:** integrar com um provedor OIDC de verdade.

**Tarefas:**

1. Suba um Keycloak descartável:

```bash
docker run --rm -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

> Se a variável não for reconhecida na versão que você baixou, use
> `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD` — o nome mudou entre versões.

2. Crie um realm, um cliente e um usuário pela interface em <http://localhost:8080>.
3. Busque o documento de descoberta e o JWKS.
4. Obtenha um token e **inspecione**: quais claims vieram? Qual `alg`? Qual `typ`?
5. Escreva um verificador com `createRemoteJWKSet`
   ([exemplo 6](06-exemplos.md#6--verificar-token-de-um-provedor-externo-keycloak-auth0-entra-id)).
6. Faça o Keycloak rotacionar a chave e observe seu verificador se adaptar sozinho.

**Como saber que acertou:** no passo 6, o primeiro token pós-rotação causa uma busca
ao JWKS e depois valida normalmente, sem que você mude nada.

**Pergunta:** compare as claims do `id_token` com as do `access_token` do Keycloak.
Cite três diferenças e explique por que cada uma existe.

---

## Laboratório 9 · Auditar uma implementação

**Nível:** avançado · **Tempo:** 1 h 30 · **Exige:** um projeto seu ou público

**Objetivo:** aplicar o checklist de auditoria a código real.

**Tarefas:**

1. Escolha um projeto: um seu, ou um projeto no GitHub que use JWT.
2. Aplique o checklist de [20.12](20-ataques-e-defesas.md#2012--checklist-de-auditoria)
   item a item.
3. Para cada item que falha, escreva: o risco concreto, a exploração, e a correção.
4. Se for código seu, corrija e escreva o teste que prova a correção.

**Buscas que dão resultado rápido:**

```bash
grep -rn "verify(" --include='*.js' .          # tem lista de algorithms?
grep -rn "decode(" --include='*.js' .          # decodifica sem verificar?
grep -rn "algorithms" --include='*.js' .       # onde está fixada?
grep -rEn "audience|issuer|aud|iss" .          # valida?
grep -rEn "eyJ[A-Za-z0-9_-]{10,}" .            # token comitado?
```

**Como saber que acertou:** você produziu um relatório com pelo menos três achados
classificados por severidade, cada um com exploração descrita.

---

## Laboratório 10 · Medir o custo

**Nível:** avançado · **Tempo:** 45 min

**Objetivo:** substituir intuição por medição.

**Tarefas:**

1. Meça o tempo de verificação de HS256, ES256 e RS256, 100.000 vezes cada.
2. Meça o tempo de **assinatura** dos três. Compare com o de verificação.
3. Meça o tamanho do token nos três.
4. Calcule: para 10.000 requisições por segundo, quanto de CPU cada opção custa? E
   quanto de banda por dia?
5. Meça o custo de uma consulta a Redis na sua rede e compare com a verificação.

```js
// esqueleto
const inicio = process.hrtime.bigint();
for (let i = 0; i < 100_000; i++) verificar(token, opcoes);
const ms = Number(process.hrtime.bigint() - inicio) / 1e6;
console.log(`${(ms / 100_000 * 1000).toFixed(1)} µs por verificação`);
```

**Como saber que acertou:** seus números têm a mesma ordem de grandeza da tabela de
[22.5](22-operacao-em-producao.md#225--desempenho). Se não têm, descubra por quê —
essa investigação vale mais que o laboratório.

**Pergunta:** verificar RSA é rápido e assinar é lento. Por que essa assimetria torna
o RS256 menos ruim do que parece, e qual é o problema real dele?

---

## Laboratório 11 · Implementar SD-JWT em miniatura

**Nível:** pesquisa · **Tempo:** 2 h · **Exige:** [65.2](65-estado-da-arte.md#652--sd-jwt--divulgação-seletiva-rfc-9901)

**Objetivo:** entender divulgação seletiva construindo uma.

**Tarefas:**

1. Emita um token com quatro claims: `nome`, `nascimento`, `cpf`, `cidade`.
2. Para cada uma, gere sal, monte a divulgação, calcule o digest.
3. Assine um JWT contendo apenas `_sd` (a lista de digests) e `_sd_alg`.
4. Monte a apresentação revelando **só** `cidade`.
5. Escreva o verificador: recalcula o digest de cada divulgação recebida, confirma
   que está no `_sd`, valida a assinatura.
6. Tente forjar: invente uma divulgação com `"cidade": "outra"` e veja falhar.
7. **Experimento crucial:** remova o sal e tente adivinhar o valor de uma claim
   booleana pelo digest. Você consegue?

**Como saber que acertou:** no passo 6, o digest não bate. No passo 7, com dois
valores possíveis (`true`/`false`) e sem sal, você quebra a claim em duas tentativas.

**Pergunta:** por que o sal é indispensável, e o que ele **não** protege?

---

## Laboratório 12 · Decidir com argumento

**Nível:** avançado · **Tempo:** 1 h · **Exige:** [21-quando-nao-usar.md](21-quando-nao-usar.md)

**Objetivo:** praticar a decisão de arquitetura, que é o que realmente separa níveis.

Para cada cenário, escreva **meia página**: escolha, justificativa, e o que você
sacrifica.

1. Blog com área administrativa. Um servidor, cinco autores.
2. SaaS B2B, 50 mil empresas, API pública consumida por clientes.
3. Aplicativo bancário, exigência de revogação imediata.
4. E-commerce com 40 microsserviços e três times.
5. API interna de uma empresa com login corporativo pelo Entra ID.
6. Dispositivo IoT sem relógio confiável, sincronizando a cada 6 h.
7. Link de "confirme seu e-mail" enviado por e-mail.

**Como saber que acertou:** compare com as respostas abaixo **depois** de escrever as
suas. Divergir é aceitável — não ter argumento, não.

<details>
<summary>Respostas sugeridas (leia só depois)</summary>

1. **Sessão com cookie.** Um servidor, revogação trivial, ~50 linhas de código. JWT
   aqui é complexidade pura.
2. **JWT + OAuth 2.0.** Terceiros precisam validar sem acesso ao seu banco. Sacrifica
   revogação imediata; mitigue com access token de 15 min.
3. **Token opaco + introspecção**, ou sessão. A exigência de revogação imediata é
   incompatível com JWT autocontido. Chamar a lista de negação de "JWT" não muda o
   custo.
4. **JWT com ES256 e JWKS.** É o caso canônico: muitos verificadores, times
   diferentes. Adicione `aud` por serviço para evitar *confused deputy*.
5. **JWT via OIDC**, sem escrever servidor de autorização. O Entra ID emite; você só
   verifica. Cuidado com o tamanho do token para usuários com muitos grupos.
6. **Cuidado especial.** Sem relógio confiável, `exp` não é confiável. Use tolerância
   generosa, `nbf` conservador, e prefira sessão ou token de vida muito longa com
   revogação por lista sincronizada. Este é o caso em que a hipótese básica do JWT
   falha.
7. **JWT, claramente.** Vida curta, uso único (via selo do estado da senha ou `jti`),
   sem estado a manter. É o caso em que o JWT é a ferramenta certa e nada mais chega
   perto.

</details>

---

## Trilha sugerida

| Se você quer | Faça |
|---|---|
| Entender o formato | 1, 2, 4 |
| Segurança de aplicação | 1, 3, 9, e os laboratórios do PortSwigger |
| Operar em produção | 5, 6, 7, 8, 10, 22 |
| Decidir arquitetura | 12, depois releia [21](21-quando-nao-usar.md) |
| Pesquisa | 11, depois [60](60-teoria-avancada.md) |

---

## Autoteste

1. No laboratório 1, por que o payload adulterado ainda pôde ser lido?
2. No laboratório 3, qual única linha de código, ao ser removida, faz três ataques
   passarem?
3. No laboratório 5, o que dá errado ao aposentar a chave antiga cedo demais?
4. No laboratório 7, por que dez chamadas paralelas derrubam a sessão?
5. No laboratório 11, por que o sal é indispensável?
6. No laboratório 12, cenário 6, por que a hipótese básica do JWT falha?
