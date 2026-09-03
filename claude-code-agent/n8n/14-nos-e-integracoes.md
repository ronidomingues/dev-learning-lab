# 14 · Nós, integrações e credenciais

`Nível: intermediário` · `n8n 2.36.9 — 910 tipos de nó na instalação padrão` · `01/09/2026`

---

Número verificado: a instalação padrão do n8n 2.36.9 registra **910 tipos de nó**
(`n8n export:nodes` devolveu `Found 910 node types`). Ninguém decora isso, e não
precisa: o que se decora é a **taxonomia** e as **cinco perguntas** da seção 6.

---

## 1. Anatomia de um nó

Todo nó tem quatro partes:

```
┌──────────────────────────────────────────────┐
│  NOME (você escolhe — vira chave de expressão)│
│  TIPO + typeVersion  (n8n-nodes-base.postgres 2.6)
│  PARÂMETROS  (resource → operation → campos)  │
│  CREDENCIAL  (referência, nunca o segredo)    │
│  SETTINGS    (retry, onError, alwaysOutputData)│
└──────────────────────────────────────────────┘
```

**O padrão `resource → operation`** organiza quase todo nó de app: primeiro você
escolhe *sobre o quê* (mensagem, canal, usuário) e depois *o que fazer* (criar,
buscar, atualizar, apagar). Reconhecer esse padrão faz você usar um nó novo sem ler
documentação.

---

## 2. Os nós que você usa todo dia

### `HTTP Request` — o mais importante de todos

Se você domina este nó, o catálogo de integrações deixa de ser uma limitação.
Qualquer serviço com API REST é alcançável.

| Recurso | Por que importa |
|---|---|
| **Authentication → Predefined** | Reaproveita a credencial de um serviço conhecido (inclusive o OAuth já negociado) sem que exista um nó dedicado para aquela operação |
| **Authentication → Generic** | Header Auth, Basic, Query Auth, OAuth2, OAuth1 |
| **Pagination** | Paginação automática por página, cursor ou link `next` |
| **Batching** | *Items per Batch* + *Batch Interval*: respeita limite de taxa sem laço |
| **Retry On Fail** | Nas *Settings* do nó |
| **Never Error** | Não falha em 4xx/5xx; você trata o status como dado |
| **Response → Include Response Headers and Status** | Necessário para lógica baseada em status |
| **Import cURL** | Cola um comando `curl` e ele preenche o nó inteiro. **Use sempre** |

> **Dica que economiza horas:** pegue o exemplo `curl` da documentação da API,
> clique em *Import cURL* e cole. Método, cabeçalhos, corpo e query vêm prontos.

### `Edit Fields (Set)`

Criar, renomear, remover campos e **fixar tipos**. Prefira-o a um Code node de
três linhas: é legível para quem não programa e não quebra item linking.

Opção *Include Other Input Fields*: decide se o resto do item continua passando.
Esquecer isso é a causa de "meus campos sumiram no meio do fluxo".

### `Code`

Ver [17-code-node-e-task-runners.md](17-code-node-e-task-runners.md).

### `Postgres` / `MySQL` / `MongoDB`

Operações: `Execute Query`, `Insert`, `Update`, `Upsert`, `Select`, `Delete`.

> **Sempre use *Query Parameters* (`$1`, `$2`) em vez de interpolar.** É a diferença
> entre um `WHERE` e uma injeção de SQL. Exemplo real no
> [projeto-modelo](07-projeto-modelo/workflows/02-consultar-pedido.json).

---

## 3. Credenciais

### 3.1 Como funcionam

Uma credencial é um registro **cifrado** no banco com `N8N_ENCRYPTION_KEY`
(AES). O workflow guarda só `{ id, name }`. Isso significa:

| Consequência | Detalhe |
|---|---|
| Exportar workflow **não vaza segredo** | Pode mandar o JSON por e-mail |
| Importar workflow deixa a credencial "faltando" | É preciso recriar ou importar à parte |
| Perder a chave = perder tudo | Backup do banco sem a chave é inútil |
| A mesma credencial serve a vários workflows | E, nos planos pagos, tem RBAC |

### 3.2 Tipos e o que muda entre eles

| Tipo | Como funciona | Cuidado |
|---|---|---|
| **API Key em header** | Você cola a chave | Rotacione; chave não expira sozinha |
| **Basic Auth** | Usuário e senha | Só sobre HTTPS |
| **Bearer / JWT** | Token | Tem validade — o nó não renova sozinho a menos que a credencial seja OAuth |
| **OAuth 2.0** | O n8n faz o *authorization code flow*, guarda o refresh token e renova | Exige **URL de callback pública** |
| **Certificado (mTLS)** | Par de chaves | Ver o curso [`tls/`](../tls/00-MAPA.md) |
| **Cofre externo** | AWS Secrets Manager, Vault, etc. | Recurso **Enterprise** |

### 3.3 A dor do OAuth 2.0 em instância local

