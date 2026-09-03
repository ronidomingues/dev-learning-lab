# 04 · Como começar — do ambiente pronto ao primeiro banco

`Nível: iniciante` · `Tempo: 45–90 minutos` · `Última atualização: 11/08/2026`

Assume o ambiente instalado pelo [03-instalacao.md](03-instalacao.md). Se
`psql --version` não responde, volte lá. Se você está numa nuvem gratuita (Neon/Supabase), use a
string de conexão que eles te deram no lugar dos parâmetros locais.

Ao final você terá: entrado no `psql`, criado um banco e tabelas, inserido e consultado dados,
feito um JOIN, usado uma transação e entendido o ciclo de trabalho do dia a dia.

---

## Passo 1 — Entrar no `psql`

O `psql` é o terminal interativo do PostgreSQL. É onde você vai viver.

```bash
# Linux (autenticação peer, como superusuário)
sudo -u postgres psql

# Ou conectando a um banco e usuário seus, por rede
psql -h localhost -U seu_usuario -d meu_primeiro_banco

# macOS (Homebrew: você é o superusuário)
psql postgres

# Docker
docker exec -it pg psql -U postgres -d laboratorio
```

Você verá o prompt:
```
psql (18.x)
Type "help" for help.

meu_primeiro_banco=>
```

O `=>` indica usuário comum; `=#` indica superusuário. Guarde essa distinção — ela te avisa quando
você tem poder demais nas mãos.

### Os comandos do `psql` que começam com `\`

