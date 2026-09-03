# 03 · O código, linha a linha

`Nível: intermediário` · `Atualizado em: 19/08/2026`

Percorre o pacote `cosmos/` inteiro, explicando **o que cada linha faz e por que
ela está escrita assim**. Onde há uma escolha de projeto, a alternativa rejeitada
está dita e o motivo também.

Ordem de leitura recomendada: siga na ordem deste arquivo, com o `.py`
correspondente aberto ao lado.

---

## Mapa de dependências entre os módulos

```
constantes.py                 (não depende de nada)
     │
     ├──► ruido.py            k·T·B, radiômetro, integração
     ├──► dispersao.py        atraso do plasma, dedispersão
     │        │
     │        └──► pulsar.py  síntese, folding, busca      ◄── usa dispersao
     ├──► doppler.py          desvio, rampa, estimação
     │
aquisicao.py                  LFSR, PN, correlação 2-D      (não depende de constantes)
deteccao.py                   estatística de decisão        (usa scipy.special/stats)
graficos.py                   figuras                       (importa matplotlib sob demanda)
     │
     └──► __main__.py         CLI: junta tudo em 4 pipelines
```

---

## 1 · `constantes.py`

```python
C_LUZ = 299_792_458.0
K_BOLTZMANN = 1.380_649e-23
```

**Por que sem incerteza.** Desde a redefinição do SI de 2019, essas duas não são
medidas: são **definições**. O metro é definido a partir de c, e o kelvin a
partir de k. Escrever `299792458.0` é exato por construção, e por isso o teste
usa `assertEqual` e não `assertAlmostEqual` — é o único lugar do projeto onde
igualdade exata de ponto flutuante é a asserção correta.

**Por que os sublinhados.** `299_792_458.0` é Python válido e legível. Um dígito
errado num número de nove algarismos é invisível sem separador.

```python
K_DISPERSAO = 4.148_808e3
```

**A constante mais importante e mais delicada do projeto.** A docstring dela é
longa de propósito: registra que o valor é **convenção da comunidade**, não a
melhor medida física, e que trocá-lo invalidaria a comparação com todo DM já
publicado. Numa base de código científica, a fonte de uma constante é parte da
constante.

```python
BANDAS_DSN = {"X": (8.42e9, "8,42 GHz — o cavalo de batalha da DSN ..."), ...}
```

**Por que uma tupla (valor, comentário)** e não só o valor: o CLI imprime o
comentário. Documentação que o programa mostra ao usuário não envelhece
esquecida num arquivo separado.

---

## 2 · `ruido.py`

### `potencia_de_ruido`

```python
if t_sys_k <= 0 or banda_hz <= 0:
    raise ValueError("temperatura e banda devem ser positivas")
return K_BOLTZMANN * t_sys_k * banda_hz
```

Duas linhas de física, uma de guarda. **Por que a guarda importa aqui**: uma
temperatura negativa passaria silenciosamente e produziria potência negativa, que
se propagaria para a SNR e daria um resultado plausível e errado. Em código
científico, falhar cedo e alto é obrigatório — o modo de falha caro não é o
travamento, é o número errado que ninguém questiona.

### `temperatura_de_sistema`

```python
for nome, v in [("t_receptor", t_receptor_k), ...]:
    if v < 0:
        raise ValueError(f"{nome} não pode ser negativa")
return t_receptor_k + t_ceu_k + t_atmosfera_k + t_solo_k
```

O laço de validação **nomeia** a variável culpada na mensagem. Validar quatro
parâmetros com quatro `if` daria a mesma segurança e mensagens piores.

A soma é direta — e a docstring explica por quê: potências de fontes
independentes somam linearmente. Somar em quadratura é o erro clássico, e vale
para amplitudes, não para potências.

### `radiometro`

```python
if n_polarizacoes not in (1, 2):
    raise ValueError("n_polarizacoes deve ser 1 ou 2")
return t_sys_k / np.sqrt(n_polarizacoes * banda_hz * tau_s)
```

