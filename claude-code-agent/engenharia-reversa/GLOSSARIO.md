# Glossário — Engenharia Reversa

**Data:** 03/09/2026. Termos em ordem alfabética. Inglês na primeira menção, com tradução.
Referências cruzadas aos arquivos onde o termo é desenvolvido.

---

### A

- **AArch64 / ARM64** — a arquitetura de 64 bits da ARM (celulares, Macs Apple Silicon, IoT).
  Instruções de tamanho fixo (4 bytes). Ver [`12`](12-arquitetura-e-assembly.md).
- **ABI (Application Binary Interface)** — contrato de baixo nível entre binários: convenção de
  chamada, layout de tipos, formato do executável. Ver [`16`](16-a-pilha-e-convencoes.md).
- **Análise dinâmica** — examinar o programa **executando-o** (depurar, tracing, instrumentar).
  Ver [`15`](15-analise-dinamica.md).
- **Análise estática** — examinar o binário **sem executá-lo** (desmontar, descompilar). Ver
  [`14`](14-analise-estatica.md).
- **angr** — framework Python de análise binária com execução simbólica. Ver [`60`](60-teoria-avancada.md).
- **Anti-debug / anti-VM / anti-disassembly** — técnicas do alvo para detectar e atrapalhar
  ferramentas de análise. Ver [`19`](19-anti-analise.md).
- **ASLR (Address Space Layout Randomization)** — sorteia endereços de carga a cada execução,
  dificultando exploração. Ver [`13`](13-formatos-de-binario.md), [`21`](21-vulnerabilidades.md).
- **Assembly (linguagem de montagem)** — representação textual do código de máquina, uma linha
  por instrução. Ver [`12`](12-arquitetura-e-assembly.md).
- **AT&T (sintaxe)** — notação de assembly `origem, destino` com `%`/`$` (objdump/GDB padrão).
  Oposta à Intel. Ver [`05`](05-manual-de-uso.md).

### B

- **Bytecode** — instruções para uma máquina virtual (Java, .NET, Python, Wasm), não para a CPU
  física; guarda mais metadados que código nativo. Ver [`10`](10-fundamentos.md), [`23`](23-mobile-e-managed.md).
- **Binary diffing** — comparar duas versões de um binário para achar o que mudou (patch
  diffing). Ver [`14`](14-analise-estatica.md).
- **Bloco básico (basic block)** — sequência de instruções sem desvio interno; nó do CFG. Ver
  [`14`](14-analise-estatica.md).

### C

- **Canário de pilha (stack canary)** — valor sentinela antes do endereço de retorno, checado no
  epílogo para detectar overflow. Ver [`16`](16-a-pilha-e-convencoes.md), [`21`](21-vulnerabilidades.md).
- **Capstone** — biblioteca de desmontagem multiarquitetura (Python/C). Ver [`05`](05-manual-de-uso.md).
- **CFG (Control Flow Graph, grafo de fluxo de controle)** — representação da função como blocos
  ligados por saltos. Ver [`14`](14-analise-estatica.md).
- **Código de máquina** — os bytes que a CPU executa diretamente. Ver [`10`](10-fundamentos.md).
- **Convenção de chamada (calling convention)** — regras de onde vão argumentos/retorno e quem
  preserva registradores (System V, Microsoft x64, AAPCS). Ver [`16`](16-a-pilha-e-convencoes.md).
- **Crackme** — programa feito de propósito para ser revertido, como treino. Ver [`07`](07-projeto-modelo/).
- **CTF (Capture The Flag)** — competição de segurança com desafios, incluindo RE. Ver [`70`](70-pratica.md).

### D

- **Descompilador (decompiler)** — ferramenta que eleva assembly a pseudocódigo tipo C (Ghidra,
  Hex-Rays). Ver [`14`](14-analise-estatica.md).
- **Desmontador (disassembler)** — traduz bytes de código de máquina em assembly. Ver [`14`](14-analise-estatica.md).
- **DGA (Domain Generation Algorithm)** — algoritmo em malware que gera domínios de C2. Ver
  [`20`](20-analise-de-malware.md).
- **DMCA §1201** — lei dos EUA que proíbe contornar proteção, com isenções para
  interoperabilidade e pesquisa. Ver [`80`](80-custos-e-licencas.md), [`95`](95-referencias.md).
- **DWARF** — formato de informação de depuração (símbolos/tipos) em ELF. Ver [`13`](13-formatos-de-binario.md).

### E

- **ELF (Executable and Linkable Format)** — formato de executável do Linux/Unix. Ver [`13`](13-formatos-de-binario.md).
- **Emulação** — rodar código de outra arquitetura ou trechos isolados (QEMU, Unicorn, Qiling).
  Ver [`15`](15-analise-dinamica.md).
- **Epílogo (epilogue)** — instruções que fecham a moldura da função e retornam (`leave; ret`).
  Ver [`16`](16-a-pilha-e-convencoes.md).
