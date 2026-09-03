# 65 · Estado da arte — agosto de 2026

**Nível:** pesquisa · **Data de levantamento: 14/08/2026**
**Este arquivo envelhece rápido.** Nós de fabricação, contagens de transistores e status de
projetos mudam a cada trimestre. Confira as fontes no rodapé antes de citar qualquer número.

---

## 1. Onde está a fabricação, hoje

### 1.1 Os nós de 2 nm entraram em produção

| Foundry | Nó | Situação (ago/2026) | Transistor |
|---|---|---|---|
| **TSMC** | N2 | **produção em volume desde o 4º trimestre de 2025** | nanosheet (GAA) de 1ª geração, **sem** backside power |
| **Intel** | 18A | **HVM desde o 4º trimestre de 2025** | RibbonFET (GAA) + **PowerVia** (backside power) |
| Samsung | SF2 | em rampa | GAA |
| TSMC | N2P / N2X | melhorias incrementais ao longo de 2026 | GAA |
| TSMC | **A16** | primeiro nó com GAA **+ backside power**; previsto para o 2º semestre de 2026, com rampa de produtos deslocada para 2027 | GAA + Super Power Rail |
| TSMC | A14 | previsto para 2028 | nanosheet de 2ª geração |

**Duas mudanças estruturais valem entender, porque afetam o que "uma porta" é fisicamente:**

**Nanosheet / GAA (*gate-all-around*).** No FinFET (2011–2024), a porta do transistor
envolvia o canal por três lados. No nanosheet, o canal é uma pilha de lâminas horizontais
e a porta o envolve pelos **quatro lados**. Controle eletrostático melhor significa menos
fuga e possibilidade de tensão mais baixa — o que ataca diretamente o problema que matou
a escala de Dennard. E a largura do canal passa a ser ajustável de forma contínua, o que dá
ao projetista um grau de liberdade novo para dimensionar portas.

**Backside power delivery (PowerVia, Super Power Rail).** A alimentação passa a chegar pela
**parte de trás** do wafer, separada dos fios de sinal na frente. Ganhos: menos queda de
tensão (IR drop), mais espaço para roteamento de sinal na frente, células mais densas.
Custo: um processo de fabricação significativamente mais complexo. A Intel colocou isso em
produção primeiro — foi a aposta técnica da empresa para retomar liderança.

### 1.2 O que vem depois: CFET

O **CFET** (*complementary FET*) empilha o transistor tipo N **em cima** do tipo P, em vez
de lado a lado. Como toda porta CMOS precisa dos dois, empilhá-los reduzirá drasticamente a
área da célula — é o próximo grande salto de densidade previsto.

**Situação em agosto de 2026:** pesquisa e demonstrações. O roteiro da imec de 2026 posiciona
o CFET como viável apenas em nós muito posteriores (a projeção pública fala em "0,7 nm", com
a régua de nomenclatura chegando a 0,3 nm por volta de 2038). **Não espere CFET em produto
antes do fim da década.**

### 1.3 O que "2 nm" significa, e não significa

**Nada mede 2 nanômetros.** Desde ~2000, o nome do nó é marketing, não dimensão física.
O comprimento de porta real em um nó "2 nm" está na casa de 12–20 nm.

O que ainda tem significado técnico: **densidade de transistores** (MTr/mm²), **altura de
célula** em pistas de metal (*track height*), e o **CPP** (*contacted poly pitch*). A própria
imec, em 2026, tem argumentado publicamente por redefinir a métrica em torno de **tamanho de
célula** em vez do nome do nó — reconhecimento oficial de que a nomenclatura perdeu o sentido.

**Se você for comparar chips, compare MTr/mm² ou área da célula padrão. Não compare nomes.**

---

## 2. As maiores contagens de transistores de 2026

| Chip | Transistores | Observação |
|---|---|---|
| **Nvidia Rubin** (GPU) | **336 bilhões** | N3P customizado; maior contagem em um acelerador |
| Nvidia Vera (CPU) | 227 bilhões | |
| Apple M5 | ~28 bilhões | N3E |
| Micron V-NAND 2 TB (flash) | 5,3 trilhões | **memória: nenhum é porta lógica** |

**A tendência que esses números escondem:** os maiores chips já não são um único pedaço de
silício. São **chiplets** — vários dies menores, fabricados possivelmente em nós diferentes,
ligados por interposer ou empilhamento 3D. Isso muda a economia: o die pequeno tem melhor
rendimento de fabricação (menos área, menos chance de defeito fatal), e cada função pode
usar o nó mais adequado. Lógica no nó mais avançado; E/S analógica, que não escala bem, em
um nó maduro e barato.