Uma linha. A docstring, quinze — porque a linha é trivial e o **porquê da raiz
quadrada** é o conteúdo do arquivo. `n_polarizacoes` restrito a {1, 2} porque não
existe 1,5 polarização; aceitar um float convidaria a um erro de unidade
silencioso.

### `tempo_necessario`

```python
return (n_sigma * t_sys_k / delta_t_alvo_k) ** 2 / (n_polarizacoes * banda_hz)
```

Inversão algébrica da anterior. **Por que existe como função separada**, se é uma
linha: porque é a pergunta que se faz de fato ("quantas horas peço?"), e porque
o teste `test_tempo_necessario_inverte_o_radiometro` verifica que as duas são
inversas exatas — um teste que pegaria um erro de expoente que a leitura não pega.

Note o **quadrado**: exigir 5 σ em vez de 3 σ custa (5/3)² = 2,8× mais tempo.

### `gerar_ruido`

```python
rng = np.random.default_rng(semente)
potencia = potencia_de_ruido(t_sys_k, banda_hz)
return rng.standard_normal(n_amostras) * np.sqrt(potencia)
```

- `default_rng(semente)` e **não** `np.random.seed()`: o gerador global é estado
  compartilhado, e duas funções que o usem interferem uma na outra. Um gerador
  local com semente explícita é reprodutível de verdade.
- `standard_normal` tem variância 1. Multiplicar por √P dá variância P — o
  **desvio padrão** escala com a raiz, e é a potência que queremos fixar.

### `integrar`

```python
n_util = (len(x) // fator) * fator
if n_util == 0:
    raise ValueError(...)
return x[:n_util].reshape(-1, fator).mean(axis=1)
```

O `reshape(-1, fator).mean(axis=1)` faz a média em blocos **vetorizada**, em C.
O equivalente com laço Python seria ~100× mais lento.

`n_util` **descarta** a sobra em vez de completar com zeros. A escolha é
deliberada e está comentada no código: zeros criariam um degrau artificial no fim
da série, e degrau no tempo é energia espalhada por todo o espectro — um
transiente espúrio na análise seguinte.

---

## 3 · `dispersao.py`

### `atraso_dispersao`

```python
termo_ref = 0.0 if f_ref_mhz is None else 1.0 / f_ref_mhz ** 2
return K_DISPERSAO * dm * (1.0 / f_mhz ** 2 - termo_ref)
```

`f_ref_mhz = None` significa **frequência infinita** — e 1/∞² = 0, que é o
`termo_ref = 0.0`. É a convenção da literatura de pulsares, porque torna o atraso
independente da banda do instrumento e portanto comparável entre observatórios.

A guarda `if dm < 0` tem mensagem física, não genérica: *"não existe coluna
negativa de elétrons"*. Mensagem de erro que ensina custa o mesmo que mensagem
de erro que só reclama.

### `aplicar_dispersao` — o simulador do meio

```python
for i, f in enumerate(freqs_mhz):
    n_desloca = int(round(atraso_dispersao(dm, f, f_ref_mhz) / dt_s))
    saida[i] = np.roll(espectro[i], n_desloca)
```

Três decisões nessas três linhas:

1. **`np.roll` (circular) e não deslocamento com preenchimento.** Simula uma
   observação contínua, em que o pulso anterior entra pela borda. Está declarado
   na docstring como limitação: num pipeline sobre arquivo finito, o correto
   seria preencher com ruído.
2. **`int(round(...))`** — atraso em número inteiro de amostras. Introduz erro de
   até meia amostra por canal. Irrelevante aqui, inaceitável em timing de
   nanossegundos, onde se usa deslocamento por fase no domínio da frequência.
   Declarado.
3. **Laço sobre canais.** Vetorizar exigiria construir uma matriz de índices; com
   64 canais o laço custa microssegundos e o código fica legível. Se fossem
   16 384 canais (CHIME), valeria vetorizar.

### `dedispersar` — o coração do pipeline

```python
acumulador = np.zeros(espectro.shape[1], dtype=np.float64)
for i, f in enumerate(freqs_mhz):
    n_desloca = int(round(atraso_dispersao(dm, f, f_ref_mhz) / dt_s))
    acumulador += np.roll(espectro[i], -n_desloca)
return acumulador
```

