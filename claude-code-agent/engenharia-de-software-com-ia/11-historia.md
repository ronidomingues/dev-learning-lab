# 11 · História — do autocomplete ao agente

**Nível:** intermediário · **Escrito em:** 20/08/2026

> Por que estudar história aqui: porque quase toda ideia vendida como nova em
> 2026 tem 40 ou 60 anos, e conhecer a versão anterior te diz **por que ela
> falhou** — o que é a informação mais útil disponível sobre se ela vai falhar de
> novo.

---

## Linha do tempo

```
1957  FORTRAN — o primeiro "a máquina escreve o código"
1968  Crise do software (Garmisch) — nasce "engenharia de software"
1976  Programação automática por síntese formal (Manna & Waldinger)
1980s CASE tools — "geração automática a partir de diagrama"
1986  Brooks, "No Silver Bullet" — essencial vs. acidental
1990s UML/MDA — a promessa do "código gerado a partir do modelo"
2001  Manifesto Ágil — reação ao ciclo de especificação pesada
2005  Intellisense/IDE moderna — completar por análise estática
2017  Transformer ("Attention is all you need")
2020  GPT-3 — plausibilidade em larga escala
2021  GitHub Copilot (jun) — completar por LLM na IDE
2022  ChatGPT (nov) — conversa vira interface padrão
2023  Copilot Chat · GPT-4 · a era do copiar-e-colar
2024  Devin (mar) · Cursor · Aider · agentes começam a agir
      out — Claude com uso de computador
2025  fev — Karpathy cunha "vibe coding"
      mai — Codex · Jules · Claude Code (GA)
      ago — AGENTS.md (OpenAI, Google, Cursor, Factory, Sourcegraph)
      jul — METR publica o estudo dos 19% mais lentos
      set — DORA 2025: 90% de adoção; IA como amplificadora
      nov — "vibe coding" é palavra do ano do Collins
      dez — AGENTS.md doado à Agentic AI Foundation (Linux Foundation)
2026  jan — METR Time Horizon 1.1: dobra a cada ~4,3 meses
      fev — Stack Overflow: 84% de uso, 29% de confiança
      2026 — Spec-driven development vira o contramovimento dominante
```

---

## Ato 1 · A promessa recorrente (1957–2000)

### FORTRAN e o primeiro pânico

Em 1957, o FORTRAN prometia que **a máquina escreveria o código de máquina**.
O nome completo era *FORmula TRANslating System*. A reação da época foi
literalmente a de 2026: programadores de assembly disseram que o código gerado
seria ineficiente e que ninguém entenderia o que a máquina produzia.

Estavam certos no curto prazo — o código era mais lento. E irrelevantes no longo
prazo, porque a economia venceu: escrever dez vezes mais rápido pagava a
ineficiência com folga.

**A lição:** toda camada de abstração é recebida com a mesma objeção
("perdemos controle") e vence pela mesma razão (economia), **desde que a camada
seja confiável e determinística**. Guarde a última condição — é ela que separa
o FORTRAN dos LLMs.

### A crise do software e a resposta formal

Na conferência da OTAN em Garmisch (1968), cunhou-se "engenharia de software"
para nomear um problema: projetos atrasavam, estouravam orçamento e não
funcionavam. A resposta acadêmica dos anos 1970 foi a **síntese de programas**:
descrever formalmente o que o programa deve fazer e deixar um provador derivar a
implementação (Manna & Waldinger, 1976).

Funcionou para problemas minúsculos. Não escalou, por dois motivos que
continuam valendo:

1. **A especificação formal completa é do tamanho do programa.** Se você tem que
   escrever tudo com precisão matemática, você já escreveu o programa.
2. **Ninguém sabe o que quer com precisão antes de ver funcionando.**

### CASE e MDA: a lição que ninguém aprendeu

Nos anos 1980 e 1990, ferramentas CASE e depois o MDA (*Model-Driven
Architecture*, OMG, 2001) prometeram: desenhe o modelo, gere o código.

Fracassaram de um jeito específico e instrutivo: **o código gerado precisava ser
editado à mão, e aí o modelo e o código divergiam para sempre.** O problema tem
nome — *round-trip engineering* — e nunca foi resolvido.

> **Guarde este parágrafo.** É a mesma armadilha que o *spec-driven development*
> de 2026 enfrenta, e é a pergunta que você deve fazer a qualquer ferramenta de
> SDD que te venderem: *"quando eu editar o código gerado, o que acontece com a
> especificação?"* Se a resposta for "não edite", é MDA outra vez.

