# 02 · Pré-requisitos — o que saber, ter e instalar antes

`Nível: iniciante` · `Atualizado em: 14/08/2026`

Este é o arquivo que responde diretamente a **"o que de Matemática se deve
aprender?"** e **"por onde começar?"**. O curso de matemática em si — com as
contas feitas — está em [`12-matematica-do-zero.md`](12-matematica-do-zero.md).

---

## Resposta em trinta segundos

**Matemática indispensável, em ordem de importância:**

1. **Números complexos** (a·e^{jθ}, fasores) — ⚠️ é aqui que quase todo mundo trava
2. **Trigonometria de verdade** (seno como rotação, não como triângulo)
3. **Somatórios e séries geométricas**
4. **Cálculo básico** (derivada, integral, e o que é uma exponencial)
5. **Álgebra linear básica** (vetor, produto interno, matriz como transformação)
6. **Probabilidade básica** (média, variância, densidade, valor esperado)

**O que você NÃO precisa para começar:** análise real, equações diferenciais
parciais, teoria da medida, variável complexa formal (resíduos, Cauchy), topologia.
Nada disso. Vem depois, e só se você for para pesquisa.

**Tempo realista até "usar DSP com competência":** 4 a 6 meses de 6–8 h por semana,
se a matemática já estiver no lugar. Se não estiver, some 2 a 4 meses de matemática
— que podem ser feitos **em paralelo**, e devem.

**Por onde começar hoje, agora:** [`04-como-comecar.md`](04-como-comecar.md).
Não espere a matemática ficar pronta. Ninguém aprende Fourier sem antes ter visto
um espectro na tela e se perguntado por que ele tem aquela cara.

---

## Parte 1 · Conhecimento

### 1.1 Indispensável

#### Números complexos — o pré-requisito nº 1

**Por que:** porque em DSP *tudo* é complexo. A Transformada de Fourier devolve
números complexos. A transformada Z vive no plano complexo. Um filtro é descrito
por polos e zeros, que são números complexos. Um sinal de rádio moderno é
literalmente representado como I + jQ, um número complexo por amostra.

**O que exatamente saber:**

| Item | Por que importa em DSP |
|---|---|
| j² = −1, forma a + jb | notação básica; `1j` em Python |
| Plano complexo, módulo e fase | módulo = amplitude, fase = atraso. É a leitura de todo espectro |
| Fórmula de Euler: e^{jθ} = cos θ + j sen θ | **a equação mais importante do campo**. Une exponencial e rotação |
| Multiplicação = rotação + escala | é o que um filtro faz com cada frequência |
| Conjugado e simetria hermitiana | por que o espectro de sinal real é espelhado, e por que `rfft` existe |
| Círculo unitário, raízes da unidade | os "bins" da DFT são exatamente as N raízes da unidade |

**Como testar se você sabe o bastante:** você consegue explicar, sem consultar,
por que e^{jπ} = −1 e por que multiplicar por e^{jω} atrasa um sinal? Se sim, está
pronto. Se não, três a cinco dias de estudo resolvem.

**Onde aprender:** [`12-matematica-do-zero.md § 3`](12-matematica-do-zero.md) neste
curso; em vídeo, a série *Imaginary Numbers Are Real* (Welch Labs, YouTube, ~1 h,
inglês com legendas) e o *Essence of Linear Algebra* do 3Blue1Brown para a intuição
geométrica. Em português, o canal **Matemática Universitária** e as aulas de
Cálculo do **Univesp** cobrem o formal.

#### Trigonometria — mas a versão certa

Não é a do ensino médio (SOH-CAH-TOA em triângulos). É a versão **circular**:
seno e cosseno como coordenadas de um ponto girando num círculo, e ângulo como
tempo × velocidade angular.

Saber de cor: sen² + cos² = 1; as fórmulas de soma de ângulos (delas sai *tudo*
sobre modulação); o que significa ω = 2πf; a identidade produto→soma
(2·sen A·sen B = cos(A−B) − cos(A+B)), que é o coração da mixagem de rádio.

