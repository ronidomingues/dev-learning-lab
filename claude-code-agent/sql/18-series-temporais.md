# 18 — Séries temporais: dado de sensor em SQL

Nível: intermediário → avançado · Data: 13/08/2026

Este é o arquivo mais específico para engenharia de processo do bloco técnico.
Dado de planta é série temporal, e série temporal tem problemas que a
literatura de SQL comercial não trata.

---

## 1. O que torna série temporal diferente

| Característica | Consequência |
|---|---|
| Só cresce; quase nunca se atualiza | O `UPDATE` é raro; o `INSERT` é constante |
| O acesso é quase sempre "um tag, um intervalo" | A chave `(tag_id, ts)` nessa ordem manda em tudo |
| Volume enorme | 200 tags × 1/min × 1 ano = **105 milhões de linhas** |
| Valores próximos entre si | Comprime muito bem (delta encoding) |
| Perde-se valor com a idade | Dado de ontem: minuto a minuto. De 2019: média horária basta |
| Amostragem irregular na prática | Buracos, jitter, registro por exceção |
| Sem contexto próprio | "180 °C" não diz nada sem saber a batelada e a fase |

**Consequência de projeto:** a modelagem de série temporal é a mais simples que
existe (três colunas) e a que mais depende de acertar a chave, o índice e a
política de retenção.

---

## 2. Modelagem

### O modelo canônico (formato "longo"/estreito)

```sql
CREATE TABLE leitura (
    tag_id    TEXT NOT NULL REFERENCES tag(tag_id),
    ts        TEXT NOT NULL,
    valor     REAL,
    qualidade TEXT NOT NULL DEFAULT 'BOA',
    PRIMARY KEY (tag_id, ts)
) STRICT, WITHOUT ROWID;
```

**Por que longo e não largo** (uma coluna por tag):

| | Longo | Largo |
|---|---|---|
| Novo instrumento | `INSERT` na tabela `tag` | `ALTER TABLE` — e a planta tem 3.000 tags |
| Tags com períodos diferentes | Natural | Linhas cheias de `NULL` |
| Espaço | Repete o `tag_id` em cada linha | Compacto se todos amostram junto |
| Consulta de um tag | Trivial e indexada | Trivial |
| Consulta de todos num instante | Precisa do índice em `ts` | Trivial |
| Pivotar para relatório | Precisa de `CASE` | Já está pivotado |

**Recomendação:** longo, sempre, para armazenamento. Pivote na consulta ou na
camada de relatório. É o que todo historiador comercial faz por dentro.

### Timestamp: `TEXT`, `INTEGER` ou tipo nativo?

| Forma | Prós | Contras |
|---|---|---|
| `TEXT` ISO-8601 UTC | Legível; ordem alfabética = cronológica; funções de data funcionam | 19 bytes por linha |
| `INTEGER` epoch (s ou ms) | 8 bytes; aritmética trivial e rápida | Ilegível a olho nu; precisa converter para exibir |
| `TIMESTAMPTZ` (PostgreSQL) | Correto, com fuso; índices e operadores nativos | Só onde existe |

Para 105 milhões de linhas, a diferença TEXT × INTEGER são ~1,1 GB. Não é
desprezível. **Recomendação:** `TIMESTAMPTZ` onde existir; `INTEGER` epoch em
SQLite quando o volume passa de dezenas de milhões; `TEXT` abaixo disso, pela
legibilidade — que vale muito na depuração.

### UTC, sempre

Horário de verão cria uma hora que **acontece duas vezes** e outra que **não
existe**. Se o `ts` é local:

- na virada de saída, duas leituras diferentes têm o mesmo timestamp — e a
  chave primária `(tag_id, ts)` **rejeita a segunda**, perdendo uma hora de
  dado;
- na virada de entrada, há um buraco de uma hora que nenhuma análise de
  cobertura consegue distinguir de uma falha de aquisição.

O Brasil suspendeu o horário de verão em 2019, mas dados anteriores a isso
existem, plantas multinacionais operam em fusos com DST, e a discussão de
retomada volta periodicamente. **Guarde UTC e converta na exibição.** Sem
exceção.

---

## 3. Reamostragem (*downsampling*)

Ninguém plota 344 mil pontos. Reduza para o bucket.

