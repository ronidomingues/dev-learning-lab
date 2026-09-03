# 18 · Visualização

**Nível:** intermediário
**Data:** 14/08/2026

Este capítulo trata do último quilômetro: transformar números corretos em decisões. É a
parte que todo mundo acha que é o assunto principal — e é a que menos funciona quando as
anteriores foram puladas.

---

## 1. A premissa

> Um gráfico é uma **codificação**: valores numéricos viram propriedades visuais
> (posição, comprimento, ângulo, área, cor). O leitor faz a decodificação de volta.
> **A qualidade do gráfico é a fidelidade dessa ida e volta.**

Isso não é opinião estética. É mensurável, e foi medido.

---

## 2. O que a pesquisa diz

Em 1984, William Cleveland e Robert McGill publicaram no *Journal of the American
Statistical Association* um experimento que ordenou as codificações visuais por **precisão
de decodificação**. É um dos resultados mais replicados da área:

```
MAIS PRECISO
   1. Posição numa escala comum          (barras, colunas, pontos alinhados)
   2. Posição em escalas não alinhadas   (small multiples)
   3. Comprimento                        (barras sem eixo comum)
   4. Ângulo / inclinação                (pizza, linhas)
   5. Área                               (bolhas, treemap)
   6. Volume                             (gráficos 3D)
   7. Cor / saturação / densidade        (mapa de calor)
MENOS PRECISO
```

**Três consequências práticas imediatas:**

1. **Barras e colunas são a escolha padrão.** Não porque são chatas — porque são precisas.
   Quando em dúvida, barra.
2. **Pizza é ruim para comparação** — usa ângulo e área, posições 4 e 5. Com 3 fatias ou
   menos, tudo bem. Com 8, é ilegível.
3. **3D é sempre pior.** Adiciona volume (posição 6) e distorção de perspectiva, sem
   acrescentar informação. Não existe caso de uso legítimo para gráfico 3D em BI.

**A ressalva honesta:** o experimento mede *precisão de leitura de valores*. Alguns
gráficos existem para outra coisa — mostrar padrão, chamar atenção, dar contexto
geográfico. Um mapa de calor é impreciso e insubstituível para ver onde há concentração.
**Precisão não é o único critério; é o critério padrão.**

---

## 3. Escolhendo o gráfico pela pergunta

Não escolha pelo gráfico que você gosta. Escolha pela pergunta que ele responde.

| A pergunta é… | Use | Evite |
|---|---|---|
| Quanto é X? (um número) | Cartão, com contexto | Cartão sozinho, sem comparação |
| Como X se compara entre categorias? | **Barras** (categorias longas) ou **colunas** | Pizza, rosca, radar |
| Como X evoluiu no tempo? | **Linhas** (contínuo) ou colunas (períodos discretos) | Barras horizontais |
| Qual a composição de X? | Barras empilhadas 100%, ou **barras simples** | Pizza com > 3 fatias |
| Como a composição evoluiu? | Área empilhada (até 4 séries) | Área com 10 séries |
| X e Y se relacionam? | **Dispersão** | Combo de duas escalas |
| O que explica a variação de X? | **Cascata** (*waterfall*) | Duas colunas lado a lado |
| Onde X está concentrado geograficamente? | Mapa coroplético / bolhas | Mapa quando geografia não importa |
| Quais os valores exatos? | **Matriz** ou tabela | Gráfico com rótulos em tudo |
| Como X se distribui? | Histograma, boxplot (visual customizado) | Média sozinha |
| X bateu a meta? | Barra com linha de referência, ou KPI | Medidor (*gauge*) — ocupa muito, informa pouco |
| Quais os principais drivers? | Principais Influenciadores, árvore de decomposição | — |

### A matriz é subestimada

**Opinião do autor:** a matriz (tabela dinâmica) é o visual mais útil e menos valorizado do
Power BI. Executivos que dizem gostar de dashboards frequentemente exportam tudo para o
Excel — porque querem **os números**, não a representação deles.

Uma matriz bem-feita, com formatação condicional discreta, barras de dados e hierarquia
expansível, resolve mais perguntas que três gráficos. Não tenha vergonha dela.

---

## 4. Princípios de projeto

### 4.1 Razão dado-tinta (Tufte, 1983)

> Maximize a proporção de tinta que representa **dados**. Remova o resto.