**Tempo:** 1 semana se estiver enferrujado. Ignorar isso é garantir sofrimento
depois.

#### Somatórios e séries

Notação Σ, troca de ordem de somatório, e a **soma geométrica**
Σₙ₌₀^{N−1} rⁿ = (1−r^N)/(1−r). Essa fórmula única aparece: na derivação da DFT,
na resposta em frequência de um FIR de média móvel, na estabilidade de IIR, na
função de transferência de um integrador. Uma fórmula, quatro usos.

**Tempo:** 2–3 dias.

#### Cálculo — só o essencial

| Precisa | Não precisa (por enquanto) |
|---|---|
| O que é derivada (taxa de variação) | Técnicas de derivação complicadas |
| O que é integral (área acumulada) | Técnicas de integração exóticas |
| Por que d/dt de e^{at} é a·e^{at} | Séries de Taylor formais, convergência |
| Integral de senoide num período = 0 | Integrais múltiplas, teoremas de Green/Stokes |
| Noção de limite e de infinitésimo | Épsilon-delta, análise real |

A rigor, **DSP puramente discreto quase não usa cálculo** — usa somatório. Cálculo
entra na parte contínua (sinais analógicos, transformada de Laplace, filtros
analógicos que viram digitais). Se você quer começar pelo digital, pode adiar.

**Tempo:** 3–4 semanas para o essencial; você provavelmente já tem metade.

#### Álgebra linear — mais importante do que dizem

| Item | Onde aparece |
|---|---|
| Vetor, norma, produto interno | um sinal **é** um vetor; correlação **é** produto interno |
| Base e mudança de base | Fourier é uma mudança de base. Essa frase é o curso inteiro em cinco palavras |
| Ortogonalidade | por que as senoides não "se misturam" na análise; por que dá para separar |
| Matriz como transformação linear | a DFT é uma matriz N×N; a FFT é fatorá-la de forma esperta |
| Autovalor e autovetor | senoides são os **autovetores** de todo sistema LTI. Isso explica por que Fourier funciona |
| Mínimos quadrados | filtro de Wiener, projeto de filtro ótimo, regressão |

Se você entender que **a Transformada de Fourier é uma projeção sobre uma base
ortogonal de senoides**, o campo inteiro fica dez vezes mais simples. É a única
percepção deste arquivo que eu insistiria em destacar.

**Tempo:** 3–4 semanas. A série *Essence of Linear Algebra* (3Blue1Brown, ~3 h)
dá a intuição em um fim de semana; o formal vem depois.

#### Probabilidade e estatística — o mínimo

Média, variância, desvio padrão, distribuição (gaussiana especialmente), valor
esperado, independência, correlação. Depois: processo estocástico, estacionaridade,
densidade espectral de potência.

**Por que:** ruído é aleatório. Sem probabilidade você sabe filtrar sinal limpo,
que não existe fora do laboratório.

**Tempo:** 2–3 semanas para o básico.

### 1.2 Ajuda muito (mas não bloqueia)

- **Programação em Python.** Não precisa ser bom: precisa saber escrever um laço,
  uma função, e usar NumPy. Se souber outra linguagem, três dias bastam.
  Alternativa: MATLAB/Octave, que é a língua franca acadêmica do campo.
- **Noção de eletrônica** (tensão, corrente, resistor, capacitor, filtro RC).
  Ajuda muito na intuição de filtros analógicos e do porquê de o campo ter nascido
  na engenharia elétrica. Não é bloqueante para quem só vai processar dados.
- **Equações diferenciais lineares.** Ajudam a entender de onde vem a transformada
  de Laplace. Adiável.
- **Física de ondas** (comprimento de onda, ressonância, propagação). Ajuda em
  acústica, radar e sísmica.
- **Inglês técnico de leitura.** Não bloqueia — este curso está em português —
  mas 90 % da literatura, da documentação e dos papers está em inglês.

### 1.3 O que NÃO é pré-requisito (e é dito por aí que é)

- **Ser engenheiro eletricista.** O campo nasceu ali, mas hoje há mais gente
  fazendo DSP em biomedicina, dados e áudio do que em telecom.