### Brooks, 1986

*No Silver Bullet* separou complexidade **essencial** (a do problema) de
**acidental** (a das ferramentas), e previu que nenhuma tecnologia isolada daria
ganho de uma ordem de grandeza em uma década, porque as ferramentas só atacam a
acidental.

Quarenta anos depois, o argumento continua sendo o melhor instrumento disponível
para avaliar promessa de produtividade. Aplicado à IA: ela ataca a acidental
brutalmente bem, e a essencial — decidir o que construir — permanece intacta.

---

## Ato 2 · A virada estatística (2017–2022)

### 2017 — Transformer

O artigo *Attention Is All You Need* (Vaswani et al., Google) introduziu a
arquitetura que viabilizou treinar modelos de linguagem em escala. Ponto de
inflexão técnico; passou despercebido fora da área por três anos.

### 2020 — GPT-3

Primeiro modelo em que a **plausibilidade** do texto gerado ultrapassou o limiar
da utilidade. Também o primeiro em que o problema central deste curso aparece:
o texto é convincente **independentemente de estar certo**.

### 2021 — GitHub Copilot

Junho de 2021, baseado no Codex (OpenAI, derivado do GPT-3 treinado em código).
A primeira ferramenta de massa. Completava a linha ou a função enquanto você
digitava.

Duas coisas nasceram aí e continuam vivas:

- A discussão de **licença e propriedade** — treinado em código do GitHub,
  incluindo GPL. Processo coletivo em 2022 (ver
  [23-licenca-propriedade-e-lei](23-licenca-propriedade-e-lei.md)).
- O hábito de **aceitar sem ler**, porque a sugestão aparecia em cinza e sumia
  com um `Tab`. A ergonomia inventou o problema antes de o problema existir em
  escala.

### 2022 — ChatGPT

Novembro de 2022. Mudou a interface de "completar" para "conversar". O fluxo de
trabalho de 2023 inteiro foi **copiar do editor, colar no navegador, copiar de
volta** — hoje engraçado, na época revolucionário.

---

## Ato 3 · Os agentes (2024–2026)

### O que precisou existir

Três peças, e nenhuma delas é o modelo:

1. **Uso de ferramentas** (*tool use*): o modelo emite uma chamada estruturada
   e recebe o resultado de volta. Sem isso, ele só fala.
2. **Janela de contexto grande**: de 4 mil tokens (2022) para 1 milhão (2026).
   Sem isso, ele não cabe num repositório.
3. **Confiabilidade em cadeia**: um laço de 50 passos com 95% de acerto por
   passo termina em 8% dos casos. Precisou passar de ~99% por passo para
   agentes serem viáveis.

O terceiro item explica por que agentes "de repente" funcionaram em 2024–2025:
não foi uma ideia nova, foi a confiabilidade por passo cruzando um limiar.

### 2024 — o ano das mãos

- **Março:** Devin, anunciado como "primeiro engenheiro de software de IA". A
  demonstração foi contestada em detalhes; o marketing marcou a categoria.
- **Meio do ano:** Cursor e Aider popularizam o agente que edita o repositório
  de verdade.
- **Outubro:** Claude ganha uso de computador (clicar, digitar, ler tela).

### 2025 — o ano da normalização

- **Fevereiro:** Karpathy cunha *vibe coding* num post curto. O termo descreve
  programar aceitando tudo, "esquecendo que o código existe".
- **Maio:** OpenAI Codex, Google Jules, Claude Code em disponibilidade geral.
- **Julho:** a METR publica o estudo que mediu devs experientes **19% mais
  lentos** com IA, em tarefas dos próprios repositórios, enquanto se achavam 20%
  mais rápidos. O balde de água fria mais útil do período.
- **Agosto:** OpenAI, Google, Cursor, Factory e Sourcegraph publicam o
  **AGENTS.md**, um formato comum de instrução para agentes.
- **Setembro:** DORA 2025 — 90% de adoção; conclusão central: IA é
  **amplificadora**.
- **Novembro:** *vibe coding* é palavra do ano do Collins. Isso importa como
  marcador cultural: o termo saiu da engenharia e virou vocabulário geral.
- **Dezembro:** AGENTS.md é doado à Agentic AI Foundation, sob a Linux
  Foundation. Mais de 60.000 projetos usam o formato; 24 ferramentas o leem.