Comandos que começam com **barra invertida** (`\`) são do `psql`, não SQL. Os essenciais:

| Comando | O que faz |
|---|---|
| `\l` | Lista os bancos de dados |
| `\c banco` | Conecta a outro banco |
| `\dt` | Lista as tabelas |
| `\d tabela` | **Descreve** uma tabela (colunas, tipos, índices) — o mais usado |
| `\du` | Lista os usuários (*roles*) |
| `\dn` | Lista os esquemas |
| `\x` | Alterna exibição "expandida" (uma coluna por linha — ótimo para linhas largas) |
| `\timing` | Liga/desliga a medição de tempo das consultas |
| `\e` | Abre a última consulta num editor de texto |
| `\i arquivo.sql` | Executa um arquivo SQL |
| `\?` | Ajuda dos comandos `\` |
| `\h COMANDO` | Ajuda da **sintaxe SQL** (ex.: `\h SELECT`) |
| `\q` | Sai |

> **Guarde estes dois:** `\?` mostra os comandos do psql; `\h` mostra a sintaxe do SQL. Com eles,
> você nunca fica preso.

---

## Passo 2 — Criar um banco e tabelas

Se você ainda não tem um banco só seu, crie um (fora do psql, ou com `CREATE DATABASE`):

```sql
-- Dentro do psql (como superusuário ou usuário com permissão):
CREATE DATABASE loja;
\c loja
```

Agora as tabelas. Vamos modelar uma lojinha: **clientes** que fazem **pedidos**.

```sql
CREATE TABLE clientes (
    id         SERIAL PRIMARY KEY,        -- inteiro que se autoincrementa; identifica a linha
    nome       TEXT NOT NULL,             -- obrigatório
    email      TEXT UNIQUE NOT NULL,      -- obrigatório e único: dois clientes não têm o mesmo
    criado_em  TIMESTAMPTZ DEFAULT now()  -- preenchido automaticamente com a data/hora atual
);

CREATE TABLE pedidos (
    id          SERIAL PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES clientes(id),  -- CHAVE ESTRANGEIRA
    descricao   TEXT NOT NULL,
    valor       NUMERIC(10,2) NOT NULL CHECK (valor >= 0), -- dinheiro: nunca use float!
    criado_em   TIMESTAMPTZ DEFAULT now()
);
```

**Verifique:**
```sql
\dt
-- esperado: as tabelas 'clientes' e 'pedidos'
\d pedidos
-- esperado: as colunas, tipos, e as restrições (a chave estrangeira para clientes)
```

### Decisões que já ensinam muito

| Decisão | Por quê |
|---|---|
| `SERIAL PRIMARY KEY` | Cada linha precisa de identidade única. `SERIAL` gera o número sozinho. (No PG 18, veremos `uuidv7()` como alternativa moderna) |
| `TEXT NOT NULL` | `NOT NULL` proíbe deixar vazio. Ausência de valor é `NULL`, e `NULL` causa surpresas — ver [75-armadilhas.md](75-armadilhas.md) |
| `email TEXT UNIQUE` | O banco **garante** que não haja e-mail repetido. A aplicação não precisa checar |
| `REFERENCES clientes(id)` | A chave estrangeira: o banco **impede** um pedido para um cliente inexistente |
| `NUMERIC(10,2)` para dinheiro | `NUMERIC` é exato. `FLOAT`/`REAL` arredonda e você perde centavos — **nunca use float para dinheiro** |
| `CHECK (valor >= 0)` | Uma regra de negócio ("valor não é negativo") vivendo no banco, não só no código |

> **A lição central:** o banco não é um depósito passivo. Ele **defende a integridade dos dados**
> — chaves, unicidade, `NOT NULL`, `CHECK`. Coisa que você teria de reimplementar (e esquecer) em
> cada aplicação, ele garante uma vez, para todas. Isso é metade do valor de um banco relacional.

---

## Passo 3 — Inserir dados (o "C" e um pouco de leitura)

```sql
INSERT INTO clientes (nome, email) VALUES
    ('Ana Silva',   'ana@exemplo.com'),
    ('Bruno Costa', 'bruno@exemplo.com'),
    ('Carla Dias',  'carla@exemplo.com');

-- 'RETURNING' devolve o que foi inserido — ótimo para pegar o id gerado
INSERT INTO pedidos (cliente_id, descricao, valor) VALUES
    (1, 'Caderno e canetas', 45.90),
    (1, 'Mochila',          129.90),
    (2, 'Livro de SQL',      89.00)
RETURNING id, descricao;
-- esperado: as duas colunas das 3 linhas inseridas
```

**O que acontece se você violar uma regra:**
```sql
INSERT INTO pedidos (cliente_id, descricao, valor) VALUES (99, 'Fantasma', 10);
-- ERROR: insert or update on table "pedidos" violates foreign key constraint
--        Key (cliente_id)=(99) is not present in table "clientes".
```
O banco **recusou**. Não existe cliente 99, então não pode existir pedido para ele. Essa recusa é
o banco trabalhando a seu favor.

---

## Passo 4 — Consultar (o "R" de Read)

```sql
-- Tudo de uma tabela
SELECT * FROM clientes;

-- Só algumas colunas, filtrando
SELECT nome, email FROM clientes WHERE nome LIKE 'A%';   -- nomes começados por A

-- Ordenar
SELECT * FROM pedidos ORDER BY valor DESC;               -- do mais caro ao mais barato

-- Limitar
SELECT * FROM pedidos ORDER BY valor DESC LIMIT 1;       -- só o pedido mais caro

-- Agregar: somar, contar, média
SELECT COUNT(*) AS total_pedidos, SUM(valor) AS faturamento FROM pedidos;

-- Agrupar: faturamento por cliente
SELECT cliente_id, COUNT(*) AS qtd, SUM(valor) AS total
FROM pedidos
GROUP BY cliente_id
ORDER BY total DESC;
```

Cada palavra-chave tem um papel, e a **ordem** importa (embora o banco a execute numa ordem
diferente da que você escreve — ver [16-consultas-e-planejador.md](16-consultas-e-planejador.md)):

```
SELECT   colunas          -- o que devolver
FROM     tabela           -- de onde
WHERE    condição         -- filtrar linhas ANTES de agrupar
GROUP BY colunas          -- agrupar
HAVING   condição         -- filtrar grupos DEPOIS de agrupar
ORDER BY colunas          -- ordenar
LIMIT    n                -- limitar a quantidade
```

---

## Passo 5 — JOIN: conectar tabelas

Aqui está o coração do modelo relacional. A tabela `pedidos` guarda `cliente_id` (um número), não
o nome do cliente. Para ver o **nome** ao lado do pedido, você **junta** as duas tabelas:

```sql
SELECT
    c.nome,
    p.descricao,
    p.valor
FROM pedidos p
JOIN clientes c ON c.id = p.cliente_id
ORDER BY c.nome;
```
Leia assim: "para cada linha de `pedidos`, encontre a linha de `clientes` cujo `id` é igual ao
`cliente_id` do pedido, e mostre o nome junto".

O `p` e o `c` são **apelidos** (*aliases*) das tabelas — economizam digitação e deixam claro de
onde vem cada coluna.

### Os tipos de JOIN, em uma imagem

```sql
-- INNER JOIN: só quem tem correspondência nas DUAS tabelas (o padrão de 'JOIN')
SELECT c.nome, p.descricao FROM clientes c JOIN pedidos p ON p.cliente_id = c.id;
-- Carla NÃO aparece: ela não tem pedidos

-- LEFT JOIN: TODOS os clientes, com ou sem pedido
SELECT c.nome, p.descricao FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id;
-- Carla aparece, com descricao NULL
```

| JOIN | Devolve |
|---|---|
| `INNER JOIN` (= `JOIN`) | Só as linhas com correspondência dos dois lados |
| `LEFT JOIN` | Todas da esquerda + as correspondentes da direita (`NULL` se não houver) |
| `RIGHT JOIN` | Todas da direita + as correspondentes da esquerda |
| `FULL JOIN` | Todas dos dois lados |
| `CROSS JOIN` | Todas as combinações (produto cartesiano — cuidado!) |

JOINs a fundo em [12-modelo-relacional-e-sql.md](12-modelo-relacional-e-sql.md).

---

## Passo 6 — Atualizar e remover (o "U" e o "D")

```sql
-- UPDATE: sempre com WHERE, ou você altera a tabela INTEIRA
UPDATE clientes SET nome = 'Ana Silva Santos' WHERE id = 1;

-- DELETE: idem — sem WHERE, apaga tudo
DELETE FROM pedidos WHERE valor < 50;
```

> ### ⚠️ O erro que apaga a empresa
> `UPDATE clientes SET nome = 'x';` — **sem `WHERE`** — muda **todos** os clientes.
> `DELETE FROM pedidos;` — **sem `WHERE`** — apaga **todos** os pedidos.
> O banco obedece. Não há "desfazer" fora de uma transação. **Sempre confira o `WHERE` antes de
> apertar Enter em `UPDATE`/`DELETE`.** Um hábito que salva carreiras: rode primeiro o mesmo
> filtro num `SELECT` (`SELECT * FROM pedidos WHERE valor < 50;`) e veja o que seria afetado.

---

## Passo 7 — Transações: tudo ou nada

Uma **transação** agrupa operações que devem acontecer juntas — ou nenhuma acontece. O exemplo
clássico é transferir dinheiro: debitar de um, creditar em outro. Se o segundo falhar, o primeiro
não pode ficar de pé.

```sql
BEGIN;                                              -- abre a transação
    UPDATE contas SET saldo = saldo - 100 WHERE id = 1;
    UPDATE contas SET saldo = saldo + 100 WHERE id = 2;
COMMIT;                                             -- confirma: as duas valem
```

Se algo der errado no meio:
```sql
BEGIN;
    DELETE FROM pedidos WHERE cliente_id = 1;
    -- opa, era o cliente errado!
ROLLBACK;                                           -- desfaz TUDO desde o BEGIN
```

Isso te dá a rede de segurança que o `UPDATE`/`DELETE` solto não tem:
```sql
BEGIN;
DELETE FROM pedidos WHERE valor < 50;
SELECT count(*) FROM pedidos;   -- confira se sobrou o que você esperava
-- gostou? COMMIT.  errou? ROLLBACK.
COMMIT;
```

Essa é a letra **A** de **ACID** — *Atomicidade*: a transação é indivisível. As outras letras
(Consistência, Isolamento, Durabilidade) estão em [15-transacoes-e-mvcc.md](15-transacoes-e-mvcc.md).

---

## O ciclo de trabalho do dia a dia

1. **Escreva o SQL num arquivo** (`consulta.sql`), não só no prompt — assim você versiona e reusa.
   ```bash
   psql -h localhost -U seu_usuario -d loja -f consulta.sql
   ```
   ou, dentro do psql: `\i consulta.sql`.
2. **Itere** com `\e` (abre a última query no editor) e `\g` (reexecuta).
3. **Meça** com `\timing on` e, quando algo ficar lento, `EXPLAIN ANALYZE` (ver
   [16-consultas-e-planejador.md](16-consultas-e-planejador.md)).
4. **Inspecione** com `\d tabela` sempre que esquecer a estrutura.

---

## Os cinco primeiros erros de uso (não de instalação)

### 1. Esquecer o `;` no fim
O `psql` espera até você fechar o comando. Se o prompt vira `loja-#` (com `-`), ele está esperando
o resto do comando. Digite `;` e Enter.

### 2. Aspas erradas
```sql
SELECT * FROM clientes WHERE nome = "Ana";   -- ❌ ERRO: "Ana" é um IDENTIFICADOR
SELECT * FROM clientes WHERE nome = 'Ana';   -- ✅ 'Ana' é um TEXTO
```
**Aspas simples** (`'`) para texto; **aspas duplas** (`"`) para nomes de tabela/coluna. Trocar as
duas é o erro nº 1 de sintaxe.

### 3. `UPDATE`/`DELETE` sem `WHERE`
Coberto no Passo 6. O mais perigoso da lista.

### 4. Confundir `NULL` com vazio
```sql
SELECT * FROM clientes WHERE telefone = NULL;    -- ❌ nunca retorna nada
SELECT * FROM clientes WHERE telefone IS NULL;   -- ✅
```
`NULL` significa "desconhecido", e nada é "igual" a desconhecido — nem outro `NULL`. Use `IS NULL`
/ `IS NOT NULL`. Ver [75-armadilhas.md](75-armadilhas.md).

### 5. Float para dinheiro
```sql
SELECT 0.1::float + 0.2::float;    -- 0.30000000000000004  😱
SELECT 0.1::numeric + 0.2::numeric; -- 0.3  ✅
```
Use `NUMERIC` para dinheiro e qualquer valor que precise ser exato.

---

## Limpeza (se quiser recomeçar)

```sql
DROP TABLE pedidos;      -- apaga a tabela e seus dados
DROP TABLE clientes;
-- ou, para zerar o banco inteiro:
\c postgres
DROP DATABASE loja;
```

---

## Para onde ir agora

| Se você quer… | Vá para |
|---|---|
| Uma referência de comandos e SQL para consultar | [05-manual-de-uso.md](05-manual-de-uso.md) |
| Mais exemplos, do trivial ao de produção | [06-exemplos.md](06-exemplos.md) |
| Uma aplicação completa com banco de verdade | [07-projeto-modelo/](07-projeto-modelo/README.md) |
| Entender o modelo relacional a fundo | [10-fundamentos.md](10-fundamentos.md) e [12](12-modelo-relacional-e-sql.md) |
| Exercícios com critério de aprovação | [70-pratica.md](70-pratica.md) |

---

## Autoteste

1. Qual é a diferença entre um comando que começa com `\` e um comando SQL? Dê um exemplo de cada.
2. Escreva o SQL que cria uma tabela `livros` com id autoincrementado, título obrigatório e um
   preço que não pode ser negativo.
3. Por que se usa `NUMERIC` e não `FLOAT` para dinheiro? Mostre o problema com um exemplo.
4. O que a cláusula `REFERENCES` faz, e o que o banco impede por causa dela?
5. Qual é a diferença entre `INNER JOIN` e `LEFT JOIN`? Quando um cliente sem pedidos aparece?
6. Por que `WHERE telefone = NULL` nunca retorna nada, e qual é a forma correta?
7. Explique o que `BEGIN` / `COMMIT` / `ROLLBACK` fazem, e como isso te protege de um `DELETE`
   errado.
8. Qual é a diferença entre aspas simples e aspas duplas em SQL?
9. Por que `UPDATE`/`DELETE` sem `WHERE` é perigoso, e qual hábito reduz o risco?
10. Escreva a query que mostra o nome de cada cliente ao lado da descrição de seus pedidos.
