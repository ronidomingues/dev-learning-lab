# 75 · Armadilhas, mitos e más práticas

> Nível: todos · Atualizado em 14/08/2026
> Ordenado por frequência com que causa estrago. Leia do começo.

---

## Parte I · As 25 armadilhas

### 1. Escrever a própria biblioteca de JWT

O parágrafo mais irônico deste material, escrito ao lado de um
[projeto que implementa JWS do zero](07-projeto-modelo/).

A diferença: aquele projeto existe **para ensinar**, e o README diz isso em negrito.
Ele não passou por anos de *fuzzing*, de auditoria adversarial, nem por dezenas de
pessoas tentando quebrá-lo.

**Em produção, use uma biblioteca auditada.** `jose` (JS), PyJWT ≥ 2.13 (Python),
Nimbus ou JJWT (Java), `golang-jwt/v5` (Go). O histórico de CVEs delas não é um
demérito — é a prova de que gente competente está olhando. Sua implementação caseira
não tem CVE porque ninguém a auditou.

---

### 2. `exp` em milissegundos

```js
exp: Date.now() + 900_000        // ❌ ano 58.582
exp: Math.floor(Date.now()/1000) + 900   // ✅
```

O bug mais perigoso do assunto, porque **passa em todos os testes**. Ninguém escreve
um teste que espera 15 minutos. Só aparece quando um token roubado ainda funciona
meses depois.

**Defesa automática:** teto sanitário na verificação — recuse `exp - iat > 30 dias`.

---

### 3. `verify()` sem lista de algoritmos

```js
jwt.verify(token, chave)                            // ❌
jwt.verify(token, chave, { algorithms: ['ES256'] }) // ✅
```

É a origem de `alg: none` e da confusão de algoritmo. Continua produzindo CVEs
críticas em 2026.

---

### 4. Não verificar `aud`

