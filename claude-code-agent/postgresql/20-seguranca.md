# 20 · Segurança

`Nível: avançado` · `Última atualização: 11/08/2026`

Um banco guarda o ativo mais sensível de uma organização. Este arquivo cobre autenticação,
autorização, criptografia e as armadilhas — em ordem de retorno sobre o esforço.

---

## 1. As camadas de segurança

A segurança do PostgreSQL é em camadas, cada uma respondendo a uma pergunta:

| Camada | Pergunta | Mecanismo |
|---|---|---|
| **Rede** | Quem pode alcançar a porta? | Firewall, `listen_addresses`, VPN |
| **Autenticação** | Quem é você? | `pg_hba.conf`, senhas, certificados |
| **Autorização** | O que você pode fazer? | Roles, `GRANT`/`REVOKE` |
| **Row-Level Security** | Quais **linhas** você pode ver? | Políticas RLS |
| **Criptografia** | Se roubarem o disco/tráfego? | TLS, criptografia em repouso |
| **Auditoria** | Quem fez o quê? | Logs, `pgaudit` |

---

## 2. Rede — a primeira barreira, e a mais violada

```conf
# postgresql.conf
listen_addresses = 'localhost'   # padrão seguro; só conexões locais
# listen_addresses = '*'         # todas as interfaces — só com pg_hba.conf restritivo!
```

> ### ⚠️ O incidente mais comum: PostgreSQL exposto na internet
> Um PostgreSQL com `listen_addresses = '*'`, porta 5432 aberta na internet e uma senha fraca é
> comprometido em **horas**. Varreduras automatizadas caçam a porta 5432 dia e noite, testam senhas
> comuns, e ao entrar exfiltram ou criptografam os dados (ransomware). Isso acontece o tempo todo.
>
> **As defesas, em ordem:**
> 1. **Não exponha o banco.** Mantenha-o numa rede privada; a aplicação conecta de dentro. Acesso
>    administrativo por **SSH** ou **VPN**, nunca pela porta 5432 aberta.
> 2. **Firewall** permitindo só os IPs necessários.
> 3. **`pg_hba.conf` restritivo** (abaixo).
> 4. **Senhas fortes** e `scram-sha-256`.
> 5. **TLS** obrigatório.

---

## 3. Autenticação — o `pg_hba.conf`

O `pg_hba.conf` (*Host-Based Authentication*) é a lista de controle de acesso: cada linha diz
**quem** pode conectar, a **qual** banco, **de onde**, e **como** provar identidade. Avaliado de
cima para baixo; a primeira linha que casa decide.

```conf
# TYPE  DATABASE  USER    ADDRESS          METHOD
local   all       all                      peer            # socket local: usa o usuário do SO
host    loja      app     10.0.0.0/24      scram-sha-256   # rede interna, senha moderna
hostssl loja      app     0.0.0.0/0        scram-sha-256   # de qualquer lugar, MAS só com SSL
host    all       all     0.0.0.0/0        reject          # nega o resto explicitamente
```

Os métodos, do melhor ao pior:

| Método | Segurança | Uso |
|---|---|---|
| `cert` | Certificado de cliente (TLS mútuo) | Máxima; automação, serviços |
| `scram-sha-256` | Senha com hash forte | **O padrão recomendado hoje** |
| `peer` / `ident` | Usa o usuário do SO | Conexões locais confiáveis |
| `ldap`, `gss`, `radius` | Integração corporativa | SSO empresarial |
| `md5` | Senha com hash fraco | **Legado — migre para scram** |
| `password` | Senha em texto puro | **Nunca** |
| `trust` | Sem verificação | **Só** em socket local de laboratório |

> **PG 18 trouxe autenticação OAuth**, permitindo integrar com provedores de identidade modernos
> (login federado) — relevante para ambientes que já usam OAuth/OIDC.

Depois de editar, recarregue: `SELECT pg_reload_conf();`.

---

## 4. Autorização — roles e privilégios

