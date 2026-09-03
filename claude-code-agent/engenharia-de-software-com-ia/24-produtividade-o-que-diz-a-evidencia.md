# 24 · Produtividade — o que a evidência realmente diz

**Nível:** avançado · **Escrito em:** 20/08/2026

> Este arquivo existe para você não ser enganado — nem pelo vendedor que promete
> 10×, nem pelo cético que cita um estudo fora de contexto. Vamos ler os dados
> com a metodologia junto.

---

## 1 · Por que "produtividade" é quase impossível de medir em software

Antes dos números, a advertência que os torna legíveis.

| Problema | Por quê |
|---|---|
| **Não há unidade de saída** | Linha de código é medida de custo, não de valor. Mais linhas costuma ser pior |
| **O valor aparece depois** | Um sistema entregue em metade do tempo pode custar o dobro em manutenção. O ciclo é de anos |
| **Efeito de novidade** | Ganho inicial de ferramenta nova frequentemente desaparece em 3–6 meses |
| **Autorrelato não funciona** | Está medido: as pessoas erram o sinal, não só a magnitude |
| **Seleção** | Quem adota cedo é diferente de quem adota tarde |
| **Confusão com esforço** | "Menos cansativo" é real e valioso, e não é a mesma coisa que "mais rápido" |

Guarde a quarta linha. Ela é o achado mais robusto de toda a literatura desta
área.

---

## 2 · METR: o estudo que quebrou a narrativa

### O que foi feito (julho de 2025)

Ensaio **randomizado controlado**. 16 desenvolvedores experientes de código
aberto, 246 tarefas reais, em repositórios **deles próprios**, com em média
**5 anos** de familiaridade com o projeto. Cada tarefa sorteada para permitir ou
proibir IA. Ferramentas: majoritariamente Cursor Pro com Claude 3.5/3.7 Sonnet.

### O resultado

> **19% mais lentos** com IA (intervalo de confiança: +2% a +39%).
> E os mesmos desenvolvedores estimaram, depois, que a IA os deixara
> **20% mais rápidos**.

### Por que isso importa mais que o número

O número em si é de "início de 2025" — a própria METR o rotula como **histórico**
e diz que não reflete necessariamente as ferramentas ou fluxos atuais. Não cite
"19%" como se fosse o estado de hoje; quem faz isso está fazendo o mesmo tipo de
erro que critica.

**O achado que não envelhece é a discrepância de 39 pontos entre percepção e
medição.** Isso é sobre cognição humana, não sobre modelos. Você não sabe se
está mais rápido. Nem eu.

### As limitações reais do estudo

Honestidade nos dois sentidos:

- 16 pessoas é pouco.
- Código aberto maduro, com padrões altos e contexto profundo — o cenário **menos
  favorável** à IA. Não generaliza para código novo ou base desconhecida.
- Ferramentas do início de 2025.
- Familiaridade média de 5 anos com o projeto: é justamente onde a IA agrega
  menos.

### A continuação, e a lição metodológica (fevereiro de 2026)

A METR publicou uma atualização importante. No estudo do fim de 2025 (57
desenvolvedores, 143 repositórios, 800+ tarefas):

| Grupo | Aceleração estimada | Intervalo |
|---|---|---|
| Desenvolvedores originais | **−18%** | −38% a +9% |
| Recém-recrutados | **−4%** | −15% a +9% |

Mas a própria METR classificou isso como **evidência muito fraca**, e mudou o
desenho do experimento. O motivo é o mais interessante de toda a história:

> **30% a 50% dos participantes disseram que estavam deixando de submeter
> tarefas porque não queriam fazê-las sem IA.**

Ou seja: as tarefas em que a IA mais ajuda **saíram sistematicamente da
amostra**. É viés de seleção que se instala sozinho, e cresce conforme a adoção
cresce.

