# 80 · Custos e licenças

**Nível:** todos
**Data da consulta de preços: 14/08/2026**
**Câmbio usado: US$ 1,00 = R$ 5,19 · € 1,00 ≈ R$ 6,05** (cotação comercial de 14/08/2026;
preço sem data e sem câmbio é desinformação, então ambos ficam registrados aqui)

---

## Resumo em uma linha

**Estudar portas lógicas custa R$ 0,00.** Todas as ferramentas necessárias para percorrer
este curso inteiro — do [`01`](01-introducao-leigo.md) ao [`70`](70-pratica.md) — são
gratuitas e de código aberto. Você só gasta dinheiro se quiser tocar em hardware físico,
e mesmo aí o mínimo viável fica em torno de R$ 100.

**Quem paga a conta:** universidades (Logisim-evolution nasceu em Carnegie Mellon e é
mantido pela Haute École Spécialisée de Suisse occidentale e comunidade), professores
individuais (Digital, de Helmut Neemann), voluntários (Icarus Verilog, GTKWave), e
empresas que lucram em outro lugar — a AMD e a Intel dão suas ferramentas de FPGA de graça
porque vendem os chips; a SiFive e outras apoiam o RISC-V porque vendem IP e serviços.

---

## 1. Software — o que se usa neste curso

| Ferramenta | Licença | Custo | Observação |
|---|---|---|---|
| **Logisim-evolution 4.1.0** | GPL-3.0 | **R$ 0** | livre para uso comercial e educacional |
| **Digital 0.31** | GPL-3.0 | **R$ 0** | idem |
| **Icarus Verilog 13.0** | GPL-2.0+ | **R$ 0** | |
| **GTKWave** | GPL-2.0 | **R$ 0** | |
| **Surfer** (visualizador moderno) | EUPL-1.2 | **R$ 0** | alternativa ao GTKWave |
| **Yosys** (síntese) | ISC | **R$ 0** | permissiva, uso comercial livre |
| **nextpnr** | ISC | **R$ 0** | |
| **OpenROAD** | BSD-3 | **R$ 0** | |
| **Verilator** | LGPL-3 / Artistic-2.0 | **R$ 0** | simulador mais rápido que existe para RTL |
| **Python** | PSF | **R$ 0** | |
| **CircuitVerse** | MIT (o simulador) | **R$ 0** | serviço web gratuito |
| **Falstad Circuit Simulator** | GPL-2.0 | **R$ 0** | |
| **nandgame** | gratuito | **R$ 0** | |
| **VS Code** | MIT (código) / proprietária (binário da Microsoft) | **R$ 0** | use VSCodium se quiser 100% livre |

### 1.1 O que as licenças permitem, na prática

| Licença | Uso comercial | Modificar | Obrigação ao distribuir |
|---|---|---|---|
| **MIT / BSD / ISC / Apache-2.0** | sim | sim | manter o aviso de copyright |
| **LGPL** | sim | sim | publicar mudanças **na biblioteca**; pode ligar a código fechado |
| **GPL-2.0 / GPL-3.0** | sim | sim | **publicar o código-fonte do trabalho derivado** |
| **EUPL-1.2** | sim | sim | semelhante à GPL, com compatibilidade europeia |
| **PSF** | sim | sim | permissiva |

**O ponto que confunde todo mundo:** a GPL do Logisim **não** contamina os circuitos que
você desenha nele. Ela se aplica ao código do simulador, não ao seu trabalho. Você pode
vender um produto projetado no Logisim sem obrigação nenhuma — do mesmo modo que a licença
do GIMP não se aplica às imagens que você cria nele.

**Onde a GPL importa de verdade:** se você **modificar** o Logisim e distribuir a versão
modificada, precisa publicar o código. Só isso.

**Cuidado real, este sim:** os arquivos de descrição de tecnologia (PDKs) das foundries
comerciais são cobertos por NDA. Isso não afeta este curso — mas afeta quem for projetar
chip de verdade, e é a razão de os PDKs abertos (SKY130, GF180, IHP SG13G2) serem um
acontecimento.

---

## 2. Software proprietário de FPGA (opcional, não exigido)

