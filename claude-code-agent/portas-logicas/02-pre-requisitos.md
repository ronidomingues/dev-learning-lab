# 02 · Pré-requisitos

**Nível:** iniciante · **Data:** 14/08/2026

Boa notícia antes de tudo: **portas lógicas é um dos assuntos com menor barreira de entrada
de toda a computação.** Não exige cálculo, não exige programação, não exige hardware caro.
Exige exatamente uma coisa: paciência para acompanhar tabelas de quatro linhas.

---

## 1. Conhecimento

### 1.1 Indispensável

| O que | Por quê | Onde aprender se faltar |
|---|---|---|
| **Ler uma tabela de duas colunas** | Toda porta é definida por uma tabela-verdade. Se você lê horário de ônibus, você já sabe. | — |
| **Contar em base 2 (binário)** | Circuitos operam sobre 0 e 1. Precisa saber que `1011` binário é 11 decimal. | Seção 2 deste arquivo — está ensinado aqui mesmo, em 5 minutos. |
| **Noção de "se… então"** | A lógica é isso. Você usa desde criança. | — |

**Não é indispensável:** eletrônica, física, cálculo, álgebra linear, programação, inglês.
Isso não é falsa modéstia do texto — o [`07-projeto-modelo/`](07-projeto-modelo/README.md)
foi escrito para ser lido por quem nunca programou, com cada linha comentada.

### 1.2 Ajuda muito

| O que | Onde ajuda | Onde aprender |
|---|---|---|
| **Programação básica em Python** | O projeto-modelo é em Python; sem isso você lê e roda, mas não modifica. | Curso "Python para Zumbis" (gratuito, PT) — ver [`85`](85-cursos-e-certificacoes.md). |
| **Aritmética binária** (soma, complemento de dois) | Entender somadores e ULA sem tropeçar. | [`20-circuitos-combinacionais.md`](20-circuitos-combinacionais.md), seção 2 — ensinado lá. |
| **Noção de tensão e corrente** | Entender por que a porta é feita assim e não de outro jeito. | [`12-do-transistor-a-porta.md`](12-do-transistor-a-porta.md) explica o mínimo necessário. |
| **Inglês de leitura** | 90% da documentação e das ferramentas. Os menus do Logisim têm português, mas os fóruns não. | — |
| **Matemática discreta / conjuntos** | Só para o [`60-teoria-avancada.md`](60-teoria-avancada.md). Nada antes. | Livro do Rosen — ver [`90`](90-bibliografia.md). |

### 1.3 Rota de resgate

Faltou algum pré-requisito? Não pare o curso — desvie:

| Falta | O que fazer **agora**, sem sair daqui |
|---|---|
| Binário | Leia a seção 2 abaixo. Leva 5 minutos e resolve. |
| Python | Leia o projeto-modelo como se fosse pseudocódigo — os comentários explicam o que cada linha faz. Rode com um comando só. |
| Aritmética binária | Pule direto para o [`04-como-comecar.md`](04-como-comecar.md); ela é construída lá, na prática. |
| Eletrônica | Ignore o [`12`](12-do-transistor-a-porta.md) na primeira leitura. O resto do curso não depende dele. |
| Paciência com instalação | Vá para a seção "Sem instalar nada" do [`03`](03-instalacao.md). Você começa em 30 segundos, no navegador. |

---

## 2. Binário em cinco minutos (o único pré-requisito que ensino aqui)

Você já sabe base 10. O número 275 significa:

```
  2×100  +  7×10  +  5×1
= 2×10²  +  7×10¹ +  5×10⁰
```

Cada casa vale 10 vezes mais que a anterior, e cada casa aceita 10 símbolos (0 a 9).

Binário é a mesma coisa com o número 2 no lugar do 10. Cada casa vale o **dobro** da
anterior, e cada casa aceita **dois** símbolos (0 e 1):

```
  1 0 1 1
  │ │ │ └── 1×1  = 1
  │ │ └──── 1×2  = 2
  │ └────── 0×4  = 0
  └──────── 1×8  = 8
                 ────
                   11
```

