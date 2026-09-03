# 11. História — de onde vieram essas medidas e que problema cada uma resolveu

`Nível: iniciante` · `Última atualização: 20/08/2026`

> Cada medida deste curso foi inventada por alguém, para resolver um problema concreto, num
> ano específico. Saber qual era o problema explica por que a medida tem a forma que tem — e
> por que ela quebra fora daquele contexto. Este arquivo é a resposta longa para "por que é
> assim?".

---

## 11.0 Linha do tempo

```
1654  Pascal & Fermat        probabilidade nasce de um problema de jogo
1662  John Graunt            primeira tábua de mortalidade — a estatística vira ofício
1713  Jacob Bernoulli        lei dos grandes números (póstumo, "Ars Conjectandi")
1733  Abraham de Moivre      a curva normal aparece como aproximação da binomial
1749  Gottfried Achenwall    cunha "Statistik": a ciência do Estado
1805  Adrien-Marie Legendre  publica o método dos mínimos quadrados
1809  Carl Friedrich Gauss   justifica a normal a partir dos mínimos quadrados
1810  Pierre-Simon Laplace   Teorema Central do Limite
1835  Adolphe Quetelet       "o homem médio" — a média aplicada a gente
1854  John Snow              o mapa da cólera: dados que mudam uma política pública
1858  Florence Nightingale   o diagrama polar: visualização que muda um exército
1886  Francis Galton         regressão à média
1888  Francis Galton         correlação
1894  Karl Pearson           cunha o termo "desvio padrão" (standard deviation)
1900  Karl Pearson           teste do qui-quadrado
1908  W. S. Gosset "Student" a distribuição t — nascida numa cervejaria
1922  Ronald Fisher          máxima verossimilhança; formaliza "estatística suficiente"
1924  Walter Shewhart        carta de controle: o foco muda da média para a variabilidade
1925  Ronald Fisher          "Statistical Methods for Research Workers"; o 0,05 se firma
1933  Neyman & E. Pearson    o arcabouço de teste de hipóteses (erros tipo I e II)
1933  Andrei Kolmogorov      axiomatiza a probabilidade
1937  Jerzy Neyman           intervalo de confiança
1945  Frank Wilcoxon         testes de posto: a estatística sem suposição de normal
1950  W. E. Deming           leva o controle estatístico ao Japão
1964  Peter Huber            estatística robusta como teoria
1973  F. J. Anscombe         o quarteto: resumo nunca substitui olhar
1977  John Tukey             "Exploratory Data Analysis"; boxplot; a cerca de 1,5×IQR
1979  Bradley Efron          bootstrap
1995  Benjamini & Hochberg   taxa de falsas descobertas (FDR)
2005  John Ioannidis         "Why Most Published Research Findings Are False"
2011  Simmons, Nelson & Simonsohn   "False-Positive Psychology": nomeia o p-hacking
2015  Open Science Collab.   Reproducibility Project: Psychology
2016  ASA                    declaração oficial sobre valores-p
2019  The American Statistician  "Moving to a World Beyond p < 0,05"
2020s Vovk, Ramdas, Grünwald e-values, inferência válida a qualquer momento, conformal
```

---

## 11.1 Antes de existir "estatística": contar mortos em Londres

**1662.** John Graunt, um comerciante de aviamentos de Londres sem formação acadêmica, faz
algo que ninguém tinha feito: pega os *Bills of Mortality* — as listas semanais de óbitos que
as paróquias publicavam desde a peste — e as **soma ao longo dos anos**.

Do amontoado ele extrai regularidades que espantaram seus contemporâneos:

- nascem mais meninos que meninas, ano após ano, numa proporção estável;
- a proporção de mortes por cada causa é notavelmente constante entre anos;
- constrói a primeira **tábua de vida**: de 100 nascidos, quantos chegam aos 6, aos 16, aos 26.

> **A descoberta filosófica de Graunt não foi um número: foi que existe regularidade no
> agregado onde há caos no indivíduo.** Ninguém sabe quando vai morrer; a proporção de mortos
> por ano é previsível. Toda a estatística depende dessa observação, e ela não era óbvia — era
> contraintuitiva o bastante para render a Graunt uma cadeira na Royal Society por indicação
> pessoal do rei Carlos II.

