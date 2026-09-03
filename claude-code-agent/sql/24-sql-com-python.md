# 24 — SQL com Python

Nível: intermediário · Data: 13/08/2026 · Exemplos **executados**

O fluxo de trabalho real de um engenheiro que usa dado: **SQL traz e agrega;
Python calcula, modela e desenha.** Este arquivo é sobre a junta entre os dois.

---

## 1. `sqlite3` da biblioteca padrão

Já vem no Python. Nada a instalar.

```python
import sqlite3

con = sqlite3.connect("planta.db")

for tag, media in con.execute(
        "SELECT tag_id, AVG(valor) FROM leitura GROUP BY tag_id"):
    print(tag, round(media, 2))

con.close()
```

### Parâmetros: a regra que não se negocia

```python
# ❌ NUNCA
tag = input("tag: ")
con.execute("SELECT * FROM leitura WHERE tag_id = '" + tag + "'")

# ✅ SEMPRE
con.execute("SELECT * FROM leitura WHERE tag_id = ?", (tag,))
```

**Demonstração, executada de verdade:**

```python
tag = "TI-101' OR '1'='1"

# concatenado
sql = "SELECT COUNT(*) FROM leitura WHERE tag_id = '" + tag + "'"
# vira: SELECT COUNT(*) FROM leitura WHERE tag_id = 'TI-101' OR '1'='1'
con.execute(sql).fetchone()          # (344640,)   ← a tabela INTEIRA

# parametrizado
con.execute("SELECT COUNT(*) FROM leitura WHERE tag_id = ?", (tag,)).fetchone()
# (0,)   ← procurou literalmente por esse texto, e não achou
```

**344.640 contra 0.** No caso de um `SELECT`, o dano é vazamento. Num
`DELETE`, é a tabela.

Isso é **injeção de SQL**, a vulnerabilidade nº 1 de aplicações há duas
décadas. E não é só segurança: um valor com apóstrofo (`O'Brien`, `Válvula
d'água`) quebra a consulta concatenada sozinho, sem malícia nenhuma.

⚠️ Detalhe que pega: `("TI-101")` **não** é uma tupla — é uma string entre
parênteses. Precisa da vírgula: `("TI-101",)`.

**Parâmetro nomeado**, mais legível em consulta longa:

```python
con.execute("SELECT * FROM leitura WHERE tag_id = :tag AND ts >= :de",
            {"tag": "TI-101", "de": "2026-07-01 00:00:00"})
```

⚠️ **Parâmetro só substitui valor, nunca nome de tabela ou coluna.** Se
precisar de nome dinâmico, valide contra uma lista branca:

```python
COLUNAS_OK = {"ts", "valor", "qualidade"}
if coluna not in COLUNAS_OK:
    raise ValueError(coluna)
con.execute(f"SELECT {coluna} FROM leitura LIMIT 5")   # agora é seguro
```

---

## 2. Receber o resultado

```python
cur = con.execute("SELECT ...")

cur.fetchone()          # uma linha, ou None
cur.fetchall()          # todas — cuidado com memória
cur.fetchmany(10000)    # em lotes
for linha in cur: ...   # em fluxo, o mais econômico
```

### Acesso por nome de coluna

```python
con.row_factory = sqlite3.Row
r = con.execute("SELECT tag_id, ts, valor FROM leitura LIMIT 1").fetchone()
print(r["valor"])   # 7.293
print(dict(r))      # {'tag_id': 'AI-101', 'ts': '2026-07-01 00:00:00', 'valor': 7.293}
```

Muito melhor que `r[2]` — que quebra silenciosamente quando alguém muda a
ordem do `SELECT`.

### Volume grande

```python
cur = con.execute("SELECT valor FROM leitura WHERE tag_id='TI-101'")
n = 0
while True:
    lote = cur.fetchmany(10000)
    if not lote:
        break
    n += len(lote)
# 43080 linhas em 15 ms
```

`fetchall()` de 100 milhões de linhas estoura a memória. `fetchmany` ou
iteração direta, sempre, quando o volume é grande ou desconhecido.

---

## 3. Escrever

```python
# transação com rollback automático em caso de exceção
with con:
    con.executemany(
        "INSERT INTO leitura (tag_id, ts, valor) VALUES (?, ?, ?)", linhas)
```

`with con:` **não fecha a conexão** — ele confirma no fim, ou desfaz se houver
exceção. Fechar é `con.close()`. É uma das confusões mais comuns da API.

**Desempenho** (medido, 20.000 linhas):

| Forma | Tempo |
|---|---|
| `execute` + `commit()` por linha | **131,50 s** |
| `executemany` + um `commit` | **0,03 s** |

**4.311× de diferença.** Ver [20-dml-e-transacoes.md](20-dml-e-transacoes.md).