- **Execução simbólica** — tratar entradas como variáveis simbólicas e resolver caminhos com SMT.
  Ver [`60`](60-teoria-avancada.md).

### F

- **Fat binary (universal)** — Mach-O com várias arquiteturas num arquivo. Ver [`13`](13-formatos-de-binario.md).
- **Flags (RFLAGS)** — bits de status do resultado da última operação (ZF, SF, CF, OF). Ver
  [`12`](12-arquitetura-e-assembly.md).
- **FLOSS** — ferramenta da Mandiant que extrai strings ofuscadas emulando rotinas de decrypt.
  Ver [`18`](18-ofuscacao-e-packers.md).
- **Frida** — framework de instrumentação dinâmica (injeta JavaScript em processos). Ver [`15`](15-analise-dinamica.md), [`23`](23-mobile-e-managed.md).
- **Fuzzing** — jogar entradas malformadas em massa para achar crashes/bugs (AFL++, libFuzzer).
  Ver [`21`](21-vulnerabilidades.md).

### G

- **Gadget (ROP)** — pequena sequência de instruções terminando em `ret`, reutilizada em ROP.
  Ver [`21`](21-vulnerabilidades.md).
- **Ghidra** — framework de RE open-source da NSA, com descompilador. Ver [`03`](03-instalacao.md), [`04`](04-como-comecar.md).
- **GOT (Global Offset Table)** — tabela de endereços de funções dinâmicas, resolvida em runtime.
  Ver [`13`](13-formatos-de-binario.md).

### H

- **Heap** — memória de alocação dinâmica (`malloc`/`new`). Ver [`17`](17-estruturas-de-dados-no-binario.md).
- **Hexadecimal** — base 16 (`0x`); 1 dígito = 4 bits; 1 byte = 2 dígitos. Ver [`02`](02-pre-requisitos.md).

### I

- **IAT (Import Address Table)** — tabela de funções importadas de DLLs em PE (equivalente da
  GOT). Ver [`13`](13-formatos-de-binario.md).
- **IDA** — desmontador/descompilador comercial da Hex-Rays; padrão histórico. Ver [`80`](80-custos-e-licencas.md).
- **Intel (sintaxe)** — notação de assembly `destino, origem` (IDA/Ghidra); recomendada para RE.
  Ver [`05`](05-manual-de-uso.md).
- **Instrumentação** — injetar código para observar/alterar um processo (Frida, Pin). Ver [`15`](15-analise-dinamica.md).
- **IOC (Indicator of Compromise)** — artefato que permite detectar uma ameaça (hash, IP, mutex).
  Ver [`20`](20-analise-de-malware.md).
- **IR / IL (representação intermediária)** — linguagem simplificada sobre a qual as ferramentas
  raciocinam (P-Code, VEX, microcode). Ver [`60`](60-teoria-avancada.md).

### J

- **JTAG / SWD** — interfaces de depuração de hardware para ler/controlar um chip. Ver [`22`](22-firmware-e-embarcados.md).
- **Jump table** — array de endereços usado para compilar um `switch` grande. Ver [`17`](17-estruturas-de-dados-no-binario.md).

### K–L

- **Keygen** — gerador de seriais válidos, feito após reverter a fórmula de validação. Ver [`06`](06-exemplos.md), [`07`](07-projeto-modelo/).
- **LIEF** — biblioteca para ler/editar ELF/PE/Mach-O em Python. Ver [`05`](05-manual-de-uso.md).
- **Linker (ligador)** — junta objetos e resolve símbolos para formar o executável. Ver [`10`](10-fundamentos.md).
- **LLM4Decompile** — primeiro LLM open-source de descompilação (2024). Ver [`65`](65-estado-da-arte.md).

### M

- **Mach-O** — formato de executável do macOS/iOS. Ver [`13`](13-formatos-de-binario.md).
- **Name mangling** — codificação de assinaturas C++ em nomes de símbolo; desfeita com `c++filt`.
  Ver [`17`](17-estruturas-de-dados-no-binario.md).
- **MITRE ATT&CK** — taxonomia de táticas/técnicas de adversários. Ver [`20`](20-analise-de-malware.md).

### N–O

- **NX / DEP (No-eXecute)** — marca memória como não-executável; força ROP. Ver [`21`](21-vulnerabilidades.md).
- **OEP (Original Entry Point)** — ponto onde o código original começa após o desempacotamento.
  Ver [`18`](18-ofuscacao-e-packers.md).
- **Ofuscação** — transformar código para dificultar leitura (mantendo o comportamento). Ver [`18`](18-ofuscacao-e-packers.md).
- **Opaque predicate (predicado opaco)** — condição sempre verdadeira/falsa usada em ofuscação.
  Ver [`18`](18-ofuscacao-e-packers.md).

### P

