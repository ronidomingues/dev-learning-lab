# 11 · História — como o campo surgiu e por que ele tem essa forma

`Nível: iniciante → intermediário` · `Atualizado em: 14/08/2026`

História aqui não é ornamento. Metade das decisões estranhas do campo — por que
44,1 kHz e não 40, por que a FFT explodiu em 1965 e não em 1805, por que
"engenharia elétrica" domina um assunto que é matemática — só faz sentido com o
contexto. E entender por que uma escolha foi feita é o que permite saber quando
ela deixou de valer.

---

## Linha do tempo

```
1807 ┃ Fourier apresenta as séries à Académie. É REJEITADO.
1822 ┃ Théorie analytique de la chaleur — publicado enfim
1898 ┃ Michelson constrói um analisador harmônico mecânico (80 engrenagens)
1915 ┃ Whittaker: teoria da interpolação cardinal
1924 ┃ Nyquist (Bell Labs): velocidade máxima de telegrafia numa banda
1928 ┃ Nyquist e Hartley formalizam o limite de banda × taxa
1933 ┃ Kotelnikov (URSS) enuncia o teorema da amostragem — ignorado no Ocidente
1940 ┃ 2ª Guerra: radar, sonar e criptografia bancam o campo
1942 ┃ Wiener: filtragem ótima de séries temporais (relatório sigiloso)
1948 ┃ Shannon: "A Mathematical Theory of Communication" — nasce a teoria da informação
1948 ┃ Transistor, nos mesmos Bell Labs
1949 ┃ Shannon publica o teorema da amostragem na forma canônica
1960 ┃ Kalman: o filtro recursivo de estado. Widrow e Hoff: o LMS
1965 ┃ Cooley & Tukey publicam a FFT ← O DIVISOR DE ÁGUAS
1969 ┃ Kaiser, Rader, Gold: projeto sistemático de filtros digitais
1975 ┃ Oppenheim & Schafer, "Digital Signal Processing" — o campo vira disciplina
1978 ┃ Speak & Spell da TI: primeiro DSP em produto de consumo em massa
1979 ┃ Intel 2920, o primeiro "processador de sinais" em chip
1982 ┃ CD de áudio (Sony/Philips): 44,1 kHz, 16 bits, no bolso de todo mundo
1983 ┃ TI TMS32010: o DSP que definiu a arquitetura por 20 anos
1987 ┃ Daubechies: wavelets ortogonais de suporte compacto
1993 ┃ MP3 padronizado (ISO/MPEG-1 Layer III)
1993 ┃ Berrou: códigos turbo chegam perto do limite de Shannon
1999 ┃ Wi-Fi 802.11a: OFDM vira infraestrutura civil
2006 ┃ Compressive sensing (Candès, Romberg, Tao, Donoho)
2012 ┃ AlexNet: aprendizado profundo começa a comer o pré-processamento
2016 ┃ WaveNet: rede neural gera forma de onda amostra a amostra
2020 ┃ DDSP (Google): DSP diferenciável — o clássico volta, agora treinável
2026 ┃ Codecs neurais e tokenização de áudio dominam a fronteira
```

---

## 1822 · Fourier, e a ideia que foi rejeitada

Joseph Fourier estudava **condução de calor**, não sinais. Para resolver a equação
do calor numa barra, propôs escrever a distribuição inicial de temperatura como
soma de senos e cossenos.

A Académie des Sciences rejeitou o trabalho em 1807. Lagrange, um dos avaliadores,
não aceitou que uma soma de funções contínuas e suaves pudesse representar uma
função com **quinas** — e ele estava parcialmente certo: a convergência nos pontos
de descontinuidade tem uma sutileza que só foi entendida décadas depois, e que hoje
chamamos de **fenômeno de Gibbs**. A série converge, mas não uniformemente: perto
do salto sobra sempre um sobressinal de ~9 %, que não some por mais termos que você
some.

Fourier publicou em 1822, na *Théorie analytique de la chaleur*. Cento e cinquenta
anos depois, o overshoot de Gibbs continua aparecendo — literalmente, na tela — na
borda de todo filtro FIR projetado por truncamento. Você vai vê-lo em
[`18-filtros-fir.md`](18-filtros-fir.md).

