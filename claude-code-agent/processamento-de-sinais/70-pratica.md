# 70 · Prática — 14 laboratórios progressivos

`Nível: iniciante → pesquisa` · `Atualizado em: 19/08/2026`

Teoria sem prática não fixa. Cada laboratório tem **objetivo, roteiro, critério de
sucesso e o que ele ensina**. Faça na ordem; cada um pressupõe o anterior.

**Regra de ouro, válida para todos:** *escreva sua previsão antes de rodar.*
Se você sempre roda primeiro e explica depois, está confirmando, não aprendendo.

---

## Bloco 1 · Fundamentos (labs 1–4)

### Lab 1 · O espectro de tudo que você tem em casa
`Pré: 04` · `Tempo: 1 h`

Grave (ou baixe) cinco sons bem diferentes: um assobio, uma palma, uma nota de
instrumento, sua voz falando "aaa", e ruído (chuveiro, ventilador).

Para cada um, produza: forma de onda, espectro em dB e espectrograma.

**Critério de sucesso:** você consegue, olhando só o espectrograma, dizer qual é
qual — e explicar por quê. A palma é banda larga e curta; o assobio é uma raia
quase pura; a vogal tem harmônicos com envoltória de formantes
([`25 §3`](25-audio-e-fala.md)).

**Ensina:** a leitura visual que você usará o resto da vida.

### Lab 2 · Provocar todos os erros de propósito
`Pré: 04, 15, 20` · `Tempo: 2 h`

Produza, deliberadamente, cada um destes e **fotografe o sintoma**:

1. **Aliasing** — seno de 3 kHz amostrado a 4 kHz.
2. **Vazamento** — seno em frequência não inteira de bin, janela retangular.
3. **Festonamento** — mesma senoide, medindo amplitude em várias posições de bin.
4. **Clipping** — amplitude 1,5 salva em WAV 16 bits.
5. **Wrap-around** — o mesmo, sem `np.clip` antes da conversão.
6. **Convolução circular** — FFT com N insuficiente ([`16 §5`](16-dft-e-fft.md)).
7. **Instabilidade** — IIR com polo em 1,01.

**Critério:** você reconhece cada um **pelo sintoma**, sem ver o código.

**Ensina:** depuração. Metade do trabalho real é diagnosticar por sintoma.

### Lab 3 · Reconstruir o teorema da amostragem
`Pré: 15` · `Tempo: 2 h`

Gere um sinal de banda limitada (soma de senoides até 1 kHz) a 44,1 kHz.
Reamostre para 2,5 kHz. Reconstrua **por interpolação sinc, escrita à mão** e
compare com o original.

Depois repita com 1,8 kHz (violando Nyquist) e meça o erro.

**Critério:** com 2,5 kHz, erro < 1 %; com 1,8 kHz, erro grande **e** você consegue
prever em que frequências os aliases apareceram.

**Ensina:** que o teorema é literalmente verdadeiro, e que violá-lo é irreversível.

### Lab 4 · A DFT na mão
`Pré: 16` · `Tempo: 1 h`

Implemente a DFT como produto matriz-vetor (`F @ x`), sem `np.fft`. Confirme
contra o NumPy. Depois implemente uma FFT radix-2 recursiva de 20 linhas e
confirme de novo. Meça o tempo dos três para N = 512, 2048, 8192.

**Critério:** os três resultados idênticos até 10⁻¹²; a curva de tempo do seu
radix-2 acompanha N log N.

**Ensina:** que a FFT não é mágica — é uma fatoração.

---

## Bloco 2 · Filtros (labs 5–8)

### Lab 5 · Projetar com especificação
`Pré: 18, 19` · `Tempo: 3 h`

Especificação: fs = 48 kHz, passa até 3 kHz com ripple ≤ 0,5 dB, rejeita a partir
de 4 kHz com ≥ 60 dB.

Projete **cinco** filtros que atendam: `firwin`, `remez`, Butterworth, Chebyshev I
e elíptico. Para cada um, tabele: ordem/taps, multiplicações por amostra, atraso
de grupo (mín/máx), e se a fase é linear.

**Critério:** a tabela está completa e você defende uma escolha para cada um de
três cenários — (a) ECG, (b) áudio em tempo real num MCU, (c) análise offline.

**Ensina:** que "projetar um filtro" é escolher entre compromissos, não achar "o
melhor".

### Lab 6 · Fase importa (ou não)
`Pré: 13, 18` · `Tempo: 2 h`

Pegue um sinal com transiente forte (palma, bateria) e passe por: (a) FIR de fase
linear, (b) IIR elíptico de mesma seletividade, (c) o mesmo IIR com `filtfilt`.

Plote os três sobrepostos no tempo. **Ouça os três.**

**Critério:** você **vê** a deformação do transiente no caso (b) e **não vê** em
(a) e (c). E consegue explicar por que (c) não serve em tempo real.

**Ensina:** a diferença entre magnitude e fase, com os ouvidos.

### Lab 7 · Streaming com estado
`Pré: 19` · `Tempo: 2 h`

Filtre um sinal longo em blocos de 256 amostras, três vezes:
(a) sem guardar `zi`, (b) guardando `zi`, (c) tudo de uma vez.

Compare (a) e (b) com (c), amostra a amostra.

**Critério:** (b) é **bit a bit idêntico** a (c); (a) tem descontinuidades exatamente
nas fronteiras de bloco, e você consegue apontá-las no gráfico.

**Ensina:** o defeito mais comum de código de áudio em tempo real.

### Lab 8 · Ponto fixo
`Pré: 28` · `Tempo: 3 h`

