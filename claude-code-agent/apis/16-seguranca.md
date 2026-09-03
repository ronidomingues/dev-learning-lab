# 16 · Segurança de APIs

`Nível: avançado` · `Atualizado: 11/08/2026`

Segurança de API não é criptografia — é, em ordem de importância: **autorização**,
**validação de entrada** e **limites**. As falhas mais comuns são banais, e é por isso que
são comuns.

---

## 1. Os três conceitos que se confundem

| Conceito | Pergunta | Mecanismo |
|---|---|---|
| **Autenticação** (AuthN) | *Quem é você?* | senha, token, certificado, chave |
| **Autorização** (AuthZ) | *Você pode fazer isso?* | escopo, papel, política, ACL |
| **Auditoria** | *O que foi feito, por quem, quando?* | log estruturado, trilha imutável |

**401 = falha de autenticação. 403 = falha de autorização.** Trocar os dois confunde o
cliente: com `401` ele tenta autenticar de novo; com `403` ele sabe que precisa de mais
permissão. É a diferença entre "faça login" e "peça acesso".

---

## 2. Mecanismos de autenticação

| Mecanismo | Como | Use quando | Cuidado |
|---|---|---|---|
| **API Key** | `X-API-Key: abc` ou `Authorization: Bearer abc` | serviço↔serviço simples, APIs públicas com cota | não identifica usuário; rotação é manual |
| **Basic** | `Authorization: Basic base64(u:s)` | ⛔ evite em API nova | base64 **não é** criptografia |
| **Bearer opaco** | `Authorization: Bearer <token>` | quando revogação imediata importa | exige consulta a cada requisição |
| **JWT** | `Authorization: Bearer <jwt>` | quando verificar sem consultar o emissor importa | **revogar é difícil** |
| **OAuth 2.x** | fluxo com servidor de autorização | acesso delegado, terceiros | complexidade real |
| **OIDC** | OAuth + identidade (`id_token`) | login de usuário | não confunda com autorização |
| **mTLS** | certificado dos dois lados | serviço↔serviço de alta segurança | gestão de certificados |
| **HMAC** | assinatura do corpo com segredo | webhooks, integrações bancárias | assinar o corpo **bruto** |

### 2.1 Token opaco vs. JWT — a decisão real

| | **Opaco** | **JWT** |
|---|---|---|
| O que é | string sem significado, chave de um registro | payload assinado, autocontido |
| Verificação | **consulta ao emissor** (ou cache) | assinatura, **offline** |
| Revogação | **imediata** — apaga do registro | **difícil** — vale até expirar |
| Vaza informação se lido | não | **sim** — o payload é apenas base64, não é cifrado |
| Tamanho | pequeno | grande (vai em toda requisição) |
| Escala | precisa do emissor disponível | **não precisa** |

> **A escolha:** JWT quando a verificação **precisa** ser offline (muitos serviços, alta
> escala, sem ponto central). Token opaco quando **revogação imediata** importa mais —
> que é o caso da maioria das APIs.
>
> **Se usar JWT: expiração curta (5–15 min) + refresh token.** Um JWT de 24 h é um passe
> livre de 24 h para quem o roubar, e não há como cancelá-lo.

### 2.2 JWT — os erros que geram CVE

```javascript
❌ jwt.verify(token, chave)                      // aceita o alg que o TOKEN disser
✅ jwt.verify(token, chave, { algorithms: ['RS256'] })
```

| Erro | Consequência |
|---|---|
| Aceitar `alg: none` | **qualquer um forja token válido** |
| Não fixar o algoritmo | confusão HS256/RS256: a chave **pública** vira segredo HMAC |
| Não validar `exp` | token eterno |
| Não validar `aud` | token do serviço A vale no serviço B |
| Não validar `iss` | token de outro emissor é aceito |
| Guardar dado sensível no payload | o payload **não é cifrado**, só codificado |
| Comparar assinatura com `===` | vaza por *timing* — use comparação em tempo constante |