**Lição que se repete no campo:** o objeto matemático nasceu de um problema físico
concreto (calor), e só virou ferramenta geral muito depois.

---

## 1924–1949 · Nyquist, Kotelnikov e Shannon: quantas amostras bastam?

**Harry Nyquist** (Bell Labs, 1924 e 1928) estava resolvendo um problema comercial:
quantos pulsos de telégrafo cabem por segundo num cabo de banda limitada? Achou o
limite de 2B símbolos por segundo numa banda B.

**Vladimir Kotelnikov** (URSS, 1933) enunciou o teorema da amostragem em forma
completa — e ficou desconhecido no Ocidente por décadas, por barreira de língua e
de Guerra Fria. Na Rússia o teorema tem o nome dele. Este é um exemplo bom de como
o crédito científico depende de geopolítica.

**Claude Shannon** (1948–1949) deu a forma canônica e, mais importante, o encaixou
numa teoria completa da comunicação. O artigo de 1948 é, na minha opinião
profissional, o artigo de engenharia mais importante do século XX: ele criou de uma
vez o conceito de bit, a entropia de fonte, a capacidade de canal e o limite do que
é possível transmitir.

**Por que 44,1 kHz no CD, e não 40?** Ouvido humano até ~20 kHz ⇒ Nyquist pede
> 40 kHz. Os 4,1 kHz extras são margem para o filtro anti-aliasing analógico, que
não é ideal e precisa de espaço de transição. E por que exatamente 44,1? Porque os
gravadores digitais do fim dos anos 1970 armazenavam áudio em **fita de vídeo**, e
44 100 = 3 amostras × 245 linhas úteis × 60 campos/s (padrão NTSC) — e o mesmo
número também fecha com 3 × 294 × 50 no PAL. Uma das constantes mais citadas do
áudio digital é, na origem, uma **restrição de compatibilidade com videocassete**.

É uma parada legítima da regra dos cinco porquês: **decisão histórica documentada**,
não princípio físico.

---

## 1940–1945 · A guerra paga a conta

Radar, sonar e criptoanálise transformaram processamento de sinais em prioridade
militar com dinheiro ilimitado. Dessa era saíram:

- **Filtro casado** (correlação com o pulso conhecido) — o exemplo 8 do
  [`06`](06-exemplos.md) é literalmente isso.
- **Filtro de Wiener** (Norbert Wiener, 1942, num relatório sigiloso apelidado de
  "the yellow peril" pela capa amarela e pela dificuldade) — separação ótima de
  sinal e ruído por critério de erro quadrático médio.
- **Detecção sob ruído** e o vocabulário estatístico que o campo usa até hoje.

**Consequência duradoura:** o campo nasceu falando de *detecção* e *estimação*, não
de *análise*. Por isso a linguagem é de engenheiro elétrico e de estatístico, e não
de matemático puro.

---

## 1965 · Cooley e Tukey, e a mudança de escala

Antes de 1965, calcular a DFT de N pontos custava N² multiplicações complexas.
Para N = 1024: mais de um milhão de operações. Nos computadores da época, minutos —
por espectro. Isso tornava a análise espectral digital **economicamente inviável**
para qualquer coisa contínua.

O algoritmo de Cooley-Tukey derrubou para N·log₂N. Para N = 1024: ~10 000 operações.
**Cem vezes mais rápido.** Para N = 1 milhão, 50 000 vezes.

Três coisas dessa história merecem ser sabidas:

1. **Gauss já tinha feito, em 1805.** Ele usou o mesmo esquema de decomposição para
   interpolar órbitas de asteroides, escreveu em latim num caderno, e o texto só foi
   publicado postumamente em 1866 — sem que ninguém percebesse o que era. Só em 1984
   Heideman, Johnson e Burrus documentaram a prioridade. **Um algoritmo pode existir
   160 anos antes de o mundo ter o problema que o torna valioso.**
2. **O contexto era político.** Tukey participava de um comitê científico ligado à
   detecção de testes nucleares soviéticos por sismógrafos — o problema pedia
   análise espectral de muitos dados sísmicos. A urgência criou a demanda.
3. **A publicação foi deliberadamente aberta.** IBM decidiu não patentear, e o
   algoritmo se espalhou em meses. Contrafactual interessante: se tivesse sido
   patenteado, a história do processamento digital teria atrasado uma década.

