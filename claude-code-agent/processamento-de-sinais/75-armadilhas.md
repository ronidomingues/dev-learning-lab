# 75 · Armadilhas, erros clássicos e mitos

`Nível: todos` · `Atualizado em: 19/08/2026`

Este é o arquivo mais lucrativo do curso em tempo economizado. São 30 armadilhas e
10 mitos, cada um com **sintoma**, **causa** e **correção** — e, quando o erro é
famoso, quem já caiu nele.

---

## Parte I · Armadilhas de convenção e unidade

### 1. Frequência normalizada por Nyquist × por fs
**Sintoma:** o filtro corta no dobro ou na metade da frequência pretendida.
**Causa:** SciPy e MATLAB usam Wn normalizada por **fs/2**, não por fs.
**Correção:** passe sempre `fs=` explicitamente. `signal.firwin(101, 800, fs=8000)`.

### 2. 20·log₁₀ × 10·log₁₀
**Sintoma:** tudo dá metade ou o dobro dos dB esperados.
**Causa:** 20 para amplitude, 10 para potência.
**Correção:** pergunte-se "isto é amplitude ou potência?" antes de digitar.

### 3. Ordem do filtro × número de taps
**Sintoma:** filtro com um coeficiente a mais ou a menos que o esperado.
**Causa:** `fir1(n, ...)` do MATLAB dá **n+1** coeficientes; `firwin(numtaps, ...)`
dá `numtaps`.
**Correção:** ao traduzir MATLAB → SciPy, `fir1(40, W)` ⟶ `firwin(41, W)`.

### 4. Convenção de sinal do denominador IIR
**Sintoma:** implementou a equação de diferenças à mão e o filtro instabilizou.
**Causa:** na SciPy, `a = [1, a1, a2]` significa `y[n] = ... − a1·y[n−1] − a2·y[n−2]`.
O sinal **inverte** ao isolar y[n].
**Correção:** use `lfilter`/`sosfilt`. Se implementar à mão, teste contra a SciPy.

### 5. RMS × pico × pico-a-pico
**Sintoma:** medida 1,41× ou 2,83× fora.
**Causa:** senoide de amplitude 1 tem RMS 0,707 e pico-a-pico 2.
**Correção:** declare a convenção no nome da variável.

### 6. Unilateral × bilateral em DEP
**Sintoma:** sua medida dá exatamente o dobro da fórmula do livro.
**Causa:** `welch` devolve densidade unilateral; fórmulas teóricas costumam ser
bilaterais.
**Correção:** ao discordar de um livro por fator 2 ou 2π, **suspeite da convenção
antes do código** ([`22 §4`](22-ruido-e-processos-estocasticos.md)).

---

## Parte II · Armadilhas de amostragem

### 7. Decimar sem filtrar
**Sintoma:** aparecem tons que não existiam; som "metálico".
**Causa:** `x[::M]` é decimação sem anti-aliasing.
**Correção:** `signal.decimate(x, M)`. Sempre.
**Nota:** é o mesmo erro do `stride` em redes convolucionais
([`29 §1`](29-dsp-e-aprendizado-de-maquina.md)) — e demorou até 2019 para a
comunidade de aprendizado profundo perceber.

### 8. Achar que aliasing dá erro
**Sintoma:** nenhum. É esse o problema.
**Causa:** aliasing não é exceção, é resultado plausível e errado.
**Correção:** filtro analógico antes do A/D; verificar a banda do sinal.

### 9. Reamostrar com `signal.resample` em sinal não periódico
**Sintoma:** artefatos nas bordas.
**Causa:** o método por FFT assume periodicidade.
**Correção:** `resample_poly` para áudio e sinais longos. **Mas meça** — no miolo,
o método por FFT é mais preciso ([`06 §6`](06-exemplos.md)).

### 10. Ignorar o jitter do clock
**Sintoma:** SNR trava abaixo do esperado, e mais bits não resolvem.
**Causa:** 1 ns de jitter limita a 78 dB em 20 kHz
([`15 §6`](15-amostragem-e-quantizacao.md)).
**Correção:** meça o clock antes de culpar o conversor.

### 11. Esquecer o droop do sample-and-hold
**Sintoma:** perda de ~3 dB no topo da banda, na saída do DAC.
**Correção:** filtro de compensação 1/sinc.

---

## Parte III · Armadilhas de FFT e análise espectral

### 12. Não janelar
**Sintoma:** uma senoide pura vira uma montanha larga com saias.
**Causa:** janela retangular implícita ([`20 §2`](20-analise-espectral-e-janelas.md)).
**Correção:** `x * np.hanning(len(x))` como padrão.

### 13. Achar que zero-padding aumenta a resolução
**Sintoma:** o gráfico fica liso mas dois picos continuam fundidos.
**Causa:** resolução é fs/N com N **real** ([`16 §2`](16-dft-e-fft.md)).
**Correção:** grave por mais tempo. Não há atalho.

