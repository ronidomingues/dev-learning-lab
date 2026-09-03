# 30 — SQL para engenheiros químicos

Nível: intermediário → avançado · Data: 13/08/2026

Este é o arquivo que responde à pergunta "para que serve isso no meu trabalho".
Ele supõe que você já leu, ou vai voltar a, [12](12-consulta-select.md),
[13](13-juncoes.md), [14](14-agregacao-e-grupos.md) e
[16](16-funcoes-de-janela.md).

---

## 1. O mapa dos sistemas de uma planta, e onde o SQL entra

Toda planta de processo tem uma pilha parecida, formalizada pela norma
**ISA-95** (a hierarquia de níveis de automação):

```
┌───────────────────────────────────────────────────────────────┐
│ Nível 4 · ERP        SAP, TOTVS, Oracle EBS                   │  banco SQL
│   ordens, custos, estoque, compras, contabilidade             │
├───────────────────────────────────────────────────────────────┤
│ Nível 3 · MES/MOM    ordem de produção, apontamento, OEE      │  banco SQL
│           LIMS       amostras, ensaios, laudos, especificação │  banco SQL
│           CMMS       manutenção, ordens de serviço, ativos    │  banco SQL
│           PIMS/Historiador   PI System, IP.21, PHD            │  ~SQL (leitura)
├───────────────────────────────────────────────────────────────┤
│ Nível 2 · SDCD/SCADA  controle, alarme, intertravamento       │  tempo real
├───────────────────────────────────────────────────────────────┤
│ Nível 1 · CLP, transmissores, válvulas                        │
├───────────────────────────────────────────────────────────────┤
│ Nível 0 · O processo. Reator, coluna, trocador                │
└───────────────────────────────────────────────────────────────┘
```

**O ponto que interessa:** dos níveis 3 e 4, **tudo é banco SQL**. E o problema
que ninguém resolve é que eles **não conversam entre si**:

- O historiador sabe que o TI-101 marcou 199 °C às 01:03 do dia 22.
- O MES sabe que a batelada B-2026-0057 rodou naquele horário.
- O LIMS sabe que o lote dessa batelada deu viscosidade 743 cP.
- O ERP sabe que o cliente devolveu o lote.
- O CMMS sabe que a válvula de vapor foi trocada dois dias antes.

**Nenhum sistema sabe os cinco fatos.** Ligar os cinco é uma junção. É
literalmente uma junção — e é o trabalho mais valioso que um engenheiro de
processo com SQL pode fazer, porque **ninguém mais na empresa tem, ao mesmo
tempo, o acesso e o entendimento do processo para fazê-lo.**

O analista de dados tem SQL e não sabe que 300 °C é termopar rompido. O
operador sabe do processo e não tem SQL. Você pode ter os dois.

---

## 2. Balanço de massa

O primeiro cálculo da profissão, e um `GROUP BY` com tolerância declarada.

```sql
SELECT b.batelada_id,
       b.carga_kg                                       AS entrada_apontada,
       ROUND(SUM(i.massa_kg), 1)                        AS soma_insumos,
       ROUND(SUM(i.massa_kg) - b.carga_kg, 1)           AS diferenca_kg,
       ROUND(100.0*(SUM(i.massa_kg) - b.carga_kg)/b.carga_kg, 3) AS erro_pct
  FROM batelada b
  JOIN consumo_insumo i USING (batelada_id)
 GROUP BY b.batelada_id, b.carga_kg
HAVING ABS(erro_pct) > 0.5              -- tolerância EXPLÍCITA
 ORDER BY ABS(erro_pct) DESC;
```

**Três coisas que fazem esta consulta ser de engenheiro e não de analista:**

1. **A tolerância está escrita.** Todo balanço de planta fecha com erro. O que
   separa dado útil de lixo é declarar qual erro é aceitável — 0,5% para
   apontamento manual, 0,1% para balança fiscal, 2% para estimativa por vazão.
2. **A unidade está no nome da coluna.** `massa_kg`, não `massa`.
3. **O `HAVING` procura o problema, não o normal.** Um relatório que lista as
   78 bateladas ninguém lê; um que lista as 9 que não fecham, todo mundo lê.

### Balanço por integração de vazão

