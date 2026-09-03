# 1. O que são essas medidas, afinal — explicado sem nenhum jargão

`Nível: iniciante` · `Pré-requisito: saber somar e dividir` · `Última atualização: 20/08/2026`

> Este arquivo não usa nenhuma fórmula que você não consiga fazer de cabeça.
> Se em algum ponto aparecer um símbolo, ele é explicado na mesma linha.

---

## 1.1 O problema que faz tudo isso existir

Imagine que você precisa descrever uma turma de 40 alunos para alguém que nunca a viu,
e só pode dizer **duas frases**.

Você não vai listar as 40 alturas. Ninguém guarda 40 números. Você vai dizer algo como:

> "É uma turma de gente mais ou menos da mesma altura, uns 1,70 m."

Nessa frase há **duas medidas**, e elas são exatamente as duas famílias de medidas que a
estatística inventou:

| O que você disse | O que é | Nome técnico |
|---|---|---|
| "uns 1,70 m" | onde os números se concentram | **medida de posição** (ou de tendência central) |
| "mais ou menos da mesma altura" | quanto eles discordam entre si | **medida de dispersão** (ou de variabilidade) |

Toda a estatística descritiva é isso: **substituir um monte de números por poucos números
que não mentem demais**. E toda a dificuldade do assunto está em duas palavras dessa frase:
*poucos* e *demais*.

Guarde esta ideia, porque ela volta em todos os arquivos deste curso:

> **Toda medida-resumo é uma compressão com perda.**
> Você joga informação fora de propósito. A pergunta nunca é "essa medida está certa?",
> e sim **"o que eu joguei fora, e isso importava?"**

---

## 1.2 As três formas de dizer "o valor típico"

### Média — o ponto de equilíbrio da gangorra

Você tem os números 2, 4, 9. Some (15) e divida pela quantidade (3): a **média** é 5.

A imagem certa para média não é "o valor do meio". É esta: imagine uma **gangorra** (uma
tábua sobre um apoio). Coloque um peso de 1 kg em cada número, na posição dele:

```
     2      4              9
     ●      ●              ●
 ────┴──────┴──────△───────┴────
 0   1   2  3   4  5  6  7  8  9  10
                   ↑
                média = 5 (único ponto de apoio que equilibra)
```

A média é **o único lugar onde você pode pôr o apoio para a tábua ficar equilibrada**.
Isso não é uma metáfora bonitinha: é literalmente a definição de centro de massa da física,
e é o motivo de a média ter todas as propriedades que tem.

Consequência imediata e importantíssima: **um peso longe do apoio desequilibra muito**.
Se o 9 virasse 900, a média salta de 5 para 302. Um único número mudou o "valor típico"
de toda a coleção. Isso não é defeito de cálculo, é como uma gangorra funciona.

> **O bar com Bill Gates.** Nove pessoas num bar ganham R$ 3.000 por mês cada uma.
> Entra Bill Gates. O salário **médio** no bar passa a ser algo perto de R$ 100 milhões.
> A frase "o salário médio neste bar é de R$ 100 milhões" é **aritmeticamente correta e
> descritivamente inútil**. Ninguém ali ficou mais rico.

### Mediana — o valor do meio da fila

Ponha todo mundo em fila, do menor para o maior, e pegue **quem está no meio**.
Com 2, 4, 9 → a mediana é 4. Com Bill Gates no bar, a mediana continua R$ 3.000.

```
 fila ordenada:  3000  3000  3000  3000 [3000] 3000  3000  3000  3000  ~10^10
                                          ↑
                                    mediana = 3000  (não se mexe)
```

A mediana **não sabe o quanto** os valores das pontas são extremos — só sabe que estão
de um lado ou do outro. Por isso ela é **robusta**: você pode trocar o maior valor por
um trilhão que ela nem pisca.

Isso é qualidade ou defeito? **Depende da pergunta.**

- "Quanto ganha uma pessoa típica deste bar?" → **mediana**.
- "Quanto de imposto de renda este bar gera?" → **média** (porque o imposto total é média × pessoas,
  e o Bill Gates realmente paga).

Essa é a primeira lição profissional deste curso: **não existe medida certa, existe medida
adequada à pergunta**. Quem diz "use sempre a mediana porque é mais robusta" está errado
com a mesma intensidade de quem diz "use sempre a média".

### Moda — o mais repetido

O valor que aparece mais vezes. Em `[41, 42, 42, 43, 44]`, a moda é 42.

A moda é a única das três que faz sentido para coisas que **não são número**: a cor mais
vendida, o navegador mais usado, o motivo de cancelamento mais frequente. Para números
contínuos (altura, tempo, preço) ela quase não serve, porque é raro dois valores serem
exatamente iguais — e aí a moda depende de como você agrupou os dados, não dos dados.

