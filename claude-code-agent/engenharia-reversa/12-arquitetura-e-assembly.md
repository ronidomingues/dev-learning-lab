# 12 · Arquitetura e Assembly — a linguagem do processador

**Nível:** intermediário · **Data:** 03/09/2026 · sintaxe **Intel** salvo indicado.

Este é o arquivo mais importante do núcleo. Reverter é **ler assembly**, e ler assembly é
entender o modelo da CPU. Começamos do zero absoluto: o que é um registrador, o que a CPU faz,
e como isso vira x86-64 e ARM64. Não decore a lista de instruções — entenda o *modelo* e
reconheça *padrões*.

---

## 1. O modelo mental da CPU (fetch–decode–execute)

Um processador é uma máquina burra e rápida que repete, bilhões de vezes por segundo:

```
   ┌──▶ FETCH  (busca a próxima instrução no endereço em RIP/PC)
   │      │
   │    DECODE (descobre o que ela manda fazer)
   │      │
   │    EXECUTE (faz: soma, move, compara, salta...)
   └──────┘      (RIP/PC avança para a próxima)
```

A CPU tem três recursos que você vai olhar o tempo todo:

- **Registradores:** um punhado de "gavetas" ultrarrápidas dentro da CPU (dezenas de bytes no
  total). Toda conta passa por eles.
- **Memória (RAM):** o "armário" grande e mais lento, endereçado por número. Código e dados
  vivem aqui.
- **Flags:** bits de status que registram o resultado da última operação (deu zero? deu
  negativo? teve *carry*?). São a base das decisões (`if`).

---

## 2. Registradores x86-64

São 16 registradores inteiros de 64 bits. Cada um tem "sub-nomes" para 32/16/8 bits — herança
histórica do 8086 (16 bits) → 386 (32 bits) → x86-64 (64 bits).

| 64 bits | 32 bits | 16 | 8 | Papel convencional |
|---|---|---|---|---|
| **RAX** | EAX | AX | AL | Acumulador; **valor de retorno** de função |
| **RBX** | EBX | BX | BL | Base (preservado entre chamadas) |
| **RCX** | ECX | CX | CL | Contador; **4º argumento** |
| **RDX** | EDX | DX | DL | Dados; **3º argumento** |
| **RSI** | ESI | SI | SIL | **2º argumento** (source em `movs`) |
| **RDI** | EDI | DI | DIL | **1º argumento** (destination em `movs`) |
| **RBP** | EBP | BP | BPL | Base do *stack frame* (moldura da função) |
| **RSP** | ESP | SP | SPL | **Topo da pilha** (stack pointer) |
| **R8–R11** | R8D… | | | Temporários; R8/R9 = **5º/6º argumentos** |
| **R12–R15** | | | | Preservados entre chamadas |
| **RIP** | | | | **Instruction pointer**: endereço da próxima instrução |
| **RFLAGS** | | | | Flags (ZF, SF, CF, OF…) |

**Detalhe que confunde:** escrever em `EAX` (32 bits) **zera** a metade alta de `RAX`. Por
isso `xor eax, eax` zera RAX inteiro — é o idioma de "zerar um registrador" (2 bytes, sem
imediato). Reconheça-o instantaneamente.

### Flags que importam
| Flag | Nome | Vira 1 quando |
|---|---|---|
| **ZF** | Zero | O resultado foi zero (base de `==`) |
| **SF** | Sign | O resultado foi negativo |
| **CF** | Carry | Houve "vai um" (aritmética sem sinal) |
| **OF** | Overflow | Estouro com sinal |

`cmp a, b` faz `a - b` **sem guardar o resultado**, só setando as flags. Depois um salto
condicional lê as flags. É assim que todo `if` funciona.

---

## 3. As instruções que cobrem 90% do que você lê

| Instrução (Intel) | Faz | Exemplo |
|---|---|---|
| `mov dst, src` | Copia src→dst | `mov rax, rbx` |
| `lea dst, [expr]` | Calcula um endereço (não acessa memória) | `lea rax, [rbp-0x10]` |
| `add`/`sub`/`imul`/`idiv` | Aritmética | `add eax, 7` |
| `and`/`or`/`xor`/`not`/`shl`/`shr` | Lógica e deslocamento | `xor eax, eax` (zera) |
| `push`/`pop` | Empilha/desempilha (mexe em RSP) | `push rbp` |
| `cmp a, b` | Compara (a−b), seta flags | `cmp edi, 0x2a` |
| `test a, b` | AND lógico, seta flags (não guarda) | `test eax, eax` (é zero?) |
| `jmp` | Salto incondicional | `jmp 0x1200` |
| `je/jne/jl/jg/jle/jge/jb/ja` | Saltos condicionais (leem flags) | `jne 0x1180` |
| `call` | Chama função (empilha endereço de retorno) | `call strcmp` |
| `ret` | Retorna (desempilha o endereço) | `ret` |
| `nop` | Não faz nada (`0x90`) | usado em patching/alinhamento |
| `syscall` | Chama o kernel (Linux x86-64) | pedir open/read/write |

**Reconhecimento de padrões — o que realmente importa:**
- `test eax, eax` + `je` = "se resultado foi zero, pule" → tradução de um `if (x == 0)`.
- `cmp` + `jl`/`jge` num laço = `for`/`while`.
- `call` seguido de `test rax,rax`/`je` = "chamou algo, checou se deu certo".
- Sequência `push rbp; mov rbp, rsp; sub rsp, N` = **prólogo** de função (abre moldura).
- `leave; ret` ou `mov rsp,rbp; pop rbp; ret` = **epílogo** (fecha e retorna).

