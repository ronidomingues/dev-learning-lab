# 80 · Custos e licenças — quanto custa aprender e trabalhar com isso

`Nível: todos` · **Preços consultados em: 14–19/08/2026**
⚠️ **Preço sem data é desinformação.** Reconfira antes de decidir compra.
Valores em BRL usam câmbio aproximado de **US$ 1 ≈ R$ 5,40** (ordem de grandeza,
não cotação).

---

## Resposta na primeira linha

**Você pode fazer este curso inteiro, do zero ao nível de pesquisa, gastando
R$ 0,00.** Toda a pilha usada aqui — Python, NumPy, SciPy, Matplotlib, Octave,
Audacity, GNU Radio — é software livre. Nenhuma conta obrigatória, nenhum cartão
de crédito, nem no plano gratuito.

O resto deste arquivo é sobre **quando** faz sentido gastar, e em quê.

---

## 1 · Software livre — a pilha completa

| Software | Licença | O que ela permite comercialmente |
|---|---|---|
| **Python** | PSF (permissiva) | tudo, inclusive fechar o código |
| **NumPy, SciPy, Matplotlib** | **BSD-3** | tudo, inclusive produto proprietário |
| **scikit-learn, pandas** | BSD-3 | idem |
| **PyWavelets** | MIT | idem |
| **GNU Octave** | **GPL-3** | usar é livre; **distribuir código ligado** obriga a abrir |
| **Audacity** | GPL-2+ | idem (uso interno é livre) |
| **GNU Radio** | GPL-3 | idem — atenção ao distribuir blocos ligados |
| **FFTW** | **GPL-2** ou comercial | ⚠️ **dupla licença** — ver abaixo |
| **PortAudio, libsndfile** | MIT / LGPL | permissiva / ligação dinâmica |

### A distinção que importa juridicamente

- **BSD/MIT (permissivas):** use, modifique, embuta em produto fechado, venda.
  Só mantenha o aviso de copyright. **NumPy e SciPy são BSD** — é por isso que
  toda a indústria os usa sem preocupação.
- **GPL (copyleft):** usar o programa é livre. **Distribuir um trabalho derivado
  obriga a liberar o fonte sob GPL.** Rodar Octave para fazer suas contas não
  contamina nada; distribuir um produto que **incorpora** código GPL, sim.
- **LGPL:** permite ligação dinâmica sem contaminar; alterações na própria
  biblioteca precisam ser abertas.

⚠️ **A armadilha da FFTW:** é a biblioteca de FFT mais rápida que existe e é
**GPL-2**. Usá-la num produto proprietário exige **comprar licença comercial do
MIT**. Muita gente descobre isso tarde. **A SciPy não usa FFTW** — usa pocketfft,
que é BSD. Ou seja: a pilha deste curso está limpa para uso comercial.

**Quem paga a conta do software livre:** NumPy e SciPy são sustentados por
NumFOCUS (doações), financiamento de fundações (CZI, Sloan, Moore) e trabalho
pago por empresas que dependem deles. Não é caridade — é infraestrutura em que
grandes empresas investem porque usá-la é mais barato que reconstruí-la.

---

## 2 · MATLAB — quando vale, e quanto custa

**Preços consultados em 14/08/2026:**

| Licença | Preço | O que inclui | Em BRL (aprox.) |
|---|---|---|---|
| **Estudante** | **US$ 119/ano** | MATLAB + Simulink + 11 toolboxes | ~R$ 640/ano |
| **Home** | **US$ 165/ano** | MATLAB + 12 toolboxes | ~R$ 890/ano |
| **Signal Processing Toolbox** (comercial, avulso) | ~US$ 500/ano | só a toolbox | ~R$ 2.700/ano |
| Acadêmica institucional | varia | via convênio da universidade | frequentemente **grátis para o aluno** |
| Comercial completa | milhares de US$/ano | por toolbox | — |

⚠️ **Mudança importante em janeiro de 2026:** a MathWorks **descontinuou as
licenças perpétuas Home e Student**. Quem já tem uma perpétua pode continuar
usando indefinidamente, mas **não pode mais renovar manutenção nem acrescentar
toolboxes**. O modelo virou assinatura anual.

