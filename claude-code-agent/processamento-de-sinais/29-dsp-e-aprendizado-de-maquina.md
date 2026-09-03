# 29 · DSP e aprendizado de máquina — o que foi absorvido e o que não foi

`Nível: avançado` · `Atualizado em: 19/08/2026`

A pergunta que todo mundo faz: *"redes neurais tornaram o DSP obsoleto?"*
A resposta curta é **não** — mas a resposta longa é mais interessante, porque o
campo mudou de forma, e entender **como** vale mais que a resposta binária.

---

## 1 · As redes já eram DSP

Antes de discutir substituição, vale ver a sobreposição. Muitas operações centrais
de redes neurais **são** operações de DSP com outro nome.

| Nome em aprendizado profundo | Nome em DSP | Relação |
|---|---|---|
| Camada **convolucional 1-D** | banco de filtros **FIR** | são a mesma operação. Os pesos **são** os taps |
| Camada convolucional 2-D | filtro 2-D / kernel | idem |
| **Stride** | decimação | idem, sem o filtro anti-aliasing (!) |
| **Pooling** | passa-baixa + subamostragem | média = média móvel |
| **Dilated convolution** | filtro esparso / à trous | vem da literatura de wavelets |
| **Campo receptivo** | comprimento da resposta ao impulso | mesma ideia |
| **Batch norm** | AGC (controle automático de ganho) | normalização de nível |
| **Atenção** | correlação / filtro casado adaptativo | produto interno com pesos |
| **Residual connection** | realimentação direta / all-pass | estrutura de fluxo |
| **SGD** | **LMS** (Widrow-Hoff, 1960) | gradiente estocástico, mesma equação |

**A linha do SGD merece destaque:** a regra de atualização do LMS
([`23 §3`](23-estimacao-e-filtragem-adaptativa.md)) é o gradiente estocástico,
publicado em 1960, trinta anos antes de retropropagação virar mainstream. O campo
de filtragem adaptativa **já treinava filtros com dados** — só que filtros
lineares, com garantias de convergência que as redes não têm.

⚠️ **Sobre stride:** decimar sem filtrar é o `x[::M]` de
[`21 §1`](21-multitaxa-e-bancos-de-filtros.md), com o mesmo aliasing. Isso foi
notado (Zhang, *"Making Convolutional Networks Shift-Invariant Again"*, 2019) e
corrigido acrescentando um passa-baixa antes do stride — o que melhorou robustez
a deslocamento. **Um resultado de aprendizado profundo obtido aplicando o teorema
da amostragem.** É o melhor exemplo de que a teoria clássica ainda paga.

---

## 2 · O que o aprendizado profundo de fato substituiu

**A extração de características feita à mão.** Isso morreu, e não volta.

| Tarefa | Antes (até ~2012) | Hoje |
|---|---|---|
| Reconhecimento de fala | MFCC + HMM + modelo de língua | espectrograma → transformer |
| Detecção de fala (VAD) | energia + zero-crossing + heurística | rede pequena |
| Separação de fontes | ICA, NMF, filtragem espacial | rede treinada (Conv-TasNet e sucessores) |
| Redução de ruído | subtração espectral, Wiener | rede (RNNoise, DeepFilterNet) |
| Reconhecimento de imagem | SIFT/HOG + SVM | CNN |
| Detecção de arritmia | regras sobre morfologia | rede sobre o sinal |

**Por que perdeu:** ajustar 40 parâmetros de um banco de filtros MFCC para ganhar
1 % de acurácia é trabalho artesanal que uma rede faz melhor, com dados.

**O que sobrou dessa transição:** a **entrada** da rede quase sempre continua
sendo um espectrograma ou mel-espectrograma. Ou seja: alguém fez STFT antes.
O DSP virou **camada de entrada**, não desapareceu.

---

## 3 · O que não foi substituído — e não será

### Aquisição