Remova, nesta ordem: fundos coloridos, bordas duplas, grades pesadas, sombras, gradientes,
ícones decorativos, títulos redundantes, eixos com casas decimais desnecessárias, legendas
quando o rótulo direto resolve.

**Antes e depois, em um visual típico:**

```
ANTES                                DEPOIS
┌═══════════════════════════┐       Faturamento por categoria · 2026
║ ▓▓▓ FATURAMENTO ▓▓▓       ║
║ ┌───────────────────────┐ ║       Tintas    ████████████████  107,2 M
║ │▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│ ║       Resinas   ███               21,2 M
║ │  ░░░░ grade ░░░░      │ ║       Solventes ██                15,3 M
║ │  ▓▓▓▓ barras 3D ▓▓▓▓  │ ║       Vernizes  █                 10,2 M
║ │  com sombra e         │ ║       Aditivos  █                  7,4 M
║ │  gradiente            │ ║
║ └───────────────────────┘ ║       (sem grade, sem eixo, rótulo direto)
║ ▓ legenda ▓ ▓ legenda ▓   ║
╚═══════════════════════════╝
```

### 4.2 Contexto obrigatório

Um número sozinho não informa. Todo KPI precisa de pelo menos um destes:

- **comparação temporal** (vs. mês anterior, vs. ano anterior);
- **comparação com meta**;
- **comparação com par** (vs. média da equipe);
- **tendência** (sparkline).

O novo visual de cartão do Power BI suporta múltiplos valores e formatação condicional
mais rica — use-o para colocar o valor e a variação juntos.

### 4.3 Ordenação

Ordene por **valor**, não alfabeticamente. Exceções: ordem natural (meses, faixas
etárias, etapas de processo) e quando o usuário procura um item específico por nome.

### 4.4 Cor com significado

**Regras práticas:**

1. **Cor categórica** (cores distintas) — só para poucas categorias, e mantenha a **mesma
   cor para a mesma categoria em todo o relatório**. Cor inconsistente entre páginas é o
   erro de design mais comum e o mais confuso.
2. **Cor sequencial** (uma matiz, várias intensidades) — para grandezas ordenadas.
3. **Cor divergente** (duas matizes com neutro no meio) — para desvios em relação a um
   ponto de referência (meta, zero, média).
4. **Cinza é uma cor.** Use cinza para o que é contexto e cor para o que é a mensagem. Um
   gráfico onde tudo é colorido é um gráfico onde nada se destaca.
5. **Não use cor como único canal.** Cerca de 8% dos homens e 0,5% das mulheres têm alguma
   deficiência de visão de cores; vermelho/verde é a combinação mais problemática.
   Acrescente forma, rótulo, ícone ou posição.

**Verificação prática:** imprima o relatório em preto e branco. Se a mensagem some, a cor
está fazendo trabalho demais.

### 4.5 Temas

Defina um **tema JSON** com a paleta, fontes e defaults, e aplique em todos os relatórios
da empresa. Exibição → Temas → Personalizar tema atual → Salvar tema atual.

A partir da atualização de julho/2026, os **Modern Visual Defaults** trazem um
"Personalizar tema atual" no painel Formatar, permitindo ajustar padrões de visuais para o
relatório inteiro (fundo, borda, ícones de cabeçalho, tooltips, sombra), mudar tamanho de
página e papel de parede de todas as páginas de uma vez, e **exportar o tema** para outros
relatórios ou para os temas organizacionais.

**Isso muda o fluxo de trabalho:** antes, padronizar exigia editar JSON à mão. Agora dá
para ajustar na interface e exportar.

---

## 5. Layout

### 5.1 A leitura em Z e o canto nobre

Em culturas de leitura da esquerda para a direita, o olho varre em Z: canto superior
esquerdo primeiro. Ponha ali o que importa mais.

