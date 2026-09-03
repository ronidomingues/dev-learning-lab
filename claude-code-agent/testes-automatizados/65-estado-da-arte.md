# 65 · Estado da arte — agosto de 2026

`Nível: avançado → pesquisa` · `Pesquisado na web em 13/08/2026`
`Este arquivo envelhece rápido. Reavalie a cada 6 meses.`

---

## 1. O panorama em uma página

| Frente | Situação em 13/08/2026 |
|---|---|
| **Corredores JS** | Vitest 4 consolidado como padrão em projetos com Vite; `node:test` maduro e sem dependência; Jest 30 estável e ainda dominante em base instalada |
| **Corredores Python** | pytest 9 é o padrão absoluto; `unittest` sobrevive só por legado |
| **E2E** | Playwright é a recomendação dominante; Cypress perdeu terreno; Selenium/WebDriver segue como padrão W3C para casos remotos |
| **Geração por IA** | adoção muito alta, maturidade baixa: gera-se muito teste, melhora-se pouco a detecção de risco |
| **Mutação** | saiu do nicho — virou a forma padrão de auditar suítes geradas por IA |
| **Ambientes** | Testcontainers como padrão de banco descartável; `tmpfs` e imagens *alpine* para velocidade |
| **Instabilidade** | continua sendo o problema operacional nº 1, e agora contamina as camadas de análise por IA |
| **Verificação formal** | segue em nicho crítico; a fronteira que se move é a verificação **leve** em linguagens de uso geral |

---

## 2. Geração de testes por modelos de linguagem

### 2.1 O que a pesquisa vem medindo

Uma revisão sistemática publicada na *ACM TOSEM* e um estudo empírico de larga escala
publicado em *Empirical Software Engineering* (2026) — este último avaliando **quatro modelos**
contra o EvoSuite, com da ordem de **216 mil casos de teste gerados** sobre Defects4J, SF110 e
CMD, comparando cinco estratégias de *prompt* (zero-shot, few-shot, chain-of-thought,
tree-of-thought e uma variante guiada) — convergem em três achados:

**a) Cobertura competitiva.** Em vários domínios, modelos superam ferramentas de geração
baseada em busca. Em geração de testes para JavaScript, há relatos de superação do estado da
arte anterior.

**b) Alucinação é o gargalo prático.** Referências a símbolos e APIs inexistentes produzem
falhas de compilação com taxas que, nos piores cenários medidos, chegam à casa dos **80 %**.
A variação entre modelos e estratégias de *prompt* é enorme — o que significa que números
isolados sobre "IA gera testes bons" não dizem nada sem o contexto do experimento.

**c) Manutenibilidade ruim.** Testes gerados apresentam com frequência os cheiros clássicos:
números mágicos, *assertion roulette*, nomes que não descrevem comportamento. Ou seja: cobrem
mais e comunicam menos.

### 2.2 As linhas de ataque de 2026

| Linha | Ideia |
|---|---|
| **execução no laço** | compilar e rodar o teste gerado, devolver o erro ao modelo, iterar |
| **guiado por lógica** | derivar as condições de caminho e pedir teste para cada uma, em vez de mapear código→teste como caixa-preta |
| **consciente da cadeia de chamadas** | dar ao modelo o contexto do grafo de chamadas, não só o método isolado |
| **RAG sobre o repositório** | recuperar testes e utilitários existentes para o modelo imitar as convenções do projeto |
| **multiagente** | um agente gera, outro critica, outro executa e repara |

### 2.3 O que a indústria está relatando

Levantamentos de mercado de 2026 apontam **adoção quase universal com profundidade baixa**:
a maior parte dos times que usa IA a usa para **gerar mais casos de teste**, e não para
melhorar a identificação de risco. Um tema recorrente é a passagem de "autocompletar testes"
para **fluxos agênticos** que priorizam *cobertura de risco* em vez de *maximização de
cobertura*.

> **Leia esses números com cuidado.** As fontes são relatórios de fornecedores de ferramentas
> de teste, com amostragem e método pouco transparentes, e interesse comercial no resultado.
> A direção qualitativa (adoção alta, maturidade baixa) é consistente entre eles; as
> porcentagens específicas não deveriam ser citadas como fato.

### 2.4 O limite que não se move

O **problema do oráculo**. Um modelo infere a intenção a partir do código, dos nomes e dos
comentários. Se o código está errado, ele infere a intenção errada e escreve o teste que
**aprova o bug**.

Isso não é limitação de capacidade do modelo; é limitação de **informação disponível**. A
intenção correta simplesmente não está no artefato. Por isso a combinação que funciona hoje é:

```
   humano escreve a INTENÇÃO (o nome do teste, a propriedade, o caso de fronteira)
                     ↓
   modelo escreve o CORPO, os dados, as variações
                     ↓
   execução + mutação verificam se aquilo tem força
```