**O sinal negativo em `-n_desloca` é a linha mais importante do arquivo.**
`aplicar_dispersao` empurra cada canal para a frente; aqui puxamos de volta.
Trocar o sinal produziria o dobro da dispersão e nenhum aviso — o pico
simplesmente não apareceria, e a depuração seria longa. É exatamente por isso que
existe o teste `test_dedispersar_desfaz_dispersar`, que verifica que os 32 canais
de amplitude 1 reaparecem somados em **uma única amostra**, com valor 32.

O acumulador é `float64` explícito: somar 64 canais de dados que poderiam vir em
`float32` acumularia erro, e a soma é justamente onde se ganha SNR.

### `plano_dm_tempo`

```python
return np.vstack([dedispersar(espectro, freqs_mhz, dm, dt_s, f_ref_mhz)
                  for dm in dms])
```

Uma linha, custo O(n_dms × n_canais × n_amostras) — **a operação mais cara de
todo o projeto**. A docstring diz isso e nomeia os algoritmos que existem para
evitá-la (tree dedispersion, FDMT) e o hardware que se usa (GPU, FPGA). Marcar
o gargalo no lugar onde ele mora vale mais que uma seção de "performance" no fim
do README.

---

## 4 · `pulsar.py`

### `perfil_gaussiano` — a distância circular

```python
d = fase - fase_pico
d = np.minimum(np.abs(d), 1.0 - np.abs(d))
return np.exp(-0.5 * (d / largura_fracao) ** 2)
```

A segunda linha é sutil e essencial. A fase é **circular**: 0,98 e 0,02 estão a
0,04 de distância, não a 0,96. Sem essa linha, um pulso perto da borda do período
seria cortado ao meio.

`fase_pico = 0.35` como padrão, e não 0,5, **de propósito**: um valor simétrico
esconderia um erro de alinhamento (um espelhamento acidental daria o mesmo
resultado). Escolher um valor assimétrico para o padrão é uma técnica barata de
tornar os testes mais severos.

### `sintetizar_observacao` — três camadas

```python
trem = perfil[(fase * n_fase).astype(int) % n_fase] * amplitude_pulso
limpo = np.tile(trem, (n_canais, 1))
disperso = dispersao.aplicar_dispersao(limpo, freqs, dm, dt_s)
ruido = rng.standard_normal((n_canais, n_amostras)) * sigma_ruido
return disperso + ruido, freqs
```

Lê-se como a física acontece, na ordem:

1. **a estrela emite** um trem periódico (`trem`), idêntico em todas as
   frequências — hipótese de espectro plano, declarada;
2. **o meio interestelar dispersa** (`aplicar_dispersao`);
3. **o receptor acrescenta ruído** térmico, independente por canal.

A indexação `perfil[(fase*n_fase).astype(int) % n_fase]` é uma amostragem por
vizinho mais próximo. Aceitável porque n_fase = 1024 é bem maior que a resolução
efetiva em fase (período/dt ≈ 714 amostras por giro). O `% n_fase` protege contra
o índice 1024 quando a fase é exatamente 1,0.

O ruído é gerado **de uma vez** para a matriz inteira, e não canal a canal: uma
chamada ao gerador em vez de 64, e o resultado é reprodutível pela semente.

### `dobrar` — o folding, com `bincount`

```python
t = np.arange(len(serie)) * dt_s
bins = ((t / periodo_s) % 1.0 * n_fase).astype(int) % n_fase
soma = np.bincount(bins, weights=serie, minlength=n_fase)
conta = np.bincount(bins, minlength=n_fase)
if np.any(conta == 0):
    raise ValueError(...)
return soma / conta
```

Linha a linha:

- `t` — instantes absolutos de cada amostra.
- `(t / periodo_s) % 1.0` — a **fase de rotação**: onde a amostra cai dentro do
  giro. O `% 1.0` é o que "enrola" o tempo no período.
