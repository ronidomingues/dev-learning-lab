# 26 · Comunicações e rádio definido por software

`Nível: avançado` · `Atualizado em: 19/08/2026`

Comunicação digital é a maior consumidora de processamento de sinais do planeta.
Todo celular, Wi-Fi, satélite e cabo submarino é uma cadeia de DSP. E o
**rádio definido por software** (SDR) transformou isso em algo que você pode
estudar com uma dongle de US$ 30 e um laptop.

O projeto [`08-projeto-espacial/`](08-projeto-espacial/README.md) já implementa,
com física real, a parte de aquisição por código PN e rastreamento Doppler.

---

## 1 · A representação I/Q — por que tudo é complexo

Um sinal de rádio real ocupa uma faixa em torno de uma portadora f_c. Trazê-lo
para banda base multiplicando por cos(2πf_c t) **não basta**: perde-se a
informação de qual lado da portadora estava cada componente.

A solução: multiplicar por cos **e** por −sen, obtendo duas trilhas:

```
   I[n] = componente "em fase"       (in-phase)
   Q[n] = componente "em quadratura" (quadrature)

   sinal complexo:  z[n] = I[n] + j·Q[n]
```

**O que isso compra:**

- O espectro deixa de ser simétrico: frequência positiva ≠ negativa, e você sabe
  de que lado da portadora está cada coisa.
- A taxa de amostragem necessária é a **largura de banda**, não o dobro dela
  (amostragem complexa).
- Modulação e demodulação viram multiplicação por e^{jθ} — rotação no plano
  complexo ([`12 §3`](12-matematica-do-zero.md)).

**Todo SDR entrega I/Q.** Se você entendeu por que a exponencial complexa é
central em DSP, entendeu por que o rádio moderno é complexo por natureza.

---

## 2 · Modulações

### Analógicas (o que veio antes)

| Modulação | Ideia | DSP para demodular |
|---|---|---|
| **AM** | amplitude ∝ mensagem | `np.abs(z)` — a envoltória |
| **FM** | frequência ∝ mensagem | `np.diff(np.unwrap(np.angle(z)))` |
| **SSB** | AM sem uma banda lateral | transformada de Hilbert |

Demodular FM comercial de uma dongle RTL-SDR são literalmente duas linhas de
NumPy sobre o I/Q, mais decimação. É o "hello world" do SDR.

### Digitais

| Esquema | Bits/símbolo | Onde |
|---|---|---|
| **BPSK** | 1 | espaço profundo, GPS — o mais robusto |
| **QPSK** | 2 | satélite, DVB, LTE em borda de célula |
| **16/64/256-QAM** | 4/6/8 | Wi-Fi, LTE, 5G, cabo — exige SNR alta |
| **GMSK** | 1 | GSM — envoltória constante, amplificador eficiente |
| **OFDM** | (agregado) | Wi-Fi, LTE, 5G, DVB-T — ver §4 |

**O compromisso central:** mais bits por símbolo exige mais SNR. Cada salto de
constelação (QPSK → 16QAM → 64QAM) custa aproximadamente **6 dB** de SNR para
manter a mesma taxa de erro. É por isso que a taxa do seu Wi-Fi cai quando você
se afasta do roteador: o modem **desce** de constelação para sobreviver.

---

## 3 · A cadeia completa de um receptor

```
antena → LNA → mistura → filtro → ADC → [ DSP: ]
                                          decimação (multitaxa, cap. 21)
                                          AGC
                                          sincronismo de frequência (Doppler/offset)
                                          sincronismo de tempo (símbolo)
                                          equalização (canal, cap. 23)
                                          demapeamento (símbolo → bits moles)
                                          decodificação (correção de erro)
                                        → bits
```

**Onde o esforço realmente vai** — e isto surpreende quem chega de fora: a
demodulação em si é trivial. **Sincronismo e equalização consomem a maior parte
do código e dos bugs.** Um receptor que "não funciona" quase nunca falha na
matemática da modulação; falha em travar em frequência, em tempo ou em fase.

### Formatação de pulso e ISI

Transmitir pulsos retangulares ocupa banda infinita. Usa-se o **cosseno levantado
com raiz** (RRC), dividido entre transmissor e receptor, de modo que a cascata
satisfaça o **critério de Nyquist para ISI zero**: o pulso resultante vale 1 no
instante de decisão e **exatamente 0** em todos os outros instantes de símbolo.

O parâmetro *roll-off* β controla o excesso de banda: β=0 é o mínimo teórico
(banda = taxa de símbolo) e exige sincronismo perfeito; β=0,35 é típico e
perdoa erro de temporização.

**O diagrama de olho** é a ferramenta de diagnóstico: sobreponha os símbolos
recebidos. Olho aberto = decisão fácil; olho fechado = ISI, ruído ou sincronismo
ruim. É a forma mais rápida de saber *onde* está o problema.

---

## 4 · OFDM — o Wi-Fi é uma FFT com antena

**O problema:** num canal com múltiplos percursos (eco), a resposta é seletiva em
frequência, e equalizar isso em banda larga é caro.

**A solução:** dividir a banda em centenas de subportadoras estreitas. Cada uma vê
um canal **aproximadamente plano** — e equalizar um canal plano é dividir por um
número complexo.

```
   bits → mapeia em N símbolos QAM → IFFT → prefixo cíclico → transmite
   recebe → remove prefixo → FFT → divide por H[k] → demapeia
```