**Verifique sempre:** assinatura, `exp`, `nbf`, `iss`, `aud`, e o **algoritmo esperado**.

### 2.3 OAuth 2.x — os fluxos

| Fluxo | Quando | Estado em 2026 |
|---|---|---|
| **Authorization Code + PKCE** | app web, mobile, SPA — qualquer coisa com usuário | ✅ **o padrão para tudo com usuário** |
| **Client Credentials** | serviço↔serviço, sem usuário | ✅ |
| **Device Code** | TV, CLI, dispositivo sem navegador | ✅ |
| **Refresh Token** | renovar acesso longo | ✅ com rotação |
| Implicit | — | ⛔ **obsoleto** — token no fragmento da URL |
| Password (ROPC) | — | ⛔ **obsoleto** — expõe a senha ao app |

**PKCE** (*Proof Key for Code Exchange*, RFC 7636) impede a interceptação do código de
autorização: o cliente gera um segredo aleatório, envia o hash dele no início e o segredo
no fim. Quem interceptar o código não consegue trocá-lo por token. **Era só para mobile;
hoje é recomendado para todos os clientes.**

> **Não implemente OAuth do zero.** Use um provedor (Keycloak, Auth0, Okta, Cognito,
> Zitadel, Ory) ou uma biblioteca madura e auditada. A quantidade de detalhes que precisam
> estar certos simultaneamente torna a implementação artesanal uma má aposta.

---

## 3. Autorização — onde estão as falhas de verdade

### 3.1 BOLA — a vulnerabilidade nº 1

*Broken Object Level Authorization*: o usuário pede um objeto que não é dele, e recebe.

```javascript
❌ app.get('/pedidos/:id', async (req, res) => {
     res.json(await db.pedidos.findById(req.params.id));   // e o dono?
   });

✅ app.get('/pedidos/:id', async (req, res) => {
     const pedido = await db.pedidos.findById(req.params.id);
     // 404, não 403: revelar a EXISTÊNCIA já é vazamento.
     if (!pedido || pedido.cliente_id !== req.usuario.cliente_id) {
       return res.status(404).json(problema404());
     }
     res.json(pedido);
   });
```

**Por que é a nº 1 há anos:** basta **uma** rota entre centenas esquecer a checagem. Não há
como testar exaustivamente à mão. As defesas estruturais:

1. **Autorização por padrão, negando** — o framework exige uma política explícita por rota,
   e recusa a rota sem ela.
2. **Filtrar na consulta**, não depois: `WHERE id = ? AND cliente_id = ?`. Assim é impossível
   esquecer o `if`.
3. **Ids opacos** como defesa em profundidade (não substitui a checagem).
4. **Teste automatizado**: para cada rota, um teste que tenta acessar o recurso de outro
   usuário e espera `404`.

### 3.2 BOPLA — nível de propriedade

O usuário lê ou escreve um **campo** que não deveria.

```javascript
❌ await db.usuarios.update(id, req.body);   // mass assignment
   // o cliente manda {"papel": "admin"} e vira administrador
```

**Defesas:** lista de campos permitidos (allowlist), `additionalProperties: false` no schema,
e campos `readOnly` no contrato — **aplicados no servidor**, não só documentados.

### 3.3 BFLA — nível de função

O usuário chama uma operação administrativa. Tipicamente: alguém descobre `POST /admin/...`
e não há checagem, porque "só o painel de admin chama isso".

**Defesa:** a autorização é do **servidor**, não da interface. Esconder o botão não é
proteção.

---

## 4. OWASP API Security Top 10 (edição 2023, vigente)

