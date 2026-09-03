# Portas Lógicas — Mapa do Assunto

**Nível geral:** do leigo absoluto à pesquisa em complexidade de circuitos
**Data de produção:** 14/08/2026
**Pergunta que originou este material:** *"Quantas portas lógicas possui o Computador e para que elas servem?"*

---

## A resposta curta (a longa está no [`50`](50-quantas-portas-tem-um-computador.md))

A pergunta tem **duas respostas**, e confundi-las é o erro mais comum de quem começa:

| Se você pergunta… | A resposta é… |
|---|---|
| **Quantos *tipos* de porta existem?** | **7 tipos clássicos** (NOT, AND, OR, NAND, NOR, XOR, XNOR) — mais o *buffer*, que alguns contam, dando 8. E, formalmente, **16 funções booleanas de duas entradas** são possíveis; as 7 clássicas são as que ganharam nome e símbolo. |
| **Quantas *unidades* de porta um computador tem?** | **Bilhões.** Um notebook de 2026 com um SoC de ~28 bilhões de transistores tem, por estimativa, **algo entre 2,5 e 5 bilhões de portas lógicas equivalentes** (estimativa central ~3,4 bi) — o resto dos transistores é memória, não porta. Um Intel 4004 de 1971 tinha ~2.250 transistores, na ordem de **algumas centenas de portas**. |

E **para que servem**: com apenas essas portas se constrói *tudo* — somar, comparar, decidir, escolher um caminho, endereçar memória, **lembrar** um bit, contar o tempo, detectar erro. Uma porta sozinha decide uma coisa banal. Um bilhão delas, ligadas na ordem certa, é um computador.

> Toda a construção — do transistor à CPU — está detalhada nos arquivos abaixo, e o
> **projeto-modelo constrói um computador de 4 bits usando *apenas* portas NAND**,
> contando cada porta gasta.

---

## O que você saberá ao final

1. O que é uma porta lógica, no nível de intuição de criança e no nível de física do transistor.
2. Por que **NAND sozinha basta** para construir qualquer computador — e a prova disso.
3. Como se sobe de um transistor a um somador, de um somador a uma ULA, de uma ULA a uma CPU.
4. Como um circuito **lembra** algo (o pulo do gato: realimentação).
5. Como se **conta** portas de verdade na indústria (gate equivalent, standard cell, área).
6. Números reais, com fonte e data, de 1971 a 2026.
7. Onde estão os limites teóricos: o que **nenhum** circuito pequeno consegue calcular, e por quê.
8. O estado da arte de agosto de 2026: nanosheet/GAA, backside power, CFET, portas quânticas.

---

## Roteiro de leitura

### Você tem 20 minutos e quer só entender
`01` → `50`

### Você quer *fazer*, não só ler
`01` → `02` → `03` → `04` → `07-projeto-modelo/` → `06` → `70`

### Você quer o curso inteiro, na ordem
Do `01` ao `95`, em ordem numérica. É contínuo e sem salto.

### Você é da área e quer só o que talvez não saiba
`50` → `60` → `65` → `75`

---

## Índice dos arquivos

### Bloco A · Porta de entrada (01–09)

| Arquivo | Nível | O que traz |
|---|---|---|
| [`01-introducao-leigo.md`](01-introducao-leigo.md) | iniciante | O que é uma porta lógica sem uma única palavra técnica. Interruptores, água, e a pergunta "quantas?" respondida em linguagem comum. |
| [`02-pre-requisitos.md`](02-pre-requisitos.md) | iniciante | O que saber antes (quase nada), o que instalar, e quanto tempo cada nível leva de verdade. |
| [`03-instalacao.md`](03-instalacao.md) | iniciante | Manual de campo: Logisim-evolution 4.1.0, Digital 0.31, Icarus Verilog 13.0, GTKWave, Python, Java 21 — em Linux, macOS e Windows. Com a alternativa **sem instalar nada**. |
| [`04-como-comecar.md`](04-como-comecar.md) | iniciante | Do ambiente pronto a um somador funcionando na tela, em 15 minutos. |
| [`05-manual-de-uso.md`](05-manual-de-uso.md) | referência | Consultável: as 7 portas, as 16 funções, identidades booleanas, símbolos ANSI e IEC, série 7400, operadores Verilog, atalhos do Logisim. |
| [`06-exemplos.md`](06-exemplos.md) | iniciante→avançado | 12 circuitos completos, do inversor ao contador com display de 7 segmentos. |
| [`07-projeto-modelo/`](07-projeto-modelo/README.md) | intermediário | **Um computador de 4 bits construído do zero em Python, só com NAND**, com contagem automática de portas e 76 testes. Roda. |

### Bloco B · Núcleo (10–69)