Quando não há apontamento, integre a vazão. E aqui aparece a diferença entre
quem entende de instrumentação e quem não entende:

```sql
-- massa = ∫ vazão dt, por trapézio, com Δt REAL entre amostras
WITH s AS (
    SELECT ts, valor,
           LEAD(valor) OVER (ORDER BY ts) AS prox_v,
           (julianday(LEAD(ts) OVER (ORDER BY ts)) - julianday(ts)) * 24.0 AS dt_h
      FROM v_leitura_boa
     WHERE tag_id = 'FI-102'
       AND ts >= '2026-07-01 00:00:00' AND ts < '2026-07-01 06:00:00'
)
SELECT ROUND(SUM((valor + prox_v)/2.0 * dt_h), 1) AS massa_kg
  FROM s
 WHERE prox_v IS NOT NULL
   AND dt_h < 0.5;        -- ← descarta os buracos: não integre sobre lacuna
```

**A última linha é a que separa o número certo do errado.** Se houve 2 horas de
falha de aquisição, o trapézio entre a última leitura antes e a primeira depois
"inventa" 2 horas de vazão que ninguém mediu. Sem essa cláusula, o balanço
fecha lindamente e está errado. Ver
[18-series-temporais.md](18-series-temporais.md).

**Regra do trapézio × degrau:** o trapézio supõe variação linear entre
amostras; o degrau (ZOH) supõe constante. Para vazão medida por placa de
orifício com amostragem de 1 min, trapézio é razoável. Para um totalizador que
só reporta por exceção, degrau é o correto — e o historiador tem essa
configuração por tag. **Descubra qual antes de integrar.**

---

## 3. Rendimento e o custo do desvio

```sql
SELECT batelada_id,
       ROUND(100.0*produzido_kg/carga_kg, 2)                     AS rendimento_pct,
       ROUND(AVG(rendimento_pct) OVER (ORDER BY ts_inicio
                 ROWS BETWEEN 9 PRECEDING AND CURRENT ROW), 2)   AS mm10,
       RANK() OVER (ORDER BY produzido_kg/carga_kg)              AS pior_posicao
  FROM v_batelada WHERE status = 'CONCLUIDA';
```

**Traduzir desvio em dinheiro** é o que faz a análise virar projeto aprovado.
Do exemplo 10 de [06-exemplos.md](06-exemplos.md), executado:

```
inclinação da regressão rendimento × temperatura de reação = −0,3652 %/°C
```

Cada grau acima do setpoint custa 0,37 ponto de rendimento. Sobre 5.000 kg de
carga, 18 kg de produto. A 78 bateladas/mês e R$ 12/kg:

> **~R$ 17 mil por mês, por grau de desvio médio.**

Esse número é o que se leva para a reunião de investimento — não o gráfico de
temperatura.

⚠️ **E a ressalva profissional obrigatória:** correlação não é causa. Ver a
seção 9 deste arquivo.

---

## 4. Controle estatístico de processo (CEP)

```sql
WITH por_batelada AS (
    SELECT batelada_id, AVG(valor) AS media, COUNT(*) AS n,
           SUM(valor*valor) AS soma_q
      FROM v_leitura_fase
     WHERE tag_id = 'TI-101' AND fase = 'reacao'
     GROUP BY batelada_id
),
global AS (
    SELECT AVG(media) AS cl,
           sqrt((SUM(media*media) - COUNT(*)*AVG(media)*AVG(media))
                / (COUNT(*)-1.0)) AS s
      FROM por_batelada
)
SELECT p.batelada_id, ROUND(p.media,2) AS x_barra,
       ROUND(g.cl,2) AS LC,
       ROUND(g.cl + 3*g.s, 2) AS LSC,
       ROUND(g.cl - 3*g.s, 2) AS LIC,
       CASE WHEN ABS(p.media - g.cl) > 3*g.s THEN 'FORA' ELSE 'ok' END AS nelson_1
  FROM por_batelada p CROSS JOIN global g;
```

### O erro conceitual que o SQL não impede

> **Limite de controle ≠ limite de especificação.**

- **Especificação (LIE/LSE)**: vem do cliente e do projeto. O que o produto
  *precisa* ser.
