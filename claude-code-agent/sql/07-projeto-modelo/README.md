# Projeto-modelo — Historiador de uma planta química em batelada

Nível: iniciante → avançado · Data: 13/08/2026 · Testado em: Python 3.10.12, SQLite 3.37.2 (Ubuntu 22.04)

Uma aplicação pequena mas **inteira**: esquema, carga de dados, camada
semântica, 14 consultas analíticas, 31 testes automatizados. Roda com
**Python e nada mais** — o SQLite vem embutido na biblioteca padrão do Python.

O que se está modelando: uma unidade de **resina alquídica em batelada**, com
reator R-101, trocador E-201, 8 instrumentos amostrados a cada minuto,
laboratório (LIMS), alarmes e apontamento de paradas. Trinta dias de operação,
~345 mil leituras.

---

## Como rodar

Pré-requisito único: **Python 3.8 ou superior**. Confira:

```bash
python3 --version
# esperado: Python 3.8.x ou superior
```

```bash
# 1. entre na pasta do projeto
cd 07-projeto-modelo

# 2. construa o banco (leva ~5 s e gera ~29 MB)
python3 scripts/gerar_dados.py

# 3. rode todas as consultas
python3 scripts/consultar.py

# 4. rode os testes
python3 -m unittest discover -s testes -v
```

Com `make`, os mesmos passos são `make banco`, `make consultas`, `make teste`,
e `make` sozinho faz os três.

Saída esperada do passo 2:

```
Banco criado em .../planta.db
  equipamento             5 linhas
  tag                     8 linhas
  leitura            344640 linhas
  batelada               78 linhas
  consumo_insumo        312 linhas
  analise_lab           308 linhas
  evento_alarme          16 linhas
  parada                 79 linhas
  tamanho              28.6 MB
```

Saída esperada do passo 4: `Ran 31 tests ... OK`.

O arquivo `planta.db` **não** está no git: ele se reconstrói a partir do
gerador, que é determinístico. Semente 42 → sempre o mesmo banco. É por isso
que os testes podem afirmar números exatos.

### Se você quiser usar o cliente `sqlite3` de linha de comando

```bash
sqlite3 planta.db
sqlite> .mode box
sqlite> .read consultas/01-panorama.sql
sqlite> .quit
```

Instalação do cliente: `sudo apt install sqlite3` (Debian/Ubuntu),
`brew install sqlite` (macOS), ou baixe o *bundle* em <https://sqlite.org/download.html>
(Windows). Ele **não** é necessário para rodar o projeto — o Python basta.

---

## Estrutura

```
07-projeto-modelo/
├── Makefile                     atalhos: banco, consultas, teste, plano, limpar
├── sql/
│   ├── 001-esquema.sql          DDL: 8 tabelas, restrições, índices
│   ├── 002-views.sql            camada semântica: 7 views
│   └── 003-seed-cadastro.sql    dados mestres (equipamentos e tags)
├── scripts/
│   ├── gerar_dados.py           gera 30 dias de operação sintética + 8 defeitos
│   └── consultar.py             executa as consultas e formata a saída
├── consultas/                   14 análises, uma por arquivo, comentadas
└── testes/
    └── test_consultas.py        31 testes: esquema, restrições, defeitos, consultas
```

---

## O que cada decisão de projeto ensina

| Decisão | Onde | O que ensina |
|---|---|---|
| `PRIMARY KEY (tag_id, ts)` nessa ordem | `001` | A ordem das colunas do índice é a ordem das perguntas. Invertida, a consulta típica fica 100× mais lenta. |
| `WITHOUT ROWID` na tabela de leituras | `001` | Índice agrupado: a tabela *é* o índice. Vale quando o acesso pela chave domina. |
| `STRICT` em todas as tabelas | `001` | Sem isso o SQLite aceita `'quente'` numa coluna `REAL`. Há um teste que prova. |
| `ts` como TEXT ISO-8601 em UTC | `001` | Ordem lexicográfica = ordem cronológica. E UTC porque horário de verão já apagou dado de planta. |
| `CHECK ((status='EM_ANDAMENTO') = (ts_fim IS NULL))` | `001` | Regra de negócio no banco, não no app: o banco é o único ponto por onde todos passam. |
| Intervalo semiaberto `[início, fim)` | `002` | Com `<=` dos dois lados, a leitura da virada pertence a duas bateladas e o total passa de 100%. Há um teste. |
| View `v_leitura_boa` | `002` | A definição de "dado confiável" em UM lugar — senão cada relatório dá um número. |
| Desvio padrão calculado na mão | `002` | SQLite não tem `STDDEV`. E a fórmula de um passo tem problema numérico conhecido. |
| Alarmes derivados das leituras | `gerar_dados.py` | Dado derivado gerado a partir da fonte nunca diverge dela. |
| Uma transação para 345 mil linhas | `gerar_dados.py` | Um `COMMIT` por linha seria minutos em vez de segundos: cada commit é um `fsync`. |

---

## Os oito defeitos plantados

O gerador **cria problemas de propósito**. Cada um tem uma consulta que o acha
e um teste que garante que ela acha. É assim que se aprende análise de dado de
processo: não com dado limpo, que não existe.