**Sem a FFT não existiriam:** MP3, JPEG, Wi-Fi, 4G/5G, ressonância magnética,
reconhecimento de voz. Todos passam por uma transformada rápida em algum ponto.

---

## 1975–1985 · O campo vira disciplina, e depois vira chip

O livro *Digital Signal Processing* de Oppenheim e Schafer (1975) — e depois
*Discrete-Time Signal Processing* (1989) — deu ao campo currículo, notação e
fronteira. Junto com Rabiner & Gold (1975), fixou o vocabulário que
[`05-manual-de-uso.md`](05-manual-de-uso.md) descreve. Praticamente toda a notação
que você vê hoje vem daí.

Em paralelo, o silício: o **Speak & Spell** da Texas Instruments (1978) pôs síntese
de voz por LPC num brinquedo de US$ 50 — foi o primeiro DSP de consumo em massa. O
**Intel 2920** (1979) e o **TMS32010** (1983) criaram a categoria "processador de
sinais": arquitetura Harvard, multiplicador-acumulador em um ciclo, endereçamento
circular. Todo DSP moderno ainda tem esses três traços.

**Por que uma arquitetura separada?** Porque a operação dominante de DSP é
`acc += coef[i] * x[i]` num laço apertado. Uma CPU de propósito geral da época
gastava vários ciclos nisso; um MAC dedicado gastava um. É otimização para **uma
única expressão**, e ela sustentou uma indústria inteira por 30 anos.

---

## 1982–1999 · Do laboratório para o bolso

- **CD (1982):** 44,1 kHz, 16 bits, correção de erro Reed-Solomon. Primeira vez que
  o público comprou processamento de sinais sem saber.
- **Modem (anos 1980–90):** equalização adaptativa, codificação treliça. O ruído
  característico da discagem é literalmente o handshake de dois DSPs negociando a
  resposta do canal.
- **MP3 (1993):** banco de filtros + MDCT + **modelo psicoacústico**. A inovação não
  foi matemática, foi **perceptual**: jogar fora o que o ouvido não ouviria. Reduziu
  12× o tamanho e mudou a indústria fonográfica antes de a indústria perceber.
- **Celular digital (GSM, anos 1990):** codec de voz a 13 kbit/s, equalização,
  correção de erro. Colocou um DSP no bolso de bilhões.
- **Wi-Fi 802.11a (1999) e depois LTE:** **OFDM** — dividir a banda em centenas de
  subportadoras ortogonais, cada uma com canal quase plano. OFDM é, na prática, uma
  IFFT no transmissor e uma FFT no receptor. **O Wi-Fi é uma FFT com antena.**

---

## 2006 · Compressive sensing: um susto na intuição de Nyquist

Candès, Romberg, Tao e Donoho mostraram que, **se o sinal for esparso em alguma
base**, é possível reconstruí-lo com muito menos amostras que Nyquist exige — desde
que as amostras sejam tomadas de forma incoerente (aleatória).

Não é violação do teorema: Nyquist responde "quantas amostras para reconstruir
**qualquer** sinal de banda B"; compressive sensing responde "quantas para
reconstruir sinais **esparsos**". Hipótese diferente, resposta diferente.

Impacto real: ressonância magnética mais rápida (menos tempo com o paciente dentro
do tubo — hoje em uso clínico), câmeras de pixel único, radar. Impacto conceitual:
mostrou que a pergunta "quantas amostras?" depende do que você sabe *a priori*
sobre o sinal. Foi a maior sacudida na intuição do campo em cinquenta anos.

---

## 2012–2026 · O aprendizado profundo come a cadeia (mas não toda)

A partir de 2012, redes neurais passaram a superar as cadeias de processamento
feitas à mão em tarefas de reconhecimento. O padrão se repetiu em voz, imagem e
biomédica:

| Antes | Depois |
|---|---|
| filtros à mão + MFCC + HMM | espectrograma → rede neural |
| vocoder paramétrico | WaveNet, HiFi-GAN, codecs neurais |
| detector projetado | modelo treinado ponta a ponta |

