# 02 · A física do sinal — de onde vem cada fórmula do código

`Nível: intermediário` · `Atualizado em: 19/08/2026`

Aqui cada equação usada no `cosmos/` é derivada ou justificada. A regra: nenhuma
fórmula aparece sem que se saiba **de onde ela veio** e **quando ela deixa de
valer**.

---

## 1 · Temperatura como unidade de potência

### A física

Um resistor a temperatura T, ligado a uma linha casada, entrega potência de
ruído numa banda B:

```
P = k · T · B          [k = 1,380649×10⁻²³ J/K]
```

Este é o **ruído de Johnson-Nyquist**, medido por Johnson e explicado por Nyquist
em 1928 (o mesmo Nyquist do teorema da amostragem — ele resolveu os dois
problemas no mesmo ano, nos mesmos Bell Labs).

**De onde vem:** cada modo do campo eletromagnético na linha carrega, no limite
clássico, energia média kT (teorema da equipartição). Numa banda B há 2B modos
por segundo (Nyquist de novo), e metade da potência flui em cada sentido.
O resultado é P = kTB.

**Quando deixa de valer:** a forma completa tem o fator de Planck
hf/(e^{hf/kT} − 1), que se reduz a kT quando hf ≪ kT. Em 10 GHz e 30 K,
hf/kT ≈ 0,016 — o erro é ~1,6 %. Em frequências de terahertz ou temperaturas
criogênicas extremas, a correção quântica importa. Este projeto trabalha na faixa
em que kTB vale.

### A convenção que simplifica tudo

Como todo ruído se exprime por kTB, é natural medir **qualquer** potência pela
temperatura equivalente. Daí:

- **T_A** (temperatura de antena): potência que a fonte astronômica entrega.
- **T_rec**: ruído do receptor, referido à entrada.
- **T_sys** = soma de tudo que entra.

Somam-se **linearmente** porque são potências de fontes independentes.

> ⚠️ Erro comum: somar em quadratura. Quadratura vale para amplitudes de sinais
> aleatórios independentes, não para potências. Potências somam direto.

### Contribuições típicas

| Fonte | Ordem de grandeza | Comentário |
|---|---|---|
| Fundo cósmico (CMB) | 2,725 K | piso absoluto, irredutível |
| Emissão galáctica | ∝ f^{−2,7} | domina abaixo de ~1 GHz; ~100 K em 100 MHz |
| Atmosfera | 2–20 K | pior em 22 GHz (água) e 60 GHz (oxigênio) |
| Spillover do solo | 5–20 K | o chão está a ~290 K; 1 % de vazamento = 2,9 K |
| Receptor (LNA) | 4–100 K | é o que se compra com criogenia e dinheiro |

---

## 2 · A equação do radiômetro

```
ΔT_min = T_sys / √(n_pol · B · τ)
```

### Derivação

1. Um sinal de banda B tem 2B graus de liberdade por segundo (teorema da
   amostragem). Em τ segundos: **N ≈ B·τ** amostras independentes complexas.
2. O detector mede potência, ou seja, o quadrado da amplitude. Para ruído
   gaussiano, a potência de cada amostra segue uma distribuição exponencial, cuja
   média e desvio padrão são **iguais**. Daí: uma única amostra tem incerteza
   relativa de 100 %.
3. Promediando N amostras independentes, a incerteza relativa da média cai por
   **√N** (a variância da média é σ²/N).
4. Logo, a menor variação detectável é T_sys/√N = T_sys/√(Bτ).

O fator `n_pol` entra porque medir as duas polarizações é observar duas vezes
simultaneamente.

### O que a equação decide, na prática

Dobrar a sensibilidade exige **quadruplicar** o tempo. Por isso a ordem de
prioridade em qualquer projeto de instrumento é:

1. **Baixar T_sys** — entra linearmente. Criogenia de 20 K para 5 K melhora 4×.
2. **Alargar B** — entra com raiz, mas é barato em eletrônica moderna.
3. **Aumentar τ** — entra com raiz, e é o recurso mais caro (tempo de telescópio).
4. **Aumentar a área da antena** — entra linearmente em T_A, mas o custo cresce
   como o cubo do diâmetro.

**Verificado no código** (`cosmos/ruido.py`, testes
`test_radiometro_escala_com_raiz_do_tempo` e
`test_duas_polarizacoes_ganham_raiz_de_dois`).

---

## 3 · Dispersão pelo plasma interestelar

### A física

Num plasma frio e não magnetizado, o índice de refração para uma onda de
frequência f é

```
n(f) = √(1 − f_p²/f²),        f_p = frequência de plasma ≈ 8,98 kHz · √(n_e [cm⁻³])
```

A **velocidade de grupo** é v_g = c·n(f) < c: frequências mais baixas viajam mais
devagar. Integrando o tempo de trânsito ao longo do caminho e expandindo para
f ≫ f_p (sempre verdade em rádio: f_p da ISM é ~1 kHz e observamos em MHz–GHz):

```
t(f) = D/c + (e²/(2π·m_e·c)) · ∫n_e dl / f²
       └─ trânsito ─┘   └──── atraso dispersivo ────┘
```