**Opinião profissional, declarada como opinião:** em 2026, geração por IA é excelente para
**ampliar** uma suíte que já tem bons casos-âncora, e ruim para **criar** uma suíte do zero
num código que ninguém entende. A parte que ela substitui bem é a datilografia; a parte que
ela não substitui é decidir o que deveria acontecer.

---

## 3. Testar código gerado por IA

O espelho do item anterior, e possivelmente o problema mais importante do campo agora.

Se uma fração crescente do código de produção é gerada por assistentes, o gargalo de
qualidade se desloca para a **verificação**. E há um risco específico: pedir ao mesmo modelo
que escreva o código **e** o teste produz correlação de erro — o teste concorda com o
equívoco do código.

Práticas que estão emergindo como resposta:

1. **oráculo humano obrigatório** — a pessoa escreve as asserções críticas, o modelo o resto;
2. **teste de propriedades** — a lei é escrita por humano e vale para toda entrada;
3. **análise de mutação sobre a suíte gerada** — a forma padrão de responder "esses testes
   pegam alguma coisa?";
4. **diversidade de origem** — quem gera o código não gera o teste.

Ferramentas de mutação (Stryker, PIT, `cargo-mutants`, mutmut) passaram a ser citadas como
**salvaguarda sistemática** exatamente nesse contexto. É um caso raro de técnica de 1978
ganhando relevância nova.

---

## 4. JavaScript: o que mudou

### 4.1 A pilha padrão de 2026

Para uma aplicação web nova, a combinação que aparece como recomendação consistente é:

```
  Vitest        → unitário e integração
  Testing Library → interação com componentes
  Playwright    → ponta a ponta
  TypeScript    → a camada estática, que elimina uma classe inteira de teste
```

Para bibliotecas e serviços Node, `node:test` sozinho basta.

### 4.2 Vitest browser mode

O Vitest passou a rodar os testes **dentro de um navegador real**, usando o Playwright (ou
WebDriver) apenas como *provedor* de navegador, não como corredor. O ganho: testar componente
com o motor de layout de verdade, sem a aproximação do jsdom — que sempre divergiu em
`getBoundingClientRect`, foco, rolagem e várias APIs.

Isso apaga parcialmente a fronteira "unitário × E2E" no front-end: passa a existir um teste de
componente rápido **e** fiel.

### 4.3 Playwright

Duas mudanças relevantes: o modo *headless* do Chromium passou a usar o **Chrome real** em
vez do binário dedicado de headless — o que reduz a classe de bug "só acontece em headless" —
e a paralelização por *workers* continua sendo o principal argumento contra o Cypress.

### 4.4 A regra de proporção que circula

Aparece com frequência em material de 2026 a heurística **70 / 20 / 10** (unitário /
integração / E2E). É uma regra de bolso razoável para aplicação web — **e não é uma lei**.
Ver [12-tipos-e-piramide.md](12-tipos-e-piramide.md) §6.3: a proporção deve emergir do risco
e da arquitetura, não de uma tabela.

---

## 5. Python: o que mudou

- **pytest 9** (nov/2025) removeu o resíduo do estilo `nose`, o namespace `pytest.collect` e
  os testes baseados em `yield`. Ganhou *subtests* nativos, configuração TOML nativa e um
  modo estrito. A série 9.x segue em manutenção — a versão usada neste curso é a **9.1.1**.
- **`uv`** consolidou-se como gerenciador de ambiente e pacotes; para projeto novo, é a
  escolha melhor que `pip` + `venv`, sobretudo pelo lockfile universal e pela velocidade.
- **Free-threaded Python** (sem GIL) é oficialmente suportado a partir do 3.14. Consequência
  para testes: código concorrente que "funcionava por causa do GIL" passa a ter corridas
  reais. Testar concorrência deixou de ser exótico em Python.
- **Hypothesis** continua a referência de teste por propriedades, com `RuleBasedStateMachine`
  para máquinas de estado.

---

## 6. Instabilidade (*flakiness*): o problema que não melhorou

É o tema mais recorrente nos levantamentos de 2026, e a razão é estrutural: as causas
apontadas são as mesmas de dez anos atrás — seletores frágeis, temporização, instabilidade de
ambiente, dependência de dados e sincronização.

**A novidade de 2026 é o efeito de segunda ordem:** quando se acopla uma camada de análise
automática (priorização de testes por IA, detecção de causa raiz) a uma suíte com alta taxa de
falso vermelho, o ruído contamina o modelo. Ou seja: **instabilidade agora custa duas vezes.**

Linhas de tratamento em uso:

| Técnica | O que faz |
|---|---|
| detecção automática | reexecuta e classifica; alimenta um painel de instabilidade |
| quarentena com prazo | tira do portão, cria a tarefa, com data |
| seletores semânticos | papel de acessibilidade e texto, em vez de CSS/XPath |
| auto-espera | condição verificável em vez de `sleep` |
| isolamento de dados | cada teste cria o que usa |

Nada disso é novo. O que mudou é que a instabilidade deixou de ser tratada como fatalidade e
passou a ter métrica e dono.

