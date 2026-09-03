# Projeto-modelo · `cofre-de-notas`

> Uma API de notas pessoais com autenticação JWT completa — **implementada do zero,
> sem uma única dependência externa**.
>
> Nível: intermediário · Testado em Node v24.18.0, Ubuntu 22.04.5, em 14/08/2026

---

## O que este projeto é

Uma aplicação pequena, mas **inteira**: registro, login, token de acesso, token de
renovação com rotação e detecção de reuso, revogação, logout de verdade, publicação
de chave pública em JWKS, rotação de chave, autorização por papel e 54 testes que
rodam.

O que ele **não** é: uma biblioteca para você usar em produção. A implementação de
JWS em `src/jwt.js` existe para que não sobre caixa-preta nenhuma — cada byte do
token é montado e conferido em código que você pode ler numa sentada. Em produção,
use [`jose`](https://github.com/panva/jose). Ver
[75-armadilhas.md](../75-armadilhas.md), armadilha nº 1.

---

## Pré-requisitos

| Item | Versão | Verificação |
|---|---|---|
| Node.js | ≥ 20 (testado em 24.18.0) | `node --version` |
| `curl` | qualquer | `curl --version` |

Nada mais. Sem `npm install`, porque não há o que instalar — a árvore de dependências
deste projeto tem exatamente zero nós. Isso é deliberado: ver
[80-custos-e-licencas.md](../80-custos-e-licencas.md) sobre custo de cadeia de suprimentos.

---

## Como rodar

```bash
cd 07-projeto-modelo

# 1. testes (gera chaves efêmeras em memória, não toca no disco)
node --test
# esperado: "pass 54  fail 0"

# 2. servidor (gera dados/chaveiro.json na primeira execução)
node src/servidor.js
# esperado:
#   cofre-de-notas ouvindo em http://localhost:3000
#   kid ativa: E54wgNtjf8S0GLiPk_sVbt3epcuwkqG0EHSICTA2WNU
```

Em outro terminal:

```bash
# a chave pública, para quem quiser verificar nossos tokens
curl -s localhost:3000/.well-known/jwks.json

# registrar
curl -s -X POST localhost:3000/auth/registrar \
  -H 'content-type: application/json' \
  -d '{"email":"ana@exemplo.com","senha":"uma-senha-longa-2026"}'

# login — guarde os dois tokens
curl -s -X POST localhost:3000/auth/login \
  -H 'content-type: application/json' \
  -d '{"email":"ana@exemplo.com","senha":"uma-senha-longa-2026"}' > /tmp/sessao.json

AT=$(node -e "console.log(require('/tmp/sessao.json').access_token)")
RT=$(node -e "console.log(require('/tmp/sessao.json').refresh_token)")

# rota protegida sem token → 401
curl -si localhost:3000/notas | head -1
# esperado: HTTP/1.1 401 Unauthorized

# com token → 200
curl -s -X POST localhost:3000/notas \
  -H "authorization: Bearer $AT" -H 'content-type: application/json' \
  -d '{"texto":"comprar pao"}'

# renovar (rotação: o refresh antigo morre agora)
curl -s -X POST localhost:3000/auth/refresh \
  -H 'content-type: application/json' -d "{\"refresh_token\":\"$RT\"}"

# reusar o refresh antigo → a família inteira é queimada
curl -s -X POST localhost:3000/auth/refresh \
  -H 'content-type: application/json' -d "{\"refresh_token\":\"$RT\"}"
# esperado: {"erro":"reuso_detectado", ...}

# logout → o access token morre NA HORA, não em 15 minutos
curl -s -X POST localhost:3000/auth/logout -H "authorization: Bearer $AT"
curl -s localhost:3000/notas -H "authorization: Bearer $AT"
# esperado: {"erro":"token_revogado", ...}
```

O arquivo [`requisicoes.http`](requisicoes.http) tem a mesma sequência pronta para o
REST Client do VS Code.

### Ferramenta de chaves

```bash
node src/ferramenta-chaves.js listar        # quais chaves existem, e qual assina
node src/ferramenta-chaves.js rotacionar    # nova chave ativa, antiga mantida
node src/ferramenta-chaves.js jwks          # o documento JWKS
node src/ferramenta-chaves.js aposentar <kid>
```

---

## Estrutura

```
07-projeto-modelo/
├── src/
│   ├── base64url.js         codificação dos segmentos — o "por que url e não base64 comum"
│   ├── jwt.js               ★ JWS compacto: assinar, verificar, validar claims. O coração.
│   ├── chaves.js            chaveiro: geração, JWKS, kid por thumbprint, rotação
│   ├── senha.js             scrypt — o passo ANTES do JWT, que quase todo tutorial pula
│   ├── armazem.js           estado do servidor: refresh, famílias, lista de negação
│   ├── autenticacao.js      emissão do par de tokens, rotação com detecção de reuso, guarda
│   ├── http.js              corpo JSON, resposta, WWW-Authenticate, cookie do refresh
│   ├── roteador.js          as rotas
│   ├── servidor.js          montagem e ponto de entrada
│   └── ferramenta-chaves.js CLI de rotação
├── test/
│   ├── jwt.test.js          33 testes — metade deles são ATAQUES
│   └── api.test.js          21 testes de ponta a ponta, com servidor HTTP real
├── dados/                   chaveiro.json é gerado aqui (fora do git)
└── requisicoes.http
```

---

## O que cada decisão de projeto ensina

### 1. `verificar()` exige a lista de algoritmos aceitos — `src/jwt.js`

O `alg` do cabeçalho **nunca** escolhe o algoritmo; ele é apenas conferido contra uma
lista fechada. Essa única linha de projeto elimina de uma vez `alg: none`, a confusão
RS256→HS256, e as variações de caixa (`nOnE`) que reabriram a falha em bibliotecas
reais em 2026 (CVE-2026-34950 no `fast-jwt`, CVE-2026-48526 no PyJWT).
Os testes em `test/jwt.test.js › ataques` executam cada um desses ataques.

### 2. O `kid` só indexa um `Map` local — `src/chaves.js`

Ele não vira caminho de arquivo, consulta SQL nem URL. É por isso que o token com
`kid: "../../etc/passwd"` do teste simplesmente não resolve chave nenhuma. A família
de ataques por `jku`/`x5u` (o token dizendo *onde* buscar a chave que o valida) não
existe aqui porque a decisão de onde buscar a chave nunca foi delegada ao token.

### 3. Access token curto + refresh opaco longo — `src/config.js`

Duas credenciais com propriedades opostas de propósito: o access token não bate no
banco (rápido, mas irrevogável até expirar → vida de 15 min), o refresh sempre bate
(revogável no ato → pode durar 14 dias). Um sistema com uma credencial só sempre
escolhe errado num dos dois eixos.

### 4. O refresh **não** é um JWT — `src/armazem.js`

São 32 bytes aleatórios, guardados como SHA-256. Fazer dele um JWT não traria
vantagem nenhuma (ele consulta o banco em todo uso, então a auto-suficiência do JWT
não serve para nada) e traria a desvantagem de expor o conteúdo. Escolher o formato
certo para cada credencial é metade do ofício.

### 5. Detecção de reuso queima a família — `src/autenticacao.js`

Se um refresh já gasto reaparece, ou há bug no cliente ou há cópia roubada em
circulação, e **não há como distinguir os dois casos**. O protocolo manda assumir o
pior. O teste `reusar um refresh ja gasto derruba a familia inteira` mostra o efeito
colateral honesto: a sessão legítima também cai.

### 6. Logout revoga o `jti` — `src/roteador.js`

O famoso "com JWT não dá para deslogar" é falso; o que existe é um custo. A lista de
negação guarda no máximo 15 minutos de logouts, porque uma entrada só precisa viver
até o `exp` do token. `armazem.limpar()` prova isso, e o teste
`a lista de negacao e limpa quando os tokens expiram` verifica.

### 7. `typ: "at+jwt"` — `src/autenticacao.js`

RFC 9068. Impede que um `id_token` do OIDC seja aceito como access token. Confundir
os dois é um dos erros de integração mais comuns em sistemas com login social.

### 8. Erro de login idêntico para senha errada e e-mail inexistente — `src/roteador.js`

Respostas diferentes entregam uma lista de e-mails válidos de graça. O teste
`senha errada e e-mail inexistente dao a MESMA resposta` trava esse comportamento.

### 9. `WWW-Authenticate` no 401 — `src/http.js`

RFC 6750 §3. Sem ele, um SPA não distingue "token expirou, renove" de "você não tem
permissão", e entra em laço de renovação infinito.

### 10. O que **não** está no payload — `test/api.test.js`

Um teste verifica que as claims são exatamente `aud, exp, iat, iss, jti, papeis, sub`.
Sem e-mail, sem nome. O payload é assinado, não cifrado: quem tem o token lê tudo, e o
token passa por logs de proxy e ferramentas de observabilidade.

---

## O que projetos reais têm e este também tem

- **tratamento de erro** com códigos estáveis (`expirado`, `assinatura_invalida`,
  `reuso_detectado`), não `500` genérico;
- **configuração** por variável de ambiente, isolada em um arquivo;
- **relógio injetável**, que é o que torna possível testar expiração sem `sleep`;
- **limite de tamanho de corpo** (413) — sem isso, um POST de 2 GB derruba o processo;
- **faxina periódica** das listas, senão elas crescem para sempre;
- **testes de ataque**, não só de caminho feliz.

## O que ele deliberadamente NÃO tem

| Ausente | Por quê | Onde se estuda |
|---|---|---|
| Banco de dados | trocaria o foco do JWT por SQL | [postgresql](../../postgresql/00-MAPA.md) |
| JWE (token cifrado) | quase sempre desnecessário | [15-criptografia-jwe.md](../15-criptografia-jwe.md) |
| OAuth 2.0 / OIDC completo | é outro assunto, grande | [19-jwt-no-oauth-e-oidc.md](../19-jwt-no-oauth-e-oidc.md) |
| Limite de tentativas de login | ortogonal ao JWT | [apis](../../apis/00-MAPA.md) |
| HTTPS | resolve-se no proxy à frente | [22-operacao-em-producao.md](../22-operacao-em-producao.md) |

---

## Verificação registrada

```
$ node --version
v24.18.0

$ node --test
ℹ tests 54
ℹ pass 54
ℹ fail 0

$ curl -s localhost:3000/saude
{"ok":true,"kidAtiva":"E54wgNtjf8S0GLiPk_sVbt3epcuwkqG0EHSICTA2WNU","agora":1786726076}
```

Executado em 14/08/2026, Ubuntu 22.04.5, Node v24.18.0. O fluxo completo
(registrar → login → rota protegida → refresh → reuso → logout → token revogado) e a
rotação de chave foram exercitados com `curl` real, não só pelos testes.

Um teste merece destaque: `thumbprint de JWK (RFC 7638)` reproduz o **vetor de teste
oficial da RFC** — o thumbprint da chave de exemplo bate exatamente
(`NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs`). É a prova de que a canonicalização
está correta e de que os `kid` gerados aqui interoperam com qualquer outra
implementação.
