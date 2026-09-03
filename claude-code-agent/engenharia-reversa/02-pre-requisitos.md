# 02 · Pré-requisitos

**Nível:** iniciante · **Data:** 03/09/2026

Engenharia reversa é uma disciplina de *segundo andar*: ela pisa em cima de várias outras.
Você **não precisa dominar** tudo antes de começar — mas precisa saber o suficiente para
não travar. Este arquivo separa o **indispensável** do **ajuda muito**, diz onde aprender
cada coisa, e dá uma **rota de resgate** honesta se faltar algo.

---

## Conhecimento

### Indispensável (sem isso você trava no primeiro dia)

| Você precisa saber | Por quê | Onde aprender |
|---|---|---|
| **Operar o terminal** (Linux/macOS ou WSL): `cd`, `ls`, pipes, executar programas | Todo o ferramental é de linha de comando | [`curso-docker`](../curso-docker/) tem uma base; ou "The Missing Semester of Your CS Education" (MIT, grátis) |
| **Ler e escrever C básico**: variáveis, ponteiros, funções, `struct`, arrays, `malloc` | O binário é C compilado; você precisa reconhecer o que virou o quê | Livro *C Programming: A Modern Approach* (K. N. King); ou "Harvard CS50" (grátis) |
| **Sistemas numéricos**: binário, **hexadecimal**, conversões, complemento de dois | Endereços, opcodes e valores aparecem em hex o tempo todo | Seção "Fundamentos" abaixo; qualquer intro de arquitetura de computadores |
| **Noção de como um programa roda**: memória, variável tem endereço, pilha existe | É o modelo mental de tudo | [`10-fundamentos.md`](10-fundamentos.md) deste curso já cobre |

> **Teste rápido de prontidão.** Você consegue dizer, sem consultar: quanto é `0xFF` em
> decimal? O que um ponteiro em C armazena? O que `int *p = &x;` faz? Se sim nas três, está
> pronto. Se não, resolva isso primeiro — leva um fim de semana, não um mês.

### Ajuda muito (dá pra aprender no caminho)

| Tópico | Por que ajuda | Quando você vai sentir falta |
|---|---|---|
| **Assembly** (x86-64 ou ARM) | É *a* linguagem que você vai ler | Já no [`04`](04-como-comecar.md) — mas o curso ensina do zero em [`12`](12-arquitetura-e-assembly.md) |
| **Arquitetura de computadores**: registradores, cache, pilha vs. heap | Explica *por que* o assembly é como é | Ao entender convenções de chamada ([`16`](16-a-pilha-e-convencoes.md)) |
| **Sistemas operacionais**: processos, memória virtual, syscalls, carregamento de programas | Análise dinâmica e formatos de binário dependem disso | Em [`13`](13-formatos-de-binario.md) e [`15`](15-analise-dinamica.md) |
| **Python** | Todo script de automação de RE é Python (angr, Capstone, Frida) | No projeto-modelo e nos labs avançados |
| **Redes** (TCP/IP, HTTP) | Malware e apps se comunicam; você vai interceptar | Em análise de malware ([`20`](20-analise-de-malware.md)) |
| **Criptografia básica**: hash, simétrico vs. assimétrico | Proteções e malware usam cripto | Em [`18`](18-ofuscacao-e-packers.md); há [`criptografia`](../criptografia/) nesta pasta |

**Nada disso é bloqueante.** O curso reintroduz cada conceito no ponto em que ele é
necessário. A lista acima existe para você saber onde estão os buracos e não se assustar.

---

## Fundamentos que você usa desde a primeira hora

### Hexadecimal em 3 minutos

Computadores contam em **binário** (base 2: só 0 e 1). Escrever binário à mão é insuportável
(`11111111`), então usamos **hexadecimal** (base 16), que empacota 4 bits em 1 dígito:

| Bin | Hex | Dec | | Bin | Hex | Dec |
|---|---|---|---|---|---|---|
| 0000 | 0 | 0 | | 1000 | 8 | 8 |
| 0001 | 1 | 1 | | 1001 | 9 | 9 |
| 0010 | 2 | 2 | | 1010 | A | 10 |
| 0011 | 3 | 3 | | 1011 | B | 11 |
| 0100 | 4 | 4 | | 1100 | C | 12 |
| 0101 | 5 | 5 | | 1101 | D | 13 |
| 0110 | 6 | 6 | | 1110 | E | 14 |
| 0111 | 7 | 7 | | 1111 | F | 15 |

- Prefixo `0x` marca hex: `0xFF` = `255`, `0x10` = `16` (não 10!), `0x100` = `256`.
- Um **byte** = 8 bits = 2 dígitos hex = 0 a 255 (`0x00` a `0xFF`).
- Confira no terminal: `python3 -c "print(0xFF, 0x10, 0xdeadbeef)"` → `255 16 3735928559`.

### Complemento de dois em 2 minutos

Como o computador guarda **números negativos**? Não há sinal de menos nos bits. A convenção
(quase universal) é **complemento de dois**: o bit mais alto vale negativo.

Em 8 bits: `1111 1111` não é 255 quando interpretado como *com sinal* — é `-1`. A regra
prática: para negar, **inverta todos os bits e some 1**. Por isso `-1` em 32 bits é
`0xFFFFFFFF`, um padrão que você vai reconhecer de olhos fechados depois de um mês.

Por que assim, e não um "bit de sinal" simples? **Trade-off de hardware documentado:** com
complemento de dois, a mesma circuitaria de soma funciona para números com e sem sinal, e
o zero é único (não há "+0" e "−0"). Foi a escolha que barateou a CPU — e virou padrão
desde os anos 1960. (Cinco porquês parando numa decisão histórica/econômica de projeto.)