---

## 1.3 A medida que quase todo mundo esquece: o quanto os números discordam

Existe uma frase clássica:

> **"Um estatístico morreu afogado atravessando um rio de 1,20 m de profundidade média."**

O rio tem 20 cm na margem e 4 m no meio. A média está correta. A média está mentindo.
O que falta na frase é **quanto a profundidade varia** — e é isso que as medidas de
dispersão dizem.

### Amplitude — a mais ingênua

Maior menos menor. No rio: 4,00 − 0,20 = 3,80 m. Simples, e quase sempre ruim: ela depende
**apenas dos dois valores mais extremos**, ou seja, exatamente dos dois números em que você
menos confia. E ela cresce sozinha quanto mais dados você coleta (com mais medições, mais
chance de pegar um valor extremo), o que é péssimo: uma medida que muda de valor só porque
você mediu mais não está descrevendo o rio, está descrevendo o seu esforço.

### Desvio padrão — a distância típica até a média

Esta é a medida de dispersão que o mundo adotou. A ideia, em português:

1. Calcule a média.
2. Veja **o quanto cada número está longe da média** (isso é o *desvio* de cada um).
3. Tire uma espécie de média desses afastamentos.
4. O resultado é o **desvio padrão**: *a distância típica entre um número qualquer e a média*.

Exemplo com as notas de duas turmas, ambas com média 6,0:

```
Turma A:  6  6  6  6  6      →  ninguém se afasta da média  → desvio padrão = 0
Turma B:  1  3  6  9 11      →  todos se afastam muito      → desvio padrão ≈ 4
```

Mesma média, realidades opostas. Dizer só "média 6" descreve as duas turmas do mesmo jeito,
e isso é uma descrição falsa. **Média sem dispersão é meia informação — e a metade que falta
costuma ser a que decide.**

> **Por que "padrão"?** É tradução de *standard deviation*, nome dado por Karl Pearson em
> 1894. "Padrão" aqui quer dizer *usual, de referência* — o desvio que serve de régua —,
> não "obrigatório". A história completa está em [11-historia.md](11-historia.md).

Um detalhe que fica para depois, mas convém já plantar: no passo 3 não se tira a média
simples dos afastamentos — antes eles são **elevados ao quadrado**, tira-se a média disso, e
no fim se aplica a raiz quadrada. Por que essa volta toda? Há três motivos, um deles
histórico e discutível. Estão em [13-medidas-de-dispersao.md](13-medidas-de-dispersao.md).
Por ora basta: *desvio padrão = afastamento típico em relação à média, na mesma unidade dos
dados*. Se as alturas estão em metros, o desvio padrão está em metros.

### A regra prática que vale a pena decorar hoje

Quando os dados têm um formato comum (o "sino", explicado adiante):

- cerca de **68%** dos valores caem a menos de **1 desvio padrão** da média;
- cerca de **95%** caem a menos de **2 desvios padrão**;
- cerca de **99,7%** caem a menos de **3 desvios padrão**.

Então "média 1,70 m com desvio padrão 0,08 m" significa, na prática: *a maioria (2 em cada 3)
está entre 1,62 m e 1,78 m; quase todo mundo (19 em 20) entre 1,54 m e 1,86 m*.
Agora sim você descreveu a turma.

⚠️ Essa regra **só vale para o formato de sino**. Para salários, tempos de resposta de um
site, tamanho de cidades e quase tudo que tem cauda longa, ela erra feio — e erra sempre para
o mesmo lado, subestimando os extremos. Isso é o assunto de
[14-forma-e-distribuicoes.md](14-forma-e-distribuicoes.md) e de
[75-armadilhas.md](75-armadilhas.md).

---

## 1.4 "Erro" não quer dizer que alguém errou

Esta é a confusão de vocabulário mais cara da estatística, e vale desfazê-la logo.

No dia a dia, "erro" é sinônimo de engano: alguém fez alguma coisa errada.
Em estatística, **erro é a distância entre o que você mediu e o que é verdade** — e essa
distância existe mesmo quando todo mundo fez tudo certo.

> Você pesa um saco de arroz cinco vezes na mesma balança:
> 1,002 · 0,998 · 1,001 · 0,999 · 1,000 kg.
> Ninguém errou nada. Mesmo assim os cinco números são diferentes. Essa variação é o **erro**.

Existem **dois tipos**, e confundi-los é o que produz desastre:

| | O que é | Analogia do tiro ao alvo | O que resolve |
|---|---|---|---|
| **Erro aleatório** | varia a cada medição, ora para mais, ora para menos | tiros espalhados **em volta** do centro | **medir mais vezes** — os desvios se cancelam |
| **Erro sistemático** (viés) | erra sempre para o mesmo lado | tiros agrupadinhos, mas **fora** do centro | medir mais vezes **não resolve nada**; só calibrar o instrumento |

```
   PRECISO e EXATO        PRECISO, não exato      EXATO, não preciso
   (pouco aleatório,      (pouco aleatório,       (muito aleatório,
    pouco viés)            muito viés)             pouco viés)

      ┌───────┐              ┌───────┐              ┌───────┐
      │   ●●  │              │       │ ●●           │  ●    │
      │  ●◎●  │              │   ◎   │●●●           │ ◎   ● │
      │   ●   │              │       │              │●   ●  │
      └───────┘              └───────┘              └───────┘
```

Se a sua balança está descalibrada 200 g para cima, pesar o arroz mil vezes vai lhe dar uma
resposta **muito precisa e completamente errada**. Nenhuma quantidade de estatística conserta
um viés: dados enviesados produzem contas enviesadas com uma casa decimal a mais.
Essa é a origem de mais desastres analíticos do que qualquer erro de fórmula.

### E a "margem de erro" da pesquisa eleitoral?

Você já ouviu: *"o candidato tem 42%, com margem de erro de 2 pontos, para mais ou para menos"*.

O que isso quer dizer, em português honesto:

> "Perguntamos a 2.000 pessoas, não aos 150 milhões de eleitores. Se repetíssemos essa mesma
> pesquisa muitas vezes, sorteando 2.000 pessoas diferentes a cada vez, a maior parte dos
> resultados cairia entre 40% e 44%. Estamos apostando que a verdade está nessa faixa."

Repare: **o erro não vem de erro de conta. Vem de você ter olhado só uma parte.**
Se você perguntasse a *todos* os eleitores, não haveria margem de erro (haveria outros
problemas — quem mente, quem não atende — mas não esse).

Daí sai o fato mais contraintuitivo, e mais útil, de todo este curso:

> **Para dobrar a precisão, é preciso quadruplicar a amostra.**

Ouvir 2.000 pessoas dá ±2 pontos. Para chegar a ±1 ponto não bastam 4.000: são necessárias
**8.000**. Para ±0,5 ponto, 32.000. É por isso que pesquisas eleitorais quase sempre têm
uns 2.000 entrevistados — depois disso, cada ponto de precisão custa caro demais. O motivo
matemático (a tal raiz quadrada) está em [17-amostragem-lgn-tcl.md](17-amostragem-lgn-tcl.md);
o significado prático, em [15-erro-e-incerteza.md](15-erro-e-incerteza.md).

E o outro fato que quase ninguém sabe: **essa margem quase não depende do tamanho da
população**. Uma amostra de 2.000 pessoas mede o Brasil (215 milhões) com a mesma precisão
com que mede a Bélgica (11 milhões). Parece impossível, e não é: a prova está no arquivo 17.
A analogia é a sopa — para saber se está salgada, você mexe bem e prova **uma colher**, e o
tamanho da panela não muda o tamanho da colher necessária. O que muda tudo é **mexer bem**
(a amostra ser realmente aleatória). Uma colher tirada só da superfície engana igual, seja a
panela grande ou pequena.

---

## 1.5 As cinco ideias que sustentam o campo inteiro

Se você parar a leitura aqui, leve estas cinco:

1. **Resumir é jogar informação fora de propósito.** A pergunta é sempre *o que se perdeu*.
2. **Posição sem dispersão é meia informação.** "Média 6" não descreve nada sozinho.
3. **Nenhuma medida é a correta; cada uma responde a uma pergunta diferente.**
   Média para totais e balanços; mediana para "o caso típico"; moda para categorias.
4. **Erro não é engano.** É a distância inevitável entre a amostra e a verdade — e ele se
   divide em aleatório (mais dados resolvem) e sistemático (mais dados pioram a ilusão).
5. **Quase todo número que você vê é uma estimativa.** "42%" nunca é 42%; é "42% mais ou menos
   alguma coisa". Um número sem sua incerteza é uma opinião com aparência de fato.

---

## 1.6 Onde essas medidas aparecem na sua vida, hoje

