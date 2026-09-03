# 2. Pré-requisitos — o que saber, o que ter, e quanto tempo leva de verdade

`Nível: iniciante` · `Última atualização: 20/08/2026`

> Resposta curta, para quem tem pressa: **para entender média, mediana e desvio padrão você
> precisa de aritmética de 6º ano e mais nada.** Para entender *erro*, *intervalo de confiança*
> e *valor-p* — a parte que realmente muda decisões — você precisa da ideia de proporção e de
> uma noção de sorteio. Cálculo e álgebra linear só aparecem no arquivo
> [60-teoria-avancada.md](60-teoria-avancada.md), e você pode chegar a "praticante competente"
> sem eles.

Este arquivo é uma promessa e um filtro: ele diz **exatamente** o que é bloqueante e o que não é,
para você não adiar o começo por medo de uma matemática que não vai precisar.

---

## 2.1 Conhecimento: indispensável

Cada item traz o **teste de suficiência** — se você resolve o teste, o pré-requisito está pago.

### 1. Aritmética: somar, dividir, e o que é uma fração

> **Teste:** um produto custava R$ 80 e passou a custar R$ 100. De quanto foi o aumento
> percentual? E se voltasse de R$ 100 para R$ 80, seria a mesma porcentagem?

<details><summary>Resposta</summary>
Aumento de 25% (20/80). A volta é de 20% (20/100) — **não** é a mesma porcentagem, porque a
base mudou. Essa assimetria é a origem de metade das mentiras com porcentagem e do motivo de
existir <b>média geométrica</b> (ver <a href="12-medidas-de-posicao.md">12</a>).
</details>

Se você errou, isso é **bloqueante** — mas custa uma tarde. Rota de resgate no fim do arquivo.

### 2. Ordenar uma lista e achar o meio dela

Mediana, quartis e percentis são, literalmente, "ponha em ordem e conte". Nenhuma fórmula.

> **Teste:** qual a mediana de `[7, 2, 9, 4]`?
<details><summary>Resposta</summary>
Ordene: 2, 4, 7, 9. Com número <b>par</b> de elementos não há um do meio: convenciona-se a
média dos dois centrais → (4+7)/2 = <b>5,5</b>. Repare que 5,5 não é nenhum dos dados —
isso é uma convenção, e existem 9 convenções diferentes para quantis
(ver <a href="12-medidas-de-posicao.md">12</a>).
</details>

### 3. Notação de somatório (Σ) — ou disposição para aprendê-la em 10 minutos

Você **não precisa** saber de antemão; precisa não travar quando vir. É só isto:

```
 Σ  xᵢ   lê-se: "some os x, do primeiro (i=1) até o último (i=n)"
i=1..n

x = [3, 5, 8]  →  Σ xᵢ = 3 + 5 + 8 = 16
```

Σ é um `for` que acumula. Se você programa, já sabe somatório e não percebeu.

### 4. A ideia de proporção e de sorteio

Necessário só a partir do arquivo 15. Nada de teoria da probabilidade: basta entender
"em 6 lançamentos de um dado honesto **não** saem necessariamente um de cada face" e
"chance de 1 em 20 significa que acontece de vez em quando, não que é impossível".

> **Teste:** você joga uma moeda honesta 10 vezes e dá cara nas 10. Qual a chance de dar
> cara na 11ª?
<details><summary>Resposta</summary>
<b>50%</b>, se a moeda for realmente honesta — a moeda não tem memória. Achar que "agora tem
que dar coroa" é a <i>falácia do apostador</i>. Mas há uma segunda leitura, mais madura:
depois de 10 caras seguidas (chance de 1 em 1.024), talvez a hipótese "a moeda é honesta"
mereça revisão. Essa tensão entre "confio no modelo" e "os dados estão me dizendo outra coisa"
é a inferência estatística inteira, resumida em três linhas.
</details>

### Nada além disso é indispensável

Especificamente, **não** são pré-requisitos: cálculo, integral, álgebra linear, teoria da
medida, programação. Cada um deles aparece em algum ponto, sempre com aviso e sempre em
arquivo próprio.

---

## 2.2 Conhecimento: ajuda muito (mas não bloqueia)

| Item | Onde ajuda | Se faltar |
|---|---|---|
| **Programar um pouco** (qualquer linguagem) | arquivos 04, 06, 07, 70 | dá para ler tudo e usar planilha; perde-se a simulação, que é o melhor professor |
| **Raiz quadrada e potência** | fórmula do desvio padrão, do erro padrão | use a calculadora; o conceito não depende disso |
| **Log e exponencial** | dados assimétricos, escala log, média geométrica (14) | pule a seção de log-transformação na primeira leitura |
| **Cálculo (derivada)** | por que a média minimiza os quadrados (12, 60) | o argumento geométrico substitui a derivada em 12 |
| **Álgebra linear** | covariância como matriz, regressão múltipla (16, 60) | só faz falta no bloco de teoria avançada |
| **Inglês técnico de leitura** | documentação, papers, 80% dos bons cursos | os melhores cursos em PT estão em [85](85-cursos-e-certificacoes.md) |
| **Planilha (Excel/Calc/Sheets)** | onde 90% do mundo realmente faz estatística | — |