- **Controle (LIC/LSC)**: ±3σ da variação natural. O que o processo
  *consegue* ser.

Plotar limite de especificação numa carta de controle leva a "ajustar" o
processo a cada ponto fora da spec — o que **aumenta** a variância. É o
experimento do funil, de Deming, e continua sendo o erro mais caro do CEP mal
aplicado, sessenta anos depois.

### Capacidade

```
Cp  = (LSE − LIE) / 6σ
Cpk = min(LSE − μ, μ − LIE) / 3σ
```

Cp mede o potencial (a largura); Cpk mede o real (largura **e** centragem).
Cp alto com Cpk baixo = processo capaz, mas descentrado — ajuste o setpoint,
não a variabilidade.

Referências de mercado: Cpk ≥ 1,33 é aceitável; ≥ 1,67 é bom; 2,0 é o
"seis sigma". *(O projeto-modelo devolve Cpk ≈ 3,2 porque o dado é sintético e
bem-comportado demais — está declarado no [README](07-projeto-modelo/README.md).)*

### Regras de Nelson

As oito regras clássicas de detecção de causa especial. Em SQL:

| Regra | O que detecta | Como fazer |
|---|---|---|
| 1 — 1 ponto além de 3σ | Choque | `CASE WHEN ABS(x-cl) > 3*s` |
| 2 — 9 pontos seguidos do mesmo lado | Deslocamento de média | *gaps and islands* sobre `SIGN(x-cl)` |
| 3 — 6 pontos crescendo/decrescendo | Tendência (desgaste, incrustação) | `LAG` + *gaps and islands* |
| 4 — 14 alternando | Superajuste do operador ou dois turnos | `LAG` + contagem de alternância |
| 5 — 2 de 3 além de 2σ | Deriva | janela `ROWS 2 PRECEDING` + `COUNT FILTER` |

A regra 3 é a mais valiosa em planta: tendência monotônica é incrustação,
catalisador desativando, filtro entupindo — **degradação previsível**, que é
justamente o que a manutenção preditiva quer pegar.

```sql
-- Regra 2 de Nelson: 9 pontos consecutivos do mesmo lado da linha central
WITH p AS (SELECT batelada_id, ts_inicio, media,
                  CASE WHEN media > (SELECT AVG(media) FROM por_batelada)
                       THEN 1 ELSE -1 END AS lado
             FROM por_batelada JOIN batelada USING (batelada_id)),
   blocos AS (SELECT *, ROW_NUMBER() OVER (ORDER BY ts_inicio)
                      - ROW_NUMBER() OVER (PARTITION BY lado ORDER BY ts_inicio) AS g
                FROM p)
SELECT lado, MIN(ts_inicio) AS de, MAX(ts_inicio) AS ate, COUNT(*) AS seguidos
  FROM blocos GROUP BY lado, g HAVING COUNT(*) >= 9;
```

---

## 5. OEE e disponibilidade

```
OEE = Disponibilidade × Desempenho × Qualidade
```

Do [projeto-modelo](07-projeto-modelo/), executado:

```
horas calendário    720,0
horas produzindo    478,7  →  disponibilidade  66,5 %
78 bateladas (77 concluídas, 1 abortada)
desempenho          96,5 %  (ciclo real vs. teórico de 6 h)
qualidade           91,0 %  (massa aprovada / massa produzida)
OEE                 58,4 %
```

**A honestidade do denominador é tudo.** O erro universal do OEE é escolher o
denominador que faz o número ficar bonito: "tempo calendário" vira "tempo
programado", e as 72 horas de parada de manutenção somem. O OEE sobe de 58%
para 65% sem nada ter mudado na planta.

**Escreva a definição junto com o número, sempre.** Um OEE sem definição
declarada não é comparável nem com ele mesmo do mês anterior.

E a decisão que mais muda o resultado: **batelada abortada conta como tempo
produzindo?** Não. Conta como perda. Muita gente conta como produzindo, e o
número fica bonito.

---

## 6. Racionalização de alarmes (ISA-18.2 / EEMUA 191)

Meta prática do EEMUA 191: no máximo ~**6 alarmes por hora** por operador em
regime normal, e menos de **10 nos 10 minutos** após um distúrbio. Acima disso
o operador para de ler — e Texas City (2005) e Milford Haven (1994) mostraram
o que vem depois.