A palavra "estatística" só apareceria em 1749, com **Gottfried Achenwall**, do alemão
*Statistik*: a ciência descritiva do **Estado**. Por quase um século, "estatística" significou
"tabelas sobre o país", sem nenhuma matemática. Herdamos daí o nome — e o hábito, ainda vivo,
de chamar de estatística qualquer tabela.

---

## 11.2 A média nasce na astronomia, não na sociologia

Antes de 1800, tirar a média de medições era **controverso**. O raciocínio dominante era: se
uma das medidas é a melhor, misturá-la com as piores só pode piorá-la. Astrônomos preferiam
escolher a observação feita nas melhores condições.

O que mudou isso foi um problema prático de urgência astronômica.

**1801.** O asteroide **Ceres** é descoberto, observado por 41 dias e some atrás do Sol.
Para reencontrá-lo, era preciso prever sua órbita a partir de pouquíssimas observações
imprecisas e discordantes. **Carl Friedrich Gauss**, com 24 anos, usa um método próprio para
combinar as observações, prevê onde Ceres reapareceria — e acerta. O asteroide é reencontrado
na posição prevista.

O método era o dos **mínimos quadrados**: escolher os parâmetros que minimizam a soma dos
quadrados dos resíduos. **Legendre** o publicou primeiro, em 1805; Gauss afirmou tê-lo usado
desde 1795 e o publicou em 1809, no *Theoria Motus*, gerando uma das disputas de prioridade
mais amargas da história da matemática.

### Por que quadrados, e não módulos?

Esta é a pergunta certa, e a resposta tem três camadas — as três valem, e é raro alguém dizer
isso com clareza:

1. **Camada matemática.** O quadrado é diferenciável em toda parte; o módulo não é (tem um
   bico em zero). Em 1805, sem computador, isso era decisivo: mínimos quadrados tem **solução
   fechada** — você resolve um sistema linear e acabou. Minimizar módulos exige otimização
   iterativa, inviável à mão para sistemas grandes.
2. **Camada probabilística.** Gauss mostrou (1809) que **se** os erros seguem a distribuição
   normal, **então** a média é a estimativa de máxima verossimilhança e os mínimos quadrados
   são ótimos. O argumento tem uma circularidade que Gauss reconheceu: ele em parte *escolheu*
   a normal por ser a distribuição que torna a média ótima.
3. **Camada honesta.** Minimizar o valor absoluto (regressão quantílica, mediana) é
   frequentemente **melhor** com dados reais, que têm outliers. A opção pelos quadrados foi um
   **trade-off computacional** de 1805 que se cristalizou em tradição e sobreviveu à razão que
   a justificava. Hoje computamos mínimos absolutos sem esforço, e não mudamos o hábito.

> **Quinto porquê.** *Por que a estatística ainda é dominada por quadrados?* Porque a álgebra
> linear dos quadrados é a mesma da geometria euclidiana: variância se decompõe pelo teorema
> de Pitágoras, projeções ortogonais resolvem regressão, ANOVA é decomposição de espaços.
> Nenhuma outra função de perda dá essa estrutura. **Não é que quadrados sejam corretos; é
> que eles são os únicos que fazem a matemática fechar bonito** — e isso, historicamente,
> pesou mais que a robustez.

---

## 11.3 Quetelet e a invenção (perigosa) do "homem médio"

**1835.** **Adolphe Quetelet**, astrônomo belga, faz o salto que criou a estatística social:
aplica a máquina de erros da astronomia a **pessoas**.

O raciocínio dele: se 100 astrônomos medem a mesma estrela, os erros se distribuem em sino em
torno do valor verdadeiro. Se 100 mil recrutas franceses têm suas alturas medidas, as alturas
também se distribuem em sino. **Logo** — concluiu — deve existir um "valor verdadeiro" do qual
cada pessoa é um desvio: *l'homme moyen*, o homem médio.

Foi enormemente influente e **filosoficamente errado de um jeito que ainda faz estrago**.