> **Opinião profissional (não é consenso):** saber programar muda o assunto de *decorar
> fórmulas* para *testar afirmações*. Quando você consegue simular 100.000 amostras em três
> linhas, conceitos como "erro padrão" e "intervalo de confiança" deixam de ser definições e
> viram coisas que você **vê acontecer na tela**. Se você tem 20 horas sobrando, gastá-las
> aprendendo o básico de Python rende mais no aprendizado de estatística do que gastá-las
> estudando estatística. É a única recomendação deste curso que peço para levar a sério
> mesmo parecendo um desvio.

---

## 2.3 Ambiente: o que ter na máquina

O detalhe passo a passo está em [03-instalacao.md](03-instalacao.md). Aqui está só o que
decidir antes:

| Nível de uso | Ferramenta suficiente | Custo | Instalação |
|---|---|---|---|
| Ler o curso, fazer as contas à mão | papel, lápis, calculadora do celular | R$ 0 | nenhuma |
| Rodar todos os exemplos deste curso | **Python 3.10+**, só a biblioteca padrão | R$ 0 | já vem no Linux e no macOS |
| Trabalhar com dados de verdade | Python + NumPy/pandas, **ou** R | R$ 0 | ver [03](03-instalacao.md) |
| Clicar em vez de programar | **JASP** ou **jamovi** (grátis, código aberto) | R$ 0 | ver [03](03-instalacao.md) |
| Não instalar nada hoje | Google Colab, JupyterLite, Anaconda Cloud | R$ 0 | só navegador |

**Requisitos de hardware:** qualquer computador dos últimos 15 anos. Estatística descritiva
em conjuntos de dados de até alguns milhões de linhas roda em 2 GB de RAM. Nada aqui precisa
de GPU, e desconfie de quem disser que precisa.

**Conta em serviço:** nenhuma é obrigatória. O Google Colab pede conta Google; é a única
conveniência que cobra um cadastro, e existe alternativa sem conta (JupyterLite).

---

## 2.4 Tempo realista até cada nível

Estes números vêm de observar gente aprendendo, não de otimismo de ementa. Assumem estudo
**com as mãos** (rodando código, refazendo contas), não leitura passiva.

| Objetivo | Tempo | O que você consegue fazer |
|---|---|---|
| Entender o que são as medidas (arquivo 01) | **40 minutos** | conversar sem falar besteira; ler jornal com desconfiança |
| Primeiro resultado na tela (04) | **+ 30 minutos** | calcular tudo em dados seus |
| Descrever um conjunto de dados com competência | **8 a 15 horas** | escolher a medida certa, ver assimetria, desconfiar de outlier |
| Entender erro, IC e valor-p **de verdade** | **25 a 50 horas** | ler um artigo científico e detectar o truque; dimensionar amostra |
| Praticante sólido (nível analista júnior) | **3 a 5 meses**, 6 h/semana | fazer análise defensável, escrever relatório honesto |
| Nível de graduação em estatística (bloco B inteiro) | **10 a 18 meses** | teoria, provas, escolha de estimador, simulação |
| Nível pesquisa (arquivos 60 e 65) | **2 a 4 anos** com orientação | ler e criticar literatura metodológica |

**Onde as pessoas travam** — na ordem em que acontece:

1. **Semana 2**: `n` versus `n−1` no desvio padrão. Todo mundo trava aqui. Resposta completa
   em [13-medidas-de-dispersao.md](13-medidas-de-dispersao.md); resposta curta: é uma correção
   de viés, e ela importa pouco quando `n > 30` e muito quando `n < 10`.
2. **Semana 4**: confundir **desvio padrão** (dispersão dos dados) com **erro padrão**
   (dispersão da média). São coisas diferentes por um fator √n. É o erro mais comum em
   artigos publicados. Arquivo [15](15-erro-e-incerteza.md).
3. **Semana 6**: achar que valor-p é "a probabilidade de a hipótese ser falsa". Não é, e a
   distância entre as duas coisas já custou carreiras. Arquivo
   [18](18-inferencia-p-e-ic.md).
4. **Mês 3**: aceitar que **correlação não é causalidade** de boca, mas continuar concluindo
   causalidade na prática. Arquivo [16](16-relacao-entre-variaveis.md).

---

## 2.5 Rota de resgate — o que fazer se faltar um pré-requisito

### Falta aritmética / porcentagem

- **Khan Academy em português**, trilha "Matemática básica" → seções de fração, decimal,
  porcentagem: <https://pt.khanacademy.org/math/arithmetic>