---

## Ambiente (hardware e software)

### Requisitos reais de máquina

| Recurso | Mínimo | Confortável | Por quê |
|---|---|---|---|
| **RAM** | 8 GB | 16 GB+ | Ghidra e uma VM de análise juntos comem memória |
| **Disco** | 30 GB livres | 100 GB+ | Ghidra ~2 GB, mais VMs de análise de malware |
| **CPU** | x86-64, 2 núcleos | 4+ núcleos, virtualização (VT-x/AMD-V) ativa | Emulação e VMs precisam de virtualização |
| **SO** | Linux, macOS ou Windows 10+ | **Linux** (nativo ou WSL2) | O ecossistema é primariamente Linux |

**Recomendação profissional:** faça engenharia reversa em **Linux** (Ubuntu/Debian ou uma
distro dedicada como Kali/REMnux), rodando dentro de uma **máquina virtual descartável**
quando o alvo for perigoso (malware). Nunca analise malware na sua máquina de trabalho.
Detalhes de laboratório seguro em [`20-analise-de-malware.md`](20-analise-de-malware.md).

### Conta em serviço

- **Nenhuma é obrigatória** para o curso. As ferramentas centrais (Ghidra, GDB, radare2)
  são gratuitas e sem cadastro.
- **Úteis e gratuitas:** conta no **GitHub** (baixar ferramentas), no **VirusTotal**
  (triagem de arquivos suspeitos — plano free), e num serviço de **CTF** (picoCTF,
  crackmes.one) para praticar.
- **IDA Free** exige aceitar uma licença (sem cadastro pago). Ver [`03`](03-instalacao.md).

---

## Tempo realista até cada nível

Sem otimismo de folheto. Assumindo estudo consistente, com as mãos no teclado, não só lendo.

| Nível | O que você consegue fazer | Tempo (10 h/semana) |
|---|---|---|
| **Sobrevivência** | Ler assembly simples, achar strings, seguir um crackme fácil | 3–6 semanas |
| **Confortável** | Reverter um programa pequeno inteiro, usar Ghidra + GDB com fluência | 3–6 meses |
| **Competente** | Analisar malware real, achar bugs simples, desfazer ofuscação leve | 1–2 anos |
| **Especialista** | Unpacking de packers comerciais, pesquisa de 0-day, firmware complexo | 3–5 anos+ |

Reverter é uma das áreas de segurança com a **curva mais longa**. A boa notícia: a curva é
suave e cada semana rende resultado visível. A má: não há atalho para as 500 horas de
"olhar assembly até parar de doer".

---

## Rota de resgate — o que fazer se faltar um pré-requisito

Você **não** precisa parar o curso. Faça isto conforme o buraco:

- **Não sei C.** Faça um curso rápido de C em paralelo (CS50 cobre em ~2 semanas). Você não
  precisa escrever C bem — precisa *reconhecer* padrões de C. Isso vem lendo binários.
- **Não sei assembly.** Ótimo: [`12-arquitetura-e-assembly.md`](12-arquitetura-e-assembly.md)
  começa do zero absoluto. Ninguém "sabe assembly" antes de reverter; aprende-se revertendo.
- **Travo no terminal.** Passe um fim de semana no "Missing Semester" (MIT, grátis) ou na
  seção de shell do [`curso-docker`](../curso-docker/) desta pasta. É pré-requisito real, resolva primeiro.
- **Hex me confunde.** Releia a seção acima e faça 20 conversões à mão. Cola em minutos.
- **Não tenho máquina potente.** Use **ambientes online** (Compiler Explorer, Dogbolt,
  playgrounds) e o Ghidra em uma VM na nuvem. Ver a seção "sem instalar nada" em
  [`03-instalacao.md`](03-instalacao.md). Você começa hoje, com um navegador.
- **Windows sem WSL.** Instale o WSL2 (um comando) ou use uma VM Linux. Reverter no Windows
  puro é possível (x64dbg é excelente), mas o curso assume Linux por padrão.

---

## Checklist de prontidão

Antes de ir para [`03-instalacao.md`](03-instalacao.md), confirme:

- [ ] Consigo abrir um terminal e navegar entre pastas sem pensar.
- [ ] Converto `0x2A` para 42 de cabeça (ou com `python3 -c`).
- [ ] Sei o que é um ponteiro em C e o que ele guarda.
- [ ] Tenho ≥ 8 GB de RAM e ≥ 30 GB de disco livre (ou um plano de usar a nuvem).
- [ ] Aceito que isso é uma maratona de meses, não uma tarde.

Faltou um item? Vá à rota de resgate acima. Não precisa faltar zero — precisa ter um plano
para cada buraco.

---

## Autoteste

1. Quais são os **quatro** conhecimentos indispensáveis, e por que cada um é indispensável e
   não apenas útil?
2. Converta à mão: `0x1F`, `0xA0`, `0xDEAD` para decimal.
3. Por que `-1` em 32 bits é `0xFFFFFFFF`? Explique via complemento de dois.
4. Qual o trade-off de hardware que fez o complemento de dois vencer o "bit de sinal"?
5. Quanto tempo, de forma realista, até você conseguir reverter um programa pequeno inteiro?
6. Você não sabe assembly. Isso te impede de começar o curso? Justifique.
7. Descreva a configuração de máquina que você usaria para analisar um malware desconhecido,
   e por que **não** faria isso na sua máquina principal.

> Próximo: [`03-instalacao.md`](03-instalacao.md) — montar o arsenal.
