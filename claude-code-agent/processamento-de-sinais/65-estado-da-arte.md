# 65 · Estado da arte — onde o campo está em agosto de 2026

`Nível: pesquisa` · `Pesquisado na web em: 19/08/2026`
⚠️ **Este arquivo envelhece rápido.** Reavalie a cada 6 meses.

---

## 1 · O que mudou de lugar

O tema oficial do ICASSP 2026 — a principal conferência da área — é
**"Where Signals Meet Intelligence"**. O nome não é marketing: descreve com
precisão o que aconteceu com o campo.

```
     2005              2015                   2026
  ┌─────────┐      ┌─────────┐          ┌──────────────┐
  │ DSP     │      │ DSP     │          │ DSP como     │
  │ clássico│  →   │ + ML na │    →     │ ESTRUTURA    │
  │ sozinho │      │  saída  │          │ dentro do ML │
  └─────────┘      └─────────┘          └──────────────┘
   projeta-se       extrai-se            embute-se o modelo
   o filtro         característica       físico na rede, e
                    e treina-se          treina-se tudo junto
```

O DSP não foi substituído nem ficou intacto: virou **viés indutivo** dentro de
modelos aprendidos. Ver [`29`](29-dsp-e-aprendizado-de-maquina.md).

---

## 2 · Codecs neurais e tokenização de áudio

**A fronteira mais ativa.** A arquitetura consolidada:

```
áudio → encoder convolucional → quantizador vetorial (RVQ) → tokens discretos
tokens → decoder → áudio
```

Uma vez discretizado, o áudio é modelado pelas mesmas arquiteturas que modelam
texto. Foi essa unificação que destravou a geração de fala e música de alta
qualidade dos últimos anos.

**O que está em disputa em 2026:**

| Eixo | Situação |
|---|---|
| **Taxa de quadros** | corrida por *frame rates* cada vez menores (menos tokens por segundo ⟹ modelos de língua mais eficientes) |
| **Restrição tripla** | o desafio de codecs de baixo recurso do ICASSP 2026 exige **taxa, computação e latência** baixas **ao mesmo tempo**, com ruído e reverberação realistas — os métodos neurais ainda não resolvem os três juntos |
| **Robustez** | desempenho fora da distribuição de treino continua sendo o calcanhar |
| **Latência** | comunicação em tempo real exige poucos ms; muitos codecs neurais não chegam lá |

**A leitura honesta:** codecs neurais ganham em qualidade por bit, e ainda perdem
em previsibilidade, custo computacional e latência. Opus continua sendo a escolha
segura para produção em tempo real; codecs neurais dominam onde a qualidade por
bit importa mais que o custo.

---

## 3 · DSP diferenciável (DDSP)

Campo maduro o suficiente para ter revisão publicada e bibliotecas, e ativo o
suficiente para produzir resultados novos a cada conferência.

**O que está resolvido:**
- osciladores harmônicos + ruído filtrado, treináveis (a formulação original de 2020);
- filtros **all-pole** e **all-pass** diferenciáveis, incluindo variantes no tempo;
- processamento diferenciável no **domínio da frequência**;
- vocoders DDSP usados como refinamento em realce de fala com **poucos recursos** —
  a atratividade vem justamente de terem poucos ou nenhum parâmetro treinável.

**Por que importa, em uma frase:** embutir a estrutura física reduce
drasticamente a necessidade de dados e devolve interpretabilidade — os parâmetros
voltam a ter nome (f0, corte, amplitude de harmônico).

**Onde ainda não chega:** problemas sem modelo físico razoável. Reconhecimento de
fala irrestrito continua sendo território de rede pura.

---

## 4 · Realce e separação

| Tarefa | Estado em 2026 |
|---|---|
| Redução de ruído em tempo real | modelos muito pequenos (centenas de milhares de parâmetros) rodando em CPU de celular; qualidade muito acima da subtração espectral clássica |
| Separação de fontes | redes no domínio do tempo superaram as espectrais; separação de música em stems é produto de consumo |
| Realce com poucos recursos | híbridos DDSP + rede pequena são a direção mais promissora |
| Cancelamento de eco | híbrido: adaptativo clássico ([`23`](23-estimacao-e-filtragem-adaptativa.md)) + supressão residual neural |

**Nota de engenharia:** o cancelamento de eco continua **híbrido**, e isso é
instrutivo. A parte linear tem solução ótima conhecida e barata; a rede cuida do
resíduo não linear (alto-falante saturando, vibração do gabinete). Usar rede para
a parte linear seria desperdício.

---

## 5 · Amostragem e aquisição

- **Compressive sensing** consolidou-se onde a esparsidade é real: **MRI acelerada
  está em uso clínico**, encurtando exames. Não virou técnica universal, e o
  entusiasmo de 2006–2012 assentou num nicho legítimo e valioso.
- **Taxa de inovação finita (FRI)** e amostragem em espaços shift-invariant
  continuam ativas em instrumentação.
- **Conversores** seguem melhorando por sobreamostragem e formatação de ruído; o
  gargalo prático continua sendo o **jitter de clock**
  ([`15 §6`](15-amostragem-e-quantizacao.md)), não o número de bits.