**Consequência para a contagem de portas:** a pergunta "quantas portas tem este chip" fica
ainda mais ambígua, porque "este chip" passou a ser um pacote com várias peças, incluindo
memória empilhada (HBM) que não é lógica nenhuma.

---

## 3. Onde a lógica não escala mais — e o que se faz a respeito

Três limites simultâneos, todos ativos em 2026:

| Limite | O que trava | Resposta da indústria |
|---|---|---|
| **Potência** | Dennard morreu em ~2005; densidade de potência é o teto | silício escuro, aceleradores, DVFS, near-threshold |
| **Fios** | interconexão domina atraso e energia desde ~130 nm | backside power, empilhamento 3D, óptica no pacote |
| **Memória** | mover um dado da DRAM custa ~100× mais energia que somá-lo | HBM, cache maior, **computação em memória** |

### 3.1 Computação em memória (*in-memory computing*)

A ideia: fazer a operação **onde o dado está**, em vez de trazê-lo até a ULA. Um array de
memristores ou de células SRAM pode realizar uma multiplicação matriz-vetor em uma única
operação analógica, aproveitando a lei de Ohm e a lei de Kirchhoff em vez de portas
lógicas.

**Situação em 2026:** aceleradores comerciais para inferência de IA existem, e o ganho de
eficiência em cargas específicas é real (uma a duas ordens de grandeza). **Mas** a
computação é analógica, com precisão limitada e sensível a variação de fabricação e
temperatura. Não substitui lógica digital de uso geral, e a minha leitura é que não
substituirá — é um acelerador de domínio, como a GPU foi.

### 3.2 Lógica de limiar e computação aproximada

Redes neurais toleram erro. Isso abriu espaço para **computação aproximada**: somadores que
erram o bit menos significativo em troca de metade da área, multiplicadores de baixa
precisão, formatos de 8 e 4 bits (e blocos de microescala, como MXFP4/MXFP6) que dominam
a inferência em 2026.

**A mudança conceitual é grande e vale registrar:** por 70 anos, a premissa foi que o
circuito digital **nunca erra**. Aceleradores modernos trocam exatidão por eficiência de
forma deliberada. É a primeira vez que se afrouxa essa premissa em produtos de massa.

---

## 4. Ferramentas: IA projetando circuitos

| Uso | Situação em 2026 |
|---|---|
| **Place & route por aprendizado por reforço** | em produção em várias empresas; ganhos de alguns por cento em área e potência, e principalmente em **tempo de projeto** |
| Geração de RTL por LLM | assistência real (testbenches, boilerplate, tradução); **não** substitui projetista |
| Verificação assistida por LLM | promissora para gerar estímulos e propriedades; a verificação formal continua sendo o que decide |
| Otimização de biblioteca de células | ativa |

**Opinião profissional, e é opinião:** a parte da IA em EDA que mais entregou valor até
agora não é gerar circuitos — é **explorar o espaço de configuração** das ferramentas
existentes, que sempre tiveram centenas de parâmetros ajustados por intuição humana. Isso
é aprendizado por reforço fazendo o que ele faz melhor, e é uma vitória menos glamorosa e
mais real que "IA projeta chip".

Houve, em 2020–2021, uma controvérsia acadêmica intensa sobre a reprodutibilidade dos
ganhos publicados no *floorplanning* por RL. Trate resultados dessa área com o ceticismo
que se aplica a qualquer benchmark divulgado por quem o vende.

---

## 5. Silício aberto — a democratização em curso

Este é o desenvolvimento que mais muda a vida de quem estuda o assunto.

| Peça do ecossistema | Situação em agosto de 2026 |
|---|---|
| **Yosys** (síntese) | maduro, usado em produção e em pesquisa |
| **OpenROAD** (place & route) | qualidade em melhora contínua; **600+ tapeouts** em SKY130 e GF180 por programas de shuttle |
| **PDKs abertos** | SkyWater SKY130, GlobalFoundries GF180, **IHP SG13G2** (130 nm BiCMOS, alemão) |
| **Tiny Tapeout** | shuttles ativos em 2026 (IHP, SkyWater, GlobalFoundries), com entregas previstas entre outubro/2026 e 2027 |
| **Efabless** | **encerrou as atividades em março de 2025** — o Tiny Tapeout migrou para o IHP e para outros parceiros |
| Cadence + SkyWater | programa de shuttle aberto, com janela de submissão fechada em janeiro/2026 e entrega prevista para julho/2026 |