### 2026 — o ano da correção de curso

Três movimentos simultâneos, e é a leitura de 2026 que importa para quem está
começando agora:

**1. O gargalo migrou publicamente para a revisão.** LinearB mediu PRs 2,6×
maiores, espera 5,3× maior, e revisão 91% mais lenta. CircleCI mediu vazão de
*feature branch* subindo 59% enquanto a vazão da `main` da equipe mediana caía.
A frase que resume: *escrever ficou barato; decidir se é seguro fundir, não.*

**2. A qualidade estrutural entrou nos dados.** GitClear, analisando 623 milhões
de alterações de 2023 a 2026: duplicação de blocos de 40,3 para 73,0 por milhão
de linhas alteradas (+81%); código movido — indicador de refatoração — de 21%
(2022) para 3,8% (2026); copiar-e-colar de 9,4% para 15,7%. Em uma frase: **o
código está sendo duplicado em vez de reaproveitado.**

**3. O contramovimento: *spec-driven development*.** Se o problema é que o
agente deriva da intenção, a resposta é tornar a intenção um artefato de
primeira classe. GitHub Spec Kit, AWS Kiro (que usa notação EARS, vinda de
requisitos aeroespaciais), OpenSpec, BMAD, Tessl. Todo grande fornecedor lançou
seu sabor.

> **Minha opinião, marcada como opinião:** o SDD é a ideia certa e está na terceira
> tentativa histórica (síntese formal nos anos 70, MDA nos anos 90, SDD agora). O
> que muda desta vez é que o gerador tolera especificação **informal** — texto,
> não lógica de primeira ordem. Isso remove o obstáculo que matou as duas
> tentativas anteriores. O obstáculo que **permanece** é o mesmo do MDA: a
> divergência entre especificação e código depois da primeira edição manual.
> Ainda não vi ninguém resolver isso; vi muita gente fingir que resolveu.

---

## O padrão que se repete, em quatro tempos

Cada geração de abstração em software seguiu o mesmo roteiro:

| Fase | FORTRAN (1957) | Compilador otimizador (1970s) | IA (2021–) |
|---|---|---|---|
| **1. Promessa** | "não precisa mais de assembly" | "não precisa otimizar à mão" | "não precisa mais programar" |
| **2. Decepção** | código lento | otimização que quebrava código | 19% mais lento; PR ilegível |
| **3. Acomodação** | usa-se para quase tudo; assembly onde importa | confia-se por padrão; `-O0` para depurar | delega-se o padronizado; verifica-se o resto |
| **4. Novo normal** | ninguém discute | ninguém discute | **estamos aqui, entrando na fase 3** |

**A diferença que importa, e é preciso dizer com clareza:** compilador é
determinístico e verificado. Dado o mesmo entrada, mesma saída, sempre; e há
prova (ou ao menos teste massivo) de que a tradução preserva a semântica.

**LLM não tem nenhuma das duas propriedades.** Por isso a acomodação da fase 3
não pode ser "confiar por padrão" — tem que ser "verificar por padrão". É uma
diferença de natureza, não de grau, e é a razão de este curso existir.

---

## Autoteste

1. Por que a objeção ao FORTRAN em 1957 é a mesma de 2026, e por que ela perdeu?
   Qual condição precisava valer para ela perder?
2. Por que a síntese formal de programas dos anos 1970 não escalou? Dê os dois
   motivos.
3. O que é *round-trip engineering* e por que ele matou o MDA?
4. Qual é a pergunta que você deve fazer a qualquer ferramenta de SDD, e por quê?
5. Explique complexidade essencial vs. acidental. Qual delas a IA ataca?
6. Quais três peças precisaram existir para agentes funcionarem? Por que a
   terceira explica o timing?
7. Faça a conta: 50 passos com 95% de acerto por passo. Qual a chance de o laço
   inteiro dar certo?
8. Cite os três movimentos de 2026 e o que cada um mediu.
9. Qual é a diferença de natureza entre um compilador e um LLM, e que consequência
   ela tem para a "fase de acomodação"?
10. Em que fase do padrão de quatro tempos estamos, e o que caracteriza a fase
    seguinte?

---

**Anterior:** [10-fundamentos](10-fundamentos.md) ·
**Próximo:** [12-o-modelo-por-dentro](12-o-modelo-por-dentro.md)