- Tempo: 6 a 10 horas. É o único investimento realmente bloqueante.

### Falta a ideia de sorteio / probabilidade

- Não estude probabilidade formal antes. **Simule.** Jogue uma moeda 50 vezes de verdade e
  anote. Depois faça o computador jogar 1 milhão. O laboratório 3 de
  [70-pratica.md](70-pratica.md) faz exatamente isso e substitui um semestre de intuição.
- Se quiser texto: Khan Academy, trilha "Estatística e probabilidade"
  (<https://pt.khanacademy.org/math/statistics-probability>).

### Falta programação

- Você tem **duas saídas legítimas**:
  1. **Planilha.** Todo exemplo deste curso tem equivalente em LibreOffice Calc / Excel,
     listado em [05-manual-de-uso.md](05-manual-de-uso.md). Não é gambiarra: a maior parte da
     estatística aplicada do mundo acontece em planilha.
  2. **Aprender o mínimo de Python.** Não o Python inteiro: variáveis, lista, `for`, `def`,
     `print`. São 4 a 6 horas e cobrem 100% do código deste curso.
     Trilha oficial em português: <https://docs.python.org/pt-br/3/tutorial/> (capítulos 3 a 5).
- ⚠️ **Não** aprenda pandas antes de aprender listas. Pular a base faz o pandas parecer mágica,
  e mágica não se depura.

### Falta cálculo / álgebra linear

- **Não é bloqueante até o arquivo 60.** Siga em frente e volte quando chegar lá.
- Quando chegar: 3Blue1Brown, "Essence of Calculus" e "Essence of Linear Algebra"
  (YouTube, legendas em português, ~3 h cada série). É o melhor material gratuito que existe
  para *intuição*; não substitui exercícios.

### Falta tempo

Ordem de leitura de emergência, 3 horas no total, que já lhe dá 80% do valor prático:

`01` → `04` → `12` (só as seções 12.1 a 12.4) → `13` (12.1–13.5) → `15` (inteiro) → `75`.

O arquivo [75-armadilhas.md](75-armadilhas.md) sozinho evita mais erro do que qualquer outro
neste curso. Se você só puder ler um arquivo depois deste, leia aquele.

---

## 2.6 Como saber que você está pronto para o arquivo 04

Checklist honesto. Se marcar todos, siga:

- [ ] Sei calcular a média de `[4, 8, 9]` de cabeça.
- [ ] Sei achar a mediana de `[4, 8, 9, 15]` e sei que ela não precisa ser um dos dados.
- [ ] Entendo que "erro" aqui não significa que alguém errou.
- [ ] Consigo abrir um terminal (ou sei que vou usar planilha/navegador).
- [ ] Aceito, por ora, que a média é uma gangorra e a mediana é uma fila.

---

## Autoteste

1. Cálculo é pré-requisito para entender desvio padrão? E para provar por que a fórmula tem
   `n−1`?
2. Qual é o único pré-requisito matemático realmente bloqueante deste curso?
3. Quanto tempo, de forma honesta, leva para entender valor-p **de verdade**?
4. Qual a diferença entre desvio padrão e erro padrão — e por que essa confusão é campeã?
5. Você não sabe programar e tem que entregar uma análise amanhã. Qual é o caminho?
6. Por que a recomendação é simular antes de estudar probabilidade formal?
7. Qual arquivo deste curso dá o maior retorno por hora lida, se você só puder ler um?

<details><summary>Respostas</summary>

1. Para **entender e usar**, não. Para **provar** a correção de Bessel (`n−1`), sim — e essa
   prova está em [60-teoria-avancada.md](60-teoria-avancada.md), fora do caminho principal.
2. Aritmética com frações e porcentagem. Todo o resto é opcional ou adiável.
3. 25 a 50 horas de estudo ativo. Quem diz "em uma aula" está vendendo a definição, não o
   entendimento.
4. Desvio padrão descreve **o espalhamento dos dados**; erro padrão descreve **o espalhamento
   da média entre amostras** — é o desvio padrão dividido por √n. A confusão é campeã porque
   os nomes são parecidos, o símbolo é parecido, e usar o menor dos dois faz o resultado
   parecer mais forte, o que gera um incentivo silencioso para errar sempre para o mesmo lado.
5. Planilha. Todo exemplo tem equivalente em Calc/Excel no arquivo
   [05](05-manual-de-uso.md).
6. Porque a intuição de aleatoriedade é construída por observação repetida, não por definição.
   Ver a média de 1.000 amostras se concentrar na tela ensina o Teorema Central do Limite
   melhor que a demonstração — e depois a demonstração fica fácil.
7. [75-armadilhas.md](75-armadilhas.md).

</details>

---

**Próximo:** [03-instalacao.md](03-instalacao.md) — manual de campo, por sistema operacional.
Se você só quer ver algo funcionando agora e decidir depois:
[04-como-comecar.md](04-como-comecar.md).