---

## 4. Como um `if`/`while`/`for` vira assembly

**Código C:**
```c
int f(int x) {
    if (x > 10) return 1;
    return 0;
}
```
**Assembly (`-O0`, Intel):**
```asm
f:
    cmp   edi, 0xa        ; x - 10  (edi = x, 1º arg)
    jle   .Lfalse         ; se x <= 10, pula
    mov   eax, 1          ; return 1
    jmp   .Lend
.Lfalse:
    mov   eax, 0          ; return 0
.Lend:
    ret
```
Um `if` é sempre **um `cmp`/`test` seguido de um salto condicional**. Um `while` é a mesma
coisa com um `jmp` de volta ao topo. O descompilador reconstrói o `if` a partir desse padrão —
mas *você* precisa saber lê-lo para quando o descompilador falhar.

**Laço `for` (soma de 0..n):**
```asm
    xor   eax, eax        ; soma = 0
    xor   ecx, ecx        ; i = 0
.Lloop:
    cmp   ecx, edi        ; i < n ?
    jge   .Ldone
    add   eax, ecx        ; soma += i
    inc   ecx             ; i++
    jmp   .Lloop
.Ldone:
    ret
```

---

## 5. Endereçamento de memória

A CPU acessa memória por expressões `[base + índice*escala + deslocamento]`:

| Expressão | Significa |
|---|---|
| `[rbp-0x8]` | Variável local (offset negativo a partir da base da moldura) |
| `[rdi]` | O que RDI aponta (desreferência de ponteiro) |
| `[rax+rcx*4]` | Elemento de array de 4 bytes: `array[i]` (rax=base, rcx=i, 4=sizeof) |
| `[rip+0x2ea1]` | Endereço relativo ao RIP (dados em PIE; strings, globais) |

**`rax + rcx*4` grita "array de int".** A escala revela o tamanho do elemento (1=char, 4=int,
8=ponteiro/long). Esse é o padrão que te faz reconhecer arrays e structs no assembly
([`17-estruturas-de-dados-no-binario.md`](17-estruturas-de-dados-no-binario.md)).

---

## 6. ARM64 (AArch64) — o outro mundo que você vai encontrar

Celulares, Macs Apple Silicon, Raspberry Pi, IoT: tudo ARM. Você **vai** reverter ARM64.
Diferenças em relação a x86:

- **Mais registradores:** `X0`–`X30` (64 bits; `W0`–`W30` são as metades de 32). `X0` = 1º
  argumento **e** valor de retorno. `SP` = pilha, `LR`(`X30`) = endereço de retorno, `PC`.
- **RISC de largura fixa:** toda instrução tem **4 bytes**. Não há instruções de tamanho
  variável (ao contrário do x86). Isso torna a desmontagem *mais fácil e confiável*.
- **Load/store:** a aritmética só opera em registradores; memória só via `ldr`/`str`. O x86
  pode operar direto na memória; ARM não.
- **Chamada via registrador:** `bl func` guarda o retorno em `LR` (não empilha automaticamente
  como o `call` do x86).

**Mesmo `if (x>10)` em ARM64:**
```asm
    cmp   w0, #10          ; compara x com 10
    ble   .Lfalse          ; branch if less-or-equal
    mov   w0, #1
    ret
.Lfalse:
    mov   w0, #0
    ret
```
A *lógica* é idêntica ao x86; muda a notação. Quem aprende a "pensar em CPU" migra entre
arquiteturas lendo a tabela de registradores e o conjunto de instruções.

---

## 7. Por que existem duas sintaxes (AT&T × Intel)

- **AT&T** (`mov $5, %eax`): origem→destino, `%`/`$`. Herança do Unix/AT&T; padrão do
  `objdump`/GDB.
- **Intel** (`mov eax, 5`): destino←origem. Padrão da documentação Intel, IDA, Ghidra.

Não é uma escolha técnica profunda — é uma **convenção histórica** de duas linhagens (Unix vs.
Intel). Para RE, use **Intel** e configure suas ferramentas para ela. (Cinco porquês parando
numa convenção arbitrária, e dito como arbitrária.)

---

## 8. Como treinar a leitura (o método que funciona)

1. Escreva C simples, compile com `-O0`, veja o assembly no **Compiler Explorer** (godbolt.org).
   Mude o C e veja o assembly mudar. Isso constrói a intuição mais rápido que qualquer livro.
2. Suba a otimização (`-O2`) e veja o compilador *destruir* a correspondência linha-a-linha —
   funde variáveis, elimina saltos, usa truques (`imul` por constante mágica no lugar de `%`).
3. Foque em **padrões**, não instruções isoladas: prólogo/epílogo, chamada+checagem, laço,
   acesso a array. Depois de ~50 funções, o assembly "aquieta".

---

## Autoteste

1. Descreva o ciclo fetch–decode–execute e o papel de RIP nele.
2. Por que `xor eax, eax` é a forma idiomática de zerar RAX (e não só EAX)?
3. O que `cmp edi, 0xa` seguido de `jle` implementa em C?
4. Traduza `[rax+rcx*4]`: que estrutura de dados isso sugere e por quê?
5. Cite três diferenças concretas entre x86-64 e ARM64 relevantes para o reverser.
6. Identifique o prólogo e o epílogo de uma função em x86-64.
7. Por que a sintaxe Intel × AT&T existe, e qual você deve usar para RE?
8. `test rax, rax; je X` aparece após um `call`. O que isso quase sempre significa?