Na astronomia, existe uma estrela real e o desvio é erro de medição. Em uma população, **não
existe uma "pessoa verdadeira"** da qual todos sejam desvios defeituosos. A variação entre
pessoas é o fenômeno, não ruído em torno de um ideal.

As consequências foram graves e concretas:

- Quetelet e seguidores trataram desvios da média como **anomalia**, alimentando o vocabulário
  do "normal" versus "anormal".
- Galton, discípulo de Quetelet, funda a **eugenia** em 1883, empurrando essa lógica ao seu
  extremo. Karl Pearson e Ronald Fisher — os dois maiores nomes da estatística moderna — foram
  eugenistas convictos. Isso não é nota de rodapé: **grande parte do aparato estatístico que
  usamos foi construída para medir e classificar diferenças humanas com finalidade
  eugênica**, e há literatura séria examinando o que dessa origem ficou embutido nos métodos.
- A ideia de "projetar para a média" se espalhou. O caso mais citado é o da Força Aérea
  americana nos anos 1940: cabines projetadas para o piloto médio em 10 dimensões corporais.
  Em 1950, o tenente Gilbert Daniels mediu 4.063 pilotos e verificou que **nenhum** deles era
  "médio" em todas as dimensões simultaneamente — o que levou os projetos a adotarem assentos
  e comandos **ajustáveis**. Essa é a lição de engenharia mais duradoura da estatística
  descritiva: *a média não é um caso; é uma abstração*.

> **Fique com isto:** a média descreve o **agregado**, nunca o **indivíduo**. Toda vez que uma
> política é desenhada para o cliente médio, o aluno médio ou o paciente médio, esse erro está
> sendo repetido.

---

## 11.4 Galton, a regressão e a correlação

**1886.** **Francis Galton** estuda alturas de pais e filhos e nota algo que o incomoda: pais
muito altos têm filhos altos, mas **menos** altos que eles; pais muito baixos têm filhos
baixos, mas menos baixos. Ele chama isso de *"regression towards mediocrity"* — regressão em
direção à mediocridade.

Galton interpretou como uma força biológica puxando a espécie de volta ao tipo. **Não é.**
É um fato puramente estatístico: sempre que duas variáveis são imperfeitamente correlacionadas,
valores extremos de uma são acompanhados por valores menos extremos da outra. O "efeito" existe
até entre variáveis sem nenhuma relação causal — e existe **nas duas direções**: filhos muito
altos também tiveram pais menos altos que eles, o que já mostra que não pode ser causa.

O nome ficou. Hoje chamamos de "regressão" um dos métodos mais usados da estatística por causa
de um mal-entendido sobre hereditariedade em 1886. Ver o
[exemplo 10 do arquivo 06](06-exemplos.md), onde o efeito é simulado sem nenhuma causa.

**1888.** Galton formaliza a **correlação**, e Karl Pearson a põe na forma que usamos hoje —
por isso "correlação de Pearson".

---

## 11.5 1894: o desvio padrão ganha nome

Até o fim do século XIX, a dispersão era medida de várias formas concorrentes, sem
padronização: *erro médio*, *erro provável* (0,6745σ, ainda comum em astronomia e física até
os anos 1930), *desvio absoluto médio*, *erro quadrático médio*.

**Karl Pearson**, em 1894, cunha o termo **standard deviation** — "desvio padrão" — e a
notação σ. A palavra "padrão" significa aqui *de referência, que serve de régua*, não
"obrigatório".

Por que essa medida venceu as concorrentes? Três razões, e nenhuma é "porque é a melhor
descrição da dispersão":

1. **Ela se decompõe.** Variâncias de variáveis independentes se **somam** — propriedade que
   nenhuma outra medida de dispersão tem. É isso que torna possível a ANOVA, a propagação de
   incerteza e o teorema de que EP = σ/√n.
2. **Ela é a medida natural da normal.** Numa distribuição normal, μ e σ são os **dois únicos**
   parâmetros: dizer os dois é dizer tudo. Nenhuma informação se perde.
3. **Ela era calculável.** Antes das calculadoras, `Σ(x−x̄)²` podia ser computado em uma
   passada com uma máquina mecânica de somar. Mediana exige ordenar, o que é caro à mão.