```sql
-- SQLite: truncar por texto
SELECT substr(ts, 1, 13) || ':00:00' AS hora, AVG(valor) FROM leitura GROUP BY 1;

-- bucket de 15 minutos, SQLite
SELECT substr(ts, 1, 14)
       || printf('%02d', (CAST(substr(ts,15,2) AS INTEGER) / 15) * 15)
       || ':00' AS bucket
  FROM leitura GROUP BY 1;

-- PostgreSQL
SELECT date_trunc('hour', ts), AVG(valor) FROM leitura GROUP BY 1;
SELECT date_bin('15 minutes', ts, TIMESTAMP '2000-01-01'), AVG(valor) FROM leitura GROUP BY 1;

-- TimescaleDB / DuckDB
SELECT time_bucket(INTERVAL '15 minutes', ts), AVG(valor) FROM leitura GROUP BY 1;
```

### **Sempre guarde min, máx e n junto com a média**

```sql
SELECT hora, n, media, minimo, maximo FROM v_hora_tag;
```

Do exemplo 1 de [06-exemplos.md](06-exemplos.md), verificado:

```
hora             | n  | media | minimo | maximo
2026-07-01 05:00 | 60 | 83.40 |   49.8 | 180.41
```

Média de 83,4 °C num intervalo que vai de 49,8 a 180,4. **A média sozinha
descreve um reator que não existiu.** O pico é o que estoura o alarme e queima
o produto; a média o esconde. É por isso que todo historiador comercial guarda
os três — e por que a sua tabela resumo deve guardar também.

⚠️ **Reamostrar por média não preserva o pico, e nada recupera o que foi
perdido.** Depois de reduzir para média horária, o pico de 199 °C que durou 47
minutos vira 189 °C. Guardar min/máx é o que salva.

---

## 4. Buracos e cobertura

### Achar as lacunas com `LEAD`

```sql
WITH i AS (
    SELECT tag_id, ts,
           LEAD(ts) OVER (PARTITION BY tag_id ORDER BY ts) AS prox
      FROM leitura
)
SELECT tag_id, ts AS antes, prox AS depois,
       ROUND((julianday(prox) - julianday(ts)) * 86400) AS lacuna_s
  FROM i
 WHERE (julianday(prox) - julianday(ts)) * 86400 > 90     -- >1,5× o período
 ORDER BY lacuna_s DESC;
```

Rodando no projeto-modelo: encontra **1 buraco de 2,02 h em cada um dos 8
tags**, exatamente onde foi plantado.

### Achar os instantes exatos que faltam

Precisa gerar a série esperada:

```sql
WITH RECURSIVE esperado(ts) AS (
    SELECT '2026-07-14 02:00:00'
    UNION ALL SELECT datetime(ts,'+1 minute') FROM esperado
     WHERE ts < '2026-07-14 06:00:00'
)
SELECT COUNT(*) FROM esperado e
 WHERE NOT EXISTS (SELECT 1 FROM leitura l
                    WHERE l.tag_id='TI-101' AND l.ts = e.ts);
-- 120
```

**Qual usar:** `LEAD` para varrer o histórico inteiro rápido (não precisa saber
o período de antemão); recursiva quando você precisa da lista dos instantes,
ou quando quer garantir uma grade completa para juntar com outra série.

### Cobertura é o primeiro número a olhar

```sql
SELECT tag_id,
       COUNT(*)                                          AS amostras,
       ROUND(100.0 * COUNT(*) / (30*24*60), 2)           AS cobertura_pct,
       COUNT(*) FILTER (WHERE qualidade <> 'BOA')        AS suspeitas
  FROM leitura GROUP BY tag_id;
```

**Um relatório sobre um período com 8% de dado faltando não está errado por
8%.** Pode estar errado por 100%, se o que faltou foi o pico. Ninguém olha
cobertura, e deveria ser a primeira consulta de toda análise.

---

## 5. Preenchimento de lacunas

Quando você precisa de uma grade regular (para FFT, para correlacionar duas
séries, para alimentar um modelo).

