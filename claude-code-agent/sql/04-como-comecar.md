# 04 — Como começar: do ambiente pronto ao primeiro resultado

Nível: iniciante · Data: 13/08/2026 · Todas as saídas deste arquivo foram **executadas**

Este arquivo supõe que o [03-instalacao.md](03-instalacao.md) já foi feito —
ou, no mínimo, que `python3 -c "import sqlite3"` funciona. Não repetimos
instalação aqui.

Meta: em **20 minutos** você terá criado um banco, carregado dados de um reator
e respondido quatro perguntas de processo com SQL.

---

## 1. Onde digitar o SQL

Três caminhos. Escolha **um** e siga até o fim; misturar confunde.

| Caminho | Comando para abrir | Bom para |
|---|---|---|
| **A. Python** (recomendado se você não usa terminal) | criar um arquivo `.py` e rodar | Quem vem de Excel/MATLAB; automatizar depois |
| **B. Cliente `sqlite3`** | `sqlite3 primeiro.db` | Explorar rápido, ver tabelas |
| **C. Navegador** | <https://sqlime.org> | Máquina bloqueada, primeiro contato |

Neste arquivo mostro o **caminho A** por extenso e dou o equivalente em B ao
lado, porque você vai encontrar os dois na internet.

---

## 2. O primeiro banco, em três passos

### Passo 1 — crie o arquivo `primeiro.py`

```python
import sqlite3

# Abre (ou cria) o arquivo primeiro.db. Se não existir, nasce agora.
con = sqlite3.connect("primeiro.db")

# executescript roda vários comandos SQL de uma vez.
con.executescript("""
CREATE TABLE leitura (
    tag_id TEXT NOT NULL,          -- qual instrumento
    ts     TEXT NOT NULL,          -- quando (texto ISO-8601, UTC)
    valor  REAL,                   -- o que ele leu
    PRIMARY KEY (tag_id, ts)       -- não pode haver duas leituras do mesmo
);                                 -- instrumento no mesmo instante

INSERT INTO leitura (tag_id, ts, valor) VALUES
  ('TI-101', '2026-07-01 10:00:00', 178.4),
  ('TI-101', '2026-07-01 10:01:00', 179.9),
  ('TI-101', '2026-07-01 10:02:00', 181.2),
  ('TI-101', '2026-07-01 10:03:00', 196.7),
  ('TI-101', '2026-07-01 10:04:00', 197.1),
  ('TI-101', '2026-07-01 10:05:00', 183.0),
  ('PI-101', '2026-07-01 10:00:00', 2.68),
  ('PI-101', '2026-07-01 10:01:00', 2.71),
  ('PI-101', '2026-07-01 10:02:00', 2.75),
  ('PI-101', '2026-07-01 10:03:00', 3.41),
  ('PI-101', '2026-07-01 10:04:00', 3.44),
  ('PI-101', '2026-07-01 10:05:00', 2.80);
""")

con.commit()      # confirma a gravação — sem isto, nada é salvo
print("Banco criado.")
```

### Passo 2 — rode

```bash
python3 primeiro.py
```

```
# esperado:
Banco criado.
```

### Passo 3 — confirme que o arquivo existe

```bash
ls -l primeiro.db
```
```
# esperado (o tamanho pode variar um pouco):
-rw-rw-r-- 1 voce voce 12288 ago 13 13:20 primeiro.db
```

**Se der errado:**

| Erro | Causa | Correção |
|---|---|---|
| `table leitura already exists` | Você rodou duas vezes | `rm primeiro.db` e rode de novo |
| `unable to open database file` | Sem permissão na pasta, ou caminho errado | `cd` para uma pasta sua; use `pwd` para ver onde está |
| `no such file or directory: primeiro.py` | Você está em outra pasta | `ls` para conferir; `cd` para a pasta certa |

**Equivalente no cliente `sqlite3`:** salve o SQL acima (sem as linhas de
Python) em `criar.sql` e rode `sqlite3 primeiro.db < criar.sql`.

---

## 3. As quatro primeiras perguntas

Crie `consultar.py`:

```python
import sqlite3

con = sqlite3.connect("primeiro.db")

def pergunta(titulo, sql):
    print(f"\n### {titulo}")
    cur = con.execute(sql)
    print(" | ".join(d[0] for d in cur.description))   # nomes das colunas
    for linha in cur:
        print(" | ".join(str(x) for x in linha))

pergunta("1. Tudo que está guardado",
         "SELECT * FROM leitura")

pergunta("2. Quando a temperatura passou de 195 °C?",
         """SELECT ts, valor
              FROM leitura
             WHERE tag_id = 'TI-101'
               AND valor > 195""")

pergunta("3. Resumo por instrumento",
         """SELECT tag_id,
                   COUNT(*)          AS n,
                   ROUND(AVG(valor), 2) AS media,
                   MAX(valor)        AS pico
              FROM leitura
             GROUP BY tag_id
             ORDER BY tag_id""")

pergunta("4. As três maiores temperaturas",
         """SELECT ts, valor
              FROM leitura
             WHERE tag_id = 'TI-101'
             ORDER BY valor DESC
             LIMIT 3""")
```

```bash
python3 consultar.py
```

**Saída real** (executada em 13/08/2026):

```
### 1. Tudo que está guardado
tag_id | ts | valor
TI-101 | 2026-07-01 10:00:00 | 178.4
TI-101 | 2026-07-01 10:01:00 | 179.9
TI-101 | 2026-07-01 10:02:00 | 181.2
TI-101 | 2026-07-01 10:03:00 | 196.7
TI-101 | 2026-07-01 10:04:00 | 197.1
TI-101 | 2026-07-01 10:05:00 | 183.0
PI-101 | 2026-07-01 10:00:00 | 2.68
PI-101 | 2026-07-01 10:01:00 | 2.71
PI-101 | 2026-07-01 10:02:00 | 2.75
PI-101 | 2026-07-01 10:03:00 | 3.41
PI-101 | 2026-07-01 10:04:00 | 3.44
PI-101 | 2026-07-01 10:05:00 | 2.8

### 2. Quando a temperatura passou de 195 °C?
ts | valor
2026-07-01 10:03:00 | 196.7
2026-07-01 10:04:00 | 197.1

### 3. Resumo por instrumento
tag_id | n | media | pico
PI-101 | 6 | 2.97 | 3.44
TI-101 | 6 | 186.05 | 197.1

### 4. As três maiores temperaturas
ts | valor
2026-07-01 10:04:00 | 197.1
2026-07-01 10:03:00 | 196.7
2026-07-01 10:05:00 | 183.0
```

**Pare aqui e leia o que aconteceu.** Você acabou de fazer, com quatro
consultas, o que uma planilha faria com filtro, tabela dinâmica e classificação
— e você pode rodar isso amanhã de novo, sobre 10 milhões de linhas, sem tocar
em nada.

Repare no `2.8` da última linha da pergunta 1: você inseriu `2.80` e ele
devolveu `2.8`. Não é erro. `2.80` e `2.8` são o mesmo número; o `0` era
formatação, e formatação não é dado. Guarde isso — está em
[17-tipos-e-nulos.md](17-tipos-e-nulos.md).

---

## 4. Anatomia de uma consulta

```sql
SELECT   tag_id, ROUND(AVG(valor), 2) AS media   -- 5. o que mostrar
  FROM   leitura                                 -- 1. de onde
 WHERE   valor IS NOT NULL                       -- 2. quais linhas
 GROUP   BY tag_id                               -- 3. como agrupar
HAVING   AVG(valor) > 1                          -- 4. quais grupos
 ORDER   BY media DESC                           -- 6. em que ordem
 LIMIT   10;                                     -- 7. quantas
```

Os números **não** são a ordem em que se escreve — são a ordem em que o banco
**executa**. Essa diferença explica quase todo erro de iniciante:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

Duas consequências que você vai encontrar hoje:

1. **O apelido (`AS media`) não funciona no `WHERE`**, porque o `WHERE` roda
   *antes* do `SELECT`, quando o apelido ainda não existe. Funciona no
   `ORDER BY`, que roda depois.
2. **`WHERE` filtra linhas; `HAVING` filtra grupos.** `WHERE` não pode usar
   `AVG()`, porque quando ele roda ainda não houve agrupamento.

Detalhe completo em [12-consulta-select.md](12-consulta-select.md).

---

## 5. O ciclo de trabalho do dia a dia

```
   ┌──────────────┐
   │ 1. Pergunta  │  "quanto tempo passou de 195 °C?"
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ 2. Explore   │  SELECT * FROM leitura LIMIT 20;   ← veja o dado ANTES
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ 3. Escreva   │  comece pelo FROM e WHERE, some uma coisa por vez
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ 4. Rode      │  com LIMIT 10 enquanto está desenvolvendo
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ 5. Confira   │  o número faz sentido físico? a contagem bate?
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ 6. Guarde    │  salve o .sql com um comentário dizendo o que responde
   └──────────────┘
```