---

## 6 · Hardware

| Tendência | Situação |
|---|---|
| **NPUs em celulares e MCUs** | aceleradores de inferência viraram padrão; DSP e ML dividem o mesmo silício |
| **TinyML / DSP embarcado** | redes de poucos KB rodando em Cortex-M ao lado de filtros clássicos |
| **RISC-V com extensões vetoriais** | alternativa aberta a DSPs proprietários, ganhando espaço |
| **FPGA** | continua insubstituível onde latência determinística é requisito |
| **Computação analógica / in-memory** | pesquisa; promete ordens de magnitude em eficiência, ainda sem produto maduro |

---

## 7 · Debates em aberto

**1 · Aprender ou projetar?**
Consenso emergente: **aprender o que não se sabe modelar, projetar o que se sabe**.
DDSP é a materialização disso. Quem defende extremos (só rede, ou só clássico)
está discutindo ideologia, não engenharia.

**2 · Métricas.**
Métricas objetivas (PESQ, STOI, SI-SDR) correlacionam mal com julgamento humano
para saídas **generativas** — uma rede pode gerar áudio que soa ótimo e pontua
mal, ou o contrário. Avaliação subjetiva é cara e lenta. Este é um problema
metodológico sério e não resolvido, e ele contamina a comparação entre trabalhos.

**3 · Reprodutibilidade.**
Modelos grandes, dados proprietários e custo de treino tornam muitos resultados
irreprodutíveis. É uma regressão em relação ao DSP clássico, em que qualquer
resultado podia ser refeito com uma folha de papel e um computador.

**4 · Robustez e garantias.**
Sistemas críticos exigem comportamento previsível fora do treino. Não há teoria
satisfatória. É o motivo real de o clássico continuar em aviação e medicina.

**5 · Energia.**
O custo energético dos modelos grandes virou restrição de projeto, não nota de
rodapé. Empurra na direção de híbridos eficientes — mais uma força a favor do DDSP.

---

## 8 · O que estudar se você quer entrar na fronteira

| Direção | Pré-requisitos deste curso | Por onde começar |
|---|---|---|
| Codecs e geração de áudio | 20, 21, 25, 29 | literatura de RVQ e codecs neurais |
| DDSP | 18, 19, 25, 29 | a revisão de DDSP para música e fala; bibliotecas de filtros diferenciáveis |
| Amostragem avançada | 15, 60 | compressive sensing, FRI |
| Tempo-frequência | 20, 24, 60 | sincrossqueeze, frames |
| Embarcado | 19, 21, 28 | CMSIS-DSP, TinyML, RISC-V vetorial |
| Radar / SDR / espacial | 22, 23, 26 + [`08-projeto-espacial/`](08-projeto-espacial/README.md) | GNU Radio, literatura de radar |

**Onde acompanhar:** ICASSP e EUSIPCO (gerais), Interspeech (fala), DAFx (áudio
digital), WASPAA (aplicações de áudio), *IEEE Transactions on Signal Processing*
e *IEEE/ACM TASLP*. Pré-prints em arXiv (eess.SP, eess.AS, cs.SD).

---

## 9 · O que **não** mudou

Vale terminar por aqui, porque é o que dá estabilidade a quem estuda:

- **Nyquist (1928)** continua exato.
- **A FFT (1965)** continua sendo o algoritmo mais usado do campo.
- **Convolução, LTI, polos e zeros** continuam descrevendo todo sistema linear.
- **O princípio da incerteza** continua sendo um teorema, não uma limitação de
  ferramenta.
- **A equação do radiômetro** continua decidindo tempo de telescópio.
- **6,02·B + 1,76 dB** continua sendo a SNR de um quantizador.

A arquitetura de rede da moda tem meia-vida de dois anos. Estes resultados têm
décadas e não se mexeram. **É por isso que este curso ensina os dois, nesta
ordem.**

---

## Autoteste

1. Como o papel do DSP mudou entre 2005, 2015 e 2026?
2. Qual é a restrição tripla que os codecs neurais ainda não resolvem juntos?
3. Por que o cancelamento de eco continua híbrido?
4. Onde compressive sensing efetivamente se consolidou?
5. Qual é o gargalo prático dos conversores hoje?
6. Por que as métricas objetivas são um problema metodológico sério?
7. Qual o consenso emergente entre aprender e projetar?
8. Cite três resultados do campo que não mudaram e não vão mudar.

---

## Fontes consultadas

- ICASSP 2026 — tema oficial "Where Signals Meet Intelligence", tutoriais e
  workshops satélites (incl. desafio de codecs de baixo recurso), site oficial da
  conferência, consultado em 19/08/2026.
- Revisão de DSP diferenciável para síntese de música e fala (arXiv 2308.15422).
- Literatura recente sobre filtros all-pole e all-pass diferenciáveis e vocoders
  DDSP para realce de fala com poucos recursos (arXiv, 2024–2025).
- Panorama de codecs neurais e de tokenização de áudio, consultado em 14/08/2026.
- As avaliações de "o que está resolvido" e "o que não chega" são **opinião
  profissional do autor deste material**, e estão marcadas como tal no texto.