- `* n_fase` e `.astype(int)` — converte fase contínua em índice de bin.
- O segundo `% n_fase` protege o caso de borda.
- **`np.bincount` com `weights`** faz o acúmulo por bin em C. Um laço Python
  sobre 60 000 amostras levaria dezenas de milissegundos; isto leva ~0,5 ms.
- Dividir `soma/conta` promedia. Usar `conta` real (e não N/n_fase) importa
  porque os bins não recebem exatamente o mesmo número de amostras quando o
  período não é múltiplo inteiro de `dt`.
- A guarda `conta == 0` transforma um `nan` silencioso (divisão por zero) numa
  mensagem que diz o que fazer: reduzir `n_fase`.

### `snr_perfil` — não sabotar a própria medida

```python
n_ruido = max(4, int(len(perfil) * (1.0 - fracao_pulso)))
base = np.sort(perfil)[:n_ruido]
return float((perfil.max() - base.mean()) / base.std())
```

`np.sort(...)[:n_ruido]` pega os bins **mais baixos** — a linha de base. Se
usássemos todos os bins, o próprio pulso inflaria o desvio padrão e a SNR sairia
menor: o sinal sabotaria a medida. Excluir a região do pulso é obrigatório, e é
um caso particular de estimação robusta.

`max(4, ...)` garante ao menos quatro amostras para estimar um desvio padrão.

---

## 5 · `doppler.py`

### `gerar_portadora_com_doppler` — o fator ½

```python
fase = 2*np.pi * (f0_hz*t + 0.5*deriva_hz_por_s*t**2) + fase_inicial
return amplitude * np.exp(1j * fase)
```

**O `0.5` é o erro nº 1 desta parte do campo.** A frequência instantânea é
f(t) = f₀ + k·t; a fase é a **integral** dela, e a integral de k·t é k·t²/2.
Escrever `2π·f(t)·t` dá o dobro da inclinação e o receptor nunca trava.

`np.exp(1j*fase)` devolve **complexo**. Não é sofisticação: sem a parte
imaginária não há como distinguir frequência positiva de negativa — ou seja, não
há como saber se a sonda se aproxima ou se afasta. O teste
`test_estimador_aceita_frequencia_negativa` existe para provar isso.

### `corrigir_doppler`

```python
correcao = np.conj(gerar_portadora_com_doppler(len(sinal), fs_hz, f_estimada_hz,
                                               deriva_hz_por_s))
return np.asarray(sinal) * correcao
```

Multiplicar pela **conjugada** da rampa estimada desfaz a rotação de fase. É a
propriedade de deslocamento em frequência da tabela de Fourier, usada como
ferramenta em vez de sofrida como efeito. Reusar a mesma função geradora para a
correção garante que os dois lados usem exatamente a mesma convenção de fase —
se a geração mudar, a correção acompanha.

### `estimar_frequencia` — interpolação com vizinhos circulares

```python
a, b, c = (20*np.log10(max(X[(k+d) % n_fft], 1e-30)) for d in (-1, 0, 1))
denom = a - 2*b + c
d = 0.5*(a - c)/denom if abs(denom) > 1e-30 else 0.0
```

- **`(k+d) % n_fft`** — vizinhos **circulares**. O espectro de um sinal complexo
  é periódico, e o pico pode cair no bin 0 ou no último. Sem o módulo, seria um
  `IndexError` ou, pior, um vizinho errado.
- **`max(..., 1e-30)`** — piso antes do `log10`, senão um bin exatamente nulo dá
  `-inf` e contamina a parábola.
- **`abs(denom) > 1e-30`** — protege contra três bins iguais (espectro plano),
  em que a parábola é degenerada.
- Interpolar **em dB** e não em linear: o topo do lóbulo de uma janela Hann é
  quase exatamente uma parábola em escala logarítmica.

### `estimar_deriva`

```python
tempos.append((i + 0.5) * n_por_bloco / fs_hz)
...
deriva, intercepto = np.polyfit(tempos, freqs, 1)
t_central = len(x) / (2 * fs_hz)
return float(intercepto + deriva * t_central), float(deriva)
```