### Configuração recomendada para carga

```python
con = sqlite3.connect("planta.db")
con.execute("PRAGMA journal_mode = WAL")
con.execute("PRAGMA synchronous = NORMAL")
con.execute("PRAGMA foreign_keys = ON")     # por conexão, sempre
```

---

## 4. Com pandas

```bash
pip install pandas
```

```python
import pandas as pd, sqlite3

con = sqlite3.connect("planta.db")

df = pd.read_sql_query("""
    SELECT ts, valor
      FROM leitura
     WHERE tag_id = ? AND ts >= ? AND ts < ?
     ORDER BY ts
""", con, params=("TI-101", "2026-07-01 00:00:00", "2026-07-02 00:00:00"),
    parse_dates=["ts"], index_col="ts")

print(df.describe())
df.resample("1h").agg(["mean", "min", "max"])
df.plot()
```

### A pergunta certa: agregar no SQL ou no pandas?

| Faça no **SQL** | Faça no **pandas** |
|---|---|
| Filtrar (`WHERE`) | Modelo estatístico, ajuste de curva |
| Agregar (`GROUP BY`) | Gráfico |
| Juntar tabelas | Reamostragem complexa, interpolação |
| Ordenar e limitar | Álgebra matricial, FFT |
| Reduzir volume **antes** de trazer | Transformação que precisa de biblioteca |

**A regra:** traga o **mínimo** de dado para o Python. Trazer 100 milhões de
linhas para o pandas fazer `groupby` é o antipadrão nº 1 — o banco faz isso
melhor, com índice, sem carregar tudo na memória.

**A exceção honesta:** para dado que já cabe na memória (< ~1 GB) e para
manipulação exploratória, o pandas é mais rápido de *escrever*. O tempo do
analista também conta.

### Escrever de volta

```python
df.to_sql("resumo_horario", con, if_exists="replace", index=True)
```
⚠️ `if_exists="replace"` **apaga a tabela e recria**, perdendo índices,
restrições e tipos. Para produção, crie a tabela com DDL próprio e use
`if_exists="append"`.

---

## 5. Com DuckDB — a combinação mais produtiva

```bash
pip install duckdb
```

```python
import duckdb

# SQL direto sobre CSV, sem criar tabela nem importar
duckdb.sql("""
    SELECT tag_id,
           count(*)                            AS n,
           round(avg(valor), 3)                AS media,
           round(stddev_samp(valor), 3)        AS desvio,
           round(quantile_cont(valor, 0.5), 3) AS mediana
      FROM 'export_do_historiador.csv'
     WHERE qualidade = 'BOA'
     GROUP BY 1
""").show()
```

**SQL sobre um DataFrame do pandas, sem conversão:**

```python
import duckdb, pandas as pd
df = pd.read_csv("leituras.csv")

duckdb.sql("SELECT tag_id, avg(valor) FROM df GROUP BY 1").df()
```

O DuckDB **enxerga as variáveis do Python** — `df` é referenciado direto no
SQL, sem cópia. Isso é o melhor dos dois mundos: a expressividade do SQL sobre
os objetos do Python.

**Ler o banco SQLite com DuckDB:**

```python
duckdb.sql("INSTALL sqlite; LOAD sqlite;")
duckdb.sql("SELECT count(*) FROM sqlite_scan('planta.db', 'leitura')")
```

**Converter CSV para Parquet** (medido: 13,3 MB → **3,3 MB**, em 144 ms):

```python
duckdb.sql("COPY (SELECT * FROM 'leitura.csv') TO 'leitura.parquet' (FORMAT parquet)")
```

Se você exporta CSV do historiador toda semana, **converta para Parquet**: 4×
menor, tipos preservados, e as consultas ficam ~7× mais rápidas.

---

## 6. SQLAlchemy: quando faz sentido

```bash
pip install sqlalchemy
```

```python
from sqlalchemy import create_engine, text
import pandas as pd

eng = create_engine("sqlite:///planta.db")
# postgresql+psycopg://usuario:senha@servidor:5432/banco
# oracle+oracledb://usuario:senha@servidor:1521/?service_name=orcl
# mssql+pyodbc://usuario:senha@servidor/banco?driver=ODBC+Driver+18+for+SQL+Server

with eng.connect() as con:
    df = pd.read_sql(text("SELECT * FROM v_batelada WHERE status = :s"),
                     con, params={"s": "CONCLUIDA"})
```

**O que ele resolve:** a mesma API para todos os bancos, e o gerenciamento de
*pool* de conexões.

