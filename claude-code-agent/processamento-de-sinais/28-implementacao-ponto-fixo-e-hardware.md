# 28 · Ponto fixo e hardware — quando os bits acabam

`Nível: avançado` · `Medições feitas em: 19/08/2026`

Todo o curso até aqui assumiu precisão infinita. Em ponto flutuante de 64 bits,
essa aproximação é boa. Em microcontrolador, FPGA, ASIC ou DSP de ponto fixo —
que é onde a maior parte do DSP do mundo realmente roda — ela é falsa, e as
consequências são brutais.

---

## 1 · Por que ponto fixo ainda existe

| | Ponto flutuante | Ponto fixo |
|---|---|---|
| Área em silício | grande | **pequena** |
| Energia por operação | alta | **baixa** (5–10× menos) |
| Custo do chip | maior | **menor** |
| Faixa dinâmica | enorme, automática | limitada, **gerenciada à mão** |
| Facilidade de programar | alta | baixa |

Em um marca-passo, um fone, um sensor a bateria ou um chip vendido aos milhões,
**energia e área são o projeto**. Ponto fixo não é legado: é a escolha certa
quando o orçamento é de microwatts.

## 2 · Notação Q

`Qm.n` = m bits de parte inteira, n de fracionária, mais o sinal.

| Formato | Faixa | Resolução | Uso |
|---|---|---|---|
| Q0.15 (int16) | [−1, 1) | 3,05×10⁻⁵ | amostras de áudio |
| Q1.14 | [−2, 2) | 6,1×10⁻⁵ | coeficientes que passam de 1 |
| Q0.31 (int32) | [−1, 1) | 4,66×10⁻¹⁰ | acumuladores |
| Q7.8 | [−128, 128) | 3,9×10⁻³ | sensores |

**A regra que evita metade dos bugs:** multiplicar Q0.15 por Q0.15 dá **Q1.30** —
o resultado tem o dobro dos bits fracionários e um bit inteiro a mais. Você
precisa deslocar de volta, e **onde** você desloca decide se perde precisão ou
transborda. Fazer isso implicitamente é a origem clássica do "por que meu filtro
soa distorcido no DSP e não no PC".

---

## 3 · 🔑 Quantização de coeficiente: o polo que sai do círculo

Este é o efeito mais perigoso, porque acontece **antes de o filtro rodar**.
Arredondar os coeficientes move as raízes do polinômio — e mover um polo para
fora do círculo unitário transforma o filtro num oscilador
([`17`](17-transformada-z.md)).

```python
import numpy as np
from scipy import signal
q = lambda v, B: np.round(v*2**(B-2))/2**(B-2)
for N in [4, 8]:
    b, a = signal.butter(N, 0.05)
    sos = signal.butter(N, 0.05, output='sos')
    for bits in [32, 16, 12, 10]:
        pa = np.abs(np.roots(q(a, bits))).max()
        ps = max(np.abs(np.roots(np.r_[1, q(s[4:], bits)])).max() for s in sos)
        ...
```

Saída real:

```
  ordem 4, 32 bits: forma direta |p|max= 0.94182 estável  | SOS |p|max= 0.94182 estável
  ordem 4, 16 bits: forma direta |p|max= 0.94016 estável  | SOS |p|max= 0.94182 estável
  ordem 4, 12 bits: forma direta |p|max= 0.99035 estável  | SOS |p|max= 0.94166 estável
  ordem 4, 10 bits: forma direta |p|max= 1.00000 INSTÁVEL | SOS |p|max= 0.94166 estável

  ordem 8, 32 bits: forma direta |p|max= 0.96970 estável  | SOS |p|max= 0.96993 estável
  ordem 8, 16 bits: forma direta |p|max= 1.00008 INSTÁVEL | SOS |p|max= 0.96995 estável
  ordem 8, 12 bits: forma direta |p|max= 1.31936 INSTÁVEL | SOS |p|max= 0.96976 estável
  ordem 8, 10 bits: forma direta |p|max= 1.45916 INSTÁVEL | SOS |p|max= 0.97026 estável
```