O `+ 0.5` põe o instante no **centro** do bloco, não no início — senão a
regressão fica com viés de meio bloco. Devolver a frequência no instante
**central** da observação (e não em t=0) é a convenção que minimiza a
correlação entre os dois parâmetros estimados.

---

## 6 · `aquisicao.py`

### `lfsr_sequencia_m`

```python
reg = [1]*grau if estado_inicial is None else [...]
if not any(reg):
    raise ValueError("estado inicial não pode ser todo zero (o LFSR travaria)")

for i in range(n):
    saida[i] = reg[-1]
    realim = 0
    for t in taps:
        realim ^= reg[t-1]
    reg = [realim] + reg[:-1]
```

- **A guarda do estado zero** não é paranoia: com todos os bits zero, o XOR
  devolve zero para sempre e o registrador trava. É por isso que a sequência tem
  2ⁿ−1 e não 2ⁿ elementos.
- `saida[i] = reg[-1]` — o bit que **sai** pela ponta é a saída.
- `realim ^= reg[t-1]` — XOR das posições de tap. `t-1` porque os taps são
  contados a partir de 1, como na literatura de polinômios primitivos.
- `reg = [realim] + reg[:-1]` — desloca e insere a realimentação na frente.

**Por que um laço Python e não vetorização:** a recorrência é intrinsecamente
sequencial (cada bit depende do anterior). Para grau 10 são 1023 iterações, ~1 ms.
Se precisasse de grau 20 (10⁶ bits), valeria uma implementação em bits empacotados.

### `codigo_pn`

```python
return (1 - 2 * lfsr_sequencia_m(grau).astype(np.float64))
```

`1 - 2*bit`: bit 0 → +1, bit 1 → −1. É o mapeamento BPSK, e é **o que faz o piso
da autocorrelação ser −1** em vez de algo positivo. Com 0/1, a correlação seria
sempre positiva e não haveria o cancelamento que produz o piso plano.

### `adquirir` — a busca 2-D

```python
x = x[:n]                                  # um período de código
C_conj = np.conj(np.fft.fft(c))            # calculado UMA vez
for i, fd in enumerate(dopplers):
    desgirado = x * np.exp(-2j*np.pi*fd*t)
    correl = np.fft.ifft(np.fft.fft(desgirado) * C_conj)
    matriz[i] = np.abs(correl)
```

- **`C_conj` fora do laço** — a FFT do código não depende da hipótese de Doppler.
  Calculá-la dentro do laço dobraria o custo. Otimização óbvia e frequentemente
  esquecida.
- **`x * exp(-2jπ·fd·t)`** remove a hipótese de Doppler **antes** de correlacionar.
  Esta é a razão de a busca ser 2-D: se a fase gira durante a correlação, a soma
  se cancela mesmo com o atraso certo.
- **Correlação via FFT** (`ifft(fft(a) * conj(fft(b)))`) — O(N log N) em vez de
  O(N²) por hipótese. Com 25 hipóteses de Doppler e N=1023, a diferença é
  perceptível; num receptor real com milhares de hipóteses, é decisiva.
- **`np.abs`** descarta a fase: o que interessa é onde está o pico.

```python
piso = np.median(matriz)
```

**Mediana e não média.** A média seria puxada para cima pelo próprio pico e por
lóbulos laterais fortes. A mediana é robusta a uma minoria de valores extremos —
exatamente o caso. Estimador robusto para um piso é regra, não requinte.

### `adquirir_acumulado`

```python
acumulador = matriz if acumulador is None else acumulador + matriz
```

Soma os **módulos**, não os complexos. Somar complexos seria integração coerente
(ganho N em vez de √N) e exigiria fase alinhada entre períodos — que Doppler
residual e instabilidade de oscilador quebram. Tomar o módulo antes torna a soma
imune a isso, ao preço de ganho menor. A troca está medida na docstring: a −20 dB,
1 período falha, 4 acertam.

---

## 7 · `deteccao.py`

### `probabilidade_falso_alarme` — a linha numericamente delicada

```python
q = 0.5 * special.erfc(limiar_sigma / np.sqrt(2.0))
return float(-np.expm1(n_tentativas * np.log1p(-q)))
```

