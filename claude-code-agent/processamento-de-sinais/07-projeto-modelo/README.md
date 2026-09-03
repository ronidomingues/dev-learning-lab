# Projeto-modelo — `sinal`: analisador, afinador e filtrador de áudio

`Nível: intermediário` · `Verificado em: 14/08/2026`
`Base: Python 3.10.12 · NumPy 2.2.6 · SciPy 1.15.3 · Matplotlib 3.10.9 · Ubuntu 22.04`

Um programa pequeno **mas inteiro**: gera um sinal de teste com resposta conhecida,
mede seus níveis, estima a frequência fundamental por três métodos independentes,
diz que nota musical é e quantos cents ela está desafinada, remove zumbido de rede
elétrica com filtros, e desenha forma de onda, espectro e espectrograma.

É o afinador de instrumento que você tem no celular — só que aberto, e com os
números da teoria à mostra em cada passo.

---

## Por que este projeto e não outro

Ele obriga a atravessar, em código que roda, o núcleo do campo:

| Conceito do curso | Onde aparece aqui |
|---|---|
| Amostragem e quantização ([15](../15-amostragem-e-quantizacao.md)) | `io_wav.py` — o int16 virando float, o passo de 2⁻¹⁵ |
| Nyquist e aliasing ([15](../15-amostragem-e-quantizacao.md)) | `geracao.tom()` recusa harmônico acima de taxa/2 |
| Janelamento e vazamento ([20](../20-analise-espectral-e-janelas.md)) | janela Hann em toda análise; `medidas.thd_db` soma uma faixa, não um bin |
| DFT/FFT e resolução ([16](../16-dft-e-fft.md)) | `_tamanho_fft`, zero-padding, interpolação parabólica |
| Autocorrelação e Wiener-Khinchin ([22](../22-ruido-e-processos-estocasticos.md)) | `f0_por_autocorrelacao` calcula ACF pela FFT |
| Filtros FIR por janela ([18](../18-filtros-fir.md)) | `fir_passa_baixa`, atraso de grupo, regra dos 4·fs/Δf |
| Filtros IIR e SOS ([19](../19-filtros-iir.md)) | `sos_passa_alta`, `notch`, fator Q |
| Fase zero × causalidade ([19](../19-filtros-iir.md)) | `filtfilt` vs `sosfilt`, com teste que mede o atraso |
| Tempo-frequência ([24](../24-tempo-frequencia-e-wavelets.md)) | espectrograma com 75 % de sobreposição |

---

## Pré-requisitos

- Python 3.10 ou mais novo (testado em 3.10.12; funciona até 3.14).
- NumPy e SciPy. Matplotlib **só** se você quiser a figura.
- Nada mais: a leitura de WAV usa o módulo `wave` da biblioteca padrão.

Se ainda não tem o ambiente, siga [`03-instalacao.md`](../03-instalacao.md).

---

## Instalar e rodar — comandos exatos

```bash
# 1. entre na pasta do projeto
cd processamento-de-sinais/07-projeto-modelo

# 2. crie e ative um ambiente isolado
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. instale as dependências
pip install -r requirements.txt

# 4. rode a suíte de testes (deve dar 25 OK)
python -m unittest discover -s tests -v
```

Saída esperada da última linha:

```
Ran 25 tests in 0.102s

OK
```

### O ciclo completo, em quatro comandos

```bash
# gera um Lá de 440 Hz com 5 harmônicos, ruído e zumbido de 60 Hz
python -m sinal gerar la.wav --f0 440 --dur 2

# analisa
python -m sinal analisar la.wav

# limpa: notch na rede + passa-alta em 80 Hz
python -m sinal filtrar la.wav limpo.wav --remover-zumbido --passa-alta 80

# desenha
python -m sinal figura la.wav painel.png
```

---

## Saída real (executada em 14/08/2026)