Definindo **DM = ∫n_e dl** (em pc·cm⁻³) e agrupando as constantes:

```
Δt = K · DM / f²,        K = 4148,808 MHz² pc⁻¹ cm³ s
```

### Sobre a constante K — uma nota de honestidade

O valor 4148,808 é uma **convenção da comunidade de pulsares**, não a melhor
medida física. O valor derivado das constantes fundamentais atuais difere na
sexta casa. A comunidade fixou o valor histórico para que DMs medidos em décadas
diferentes sejam comparáveis. Mudar a constante mudaria todos os DMs publicados.

É um caso limpo de **convenção arbitrária mantida por compatibilidade** — o mesmo
tipo de decisão que fixou 44,1 kHz no CD ([`11-historia.md`](../11-historia.md)).
E é obrigatório declarar qual constante se usou. O `cosmos/constantes.py` declara.

### O número que dá escala ao problema

Com DM = 50 pc·cm⁻³, entre 800 e 400 MHz:

```
Δt = 4148,808 × 50 × (1/400² − 1/800²) = 0,972377 s
```

**Quase um segundo** de varredura ao longo da banda. Se você somar os canais sem
corrigir, o pulso — que dura milissegundos — se espalha por um segundo inteiro e
desaparece. **Verificado no código** com erro nulo (`test_atraso_conta_de_mao`).

### O limite da dedispersão incoerente

A dedispersão incoerente corrige o atraso **entre** canais, mas dentro de cada
canal ainda há dispersão residual, porque o canal tem largura Δf:

```
t_borrão ≈ 2·K·DM·Δf / f³
```

Se `t_borrão` > largura do pulso, o pulso se apaga e **nenhum processamento
posterior o recupera**. Daí duas consequências de projeto:

1. Instrumentos modernos usam **milhares de canais** (o CHIME usa 16 384).
2. Existe a **dedispersão coerente**, que corrige a *fase* do sinal em tensão, e
   não tem esse limite — ao preço de exigir os dados brutos, ordens de grandeza
   mais volumosos, e de custar muito mais computação.

Implementado em `dispersao.dispersao_maxima_tolerada`, e o CLI **avisa** quando o
DM pedido excede o limite do instrumento configurado.

---

## 4 · Folding e a estatística do pulso

### Por que funciona

Amostras separadas por múltiplos exatos do período contêm o **mesmo** valor de
sinal e valores **independentes** de ruído. Somando N delas:

```
sinal → N·s          ruído → √N·σ          SNR → √N · (s/σ)
```

### A tolerância no período — o ponto que costuma escapar

Se o período usado errar por δP, o pulso escorrega em fase. Depois de T segundos
de observação, o escorregamento acumulado é `T·δP/P²` períodos. Para não borrar:

```
δP/P < P/T = 1/(número de giros observados)
```

| Observação | Giros | Precisão relativa exigida |
|---|---|---|
| 60 s, P = 0,714 s | 84 | ~1 % |
| 1 h, P = 0,714 s | 5 042 | ~2×10⁻⁴ |
| 10 anos, P = 5 ms | 6×10¹⁰ | ~2×10⁻¹¹ |

A última linha é o **timing de pulsar** de precisão, e é por isso que períodos
publicados têm 15 casas decimais — e por que o modelo precisa incluir o
movimento da Terra, a posição no céu e correções relativísticas.

**Verificado**: `test_periodo_errado_nao_detecta` mostra que errar 10 % no
período destrói a detecção.

### Estimar a SNR sem se autossabotar

A linha de base tem de ser estimada **excluindo a região do pulso**. Se você usar
todos os bins, o próprio pulso infla o desvio padrão e a SNR sai menor — o sinal
sabota a própria medida. Implementado em `pulsar.snr_perfil` ordenando os bins e
usando só os mais baixos.

---

## 5 · Doppler

### A fórmula e seu limite

```
f_rx = f_tx · (1 − v_r/c)          [não relativística]
```

Válida para v ≪ c. Para 20 km/s, v/c = 6,7×10⁻⁵, e o termo de segunda ordem
(v²/2c² ≈ 2×10⁻⁹) só importa em experimentos de relatividade — que a DSN de fato
faz, e que exigem a forma relativística completa.

### Escala prática

Na banda X (8,42 GHz): **28,086 Hz por (m/s)**. Uma sonda a 20 km/s desloca
561,7 kHz — muito maior que a largura de banda do laço de rastreamento, que é de
poucos hertz.

**Consequência de arquitetura:** o receptor **não procura às cegas**. Ele prediz
o Doppler a partir da efeméride orbital e sintoniza o receptor de acordo. A
aquisição só precisa cobrir o **erro residual** da predição. Sem efeméride, o
espaço de busca seria grande demais.

### Por que duas vias

A DSN transmite da Terra, a sonda devolve coerentemente (multiplicando por uma
razão fixa como 880/749), e a Terra compara com a referência local — um **maser
de hidrogênio**. Assim, o relógio de referência fica em Terra, e não no oscilador
pequeno, envelhecido e termicamente instável da sonda.