```sql
SELECT a.tag_id, t.descricao, a.tipo,
       COUNT(*)                                                  AS n,
       ROUND(COUNT(*)/30.0, 2)                                   AS por_dia,
       COUNT(*) FILTER (WHERE a.ts_reconhecimento IS NULL)       AS nao_reconhecidos,
       ROUND(AVG((julianday(a.ts_normalizacao)-julianday(a.ts))*1440), 1) AS dur_min,
       COUNT(*) FILTER (WHERE (julianday(a.ts_normalizacao)-julianday(a.ts))*1440 < 2
                          AND a.ts_reconhecimento IS NULL)       AS fugazes
  FROM evento_alarme a JOIN tag t USING (tag_id)
 GROUP BY 1,2,3 ORDER BY n DESC;
```

Resultado do projeto-modelo — **12 eventos em 30 dias**:

```
PI-101 ALTO    5 eventos  100 % fugazes  ← espículas de instrumento
AI-101 BAIXO   4 eventos   75 % fugazes  ← limite mal ajustado
TI-101 ALTO    2 eventos    0 % fugazes  ← as DUAS excursões reais
AI-101 ALTO    1 evento   147 min        ← sensor de pH sujo
```

**Dez dos doze alarmes não eram processo.** Os dois que importavam ficaram
enterrados. Numa planta real com 3.000 tags o padrão é o mesmo, em escala:
tipicamente 80% dos alarmes vêm de menos de 20 tags — Pareto puro.

**O relatório que resolve** é este, ordenado por frequência: os "*bad actors*".
Corrigir os dez piores tags costuma cortar metade dos alarmes. É um projeto de
engenharia com retorno mensurável, e o SQL é a ferramenta inteira dele.

⚠️ A consulta acima conta **eventos**, não distúrbios. Um alarme que oscila 40
vezes em 10 minutos (*chattering*) pode aparecer como poucos eventos. Para
racionalização séria, conte transições cruas e agrupe por proximidade.

---

## 7. Qualidade, LIMS e liberação de lote

```sql
SELECT b.batelada_id, b.ts_fim,
       COUNT(*) FILTER (WHERE v.veredito <> 'CONFORME') AS fora_de_spec,
       GROUP_CONCAT(CASE WHEN v.veredito <> 'CONFORME'
                    THEN v.parametro||'='||ROUND(v.valor,1) END, '; ') AS detalhe,
       CASE WHEN COUNT(*) FILTER (WHERE v.veredito <> 'CONFORME') = 0
            THEN 'LIBERADO' ELSE 'RETIDO' END AS decisao
  FROM v_batelada b JOIN v_lab_conforme v USING (batelada_id)
 GROUP BY 1,2 HAVING fora_de_spec > 0;
```

**Três coisas que uma auditoria vai perguntar e que só o SQL responde bem:**

1. **A especificação vigente na data do lote.** Um lote de 2024 tem de ser
   julgado pela spec de 2024, não pela de hoje. Isso exige historiar a
   especificação (SCD tipo 2 — ver [19](19-ddl-e-modelagem.md)). Quem guarda só
   a spec atual não consegue reproduzir o laudo histórico.
2. **De onde veio o número.** Uma consulta versionada no git é rastreável;
   uma planilha não é.
3. **O atraso do laboratório.** No projeto-modelo, o laudo sai **4 a 5 horas
   depois** do fim da batelada. Nesse intervalo, a planta já fez a próxima com
   os mesmos parâmetros. É o argumento econômico dos analisadores em linha e
   dos *soft sensors*: cada hora de atraso é uma batelada de risco.

---

## 8. Manutenção e confiabilidade