```
┌──────────────────────────────────────────────────────┐
│  Título do relatório          [filtros globais]      │
├──────────────────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐         │
│  │  KPI 1 │ │  KPI 2 │ │  KPI 3 │ │  KPI 4 │  ← o Z começa aqui
│  └────────┘ └────────┘ └────────┘ └────────┘         │
├──────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐ ┌───────────────────┐  │
│  │  Gráfico principal       │ │  Gráfico apoio    │  │
│  │  (a mensagem central)    │ │                   │  │
│  └──────────────────────────┘ └───────────────────┘  │
├──────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐    │
│  │  Detalhe (matriz)                            │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### 5.2 Quantos visuais por página?

**Regra empírica: 5 a 8.** Acima disso, o desempenho degrada (cada visual é pelo menos
uma consulta DAX) e a atenção se dispersa.

Se você precisa de mais, use páginas de detalhe com *drillthrough* em vez de amontoar.

### 5.3 Uma página, uma pergunta

Cada página deve responder a **uma** pergunta de negócio, e o título deve dizer qual.

Ruim: "Vendas". Bom: "Onde estamos perdendo margem?".

### 5.4 Layout de celular

Exibição → Layout móvel. Sem ele, o relatório no celular aparece encolhido e ilegível.

Regra: no celular, **3 a 4 visuais empilhados**, os mais importantes, em orientação
retrato. Não tente reproduzir a página do desktop.

---

## 6. Acessibilidade

Não é opcional em setor público, e é boa prática em qualquer lugar.

| Item | Como fazer |
|---|---|
| **Texto alternativo** | Formato → Geral → Texto Alt, em cada visual |
| **Ordem de tabulação** | Painel Seleção → Ordem de tabulação; remova os decorativos |
| **Contraste** | Mínimo 4,5:1 entre texto e fundo (WCAG AA) |
| **Não depender de cor** | Adicione forma, rótulo ou padrão |
| **Modo alto contraste** | O Power BI respeita o do Windows; teste |
| **Leitor de tela** | Teste com Narrador/NVDA ao menos uma vez |
| **Tabela alternativa** | Todo visual tem "Mostrar como tabela" (`Alt+Shift+F11`) |

**Ganho colateral:** relatórios acessíveis costumam ser mais legíveis para todo mundo.
Texto alternativo obriga você a escrever, em uma frase, o que o visual quer dizer — e se
você não consegue, o visual não está dizendo nada.

---

## 7. Desempenho de renderização

| Prática | Ganho |
|---|---|
| Menos visuais por página | **Alto** — cada visual é ao menos uma consulta |
| Evitar visuais que retornam muitas linhas (tabelas com 50 mil linhas) | Alto |
| Evitar visuais customizados pesados | Médio a alto |
| Usar "Pausar visuais" (guia Otimizar) ao editar | Alto (produtividade) |
| Reduzir campos no visual | Médio |
| Evitar segmentações com milhares de itens | Médio |
| Filtrar no nível do relatório em vez de em 8 visuais | Médio |
| Desativar interações desnecessárias entre visuais | Médio |

**A ferramenta:** guia **Otimizar** → **Analisador de Desempenho** → Iniciar gravação →
interagir. Ele mostra, por visual, o tempo de consulta DAX, o tempo de renderização e o
tempo de "outros". E permite **copiar a consulta DAX** para o DAX Studio. Ver
[`22-desempenho.md`](22-desempenho.md).

---

## 8. Visuais customizados — quando e com que cuidado

O AppSource tem centenas de visuais de terceiros. Antes de usar um:

| Pergunta | Por quê |
|---|---|
| É **certificado** pela Microsoft? | Certificado = código revisado e **sem acesso à internet** |
| Quem mantém? | Visual abandonado quebra numa atualização mensal |
| Funciona na exportação para PDF/PowerPoint? | Muitos não |
| Funciona no mobile? | Muitos não |
| Precisa de licença separada? | Vários são pagos por usuário |
| Envia dados para fora? | **Não certificado pode enviar seus dados a um servidor externo** |

A última linha é a mais séria e a menos verificada. Um visual não certificado pode fazer
chamadas de rede. Em ambiente corporativo, **restrinja a visuais certificados** por
configuração de locatário.

**Opinião do autor:** 90% dos usos de visual customizado que vi poderiam ser resolvidos com
visuais nativos e um pouco de criatividade. Os 10% legítimos costumam ser: boxplot,
gráfico de Gantt, gráfico de Sankey e tabelas com recursos especiais.

---

## 9. Os erros de visualização que mais vejo

1. **Eixo Y não começando em zero, num gráfico de barras.** Exagera diferenças
   dramaticamente. Em gráfico de **linhas**, truncar o eixo é aceitável e às vezes
   necessário; em **barras**, é distorção — porque barra codifica comprimento.

2. **Pizza com 12 fatias.** Ninguém consegue ordenar as fatias 5 a 12.

3. **Duplo eixo Y.** Sugere correlação que pode não existir, e a escolha das escalas
   determina a "história". Use com muita parcimônia, ou dois gráficos empilhados
   compartilhando o eixo X.

4. **Cores diferentes para a mesma categoria em páginas diferentes.**

5. **Mapa porque tem "estado" na tabela.** Mapa só quando a **geografia** é a mensagem.
   Se a pergunta é "qual estado vende mais", barras ordenadas respondem melhor.

6. **Rótulos de dados em tudo.** Se você precisa dos números exatos, use uma matriz. Se
   precisa do padrão, use o gráfico. Os dois juntos poluem.

7. **Título genérico.** "Vendas por mês" descreve o eixo. "Vendas caíram 3 meses seguidos
   no Sul" descreve o achado. Use o segundo quando souber a resposta.

8. **Gráfico de 3 valores.** Se são três números, escreva uma frase.

9. **Precisão falsa.** `R$ 167.700.759,11` num cartão executivo. Use `R$ 167,7 M`.

10. **Não mostrar o que falta.** Um gráfico de vendas por produto que só mostra os que
    venderam esconde a informação mais acionável.

---

## 10. Os cinco porquês: por que gráfico de pizza é ruim?

1. **Por que pizza é pior que barras?**
   Porque codifica valor em **ângulo e área**, que a pesquisa de Cleveland e McGill (1984)
   posiciona em 4º e 5º lugar em precisão, contra a posição numa escala comum (1º) das
   barras.

2. **Por que ângulo é difícil de julgar?**
   Porque o sistema visual humano não tem um mecanismo dedicado a estimar ângulos com
   precisão, e a percepção é sistematicamente enviesada — ângulos agudos são subestimados
   e obtusos superestimados.

3. **Por que área é ainda pior?**
   Por causa da **lei de potência de Stevens**: a magnitude percebida cresce com o
   estímulo elevado a um expoente que, para área, é da ordem de 0,7. Ou seja, dobrar a
   área **não** é percebido como o dobro. A percepção comprime a escala.

4. **Por que a percepção é comprimida assim?**
   É uma propriedade do sistema sensorial, encontrada em várias modalidades (brilho,
   sonoridade, peso). A hipótese predominante é que a compressão amplia a faixa dinâmica
   útil: um sistema linear saturaria rápido. É adaptação evolutiva, não escolha.

5. **Parada legítima — propriedade da percepção humana.**
   O limite não está na ferramenta nem na convenção de design. Está no aparelho perceptivo
   de quem lê. Nenhuma melhoria de software resolve. **Por isso a recomendação é robusta**
   e não uma questão de gosto.

**A ressalva justa:** pizza funciona para o caso "duas ou três partes de um todo, onde
uma delas é claramente dominante". Nesse caso, o leitor não está estimando ângulos —
está reconhecendo uma proporção grosseira, e isso o olho faz bem.

---

## 11. Autoteste

1. Ordene as codificações visuais por precisão, segundo Cleveland e McGill.
2. Por que barras são a escolha padrão?
3. Escolha o visual para: "como a composição do faturamento por categoria evoluiu em 3 anos".
4. Por que a matriz é subestimada?
5. Cite quatro coisas para remover em nome da razão dado-tinta.
6. Que quatro tipos de contexto podem acompanhar um KPI?
7. Por que "não use cor como único canal", e qual é o teste prático?
8. Quantos visuais por página, e por quê?
9. Por que truncar o eixo Y é distorção em barras e aceitável em linhas?
10. Que risco de segurança existe em visuais customizados não certificados?
11. Explique, com a lei de Stevens, por que área é uma codificação ruim.

---

**Próximo:** [`19-interatividade-e-relatorios.md`](19-interatividade-e-relatorios.md) — o que
transforma um relatório em ferramenta.

---

*Referências: Cleveland, W. S.; McGill, R. "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods". Journal of the American Statistical Association, v. 79, n. 387, 1984. Tufte, E. "The Visual Display of Quantitative Information", 1983. Stevens, S. S. "On the Psychophysical Law", Psychological Review, 1957. Recursos de tema de julho/2026 conforme [Microsoft Learn — What's new](https://learn.microsoft.com/en-us/power-bi/fundamentals/whats-new), consultado em 14/08/2026.*