- **Análise complexa formal** (integrais de contorno, resíduos, Cauchy). Só na
  derivação rigorosa da transformada Z inversa. Você usa a transformada Z sem isso.
- **Teoria da medida / integral de Lebesgue.** Só em pesquisa teórica.
- **Saber montar circuito.** Zero necessário para o caminho digital.

---

## Parte 2 · Ambiente

### Hardware

| Item | Mínimo | Confortável | Comentário |
|---|---|---|---|
| CPU | qualquer x86-64 ou ARM dos últimos 10 anos | 4+ núcleos | FFT de áudio é barata; imagem e ML é que pesam |
| RAM | 4 GB | 8–16 GB | 1 min de áudio a 44,1 kHz em float64 = 21 MB. Vídeo é outra história |
| Disco | 5 GB | 20 GB | Python + SciPy + Matplotlib ≈ 1,2 GB; datasets de áudio, dezenas de GB |
| GPU | nenhuma | opcional | Só importa para DSP + aprendizado profundo (cap. [29](29-dsp-e-aprendizado-de-maquina.md)) |
| Áudio | nenhum | fone + microfone | Ouvir o resultado é meio caminho da intuição |

**Nada neste curso exige hardware especial.** O projeto-modelo roda em qualquer
máquina em menos de um segundo.

### Software

| Software | Versão mínima | Papel |
|---|---|---|
| Python | 3.10 | linguagem principal do curso |
| NumPy | 1.24 | vetores, FFT |
| SciPy | 1.10 | `scipy.signal`: filtros, janelas, espectrogramas |
| Matplotlib | 3.6 | gráficos — em DSP, **não plotar é trabalhar às cegas** |
| Jupyter (opcional) | 7.0 | ciclo de exploração rápido |
| Audacity (opcional) | 3.4 | ver e ouvir áudio sem programar |
| GNU Octave (opcional) | 8.0 | rodar código MATLAB de livros e papers, de graça |

Instalação completa, por sistema operacional, em [`03-instalacao.md`](03-instalacao.md).

### Conta em serviço

**Nenhuma é obrigatória.** Você pode fazer o curso inteiro sem criar conta em
lugar nenhum e sem gastar um centavo. Opcionais: Google Colab (grátis, roda no
navegador, útil se sua máquina for fraca) e GitHub (para versionar seus exercícios).

---

## Parte 3 · Tempo realista

Números honestos, para 6–8 h por semana de estudo consistente. Se você estudar
2 h por semana, multiplique por três — e note que abaixo de ~4 h/semana o
esquecimento come o progresso e o prazo tende ao infinito.

| Marco | Tempo | O que você consegue fazer |
|---|---|---|
| **Primeiro resultado na tela** | 1 tarde | Carregar um áudio, plotar espectro, achar a frequência dominante |
| **Usuário funcional** | 4–6 semanas | Projetar filtro passa-baixa/alta/faixa, entender aliasing, ler espectrograma, resolver 80 % dos problemas do dia a dia |
| **Praticante sólido** | 4–6 meses | Escolher entre FIR e IIR com argumento, projetar com especificação, entender fase e atraso de grupo, multitaxa, lidar com ruído |
| **Especialista aplicado** | 1,5–3 anos | Sistema completo em produção: tempo real, ponto fixo, restrição de latência, análise adaptativa, depurar o que ninguém entende |
| **Nível de pesquisa** | 4–6 anos (mestrado + doutorado) | Provar propriedades, publicar, criar método novo |

**Se a matemática não estiver no lugar**, some ao começo:

| Assunto | Tempo (do zero) | Pode estudar em paralelo com DSP? |
|---|---|---|
| Trigonometria circular | 1 semana | sim |
| Números complexos | 1–2 semanas | **não** — faça antes |
| Somatórios e séries | 3 dias | sim |
| Cálculo essencial | 3–4 semanas | sim |
| Álgebra linear essencial | 3–4 semanas | sim |
| Probabilidade essencial | 2–3 semanas | sim, adiável para depois do capítulo 20 |

