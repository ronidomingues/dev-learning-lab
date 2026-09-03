# Projeto-modelo — Biblioteca

`Nível: intermediário` · `Última atualização: 11/08/2026`

Uma aplicação **pequena porém inteira**: uma biblioteca com livros, autores, exemplares físicos,
membros e empréstimos. Modela relações de verdade, defende regras de negócio **no banco**, e tem
uma API e testes de integração contra um PostgreSQL real.

Não é um trecho de SQL solto. É o esqueleto do que você encontraria numa aplicação real, reduzido
ao mínimo que ainda ensina.

---

## O que este projeto ensina

| Conceito | Onde está |
|---|---|
| Chaves primárias com `GENERATED ALWAYS AS IDENTITY` | [`schema/001_schema.sql`](schema/001_schema.sql) |
| Chave estrangeira e `ON DELETE CASCADE`/`RESTRICT` | `001_schema.sql` |
| Relação muitos-para-muitos (tabela de junção) | `livros_autores` em `001_schema.sql` |
| Distinguir a obra (livro) do objeto físico (exemplar) | `001_schema.sql` |
| Restrições `CHECK`, `UNIQUE`, `NOT NULL` | `001_schema.sql` |
| **Índice único parcial** para regra de negócio | "um empréstimo aberto por exemplar" |
| Índices B-tree, GIN (JSONB), por expressão, parciais | `001_schema.sql` |
| View | `livros_disponiveis` |
| Funções PL/pgSQL com regras e transação | [`schema/002_functions.sql`](schema/002_functions.sql) |
| `FOR UPDATE`, tratamento de exceção, `RAISE` | `002_functions.sql` |
| Consultas parametrizadas (anti-SQL-injection) | [`app/src/db.js`](app/src/db.js) |
| Pool de conexões | `app/src/db.js` |
| Transação no código da aplicação | `cadastrarLivro` em [`app/src/repositorio.js`](app/src/repositorio.js) |
| `array_agg ... FILTER`, subconsulta correlacionada | `listarLivros` |
| Testes de integração contra Postgres real | [`app/test/biblioteca.test.js`](app/test/biblioteca.test.js) |
| Schema aplicado por `docker-entrypoint-initdb.d` | [`compose.yaml`](compose.yaml) |
| Backup lógico verificado + retenção | [`scripts/backup.sh`](scripts/backup.sh) |

---

## Modelo de dados

```
   autores ──┐                          ┌── membros
             │ (muitos-para-muitos)     │
        livros_autores                  │
             │                          │
          livros ──< exemplares ──< emprestimos >──┘
          (a obra)   (cópia física)   (quem pegou, quando, devolveu?)
```

Decisão central: **`livros` é o título; `exemplares` é a cópia física.** Uma biblioteca tem três
cópias de "Dom Casmurro" — um livro, três exemplares. Você empresta um **exemplar**, não o livro.
Confundir os dois é o erro de modelagem nº 1 em sistemas assim, e o projeto o evita de propósito.

---

## Pré-requisitos

- **Docker** e **Docker Compose v2** (o caminho recomendado — sobe tudo com um comando).
  Alternativamente, um PostgreSQL 18 local e Node 22+.
- Ver o curso de Docker em [`../../docker`](../../docker/00-MAPA.md) se precisar.

---

## Como rodar — comandos exatos

### Com Docker (recomendado)

```bash
cd homelab/learn-process/postgresql/07-projeto-modelo

# 1. Configuração
cp .env.example .env        # edite a senha se quiser

# 2. Subir (o schema é aplicado automaticamente na primeira inicialização do banco)
docker compose up -d --build
#    equivalente:  make subir

# 3. Verificar a API
curl -s http://localhost:3000/saude          # {"status":"ok"}
curl -s http://localhost:3000/livros | jq    # os livros do seed, com autores

# 4. Emprestar um exemplar (use um exemplar_id disponível; veja /livros e a view)
curl -s -X POST http://localhost:3000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"exemplar_id":1,"membro_id":1,"dias":7}'

# 5. Tentar emprestar o MESMO exemplar de novo → 409, o banco recusa
curl -s -X POST http://localhost:3000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"exemplar_id":1,"membro_id":2}'
# esperado: {"erro":"exemplar 1 já está emprestado","codigo":"indisponivel"}

# 6. Devolver
curl -s -X POST http://localhost:3000/devolucoes \
  -H 'Content-Type: application/json' -d '{"exemplar_id":1}'

# 7. Abrir um psql para explorar
make psql
#    dentro:  SELECT * FROM livros_disponiveis;  ·  SELECT * FROM emprestimos_atrasados();
```