```
$ python -m sinal analisar la.wav
arquivo ................ la.wav
taxa de amostragem ..... 44100 Hz  (Nyquist = 22050 Hz)
duração ................ 2.000 s  (88200 amostras)
resolução espectral .... 1.00 Hz/bin  (janela de análise = 44100 amostras)

pico ................... 0.9000  (-0.92 dBFS)
RMS .................... 0.3174  (-9.97 dBFS)
fator de crista ........ 9.05 dB   (senoide pura = 3,01 dB)
componente DC .......... -0.000011
amostras ceifadas ...... 0  (0.000 %)
energia em 60±5 Hz .... 0.87 %

estimativa de f0
  FFT + parábola .......   439.997 Hz
  HPS ..................   440.038 Hz
  autocorrelação .......   440.025 Hz
  consenso (mediana) ...   440.025 Hz

nota ................... A4  (ideal 440.000 Hz com A4=440.0)
desvio ................. +0.1 cents  sustenido ↑
veredito ............... afinado
THD (5 harmônicos) ..... -2.57 dB  (74.39 %)
```

**Leia esses números — cada um ensina algo:**

- **Resolução de 1,00 Hz/bin** com 44 100 amostras a 44,1 kHz. Resolução = taxa/N.
  Nada que você faça depois da aquisição melhora isso; zero-padding interpola,
  não resolve. Mas o erro final foi de **0,1 cent** (≈ 0,025 Hz), quarenta vezes
  menor que o bin — é o que a interpolação parabólica compra.
- **Fator de crista 9,05 dB.** Uma senoide pura dá 3,01 dB. Nove dB indica soma de
  harmônicos com fases variadas: o pico cresce mais que o RMS.
- **0,87 % da energia em 60 ± 5 Hz.** Depois do notch, 0,00 %.
- **THD de −2,57 dB (74 %)** parece desastroso e está **correto**: o sinal foi
  *sintetizado* com cinco harmônicos fortes de propósito. Num amplificador real
  isso seria defeito; aqui é a especificação. Medida sem contexto não significa nada.
- **Os três estimadores concordam** dentro de 0,04 Hz. Quando divergem, o programa
  avisa — e a divergência costuma ser erro de oitava, não ruído.

Teste o afinador desafinando de propósito:

```
$ python -m sinal gerar off.wav --f0 452 && python -m sinal analisar off.wav
...
nota ................... A4  (ideal 440.000 Hz com A4=440.0)
desvio ................. +46.7 cents  sustenido ↑
veredito ............... DESAFINADO
```

452 Hz está a 46,7 cents de A4 — quase meio semitom. Confere:
1200·log₂(452/440) = 46,6.

E a filtragem:

```
$ python -m sinal filtrar la.wav limpo.wav --remover-zumbido --passa-alta 80
gravado: limpo.wav
  · notch 60 Hz × 3 harmônicos
  · passa-alta Butterworth 80.0 Hz ordem 4
  fase ............... zero (filtfilt)
  RMS antes .......... -9.97 dBFS
  RMS depois ......... -10.01 dBFS
  energia removida ... 1.05 %
```

1,05 % de energia removida e a nota intacta: exatamente o zumbido, e só ele.

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md            você está aqui
├── requirements.txt     dependências com versão testada
├── sinal/
│   ├── __init__.py
│   ├── __main__.py      CLI com argparse: gerar | analisar | filtrar | figura
│   ├── config.py        parâmetros sintonizáveis + variáveis de ambiente SINAL_*
│   ├── io_wav.py        WAV PCM ↔ float [-1,1) com a biblioteca padrão
│   ├── geracao.py       síntese: tom harmônico, ADSR, ruído, zumbido, chirp
│   ├── medidas.py       pico, RMS, dBFS, fator de crista, clipping, SNR, THD
│   ├── frequencia.py    f0 por FFT, HPS e autocorrelação; Hz → nota + cents
│   ├── filtros.py       FIR por janela, Butterworth SOS, notch, fase zero
│   └── graficos.py      onda + espectro + espectrograma em um PNG
└── tests/
    └── test_sinal.py    25 testes (unittest da biblioteca padrão)