**O que isso significa na prática:** por algumas centenas de dólares, um estudante pode ter
**seu próprio circuito fabricado em silício real**. Isso era impensável há dez anos, quando
o mínimo eram dezenas de milhares de dólares e um NDA.

O fechamento da Efabless em 2025 é um lembrete de que o ecossistema ainda é frágil e
depende de financiamento incerto. Mas o Tiny Tapeout sobreviveu à transição, o que é um
bom sinal de resiliência.

**Recomendação:** se você chegar ao fim deste curso e quiser hardware de verdade,
Tiny Tapeout é o caminho mais curto entre "entendi portas lógicas" e "tenho um chip meu
na mão". Ver [`80-custos-e-licencas.md`](80-custos-e-licencas.md) para preços.

---

## 6. RISC-V — a arquitetura aberta amadureceu

O RISC-V deixou de ser curiosidade acadêmica. Em 2026:

- extensões vetoriais (RVV 1.0) e de matriz consolidadas;
- núcleos de alto desempenho em desenvolvimento por várias empresas;
- adoção massiva em controladores embarcados dentro de chips maiores (o núcleo de
  gerenciamento de energia do seu SoC provavelmente é RISC-V);
- ecossistema de software (Linux, LLVM, GCC) maduro.

**Por que isso importa para portas lógicas:** o RISC-V é a única arquitetura moderna cujo
manual você pode ler inteiro em um fim de semana e cuja implementação você pode construir
com o conhecimento deste curso. Existem implementações educacionais de código aberto com
poucos milhares de linhas de Verilog. É o caminho natural depois do
[projeto-modelo](07-projeto-modelo/README.md).

---

## 7. Computação quântica — status franco

Agosto de 2026, do noticiário técnico do mês:

- vários fornecedores anunciando contagens de **qubits lógicos na faixa de 90 a 100**;
- latências de decodificação de erro caindo para a faixa de sub-microssegundo;
- a D-Wave publicou na *Nature* trabalho com qubits de "apagamento" em trilho duplo, com
  fidelidade de dois qubits próxima de 99,9%;
- a Pasqal demonstrou aprisionamento de átomos neutros **em chip**, via circuitos fotônicos
  integrados, apontando para escala de manufatura;
- financiamento em alta, incluindo programas públicos (um consórcio liderado pela UCLA
  recebeu US$ 4 milhões da NSF para um alvo de 60 qubits lógicos).

**Leitura honesta:** o progresso em **correção de erro** é real e é a métrica que importa —
qubits físicos brutos deixaram de ser notícia relevante há anos. Mas "90 a 100 qubits
lógicos" ainda está muito longe dos milhares necessários para quebrar criptografia ou
resolver problemas industriais de porte. E nada disso compete com portas lógicas clássicas
para computação de uso geral: são domínios diferentes.

Trate anúncios de empresas do setor com o ceticismo apropriado a uma área com muito capital
e muita necessidade de manchete.

---

## 8. Fronteiras de pesquisa em lógica

| Linha | Promessa | Situação realista em 2026 |
|---|---|---|
| **Lógica adiabática/reversível** | dissipação próxima do limite de Landauer | protótipos; lenta e cara em área |
| **Lógica superconditora (RSFQ/AQFP)** | 100× menos energia, dezenas de GHz | precisa de 4 K; nicho (leitura de qubits, HPC especializado) |
| **Spintrônica / lógica magnética** | não volátil, sem corrente de fuga | pesquisa; lenta comparada a CMOS |
| **Fotônica integrada** | comunicação sem perda resistiva | **vencendo em interconexão** (óptica no pacote), não em lógica |
| **Transistores 2D (MoS₂, grafeno)** | canal de um átomo de espessura | pesquisa; fabricação em escala é o obstáculo |
| **Empilhamento 3D de lógica** | mais transistores por área de wafer | **em produção**: memória sobre lógica, chiplets empilhados |
| **Nós criogênicos** | CMOS a 77 K ganha desempenho e eficiência | nicho; o custo do resfriamento raramente compensa |

**Minha aposta, e é aposta:** de tudo nessa lista, o que já está mudando produtos é o
**empilhamento 3D** e a **fotônica na interconexão**. O restante é pesquisa legítima com
horizonte longo. A lógica em si continuará sendo CMOS por, no mínimo, uma década — não
porque não haja alternativas, mas porque a infraestrutura de fabricação do CMOS representa
um investimento acumulado de trilhões de dólares, e nenhum concorrente é melhor o
suficiente para justificar recomeçar.

---

## 9. O que **não** mudou, e provavelmente não vai mudar