| # | Risco | Defesa central |
|---|---|---|
| **API1** | **BOLA** — autorização por objeto | checar o dono em toda leitura e escrita |
| API2 | Autenticação quebrada | não implementar do zero; expiração curta; MFA |
| **API3** | **BOPLA** — propriedades | allowlist de campos; `readOnly` aplicado |
| API4 | Consumo de recursos irrestrito | rate limit, limite de tamanho, de página, de profundidade |
| **API5** | **BFLA** — autorização por função | política por rota, negando por padrão |
| API6 | Acesso irrestrito a fluxo sensível | detectar automação em compra, cadastro, cupom |
| API7 | **SSRF** | validar e restringir URLs fornecidas pelo usuário |
| API8 | Configuração incorreta | CORS, cabeçalhos, TLS, mensagens de erro |
| API9 | Gestão de inventário | APIs antigas e ambientes de teste esquecidos no ar |
| API10 | Consumo inseguro de APIs de terceiros | validar o que **vem** do parceiro também |

**API9 merece destaque porque é invisível:** a versão `/v1` que ninguém usa mas continua
respondendo; o ambiente de homologação com dados de produção e sem autenticação; a API de
um projeto descontinuado. **Você não protege o que não sabe que existe.** Mantenha um
inventário e desligue o que não se usa.

**API7 (SSRF) em detalhe**, porque é fácil de introduzir:

```javascript
❌ const r = await fetch(req.body.url);   // o usuário escolhe o destino
   // ele manda http://169.254.169.254/latest/meta-data/ e lê as credenciais da nuvem
```

**Defesas:** allowlist de domínios; **resolver o DNS e checar o IP** (bloquear faixas
privadas, loopback e link-local); proibir redirecionamento; timeout curto; e, quando
possível, fazer a chamada de uma rede sem acesso ao metadata service.

---

## 5. Validação de entrada

**A regra:** valide **tudo** que vem de fora — corpo, query, cabeçalhos, caminho, cookies.
Rejeite o que não reconhecer.

| Ataque | Defesa |
|---|---|
| **Injeção SQL** | consultas parametrizadas, **sempre**. Nunca concatenação |
| **Injeção NoSQL** | validar tipo — `{"$ne": null}` num campo string é injeção |
| **Injeção de comando** | não passar entrada para shell; se inevitável, allowlist estrita |
| **XSS** (se a resposta vira HTML) | escapar na saída; `Content-Type` correto; `nosniff` |
| **XXE** (XML) | desabilitar entidades externas no parser |
| **Path traversal** | normalizar e verificar que o caminho final está dentro da raiz |
| **ReDoS** | evitar regex com retrocesso catastrófico; limitar o tamanho da entrada |
| **Mass assignment** | allowlist de campos |
| **Zip bomb / JSON bomb** | limitar tamanho e profundidade antes de desserializar |

**Limites que toda API precisa ter, e quase nenhuma tem todos:**

```javascript
const LIMITES = {
  corpoBytes:        256 * 1024,
  itensPorPagina:    100,
  itensPorLote:      1000,
  profundidadeJSON:  10,      // JSON aninhado 10.000 níveis estoura a pilha
  tamanhoStringCampo: 10_000,
  requisicoesPorMinuto: 100,
  camposPorObjeto:   100,     // 100.000 chaves consomem CPU no parse
  timeoutSegundos:   30
};
```

---

## 6. Rate limiting

| Estratégia | Como | Nota |
|---|---|---|
| **Janela fixa** | conta por minuto cheio | simples; permite **dobro** na virada |
| **Janela deslizante** | conta os últimos 60 s | **recomendada**; sem o buraco da virada |
| **Token bucket** | fichas repostas a taxa constante | permite rajada controlada |
| **Leaky bucket** | saída a taxa constante | suaviza o tráfego |

**Por que a janela fixa tem buraco:** com limite de 100/min, o cliente faz 100 no segundo
59 e mais 100 no segundo 61 — **200 em dois segundos**, o dobro do pretendido.

**Por chave, não por IP:** clientes atrás do mesmo NAT corporativo compartilhariam a cota.
Limite por **identidade** quando houver autenticação; por IP só para tráfego anônimo.