**Quando MATLAB vale o dinheiro:**

| Situação | Vale? |
|---|---|
| Sua universidade tem licença institucional | **sim** — é grátis para você, use |
| Você trabalha com Simulink / geração de código para embarcado | **sim** — não há equivalente livre maduro |
| Área que exige (aeroespacial, automotivo, certificação) | **sim** — é o padrão do setor |
| Precisa reproduzir código de paper ou livro | Octave resolve a maioria dos casos, de graça |
| Aprender DSP | **não** — Python faz tudo o que este curso precisa |
| Produção / serviço web | **não** — licenciamento de runtime complica |

**Minha recomendação profissional:** aprenda **Python**. Saiba **ler** MATLAB
(a tabela de equivalência está em [`05-manual-de-uso.md`](05-manual-de-uso.md)),
porque metade da literatura está nele. Use Octave quando precisar executar código
MATLAB alheio. Compre MATLAB só se Simulink ou o setor exigirem.

---

## 3 · Hardware

### Para o curso: R$ 0

Qualquer computador dos últimos 10 anos. Requisitos reais em
[`03-instalacao.md`](03-instalacao.md): 4 GB de RAM, 5 GB de disco.

### Áudio (opcional)

| Item | Faixa | Comentário |
|---|---|---|
| Fone razoável | R$ 150–600 | mais útil que caixas para ouvir detalhe |
| Interface de áudio USB | R$ 500–1.500 | só se for gravar com microfone decente |
| Microfone de medição | R$ 300–1.500 | para acústica de sala |

### SDR — rádio (preços de 14/08/2026)

| Hardware | Preço | Em BRL | Nota |
|---|---|---|---|
| **RTL-SDR Blog V4** | US$ 30–40 | ~R$ 160–215 | ⚠️ **produção encerrada** — o chip R828D acabou. Procure sucessor ou estoque |
| **ADALM-PLUTO** | US$ 100–250 | ~R$ 540–1.350 | TX **e** RX; da Analog Devices |
| **HackRF One** | ~US$ 340 | ~R$ 1.840 | TX/RX até 6 GHz |
| **USRP (Ettus)** | US$ 1.000+ | R$ 5.400+ | padrão de pesquisa |

⚠️ **Custos ocultos de importação no Brasil:** imposto de importação (60 % sobre
valor + frete) mais ICMS estadual podem **mais que dobrar** o preço final. Um
RTL-SDR de US$ 35 pode sair a R$ 400–500 na porta. Considere revendedores
nacionais.

### Embarcado

| Item | Preço | Uso |
|---|---|---|
| Raspberry Pi 5 | R$ 500–900 | processamento em tempo real, SDR |
| Placa Cortex-M4F (STM32, Teensy) | R$ 100–300 | DSP embarcado com CMSIS-DSP |
| FPGA iniciante (Tang Nano, iCEBreaker) | R$ 200–600 | aprender fluxo de FPGA |

---

## 4 · Nuvem e serviços

| Serviço | Camada gratuita | Onde ela acaba |
|---|---|---|
| **Google Colab** | grátis, sem cartão | sessão cai por inatividade; GPU limitada e imprevisível |
| Colab Pro | ~US$ 10/mês | mais tempo e GPU melhor |
| **Kaggle Notebooks** | 30 h/semana de GPU, grátis | limite semanal |
| **GitHub** | repositórios ilimitados | Actions tem minutos limitados no plano free |
| AWS/GCP/Azure | crédito inicial | **egress** é o custo oculto clássico |

⚠️ **Custo oculto nº 1 em nuvem: transferência de saída (egress).** Processar
áudio ou imagem na nuvem é barato; **baixar os resultados** pode custar mais que o
processamento. Datasets de áudio têm dezenas a centenas de GB.

**Para este curso, nada disso é necessário.** Tudo roda no seu computador.

---

## 5 · Custos ocultos, em geral