```sql
-- MTBF e MTTR por equipamento
WITH falhas AS (
    SELECT equipamento_id, ts_inicio, ts_fim,
           (julianday(ts_fim) - julianday(ts_inicio)) * 24.0            AS reparo_h,
           (julianday(ts_inicio)
            - julianday(LAG(ts_fim) OVER (PARTITION BY equipamento_id
                                          ORDER BY ts_inicio))) * 24.0  AS operou_h
      FROM parada WHERE categoria = 'FALHA'
)
SELECT equipamento_id,
       COUNT(*)                 AS falhas,
       ROUND(AVG(operou_h), 1)  AS MTBF_h,
       ROUND(AVG(reparo_h), 1)  AS MTTR_h,
       ROUND(100.0*AVG(operou_h)/(AVG(operou_h)+AVG(reparo_h)), 2) AS disponibilidade_pct
  FROM falhas WHERE operou_h IS NOT NULL
 GROUP BY equipamento_id;
```

**Manutenção preditiva começa aqui**, não em aprendizado de máquina. As
consultas que pegam degradação antes da falha:

| Sinal | Consulta |
|---|---|
| Tendência monotônica | Regra 3 de Nelson, ou inclinação da regressão por janela móvel |
| Vibração/corrente subindo | Média móvel de 7 dias contra a de 90 dias |
| Aproximação do limite | `COUNT(*) FILTER (WHERE valor > 0.9*limite)` por semana |
| Trocador incrustando | `(T_entrada − T_saída)` caindo com vazão constante — a queda do U |
| Filtro entupindo | ΔP subindo com vazão constante |
| Bomba cavitando | Variância da pressão de sucção aumentando |

O quarto item merece nota: **coeficiente global de troca térmica** estimado por
SQL é uma das análises de maior retorno que existem, porque a incrustação é
lenta, previsível e cara.

```sql
-- proxy de U: carga térmica / ΔT médio logarítmico, por dia
WITH d AS (
  SELECT substr(ts,1,10) AS dia,
         AVG(CASE WHEN tag_id='FI-201' THEN valor END) AS vazao_kg_h,
         AVG(CASE WHEN tag_id='TI-201' THEN valor END) AS t_saida,
         AVG(CASE WHEN tag_id='TI-101' THEN valor END) AS t_quente
    FROM v_leitura_boa GROUP BY 1)
SELECT dia,
       ROUND(vazao_kg_h * 4.18 * (t_saida - 22.0), 0)                AS carga_kJ_h,
       ROUND(t_quente - t_saida, 2)                                  AS delta_T,
       ROUND(vazao_kg_h * 4.18 * (t_saida - 22.0)
             / NULLIF(t_quente - t_saida, 0), 1)                     AS UA_proxy
  FROM d ORDER BY dia;
```

Uma queda consistente do `UA_proxy` ao longo de semanas **é** a incrustação, e
a data em que ele cruza o limite econômico **é** a data de parada para limpeza.

⚠️ Este é um *proxy*, não um cálculo rigoroso: usa ΔT simples em vez de LMTD,
supõe cp constante e ignora a temperatura de entrada da água. Serve para ver
tendência, não para dimensionar equipamento. **Diga isso no relatório.**

---

## 9. Sustentabilidade, energia e emissões

Área que cresceu muito com CBAM, ESG e metas de descarbonização.

```sql
-- intensidade energética: kWh por tonelada de produto, por mês
WITH energia AS (
    SELECT substr(ts,1,7) AS mes, SUM(valor)/60.0 AS kwh   -- kW amostrado por minuto
      FROM v_leitura_boa WHERE tag_id = 'JI-101' GROUP BY 1
),
producao AS (
    SELECT substr(ts_inicio,1,7) AS mes, SUM(produzido_kg)/1000.0 AS toneladas
      FROM batelada WHERE status='CONCLUIDA' GROUP BY 1
)
SELECT e.mes,
       ROUND(e.kwh, 0)                            AS kwh,
       ROUND(p.toneladas, 1)                      AS toneladas,
       ROUND(e.kwh / NULLIF(p.toneladas, 0), 1)   AS kwh_por_tonelada
  FROM energia e JOIN producao p USING (mes) ORDER BY mes;
```

**O detalhe que engenheiro nota e programador não:** `SUM(valor)/60.0` só está
certo se a amostragem for uniforme de 1 minuto. Com registro por exceção, a
integral correta é `SUM(potência × Δt)` com `Δt` real — ver a seção 2.

Emissões (Escopo 1) seguem o mesmo padrão: consumo × fator de emissão, com o
fator numa tabela **historiada** (ele muda por ano e por fonte, e o relatório
de 2024 precisa do fator de 2024).