Depois de percorrer nanosheet, backside power, CFET, quântico e fotônica, vale registrar o
que continua exatamente igual:

- A **tabela-verdade** do AND é a mesma de 1847.
- **NAND continua funcionalmente completa**, e continua sendo a porta mais barata em CMOS.
- O **flip-flop D mestre-escravo** continua sendo o elemento de memória padrão.
- **Setup, hold e a equação de f_max** continuam valendo, e continuam sendo o que faz um
  projeto funcionar ou não.
- **Metaestabilidade** continua sem cura, só com mitigação.
- **Mover dados continua custando mais que computá-los** — e a distância só aumentou.

Tudo o que este curso ensina do [`10`](10-fundamentos.md) ao [`40`](40-da-porta-ao-computador.md)
sobreviveu a cinco substituições completas da camada física. É bastante razoável apostar
que sobreviverá à sexta.

---

## Autoteste

1. Qual a diferença entre FinFET e nanosheet/GAA, e que problema o GAA ataca?
2. O que é backside power delivery, e qual o custo dele?
3. "2 nm" mede o quê? Que métricas ainda têm significado?
4. O que é CFET e quando esperar produtos?
5. Por que chiplets tornam a pergunta "quantas portas tem este chip" ainda mais ambígua?
6. Quais são os três limites simultâneos da escalabilidade em 2026?
7. O que é computação em memória, e qual sua limitação fundamental?
8. Qual premissa de 70 anos os aceleradores de IA afrouxaram?
9. Qual uso de IA em EDA entregou mais valor real até agora?
10. Quanto custa, hoje, fabricar um circuito próprio em silício, e por qual caminho?
11. Por que "90 a 100 qubits lógicos" ainda não ameaça a criptografia?
12. Cite três coisas deste curso que não mudaram apesar de tudo isso.

*(Respostas: 1 — a porta envolve o canal pelos quatro lados em vez de três, atacando fuga e
permitindo tensão mais baixa; 2 — alimentação pela parte de trás do wafer, com ganho de
densidade e queda de tensão, ao custo de processo muito mais complexo; 3 — é nome comercial,
nada mede 2 nm; use MTr/mm², altura de célula e CPP; 4 — empilhar o transistor N sobre o P;
não antes do fim da década; 5 — porque o produto é um pacote com vários dies, incluindo
memória; 6 — potência, fios e memória; 7 — computar onde o dado está, com limitação de
precisão por ser analógica; 8 — a de que o circuito digital nunca erra; 9 — explorar o
espaço de parâmetros das ferramentas existentes; 10 — algumas centenas de dólares, via
Tiny Tapeout; 11 — porque seriam necessários milhares de qubits lógicos, não dezenas;
12 — tabela-verdade, completude do NAND, flip-flop D, setup/hold, metaestabilidade, e o
custo de mover dados.)*

---

### Fontes consultadas (14/08/2026)

- Wikipedia, *Transistor count* — Nvidia Rubin (336 bi), Vera (227 bi), Apple M-series,
  Micron V-NAND 2 TB (5,3 tri).
- Status de N2/18A em produção em volume desde o 4º tri de 2025; A16 previsto para o 2º
  semestre de 2026 com rampa deslocada para 2027; A14 para 2028 — compilado de
  https://www.tsmc.com/english/dedicatedFoundry/technology/logic/l_2nm, IEEE Spectrum
  (*TSMC's N2 Technology*), SemiAnalysis (*Clash of the Foundries*) e SemiWiki, consultados
  em 14/08/2026.
- Roteiro da imec de 2026 (CFET em nós muito posteriores; redefinição da métrica em torno
  de tamanho de célula) — via Tom's Hardware, consultado em 14/08/2026.
- Silício aberto: Tiny Tapeout (shuttles TTIHP26b, TTSKY26c, TTGF26a/b em 2026; entregas
  de out/2026 em diante) — https://tinytapeout.com/chips/ ; encerramento da Efabless em
  março de 2025 e migração para o IHP — Hackster.io; OpenROAD com 600+ tapeouts em SKY130
  e GF180 — documentação do OpenROAD. Todos consultados em 14/08/2026.
- Quântica, agosto de 2026: D-Wave (*Nature*, qubits de apagamento em trilho duplo,
  fidelidade ~99,9%), Pasqal (átomos neutros em chip via fotônica integrada, 10/08/2026),
  consórcio da UCLA (US$ 4 mi da NSF, 60 qubits lógicos, 08/08/2026) — via Forbes e
  agregadores do setor, consultados em 14/08/2026.