- **Packer** — comprime/cifra o executável e o restaura em runtime (ex.: UPX). Ver [`18`](18-ofuscacao-e-packers.md).
- **Patching** — modificar bytes do binário para alterar comportamento. Ver [`05`](05-manual-de-uso.md), [`06`](06-exemplos.md).
- **PE (Portable Executable)** — formato de executável do Windows. Ver [`13`](13-formatos-de-binario.md).
- **PIE (Position-Independent Executable)** — executável reposicionável (habilita ASLR no código).
  Ver [`13`](13-formatos-de-binario.md).
- **PLT (Procedure Linkage Table)** — trampolins que resolvem funções dinâmicas via GOT. Ver [`13`](13-formatos-de-binario.md).
- **Prólogo (prologue)** — instruções que abrem a moldura da função (`push rbp; mov rbp,rsp`).
  Ver [`16`](16-a-pilha-e-convencoes.md).
- **Pseudo-C** — saída do descompilador: código parecido com C, não o fonte original. Ver [`14`](14-analise-estatica.md).

### R

- **radare2 / rizin** — frameworks de RE de linha de comando, open-source. Ver [`05`](05-manual-de-uso.md).
- **Registrador** — memória ultrarrápida dentro da CPU (RAX, RDI, RSP…). Ver [`12`](12-arquitetura-e-assembly.md).
- **RELRO** — proteção que torna a GOT somente-leitura. Ver [`21`](21-vulnerabilidades.md).
- **RIP / PC** — registrador que aponta a próxima instrução (instruction pointer). Ver [`12`](12-arquitetura-e-assembly.md).
- **ROP (Return-Oriented Programming)** — encadear gadgets do próprio binário para contornar NX.
  Ver [`21`](21-vulnerabilidades.md).

### S

- **Sandbox** — ambiente isolado para executar código suspeito com segurança. Ver [`15`](15-analise-dinamica.md), [`20`](20-analise-de-malware.md).
- **Seção (section) / segmento (segment)** — divisões do binário (`.text`, `.rodata`) e unidades
  de carga na memória. Ver [`13`](13-formatos-de-binario.md).
- **SMT (Satisfiability Modulo Theories)** — solucionador de fórmulas lógicas com teorias (Z3);
  motor da execução simbólica. Ver [`60`](60-teoria-avancada.md).
- **SSA (Static Single Assignment)** — forma intermediária onde cada variável é atribuída uma vez.
  Ver [`60`](60-teoria-avancada.md).
- **Stack (pilha)** — região LIFO para retorno, locais e argumentos; cresce para baixo. Ver [`16`](16-a-pilha-e-convencoes.md).
- **Stack frame (moldura)** — espaço de trabalho de uma função na pilha. Ver [`16`](16-a-pilha-e-convencoes.md).
- **strace / ltrace** — tracers de chamadas de sistema / de biblioteca. Ver [`05`](05-manual-de-uso.md), [`15`](15-analise-dinamica.md).
- **strings** — extrai sequências de texto legíveis de um binário. Ver [`04`](04-como-comecar.md).
- **Stripped** — binário sem tabela de símbolos (sem nomes de função). Ver [`10`](10-fundamentos.md).
- **Symbol (símbolo)** — nome associado a um endereço (função/variável). Ver [`13`](13-formatos-de-binario.md).
- **Syscall (chamada de sistema)** — pedido do programa ao kernel (open, read, connect…). Ver [`15`](15-analise-dinamica.md).

### T–U

- **Taint analysis** — rastrear como dados de entrada fluem pelo programa (fonte→sink). Ver [`21`](21-vulnerabilidades.md).
- **UPX** — packer open-source com desempacotamento oficial (`upx -d`). Ver [`18`](18-ofuscacao-e-packers.md).
- **Use-after-free (UAF)** — usar memória já liberada; classe de vulnerabilidade. Ver [`21`](21-vulnerabilidades.md).

### V–Z

- **Vtable (virtual method table)** — array de ponteiros de função para métodos virtuais (C++).
  Ver [`17`](17-estruturas-de-dados-no-binario.md).
- **Watchpoint** — breakpoint que dispara quando um valor de memória muda. Ver [`15`](15-analise-dinamica.md).
- **WebAssembly (Wasm)** — bytecode portátil para a web; alvo emergente de RE. Ver [`23`](23-mobile-e-managed.md), [`65`](65-estado-da-arte.md).
- **x86-64 (AMD64)** — arquitetura de 64 bits dominante em desktops/servidores. Ver [`12`](12-arquitetura-e-assembly.md).
- **XOR (ofuscação por)** — cifra reversível de byte único, comum em malware; `p = c ^ k`. Ver [`06`](06-exemplos.md), [`07`](07-projeto-modelo/).
- **YARA** — linguagem/ferramenta de regras para detectar padrões em arquivos/malware. Ver [`20`](20-analise-de-malware.md).
- **Z3** — solucionador SMT da Microsoft Research, motor de muitas ferramentas de RE. Ver [`60`](60-teoria-avancada.md).
