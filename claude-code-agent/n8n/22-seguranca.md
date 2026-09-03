# 22 · Segurança

`Nível: avançado` · `Pesquisado na web em 01/09/2026`

---

## 1. O modelo de ameaça, em uma frase

> **Quem pode editar um workflow executa código no seu servidor, com as credenciais
> de todo mundo.**

Tudo neste arquivo decorre disso. Não é uma falha do n8n; é a natureza de uma
ferramenta cuja função é executar lógica arbitrária com acesso a sistemas.
O trabalho é reduzir o raio de alcance.

Os ativos a proteger, em ordem de valor:

| Ativo | Onde | Se vazar |
|---|---|---|
| `N8N_ENCRYPTION_KEY` | env ou `~/.n8n/config` | **Todas** as credenciais são decifráveis |
| Credenciais | banco, cifradas | Acesso aos sistemas conectados |
| Dados de execução | banco | Dados de clientes, PII, tokens em cabeçalhos |
| Os próprios workflows | banco | Mapa completo dos seus processos |
| URLs de webhook | públicas por natureza | Disparo não autorizado |

---

## 2. As dez medidas, em ordem de custo-benefício

| # | Medida | Como | Custo |
|---|---|---|---|
| 1 | **HTTPS sempre** | Proxy reverso com TLS; nunca 5678 exposta | baixo |
| 2 | **Chave de criptografia própria e guardada** | `N8N_ENCRYPTION_KEY` num cofre | baixo |
| 3 | **Task runners em modo externo** | [17](17-code-node-e-task-runners.md#52-os-dois-modos-e-por-que-isso-importa-muito) | médio |
| 4 | **Bloquear `$env`** | `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` | baixo |
| 5 | **Autenticar todo webhook** | HMAC, header auth ou mTLS | baixo |
| 6 | **MFA e verificação de e-mail** | Configuração de instância | baixo |
| 7 | **Proteção SSRF** | Recurso próprio do n8n | baixo |
| 8 | **Bloquear nós perigosos** | `NODES_EXCLUDE` | baixo |
| 9 | **Auditoria periódica** | `n8n audit` | baixo |
| 10 | **RBAC e projetos** | Recurso **licenciado** | $$ |

---

## 3. A chave de criptografia

```bash
openssl rand -hex 32
```

- Se você **não** definir `N8N_ENCRYPTION_KEY`, o n8n gera uma no primeiro boot e a
  grava em `~/.n8n/config`. Funciona — desde que você nunca perca o volume.
- **Todos** os processos (main, workers, webhook) precisam da **mesma** chave.
- Trocar a chave torna as credenciais existentes ilegíveis. O n8n 2.x oferece
  **rotação de chave de dados** com recurso próprio, e o **n8n 3.0 liga a rotação de
  chave por padrão**.
- **Nunca guarde a chave no mesmo lugar do backup do banco.** Junto, é o mesmo que
  não cifrar.

---

## 4. Autenticação e autorização

| Recurso | Edição | Observação |
|---|---|---|
| Usuário/senha local | Community | Padrão |
| **MFA (TOTP)** | Community | Ligue. Há política de instância para **exigir** MFA |
| Verificação de e-mail | Community | `Verify user emails` |
| **SSO SAML / OIDC** | **Enterprise** | Integra com o IdP da empresa |
| LDAP | **Enterprise** | |
| **RBAC / projetos** | **licenciado** | Sem isso, todo mundo vê tudo |
| Log de auditoria e streaming | **Enterprise** | |
| Cofre externo de segredos | **Enterprise** | Vault, AWS Secrets Manager |

> **Consequência prática que muita gente descobre tarde:** na edição Community,
> **não há separação real entre usuários**. Se cinco pessoas usam a mesma instância,
> as cinco alcançam todas as credenciais. Para times com times, ou você licencia, ou
> **sobe instâncias separadas** — que é uma alternativa legítima e barata.

---

## 5. SQL, comandos e injeção

**Sempre parametrize.**

```
❌  SELECT * FROM clientes WHERE email = '{{ $json.email }}'
✅  SELECT * FROM clientes WHERE email = $1      + Query Parameters
```

O primeiro entrega o banco a quem mandar `x' OR '1'='1`. Vale igual para:

- **Comandos de shell** (nó Execute Command) — evite; se for inevitável, valide com
  lista de permissão, nunca de bloqueio.
- **HTML** montado por expressão — risco de XSS quando renderizado em algum lugar.
- **URLs** montadas com entrada externa — risco de SSRF (adiante).

---

## 6. SSRF

*Server-Side Request Forgery*: um fluxo que aceita uma URL de fora e a chama pode
ser usado para alcançar a **rede interna** — inclusive endpoints de metadados de
nuvem (`169.254.169.254`), que devolvem credenciais de instância.

```
❌  HTTP Request com URL = {{ $json.body.callback_url }}
```

Defesas, em ordem:

1. **Não aceite URL de fora.** Aceite um identificador e monte a URL você.
2. Ligue a **proteção SSRF** do n8n
   ([Enable SSRF protection](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/enable-ssrf-protection.md)).
3. Segmente a rede: o contêiner do n8n não deveria alcançar sua rede interna.
4. Lista de permissão de domínios, validada em Code antes da chamada.

---

## 7. Reduzir a superfície

```yaml
environment:
  # bloqueia nós perigosos numa instância multiusuário
  NODES_EXCLUDE: '["n8n-nodes-base.executeCommand","n8n-nodes-base.readWriteFile"]'
  # expressões não leem variáveis de ambiente
  N8N_BLOCK_ENV_ACCESS_IN_NODE: "true"
  # desliga a API pública se ninguém a usa
  N8N_PUBLIC_API_DISABLED: "true"
  # sem telemetria
  N8N_DIAGNOSTICS_ENABLED: "false"
  # permissão restrita no arquivo de config
  N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS: "true"
```

**`Execute Command` é o nó mais perigoso do catálogo:** ele roda comandos no
contêiner do n8n. Numa instância com mais de uma pessoa, bloqueie.

---

## 8. Dados de execução são um passivo

Cada execução guarda **tudo o que passou** por cada nó — CPF, cartão, token no
cabeçalho. Isso é ótimo para depurar e é um problema de conformidade (LGPD/GDPR).

Medidas:

| Medida | Como |
|---|---|
| Reduzir a retenção | `EXECUTIONS_DATA_MAX_AGE` curto |
| Não salvar sucessos | *Settings → Save successful production executions: off* |
| **Redigir campos sensíveis** | Recurso *Redact execution data* |
| Não trafegar o que não precisa | Um `Edit Fields` que descarta campos logo na entrada |

> **Padrão profissional que recomendo:** o **primeiro** nó depois do gatilho deve
> reduzir o item ao mínimo necessário. O que não entra no fluxo não é guardado, não
> vaza e não precisa ser redigido depois.

---

## 9. Auditoria

```bash
docker compose exec n8n n8n audit
```

Verifica credenciais não usadas, nós arriscados, instância desatualizada,
permissões de arquivo, configurações frouxas. **Rode antes de cada revisão de
segurança** — é gratuito e leva segundos.

Complementos:

- Log de auditoria e *log streaming* (Enterprise) para SIEM.
- Versione os workflows em Git ([23](23-ciclo-de-vida-e-versionamento.md)) — assim
  existe histórico de quem mudou o quê.

---

## 10. Community nodes e cadeia de suprimentos

Um nó da comunidade é um pacote npm executado **com os privilégios do n8n**.
Ele pode ler credenciais e falar com qualquer host.

- `N8N_UNVERIFIED_PACKAGES_ENABLED` controla pacotes não verificados. O n8n **já
  avisa no log da 2.36.9** que o padrão dessa variável **mudará para `false`**.
- Fixe versões. Não instale nó da comunidade em produção sem revisar o código.
- Alternativa quase sempre melhor: `HTTP Request`.

---

## 11. Checklist de segurança para produção

- [ ] HTTPS por proxy reverso; a porta 5678 não está exposta na internet.
- [ ] `N8N_ENCRYPTION_KEY` definida, guardada em cofre, **fora** do backup do banco.
- [ ] Task runners em **modo externo**, com limites de CPU/memória e rede restrita.
- [ ] `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`.
- [ ] Todos os webhooks autenticados (HMAC ou header auth).
- [ ] MFA exigido; verificação de e-mail ligada.
- [ ] Proteção SSRF ligada; o contêiner não alcança a rede interna sem necessidade.
- [ ] `NODES_EXCLUDE` bloqueia `executeCommand` e afins.
- [ ] API pública desligada, ou com chaves rotacionadas.
- [ ] Retenção de execuções curta; campos sensíveis redigidos ou nunca coletados.
- [ ] `n8n audit` roda periodicamente e alguém lê o resultado.
- [ ] Atualizações acompanhadas (o n8n lança quase toda semana).
- [ ] Se há mais de um time: RBAC licenciado **ou** instâncias separadas.
- [ ] Backup testado, com restauração exercitada de verdade.

---

## Autoteste

1. Enuncie o modelo de ameaça do n8n em uma frase.
2. Por que a chave de criptografia não pode ficar junto do backup do banco?
3. Na edição Community, cinco pessoas na mesma instância compartilham o quê?
4. Escreva a forma segura de consultar por e-mail no nó Postgres.
5. O que é SSRF e por que `169.254.169.254` é o alvo clássico?
6. Cite quatro defesas contra SSRF, em ordem.
7. Por que `Execute Command` é o nó mais perigoso?
8. Qual é o padrão recomendado para reduzir o passivo dos dados de execução?
9. O que `n8n audit` verifica?
10. Qual o risco real de um nó da comunidade, e a alternativa quase sempre melhor?

---

*Fontes consultadas em 01/09/2026: [Security](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security.md),
[Harden task runners](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/harden-task-runners.md),
[Enable SSRF protection](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/enable-ssrf-protection.md),
[Rotate encryption keys](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/rotate-encryption-keys.md),
[Run security audits](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/run-security-audits.md),
[v3.0 breaking changes](https://docs.n8n.io/changelog/v30-breaking-changes).*

*Anterior: [21-escala-e-producao.md](21-escala-e-producao.md) · Próximo: [23-ciclo-de-vida-e-versionamento.md](23-ciclo-de-vida-e-versionamento.md)*