É uma decisão de **arquitetura de sistema**, não de algoritmo, e é a que mais
contribui para a precisão. Vale a lição geral: onde colocar a referência costuma
importar mais que qual algoritmo usar.

### A rampa: o erro do fator ½

A frequência instantânea é f(t) = f₀ + k·t. A fase é a **integral**:

```
φ(t) = 2π·(f₀·t + ½·k·t²)
```

Escrever `2π·f(t)·t` dá o dobro da inclinação e o receptor nunca trava. É o mesmo
½ do chirp, e é o erro de implementação mais comum nessa parte.

---

## 6 · Códigos pseudoaleatórios e ganho de processamento

### O ganho

```
G = 10·log₁₀(N) dB
```

Com N = 1023 (código C/A do GPS): **30,1 dB**. Um sinal 20 dB abaixo do ruído sai
da correlação 10 dB acima dele.

### Por que sequência-m e não ruído de verdade

Uma sequência-m gerada por LFSR com polinômio primitivo tem as **propriedades de
Golomb**:

1. **Balanceamento**: exatamente 2^(n−1) uns e 2^(n−1)−1 zeros.
2. **Autocorrelação de dois níveis**: N no atraso zero e **exatamente −1** em
   todos os outros.
3. **Propriedade de janela**: toda subsequência de n bits é única.

A propriedade 2 é decisiva. Ruído verdadeiro teria correlações laterais
flutuando em ±√N ≈ ±32 para N = 1023; a sequência-m tem exatamente −1.
**Determinismo bem escolhido bate aleatoriedade.**

**Verificado no código** — `test_autocorrelacao_de_dois_niveis` confirma laterais
todas iguais a −1,000 dentro de 10⁻⁶, para graus 5 e 10.

### Por que a busca precisa ser 2-D

Se houver Doppler não compensado, a fase gira durante a correlação e a soma se
cancela — **mesmo com o atraso correto**. Com 1 ms de integração, 1 kHz de
Doppler gira um ciclo inteiro e zera a correlação. Por isso a aquisição varre
atraso **e** Doppler.

### Coerente × não coerente

| | Coerente | Não coerente |
|---|---|---|
| O que se soma | os complexos | os módulos |
| Ganho | N | ~√N |
| Exige | fase estável em toda a integração | nada |
| Quando usar | Doppler já bem estimado | aquisição inicial |

**Medido neste projeto**: a −20 dB de SNR, um período de código falha e quatro
períodos acumulados não coerentemente acertam atraso e Doppler.

---

## 7 · Estatística de detecção

### O efeito das múltiplas tentativas

Para ruído gaussiano, a probabilidade de uma amostra exceder n sigmas é
Q(n) = ½·erfc(n/√2). Com N tentativas independentes:

```
P(ao menos uma) = 1 − (1 − Q)^N
```

| Limiar | 1 tentativa | 10⁶ tentativas |
|---|---|---|
| 3 σ | 1,3×10⁻³ | ~1 (certeza) |
| 5 σ | 2,9×10⁻⁷ | **~25 %** |
| 7 σ | 1,3×10⁻¹² | 1,3×10⁻⁶ |

**"5 sigma" não significa nada sem dizer quantas tentativas foram feitas.**
É por isso que buscas de pulsar exigem 8–10 σ e física de partículas fixou 5 σ
para buscas com poucos graus de liberdade.

Em física de partículas isso se chama *look-elsewhere effect*; em estatística,
problema das comparações múltiplas.

### Duas ressalvas honestas, implementadas no código

1. O produto n_DM × n_períodos **superestima** as tentativas independentes,
   porque células vizinhas da grade são correlacionadas. Usar o limite superior
   torna o teste conservador — a direção certa de errar numa busca de descoberta.
2. **Ruído real não é gaussiano.** Interferência de rádio produz caudas muito
   mais pesadas que a teoria. Por isso os cortes de veredito em
   `deteccao.resumo_deteccao` são conservadores, e por isso todo candidato de
   verdade exige **confirmação em outra observação, com outro instrumento**.

### Estabilidade numérica

`1 − (1 − q)^N` com q pequeno sofre cancelamento catastrófico em ponto flutuante.
O código usa `−expm1(N·log1p(−q))`, que calcula a mesma coisa com precisão total.
É um detalhe de análise numérica, e é a diferença entre obter 2,9×10⁻⁷ e obter 0.

---

## Autoteste

1. Por que temperaturas de ruído somam linearmente e não em quadratura?
2. Derive, em quatro passos, a equação do radiômetro.
3. Por que se investe primeiro em criogenia e só depois em tempo de observação?
4. De onde vem a dependência 1/f² do atraso dispersivo?
5. Por que a constante 4148,808 é convenção e não medida?
6. Qual é o limite da dedispersão incoerente e como se contorna?
7. Uma observação de 1 hora de um pulsar de 0,714 s exige que precisão no período?
8. Por que a linha de base da SNR precisa excluir a região do pulso?
9. Por que a DSN usa duas vias em vez de uma?
10. O que a propriedade de Golomb nº 2 garante, e por que ruído real seria pior?
11. Quando usar acumulação coerente e quando usar não coerente?
12. Por que "5 sigma" pode não significar nada?