---

## 7. Ambientes de teste

- **Testcontainers** é o padrão de fato para banco, fila e serviços auxiliares descartáveis,
  com bibliotecas maduras em Python, JS/TS, Java, Go e .NET.
- **`node:sqlite`** e SQLite em memória cobrem bem os casos em que o dialeto não importa —
  e são uma armadilha quando importa.
- **`tmpfs`** para o diretório de dados do banco em CI é um ganho de desempenho subutilizado.
- **Dev containers / Codespaces** tornaram viável ter o mesmo ambiente na máquina e no CI, o
  que ataca a causa raiz de metade dos testes instáveis.

---

## 8. Perguntas em aberto

1. **Oráculo automático.** Continua sem solução geral, e é o gargalo de tudo — geração
   automática, teste de IA, teste de sistemas científicos.
2. **Testar sistemas não determinísticos.** Como fazer regressão de um sistema cuja saída é
   uma distribuição? Teste metamórfico e limites estatísticos são o estado da arte, e são
   insuficientes.
3. **Mutação viável em escala.** O custo continua proporcional a (mutantes × tempo da suíte).
   Mutação incremental sobre o diff é o caminho mais promissor.
4. **Especificação executável que humanos escrevam.** Propriedades funcionam e são pouco
   adotadas — provavelmente um problema de ergonomia, não de poder.
5. **Medir a eficácia real de uma suíte.** Sem oráculo, todas as métricas são proxies. Ligar
   "suíte" a "defeitos que escaparam" continua sendo mais arte que ciência.
6. **Testar agentes de IA.** Um sistema que chama modelos, usa ferramentas e mantém estado
   entre passos tem espaço de comportamento gigantesco e não determinístico. As práticas ainda
   estão sendo inventadas.

---

## 9. O que **não** mudou desde 2002

Vale terminar por aqui, como antídoto ao hype:

- Arrange–Act–Assert continua sendo a anatomia de todo teste.
- A definição de unidade continua em disputa, pelos mesmos motivos.
- Um teste que você nunca viu falhar continua não sendo um teste.
- Suíte lenta continua sendo suíte que ninguém roda.
- O nome do teste continua sendo a parte mais importante dele.
- Código difícil de testar continua sendo, quase sempre, código mal desenhado.
- Cobertura continua não medindo qualidade.

Ferramenta muda a cada três anos. Isto aqui não mudou em vinte e quatro.

---

## Autoteste

1. Quais são os três achados convergentes da pesquisa sobre geração de testes por LLM?
2. Por que números de relatórios de mercado sobre adoção de IA devem ser lidos com cautela?
3. Qual é o limite conceitual da geração automática que nenhum modelo resolve, e por quê?
4. Qual é o risco de pedir ao mesmo modelo o código e o teste?
5. Por que a análise de mutação, de 1978, ganhou relevância nova em 2026?
6. O que o *browser mode* do Vitest muda na fronteira unitário × E2E?
7. Que efeito de segunda ordem a instabilidade passou a ter em 2026?
8. Qual consequência o Python sem GIL traz para testes?
9. Cite três perguntas em aberto do campo.
10. Cite quatro coisas que não mudaram em vinte e quatro anos.

---

## Fontes consultadas (13/08/2026)

- [Enhancing Automated Unit Test Generation with LLMs: A Systematic Literature Review — ACM TOSEM](https://dl.acm.org/doi/10.1145/3802827)
- [Prompt engineering in LLMs for automated unit test generation: A large-scale study — Empirical Software Engineering (2026)](https://link.springer.com/article/10.1007/s10664-026-10840-4)
- [A Logic-Guided and Explainable Approach to LLM-Based Unit Test Generation](https://doi.org/10.3390/app16052542)
- [Call-Chain-Aware LLM-Based Test Generation for Java Projects (arXiv)](https://arxiv.org/pdf/2604.22046)
- [Enhancing LLMs with RAG for Software Testing and Inspection Automation (arXiv)](https://arxiv.org/pdf/2604.15270)
- [State of QA Automation 2026 — Quash](https://quashbugs.com/blog/state-of-qa-automation-2026-report) *(relatório de fornecedor)*
- [Top Software Testing Trends 2026: Data vs Hype — TestDino](https://testdino.com/blog/software-testing-trends) *(relatório de fornecedor)*
- [Vitest — Browser Mode](https://vitest.dev/guide/browser/) · [Configuring Playwright](https://vitest.dev/config/browser/playwright)
- [Vitest + Jest + Playwright: Full Testing Stack 2026 — PkgPulse](https://www.pkgpulse.com/guides/vitest-jest-playwright-complete-testing-stack-2026)
- [pytest 9.0.0 — LWN](https://lwn.net/Articles/1045923/) · [Changelog do pytest](https://docs.pytest.org/en/stable/changelog.html)
- [Node.js — Test runner](https://nodejs.org/api/test.html)