| Custo | Ordem de grandeza | Como evitar |
|---|---|---|
| **Tempo de aprendizado** | 4–6 meses × seu custo/hora | é o maior custo real, e ninguém o contabiliza |
| Aprisionamento em MATLAB | migração custa meses | escreva em Python desde o começo |
| Licença de biblioteca (FFTW) | de zero a milhares | verifique a licença **antes** de embutir |
| Importação de hardware | até 2× o preço | compre nacional quando possível |
| Egress de nuvem | surpresa na fatura | processe onde os dados estão |
| Dados anotados | caro se precisar de anotação humana | use bases públicas |
| Certificação (setores regulados) | dezenas de milhares | planeje desde o projeto |

---

## 6 · Alternativas livres a ferramentas pagas

| Pago | Livre | O que se perde |
|---|---|---|
| MATLAB | **Python + SciPy** | Simulink; geração de código certificada; toolboxes específicas |
| MATLAB | **GNU Octave** | desempenho; toolboxes; Simulink. Sintaxe ~compatível |
| Simulink | Scilab/Xcos, OpenModelica | maturidade e ecossistema |
| LabVIEW | Python + PyVISA | integração com instrumentos de bancada |
| Adobe Audition | **Audacity**, Ardour, Reaper (barato) | fluxo profissional |
| Wolfram | SymPy | simbólico avançado |
| Toolbox de wavelets | **PyWavelets** | pouca coisa; é boa |

**Onde o livre realmente perde:** geração automática de código **certificado**
para aviação/automotivo (DO-178C, ISO 26262). Aí o MATLAB/Simulink domina, e não
por marketing — a certificação da ferramenta faz parte do processo.

---

## 7 · Livros

Detalhe completo em [`90-bibliografia.md`](90-bibliografia.md). Resumo de custo:

| Categoria | Faixa |
|---|---|
| **Legalmente gratuitos** (dspguide.com, Think DSP, livros do Julius Smith) | R$ 0 |
| Usados / edições antigas | R$ 50–200 |
| Novos importados | R$ 400–900 |
| Nacionais | R$ 100–300 |

**Três livros excelentes e 100 % gratuitos e legais** cobrem do zero ao
intermediário. Não é preciso comprar nada para fazer este curso.

---

## 8 · Orçamentos sugeridos

| Perfil | Gasto | O que inclui |
|---|---|---|
| **Estudante autodidata** | **R$ 0** | tudo deste curso, com software livre e livros abertos |
| Entusiasta de rádio | R$ 200–500 | + um SDR (preferir compra nacional) |
| Praticante de áudio | R$ 300–1.000 | + fone decente e interface simples |
| Embarcado | R$ 300–1.000 | + placa Cortex-M ou FPGA de entrada |
| Profissional em setor regulado | R$ 5.000+/ano | + MATLAB/Simulink e toolboxes |

---

## Autoteste

1. Quanto custa fazer este curso inteiro? O que exatamente é grátis?
2. Qual a diferença prática entre BSD e GPL para quem vai vender um produto?
3. Por que a FFTW é uma armadilha, e por que a SciPy não é?
4. O que mudou nas licenças Home e Student do MATLAB em janeiro de 2026?
5. Em que três situações MATLAB vale o dinheiro?
6. Qual o custo oculto clássico de processar sinais na nuvem?
7. Por que um SDR de US$ 35 pode custar R$ 450 no Brasil?
8. Onde o software livre realmente perde para o pago?
9. Quem paga a conta do NumPy e do SciPy?

---

## Fontes consultadas

- Preços MATLAB (Student US$ 119/ano, Home US$ 165/ano, fim das licenças
  perpétuas em janeiro de 2026; Signal Processing Toolbox ~US$ 500/ano comercial)
  — consultado em 14/08/2026.
- Preços de SDR (RTL-SDR Blog V4 US$ 30–40 e descontinuação por falta do chip
  R828D; HackRF One ~US$ 340; ADALM-PLUTO US$ 100–250) — rtl-sdr.com e
  revendedores, consultado em 14/08/2026.
- Licenças verificadas na documentação oficial de cada projeto.
- Câmbio e impostos de importação: ordens de grandeza, não cotação do dia.