Um token válido de outro serviço é aceito no seu. Em microsserviços, é escalação de
privilégio. Ver o *confused deputy* em [20.9](20-ataques-e-defesas.md#209--ataques-de-aplicação).

---

### 5. Não verificar `iss`

Com dois provedores e chaves num pote comum, um token do Google é aceito como se
fosse do seu Keycloak. E o `sub` do Google pode colidir com um ID interno seu.

---

### 6. Comparar `iss` com `startsWith` ou `includes`

```js
if (payload.iss.startsWith('https://conta.auth0.com')) { }  // ❌
```

`https://conta.auth0.com.atacante.com` passa. Comparação de `iss` é **exata**, byte a
byte. E cuidado com a barra final: Auth0 emite com, Keycloak sem.

---

### 7. `aud` como array quebrando a comparação

```js
if (payload.aud !== 'api-pedidos') recusar();   // ❌ falha quando aud é array
```

A RFC permite os dois formatos. Trate os dois.

---

### 8. Dado sensível no payload

CPF, e-mail, telefone, dado de saúde, chave de API. O payload é **público** para quem
tem o token, e o token vai para o log do proxy, para o APM, para o tíquete de
suporte.

E a resposta não é cifrar. É **tirar do token**.

---

### 9. `localStorage` para o refresh token

Um XSS exfiltra a credencial de longa duração e a usa por semanas, do servidor dele.
Ver [18](18-onde-guardar-no-cliente.md).

---

### 10. Token na URL

```
GET /pagina?token=eyJ...      # ❌
```

Vai para o histórico do navegador, o log do servidor, o `Referer` de todo link
externo, e a ferramenta de analytics. Um vazamento que ninguém percebe porque não é
um "incidente".

---

### 11. Decodificar sem verificar, no servidor

```js
const dados = JSON.parse(atob(token.split('.')[1]));   // ❌
if (dados.papel === 'admin') { }
```

Continua sendo achado em auditoria em 2026.

---

### 12. Autorização só no cliente

O front esconde o botão de administrador; a API não checa nada. Esconder não é
autorizar. O cliente decide o que **mostrar**; o servidor decide o que **permitir**.

---

### 13. Segredo HMAC fraco

`"secret"`, `"minha-empresa-2026"`, a senha do banco. Ataque **offline**: bilhões de
tentativas por segundo, sem tocar no seu servidor.

```bash
openssl rand -base64 32     # ✅ o único jeito certo
```

---

### 14. O mesmo segredo em todos os ambientes

Um token de homologação vale em produção. Qualquer pessoa com acesso ao ambiente de
teste emite tokens de produção. **Chave e `iss` diferentes por ambiente.**

---

### 15. Chave privada no repositório

Ela fica no histórico do Git para sempre, em todo *fork* e em todo *clone*. Remover
do `HEAD` não resolve.

```bash
# hook de pre-commit
grep -rEn 'BEGIN (EC |RSA |OPENSSH )?PRIVATE KEY|eyJ[A-Za-z0-9_-]{10,}\.eyJ' . && exit 1
```

---

### 16. `kid` como caminho, URL ou SQL

Travessia de caminho, SSRF, injeção de SQL — **na verificação da autenticação**. Ver
[20.4](20-ataques-e-defesas.md#204--injeção-por-kid).

---

### 17. Confiar em `jku` ou `jwk` do token

O token dizendo qual chave o valida. Sempre confere, e sempre é o atacante.

---

### 18. Criar o cliente JWKS dentro do handler

```js
app.get('/x', async (req, res) => {
  const jwks = createRemoteJWKSet(url);   // ❌ uma chamada de rede POR REQUISIÇÃO
});
```

Uma vez por processo. Sintoma: latência inexplicável e o emissor reclamando de carga.

---

### 19. Apagar a chave antiga no instante da rotação

Todo token vivo morre. Onda de "fui deslogado do nada", proporcional ao seu tráfego.
Espere a vida do token mais longo.

---

### 20. Assinar com a chave nova antes de publicá-la

O erro inverso, e mais sutil: tokens com `kid` desconhecido circulam, os consumidores
rebuscam o JWKS, os que têm *cooldown* recusam tokens legítimos por minutos. Some
sozinho, e por isso ninguém descobre a causa.

---

### 21. Não deduplicar a renovação no cliente

Dez chamadas paralelas → detecção de reuso → sessão da pessoa cai sem motivo. O bug
aparece só em produção, quando a rede fica lenta. Ver
[laboratório 7](70-pratica.md#laboratório-7--concorrência-derrubando-a-sessão).

---

### 22. 401 onde deveria ser 403

O cliente recebe 401, renova o token, tenta de novo, recebe 401, renova... **laço
infinito** contra o seu próprio servidor.

- **401** = "não sei quem você é" → renove
- **403** = "sei quem você é e a resposta é não" → não adianta renovar

---

### 23. Token sem `Cache-Control: no-store`

Um proxy intermediário guarda a resposta com o token e a serve para outra pessoa.

---

### 24. Mandar o `id_token` para a API

A `aud` dele é o cliente, não a API. Se a sua API aceita, é porque não valida `aud` —
e aí aceitaria qualquer coisa. Ver [19.2](19-jwt-no-oauth-e-oidc.md#192--os-três-tokens-do-oidc).

---

### 25. Não monitorar `assinatura_invalida`

É o único sinal de que alguém está forjando tokens. Se ele estiver na mesma linha de
log de `expirado` — que acontece milhares de vezes por dia —, você não tem sinal
nenhum.

---

## Parte II · Os 12 mitos

### Mito 1 · "JWT é criptografado"

**Não.** É **assinado**. Qualquer pessoa lê o conteúdo com um comando:

```bash
echo "$TOKEN" | cut -d. -f2 | tr '_-' '/+' | base64 -d
```

Cifrar exige JWE, e você [provavelmente não precisa](15-criptografia-jwe.md).

---

### Mito 2 · "JWT é mais seguro que sessão"

**Não.** É **diferente**. Em vários cenários é **menos** seguro, porque revogar é
difícil e há mais superfície para errar. Sessão com cookie `HttpOnly` é uma solução
madura e simples.

---

### Mito 3 · "JWT elimina o banco de dados"

**Quase nunca.** Assim que você precisar deslogar alguém, renovar sem pedir a senha,
ou refletir uma mudança de permissão, o estado volta. O
[projeto-modelo](07-projeto-modelo/src/armazem.js) mostra exatamente onde.

---

### Mito 4 · "Não dá para revogar um JWT"

**Dá.** Lista de negação por `jti`. E o custo é menor do que a fama:

> 10 milhões de logouts por dia, access token de 15 min → **~100 mil entradas
> simultâneas → ~10 MB de Redis**.

O custo real é uma **consulta a mais por requisição** — de latência, não de memória.

---

### Mito 5 · "JWT é stateless"

O **token** é autocontido. O **sistema** não é. Refresh token, detecção de reuso,
lista de negação e chaves são estado. Chamar isso de *stateless* é o marketing que
levou milhares de equipes a escolher errado.

---

### Mito 6 · "Base64 protege o conteúdo"

Base64 é **codificação**, não criptografia. Reversível por qualquer pessoa, sem
chave. É escrever de trás para frente.

---

### Mito 7 · "HS256 é suficiente porque o segredo é forte"

O problema do HS256 não é força — é **arquitetura**. Quem verifica pode forjar. Se um
segundo serviço precisar validar, você lhe deu o poder de emitir. E a auditoria não
consegue dizer qual dos serviços emitiu um token suspeito.

---

### Mito 8 · "Access token de vida longa é conveniente"

É conveniente e é a decisão que transforma um vazamento em incidente permanente. A
janela de estrago de um token roubado **é** o seu tempo de vida.

---

### Mito 9 · "Preciso do OAuth para usar JWT"

**Não.** São coisas independentes. O [projeto-modelo](07-projeto-modelo/) usa JWT sem
uma linha de OAuth. Você precisa de OAuth/OIDC quando há **terceiros** ou
**federação**.

---

### Mito 10 · "Se tem XSS, já era de qualquer jeito"

**Verdade parcial, e a diferença importa.** Com cookie `HttpOnly`, o atacante age de
dentro da sua página, sujeito ao seu CSP e ao seu CORS, e para quando a aba fecha. Com
o token em `localStorage`, ele **exfiltra a credencial** e a usa do servidor dele, por
semanas. Sessão sequestrada ≠ credencial roubada.

---

### Mito 11 · "Meu token é seguro porque é longo"

Comprimento não é entropia, e nada disso ajuda se a verificação estiver errada. Um
token de 2 KB verificado com `alg` lido do próprio token é tão inseguro quanto um de
100 bytes.

---

### Mito 12 · "jwt.io é seguro, processa tudo no navegador"

**Verdade, e mesmo assim não cole token de produção.** Um token é uma credencial viva.
O risco não é só o site — é a extensão de navegador instalada, o histórico, a captura
de tela na chamada de suporte, o colega olhando. Use `jwt-cli`, offline.

---

## Parte III · Cheiros de código

Sinais de que a implementação merece uma auditoria:

```js
jwt.verify(token, chave)                   // sem algorithms
jwt.decode(token)                          // no servidor, para decidir algo
{ expiresIn: '30d' }                       // access token de 30 dias
process.env.JWT_SECRET || 'segredo'        // fallback inseguro em produção
algorithms: ['HS256', 'RS256']             // famílias misturadas
catch (e) { return null }                  // erro de verificação engolido
localStorage.setItem('refresh_token', ...) // refresh ao alcance do JS
res.json({ token })                        // sem Cache-Control: no-store
if (!user) return 'usuário não existe'     // enumeração de usuários
console.log(req.headers)                   // token no log
```

```bash
# varredura rápida em qualquer repositório
grep -rn "verify(" --include='*.js' . | grep -v algorithms
grep -rn "decode(" --include='*.js' .
grep -rEn "expiresIn.*['\"](30d|1y|365d)" .
grep -rEn "eyJ[A-Za-z0-9_-]{10,}\.eyJ" .
```

---

## Parte IV · Por que essas práticas persistem

Não é ignorância. São incentivos, e vale entendê-los:

**1. Tutoriais envelhecem e continuam no topo da busca.** Um artigo de 2016 ensinando
`jwt.verify(token, secret)` continua bem posicionado e sem aviso de que está errado.

**2. Funciona.** Todo antipadrão aqui **funciona** no caminho feliz. O código passa,
o teste passa, o produto entrega. A falha aparece meses depois, num contexto que
ninguém liga à decisão original.

**3. A narrativa foi mais forte que a análise.** "JWT é stateless e escala" foi
repetido em milhares de posts entre 2015 e 2020, sem a segunda metade da frase.

**4. Cargo cult.** "O Google usa JWT" — usa, para federação entre organizações, que é
o problema do Google. Copiar a solução sem o problema é o erro.

**5. A alternativa parece antiquada.** Sessão com cookie é tecnologia de 1994. Há uma
pressão real, e não técnica, para escolher o que parece moderno.

**6. Ninguém é promovido por escolher a solução simples.** Este é honesto e
desconfortável: "usei um cookie de sessão" não rende apresentação em conferência.

---

## Autoteste

1. Por que este material implementa JWT do zero e ao mesmo tempo diz para não fazer
   isso em produção?
2. Por que o bug do `exp` em milissegundos passa em todos os testes?
3. Um colega diz "JWT é criptografado". Prove o contrário em um comando.
4. Faça a conta do mito 4. Qual é o custo **real** da lista de negação?
5. Qual a diferença entre "o token é stateless" e "o sistema é stateless"?
6. Responda ao "se tem XSS, já era de qualquer jeito" com a distinção concreta.
7. Por que devolver 401 onde deveria ser 403 causa laço infinito?
8. Cite três cheiros de código que você procuraria numa revisão de PR.
9. Cite três razões **não técnicas** pelas quais os antipadrões persistem.
10. Por que `startsWith` na comparação de `iss` é explorável?