Nyquist, anti-aliasing, quantização, dither, jitter. **Nenhuma rede conserta dado
amostrado errado.** Se você fez aliasing na captura, a informação não existe mais
— e a rede vai aprender confiantemente o padrão errado. Isso é matemática de
contagem de graus de liberdade ([`15`](15-amostragem-e-quantizacao.md)), não
capacidade de modelo.

### Tempo real e baixo consumo

Um biquad são 5 multiplicações por amostra ([`19 §6`](19-filtros-iir.md)). Uma
rede, mesmo pequena, são milhares. Num fone com bateria, num marca-passo ou num
sensor a célula-botão, **não há competição**. É por isso que ANC continua sendo
filtro adaptativo clássico, e que o front-end de todo rádio continua sendo CIC e
FIR ([`28`](28-implementacao-ponto-fixo-e-hardware.md)).

### Garantias

Um Butterworth tem resposta **provada**. Estabilidade **provada**. Comportamento
previsível fora dos dados de treino. Uma rede tem desempenho **medido num
conjunto de teste**, e comportamento desconhecido fora dele.

Em sistemas críticos — aviação, médico, industrial — isso é decisivo, e é
requisito de certificação, não preferência de engenheiro.

### Explicação

Quando o sistema falha, alguém precisa dizer por quê. Quem entende de sinais
olha o espectrograma e diz "isso é aliasing", "isso é vazamento", "isso é o
filtro tocando". Essa capacidade não é substituível por acurácia.

### Interpretação física

DM mede coluna de elétrons. Doppler mede velocidade. Formantes medem trato vocal.
Uma rede pode **prever** essas grandezas melhor; ela não as **define**. A ciência
vive nas grandezas, não na predição.

---

## 4 · A síntese: DSP diferenciável (DDSP)

O desenvolvimento mais interessante dos últimos anos, e o que resolve a falsa
dicotomia.

**A ideia:** colocar os blocos clássicos — osciladores, filtros, envoltórias,
reverberadores — **dentro** da rede, como componentes cujos parâmetros são
treináveis por gradiente.

```
    rede neural  ──►  parâmetros  ──►  [ oscilador harmônico ]
    (aprende o                          [ filtro variante    ]  ──► som
     controle)                          [ reverberador       ]
                                        ↑ blocos de DSP clássico, diferenciáveis
```

**O que se ganha:**

| Vantagem | Por quê |
|---|---|
| **Muito menos dados** | a estrutura física já está embutida; a rede não precisa reaprender o que é uma senoide |
| **Interpretabilidade** | os parâmetros têm significado: f0, amplitude de harmônico, corte do filtro |
| **Controle** | dá para editar o resultado mudando um parâmetro |
| **Eficiência** | o sintetizador é barato; a rede só produz controles |
| **Garantia parcial** | o bloco de DSP continua tendo as propriedades provadas |

**Marcos:** DDSP (Engel et al., Google, 2020) mostrou síntese de timbre com
qualidade alta e dados escassos. Desde então: filtros IIR diferenciáveis,
*allpass* diferenciáveis para estimação de fase, e bibliotecas de processamento
diferenciável no domínio da frequência apresentadas em conferências recentes de
processamento de sinais.

**Minha opinião profissional:** DDSP é a direção certa para problemas em que
existe um modelo físico razoável. Onde não existe (reconhecimento de fala
irrestrito, por exemplo), a rede pura continua ganhando. Não é uma técnica
universal; é a ferramenta certa quando você **sabe alguma coisa** sobre o sinal e
quer que o modelo aproveite esse conhecimento em vez de reaprendê-lo.

---

## 5 · Codecs neurais e tokenização de áudio

O estado da arte em 2026 para geração e compressão de áudio:

```
áudio → [ encoder ] → [ quantizador vetorial ] → tokens discretos
tokens → [ decoder ] → áudio
```

Uma vez que o áudio vira **tokens discretos**, ele pode ser modelado pelas mesmas
arquiteturas que modelam texto — transformers e modelos de língua. Foi essa
unificação que destravou geração de fala e de música de alta qualidade.