### 14. Plotar o resultado complexo da FFT
**Sintoma:** `ComplexWarning`, gráfico sem sentido.
**Correção:** `np.abs(X)` para magnitude, `np.unwrap(np.angle(X))` para fase.

### 15. `log10` de zero
**Sintoma:** `-inf` no gráfico, eixo destruído.
**Correção:** `20*np.log10(np.maximum(np.abs(X), 1e-12))`.

### 16. Não remover a média antes da FFT
**Sintoma:** um pico enorme em DC vazando para os bins vizinhos.
**Correção:** `x = x - x.mean()`, ou `signal.detrend(x)`.

### 17. Normalização errada com janela
**Sintoma:** amplitude 6 dB baixa.
**Causa:** dividiu por N em vez de por `sum(w)` (Hann tem soma ≈ N/2).
**Correção:** `2*np.abs(X)/np.sum(w)`.

### 18. N primo na FFT
**Sintoma:** lentidão inexplicável em lote.
**Correção:** `scipy.fft.next_fast_len(N)`.

### 19. Convolução circular acidental
**Sintoma:** lixo no começo do resultado.
**Causa:** FFT com N < len(x)+len(h)−1.
**Correção:** `signal.fftconvolve` / `oaconvolve`.

### 20. Confundir espectro de potência com densidade
**Sintoma:** o "nível de ruído" muda quando você muda `nperseg`.
**Causa:** leu potência onde devia ler densidade
([`20 §6`](20-analise-espectral-e-janelas.md)).
**Correção:** `scaling='density'` para ruído, `'spectrum'` para tons.

### 21. Validar um estimador ao longo do eixo errado
**Sintoma:** a variância medida não bate com a teoria.
**Causa:** mediu dispersão ao longo da frequência (bins correlacionados) em vez de
entre realizações.
**Correção:** **Monte Carlo**. Este erro está documentado, com o percurso completo
do diagnóstico, em [`20 §4`](20-analise-espectral-e-janelas.md) — eu mesmo caí nele
ao escrever este curso.

---

## Parte IV · Armadilhas de filtros

### 22. `filtfilt` em tempo real
**Sintoma:** "funcionou no notebook e no equipamento ficou estranho".
**Causa:** `filtfilt` precisa do sinal inteiro, inclusive do futuro.
**Correção:** `sosfilt` com estado.

### 23. Esquecer a atenuação dobrada do `filtfilt`
**Sintoma:** o corte ficou 6 dB em vez de 3 dB.
**Causa:** filtrar duas vezes eleva |H| ao quadrado.
**Correção:** projete para metade da atenuação desejada.

### 24. Esquecer o `zi` no processamento em blocos
**Sintoma:** clique na fronteira de cada bloco.
**Correção:** `y, zi = signal.sosfilt(sos, bloco, zi=zi)`, propagando `zi`.

### 25. Forma direta em ordem alta
**Sintoma:** filtro instável, ou `NaN`.
**Causa:** sensibilidade das raízes ao coeficiente ([`19 §3`](19-filtros-iir.md)).
**Correção:** `output='sos'`. Em float32 e ponto fixo é **requisito**.

### 26. Não plotar a resposta antes de aplicar
**Sintoma:** descobre o erro no fim da cadeia.
**Correção:** `signal.freqz`/`sosfreqz` **sempre**, antes de aplicar.

### 27. Passa-alta FIR com número par de taps
**Sintoma:** a SciPy reclama, ou o filtro não faz o que devia.
**Causa:** tipo II tem zero obrigatório em Nyquist
([`18 §2`](18-filtros-fir.md)).
**Correção:** use N ímpar.

### 28. Ignorar o transiente inicial
**Sintoma:** as primeiras amostras estão erradas.
**Causa:** o filtro parte com estado zero.
**Correção:** descarte as primeiras N amostras, ou inicialize com `sosfilt_zi`.

### 29. Q alto demais num notch
**Sintoma:** um "toque" que soa como sinal.
**Causa:** polo quase no círculo unitário, resposta ao impulso longa.
**Correção:** Q ≤ ~30 para 60 Hz. Mais estreito não é melhor.

### 30. Derivar um sinal ruidoso
**Sintoma:** o resultado é puro ruído.
**Causa:** derivar multiplica por jω — amplifica exatamente onde está o ruído.
**Correção:** Savitzky-Golay, ou suavizar antes.

---

## Parte V · Mitos

### Mito 1 · "Mais bits sempre melhora"
**Falso.** Acima do ruído analógico do sistema, bits extras só codificam ruído.
Um conversor "de 24 bits" entrega ENOB de 19–21 na prática
([`15 §4`](15-amostragem-e-quantizacao.md)). E o **jitter** frequentemente limita
antes dos bits.