**Leia a linha "ordem 8, 16 bits".** Um Butterworth de ordem 8 com coeficientes em
16 bits, em forma direta, tem polo em **1,00008**. Estável no papel, oscilador no
silício. Com 12 bits, |p| = 1,32 — explode em milissegundos.

**E a coluna do SOS não se move:** 0,970 em todos os casos, de 32 a 10 bits.

**A explicação** está no fenômeno do polinômio de Wilkinson
([`19`](19-filtros-iir.md), cinco porquês): a sensibilidade das raízes aos
coeficientes cresce exponencialmente com o grau. Grau 8 é sensível; grau 2 (um
biquad) não é.

> **A regra prática mais importante deste capítulo: em ponto fixo, SOS não é
> recomendação — é requisito.** E verifique os polos **depois** de quantizar, não
> antes. `np.abs(np.roots(...)).max() < 1` é uma linha; descobrir isso em campo
> custa uma revisão de hardware.

Para casos extremos (polo muito perto do círculo, como um passa-alta de 0,1 Hz a
48 kHz), existem estruturas de sensibilidade ainda menor: **acoplada** (forma de
Gold-Rader), **treliça** (lattice) e **onda digital** (wave filters).

---

## 4 · Ruído de arredondamento: acumula, e realimenta

Cada multiplicação arredonda. Em FIR, os erros só somam. Em **IIR eles
realimentam** e circulam pelo filtro.

```
  24 bits: SNR da saída = 152.7 dB  (teoria da entrada 6.02B+1.76 = 146.2 dB)
  16 bits: SNR da saída = 100.6 dB  (teoria da entrada           =  98.1 dB)
  12 bits: SNR da saída =  77.1 dB  (teoria da entrada           =  74.0 dB)
   8 bits: SNR da saída =  60.8 dB  (teoria da entrada           =  49.9 dB)
```

(Saída real, passa-baixa Butterworth de ordem 4, corte em 0,1.)

**A SNR de saída é MAIOR que a de entrada** — o que parece impossível e não é.
O filtro é passa-baixa e o ruído de quantização é branco: o filtro remove a parte
do ruído que caiu fora da banda passante. Com 8 bits o ganho é de 11 dB.

**A lição** é a mesma da sobreamostragem ([`15 §5`](15-amostragem-e-quantizacao.md)):
ruído branco filtrado perde a fração de potência que estava fora da banda.
Filtrar melhora a SNR sempre que o sinal está numa banda menor que o ruído.

### Acumulador de guarda

A defesa padrão em FIR: acumular em precisão maior que as parcelas.

- Amostras Q0.15, coeficientes Q0.15 → produtos Q1.30.
- Acumule em **40 bits** (Q9.30): sobram 8 bits de guarda, suficientes para somar
  256 termos sem transbordar.
- Arredonde **uma única vez**, no fim.

Todo DSP de ponto fixo tem acumulador de 40 bits exatamente por isso. É uma
decisão de arquitetura de 1983 (TMS32010) que sobrevive porque a matemática não
mudou.

---

## 5 · Transbordo, saturação e ciclos limites

**Transbordo (overflow)** em complemento de dois **dá a volta**: 32767 + 1 =
−32768. Em áudio, isso é o estalo mais violento possível.

**Saturação** trava no máximo em vez de dar a volta. Distorce, mas não estala.
Todo DSP tem instruções aritméticas saturantes por isso.

⚠️ **Exceção importante:** o **CIC** ([`21 §3`](21-multitaxa-e-bancos-de-filtros.md))
depende do transbordo em complemento de dois para funcionar. Ativar saturação
**quebra** o filtro. É um dos raros lugares em que overflow é correto — e um
ótimo exemplo de por que "sempre sature" é regra, não lei.

**Ciclos limites (limit cycles):** um IIR em ponto fixo pode entrar em oscilação
sustentada de baixa amplitude **mesmo com polos estáveis e entrada zero**, porque
o arredondamento realimenta e se autossustenta. Sintoma: um chiado ou tom baixo
que não some no silêncio. Defesas: dither interno, arredondamento por truncamento
de magnitude, ou estruturas que provadamente não têm ciclos (wave filters).