> **Cinco porquês, até o fim.** *Por que se eleva ao quadrado?* Para não cancelar sinais.
> *Por que não usar o módulo, que também não cancela?* Porque o módulo não é diferenciável e
> não se decompõe. *Por que a decomposição importa tanto?* Porque variâncias somam, e é isso
> que sustenta EP = σ/√n, ANOVA e propagação de erro. *Por que variâncias somam?* Porque a
> variância é um produto interno em um espaço vetorial, e variáveis independentes são
> **ortogonais** nesse espaço — somar variâncias é o teorema de Pitágoras.
> **Parada legítima: é um fato geométrico, não uma convenção.**

---

## 11.6 A cervejaria que mudou a ciência: Gosset e a t

**1908.** **William Sealy Gosset** é químico-chefe da cervejaria **Guinness**, em Dublin. Seu
problema é industrial e imediato: avaliar a qualidade de lotes de cevada e de levedura com
**amostras minúsculas** — três, quatro, cinco medições. Não havia como coletar mil.

A teoria da época dizia: use σ/√n e a curva normal. Gosset percebeu, na prática, que isso
**não funciona com n pequeno**, porque você não conhece σ — você o estima por `s`, e essa
estimativa também erra. Ignorar o erro do erro produzia intervalos estreitos demais e decisões
erradas na cervejaria.

Gosset deriva a distribuição correta para `(x̄ − μ)/(s/√n)`: a **distribuição t**, com caudas
mais grossas que a normal, tanto mais grossas quanto menor o `n`. Ela converge para a normal
quando `n` cresce.

Ele publica na *Biometrika* sob o pseudônimo **"Student"** porque a Guinness proibia
publicações de funcionários — segundo o relato mais aceito, depois que um empregado havia
revelado segredos industriais. A empresa temia que artigos revelassem vantagem competitiva.
Ironia registrada: **a Guinness tinha razão em considerar isso vantagem competitiva**, e
mesmo assim o método vazou para o mundo inteiro sob um nome falso.

> **Por que isso importa até hoje:** toda vez que você usa `t` em vez de `1,96` com amostra
> pequena, está usando a solução de um problema de controle de qualidade de cerveja de 1908.
> E o erro que Gosset corrigiu — **esquecer que a estimativa da dispersão também tem erro** —
> continua sendo cometido diariamente. Ver [15-erro-e-incerteza.md](15-erro-e-incerteza.md).

---

## 11.7 Fisher e a origem arbitrária do 0,05

**Ronald A. Fisher** é, com folga, a figura mais influente da estatística do século XX.
Entre 1922 e 1935 ele cria ou consolida: máxima verossimilhança, análise de variância,
delineamento experimental, **aleatorização** como fundamento da inferência causal, e o valor-p
como ferramenta de rotina.

O famoso **0,05** aparece no *Statistical Methods for Research Workers* (1925). Fisher escreve,
em essência, que dois desvios padrão é um limite conveniente e que ele pessoalmente prefere
ignorar resultados que não o alcancem.

**Não havia teoria por trás disso.** Havia praticidade tipográfica: as tabelas eram calculadas
à mão e impressas em livros, então era preciso escolher **alguns** níveis para tabelar. 0,05,
0,01 e 0,001 foram os escolhidos. Fisher depois protestou explicitamente contra o uso
mecânico de um limiar fixo, defendendo que o valor-p exato fosse reportado e julgado no
contexto — mas o limiar já tinha vida própria.

> **Esta é uma parada legítima da regra dos cinco porquês: uma convenção arbitrária, adotada
> por conveniência de impressão, que se tornou critério de publicação de artigos científicos e
> de aprovação de medicamentos por quase um século.** Não há justificativa matemática para
> 0,05. Se as tabelas de 1925 tivessem sido impressas com 0,03 e 0,003, a ciência do século XX
> teria outro limiar — e as mesmas discussões.

Fisher também travou uma guerra pública e pessoal com **Jerzy Neyman** e **Egon Pearson**, que
em 1933 propuseram outro arcabouço: em vez de "quanto os dados surpreendem sob H₀", pensar em
**decisão** com taxas de erro tipo I (α) e tipo II (β) controladas a longo prazo. Neyman
introduziria o **intervalo de confiança** em 1937.