| Método | Como | Quando usar |
|---|---|---|
| **Nada** | Deixe `NULL` | O padrão. Se você não sabe, não invente |
| **LOCF** (*last observation carried forward*) | Repete o último valor | Sinal de estado: setpoint, status de bomba, modo de operação |
| **Interpolação linear** | Média ponderada dos vizinhos | Sinal contínuo e lento: temperatura, nível |
| **Zero** | `COALESCE(v, 0)` | **Quase sempre errado**. Só se zero for o valor físico |
| **Média do período** | Preenche com a média | Estatisticamente ruim: reduz a variância artificialmente |

```sql
-- LOCF portátil, via gaps and islands
WITH g AS (
  SELECT ts, valor,
         MAX(CASE WHEN valor IS NOT NULL THEN ts END)
             OVER (ORDER BY ts ROWS UNBOUNDED PRECEDING) AS ts_ultimo_valido
    FROM grade_completa)
SELECT g.ts, COALESCE(g.valor, l.valor) AS preenchido
  FROM g LEFT JOIN leitura l ON l.ts = g.ts_ultimo_valido;
```

**Regra de ouro que vale mais que o código:** se você preencheu, **marque a
linha como preenchida**. Uma coluna `origem TEXT` com `'medido'` / `'LOCF'` /
`'interpolado'` custa nada e resolve a pergunta "de onde veio esse número?" —
que é a pergunta que o auditor faz e que ninguém consegue responder seis meses
depois.

---

## 6. Registro por exceção (*exception reporting*)

Historiadores comerciais (PI System, IP.21, PHD) **não guardam todo ponto**.
Guardam só quando o valor muda mais que uma banda morta, e usam compressão
por desvio (o *swinging door* do PI). Um tag "amostrado a 1 s" pode ter 200
pontos gravados por dia.

**O que isso significa para o seu SQL:**

1. **O intervalo entre pontos é irregular por projeto.** Contar amostras não
   mede tempo. Use `LEAD(ts) - ts`, sempre.
2. **Média aritmética simples é errada.** O certo é a média ponderada pelo
   tempo:
   ```sql
   SELECT SUM(valor * dt) / SUM(dt) AS media_ponderada_no_tempo
     FROM (SELECT valor,
                  (julianday(LEAD(ts) OVER (ORDER BY ts)) - julianday(ts)) * 1440 AS dt
             FROM leitura WHERE tag_id = 'TI-101');
   ```
   Com amostragem regular os dois coincidem. Com registro por exceção, **não**:
   um valor que ficou parado 3 horas pesaria igual a um que durou 1 minuto.
3. **O valor entre dois pontos gravados é uma interpolação**, e o historiador
   escolhe qual (degrau ou linear) por tag. Saiba qual está configurado antes
   de integrar vazão.

Este é o ponto em que engenheiro de processo tem vantagem sobre analista de
dados: você sabe que existe banda morta. Ele não.

---

## 7. Contexto: dar sentido ao número

Uma leitura sozinha não vale nada. `180 °C` só significa algo com batelada,
fase, produto e turno.

```sql
-- junção temporal: leitura → batelada
JOIN batelada b ON l.ts >= b.ts_inicio AND l.ts < COALESCE(b.ts_fim, '9999-12-31')

-- fase, derivada do tempo decorrido (receita fixa)
CASE WHEN (julianday(l.ts) - julianday(b.ts_inicio))*1440 < 45 THEN 'carga'
     WHEN ... < 120 THEN 'aquecimento'
     ... END

-- turno
CASE WHEN CAST(strftime('%H', ts) AS INTEGER) BETWEEN  6 AND 13 THEN 'A'
     WHEN CAST(strftime('%H', ts) AS INTEGER) BETWEEN 14 AND 21 THEN 'B'
     ELSE 'C' END
```

⚠️ **Turno cruza a meia-noite**, e essa é a fonte clássica de erro: o turno C
começa às 22:00 e termina às 6:00 do **dia seguinte**. Agrupar por
`substr(ts,1,10)` (o dia calendário) parte o turno C em dois. A correção é
definir "dia de produção" deslocado:

```sql
-- dia de produção começa às 06:00
substr(datetime(ts, '-6 hours'), 1, 10) AS dia_producao
```

Isto é o tipo de detalhe que faz o relatório de produção não bater com o
apontamento do operador, e leva semanas para alguém descobrir.

---