| # | Defeito | Consulta que acha | Teste |
|---|---|---|---|
| A1 | 2 h sem aquisição em 14/07 | `09-buracos-de-aquisicao` | `test_a1_...` |
| A2 | TI-201 travado por 90 min | `08-sensor-travado` | `test_a2_...` |
| A3 | pH com qualidade RUIM por 6 h | `14-qualidade-do-dado` | `test_a3_...` |
| A4 | 20 leituras nulas de nível | `14-qualidade-do-dado` | `test_a4_...` |
| A5 | 2 bateladas acima de 195 °C | `05-excursao-de-temperatura` | `test_a5_...` |
| A6 | 1 batelada abortada | `01-panorama` / `11-oee` | `test_a6_...` |
| A7 | Erro de apontamento de solvente | `04-balanco-de-massa` | `test_a7_...` |
| A8 | Espículas de 9,9 bar com qualidade BOA | `14-qualidade-do-dado` | `test_a8_...` |

O A8 é o mais importante e o mais desconfortável: **o flag de qualidade do
coletor não pega tudo**. Uma espícula de instrumento chega marcada como boa,
entra na média, e gera alarme. Quem confia cegamente no flag de qualidade
acredita que já filtrou.

---

## As 14 consultas, e o que cada uma ensina de SQL

| Arquivo | Pergunta de processo | Recurso de SQL |
|---|---|---|
| `01-panorama` | Como foi o mês? | `COUNT FILTER`, `NULLIF`, divisão segura |
| `02-perfil-de-batelada` | Como foi a curva da batelada B-57? | pivô com `CASE`, reamostragem por bucket |
| `03-rendimento-e-ranking` | Quais bateladas renderam mal? | `RANK`, `LAG`, `NTILE`, moldura `ROWS BETWEEN` |
| `04-balanco-de-massa` | O balanço fecha? | agregação de tabela filha, `HAVING`, tolerância explícita |
| `05-excursao-de-temperatura` | Quanto tempo fora de faixa? | agregação condicional, grau-minuto |
| `06-cep-capacidade` | O processo está sob controle? Cp/Cpk? | CTE encadeada, `CROSS JOIN` de escalar |
| `07-taxa-e-media-movel` | Qual a taxa de aquecimento? | `LAG`/`LEAD`, cláusula `WINDOW`, média móvel |
| `08-sensor-travado` | Algum instrumento congelou? | *gaps and islands* com soma acumulada |
| `09-buracos-de-aquisicao` | Confio nesse dado? | `LEAD` para medir lacuna, cobertura |
| `10-oee-e-pareto` | Onde está o tempo perdido? | acumulado com `SUM() OVER (ORDER BY)`, `SUM() OVER ()` |
| `11-oee` | Qual o OEE? | CTEs independentes com `CROSS JOIN`, `EXISTS` |
| `12-lab-versus-processo` | Temperatura explica a viscosidade? | correlação de Pearson em SQL puro |
| `13-alarmes` | O painel está racional? | `FILTER`, taxa por dia, classificação por duração |
| `14-qualidade-do-dado` | Filtrar por qualidade muda o número? | `COUNT(*)` vs `COUNT(col)`, viés |

---

## Resultados reais desta execução (13/08/2026)

Números obtidos rodando o projeto, não estimados.

```
OEE do R-101 em 30 dias
  horas calendário    720,0
  horas produzindo    478,7   → disponibilidade 66,5 %
  78 bateladas (77 concluídas, 1 abortada)
  desempenho          96,5 %   (ciclo real vs. ciclo teórico de 6 h)
  qualidade           91,0 %   (massa aprovada no lab / massa produzida)
  OEE                 58,4 %
```

```
Excursão de temperatura
  B-2026-0057   pico 199,05 °C   47 min acima de 195 °C   432,7 grau-minuto
  B-2026-0023   pico 197,29 °C   32 min acima de 195 °C   296,6 grau-minuto
```

```
Correlação (n = 77 bateladas)
  r(pico de temperatura, viscosidade)  = +0,5395
  r(pico de temperatura, rendimento)   = −0,7675
```

```
Pareto de paradas do R-101
  SETUP          126,0 h   54,0 %   (acumulado  54,0 %)
  PROGRAMADA      72,0 h   30,8 %   (acumulado  84,8 %)
  FALTA_INSUMO    24,5 h   10,5 %   (acumulado  95,3 %)
  FALHA            8,0 h    3,4 %   (acumulado  98,7 %)
  QUALIDADE        3,0 h    1,3 %   (acumulado 100,0 %)
```

```
Racionalização de alarmes — 12 eventos em 30 dias
  PI-101 ALTO     5 eventos   100 % fugazes (<2 min, não reconhecidos)
  AI-101 BAIXO    4 eventos    75 % fugazes
  TI-101 ALTO     2 eventos   duração média 40 min, ambos reconhecidos
  AI-101 ALTO     1 evento    duração 147 min
```