| Ferramenta | Edição gratuita | Limite da gratuita | Preço da paga |
|---|---|---|---|
| **AMD Vivado** | ML Standard | dispositivos pequenos/médios; sem os maiores | Enterprise: milhares de dólares/ano por assento |
| **Intel/Altera Quartus Prime** | Lite | famílias de entrada (Cyclone, MAX) | Standard/Pro: milhares de dólares/ano |
| **Gowin EDA** | Education | exige cadastro; chave anual | comercial sob consulta |
| **Lattice Radiant/Diamond** | gratuita com licença | por dispositivo | comercial sob consulta |

**Custo oculto real dessas ferramentas:** 25 a 100 GB de disco, uma a três horas de
instalação, e licenças que **expiram e precisam ser renovadas** — inclusive as gratuitas.
Um projeto de estudo que fica parado seis meses volta com a licença vencida.

**Alternativa aberta, que recomendo para aprender:** `Yosys + nextpnr + IceStorm` (para
iCE40) ou `+ apicula` (para Gowin/Tang Nano). Instala em cinco minutos, ocupa ~500 MB, não
expira, e roda em qualquer máquina.

---

## 3. Hardware — quanto custa tocar no assunto

### 3.1 O caminho mais barato: CIs da série 7400

| Item | Preço no Brasil (14/08/2026, faixa observada em lojas de eletrônica) |
|---|---|
| CI 74HC00 (4 NANDs) | R$ 2 a R$ 6 por unidade |
| Kit com 10 CIs variados (00, 04, 08, 32, 86…) | R$ 40 a R$ 90 |
| Protoboard 830 pontos | R$ 20 a R$ 45 |
| Kit de jumpers | R$ 15 a R$ 35 |
| Fonte 5 V (ou módulo de alimentação para protoboard) | R$ 15 a R$ 40 |
| LEDs, resistores, chaves | R$ 20 a R$ 40 |
| **Bancada mínima completa** | **R$ 130 a R$ 250** |

*(Faixas típicas de varejo brasileiro em agosto de 2026; variam muito por loja, e componentes
importados diretamente costumam custar metade, com 30 a 60 dias de espera.)*

**Vale a pena?** Para o **aprendizado conceitual**, não — o simulador ensina mais rápido e
sem fiação errada. Para a **experiência física** de ver um circuito que você montou
funcionar, sim, e o efeito motivacional é real. Minha recomendação: faça os labs 1 a 9 no
simulador; se ainda quiser hardware, aí compre.

### 3.2 FPGAs — preços internacionais (14/08/2026)

| Placa | Preço (USD) | Em BRL* | Cadeia aberta? | Para quem |
|---|---|---|---|---|
| **Tang Nano 9K** | ~US$ 15 | ~R$ 78 | sim (apicula) | **melhor custo-benefício para começar** |
| Tang Nano 20K | ~US$ 30–40 | ~R$ 155–210 | sim | mais recursos |
| iCEBreaker / iCEstick | ~US$ 70–100 | ~R$ 360–520 | **sim (totalmente aberta)** | quem quer cadeia 100% livre |
| **Basys 3** (Xilinx Artix-7) | < US$ 150 | ~R$ 780 | não (Vivado) | padrão de disciplinas universitárias |
| **DE10-Lite** (Intel MAX 10) | ~US$ 150 | ~R$ 780 | não (Quartus) | idem, no ecossistema Intel |
| Arty A7-35T, Zybo Z7 | US$ 200–500+ | R$ 1.000–2.600 | não | projetos avançados |

*Conversão direta pelo câmbio, **sem** impostos. No Brasil, importação acrescenta tipicamente
60% de imposto de importação + ICMS estadual, o que pode **dobrar** o preço final. Uma placa
de US$ 15 pode chegar a R$ 160–200 com frete e tributos.

**Recomendação franca:** se for comprar uma primeira FPGA, compre uma **suportada pela
cadeia aberta** (Tang Nano ou iCE40). Instalar 80 GB de Vivado para acender um LED é a
experiência que mais faz gente desistir de hardware. E o Tang Nano 9K, a ~US$ 15, é
barato o suficiente para não doer se você não usar.