**A lição que fica:** medir o efeito da IA em ensaio randomizado está ficando
**metodologicamente mais difícil** justamente porque a adoção virou norma. Isso
significa que a qualidade da evidência disponível vai piorar, não melhorar — e
que você deve depender menos de estudo publicado e mais de medição no seu
próprio contexto.

---

## 3 · DORA: a IA como amplificadora

Relatório *State of AI-assisted Software Development* (2025): ~5.000
profissionais, 100+ horas de dados qualitativos.

| Achado | Número |
|---|---|
| Adoção | **90%** (+14 pontos em um ano) |
| Efeito na vazão de entrega | **Positivo** — reversão do achado do ano anterior |
| Conclusão central | A IA é **amplificadora** |

> Ela **magnifica as forças de organizações de alto desempenho e as disfunções
> das que já vão mal.**

O relatório traz o *AI Capabilities Model*, com sete práticas fundacionais que
amplificam o efeito positivo. O acompanhamento de 2026 sobre ROI reforça: o
maior retorno vem do **sistema organizacional** — qualidade da plataforma
interna, clareza dos fluxos, alinhamento dos times — não da ferramenta.

**Como conciliar com a METR:** não há contradição. A METR mediu **indivíduos
experientes em código maduro**; o DORA mede **organizações**. As duas coisas
podem ser verdadeiras: o dev sênior no repositório que ele domina não ganha
tempo, e a organização entrega mais porque o gargalo dela estava em outro lugar.

---

## 4 · O gargalo se moveu: os dados de 2026

**LinearB**, *2026 Software Engineering Benchmarks Report* — 8,1 milhões de PRs,
4.800 equipes, 42 países:

| Métrica | Valor |
|---|---|
| PRs fundidos por equipes com adoção intensa | **+98%** |
| Tempo de revisão | **+91%** |
| Ganho líquido de produtividade organizacional | **~10%** |
| Espera até a primeira revisão (PR de agente) | **5,3×** (1.055 vs. 201 min) |
| Tamanho do PR no p75 | **2,6×** (408 vs. 157 linhas) |
| Código de IA aprovado sem modificação | **32,7%** (humano: 84,4%) |

**CircleCI** (2026): vazão de *feature branch* **+59%** ano a ano, enquanto a
vazão da `main` da equipe mediana **caiu**.

Leia as duas últimas linhas juntas. Elas dizem a mesma coisa por caminhos
diferentes:

> **Dobrou-se a produção e obteve-se ~10% de ganho líquido.** O resto virou
> estoque na fila de revisão.

Isso é teoria das restrições de manual: otimizar uma etapa que não é o gargalo
aumenta o inventário, não a vazão.

---

## 5 · Qualidade estrutural: GitClear

623 milhões de alterações analisadas, 2023–2026:

| Indicador | 2022 | 2023 | 2026 |
|---|---|---|---|
| Duplicação de blocos / milhão de linhas alteradas | — | 40,3 | **73,0** (+81%) |
| Código movido (refatoração) | 21% | 13% | **3,8%** |
| Copiar-e-colar | 9,4% | — | **15,7%** |

Antes da IA, refatorar era preferido a duplicar em cerca de 2 para 1. Hoje a
preferência inverteu com folga.

### A ressalva metodológica honesta

GitClear mede **estrutura**, não **qualidade**. Duplicação não é sempre ruim:
duplicação deliberada é às vezes melhor que abstração prematura (o argumento de
Sandi Metz: "duplicação é mais barata que a abstração errada").

**Mas 81% de aumento não é decisão deliberada.** É deriva. E o mecanismo é claro
e explicado no [19-arquitetura-para-maquina](19-arquitetura-para-maquina.md): o
agente não conhece o sistema todo, duplicar é local e sempre funciona.

---

## 6 · Confiança: Stack Overflow

Pesquisa de 2025, publicada e analisada em fevereiro de 2026:

| Métrica | Valor | Variação |
|---|---|---|
| Usam ou planejam usar IA | **84%** | de ~70% em 2023 |
| **Confiam** na saída | **29%** | **−11 pontos** em um ano |