**Os três hábitos que separam quem sofre de quem não sofre:**

1. **`LIMIT 10` enquanto desenvolve.** Consulta errada sobre 10 milhões de
   linhas demora e ainda dá errado. Sobre 10 linhas, dá errado rápido.
2. **`COUNT(*)` antes e depois de cada `JOIN`.** Se o número de linhas mudou de
   um jeito que você não previu, a junção está errada — e você acabou de
   descobrir isso em 3 segundos em vez de na reunião.
3. **Comentário no topo de cada `.sql`** dizendo a pergunta que ele responde e
   a data. Consulta sem contexto é indecifrável em duas semanas — inclusive
   por quem a escreveu.

---

## 6. Os cinco primeiros erros de USO (não de instalação)

Todos reproduzidos de verdade, com a mensagem literal que o SQLite devolve.

### Erro 1 — `no such table: leituras`

```sql
SELECT * FROM leituras;
```
```
OperationalError: no such table: leituras
```

Tabela no **singular**, `leitura`. Além do erro de digitação, pode ser que você
esteja conectado ao banco errado.

**Como investigar:**
```sql
SELECT name FROM sqlite_master WHERE type='table';
```
No cliente `sqlite3`, `.tables` faz o mesmo. Em PostgreSQL, `\dt`.

### Erro 2 — `no such column: TI` (aspas erradas)

```sql
SELECT * FROM leitura WHERE tag_id = TI-101;
```
```
OperationalError: no such column: TI
```

Sem aspas, o SQL entende `TI-101` como *a coluna `TI` menos o número 101*.
**Texto vai entre aspas simples:**

```sql
SELECT * FROM leitura WHERE tag_id = 'TI-101';
```

Regra que vale em todo dialeto padrão:
- `'texto'` — aspas **simples** para valor de texto;
- `"nome de coluna"` — aspas **duplas** para identificador (só quando o nome
  tem espaço ou é palavra reservada);
- aspas duplas em volta de um valor é a fonte nº 1 de `no such column`.

⚠️ O MySQL aceita `"texto"` por padrão, o que ensina o hábito errado a uma
geração inteira de gente. Ver [23-dialetos.md](23-dialetos.md).

### Erro 3 — `misuse of aggregate: AVG()`

```sql
SELECT tag_id, AVG(valor) AS media
  FROM leitura
 WHERE media > 100
 GROUP BY tag_id;
```
```
OperationalError: misuse of aggregate: AVG()
```

Duas coisas erradas ao mesmo tempo, e as duas são a ordem de execução:
o `WHERE` roda antes do `GROUP BY` (não existe média ainda) e antes do `SELECT`
(não existe o apelido `media` ainda).

**Certo:**
```sql
SELECT tag_id, AVG(valor) AS media
  FROM leitura
 GROUP BY tag_id
HAVING AVG(valor) > 100;
```

### Erro 4 — `WHERE valor = NULL` devolve zero linhas, sem erro

```sql
SELECT * FROM leitura WHERE valor = NULL;
```
```
(0 linhas)   -- e nenhum erro
```

Este é o **pior** dos cinco, porque não avisa. `NULL` significa "desconhecido".
Perguntar se um desconhecido é igual a outro desconhecido dá... desconhecido —
que não é verdadeiro, e a linha não entra. Nem `<> NULL` funciona.

**Certo:**
```sql
SELECT * FROM leitura WHERE valor IS NULL;
SELECT * FROM leitura WHERE valor IS NOT NULL;
```

Arquivo inteiro sobre isso: [17-tipos-e-nulos.md](17-tipos-e-nulos.md).

### Erro 5 — comparação de data que "funciona" e engana

```sql
SELECT ts FROM leitura WHERE ts > '2026-07-01';
```
```
(12 linhas)  -- todas! inclusive as do próprio dia 01
```

Como `ts` é texto, a comparação é **lexicográfica**: a cadeia
`'2026-07-01 10:00:00'` é maior que `'2026-07-01'` porque é mais longa e o
prefixo é igual. O resultado *parece* certo e não é.