---

## 10. As três armadilhas de análise de dado de processo

### 10.1 Correlação não é causa — o exemplo executado

Do exemplo 9 de [06-exemplos.md](06-exemplos.md):

```
batelada    | temp_reacao | viscosidade
B-2026-0057 |      189,38 |       743,7   ← a hipótese funciona
B-2026-0072 |      180,17 |       650,9   ← e aqui?
B-2026-0007 |      181,91 |       641,6
B-2026-0044 |      180,60 |       636,0
B-2026-0069 |      179,48 |       620,3
```

A primeira linha confirma "temperatura alta → viscosidade alta". **As quatro
seguintes destroem a explicação:** viscosidade igualmente fora de spec, com
temperatura perfeitamente normal.

Se você parasse na primeira linha — e é o que a maioria faz, porque confirma a
hipótese — sairia da reunião com uma ação sobre controle de temperatura, e o
problema continuaria em 80% dos casos.

Numa planta real, pico de temperatura estará correlacionado também com carga,
lote de matéria-prima, turno, umidade ambiente e dia da semana — todos
correlacionados **entre si**. O SQL entrega a correlação. **Quem elimina
hipótese é o engenheiro.**

### 10.2 O dado que não está lá

Três ausências invisíveis, em ordem de perigo:

1. **Linha inexistente.** `COUNT(*)` não vê o que não está. Só uma série de
   referência revela. No projeto-modelo, 2 horas apagadas do dia 14/07 — 0,28%
   dos dados. Se fosse durante a excursão, mudaria a conclusão inteira.
2. **Dado marcado como bom que não é.** As espículas de 9,9 bar do defeito A8
   têm qualidade `BOA`, z-score 63, e geram alarme. O flag de qualidade do
   coletor **não pega tudo**.
3. **Viés de sobrevivência do sensor.** Instrumento falha justamente em
   condição extrema — satura, esquenta, entope. Os nulos **não são aleatórios**,
   e ignorá-los (o que `AVG` faz sozinho) enviesa a média para o lado bonito.

### 10.3 Somar o que não se soma

O SQL calcula qualquer coisa que você pedir. Ele não sabe termodinâmica.

| Grandeza | `SUM` faz sentido? | O que fazer |
|---|---|---|
| Massa, energia, volume | **Sim** — extensivas | Somar |
| Temperatura, pressão, pH, densidade | **Não** — intensivas | Média (ponderada, se for o caso) |
| Vazão | **Não** — é taxa | Integrar: `SUM(vazão × Δt)` |
| Nível | **Não** — é estado | Diferença entre início e fim |
| Concentração | **Não** | Média ponderada pela vazão mássica |
| Rendimento, OEE, disponibilidade | **Não** (média de razões) | Razão de somas |

A média de pH merece destaque: **pH é logarítmico.** A média aritmética de pH 3
e pH 7 não é pH 5 — a média correta passa pela concentração de H⁺:
`-log10(AVG(power(10, -ph)))`. Quase todo relatório de efluente do país erra
isso.

---

## 11. Trilha de 90 dias para um engenheiro de processo

| Semana | O que fazer | Arquivo |
|---|---|---|
| 1 | Instalar; rodar o projeto-modelo; primeiras consultas | [03](03-instalacao.md), [04](04-como-comecar.md) |
| 2–3 | `SELECT`, `WHERE`, `GROUP BY` sobre uma exportação **real** do seu historiador | [12](12-consulta-select.md), [14](14-agregacao-e-grupos.md) |
| 4–5 | `JOIN`: cruzar processo com laboratório ou com apontamento | [13](13-juncoes.md) |
| 6–7 | Funções de janela: média móvel, taxa, *gaps and islands* | [16](16-funcoes-de-janela.md) |
| 8–9 | **Refazer um relatório que você faz na planilha.** Compare os números | [06](06-exemplos.md), este arquivo |
| 10–11 | Automatizar: Python + agendamento; salvar `.sql` no git | [24](24-sql-com-python.md) |
| 12–13 | Pedir acesso somente-leitura ao banco corporativo; camada semântica | [22](22-views-e-analitico.md) |