Pegue o Butterworth de ordem 8 do Lab 5. Quantize os coeficientes para 16, 12 e
10 bits, em forma direta e em SOS. Para cada caso: calcule `max|polo|`, e se for
estável, rode e meça a SNR de saída.

**Critério:** você reproduz o resultado de [`28 §3`](28-implementacao-ponto-fixo-e-hardware.md)
— forma direta instabiliza, SOS não.

**Ensina:** por que `output='sos'` é requisito e não estilo.

---

## Bloco 3 · Aplicações (labs 9–11)

### Lab 9 · Afinador completo
`Pré: 07-projeto-modelo` · `Tempo: 4 h`

Estenda o projeto-modelo: implemente **YIN** como quarto estimador de f0 e
compare com os três existentes em três sinais — senoide pura, nota de violão real,
e voz cantada com vibrato.

**Critério:** você tabela erro médio e pior caso de cada método por sinal, e
explica **qual falha em quê** e por quê.

**Ensina:** que estimadores têm modos de falha, e que a escolha depende do sinal.

### Lab 10 · Limpar um sinal biomédico
`Pré: 06 §4, 19` · `Tempo: 3 h`

Baixe um ECG real (PhysioNet tem bases públicas). Remova zumbido de rede e deriva
de linha de base. Detecte os complexos QRS e calcule a variabilidade RR.

Depois **repita com corte em 0,5 Hz e em 0,05 Hz** e compare o segmento ST.

**Critério:** você mostra, no gráfico, a distorção do segmento ST causada pelo
corte em 0,5 Hz — e entende por que a norma de diagnóstico exige 0,05 Hz.

**Ensina:** que uma escolha de filtro pode ter consequência clínica.

### Lab 11 · SDR de verdade
`Pré: 26, 03 §4.4` · `Tempo: 4 h` · `Requer hardware (~US$ 30)`

Com uma dongle SDR: (a) demodule FM comercial em NumPy puro sobre o I/Q;
(b) decodifique ADS-B de aviões em 1090 MHz.

Sem hardware: use gravações I/Q públicas — existem várias, e o processamento é
idêntico.

**Critério:** você ouve a rádio e vê a posição de aviões reais.

**Ensina:** que a cadeia inteira, do fóton ao bit, cabe na sua cabeça.

---

## Bloco 4 · Pesquisa (labs 12–14)

### Lab 12 · Detectar um pulsar
`Pré: 08-projeto-espacial` · `Tempo: 4 h`

Faça os níveis 2 e 3 de [`08-projeto-espacial/06-exercicios.md`](08-projeto-espacial/06-exercicios.md):
busca 2-D em DM × período, excisão de RFI, e interpolação do pico de DM com barra
de erro.

**Critério:** seu pipeline recupera P e DM de uma injeção **cega** feita por outra
pessoa — e diz "não há sinal" quando não há.

**Ensina:** o método científico aplicado a processamento de sinais.

### Lab 13 · Medir o próprio estimador
`Pré: 20 §4, 60 §5` · `Tempo: 3 h`

Escolha um estimador (frequência de senoide, por exemplo). Meça, por Monte Carlo
com 500 realizações: viés, variância, e compare com o **limite de Cramér-Rao**.

Varie a SNR e trace variância × SNR junto com o CRB.

**Critério:** você identifica o **limiar de SNR** abaixo do qual o estimador
descola do CRB (o efeito de limiar clássico), e explica por que ele existe.

**Ensina:** a diferença entre "meu código funciona" e "meu estimador é eficiente".

### Lab 14 · Reproduzir um paper
`Pré: tudo` · `Tempo: 10–20 h`

Escolha um artigo com resultado quantitativo e método descrito, e reproduza uma
figura. Sugestões acessíveis: comparação de janelas, desempenho de LMS × RLS,
ou uma métrica de realce de fala.

**Critério:** sua figura bate com a publicada, **ou** você documenta precisamente
em que ela difere e o que faltava na descrição do método.

**Ensina:** o que é reprodutibilidade de verdade — e por que ela é mais rara do
que se imagina. Frequentemente você descobre que o paper omitiu um detalhe
essencial; isso também é um resultado.

---

## Como usar estes laboratórios

| Se você tem | Faça |
|---|---|
| um fim de semana | 1, 2, 5 |
| duas semanas | 1 a 8 |
| um semestre | todos, com o projeto-modelo entre o 8 e o 9 |
| foco em áudio | 1, 2, 5, 6, 9, 10 |
| foco em embarcado | 2, 5, 7, 8 |
| foco em pesquisa | 3, 4, 12, 13, 14 |

**Registre tudo num caderno de laboratório.** Data, parâmetros, previsão,
resultado, e o que surpreendeu. A coluna "o que surpreendeu" é a mais valiosa —
é onde seu modelo mental estava errado, e é o único lugar onde o aprendizado
acontece de verdade.

---

## Autoteste

1. Por que a regra "escreva sua previsão antes de rodar" é a mais importante daqui?
2. No Lab 2, qual é a diferença de sintoma entre aliasing e vazamento espectral?
3. No Lab 3, o que exatamente você prova ao reconstruir com interpolação sinc?
4. No Lab 6, por que o caso (c) — `filtfilt` — não serve em tempo real, apesar de
   ter o melhor resultado visual?
5. No Lab 7, qual é o critério de sucesso, e por que "quase igual" não basta?
6. No Lab 10, que consequência clínica você deve conseguir demonstrar no gráfico?
7. No Lab 13, o que é o "efeito de limiar" e por que ele existe?
8. Por que o Lab 14 (reproduzir um paper) frequentemente termina descobrindo uma
   omissão no método publicado — e por que isso também é um resultado?