No PostgreSQL, usuários e grupos são a mesma coisa: **roles**. Um role pode ter login (é um
"usuário") ou não (é um "grupo"), e roles herdam privilégios de outros.

```sql
-- Princípio do menor privilégio: a aplicação NÃO deve ser superusuário
CREATE ROLE app LOGIN PASSWORD 'forte';
CREATE ROLE leitura NOLOGIN;              -- grupo
CREATE ROLE escrita NOLOGIN;

GRANT CONNECT ON DATABASE loja TO app;
GRANT USAGE ON SCHEMA public TO leitura, escrita;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO leitura;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO escrita;
GRANT leitura, escrita TO app;            -- app herda os dois

-- Privilégios para tabelas FUTURAS (senão você regrant a cada tabela nova)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO leitura;
```

> **A regra de ouro: a aplicação nunca conecta como superusuário nem como o dono das tabelas.**
> Ela usa um role com **só** os privilégios de que precisa. Assim, uma falha de SQL injection ou um
> bug não pode `DROP TABLE`, criar usuários ou ler o que não deve. O superusuário é para
> administração, não para o dia a dia.

Privilégios concedíveis: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`,
`TRIGGER` (tabelas); `USAGE`, `CREATE` (esquemas); `CONNECT`, `TEMP` (bancos); `EXECUTE` (funções).

```sql
REVOKE INSERT ON clientes FROM escrita;
\dp clientes           -- ver os privilégios atuais (no psql)
```

---

## 5. Row-Level Security (RLS) — filtrar por linha

`GRANT` controla acesso a **tabelas inteiras**. A **RLS** controla acesso a **linhas específicas** —
essencial para multi-inquilino (cada cliente vê só seus dados) sem confiar só na aplicação.

```sql
ALTER TABLE pedidos ENABLE ROW LEVEL SECURITY;

-- Cada usuário só vê os pedidos da sua empresa
CREATE POLICY pedidos_da_empresa ON pedidos
    USING (empresa_id = current_setting('app.empresa_id')::bigint);

-- A aplicação define a variável a cada conexão/transação:
SET app.empresa_id = '42';
SELECT * FROM pedidos;   -- retorna SÓ os da empresa 42, mesmo sem WHERE
```

RLS é aplicada pelo **banco**, então vale para toda consulta, de qualquer cliente — a aplicação não
pode "esquecer" o filtro. É a forma correta de isolar inquilinos no mesmo banco. Cuidado:
superusuários e o dono da tabela ignoram RLS por padrão (há `FORCE ROW LEVEL SECURITY` para o
dono).

---

## 6. Criptografia

**Em trânsito (TLS):** cifra a conexão entre cliente e servidor. Configure `ssl = on` e certificados
no `postgresql.conf`, e exija com `hostssl` no `pg_hba.conf`. Do lado do cliente,
`sslmode=require` (ou `verify-full`, que também valida o certificado do servidor — o ideal).

**Em repouso (o disco):** o PostgreSQL não tem criptografia de disco embutida (TDE) no núcleo open
source. As opções:
- **Criptografia no nível do sistema de arquivos/volume** (LUKS no Linux, criptografia do provedor
  de nuvem) — a abordagem padrão e recomendada.
- **`pgcrypto`** para cifrar **colunas** específicas (dados muito sensíveis, como tokens).
- Distribuições comerciais (EDB, etc.) oferecem TDE integrado.

```sql
CREATE EXTENSION pgcrypto;
-- Guardar senha com hash (nunca em texto puro)
INSERT INTO usuarios (login, senha_hash) VALUES ('ana', crypt('senha', gen_salt('bf')));
SELECT * FROM usuarios WHERE login='ana' AND senha_hash = crypt('senha', senha_hash);
```

> **Senhas de usuários da aplicação nunca em texto puro.** Use `crypt()` com bcrypt (`gen_salt('bf')`)
> ou faça o hash na aplicação. E **nunca** logue senhas nem dados sensíveis.

---

## 7. Auditoria

```sql
-- Log básico via postgresql.conf
-- log_statement = 'ddl'        -- registra mudanças de esquema
-- log_connections = on
-- log_disconnections = on