### Mito 2 · "Taxa de amostragem maior sempre melhora o som"
**Discutível, e menos do que se vende.** 96 kHz não acrescenta nada audível ao
conteúdo (o ouvido vai a 20 kHz). O que pode melhorar é o **filtro
anti-aliasing**, que fica mais suave. Em produção há um argumento real: menos
artefato acumulado em processamento não linear. Para distribuição, 48 kHz basta.
*Isto é opinião profissional; há debate honesto.*

### Mito 3 · "Filtro digital é sempre melhor que analógico"
**Falso.** Antes do A/D **tem** de haver filtro analógico — é matematicamente
impossível fazer anti-aliasing em digital. E analógico não tem latência de bloco.

### Mito 4 · "Fase não importa em áudio"
**Parcialmente falso.** Para sinais estacionários, o ouvido é pouco sensível. Para
**transientes**, fase não linear borra o ataque audivelmente
([`13 §5`](13-sinais-e-sistemas-lti.md)). Em ECG e comunicação digital, é crítica.

### Mito 5 · "A FFT é uma transformada diferente da DFT"
**Falso.** A FFT é um **algoritmo** para calcular a DFT. Mesmo resultado, menos
operações.

### Mito 6 · "Zero-padding melhora a resolução"
**Falso.** Interpola, não resolve. Ver armadilha 13.

### Mito 7 · "Wavelets substituem Fourier"
**Falso**, e foi muito repetido nos anos 1990. Wavelets ganham em compressão,
denoising e transientes; Fourier ganha em análise harmônica e interpretabilidade
([`24 §5`](24-tempo-frequencia-e-wavelets.md)).

### Mito 8 · "Redes neurais tornaram o DSP obsoleto"
**Falso.** Toda rede de áudio recebe espectrograma; camada convolucional **é**
filtro FIR; SGD **é** LMS. O DSP virou estrutura dentro do ML
([`29`](29-dsp-e-aprendizado-de-maquina.md)).

### Mito 9 · "Compressive sensing revoga Nyquist"
**Falso.** Ele responde a **outra pergunta** — quantas amostras para sinais
*esparsos*. Hipótese diferente, resposta diferente ([`11`](11-historia.md)).

### Mito 10 · "5 sigma é uma detecção"
**Falso sem contexto.** Com 10⁶ tentativas, 5 σ acontece por acaso em ~25 % das
buscas ([`08-projeto-espacial/02 §7`](08-projeto-espacial/02-a-fisica-do-sinal.md)).
Sempre corrija por tentativas independentes.

---

## Diagnóstico rápido por sintoma

| Sintoma | Suspeite de | Armadilha |
|---|---|---|
| tom que não existe | aliasing | 7, 8 |
| som metálico | aliasing ou reamostragem ruim | 7, 9 |
| pico largo com "saias" | falta de janela | 12 |
| dois picos não separam | resolução insuficiente | 13 |
| amplitude 6 dB baixa | normalização de janela | 17 |
| clique periódico | `zi` não propagado | 24 |
| saída explodiu ou `NaN` | forma direta / polo fora | 25 |
| corte no dobro da frequência | normalização de Wn | 1 |
| primeiras amostras erradas | transiente inicial | 28 |
| "toque" após um som | Q alto demais / corte abrupto | 29 |
| nível de ruído muda com `nperseg` | potência × densidade | 20 |
| discordância exata de fator 2 | convenção | 2, 6 |
| funciona offline, falha ao vivo | `filtfilt` | 22 |
| SNR trava com mais bits | jitter | 10 |

---

## As cinco regras que evitam a maioria destes erros

1. **Passe `fs=` sempre.** Elimina a classe inteira de erros de normalização.
2. **Plote antes de aplicar.** `freqz` custa três linhas.
3. **Teste com sinal sintético de resposta conhecida** antes de tocar em dado real.
4. **Escreva a taxa de amostragem no nome da variável e do arquivo.**
5. **Preveja antes de rodar.** Se a previsão errar, você acabou de encontrar onde
   seu modelo mental está furado — que é a única coisa que realmente vale.

---

## Autoteste

1. Seu filtro está cortando em 1600 Hz quando você pediu 800. Diagnóstico?
2. Um colega mede 3 dB onde você mede 6 dB. Quais são as duas causas mais prováveis?
3. Seu código de áudio ao vivo produz um clique a cada 256 amostras. O que falta?
4. Uma senoide pura aparece como montanha larga com "saias". Causa e correção?
5. Você aumentou `nperseg` e o nível de ruído mudou. O que está errado?
6. Por que "mais bits sempre melhora" é mito, e o que costuma limitar antes?
7. Por que "5 sigma é uma detecção" é falso sem contexto?
8. Explique por que decimar sem filtrar e o `stride` de redes convolucionais são o
   mesmo erro.
9. Cite as cinco regras que evitam a maioria dos erros deste arquivo.