**O que ele traz junto:** o ORM (mapeamento objeto-relacional), que gera SQL a
partir de classes Python. **Opinião profissional:** para aplicação, o ORM tem
lugar; para **análise de dados, não**. Você conhece a consulta que quer, e
descrevê-la em objetos Python é uma tradução a mais entre você e o resultado.
Use o `text()` e escreva SQL.

---

## 7. Conectar aos bancos da empresa

| Banco | Pacote | Notas |
|---|---|---|
| PostgreSQL | `psycopg[binary]` | Versão 3; a 2 era `psycopg2` |
| SQL Server | `pyodbc` | Precisa do *Microsoft ODBC Driver 18* instalado no sistema |
| Oracle | `oracledb` | **Modo *thin* não exige Oracle Client** — foi a maior melhoria da década para quem sofria com o Instant Client |
| MySQL | `mysqlclient` ou `PyMySQL` | |
| SAP HANA | `hdbcli` | |
| ODBC genérico | `pyodbc` | Serve para PI SQL Client também |

**Segredos: nunca no código.**

```python
import os
senha = os.environ["DB_SENHA"]        # variável de ambiente
```
Ou um arquivo `.env` **fora do git** (com `python-dotenv`), ou o cofre da
empresa. Senha em `.py` versionado é o achado mais comum de qualquer auditoria
de segurança, e o mais fácil de evitar.

---

## 8. Um script de relatório completo

Junta tudo: consulta parametrizada, transação, verificação e saída.

```python
#!/usr/bin/env python3
"""Relatório mensal de rendimento. Uso: python3 relatorio.py 2026-07"""
import sqlite3, sys, csv
from datetime import date

SQL = """
SELECT b.operador,
       COUNT(*)                        AS bateladas,
       ROUND(AVG(b.rendimento_pct), 2) AS rendimento_medio,
       ROUND(MIN(b.rendimento_pct), 2) AS pior,
       ROUND(SUM(b.produzido_kg)/1000.0, 1) AS toneladas
  FROM v_batelada b
 WHERE b.status = 'CONCLUIDA'
   AND b.ts_inicio >= :de AND b.ts_inicio < :ate
 GROUP BY b.operador
 ORDER BY rendimento_medio DESC
"""

def main(mes):                                    # mes = '2026-07'
    ano, m = map(int, mes.split("-"))
    de  = f"{ano:04d}-{m:02d}-01 00:00:00"
    ate = (f"{ano+1:04d}-01-01 00:00:00" if m == 12
           else f"{ano:04d}-{m+1:02d}-01 00:00:00")

    con = sqlite3.connect("file:planta.db?mode=ro", uri=True)   # somente leitura
    con.row_factory = sqlite3.Row
    linhas = con.execute(SQL, {"de": de, "ate": ate}).fetchall()

    if not linhas:
        print(f"Nenhuma batelada concluída em {mes}.", file=sys.stderr)
        return 1

    total = sum(l["bateladas"] for l in linhas)
    print(f"Relatório de {mes} — {total} bateladas — gerado em {date.today()}")
    for l in linhas:
        print(f"  {l['operador']:<14} {l['bateladas']:>3} bat. "
              f"{l['rendimento_medio']:>6.2f}%  pior {l['pior']:>6.2f}%  "
              f"{l['toneladas']:>6.1f} t")

    with open(f"rendimento-{mes}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(linhas[0].keys())
        w.writerows(tuple(l) for l in linhas)
    con.close()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "2026-07"))
```

Repare em quatro decisões:

1. **`mode=ro`** — abre somente leitura. Um relatório não tem por que poder
   escrever, e essa linha elimina a chance de um acidente.
2. **Fronteiras calculadas em Python**, passadas como parâmetro. O SQL fica
   portátil e *sargable*.
3. **Trata o caso vazio** e devolve código de saída ≠ 0 — para o agendador
   saber que falhou.
4. **A data de geração sai no relatório.** Relatório sem data é relatório sem
   contexto.

---

## Autoteste

1. Por que `"... WHERE tag = '" + valor + "'"` é errado? Cite as duas razões.
2. Qual foi o resultado real da consulta com `"TI-101' OR '1'='1"` concatenada?
3. Por que `("TI-101")` não funciona como parâmetro?
4. Como passar um nome de **coluna** dinâmico com segurança?
5. `with con:` fecha a conexão?
6. Quando agregar no SQL e quando no pandas? Qual a regra e qual a exceção?
7. Por que `df.to_sql(..., if_exists="replace")` é perigoso?
8. Como o DuckDB consulta um DataFrame do pandas, e por que isso é útil?
9. Por que abrir o banco com `mode=ro` num script de relatório?
10. Onde guardar a senha do banco, e onde nunca guardar?

---

*Próximo: [30-engenharia-quimica.md](30-engenharia-quimica.md) — o arquivo
específico da sua profissão.*