**O que morreu:** grande parte da **extração de características** feita à mão.
Ninguém mais ajusta 40 parâmetros de um banco de filtros de MFCC para melhorar 1 %
de acurácia.

**O que não morreu, e não vai morrer:**

- **A aquisição.** Nyquist, anti-aliasing, quantização e dither continuam sendo
  física e matemática. Nenhuma rede conserta dado amostrado errado.
- **A representação de entrada.** Quase toda rede de áudio come espectrograma ou
  mel-espectrograma — ou seja, alguém fez STFT antes.
- **Tempo real e baixa potência.** Um filtro IIR de 4ª ordem cabe em 12 multiplicações
  por amostra. Nenhuma rede compete com isso num fone de ouvido.
- **A explicação.** Quando o sistema falha, quem entende de sinal descobre por quê.
- **A própria estrutura das redes.** Uma camada convolucional **é** um banco de
  filtros FIR. *Stride* **é** decimação. *Pooling* **é** filtro passa-baixa seguido
  de subamostragem. O vocabulário mudou; a matemática não.

E desde ~2020 o pêndulo voltou um pouco: **DDSP** (DSP diferenciável) põe
osciladores, filtros e envoltórias *dentro* da rede como componentes treináveis.
Você ganha o melhor dos dois: a eficiência e a interpretabilidade do modelo físico,
com o ajuste automático do aprendizado. Detalhes em
[`29`](29-dsp-e-aprendizado-de-maquina.md) e [`65`](65-estado-da-arte.md).

---

## Padrões que se repetem na história deste campo

1. **A matemática chega décadas antes da aplicação.** Fourier em 1822, uso
   massivo em 1965. Wavelets nos anos 1980, JPEG2000 em 2000. Compressive sensing
   em 2006, ressonância clínica nos anos 2010.
2. **Guerra e comércio pagam a conta, e determinam o vocabulário.** O campo fala
   "detecção", "canal", "ruído" porque nasceu em telegrafia, radar e telefonia.
3. **A restrição de hardware vira convenção permanente.** 44,1 kHz existe por causa
   de videocassete. Potências de 2 em FFT existem por causa do radix-2. Ambas
   sobrevivem ao motivo que as criou.
4. **Redescobertas são a norma.** Gauss/Cooley-Tukey, Kotelnikov/Shannon,
   Whittaker/Shannon. Quem publica em inglês, na hora certa, leva o nome.
5. **Nada é substituído; tudo é absorvido.** Analógico não morreu (todo A/D tem um
   filtro analógico na frente). DSP clássico não morreu com a IA — virou camada
   dentro dela.

---

## Autoteste

1. Por que a Académie rejeitou Fourier em 1807, e qual fenômeno dá alguma razão ao
   crítico?
2. De onde vem, exatamente, o número 44 100?
3. Por que a FFT de 1965 mudou o campo se Gauss já a conhecia em 1805?
4. Que problema geopolítico concreto motivou o trabalho de Tukey?
5. Qual foi a inovação central do MP3 — e por que ela não é matemática?
6. Compressive sensing viola Nyquist? Explique a diferença de hipótese.
7. Cite três coisas do DSP clássico que o aprendizado profundo não substituiu.
8. Qual é a relação entre uma camada convolucional e um filtro FIR?

---

## Fontes

- Fourier, J. *Théorie analytique de la chaleur*, 1822 (domínio público).
- Shannon, C. E. "A Mathematical Theory of Communication", *Bell System Technical
  Journal*, 1948; "Communication in the Presence of Noise", *Proc. IRE*, 1949.
- Nyquist, H. "Certain Topics in Telegraph Transmission Theory", *Trans. AIEE*, 1928.
- Cooley, J. W.; Tukey, J. W. "An Algorithm for the Machine Calculation of Complex
  Fourier Series", *Mathematics of Computation* 19(90), 1965.
- Heideman, M. T.; Johnson, D. H.; Burrus, C. S. "Gauss and the History of the Fast
  Fourier Transform", *IEEE ASSP Magazine*, 1984.
- Oppenheim, A. V.; Schafer, R. W. *Digital Signal Processing*, Prentice Hall, 1975.
- Candès, E.; Romberg, J.; Tao, T. *IEEE Trans. Information Theory*, 2006;
  Donoho, D. "Compressed Sensing", idem, 2006.