### 3.3 Fabricar silício de verdade

Este era, até poucos anos atrás, um número inacessível. Deixou de ser.

| Caminho | Custo | O que você recebe |
|---|---|---|
| **Tiny Tapeout** (1 tile) | **€ 70** (~R$ 425 / ~US$ 76) por tile; projetos analógicos exigem 2 tiles (mín. € 140) | seu circuito num chip real, mais placa de demonstração |
| Tiny Tapeout — pinos analógicos | € 40 por pino (primeiros 2), € 100 depois | |
| Shuttle acadêmico (Europractice, MOSIS) | milhares a dezenas de milhares de dólares | área maior, nós maduros |
| **Tapeout próprio, nó maduro (130–65 nm)** | US$ 50 mil a US$ 500 mil | máscaras + wafers |
| **Tapeout próprio, nó avançado (3–2 nm)** | **US$ 10 a 50 milhões** só de máscaras | — |

*(Preços do Tiny Tapeout conforme a página oficial de especificações e o FAQ, consultados em
14/08/2026. O valor por submissão varia por shuttle e por rodada — confira a calculadora no
site antes de orçar. Rodadas anteriores praticaram US$ 150 para as primeiras 100 submissões
individuais e US$ 300 depois, com tiles extras a US$ 50.)*

**A diferença de escala vale ser contemplada:** € 70 contra US$ 50 milhões. É a diferença
entre "um estudante brasileiro pode ter um chip seu" e "só uma empresa com faturamento
bilionário pode fabricar em nó avançado". Ambas as coisas são verdadeiras em 2026.

---

## 4. Custos ocultos

| Custo oculto | Onde aparece | Como evitar |
|---|---|---|
| **Tempo de instalação** | Vivado/Quartus: 1–3 h e 25–100 GB | use a cadeia aberta ou o navegador |
| **Licença gratuita que expira** | Vivado/Quartus/Gowin exigem renovação anual | anote a data; ou use ferramentas livres |
| **Impostos de importação** | placas FPGA compradas fora | pode dobrar o preço; considere revendedores nacionais |
| **Prazo de entrega** | componentes importados: 30–60 dias | compre com antecedência ou pague o preço nacional |
| **Aprisionamento em ferramenta** | projeto feito só em Vivado não abre em outra | mantenha o RTL genérico; isole o específico do fabricante |
| **Arquivos de onda (.vcd)** | um `$dumpvars` esquecido gera dezenas de GB | limite o escopo do dump; use FST em vez de VCD |
| **Formato de arquivo** | `.circ` do Logisim 4.x pode não abrir na 3.x | versione no git; guarde cópia antes de atualizar |
| **Curva de aprendizado das ferramentas** | o custo real deste assunto | é tempo, não dinheiro — e é o maior de todos |

---

## 5. Alternativas gratuitas e o que se perde ao trocar

| Ferramenta paga | Alternativa livre | O que se perde |
|---|---|---|
| Cadence/Synopsys (síntese ASIC) | **Yosys** | otimização de ponta, suporte a nós avançados, suporte comercial |
| Cadence Innovus (P&R) | **OpenROAD** | qualidade de resultado em projetos grandes, mas a distância diminuiu |
| ModelSim/Questa | **Icarus Verilog** / **Verilator** | suporte completo a SystemVerilog e UVM (o Verilator é mais rápido, porém só para RTL sintetizável) |
| Vivado (síntese Xilinx) | Yosys + nextpnr-xilinx | suporte a dispositivos recentes e a IP proprietário |
| MATLAB/Simulink HDL Coder | Python + cocotb, Amaranth, SpinalHDL | fluxo integrado com processamento de sinais |
| Altium/OrCAD (PCB) | KiCad | pouco, hoje — o KiCad ficou muito bom |

**Opinião profissional:** para **aprender**, as alternativas livres são melhores, porque
instalam rápido, cabem na cabeça e não escondem o que estão fazendo. Para **produzir chip
comercial em nó avançado**, ainda não há substituto para as ferramentas proprietárias — mas
a distância tem diminuído todo ano, e o OpenROAD já acumula mais de 600 tapeouts.

---

