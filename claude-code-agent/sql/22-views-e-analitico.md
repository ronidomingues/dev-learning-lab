# 22 — Views, camada semântica e SQL analítico

Nível: intermediário · Data: 13/08/2026

Como transformar um monte de consultas soltas em algo que a organização inteira
usa e confia. É aqui que SQL deixa de ser habilidade individual e vira ativo da
área.

---

## 1. View: uma consulta com nome

```sql
CREATE VIEW v_leitura_boa AS
SELECT tag_id, ts, valor
  FROM leitura
 WHERE qualidade = 'BOA' AND valor IS NOT NULL;

SELECT AVG(valor) FROM v_leitura_boa WHERE tag_id = 'TI-101';
```

Uma view **não guarda dado**. Toda vez que você a consulta, o banco executa a
consulta de dentro. Ela é substituição de texto com otimização.

### As três razões de existir

**1. A definição em UM lugar.**

O que é "dado confiável"? Se cada engenheiro escrever seu filtro, um vai
esquecer a qualidade, outro vai esquecer o `NULL`, e os dois relatórios vão
divergir na reunião. A discussão vira "de quem é o número certo" em vez de
"o que fazer com o número" — e essa é a pior reunião que existe.

**2. Esconder junção que todo mundo erra.**

`v_leitura_batelada` esconde a junção temporal com intervalo semiaberto. Quem
usa a view não tem como errar a fronteira.

**3. Interface estável.**

O Power BI do gerente aponta para `v_batelada`. Você reorganiza a tabela por
baixo, muda nome de coluna, particiona — e o relatório continua funcionando,
desde que a view mantenha as mesmas colunas.

### Custo e limite

Views não custam nada por si: o otimizador achata (*inline*) a definição e
otimiza o conjunto. **Mas**:

⚠️ **View sobre view sobre view** vira uma consulta gigantesca que o
otimizador pode não conseguir simplificar. Três níveis é o limite prático; a
partir daí, meça.

⚠️ **View com `GROUP BY` consultada com `WHERE`** pode não conseguir empurrar
o filtro para dentro (o *predicate pushdown* falha através de agregação em
alguns casos), e aí você agrega tudo para filtrar dez linhas.

---

## 2. View materializada

Uma view **materializada** guarda o resultado. Vira uma tabela que se atualiza.

```sql
-- PostgreSQL
CREATE MATERIALIZED VIEW mv_producao_diaria AS
SELECT substr(ts_inicio,1,10) AS dia, COUNT(*) AS n, SUM(produzido_kg) AS kg
  FROM batelada GROUP BY 1;

REFRESH MATERIALIZED VIEW CONCURRENTLY mv_producao_diaria;
```

| | View | View materializada |
|---|---|---|
| Guarda dado | Não | Sim |
| Sempre atual | Sim | Só até o último `REFRESH` |
| Custo de leitura | O da consulta | O de ler uma tabela |
| Custo de escrita | Zero | O `REFRESH` |
| Existe em | Todos | PostgreSQL, Oracle, SQL Server (*indexed view*), DuckDB. **Não no SQLite** |

**No SQLite**, emule com tabela + processo de atualização (é o que o
[projeto-modelo](07-projeto-modelo/) faria numa versão de produção, e o que a
seção de consolidação de [18-series-temporais.md](18-series-temporais.md)
descreve).

**TimescaleDB** tem *continuous aggregates*: view materializada que se
atualiza **incrementalmente** — só recalcula os buckets de tempo que mudaram.
Para dado de planta, é a funcionalidade mais valiosa do produto.

---

## 3. Camada semântica

O padrão que separa área de dados profissional de amadora. Três camadas:

```
┌──────────────────────────────────────────────────────────┐
│ CONSUMO      Power BI · Excel · Python · relatório PDF   │
├──────────────────────────────────────────────────────────┤
│ SEMÂNTICA    v_batelada · v_leitura_fase · v_oee         │  ← views
│              nomes de negócio, regras únicas, unidades   │
├──────────────────────────────────────────────────────────┤
│ BRUTA        leitura · batelada · analise_lab            │  ← tabelas
│              como o dado chegou; ninguém consulta direto │
└──────────────────────────────────────────────────────────┘
```

**A regra:** o usuário final **nunca** consulta a camada bruta. Se ele
consulta, cada um reimplementa a regra do seu jeito e você perde o controle do
número.

**Como se implementa a proibição, na prática:** permissão. Dê `SELECT` nas
views e não nas tabelas.

```sql
-- PostgreSQL
REVOKE ALL ON leitura FROM analista;
GRANT SELECT ON v_leitura_boa TO analista;
```

No SQLite não há usuários — a separação é por convenção e disciplina, o que
significa que ela vai ser violada. É mais um argumento para PostgreSQL quando
o uso deixa de ser individual.

### O que colocar na camada semântica

| Coisa | Exemplo |
|---|---|
| Definição de qualidade | `v_leitura_boa` |
| Grandeza derivada | `rendimento_pct`, `duracao_h` |
| Junção difícil | `v_leitura_batelada`, `v_leitura_fase` |
| Regra de conformidade | `v_lab_conforme` com o veredito |
| Conversão de unidade | tudo em kg, tudo em °C, sempre |
| Nomes de negócio | `rendimento_pct`, não `p_kg_div_c_kg` |
| Filtro de escopo | só bateladas concluídas, só a planta X |

---

## 4. Modelagem analítica: estrela

Vindo do vocabulário de *data warehouse* (Ralph Kimball), e é o modelo que o
Power BI espera.

```
                    ┌──────────────┐
                    │  dim_tempo   │
                    └───────┬──────┘
    ┌──────────────┐        │        ┌──────────────┐
    │ dim_equipam. ├────┐   │   ┌────┤  dim_produto │
    └──────────────┘    │   │   │    └──────────────┘
                     ┌──┴───┴───┴──┐
                     │ fato_batelada│   ← medidas: carga_kg, produzido_kg,
                     └──┬───────────┘      duracao_h, energia_kwh
    ┌──────────────┐    │
    │ dim_operador ├────┘
    └──────────────┘
```

| | Fato | Dimensão |
|---|---|---|
| Contém | Números que se somam | Atributos que descrevem |
| Volume | Muitas linhas | Poucas |
| Exemplo | `fato_batelada`, `fato_leitura` | `dim_tempo`, `dim_equipamento` |
| Muda | Só cresce | Devagar (ver SCD em [19](19-ddl-e-modelagem.md)) |

**Vale a pena?** Para um relatório de Power BI que a fábrica inteira usa, sim:
o modelo em estrela é o que as ferramentas de BI otimizam, e a `dim_tempo`
(uma linha por dia, com mês, trimestre, semana, turno, feriado, dia útil) evita
recalcular calendário em toda consulta.

Para uma análise pontual, é burocracia. **Não monte um data warehouse para
responder uma pergunta.**

---

## 5. Consultas analíticas típicas

### Comparação com o período anterior

```sql
WITH mensal AS (
    SELECT substr(ts_inicio,1,7) AS mes,
           SUM(produzido_kg)     AS kg
      FROM batelada WHERE status='CONCLUIDA' GROUP BY 1
)
SELECT mes, kg,
       LAG(kg) OVER (ORDER BY mes)                                AS mes_anterior,
       ROUND(100.0*(kg - LAG(kg) OVER (ORDER BY mes))
             / LAG(kg) OVER (ORDER BY mes), 1)                    AS variacao_pct
  FROM mensal ORDER BY mes;
```

### Acumulado no ano (*year to date*)

```sql
SELECT mes, kg,
       SUM(kg) OVER (ORDER BY mes ROWS UNBOUNDED PRECEDING) AS acumulado
  FROM mensal;
```

### Pareto (80/20)