| Arquivo | Nível | O que traz |
|---|---|---|
| [`10-fundamentos.md`](10-fundamentos.md) | iniciante→intermediário | Álgebra booleana, tabelas-verdade, as 16 funções de 2 variáveis, completude funcional, formas normais. |
| [`11-historia.md`](11-historia.md) | iniciante | Boole (1847) → Shannon (1937) → relé → válvula → transistor → CI → VLSI. Por que cada troca aconteceu. |
| [`12-do-transistor-a-porta.md`](12-do-transistor-a-porta.md) | intermediário | Como um transistor MOS vira uma porta CMOS, por que NAND custa 4 transistores e XOR custa 12, atraso, fan-out, margem de ruído, famílias lógicas. |
| [`20-circuitos-combinacionais.md`](20-circuitos-combinacionais.md) | intermediário | Somador, subtrator, multiplexador, decodificador, comparador, ULA, barrel shifter, paridade. Minimização por Karnaugh e Quine–McCluskey. |
| [`30-circuitos-sequenciais.md`](30-circuitos-sequenciais.md) | intermediário→avançado | Realimentação, latch SR, flip-flop D, registrador, contador, memória SRAM, setup/hold, metaestabilidade, máquinas de estado. |
| [`40-da-porta-ao-computador.md`](40-da-porta-ao-computador.md) | avançado | Como as peças viram uma CPU RISC-V de ciclo único: caminho de dados, controle, pipeline, e onde exatamente as portas são gastas. |
| [`50-quantas-portas-tem-um-computador.md`](50-quantas-portas-tem-um-computador.md) | avançado | **A resposta longa.** Metodologia de contagem, gate equivalent, transistor vs. porta, tabela histórica de 1971 a 2026, e por que a maior parte dos transistores não é porta nenhuma. |
| [`60-teoria-avancada.md`](60-teoria-avancada.md) | pesquisa | Complexidade de circuitos: argumento de contagem de Shannon, classes AC⁰/NC¹/P-poly, limites inferiores, circuitos monótonos, profundidade × tamanho, lógica reversível e o limite de Landauer. |
| [`65-estado-da-arte.md`](65-estado-da-arte.md) | pesquisa | Agosto de 2026: N2/18A em produção, nanosheet, backside power, CFET no horizonte, EDA com IA, silício aberto, portas quânticas, computação em memória. |

### Bloco C · Prática e erros (70–79)

| Arquivo | Nível | O que traz |
|---|---|---|
| [`70-pratica.md`](70-pratica.md) | todos | 12 laboratórios progressivos, do inversor à CPU, com critério de "deu certo". |
| [`75-armadilhas.md`](75-armadilhas.md) | todos | 20 erros clássicos e 8 mitos — incluindo os que professores repetem. |

### Bloco D · Economia e ecossistema (80–89)

| Arquivo | Nível | O que traz |
|---|---|---|
| [`80-custos-e-licencas.md`](80-custos-e-licencas.md) | todos | Preços com data (14/08/2026): software livre, FPGAs, kits de CI 7400, EDA proprietária, e quanto custa fabricar silício de verdade. |
| [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md) | todos | Cursos gratuitos em PT, EN e FR, pesquisados na web, com link e avaliação franca. Certificações que valem e as que não valem. |

### Bloco E · Fontes (90–99)

| Arquivo | O que traz |
|---|---|
| [`90-bibliografia.md`](90-bibliografia.md) | Livros com edição real, nível, e o que é legalmente gratuito. |
| [`95-referencias.md`](95-referencias.md) | Papers seminais, specs, datasheets, ferramentas, pessoas a seguir. |
| [`GLOSSARIO.md`](GLOSSARIO.md) | ~140 termos definidos, mais uma tabela das distinções que mais confundem. |

---

## As 12 camadas de profundidade — onde cada uma está

| # | Camada | Onde |
|---|---|---|
| 1 | Intuição para leigo | `01` |
| 2 | Definição informal | `01`, `10` |
| 3 | Por que existe | `11` |
| 4 | Ambiente e primeiro uso | `03`, `04` |
| 5 | Fundamentos formais | `10` |
| 6 | Mecânica interna | `12`, `20`, `30` |
| 7 | Implementação prática | `06`, `07-projeto-modelo/` |
| 8 | Casos de uso reais | `40`, `50` |
| 9 | Trade-offs e alternativas | `12`, `20`, `75` |
| 10 | Economia do assunto | `80` |
| 11 | Profundidade de pesquisa | `60` |
| 12 | Estado da arte | `65` |

---

## Status dos blocos

| Bloco | Status | Observação |
|---|---|---|
| A · Porta de entrada | ✅ | Instalação verificada em Ubuntu 22.04.5 em 14/08/2026; projeto-modelo executado, 76 testes passando. |
| B · Núcleo | ✅ | 9 arquivos, do fundamento à fronteira de pesquisa. |
| C · Prática e erros | ✅ | 12 laboratórios, 20 armadilhas, 8 mitos. |
| D · Economia e ecossistema | ✅ | Preços e cursos pesquisados na web em 14/08/2026. |
| E · Fontes | ✅ | Referências verificadas; nada inventado. |

**Pendente:** nada de estrutura. Reavaliar `65-estado-da-arte.md` e `80-custos-e-licencas.md`
a cada ~12 meses — nós de fabricação e preços de placa mudam rápido.

---

## Autoteste do mapa

1. Por que "quantas portas lógicas um computador tem" é uma pergunta com duas respostas legítimas?
2. Quantos tipos clássicos de porta existem, e quantas funções booleanas de duas entradas são teoricamente possíveis?
3. Se um chip tem 28 bilhões de transistores, por que **não** se pode dividir por 4 e dizer que ele tem 7 bilhões de portas?
4. Qual arquivo você leria se quisesse apenas construir algo hoje, sem teoria?
5. Em qual arquivo está a prova de que só a porta NAND basta?

*(Respostas: 1 — tipos vs. unidades, `50`; 2 — 7 clássicas e 16 possíveis, `10`; 3 — porque a maior parte é memória SRAM, não lógica, `50`; 4 — `03` → `04` → `07-projeto-modelo/`; 5 — `10`, seção de completude funcional.)*