## 8. Retenção e agregação em camadas

105 milhões de linhas por ano. Guardar tudo, para sempre, ao mesmo detalhe,
é caro e desnecessário.

```
┌─────────────────────────────────────────────────────────┐
│ leitura_bruta      1 min      últimos  90 dias   ~26 M  │
│ leitura_hora       1 h        últimos  5 anos    ~8,8 M │  min/máx/média/n
│ leitura_dia        1 dia      para sempre        ~0,6 M │  min/máx/média/n
└─────────────────────────────────────────────────────────┘
```

```sql
-- consolidação da hora anterior, rodada de hora em hora
INSERT INTO leitura_hora (tag_id, hora, n, media, minimo, maximo)
SELECT tag_id, substr(ts,1,13)||':00:00', COUNT(*),
       AVG(valor), MIN(valor), MAX(valor)
  FROM leitura
 WHERE ts >= :inicio AND ts < :fim AND qualidade = 'BOA'
 GROUP BY tag_id, substr(ts,1,13)
ON CONFLICT (tag_id, hora) DO UPDATE
   SET n = excluded.n, media = excluded.media,
       minimo = excluded.minimo, maximo = excluded.maximo;

DELETE FROM leitura WHERE ts < date('now', '-90 days');
```

O `ON CONFLICT` torna a consolidação **idempotente** — reexecutar não duplica.
Ver o exemplo 14 de [06-exemplos.md](06-exemplos.md).

⚠️ **Não se pode reagregar média de média sem o `n`.** A média de médias
horárias só é igual à média geral se todas as horas tiverem o mesmo número de
amostras — e não têm, por causa dos buracos. Guarde `n` e faça
`SUM(media*n)/SUM(n)`.

⚠️ **Min e máx reagregam perfeitamente** (`MIN(MIN)`, `MAX(MAX)`); desvio
padrão **não** — para reagregar desvio você precisa guardar `SUM(x)` e
`SUM(x²)`, não o desvio. Isso se chama agregação **algébrica** × **holística**,
e é a razão de a mediana ser impossível de reagregar (por isso todo sistema de
BI mente sobre mediana em drill-up).

---

## 9. Quando o SQL genérico deixa de bastar

| Volume/necessidade | Ferramenta |
|---|---|
| < 10 milhões de linhas | SQLite ou PostgreSQL puro. Simples assim |
| 10 M – 1 bilhão | **TimescaleDB** (extensão do PostgreSQL): partição automática por tempo, compressão de 90%+, *continuous aggregates*, `time_bucket_gapfill` |
| Análise sobre exportação em arquivo | **DuckDB**: `ASOF JOIN`, `time_bucket`, lê Parquet direto |
| Altíssima frequência (kHz), muitos escritores | InfluxDB, VictoriaMetrics, ClickHouse |
| Já existe na planta | **PI System, IP.21, PHD** — e você consulta via a camada SQL deles |

**Opinião profissional:** para 95% das plantas químicas brasileiras, o
historiador já existe e a decisão certa **não** é substituí-lo. É extrair dele
para um PostgreSQL/DuckDB onde você possa cruzar com LIMS, ERP e apontamento —
que é exatamente o que o historiador não faz bem. O historiador é ótimo em
guardar sinal e péssimo em relacionar. Ver
[30-engenharia-quimica.md](30-engenharia-quimica.md).

---

## Autoteste

1. Por que a chave `(tag_id, ts)` nessa ordem, e não `(ts, tag_id)`?
2. Formato longo × largo: por que longo vence para armazenamento?
3. Dê os dois problemas concretos de guardar timestamp em hora local.
4. Por que guardar min e máx junto com a média na reamostragem?
5. Cite as duas formas de achar buracos e diga quando usar cada uma.
6. O que é registro por exceção e quais **duas** consequências ele tem para as
   suas consultas?
7. Escreva a média ponderada no tempo e explique quando ela difere da média
   simples.
8. Por que agrupar por `substr(ts,1,10)` quebra o relatório de turno?
9. Por que não se pode reagregar média de médias sem o `n`? E desvio padrão?
10. Quando trocar PostgreSQL puro por TimescaleDB?

---

*Próximo: [19-ddl-e-modelagem.md](19-ddl-e-modelagem.md).*