### Com PostgreSQL local (sem Docker)

```bash
createdb biblioteca
psql -d biblioteca -v ON_ERROR_STOP=1 \
  -f schema/001_schema.sql -f schema/002_functions.sql -f schema/003_seed.sql

# a aplicação:
cd app && npm install
DATABASE_URL="postgres://SEU_USUARIO@localhost:5432/biblioteca" npm start
```

### Rodar os testes

```bash
make testes
#    equivalente:  docker compose --profile testes run --rm testes
# ou, com banco local:
cd app && DATABASE_URL="postgres://...@localhost:5432/biblioteca" npm test
```

---

## Estrutura de pastas

```
07-projeto-modelo/
├── compose.yaml              # PostgreSQL 18 + app, com perfil de testes
├── .env.example              # copie para .env
├── Makefile                  # atalhos
├── schema/
│   ├── 001_schema.sql        # tabelas, restrições, índices, view
│   ├── 002_functions.sql     # emprestar(), devolver(), emprestimos_atrasados()
│   └── 003_seed.sql          # dados de exemplo
├── scripts/
│   └── backup.sh             # backup lógico verificado + retenção
└── app/
    ├── Dockerfile
    ├── package.json          # usa a biblioteca 'pg' (node-postgres)
    ├── src/
    │   ├── db.js             # pool de conexões, consultas parametrizadas, transação
    │   ├── repositorio.js    # todas as queries da aplicação
    │   └── server.js         # API HTTP mínima
    └── test/
        └── biblioteca.test.js # testes de integração contra Postgres real
```

---

## O que cada decisão de projeto ensina

### 1. A regra de negócio mora no banco, não só no código

"Um exemplar não pode ter dois empréstimos abertos" é garantido por um **índice único parcial**:

```sql
CREATE UNIQUE INDEX ix_um_emprestimo_aberto_por_exemplar
    ON emprestimos (exemplar_id) WHERE devolvido_em IS NULL;
```

*O que se aprende:* a aplicação pode ter um bug, ser reescrita, ou ganhar um segundo cliente
(um script, outra API) que esquece a regra. O banco **nunca** esquece. Mil requisições
simultâneas para emprestar o mesmo exemplar — só uma vence, garantido pelo índice, sem você
escrever lógica de bloqueio.

### 2. Livro ≠ exemplar