**Opinião profissional:** o único que eu trataria como bloqueante é **números
complexos**. Os outros você aprende sob demanda, quando a necessidade aparece —
e aprende melhor assim, porque terá visto o problema antes da ferramenta.

---

## Parte 4 · Rota de resgate — o que fazer se faltar um pré-requisito

### "Não sei nada de números complexos"

Pare o DSP por uma semana. Leia [`12-matematica-do-zero.md § 3`](12-matematica-do-zero.md),
assista *Imaginary Numbers Are Real* (Welch Labs) e faça **este** exercício até
sair natural: em Python, calcule `np.exp(1j*np.pi)` e explique o resultado; depois
plote `np.exp(1j*2*np.pi*np.arange(100)/100)` no plano complexo e veja o círculo
aparecer. Quando o círculo fizer sentido físico para você, volte.

### "Meu cálculo está enferrujado"

Não pare. Siga o caminho **discreto**: capítulos [13](13-sinais-e-sistemas-lti.md),
[16](16-dft-e-fft.md), [18](18-filtros-fir.md) usam somatório, não integral.
Repõe cálculo em paralelo (Khan Academy em português, ~20 h) e volte para os
capítulos contínuos ([14](14-fourier.md), [17](17-transformada-z.md)) depois.

### "Nunca programei"

Faça 10 h de Python básico primeiro — variáveis, laços, funções, listas. Depois
2 h de NumPy (só `array`, indexação, operações elemento a elemento, `np.arange`,
`np.sin`). É genuinamente o suficiente para todo este curso. Sugestão em
português: *Curso em Vídeo* (Gustavo Guanabara) para Python, e a documentação
"NumPy: the absolute basics for beginners" para NumPy.

### "Não tenho tempo para o caminho longo"

Caminho mínimo viável, ~20 h totais, e você sai sabendo fazer coisa útil:

`01` → `03` → `04` → `06` (exemplos 1 a 5) → `15` (amostragem) → `16` (DFT/FFT)
→ `18` (FIR) → `75` (armadilhas) → `07-projeto-modelo/`

Você vai saber **fazer** e não vai saber **provar**. Para 90 % dos trabalhos, basta.
Se algum dia precisar provar, a base estará montada.

### "Estudo sozinho e não sei se estou entendendo"

Três testes que não mentem:

1. Você consegue **prever** o resultado antes de rodar o código? Se sempre roda
   primeiro e explica depois, ainda não entendeu.
2. Você consegue explicar para alguém sem usar as palavras "transformada",
   "domínio" e "espectro"?
3. Você reconhece o erro pelo sintoma? (som metálico → aliasing; eco → fase;
   raia que não deveria existir → vazamento espectral).

---

## Checklist antes de ir para o `03`

- [ ] Sei o que é um número complexo e o que e^{jθ} significa geometricamente.
- [ ] Sei que ω = 2πf e sei converter Hz ↔ rad/s.
- [ ] Consigo escrever um laço e uma função em Python (ou aceito 10 h para aprender).
- [ ] Tenho uma máquina com 4 GB de RAM e 5 GB de disco livre.
- [ ] Aceitei que vou começar a praticar **antes** de a matemática estar pronta.

---

## Autoteste

1. Qual é o único pré-requisito matemático que eu trataria como bloqueante, e por quê?
2. Por que álgebra linear é mais central em DSP do que o currículo típico sugere?
3. Cite dois assuntos frequentemente listados como pré-requisito que não são.
4. Quanto tempo, honestamente, até você projetar um filtro com especificação?
5. Você está com cálculo fraco. Qual caminho de capítulos seguir para não travar?
6. Por que praticar antes de dominar a teoria é recomendado aqui, e não o contrário?
7. Qual hardware este curso exige de fato?

---

**Próximo:** [`03-instalacao.md`](03-instalacao.md) — instalar tudo, em qualquer
sistema operacional, com verificação a cada passo. Ou, se quiser começar sem
instalar nada, pule direto para a primeira seção do `03`.