**O marco da semana 8–9 é o único que importa de verdade.** Refazer um
relatório existente é o exercício que prova o valor: você já sabe a resposta
certa, então descobre imediatamente onde errou — e, com frequência
desconfortável, descobre que a **planilha** é que estava errada.

**Como pedir acesso** (o obstáculo real, e é político, não técnico):

1. Peça **somente leitura**, a uma **réplica**, não ao banco de produção.
2. Diga qual relatório específico você quer eliminar, com o tempo que ele
   consome hoje em horas por mês.
3. Ofereça-se para documentar as consultas e entregá-las à área de TI.
4. Comece por um sistema de menor risco (historiador ou LIMS) antes do ERP.

---

## 12. Ferramentas do mercado, e onde o SQL se encaixa

| Ferramenta | O que faz | Precisa de SQL? |
|---|---|---|
| **Seeq** | Análise de série temporal sobre historiadores (PI, IP.21, PHD, Proficy), com busca por padrão e capsulas de contexto | Não, mas ajuda a entender o que ela faz |
| **TrendMiner** | Concorrente direto do Seeq; mesma proposta | Idem |
| **Power BI / Tableau** | Painéis | **Sim** — quando fica lento, é o SQL gerado |
| **PI Vision / PI DataLink** | Visualização e exportação do PI para Excel | Não, mas o PI SQL Client existe |
| **Aspen Mtell / Prescriptive** | Manutenção preditiva | Não |
| **dbt** | Transformação em SQL com testes e documentação | **Só SQL** |
| **Python + pandas** | Modelagem, gráfico, estatística | Complementar |

**Opinião profissional, declarada:** Seeq e TrendMiner são excelentes no que
fazem — análise exploratória de série temporal com contexto — e resolvem em
minutos o que em SQL leva horas. **Mas** custam caro (licença por usuário, na
casa das dezenas de milhares de reais por ano), dependem do fornecedor, e **não
substituem o SQL** no ponto que mais importa: cruzar o historiador com LIMS,
ERP, CMMS e apontamento. Essa junção continua sendo sua.

Meu conselho, na prática: **aprenda SQL primeiro.** Ele é gratuito, universal,
funciona em todos os sete sistemas da pilha ISA-95, e não some quando a empresa
corta o contrato de licença. Se depois a empresa comprar Seeq, você vai
aproveitar melhor — porque vai entender o que a ferramenta está fazendo por
baixo.

---

## Autoteste

1. Cite os cinco sistemas de uma planta que guardam parte da história de um
   lote, e o que cada um sabe.
2. Por que você, engenheiro químico, está em melhor posição que um analista de
   dados para fazer essa junção?
3. Na integração de vazão, por que a cláusula `dt_h < 0.5` é essencial?
4. Diferencie limite de controle e limite de especificação. O que acontece
   quando se confundem?
5. Cp alto e Cpk baixo: o que fazer?
6. Qual regra de Nelson detecta incrustação, e por que ela é a mais valiosa em
   planta?
7. Qual escolha muda mais o OEE, e como se manipula esse número sem mentir?
8. Dos 12 alarmes do projeto-modelo, quantos eram processo real? O que isso
   ensina?
9. Por que o atraso do laboratório é um argumento econômico para analisador em
   linha?
10. Cite três grandezas que não se soma e o que fazer no lugar.
11. Por que a média aritmética de pH está errada, e qual a certa?
12. Como você pediria acesso ao banco corporativo? Descreva os quatro passos.

---

## Fontes

- ISA-95 (hierarquia de níveis) e ISA-88 (controle de batelada) — ISA.
- ISA-18.2 e EEMUA 191 — gestão de alarmes.
- AVEVA PI SQL Client (ODBC/OLE DB) e PI OLEDB Enterprise:
  <https://docs.aveva.com/bundle/pi-sql-client-oledb/page/1014303.html>
- Panorama de historiadores e analítica industrial (Seeq, TrendMiner, IP.21,
  PHD, PI System) — pesquisa web em 13/08/2026.
- Cálculos e números do [projeto-modelo](07-projeto-modelo/), **executados**
  em 13/08/2026.

---

*Próximo: [60-teoria-avancada.md](60-teoria-avancada.md), ou
[70-pratica.md](70-pratica.md) para colocar a mão.*