*O que se aprende:* modelar a diferença entre a coisa abstrata (o título) e a coisa concreta (a
cópia) é o que separa um modelo que funciona de um que trava no primeiro caso real ("como empresto
uma das três cópias?").

### 3. Consultas sempre parametrizadas

```js
query('SELECT ... WHERE titulo LIKE $1', [busca]);   // ✅ nunca concatene
```

*O que se aprende:* `"... WHERE nome = '" + entrada + "'"` é a porta aberta para **SQL injection**
— a vulnerabilidade que vaza bancos inteiros. Parâmetros (`$1`, `$2`) separam código de dado, e o
banco trata a entrada como valor, nunca como comando. Também deixa o Postgres reusar o plano.

### 4. Pool de conexões, com `release()` garantido

*O que se aprende:* cada conexão é um **processo** no servidor Postgres (`max_connections`, padrão
100). Abrir uma por requisição derruba o banco sob carga. O pool reaproveita; e esquecer o
`release()` (no `finally`) vaza conexões até esgotar — um dos bugs de produção mais comuns.

### 5. Transação: cadastrar livro + autores é tudo-ou-nada

*O que se aprende:* se a criação do segundo autor falhar, o livro e o primeiro autor **não** podem
ficar de pé. `comTransacao` envolve tudo num `BEGIN`/`COMMIT`, com `ROLLBACK` automático no erro.

### 6. Funções no banco vs. lógica na aplicação — o debate honesto

O projeto faz os **dois**, de propósito, para você comparar:
- `emprestar()`/`devolver()` são **funções no banco** — beneficiam-se de atomicidade e de estar
  perto dos dados travados (`FOR UPDATE`).
- `cadastrarLivro()` é **transação no código** — mais visível para quem lê a aplicação.

*Opinião profissional:* lógica no banco é atômica e à prova de "a aplicação esqueceu", mas é
**invisível** para quem lê só o código — e mais difícil de versionar e testar. Regra prática:
ponha no banco o que precisa de garantia absoluta de integridade e atomicidade; deixe no código a
lógica de negócio que muda com frequência. Não há resposta única, e equipes divergem — o
importante é decidir conscientemente, não por acidente.

---

## Laboratórios com este projeto

### Lab 1 — O banco defende a regra
```bash
make psql
```
```sql
-- Empreste um exemplar
SELECT emprestar(1, 1, 7);
-- Tente de novo o mesmo exemplar: FALHA
SELECT emprestar(1, 2, 7);       -- ERROR: exemplar 1 já está emprestado
-- Veja que ele sumiu da lista de disponíveis
SELECT * FROM livros_disponiveis WHERE exemplar_id = 1;   -- 0 linhas
-- Devolva e ele volta
SELECT devolver(1);
SELECT * FROM livros_disponiveis WHERE exemplar_id = 1;   -- 1 linha
```

### Lab 2 — Transação tudo-ou-nada
```sql
BEGIN;
  DELETE FROM emprestimos;      -- opa
  SELECT count(*) FROM emprestimos;   -- 0
ROLLBACK;                        -- desfaz
SELECT count(*) FROM emprestimos;     -- voltou
```

### Lab 3 — Ver o plano de uma consulta
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM livros_disponiveis WHERE titulo LIKE 'Dom%';
-- observe se usa o índice ix_livros_titulo_lower (dica: a view filtra por título)
```

### Lab 4 — Atrasos
```sql
-- Crie um empréstimo já vencido, direto:
INSERT INTO emprestimos (exemplar_id, membro_id, vence_em, emprestado_em)
VALUES (2, 1, current_date - 5, now() - interval '20 days');
SELECT * FROM emprestimos_atrasados();
```

### Lab 5 — Backup e restauração
```bash
make backup
make limpar          # apaga o volume
make subir           # recria (schema + seed)
docker compose exec -T db pg_restore -U biblioteca -d biblioteca --clean --if-exists < backups/biblioteca_*.dump
```

### Lab 6 — SQL injection (por que os parâmetros importam)
Tente, no `repositorio.js`, trocar a query parametrizada por concatenação e passe uma busca como
`'; DROP TABLE livros; --`. **Faça isso só neste laboratório descartável** para ver o estrago — e
depois entenda por que o código real nunca faz isso.

---

## Verificação feita neste material

Transparência sobre o que foi e o que não foi testado no ambiente de escrita:

- ✅ **A sintaxe JavaScript** de `db.js`, `repositorio.js`, `server.js` e dos testes foi validada
  (`node --check`), e a suíte **roda e pula corretamente** quando `DATABASE_URL` não está definida
  (5 testes, 0 falhas, 5 pulados) — comportamento intencional: o teste diz o que precisa em vez de
  falhar com erro de conexão confuso.
- ⚠️ **O SQL (`schema/*.sql`) e os testes de integração NÃO puderam ser executados contra um
  PostgreSQL real** no ambiente de escrita, porque não havia servidor Postgres nem acesso ao Docker
  daemon aqui. O SQL segue a documentação oficial do PostgreSQL 18 na data (11/08/2026), mas
  **rode-o você mesmo** com `make subir` + `make testes` e trate qualquer divergência como parte do
  aprendizado. O material não afirma o que não verificou.
- 📌 Se algum comando falhar na sua máquina, o problema é local (versão, permissão, porta) —
  comece pelo log: `docker compose logs db`.

---

## Autoteste

1. Por que a regra "um empréstimo aberto por exemplar" está no banco e não só no código?
2. Qual é a diferença entre `livros` e `exemplares`, e por que ela importa?
3. Por que consultas parametrizadas (`$1`) previnem SQL injection?
4. O que acontece se você esquecer o `cliente.release()` no pool, e onde ele está garantido?
5. Quando a regra de negócio deve ir para uma função no banco, e quando para o código?
6. O que o índice único **parcial** (`WHERE devolvido_em IS NULL`) permite que um índice único
   comum não permitiria?
7. Por que `devolver()` é idempotente, e por que isso é bom?
8. Como o schema é aplicado automaticamente quando o container do Postgres sobe pela primeira vez?
9. Por que o backup é feito com `pg_dump -Fc` e verificado com `pg_restore --list`?