O provedor (Google, Microsoft, Slack) precisa **redirecionar o navegador de volta**
para o seu n8n depois do consentimento. Se seu n8n é `http://localhost:5678`, o
provedor não alcança — e muitos exigem HTTPS.

Três saídas, em ordem de preferência:

1. **Domínio com HTTPS** (produção): `WEBHOOK_URL=https://n8n.seu.dominio/` e o
   redirect URI cadastrado no provedor.
2. **Túnel** (Cloudflare Tunnel/ngrok) para desenvolvimento — a URL muda a cada
   sessão, então recadastre o redirect a cada vez.
3. **Credencial genérica com token manual**: obtenha o token por fora e use
   Header Auth. Funciona, mas você fica responsável por renovar.

> O redirect URI que o n8n espera aparece **na própria tela da credencial**.
> Copie de lá, não invente.

### 3.4 Gerir credenciais como código

Sem os recursos licenciados de *source control* e *external secrets*, o caminho é a CLI:

```bash
# exportar (⚠️ --decrypted grava segredo em texto claro)
docker compose exec n8n n8n export:credentials --all --decrypted --output=/tmp/cred.json

# importar em outra instância
docker compose exec -T n8n n8n import:credentials --input=/import/credenciais/postgres.json
```

**Verificado na prática:** o `import:credentials` aceita um JSON **em texto claro**
no formato `[{ id, name, type, data: {...} }]` e cifra na importação. É assim que o
[projeto-modelo](07-projeto-modelo/README.md) provisiona a credencial do Postgres
sem passo manual.

**Sem `--decrypted`**, o arquivo sai cifrado e só serve numa instância com a
**mesma** `N8N_ENCRYPTION_KEY`.

---

## 4. Community nodes

Além dos nós oficiais, há pacotes npm da comunidade instaláveis pela interface
(*Settings → Community nodes*) ou por variável de ambiente.

**Antes de instalar um, responda:**

1. Quantos downloads e quando foi o último commit?
2. O código está publicado e é legível?
3. **Um nó da comunidade roda com os mesmos privilégios do n8n.** Ele pode ler suas
   credenciais e fazer requisições para onde quiser. Você confia nesse autor?

> Instalar um nó da comunidade é equivalente, em confiança, a instalar uma
> dependência npm em produção — porque é literalmente isso. A variável
> `N8N_UNVERIFIED_PACKAGES_ENABLED` controla pacotes não verificados, e o próprio
> n8n avisa que **o padrão dela mudará para `false`** numa versão futura.
> (Aviso literal visto no log da versão 2.36.9.)

**Alternativa quase sempre melhor:** montar a integração com `HTTP Request`. Sem
dependência, sem risco de abandono, e você entende o que está acontecendo.

---

## 5. Quando não existe nó para o seu serviço

Em ordem de esforço:

1. **HTTP Request** com credencial genérica. Resolve 95% dos casos.
2. **HTTP Request** com *Predefined Credential Type* — se existe uma credencial
   daquele serviço mas não a operação que você quer, você reaproveita o OAuth.
3. **Community node**, se existir e for confiável.
4. **Escrever seu próprio nó** (TypeScript, `n8n-node-dev`) — vale a pena só se for
   usar em muitos fluxos e por muito tempo. Ver [95-referencias.md](95-referencias.md).

---

## 6. As cinco perguntas antes de usar qualquer nó novo

Um método que funciona para qualquer um dos 910:

1. **Qual é o `resource` e a `operation`?** (o que ele sabe fazer)
2. **Quantos itens ele consome e quantos produz?** (cardinalidade — arquivo [12](12-o-modelo-de-dados.md))
3. **Ele tem paginação/batching embutidos?** (antes de escrever laço)
4. **O que ele faz quando não encontra nada?** (zero itens ou erro?)
5. **O que ele faz quando falha — e é seguro repetir?** (idempotência — arquivo [18](18-erros-e-confiabilidade.md))

Quem responde essas cinco antes de arrastar o nó não escreve fluxo frágil.

---

## Autoteste

1. Quantos tipos de nó tem a instalação padrão? Você precisa conhecê-los?
2. Explique o padrão `resource → operation`.
3. Cite três recursos do HTTP Request que evitam escrever código.
4. O que é *Import cURL* e por que é o atalho mais subestimado da ferramenta?
5. Uma credencial fica dentro do workflow? O que fica?
6. Por que OAuth 2.0 é difícil em `localhost`, e quais as três saídas?
7. Qual o formato aceito pelo `import:credentials` em texto claro?
8. Qual o risco real de instalar um nó da comunidade?
9. Você precisa integrar um serviço sem nó dedicado. Qual a ordem de tentativas?
10. Enuncie as cinco perguntas antes de usar um nó novo.

---

*Anterior: [13-expressoes.md](13-expressoes.md) · Próximo: [15-fluxo-de-controle.md](15-fluxo-de-controle.md)*