**Duas ideias geniais:**

1. **A IFFT gera N subportadoras ortogonais de uma vez**, em O(N log N). Fazer isso
   com N osciladores seria inviável. A ortogonalidade é a das exponenciais
   complexas ([`12 §6`](12-matematica-do-zero.md)).
2. **O prefixo cíclico** copia o fim do símbolo para o começo. Isso transforma a
   convolução **linear** do canal em convolução **circular** — e convolução
   circular na frequência é multiplicação ponto a ponto
   ([`16 §5`](16-dft-e-fft.md)). Assim a equalização vira uma divisão por bin.

O "artefato" da convolução circular, que no capítulo 16 é o erro a evitar, aqui é
**explorado de propósito**. É o exemplo mais elegante do campo.

**O preço do OFDM:** PAPR alto (a soma de N senoides tem picos grandes, exigindo
amplificador linear e caro) e sensibilidade a erro de frequência (que destrói a
ortogonalidade). Daí o 5G usar SC-FDMA no *uplink*, onde a eficiência do
amplificador do celular importa mais.

---

## 5 · Espalhamento espectral e códigos

Já detalhado, com física e código executável, no
[`08-projeto-espacial/`](08-projeto-espacial/README.md):

- sequências-m por LFSR, com as propriedades de Golomb verificadas numericamente;
- ganho de processamento 10·log₁₀(N) — 30,1 dB para o código C/A do GPS;
- aquisição 2-D em atraso × Doppler;
- integração coerente × não coerente.

**Onde se usa:** GPS/GNSS, CDMA, comunicação de espaço profundo, e — no caso do
GPS — a razão de o sinal funcionar 20 dB abaixo do ruído térmico.

---

## 6 · Correção de erro: chegando ao limite de Shannon

| Código | Ano | Distância do limite |
|---|---|---|
| Hamming, BCH | 1950s | longe |
| Reed-Solomon | 1960 | bom para erros em rajada (CD, DVD, QR code) |
| Convolucional + Viterbi | 1967 | padrão espacial por décadas |
| **Turbo** | 1993 | ~0,5 dB do limite |
| **LDPC** | 1962/redescoberto 1996 | ~0,1 dB; Wi-Fi, 5G, DVB-S2 |
| **Polar** | 2008 | primeiro com prova de atingir a capacidade; canais de controle do 5G |

**A história do LDPC merece nota:** inventado por Gallager em 1962, foi **esquecido
por 30 anos** porque a computação da época não dava conta da decodificação
iterativa. Redescoberto em 1996, hoje está em todo lugar. É um caso claro do
padrão de [`11-historia.md`](11-historia.md): a matemática chega décadas antes de
o hardware a tornar viável.

**O limite de Shannon** (1948) diz a capacidade máxima:

```
C = B·log₂(1 + SNR)     bits/s
```

Turbo e LDPC chegaram a fração de dB dele. Em termos práticos: **o problema da
correção de erro está essencialmente resolvido**, e o esforço migrou para MIMO,
uso do espectro e eficiência energética.

---

## 7 · SDR na prática

| Hardware | Preço (ago/2026) | Faixa | Nota |
|---|---|---|---|
| **RTL-SDR Blog V4** | US$ 30–40 | 500 kHz – 1,7 GHz | só recepção, 8 bits. ⚠️ **produção encerrada** — o chip R828D acabou |
| **ADALM-PLUTO** | US$ 100–250 | 325 MHz – 3,8 GHz | TX **e** RX; da Analog Devices, forte em ensino |
| **HackRF One** | ~US$ 340 | 1 MHz – 6 GHz | TX/RX, banda larga, 8 bits |
| **USRP (Ettus)** | US$ 1 000+ | vários | padrão de pesquisa |

Preços consultados em 14/08/2026; ver [`80-custos-e-licencas.md`](80-custos-e-licencas.md).

**Software:** GNU Radio 3.10.x estável (4.0 em RC desde março de 2026),
gr-satellites, SDR++, GQRX. Instalação em [`03-instalacao.md`](03-instalacao.md).

**Projetos de primeira semana:**
1. Demodular FM comercial (duas linhas de NumPy sobre I/Q).
2. Decodificar **ADS-B** — a telemetria que os aviões transmitem em 1090 MHz.
3. Receber imagens de satélites meteorológicos **NOAA APT** com antena caseira.
4. Decodificar pacotes **AIS** de navios.

⚠️ **Legalidade:** receber é livre em quase todo lugar. **Transmitir exige
licença** — no Brasil, autorização da Anatel, e a faixa de radioamador exige
licença de operador. RTL-SDR só recebe, o que evita o problema por construção.

---

## Autoteste

1. Por que a representação I/Q é complexa, e o que se perderia sem o Q?
2. Quanto de SNR a mais custa passar de QPSK para 16-QAM, aproximadamente?
3. Onde vai a maior parte do esforço de projeto de um receptor?
4. O que o critério de Nyquist para ISI zero garante, e como se obtém?
5. Explique as duas ideias centrais do OFDM.
6. Por que o prefixo cíclico existe, e que "defeito" da FFT ele explora?
7. Por que o LDPC ficou 30 anos esquecido?
8. Escreva o limite de Shannon e diga o que ele implica hoje.
9. Que hardware SDR você recomendaria para começar, e qual a ressalva atual?