---

## 6 · O hardware

| Plataforma | Força | Fraqueza | Uso típico |
|---|---|---|---|
| **MCU** (Cortex-M) | barato, integrado, baixo consumo | pouca MIPS | sensores, IoT, áudio simples |
| **Cortex-M4F/M7 + CMSIS-DSP** | FPU e SIMD, biblioteca pronta | ainda limitado | wearables, áudio embarcado |
| **DSP dedicado** (TI C6000, SHARC) | MAC, endereçamento circular, zero-overhead loop | ecossistema estreito | áudio profissional, telecom |
| **FPGA** | paralelismo massivo, latência determinística | projeto caro e lento | radar, SDR, instrumentação, front-end |
| **GPU** | vazão enorme | latência alta, energia | offline, treino de redes, imagem |
| **ASIC** | melhor tudo, em escala | milhões de dólares de NRE | celular, conversores |
| **CPU + SIMD** | fácil, flexível | energia | tudo que não é embarcado |

### As três características que definem um DSP

1. **MAC em um ciclo** — `acc += a*b`, a operação dominante de FIR e correlação.
2. **Arquitetura Harvard** — barramentos separados de dados e instruções, para
   buscar coeficiente e amostra no mesmo ciclo.
3. **Endereçamento circular** — o buffer de atraso avança sem teste de fronteira
   nem cópia.

As três vêm do TMS32010 (1983) e continuam em silício moderno, porque otimizam a
**mesma expressão** que o campo usa desde sempre.

### Onde cada uma ganha

- **FIR longo, taxa alta** → FPGA (paralelismo) ou FFT em CPU.
- **IIR de ordem baixa, latência mínima** → MCU/DSP, amostra a amostra.
- **Muitos canais independentes** → GPU ou FPGA.
- **Latência determinística garantida** → FPGA. CPU com sistema operacional
  **não** garante prazo; é a razão de instrumentação séria usar FPGA mesmo quando
  a CPU teria vazão suficiente.

---

## 7 · Fluxo de trabalho recomendado

```
1. PROTOTIPE em float64 (NumPy/SciPy). Valide a matemática.
2. SIMULE ponto fixo ainda em Python (quantize coeficientes e sinais).
   → verifique os polos DEPOIS de quantizar
   → meça a SNR de saída
   → procure ciclos limites com entrada zero e com entrada pequena
3. ESCOLHA o formato Q e o tamanho do acumulador com base na simulação.
4. IMPLEMENTE no alvo.
5. COMPARE bit a bit contra a simulação. Divergência = bug, não "precisão".
```

**O passo 5 é o que quase todo mundo pula e é o que economiza semanas.** Se a
simulação em Python e o alvo não derem o mesmo resultado, há um erro de
arredondamento, de deslocamento ou de saturação em algum lugar — e é muito mais
barato achá-lo comparando com uma referência que depurando no osciloscópio.

**Ferramentas:** `fxpmath` ou `numpy` com quantização manual em Python; CMSIS-DSP
para Cortex-M; `fi` do MATLAB (Fixed-Point Designer); Vitis HLS / Verilog para
FPGA.

---

## Autoteste

1. Por que ponto fixo ainda existe, se ponto flutuante é mais fácil?
2. Q0.15 × Q0.15 dá que formato? Qual o erro clássico daí?
3. Ordem 8 com coeficientes de 16 bits em forma direta: o que acontece, e por quê?
4. Por que SOS resolve, e qual fenômeno numérico explica a diferença?
5. Como a SNR de saída pode ser maior que a de entrada?
6. Para que serve o acumulador de 40 bits, e quantos termos ele protege?
7. Qual filtro depende de transbordo e quebra com saturação?
8. O que é um ciclo limite e qual o sintoma audível?
9. Cite as três características arquiteturais de um DSP e o que cada uma otimiza.
10. Por que instrumentação séria usa FPGA mesmo quando a CPU teria vazão?