A fórmula matemática é `1 − (1−q)^N`. Escrita assim, em ponto flutuante, ela
**falha**: para q ~ 3×10⁻⁷, `1-q` arredonda para algo cujo N-ésimo poder perde os
dígitos significativos, e a subtração de 1 sofre cancelamento catastrófico.

`log1p(x)` calcula log(1+x) com precisão total para x pequeno; `expm1(x)` calcula
eˣ−1 do mesmo jeito. A composição `-expm1(N*log1p(-q))` é matematicamente idêntica
e numericamente correta.

É a diferença entre obter 2,87×10⁻⁷ e obter 0,0 — e um 0,0 aqui significaria
"impossível ser acaso", que é a conclusão oposta à correta em muitos casos.

### `limiar_para_falso_alarme`

```python
q = -np.expm1(np.log1p(-pfa_alvo) / n_tentativas)
return float(stats.norm.isf(q))
```

Inverte a anterior: resolve q e usa `isf` (*inverse survival function*), que é a
inversa da cauda superior. Usar `ppf(1-q)` daria o mesmo resultado matemático com
perda de precisão para q pequeno — de novo, cancelamento.

### `tentativas_independentes_busca`

```python
return int(n_dms) * int(n_periodos) * int(n_fase)
```

Uma multiplicação, e uma docstring longa explicando que ela **superestima**,
porque células vizinhas da grade são correlacionadas. Usar o limite superior
torna o teste conservador — a direção certa de errar numa busca de descoberta.
Determinar o número efetivo exige Monte Carlo com ruído puro, que é o que
colaborações sérias fazem antes de anunciar.

---

## 8 · `__main__.py` — o que a CLI acrescenta

O CLI não é enfeite: ele é onde as peças viram **pipeline**, e onde o resultado
vira **decisão**. Três padrões que valem copiar:

**1 · Imprimir a comparação, não só o resultado.**

```python
print(f"  melhor DM .............. {dms[i]:.2f} pc·cm⁻³   (verdadeiro {args.dm:.2f})")
```

Todo valor estimado sai ao lado do valor verdadeiro. Quem lê a saída **vê** se o
pipeline acertou, sem precisar conferir em outro lugar.

**2 · Imprimir o ganho de cada etapa.**

```python
print(f"  somando canais SEM dedispersar ... {sem_dedisp:6.2f} sigma")
print(f"  com dedispersão correta .......... {snrs[i]:6.2f} sigma")
print(f"  √n_canais (limite teórico) ....... {np.sqrt(args.canais):6.2f}×")
```

Mostrar o limite teórico ao lado do ganho obtido transforma a saída em
**diagnóstico**: se o ganho real ficar muito abaixo do teórico, algo está errado.

**3 · Emitir o alerta de RFI.**

```python
print(f"  SNR em DM = 0 .......... {snrs[0]:.2f} sigma"
      f"   <- se este fosse o maior, seria RFI, não astronomia")
```

Interferência terrestre não sofre dispersão, logo tem seu máximo em DM = 0. É o
teste de triagem mais usado em busca de FRBs, e cabe numa linha de saída.

E o código de retorno: `_cmd_enlace` devolve **3** quando a aquisição falha, não
0. Um pipeline que "roda sem erro" mas não detecta nada precisa dizer isso ao
script que o chamou.

---

## Autoteste

1. Por que `constantes.py` usa `assertEqual` nos testes de c e k?
2. Qual é o efeito de trocar o sinal em `-n_desloca` no `dedispersar`?
3. Por que `perfil_gaussiano` calcula distância circular?
4. O que `np.bincount` faz no folding, e qual a alternativa mais lenta?
5. Por que `snr_perfil` ordena o perfil antes de estimar a linha de base?
6. Onde está o fator ½ e o que acontece se ele for esquecido?
7. Por que `C_conj` é calculado fora do laço de Doppler?
8. Por que o piso da aquisição usa mediana e não média?
9. Explique por que `1 - (1-q)**N` falha e o que o substitui.
10. Por que `_cmd_enlace` devolve 3 e não 0 quando falha?