| Situação | Medida em jogo | Pegadinha |
|---|---|---|
| "Renda média do brasileiro" no jornal | média | a renda é assimétrica; a **mediana** é bem menor e descreve melhor a maioria |
| Tempo de entrega do aplicativo | mediana e **percentil 95** | a média esconde os 5% de entregas horríveis, que são as que geram reclamação |
| "Seu plano tem 99,9% de disponibilidade" | proporção | 0,1% de um mês = 43 minutos fora do ar |
| Nota do produto: 4,7 estrelas | média de notas | 4,7 com 6 avaliações ≠ 4,7 com 6.000; falta o **erro** |
| Resultado do seu exame de sangue | intervalo de referência | o "normal" é a faixa dos 95% centrais de gente saudável — 1 em 20 saudáveis cai fora **por definição** |
| Inflação do mês | média ponderada | o peso de cada item é o da cesta média, que provavelmente não é a sua |
| Velocidade média do trajeto | média harmônica | tirar a média simples de duas velocidades dá resultado errado (ver [12](12-medidas-de-posicao.md)) |

O caso do exame de sangue merece um segundo de atenção, porque ele mostra a estatística
mordendo a vida real: se você faz um painel com 20 exames e está perfeitamente saudável,
a chance de **pelo menos um** deles vir "alterado" é de cerca de 64%. Não é erro do
laboratório. É o preço de olhar para 20 coisas ao mesmo tempo, cada uma com 5% de chance de
falso alarme. Isso se chama **problema das comparações múltiplas** e está em
[18-inferencia-p-e-ic.md](18-inferencia-p-e-ic.md).

---

## 1.7 O que este curso vai fazer com você

Do jeito que dá para conferir:

- No arquivo [04-como-comecar.md](04-como-comecar.md) você calcula tudo isso **hoje**, em 15
  minutos, sem instalar nada além do que já vem no seu computador.
- No [07-projeto-modelo/](07-projeto-modelo/README.md) você roda um programa que lê uma
  planilha e produz um relatório estatístico **honesto** — que avisa quando a média não
  deveria ser usada.
- Do arquivo 10 em diante, cada medida é desmontada até o osso: de onde vem a fórmula, o que
  ela minimiza, quando ela quebra, e o que os profissionais usam no lugar quando ela quebra.

---

## Autoteste

Responda antes de seguir. As respostas estão logo abaixo — não olhe antes.

1. Num bairro, a renda **média** é R$ 8.000 e a **mediana** é R$ 2.500. O que isso diz sobre
   o bairro? Qual das duas você usaria numa reportagem sobre "quanto ganha o morador típico"?
2. Duas cidades têm temperatura média anual de 20 °C. Uma tem desvio padrão de 2 °C, a outra
   de 12 °C. Descreva com palavras como é morar em cada uma.
3. Uma balança de farmácia marca sempre 300 g a mais. Pesar-se 50 vezes e tirar a média
   resolve o problema? Por quê?
4. Uma pesquisa com 1.000 pessoas tem margem de erro de ±3 pontos. Quantas pessoas seriam
   necessárias para chegar a ±1,5 ponto?
5. Por que a amplitude (maior − menor) é uma medida de dispersão ruim?
6. Seu chefe diz: "o tempo médio de resposta do site é 200 ms, está ótimo". Que pergunta você
   faz antes de concordar?
7. Cite uma situação em que a **média** é claramente a medida certa e a mediana seria errada.

<details>
<summary>Respostas</summary>

1. Que a renda é **muito assimétrica**: poucos moradores muito ricos puxam a média para cima,
   enquanto metade do bairro ganha até R$ 2.500. Para "morador típico", **mediana**.
   (Média muito maior que a mediana é o sinal clássico de cauda longa à direita.)
2. Com desvio padrão 2 °C, o ano inteiro é morno e previsível, quase sempre entre 16 e 24 °C.
   Com 12 °C, há verões de 45 °C e invernos abaixo de zero — mesma média, outra vida.
3. **Não.** É erro sistemático (viés): a média de 50 pesagens converge para "peso + 300 g",
   com muita precisão e nenhuma exatidão. Só calibrar resolve.
4. **4.000.** Dobrar a precisão exige quadruplicar a amostra.
5. Porque usa só os dois valores extremos — justamente os menos confiáveis — e cresce
   sistematicamente à medida que você coleta mais dados, descrevendo o seu esforço em vez
   do fenômeno.
6. "Média de quê — e qual é o **percentil 95**?" A média esconde a cauda; o usuário que
   espera 4 segundos é o que reclama, cancela e escreve no Twitter.
7. Qualquer situação em que o **total** importa: folha de pagamento (média × nº de
   funcionários = custo total), consumo médio de energia por casa (× nº de casas = carga da
   rede), ticket médio (× nº de vendas = faturamento). A mediana não tem essa propriedade.

</details>

---

**Próximo:** [02-pre-requisitos.md](02-pre-requisitos.md) — o que você precisa saber e ter
antes de continuar, com tempos honestos. Se quiser pular direto para a prática:
[04-como-comecar.md](04-como-comecar.md).