```

---

## O que cada decisão de projeto ensina

**Ler WAV com a biblioteca padrão, não com `librosa`.**
Trinta linhas em que se vê o int16 dividido por 32768. Quem nunca viu isso acha
que "áudio digital" é mágica. Também evita puxar 400 MB de dependência para um
exemplo didático — e `librosa` sozinho já traz `numba`, `soundfile` e `scikit-learn`.

**Três estimadores de f0 em vez de um.**
Não é redundância: é o padrão de projeto certo para estimação. Cada método falha
de um jeito conhecido (FFT erra oitava para cima, HPS erra para baixo sem piso,
autocorrelação se atrapalha com vibrato). A mediana de três estimadores com
falhas *independentes* é muito mais robusta que qualquer um deles.

**Um piso no espectro comprimido do HPS.**
Nasceu de um teste vermelho: senoide pura de 440 Hz devolvia 110 Hz. A causa está
comentada no código — sem piso, o produto num sub-harmônico compara-se
numericamente ao produto na fundamental, e o arredondamento decide. É o tipo de
bug que só aparece com um caso de teste degenerado, e é por isso que ele existe.

**`n_fft` como piso, nunca como teto.**
`np.fft.rfft(x, n=8192)` com 88 200 amostras **descarta** 80 008 delas sem avisar.
A função `_tamanho_fft` transforma isso num zero-padding. Antes da correção, o
programa analisava só os primeiros 0,19 s — o ataque da nota — e errava por
0,8 cent em vez de 0,1.

**Configuração em `dataclass` congelada com validação.**
`n_fft` tem de ser potência de dois; a validação recusa 5000 com mensagem clara.
Frequência de rede é 60 Hz aqui e 50 Hz na Europa: `SINAL_FREQ_REDE=50`.

**Testes com tolerância justificada, não com `assertEqual`.**
Em DSP, `assertEqual(x, 440.0)` nunca passa. Cada `delta` no arquivo de teste tem
um comentário dizendo de onde veio: 2⁻¹⁴ é o passo de quantização, 3,0103 dB é
20·log₁₀(√2), 0,5 % é o limiar de percepção do ouvido.

**Tratamento de erro com mensagem acionável.**
`ErroDeAudio` num MP3 não diz "formato inválido", diz o comando `ffmpeg` que
resolve. `ErroDeFiltro` num corte acima de Nyquist lembra que o limite é taxa/2.

**Um teste que mede a fase.**
`test_filtfilt_tem_fase_zero` filtra um impulso e verifica que o pico **não se
moveu**; `test_sosfilt_causal_atrasa` verifica que ele **se moveu**. É a diferença
entre offline e tempo real, expressa em duas asserções.

---

## Exercícios sobre este código

1. Troque a janela Hann por retangular em `f0_por_fft` e meça quanto o erro em
   cents piora. Explique com o que você leu em [`20`](../20-analise-espectral-e-janelas.md).
2. Faça `--taxa 8000` e `--f0 3000`. Por que o programa se recusa a gerar?
   Force gerando um seno de 3 kHz manualmente a 8 kHz e veja em que frequência
   o analisador acha que ele está.
3. Implemente o YIN (diferença acumulada normalizada) como quarto estimador e
   compare com os três em sinal com vibrato.
4. Adicione `--tempo-real`, que processa o WAV em blocos de 512 amostras com
   `sosfilt` e estado (`zi`), e prove que a saída é idêntica à de um `sosfilt`
   sobre o sinal inteiro.
5. Meça o custo: quanto tempo leva a análise de 1 s? Compare `np.fft.rfft` com
   `scipy.fft.rfft` (que usa pocketfft com múltiplas threads).

---

## Autoteste

1. Por que a resolução espectral foi 1,00 Hz e não 5,38 Hz?
2. O que a interpolação parabólica melhora, e o que ela **não** melhora?
3. Por que o fator de crista deste sinal é 9 dB e não 3 dB?
4. Por que `filtfilt` não pode ser usado num afinador em tempo real?
5. O que aconteceria com `escrever_wav` se removêssemos o `np.clip`?
6. Por que a mediana e não a média dos três estimadores?
7. THD de 74 % é um defeito aqui? Justifique.