-- pgaudit: auditoria detalhada e granular (extensão)
CREATE EXTENSION pgaudit;
```

`pgaudit` registra quem executou o quê, com detalhe suficiente para conformidade (LGPD, GDPR,
PCI-DSS). O log de auditoria deve ir para um destino que o próprio administrador do banco não possa
apagar sem deixar rastro.

---

## 8. As armadilhas de segurança

| Armadilha | Correção |
|---|---|
| **Banco exposto na internet** | Rede privada; acesso por SSH/VPN; nunca 5432 aberto |
| **App conecta como superusuário** | Role com privilégio mínimo |
| **SQL injection** | **Consultas parametrizadas** (`$1`), sempre — ver [projeto-modelo](07-projeto-modelo/README.md) |
| **Senha no código / no Git** | Variáveis de ambiente, `.pgpass`, gerenciador de segredos |
| **`trust` no pg_hba.conf** | Só em socket local de laboratório |
| **`md5` legado** | Migrar para `scram-sha-256` |
| **Sem TLS** | `sslmode=verify-full` no cliente, `hostssl` no servidor |
| **Backups sem criptografia** | Cifrar os backups; testar a restauração |
| **Multi-inquilino confiando só na app** | RLS no banco |
| **Superusuário para tudo** | Superusuário só para administração |

**SQL injection** merece destaque por ser a mais comum e a mais grave:
```sql
-- ❌ NUNCA: concatenar entrada do usuário
"SELECT * FROM users WHERE nome = '" + entrada + "'"
-- entrada = "'; DROP TABLE users; --"  → catástrofe

-- ✅ SEMPRE: parâmetros. O banco trata a entrada como VALOR, nunca como comando.
query("SELECT * FROM users WHERE nome = $1", [entrada]);
```

---

## 9. Checklist de segurança de produção

- [ ] Banco **não** exposto à internet; acesso admin por SSH/VPN
- [ ] Firewall restringindo IPs de origem
- [ ] `pg_hba.conf` restritivo, com `reject` explícito no fim
- [ ] `scram-sha-256` (não `md5`, não `trust`, não `password`)
- [ ] TLS obrigatório (`hostssl`), cliente com `sslmode=verify-full`
- [ ] Aplicação com role de **privilégio mínimo**, nunca superusuário
- [ ] `ALTER DEFAULT PRIVILEGES` configurado para tabelas futuras
- [ ] RLS onde há multi-inquilino
- [ ] Senhas de usuários com hash (bcrypt), nunca em texto puro
- [ ] Segredos fora do código e do Git
- [ ] Consultas **sempre** parametrizadas
- [ ] Backups criptografados e com restauração testada
- [ ] Auditoria (`pgaudit` ou logs) onde exigido por conformidade
- [ ] PostgreSQL e SO atualizados (patches de segurança)

---

## Autoteste

1. Cite as seis camadas de segurança e a pergunta que cada uma responde.
2. Por que um PostgreSQL exposto na internet com senha fraca é um incidente iminente, e como
   evitar?
3. O que o `pg_hba.conf` controla, e como suas linhas são avaliadas?
4. Ordene os métodos de autenticação do melhor ao pior, e diga qual é o padrão recomendado.
5. Por que a aplicação nunca deve conectar como superusuário?
6. O que a RLS resolve que o `GRANT` não resolve? Dê um exemplo de multi-inquilino.
7. Onde o PostgreSQL faz (e não faz) criptografia em repouso, e quais são as opções?
8. Por que consultas parametrizadas previnem SQL injection?
9. Por que uma senha de usuário nunca deve ser guardada em texto puro, e o que usar?
10. Percorra o checklist e aponte os três itens de maior impacto.