E o motivo nº 1 para ainda procurar um humano: **"quando eu não confio na
resposta da IA"** (75%).

**Isso não é contradição.** É a assinatura de uma ferramenta que é útil o
bastante para você não largar e errada o bastante para você não relaxar. É
exatamente o perfil descrito no [10-fundamentos](10-fundamentos.md).

---

## 7 · Como ler qualquer estudo desta área

Sete perguntas. Aplique a este arquivo também.

| # | Pergunta | Sinal de alarme |
|---|---|---|
| 1 | Quem pagou? | Fornecedor medindo o próprio produto |
| 2 | Mediu ou perguntou? | Autorrelato — a METR mostrou que erra o **sinal** |
| 3 | Qual foi a tarefa? | *Benchmark* fechado ≠ trabalho real |
| 4 | Quem participou? | Sênior em código próprio ≠ júnior em código novo |
| 5 | Mediu qualidade também? | Só velocidade é meia história |
| 6 | Qual é o horizonte? | Ganho de 3 meses pode ser efeito de novidade |
| 7 | Qual é o intervalo de confiança? | "19%" com IC de +2% a +39% é uma faixa larga |

---

## 8 · O que eu concluo — marcado como opinião

Com base em tudo acima, e em observação de campo:

1. **O ganho é real e é menor que a propaganda.** Ordem de 10–30% de vazão
   organizacional em times que já eram bons, não 10×.
2. **O ganho é altamente desigual.** Muito grande em código novo, área
   desconhecida, boilerplate e tarefa mecânica. Perto de zero — ou negativo — em
   código maduro que você domina.
3. **O gargalo se moveu para a revisão**, e a maioria não ajustou a capacidade
   de revisão. Isso é o que come o ganho.
4. **A qualidade estrutural está piorando em média.** E ninguém mede, então
   ninguém corrige.
5. **A variável decisiva não é a ferramenta; é o sistema em volta.** DORA está
   certo, e isso é ao mesmo tempo animador (dá para melhorar) e frustrante
   (não dá para comprar).
6. **Você não sabe se está mais rápido.** Meça, ou aceite que é palpite.

### Como medir no seu contexto

O único dado que vale para você é o seu. Sugestão mínima e barata:

| Meça | Como |
|---|---|
| Vazão da `main` (não de *branch*) | PRs fundidos por semana |
| Tempo até a primeira revisão | Métrica do Git/GitHub |
| Tamanho médio do PR | Idem |
| Reversões e incidentes | Contagem simples |
| Duplicação (tendência) | `jscpd` / SonarQube no CI |
| Custo de API por PR fundido | Painel do provedor ÷ PRs |

E, principalmente: **estabeleça a linha de base antes de mudar qualquer coisa.**
Sem ela, toda avaliação futura vira anedota.

---

## Autoteste

1. Cite quatro razões pelas quais produtividade em software é difícil de medir.
2. O que a METR mediu em 2025, e qual dos dois achados **não** envelhece?
3. Cite duas limitações honestas do estudo da METR.
4. Por que a METR mudou o desenho do experimento em 2026? Qual é a lição
   metodológica?
5. Como conciliar o achado da METR com o do DORA sem que um invalide o outro?
6. Dobrou-se a produção de PRs e o ganho líquido foi ~10%. Para onde foi o resto?
7. Qual é a ressalva metodológica honesta sobre os dados do GitClear?
8. Uso 84%, confiança 29%. Por que isso não é contradição?
9. Cite as sete perguntas para ler um estudo desta área.
10. Cite três coisas que você mediria no seu time e por que a linha de base
    precisa vir antes.

---

**Anterior:** [23-licenca-propriedade-e-lei](23-licenca-propriedade-e-lei.md) ·
**Próximo:** [25-niveis-do-dev-com-ia](25-niveis-do-dev-com-ia.md)