```sql
SELECT causa, horas,
       ROUND(100.0*horas/SUM(horas) OVER (), 1)                        AS pct,
       ROUND(100.0*SUM(horas) OVER (ORDER BY horas DESC
                                    ROWS UNBOUNDED PRECEDING)
             / SUM(horas) OVER (), 1)                                  AS acumulado
  FROM (SELECT causa, SUM(dur_h) AS horas FROM parada GROUP BY causa)
 ORDER BY horas DESC;
```

### Coorte / campanha

"As bateladas do lote de matéria-prima X renderam diferente das do lote Y?" —
agrupe por lote e compare distribuição, não só média (ver quartis no exemplo 12
de [06-exemplos.md](06-exemplos.md)).

---

## 6. SQL gerado por ferramenta

Power BI, Tableau, Metabase e Superset **geram SQL**. Quando o painel está
lento, o problema é o SQL gerado — e ele costuma ser feio.

**Como ver o que a ferramenta gerou:**

- Power BI: *Performance Analyzer* → copiar a consulta DAX/SQL.
- Metabase: botão "ver o SQL".
- PostgreSQL, do lado do servidor:
  ```sql
  SELECT query, calls, mean_exec_time
    FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20;
  ```

**Os problemas típicos e as correções:**

| Problema | Correção |
|---|---|
| `SELECT *` com 40 colunas | Aponte a ferramenta para uma view enxuta |
| Filtro de data com função na coluna | Faça a view expor uma coluna `dia` já pronta e indexada |
| Junção de 12 tabelas em toda visualização | Materialize numa tabela estrela |
| Re-agrega 100 M linhas a cada clique | Tabela de resumo horário/diário |

**Isto é o argumento profissional para a camada semântica:** você não controla
o SQL que a ferramenta gera, mas controla **sobre o que** ela gera.

---

## 7. Controle de versão e teste de SQL

SQL é código. Trate como código.

```
sql/
├── migracoes/        001-..., 002-...     ← esquema, numeradas, nunca editadas
├── views/            v_batelada.sql       ← recriáveis, idempotentes
├── consultas/        relatorio-mensal.sql ← analíticas, comentadas
└── testes/           test_views.py
```

**O que testar** (e o [projeto-modelo](07-projeto-modelo/testes/) faz os cinco):

1. **Restrições rejeitam o que devem** — insira lixo e espere erro.
2. **Views devolvem o que se espera** — sobre dado conhecido, com resposta
   conhecida.
3. **Invariantes de negócio** — nenhuma leitura em duas bateladas; rendimento
   entre 0 e 100; soma bate com a fonte.
4. **As consultas executam** — protege contra a coluna renomeada que quebrou
   dez relatórios.
5. **Reconciliação** — o total da view resumo bate com o total da tabela bruta.

**Ferramentas:** `dbt` (o padrão de mercado para transformação em SQL, com
testes e documentação), `SQLFluff` (formatador e *linter*), `pgTAP`
(testes dentro do PostgreSQL). Todas gratuitas.

**O ponto que quase ninguém faz e deveria:** um teste de **reconciliação**
rodando todo dia, comparando o número do relatório gerencial com o número da
fonte. É o que descobre, em 24 horas em vez de 6 meses, que alguém mudou uma
regra e o painel passou a mentir.

---

## Autoteste

1. Uma view guarda dado? O que ela custa?
2. Cite as três razões para criar uma view e dê um exemplo de planta para cada.
3. Quando view materializada compensa? Cite o custo.
4. O que é camada semântica e como se **força** que ela seja usada?
5. Fato × dimensão: dê dois exemplos de cada numa planta química.
6. Quando modelagem em estrela é burocracia desnecessária?
7. Seu painel de BI está lento. Descreva o roteiro de diagnóstico.
8. Cite cinco coisas que se deve testar numa base analítica.
9. O que é um teste de reconciliação e o que ele protege?

---

*Próximo: [23-dialetos.md](23-dialetos.md).*