## 6. Quanto custa uma porta lógica, afinal?

Um exercício de perspectiva:

| Época | Custo aproximado por porta | Fonte do número |
|---|---|---|
| 1960 (transistor discreto) | ~US$ 5 | preço de componente da época |
| 1970 (CI de pequena escala) | ~US$ 0,10 | série 7400 |
| 1990 | ~US$ 0,0001 | |
| **2026 (nó avançado)** | **~US$ 0,00000001** (10⁻⁸) | derivado de ~US$ 20.000 por wafer, ~30 bi de transistores por chip, ~60 chips por wafer |

*(A última linha é uma estimativa minha, com as premissas declaradas; fabricantes não
publicam custo por transistor. Trate como ordem de grandeza.)*

Uma porta lógica hoje custa cerca de **um centésimo de milionésimo de dólar**. É por isso
que um projetista moderno gasta portas com liberdade: a ULA calcula oito operações e joga
sete fora ([`20`](20-circuitos-combinacionais.md)), o preditor de desvio usa mais silício
que a ULA ([`40`](40-da-porta-ao-computador.md)), e ninguém minimiza circuito à mão. O
recurso escasso deixou de ser a porta — passou a ser **energia, fios e tempo de projeto**.

Entender essa inversão econômica é entender por que o hardware de 2026 é como é.

---

## Autoteste

1. Quanto custa fazer este curso inteiro?
2. Quem paga a conta das ferramentas gratuitas de eletrônica digital?
3. A licença GPL do Logisim se aplica aos circuitos que você desenha nele? Justifique.
4. Qual o custo oculto mais frequente das ferramentas gratuitas de FPGA?
5. Qual placa FPGA você recomendaria a um iniciante brasileiro, e por quê?
6. Quanto custa fabricar um chip seu pelo Tiny Tapeout? E num nó de 2 nm?
7. Quanto custa aproximadamente uma porta lógica em 2026?
8. Que consequência de projeto essa economia produziu?
9. O que se perde ao trocar Cadence por Yosys+OpenROAD? E ao trocar Altium por KiCad?
10. Por que preço sem data e sem câmbio é desinformação?

*(Respostas: 1 — R$ 0,00; 2 — universidades, professores individuais, voluntários e
empresas que lucram vendendo chips ou IP; 3 — não: aplica-se ao código do simulador, não ao
seu trabalho; 4 — licenças gratuitas que expiram e exigem renovação, além de 25–100 GB de
instalação; 5 — Tang Nano 9K, por ~US$ 15 e com cadeia de ferramentas aberta;
6 — € 70 por tile contra US$ 10–50 milhões só de máscaras; 7 — da ordem de 10⁻⁸ dólares;
8 — gasta-se porta com liberdade: cálculo redundante, previsão de desvio cara, nenhuma
minimização manual; 9 — perde-se qualidade em projetos grandes e suporte a nós avançados;
com KiCad, hoje se perde muito pouco; 10 — porque preços e câmbio mudam, e um número sem
contexto temporal induz a decisão errada.)*

---

### Fontes consultadas (14/08/2026)

- Licenças verificadas nos repositórios oficiais: Logisim-evolution (GPL-3.0), Digital
  (GPL-3.0), Icarus Verilog (GPL-2.0+), Yosys (ISC), OpenROAD (BSD-3), Verilator
  (LGPL-3/Artistic-2.0).
- Tiny Tapeout — preços por tile e por pino analógico: https://tinytapeout.com/specs/analog/
  e https://tinytapeout.com/faq/ ; valores históricos de rodadas anteriores via
  Electronics-Lab e eeNews Europe.
- Preços de placas FPGA: levantamento de mercado internacional de agosto de 2026
  (Tang Nano 9K ~US$ 15; DE10-Lite ~US$ 150; Basys 3 abaixo de US$ 150).
- Câmbio USD/BRL de 14/08/2026: ~R$ 5,19 (cotação comercial; faixa de 52 semanas entre
  R$ 4,89 e R$ 5,61).
- Preços de componentes no varejo brasileiro: faixas típicas observadas em lojas de
  eletrônica em agosto de 2026. **Confira antes de comprar** — variam muito.