**Certo — sempre com intervalo semiaberto e horário explícito:**
```sql
SELECT ts FROM leitura
 WHERE ts >= '2026-07-01 00:00:00'
   AND ts <  '2026-07-02 00:00:00';
```

**Por que `<` e não `<=`:** com `<= '2026-07-01 23:59:59'` você perde tudo o
que acontecer entre 23:59:59,001 e a virada. Em dado de sensor a milissegundo,
isso é um buraco silencioso todo dia. O padrão profissional é sempre
`[início, fim)`. Ver [18-series-temporais.md](18-series-temporais.md).

**Menções honrosas** (os erros 6 a 10, que você também vai cometer):

| Sintoma | Causa |
|---|---|
| `JOIN` devolveu mais linhas que a tabela original | Cardinalidade: um lado tem duplicatas. [13](13-juncoes.md) |
| Divisão deu `0` | Divisão de inteiro por inteiro. Use `100.0 * a / b` |
| Vírgula sobrando antes do `FROM` | `SELECT a, b, FROM t` — o SQL não perdoa |
| Nada foi salvo | Faltou `commit()` (Python) ou `COMMIT;` (transação explícita) |
| Acentuação saiu errada | Codificação do terminal ou do arquivo; use UTF-8 |

---

## 7. Sinta a diferença de escala

Vale a pena fazer isto agora, para o resto do curso ter peso. Rode o
[projeto-modelo](07-projeto-modelo/):

```bash
cd 07-projeto-modelo
python3 scripts/gerar_dados.py
```
```
# esperado, em ~5 segundos:
Banco criado em .../planta.db
  equipamento             5 linhas
  tag                     8 linhas
  leitura            344640 linhas
  ...
  tamanho              28.6 MB
```

```bash
python3 scripts/consultar.py 01
```
```
  bateladas | concluidas | abortadas | carga_t | produzido_t | rendimento_global_pct | ...
         78 |         77 |         1 |   389.3 |       352.7 |                  90.6 | ...
  [1 linha(s) em 1.1 ms]
```

**344 mil leituras, resumo do mês em 1,1 milissegundo.** O Excel abriria o
arquivo em alguns minutos, se abrisse. É por isso que vale aprender.

---

## 8. Para onde ir agora

```
       você está aqui
            │
            ▼
    ┌───────────────┐
    │ 04-como-come… │
    └───────┬───────┘
            │
   ┌────────┴─────────────────────────┐
   ▼                                  ▼
"quero resolver um problema"    "quero entender de verdade"
   │                                  │
   ▼                                  ▼
06-exemplos.md                  10-fundamentos.md
07-projeto-modelo/              12-consulta-select.md
   │                                  │
   ▼                                  ▼
30-engenharia-quimica.md        13-juncoes.md → 14 → 15 → 16
   │                                  │
   └──────────────┬───────────────────┘
                  ▼
            70-pratica.md
```

- **Com pressa, precisa de um relatório amanhã:**
  [06-exemplos.md](06-exemplos.md) → ache o exemplo parecido → adapte.
- **Engenheiro químico querendo ver a aplicação primeiro:**
  [30-engenharia-quimica.md](30-engenharia-quimica.md).
- **Quer a base sólida, na ordem certa:**
  [10-fundamentos.md](10-fundamentos.md) e siga a numeração.
- **Quer referência de sintaxe para consultar:**
  [05-manual-de-uso.md](05-manual-de-uso.md).

---

## Autoteste

1. Qual é a ordem em que o banco **executa** as cláusulas, e por que ela
   difere da ordem em que se escreve?
2. Por que `WHERE media > 100` falha quando `media` é um apelido de `AVG()`?
3. `SELECT * FROM leitura WHERE valor = NULL` devolve zero linhas. Por quê, e
   qual é a forma correta?
4. Você escreveu `WHERE tag_id = TI-101` e recebeu `no such column: TI`.
   Explique o que o interpretador entendeu.
5. Por que `ts > '2026-07-01'` traz linhas do próprio dia 1º?
6. Por que se usa intervalo semiaberto `[início, fim)` em vez de `BETWEEN`
   com `23:59:59`?
7. Cite os três hábitos do ciclo de trabalho e o que cada um previne.
8. Você inseriu `2.80` e o banco devolveu `2.8`. Isso é um erro?

---

*Próximo: [05-manual-de-uso.md](05-manual-de-uso.md) (referência) ou
[06-exemplos.md](06-exemplos.md) (receitas).*