Leia esta última tabela como um engenheiro de processo leria: **dos 12 eventos
de alarme do mês, apenas 2 eram processo de verdade** — os dois de temperatura,
que são exatamente as duas bateladas com excursão. Os cinco de pressão são as
espículas de instrumento do defeito A8; os de pH são limite mal ajustado,
tocando quando o pH encosta no fim natural da reação; e o alarme de pH ALTO de
147 minutos é o sensor sujo do defeito A3 — um alarme inteiramente causado por
um instrumento defeituoso. Isto é 83 % de alarme espúrio, e num painel real
esse ruído é o que treina o operador a ignorar o painel. É o mecanismo que a
ISA-18.2 e o EEMUA 191 tentam impedir, e é por isso que "racionalização de
alarme" é um projeto de engenharia, não de TI.

Repare também no que a consulta 13 **não** vê: ela conta eventos, não
distúrbios. Se um alarme oscilar 40 vezes em 10 minutos (*chattering*), aqui
ele aparece como poucos eventos, porque o gerador agrupa minutos consecutivos.
Um sistema de análise de alarme real precisa dessa contagem crua — e é a
primeira coisa que se descobre ao fazer o primeiro relatório de verdade.

### Uma honestidade sobre o Cp/Cpk

A consulta 06 devolve Cp ≈ 3,4 e Cpk ≈ 3,2. **Nenhuma planta real tem isso.**
O ruído do termopar simulado é de 0,35 °C e a especificação é de ±5 °C, o que
dá uma capacidade absurda. Numa unidade de verdade, um Cpk de 1,33 já é bom e
1,67 é excelente. O número aqui serve para você ver a fórmula funcionando, não
para calibrar expectativa. Dado sintético é sempre bem-comportado demais — e
saber disso é parte do treinamento.

---

## Desempenho e índices (medido nesta máquina)

```
consulta                                     tempo     plano de execução
--------------------------------------------------------------------------------
tag + intervalo (usa a chave primária)        0,1 ms   SEARCH USING PRIMARY KEY
instante exato (usa ix_leitura_ts)           <0,1 ms   SEARCH USING INDEX ix_leitura_ts
filtro por valor (sem índice)                17,8 ms   SCAN leitura
  ... o mesmo, com índice em valor            0,5 ms   SEARCH USING COVERING INDEX
substr(ts,1,10)='2026-07-10'                  5,0 ms   SEARCH USING PRIMARY KEY (tag_id=?)
  ... reescrito como ts>=... AND ts<...        0,1 ms   SEARCH USING PRIMARY KEY (tag_id=? AND ts>? AND ts<?)
```

As duas últimas linhas são a lição mais lucrativa deste projeto: **função
aplicada na coluna impede o uso do índice**. `substr(ts,1,10) = '2026-07-10'`
força ler todas as 43.080 leituras do tag; `ts >= '2026-07-10' AND ts <
'2026-07-11'` lê 1.440. Cinquenta vezes mais rápido, mesma resposta. O termo
técnico é *sargable* (Search ARGument ABLE). Ver `21-indices-e-desempenho.md`.

Para ver o plano de qualquer consulta do projeto:

```bash
python3 scripts/consultar.py --plano 05
```

---

## Limitações declaradas

- **Dado sintético.** Os sinais vêm de fórmulas com ruído gaussiano, não de
  uma planta. A correlação entre temperatura e viscosidade existe porque foi
  colocada lá. Ver a nota sobre Cp/Cpk acima.
- **SQLite.** Um historiador de verdade não usa SQLite: usa PI System, Aspen
  IP.21, PHD, ou um banco de série temporal (TimescaleDB, InfluxDB). A escolha
  aqui é didática — o SQLite tem zero instalação e o SQL é 95 % o mesmo.
  Ver `18-series-temporais.md` e `23-dialetos.md`.
- **Não testado em Windows nem macOS.** O código só usa biblioteca padrão e
  não deve ter problema, mas não foi executado lá. Declarado, não suposto.
- **Sem escrita concorrente.** O `PRAGMA journal_mode = WAL` está lá e é o
  certo, mas o projeto não exercita dois processos escrevendo ao mesmo tempo.
- **Sem autenticação, sem rede, sem API.** É um projeto de SQL, não de sistema.

---

## Exercícios sobre este projeto

1. Acrescente o tag `FI-103` (vazão de descarga) e reescreva o balanço de massa
   usando a integral da vazão em vez do apontamento. Compare os dois.
2. A consulta 05 conta amostras. Reescreva-a usando `LEAD(ts)` para somar o
   tempo real entre amostras — e explique por que o resultado muda no dia 14/07.
3. Crie um índice que faça a consulta 14 rodar em menos de 50 ms. Meça antes e
   depois com `--plano`.
4. Implemente a regra 2 de Nelson (nove pontos seguidos do mesmo lado da linha
   central) na consulta 06. Dica: *gaps and islands*.
5. Adicione uma tabela `receita` com o setpoint por produto e faça a consulta
   06 usar o setpoint da receita em vez do valor fixo 175–185.
6. Troque o `ts` TEXT por `INTEGER` epoch e meça a diferença de tamanho do
   banco e de tempo das consultas 08 e 09.

---

*Voltar para o [mapa do assunto](../00-MAPA.md).*