O que se ensina hoje na maioria dos cursos é um **híbrido incoerente** dos dois — o "teste de
significância de hipótese nula" — que Fisher rejeitaria e Neyman também. A confusão sobre o
que é um valor-p ([arquivo 18](18-inferencia-p-e-ic.md)) tem aqui sua origem histórica: não é
o aluno que confunde, é o método que foi remendado.

---

## 11.8 Shewhart, Deming e a virada industrial: a variabilidade vale mais que a média

**1924.** **Walter Shewhart**, dos Bell Labs, escreve um memorando de uma página com a
primeira **carta de controle**. A ideia é uma inversão de foco:

> Não pergunte "qual é a média?". Pergunte **"a variabilidade deste processo é a de sempre, ou
> algo mudou?"**

Shewhart separa **causa comum** (a variação natural, sempre presente, inerente ao processo) de
**causa especial** (algo específico aconteceu). E enuncia a lição que atravessa toda a gestão
moderna: **reagir a causa comum como se fosse causa especial piora o processo**. Ajustar a
máquina a cada peça fora do alvo aumenta a variabilidade em vez de reduzir.

**W. Edwards Deming** leva isso ao Japão a partir de 1950, com resultados que reorganizaram a
indústria mundial. A demonstração pedagógica de Deming — o *experimento das contas vermelhas*,
em que trabalhadores são premiados e punidos por resultados inteiramente determinados por
sorteio — é uma das melhores aulas de estatística já dadas, e ensina exatamente o mesmo que a
regressão à média do [exemplo 10](06-exemplos.md).

> **O eco disso hoje:** todo painel de indicadores que compara "esta semana com a semana
> passada" e cobra explicação por cada oscilação está cometendo o erro que Shewhart nomeou em
> 1924. A pergunta certa nunca é "por que caiu 3%?"; é "3% está fora da variação normal deste
> indicador?".

---

## 11.9 Tukey e a revolução de olhar para os dados

**John Tukey** (que também cunhou as palavras *bit* e *software*) percebe, nos anos 1960, que
a estatística tinha virado uma disciplina de **confirmação** — testes, provas, otimalidade —
e tinha esquecido a parte de **descobrir**.

Em *Exploratory Data Analysis* (1977) ele propõe uma prática deliberadamente informal, feita
com lápis e papel, baseada em resumos robustos e em desenho. Dali saem:

- o **boxplot** (diagrama de caixa) e o resumo de cinco números;
- a **cerca de 1,5 × IQR** para sinalizar outliers — e Tukey foi explícito ao dizer que era
  uma **régua prática**, não um teste. O 1,5 foi escolhido porque, numa distribuição normal,
  ele marca cerca de 0,7% dos dados: raro o bastante para chamar atenção, comum o bastante para
  não ser alarme falso constante. **É uma convenção calibrada, não um resultado.**
- o *stem-and-leaf*, a mediana como resumo padrão, a ênfase em **resíduos**.

A frase de Tukey que resume a disciplina inteira:

> *"Far better an approximate answer to the right question, which is often vague, than an
> exact answer to the wrong question, which can always be made precise."*
> ("Muito melhor uma resposta aproximada à pergunta certa, que costuma ser vaga, do que uma
> resposta exata à pergunta errada, que sempre pode ser tornada precisa.")

**1973.** **F. J. Anscombe**, colega de Tukey, publica o quarteto que leva seu nome
([exemplo 9](06-exemplos.md)) — quatro conjuntos com estatísticas idênticas e formatos
completamente diferentes. O timing não é acidental: os computadores começavam a permitir
calcular sem olhar, e Anscombe estava avisando o que aconteceria.

---

## 11.10 1979: o computador devolve o poder à estatística

**Bradley Efron** publica o **bootstrap**. A ideia é quase indecente na sua simplicidade:

> Sua amostra é a melhor estimativa que você tem da população. Então **trate a amostra como se
> fosse a população** e sorteie dela, com reposição, milhares de vezes. A variação entre esses
> sorteios estima a variação entre amostras reais.

Antes, calcular o erro padrão de uma estatística exigia derivação matemática caso a caso — e
para muitas medidas (mediana, quartis, razões, coeficientes de assimetria) não havia solução
fechada, ou havia uma aproximação ruim. Com o bootstrap, **qualquer** medida ganha erro padrão
e intervalo de confiança, com dez linhas de código.

Isso mudou o eixo do campo: de "que suposições eu preciso fazer para ter uma fórmula?" para
"que suposições eu preciso fazer, e ponto — porque a conta o computador faz". É a mudança
tecnológica mais importante da estatística desde a máquina de somar.

---

## 11.11 2005–2026: a crise de replicação e o cerco ao valor-p

**2005.** **John Ioannidis** publica *"Why Most Published Research Findings Are False"*.
O argumento é aritmético, não retórico: dado um poder estatístico típico baixo, muitas
hipóteses testadas e forte incentivo a publicar positivos, **a maioria dos resultados
"significativos" publicados será falsa**, mesmo sem nenhuma má-fé.

**2011.** Simmons, Nelson e Simonsohn, em *"False-Positive Psychology"*, demonstram
empiricamente que decisões aparentemente inocentes durante a análise — quando parar de coletar
dados, quais covariáveis incluir, quais condições comparar — elevam a taxa de falso positivo
de 5% para mais de 60%. Nomeiam o fenômeno: **graus de liberdade do pesquisador**, e o que
resulta dele, **p-hacking**.

**2015.** O *Reproducibility Project: Psychology* tenta replicar 100 estudos publicados em
revistas de primeira linha. Menos da metade replica, e os tamanhos de efeito das replicações
são, em média, cerca de metade dos originais.

**2016.** A **American Statistical Association** publica sua primeira declaração de posição em
178 anos de existência — sobre valores-p. Seis princípios, dos quais os mais citados:
*o valor-p não mede a probabilidade de a hipótese ser verdadeira*; *não mede o tamanho do
efeito nem a importância do resultado*; *"p < 0,05" não deve ser base para decisão científica
ou de política*.

**2019.** O periódico *The American Statistician* dedica uma edição inteira a
*"Moving to a World Beyond p < 0,05"*, com 43 artigos. O editorial é direto: **"não diga
'estatisticamente significante'; não use a expressão"**. No mesmo ano, um comentário na
*Nature* liderado por Amrhein, Greenland e McShane, assinado por mais de 800 cientistas, pede
o abandono do conceito de significância estatística.

**Onde estamos em 2026.** O debate não está resolvido, e é honesto dizer isso:

- muitos periódicos exigem hoje tamanho de efeito e IC junto com o p; alguns baniram o p;
- pré-registro de hipóteses e *Registered Reports* se tornaram práticas relevantes;
- há um movimento de fundo em direção a métodos bayesianos e a **e-values** e **inferência
  válida a qualquer momento**, que resolvem tecnicamente o problema de "espiar os dados
  enquanto coleta" ([arquivo 65](65-estado-da-arte.md));
- mas o p continua onipresente na prática, e o incentivo que produziu o problema — carreiras
  medidas por publicações positivas — mudou muito pouco.

> **Opinião profissional, declarada como tal:** a crise não é um problema de estatística; é um
> problema de incentivos que se manifesta na estatística. Trocar o valor-p por fator de Bayes
> ou por e-value sem mudar o que se recompensa apenas move o p-hacking de sala. O que
> demonstrou funcionar de fato é **pré-registro** e **replicação** — nenhum dos dois é uma
> técnica estatística.

---

## 11.12 O que a história ensina sobre as medidas

| Medida | Nasceu para | Consequência de a usar fora disso |
|---|---|---|
| **Média** | combinar medições astronômicas com erro simétrico | com dados assimétricos ou outliers, descreve mal |
| **Mínimos quadrados** | ter solução fechada sem computador | escolha de 1805 que hoje não é mais obrigatória |
| **Desvio padrão** | descrever a normal e permitir decomposição | com cauda pesada, infla e perde interpretação |
| **t de Student** | amostra minúscula de cevada | corrige a subestimação da incerteza com n pequeno |
| **0,05** | conveniência de tabela impressa | virou critério de verdade científica sem nunca ter sido |
| **Cerca de 1,5×IQR** | régua visual do boxplot | virou "teste de outlier" que Tukey nunca propôs |
| **Bootstrap** | dispensar fórmulas fechadas | ainda supõe que a amostra representa a população |

**O padrão que se repete:** cada medida foi uma boa resposta a um problema específico com as
restrições da época. Nenhuma foi projetada para ser universal. **Quase todo mau uso de
estatística é uma ferramenta correta aplicada fora do problema que a gerou.**

---

## Autoteste

1. Qual foi a descoberta conceitual de Graunt em 1662 — e por que ela não era óbvia?
2. Por que os mínimos quadrados venceram os mínimos módulos em 1805? Essa razão ainda vale?
3. Qual é o erro filosófico central do "homem médio" de Quetelet?
4. Galton achou que a regressão à média era uma força biológica. Por que não é?
5. Por que Gosset publicou como "Student", e que problema prático a t resolveu?
6. De onde vem o 0,05?
7. Qual foi a inversão de foco proposta por Shewhart em 1924?
8. O que o bootstrap tornou possível que antes exigia derivação matemática caso a caso?
9. Segundo a ASA (2016), cite duas coisas que o valor-p **não** é.
10. Que padrão histórico se repete no mau uso de medidas estatísticas?

<details><summary>Respostas</summary>

1. Que existe **regularidade estável no agregado** onde há imprevisibilidade total no
   indivíduo. Não era óbvio porque a intuição pré-moderna tratava eventos individuais
   (mortes, nascimentos) como singulares e sem lei.
2. Porque o quadrado é diferenciável e produz **solução fechada** — resolvível à mão em 1805.
   Hoje essa razão **não vale mais**: mínimos absolutos e regressão quantílica são
   computacionalmente triviais. O que segura os quadrados hoje é a estrutura geométrica
   (variâncias somam, projeções ortogonais), não a facilidade de cálculo.
3. Tratar a variação entre pessoas como **erro em torno de um ideal**, por analogia indevida
   com o erro de medição astronômica. Não existe uma "pessoa verdadeira"; a variação é o
   fenômeno.
4. Porque o efeito ocorre em **ambas as direções** (filhos altos também tiveram pais menos
   altos) e ocorre entre quaisquer variáveis imperfeitamente correlacionadas, inclusive sem
   relação causal. É consequência de correlação < 1, não de biologia.
5. Porque a Guinness proibia publicação de funcionários. A t resolveu a subestimação da
   incerteza quando **σ é estimado a partir de uma amostra pequena** — o erro de esquecer que
   a estimativa da dispersão também erra.
6. De uma escolha de conveniência para tabelar valores críticos em livros impressos
   (Fisher, 1925). Não há justificativa matemática; é convenção arbitrária que virou critério.
7. Deixar de perguntar "qual é a média?" e passar a perguntar **"a variabilidade é a de
   sempre, ou algo mudou?"** — e não reagir a causa comum como se fosse causa especial.
8. Calcular **erro padrão e intervalo de confiança para qualquer estatística**, inclusive as
   sem fórmula fechada (mediana, quartis, razões, assimetria).
9. Não é a probabilidade de a hipótese nula ser verdadeira; não mede o tamanho nem a
   importância do efeito. (Também: não deve ser base isolada para decisão.)
10. Uma ferramenta criada para um problema específico, com as restrições de sua época,
    aplicada fora daquele contexto — e cristalizada como se fosse universal.

</details>

---

**Fontes:** as datas e atribuições seguem, principalmente, Stephen M. Stigler, *The History of
Statistics: The Measurement of Uncertainty before 1900* (Harvard, 1986) e *Statistics on the
Table* (Harvard, 1999); a declaração da ASA de 2016 (Wasserstein & Lazar, *The American
Statistician* 70(2)); e o editorial de 2019 (Wasserstein, Schirm & Lazar, *TAS* 73(sup1)).
Ver [90-bibliografia.md](90-bibliografia.md) e [95-referencias.md](95-referencias.md).

**Próximo:** [12-medidas-de-posicao.md](12-medidas-de-posicao.md) — cada medida de posição
desmontada até o osso.