Logo, `1011` em binário é **11** em decimal. Só isso.

Os valores das casas, que vale decorar até a oitava:

| Casa | 8ª | 7ª | 6ª | 5ª | 4ª | 3ª | 2ª | 1ª |
|---|---|---|---|---|---|---|---|---|
| Vale | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |

**Vocabulário que vem junto:**

- **bit** — uma casa binária. Um 0 ou um 1. (De *binary digit*.)
- **byte** — 8 bits. Guarda de 0 a 255 (são 2⁸ = 256 combinações).
- **nibble** — 4 bits, meio byte. O projeto-modelo trabalha com nibbles.
- **palavra (*word*)** — quantos bits o processador manipula de uma vez. Hoje, tipicamente 64.

**Teste rápido:** quanto vale `1100 0001`?
*(Resposta: 128 + 64 + 1 = 193.)*

Se você acertou, tem todo o pré-requisito matemático deste curso.

---

## 3. Ambiente

### 3.1 Hardware — o que é preciso de verdade

| Item | Mínimo | Confortável | Observação |
|---|---|---|---|
| Processador | qualquer um dos últimos 15 anos | — | simular portas é leve |
| Memória RAM | 4 GB | 8 GB | Logisim é em Java, quer ~1 GB |
| Disco | 2 GB livres | 10 GB | com FPGA proprietária, 50–100 GB (ver abaixo) |
| Tela | 1366×768 | 1920×1080 | diagramas de circuito ocupam espaço |
| Placa de vídeo dedicada | **não** | — | nada aqui usa GPU |
| Internet | só para baixar | — | tudo roda offline depois |
| **Hardware físico (FPGA, protoboard)** | **não** | opcional | Ver seção 3.4 |

> **Opinião profissional:** o instinto de comprar componentes antes de entender o assunto
> desperdiça dinheiro e adia o aprendizado. Faça o curso inteiro em simulador. Se ao final
> você ainda quiser tocar em hardware, aí sim compre — e saberá exatamente o quê.

### 3.2 Sistema operacional

Tudo funciona nos três. Sem exceção e sem asterisco:

| SO | Situação | Observação |
|---|---|---|
| **Linux** (Debian/Ubuntu, Fedora/RHEL, Arch) | ✅ ideal | tudo por gerenciador de pacotes |
| **macOS** (Intel e Apple Silicon) | ✅ ótimo | Homebrew resolve tudo; Logisim precisa de Java ARM nativo no Apple Silicon |
| **Windows 10/11** | ✅ bom | Logisim/Digital nativos; para Verilog, **WSL2 é o caminho recomendado** |
| **ChromeOS / tablet / celular** | 🟡 parcial | só as ferramentas de navegador (CircuitVerse, Falstad, nandgame) — que dão conta de 70% do curso |

### 3.3 Software — o que instalar

Detalhe passo a passo no [`03-instalacao.md`](03-instalacao.md). Resumo do que se instala e por quê:

| Ferramenta | Versão de referência (14/08/2026) | Para quê | Obrigatório? |
|---|---|---|---|
| **Java (JDK) 21+** | Temurin 21 LTS | Logisim-evolution roda sobre Java | sim, se usar Logisim |
| **Logisim-evolution** | 4.1.0 (15/02/2026) | desenhar e simular circuitos com mouse | **recomendado** |
| **Digital** | 0.31 | alternativa mais leve ao Logisim, ótima para ensino | opcional |
| **Python** | 3.11+ | projeto-modelo e exercícios | **sim** |
| **Icarus Verilog** | 13.0 | descrever circuitos em texto (HDL) e simular | intermediário em diante |
| **GTKWave / Surfer** | conforme distro | ver formas de onda no tempo | junto com Verilog |
| **Editor de texto** | VS Code, Kate, Notepad++ | escrever Verilog/Python | sim |
| **Vivado / Quartus** | 2026.x | levar o circuito para FPGA real | **não** — 50–100 GB, só se tiver placa |

### 3.4 Conta em serviço

**Nenhuma é obrigatória.** Não existe paywall neste assunto. Opcionais:

| Serviço | Para quê | Grátis? |
|---|---|---|
| CircuitVerse.org | simulador no navegador, salva projetos | sim, conta gratuita |
| EDA Playground | rodar Verilog no navegador | sim, exige cadastro |
| Coursera (Nand2Tetris) | curso completo | sim no modo *audit* |
| GitHub | baixar ferramentas, versionar seus circuitos | sim |

Nenhum deles pede cartão de crédito para o que este curso usa.

---

## 4. Tempo realista até cada nível

Estas estimativas assumem estudo **com as mãos** (fazendo os laboratórios), não leitura passiva.
Leitura passiva rende cerca de um terço disso e some da memória em duas semanas.

| Nível | O que você consegue fazer | Tempo | Arquivos |
|---|---|---|---|
| **Curiosidade satisfeita** | Explicar o que é uma porta e responder a pergunta do título para alguém. | **1–2 horas** | `01`, `50` |
| **Alfabetizado** | Ler um diagrama, montar AND/OR/NOT no simulador, escrever tabela-verdade. | **6–10 horas** | `01`–`06`, `10` |
| **Funcional** | Projetar somador, multiplexador, contador; simplificar por Karnaugh. | **30–50 horas** | + `20`, `70` (lab. 1–7) |
| **Competente** | Projetar uma ULA e uma máquina de estados; entender timing, setup/hold. | **80–120 horas** | + `30`, `40`, projeto-modelo |
| **Profissional júnior de hardware** | Escrever Verilog sintetizável, fechar timing, rodar em FPGA. | **6–12 meses** | tudo + FPGA real + livro do Harris |
| **Pesquisa** | Ler papers de complexidade de circuitos e contribuir. | **anos** | `60`, `65` + pós-graduação |

**Honestidade sobre esses números:** os três primeiros níveis são atingíveis por qualquer
pessoa disciplinada, e a maioria das pessoas se surpreende com a rapidez. O salto do
"competente" para o "profissional" é onde 90% desiste, e o motivo quase nunca é
dificuldade conceitual — é que projetar hardware de verdade envolve ferramentas
pesadas, lentas e mal documentadas, e o ciclo de tentativa e erro passa de segundos
para dezenas de minutos. Isso desanima. Saiba disso antes.

### Uma calibragem útil

Um curso universitário de "Sistemas Digitais" ou "Circuitos Lógicos" tem tipicamente
**60 a 80 horas-aula** e cobre daqui até o [`30`](30-circuitos-sequenciais.md). Se você
chegar ao final do `30` com os laboratórios feitos, você cobriu a disciplina inteira.
O [`40`](40-da-porta-ao-computador.md) em diante já é "Arquitetura de Computadores",
a disciplina seguinte.

---

## 5. Checklist antes de seguir para o `03`

- [ ] Sei converter `1011` para decimal sem consultar tabela.
- [ ] Sei o que são bit, byte e nibble.
- [ ] Tenho um computador com 4 GB de RAM e 2 GB livres em disco.
- [ ] Aceito que **não** preciso comprar nada.
- [ ] Sei que, se a instalação me irritar, existe a saída pelo navegador no [`03`](03-instalacao.md).

---

## Autoteste

1. Qual é o único pré-requisito matemático real deste assunto?
2. Quanto vale `0110 0100` em decimal?
3. Você precisa de placa FPGA para fazer este curso? E de placa de vídeo?
4. Quanto tempo, sendo honesto, até conseguir projetar um somador do zero?
5. Qual é a rota de resgate para quem não sabe Python?
6. Por que o texto recomenda **não** comprar hardware no começo?
7. Qual ferramenta você instalaria se tivesse tempo para instalar apenas uma?

*(Respostas: 1 — numeração binária; 2 — 64+32+4 = 100; 3 — não e não; 4 — ~30–50 h de estudo com as mãos; 5 — ler o projeto-modelo como pseudocódigo, rodando com um comando; 6 — desperdiça dinheiro antes de você saber o que precisa, e adia o estudo; 7 — Logisim-evolution, ou nenhuma, usando CircuitVerse no navegador.)*