**Onde o DSP continua dentro disso:**
- o *encoder* é uma pilha de convoluções, ou seja, **um banco de filtros aprendido**;
- o *downsampling* é decimação multitaxa;
- as perdas de treino são frequentemente **espectrais** (multi-resolution STFT
  loss) — ou seja, comparam espectrogramas, não formas de onda, porque a fase é
  perceptualmente menos importante ([`25 §1`](25-audio-e-fala.md));
- a qualidade é avaliada com métricas perceptuais herdadas da psicoacústica.

Detalhes e referências datadas em [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

## 6 · Como decidir, na prática

| Situação | Escolha |
|---|---|
| A física é conhecida e o modelo fecha | **DSP clássico**. Não treine o que você pode calcular |
| Restrição dura de energia ou latência | **DSP clássico** |
| Precisa de garantia formal / certificação | **DSP clássico** |
| O mapeamento é complexo e há **muitos dados** | rede |
| Há modelo físico **e** variação difícil de modelar | **DDSP / híbrido** |
| Precisa explicar cada decisão | DSP, ou híbrido interpretável |
| Protótipo rápido, dados abundantes, sem restrição | rede |

**A regra que eu daria a alguém começando hoje:** aprenda DSP **primeiro**.
Não porque seja mais importante, mas porque:

1. É a **camada de entrada** de praticamente todo sistema de áudio/sinal com IA —
   você vai precisar dela de qualquer forma;
2. Explica **por que** a rede funciona (convolução = filtro) e por que às vezes
   não funciona (aliasing no stride);
3. Dá o vocabulário para **depurar**, que é onde o tempo de verdade é gasto;
4. Não envelhece. Nyquist é de 1928 e continua exato. A arquitetura de rede da
   moda tem meia-vida de dois anos.

---

## Os cinco porquês: por que redes precisam de espectrograma se poderiam ler a forma de onda?

1. **Por que quase toda rede de áudio recebe espectrograma?** Porque treinar
   direto na forma de onda exige muito mais dados e computação para a mesma
   qualidade.
2. **Por que exige mais?** Porque a rede precisaria **aprender** a fazer análise
   tempo-frequência a partir do zero — descobrir sozinha que decompor em senoides
   é útil.
3. **Por que descobrir isso é difícil?** Porque exige aprender filtros com centenas
   de taps e fases coerentes, um espaço de busca enorme, para reproduzir algo que
   Fourier já dá de graça e exatamente.
4. **Mas redes que leem forma de onda existem (WaveNet, Conv-TasNet). Como?**
   Elas funcionam, e o que aprendem nas primeiras camadas **é um banco de filtros**
   — quando se inspecionam os pesos, aparecem respostas passa-faixa parecidas com
   as de um banco de filtros auditivo. Ou seja: elas redescobrem Fourier.
5. **Então por que dar Fourier de presente?** Porque é conhecimento correto,
   custa zero e libera capacidade do modelo para o que ele realmente precisa
   aprender. **Parada legítima: é um trade-off de viés indutivo** — embutir
   estrutura verdadeira sempre reduz a necessidade de dados. É o mesmo argumento
   que justifica convolução em vez de camada densa para imagens.

---

## Autoteste

1. Cite cinco operações de rede neural que são operações de DSP com outro nome.
2. Qual algoritmo de 1960 é o SGD, e em que área ele nasceu?
3. O que há de errado com stride, do ponto de vista de amostragem?
4. O que o aprendizado profundo de fato substituiu?
5. Cite três coisas que não foram substituídas, com o motivo de cada uma.
6. O que é DDSP e o que exatamente ele ganha?
7. Quando DDSP **não** é a escolha certa?
8. O que as primeiras camadas de uma rede que lê forma de onda acabam aprendendo?
9. Por que aprender DSP antes de aprendizado profundo, se o segundo é o que está
   em alta?