**A resposta correta:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
RateLimit: limit=100, remaining=0, reset=30
RateLimit-Policy: 100;w=60
Content-Type: application/problem+json
```

Sem `Retry-After`, clientes ingênuos retentam imediatamente e **agravam** o problema que o
rate limit deveria conter.

---

## 7. Não vaze informação

**Nas respostas de erro:**
```json
❌ { "erro": "SequelizeDatabaseError: relation \"usuarios_prod\" does not exist
              at /app/src/db/pool.js:42:11 ... (pg 8.11.3)" }
✅ { "type": "...", "title": "Erro interno", "status": 500,
     "instance": "/requisicoes/9f2a-4b1c" }
```
A stack trace revela: estrutura interna, nomes de tabela, caminhos, versões de biblioteca
(que apontam para CVEs conhecidos) — e às vezes credenciais em mensagens de erro de conexão.

**Nos cabeçalhos:** remova `X-Powered-By`, `Server` detalhado. É reconhecimento gratuito.

**Nos tempos de resposta:** se "usuário não existe" responde em 5 ms e "senha errada" em
80 ms (por causa do hash), um atacante **enumera usuários pelo relógio**. Faça o trabalho
constante, ou responda a mesma coisa nos dois casos.

**Nas mensagens:** "e-mail não cadastrado" confirma quais e-mails existem. Prefira
"credenciais inválidas" para os dois casos.

**Nos logs:** nunca registre token, senha, cartão, CPF completo. O log vai para um
agregador que muita gente acessa. (O `log.js` do projeto-modelo mascara automaticamente.)

---

## 8. Transporte e cabeçalhos

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Cache-Control: no-store            # em rotas autenticadas
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
```

| Item | Recomendação |
|---|---|
| TLS | **1.2 mínimo, 1.3 preferido**. Sem exceção, inclusive na rede interna |
| HSTS | ligue, com `includeSubDomains` |
| Certificado | automatize a renovação (ACME/Let's Encrypt). Certificado vencido é a causa nº 1 de incidente evitável |
| CORS | origens **explícitas**. `*` só para dado realmente público, e nunca com credenciais |
| Cookies (se usar) | `HttpOnly`, `Secure`, `SameSite=Lax` ou `Strict` |
| `nosniff` | sempre — impede o navegador de adivinhar o tipo |
| CSP | mesmo em API JSON: `default-src 'none'` reduz o dano se algo servir HTML por engano |

---

## 9. Segredos

| Regra | Por quê |
|---|---|
| Nunca no código | vai para o Git, e o Git tem histórico **para sempre** |
| Nunca em URL | vai para log de acesso, `Referer`, histórico do navegador |
| Nunca no log | o agregador é lido por muita gente |
| Em variável de ambiente ou cofre | Vault, AWS Secrets Manager, Doppler, SOPS |
| **Rotação periódica** | limita a janela de um vazamento |
| **Escaneie o repositório** | `gitleaks`, `trufflehog`, secret scanning do GitHub |

**Se um segredo vazou:** **rotacione primeiro**, investigue depois. Remover o commit **não
resolve** — se o repositório foi clonado ou é público, o segredo já foi copiado. Considere-o
comprometido a partir do instante do `push`.

---

## 10. Os cinco porquês: por que BOLA é a vulnerabilidade nº 1 há anos?

**1. Por que a falha de autorização por objeto é a mais comum?**
Porque ela exige uma checagem **em cada endpoint, para cada objeto**, e não há um lugar
central onde escrevê-la uma vez.

**2. Por que não dá para centralizar?**
Porque a regra de "quem pode ver o quê" depende do **domínio**: um pedido pertence ao
cliente; um documento pertence à equipe; um relatório é visível para o gestor da área. Não
existe regra genérica — depende de conhecer o negócio.

**3. Por que os testes não pegam?**
Porque o teste típico usa **um** usuário e verifica que ele consegue acessar o **próprio**
recurso. O caso que falha — usuário A acessando o recurso de B — não é o caminho feliz e
raramente é escrito.

**4. Por que ferramentas automáticas não pegam?**
Porque a ferramenta não sabe **quem deveria** ter acesso. Ela vê uma requisição `200` e não
tem como saber se aquele `200` era legítimo. É um problema de conhecimento de domínio, não
de análise de código.

**5. O que realmente funciona, então?**
Mudar a estrutura para que **esquecer seja impossível**:
(a) filtrar **na consulta** (`WHERE cliente_id = ?`), não com um `if` depois — assim não há
o que esquecer; (b) autorização declarativa por rota, com o framework **recusando** rotas
sem política declarada; (c) um teste automático, gerado para todas as rotas, que tenta
acesso cruzado e espera `404`.

**A lição geral:** segurança que depende de disciplina individual falha na escala de um time.
Segurança que depende de estrutura, não.

*(Parada legítima: limite fundamental — a regra de autorização é conhecimento de domínio,
não propriedade computável do código.)*

---

## 11. Checklist de segurança

**Autenticação**
- [ ] HTTPS obrigatório, TLS 1.2+, HSTS ligado.
- [ ] Sem Basic Auth; sem senha em URL; sem token em query string.
- [ ] JWT com algoritmo **fixado** e `exp`, `iss`, `aud` validados.
- [ ] Expiração curta + refresh com rotação.
- [ ] Comparação de segredo em **tempo constante**.

**Autorização**
- [ ] Checagem de dono em **toda** leitura e escrita de objeto (BOLA).
- [ ] Filtragem na consulta, não com `if` depois.
- [ ] Allowlist de campos na escrita (BOPLA / mass assignment).
- [ ] Política declarada por rota, negando por padrão (BFLA).
- [ ] `404` em vez de `403` onde a existência é sensível.

**Entrada**
- [ ] Schema validando corpo, query e caminho; `additionalProperties: false`.
- [ ] Consultas parametrizadas; nunca concatenação.
- [ ] Limites: corpo, página, lote, profundidade, tamanho de campo, timeout.
- [ ] URLs fornecidas pelo usuário validadas contra SSRF.

**Saída**
- [ ] Nenhuma stack trace, SQL, caminho ou versão no corpo do erro.
- [ ] Cabeçalhos de identificação do servidor removidos.
- [ ] Mensagens de erro que não enumeram usuários.
- [ ] `Cache-Control: no-store` em rota autenticada.

**Operação**
- [ ] Rate limit com `429` + `Retry-After`.
- [ ] Log estruturado **sem segredo**, com request-id.
- [ ] Inventário de APIs; ambientes antigos desligados.
- [ ] Escaneamento de segredos no repositório.
- [ ] Dependências monitoradas por CVE.

---

## Autoteste

1. Qual a diferença entre 401 e 403? Como a escolha errada confunde o cliente?
2. Quando usar JWT e quando usar token opaco? Qual é o custo de cada um?
3. Cite quatro erros de validação de JWT e a consequência de cada um.
4. O que é PKCE e que ataque ele impede? Por que virou recomendado para todos os clientes?
5. Escreva a versão correta de `GET /pedidos/:id` evitando BOLA. Por que `404` e não `403`?
6. O que é mass assignment e quais são as duas defesas?
7. Por que API9 (gestão de inventário) é perigosa apesar de parecer burocrática?
8. Dê um exemplo concreto de SSRF e três defesas.
9. Por que janela fixa de rate limit permite o dobro do limite?
10. Como um atacante enumera usuários pelo tempo de resposta? Como impedir?
11. Por que BOLA é a nº 1 há anos, e o que **estruturalmente** resolve?

---

### Fontes consultadas (11/08/2026)

- OWASP — *API Security Top 10 (2023)* — https://owasp.org/API-Security/
- IETF — RFC 6749 (OAuth 2.0), RFC 6750 (Bearer), RFC 7636 (PKCE), RFC 7519 (JWT), RFC 8725 (JWT Best Practices)
- IETF — *OAuth 2.0 Security Best Current Practice* — https://datatracker.ietf.org/doc/draft-ietf-oauth-security-topics/
- OWASP — *Cheat Sheet Series* (REST Security, JWT, Mass Assignment) — https://cheatsheetseries.owasp.org/
