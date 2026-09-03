# 17 · Estruturas de dados no binário

**Nível:** avançado · **Data:** 03/09/2026 · sintaxe Intel.

O assembly não tem `struct`, `array` ou `class` — só endereços e offsets. Reverter dados é
reconhecer como cada construção de alto nível **vira aritmética de ponteiros**. Este arquivo é
o dicionário desses padrões.

---

## 1. Arrays — o padrão `base + índice*escala`

```c
int v[10];  v[i] = 7;
```
```asm
mov  dword ptr [rbp + rax*4 - 0x30], 7   ; base=[rbp-0x30], índice=rax, escala=4 (sizeof int)
```
A **escala** revela o tamanho do elemento: **1**=`char`, **2**=`short`, **4**=`int`/`float`,
**8**=`long`/`double`/ponteiro. A **base** é onde o array começa. Ao ver `[X + i*N]` num laço,
pense "array de elementos de N bytes".

Array de strings (`char *argv[]`) usa escala **8** (ponteiros), e cada elemento é, por sua vez,
um ponteiro para os bytes da string — dupla desreferência.

---

## 2. Structs — offsets constantes a partir de um ponteiro

```c
struct Ponto { int x; int y; char nome[16]; };
p->y = 5;
```
```asm
mov  dword ptr [rdi + 4], 5    ; rdi = p; offset 4 = campo 'y' (x ocupa [rdi+0])
```
Campos viram **offsets fixos**: `x` em `+0`, `y` em `+4`, `nome` em `+8`. Reconhecer um mesmo
ponteiro acessado em `+0`, `+4`, `+8`, `+24`… = uma struct. **No Ghidra**, você *define* a
struct e o descompilador reescreve `[rdi+4]` como `p->y` — o passo que torna o código legível.

### Alinhamento e padding (uma pegadinha)
O compilador insere **padding** para alinhar campos (um `int` costuma ficar em offset múltiplo
de 4; um `double`/ponteiro, de 8). Por isso o offset de um campo **não** é a soma ingênua dos
tamanhos anteriores:
```c
struct S { char c; int i; };   // c em +0, PADDING em +1..+3, i em +4 — sizeof = 8, não 5
```
Ao remontar uma struct, respeite o alinhamento ou os offsets não baterão.

---

## 3. Strings — C vs. contadas

- **String C:** sequência de bytes terminada em `\0` (0x00). Funções como `strlen`/`strcpy`
  varrem até o zero. No binário: um run de bytes ASCII em `.rodata` seguido de `00`.
- **String contada** (Pascal, muitos formatos): um tamanho no início, sem terminador.
  Reconhecível por um acesso a `[ptr]` (o tamanho) antes do conteúdo em `[ptr+N]`.
- **UTF-16** (Windows/`wchar_t`): 2 bytes por caractere (`'A'` = `41 00`). Use `strings -e l`.

---

## 4. Ponteiros e desreferência em cadeia

`a->b->c` vira uma cadeia de `mov` seguindo endereços:
```asm
mov rax, [rdi]        ; rax = a->b   (carrega o ponteiro no offset 0)
mov rax, [rax + 8]    ; rax = b->c   (offset 8 dentro de *b)
```
Cada `mov reg, [reg + off]` é "pegue o ponteiro naquele campo e siga". Listas ligadas, árvores
e grafos aparecem exatamente assim: um laço que faz `no = no->prox` (`mov rax, [rax+off]`) até
`NULL` (`test rax,rax; je fim`).

---

## 5. C++ — objetos, vtables e polimorfismo

C++ compila para o mesmo assembly de C, mais alguns padrões característicos.

### Métodos e o `this`
Um método `obj.metodo(a)` passa o objeto como **argumento oculto** `this` no 1º registrador:
```asm
mov rsi, a
mov rdi, obj          ; 'this' vai em RDI (System V)
call Classe::metodo
```
Ver um `call` cujo 1º argumento é sempre um ponteiro para o mesmo objeto = método de classe.

### vtable (funções virtuais)
Objetos com métodos `virtual` têm, no offset 0, um ponteiro para a **vtable**: um array de
ponteiros de função. Uma chamada virtual é **indireta**:
```asm
mov rax, [rdi]        ; rax = vtable (offset 0 do objeto)
call [rax + 0x10]     ; chama o 3º método virtual (offset 0x10 = índice 2)
```
`call [reg+offset]` após carregar `[obj]` é a assinatura inconfundível de **método virtual /
polimorfismo**. A vtable te dá o mapa de métodos da classe. Ghidra/IDA têm assistentes para
reconstruir hierarquias de classe a partir de vtables e do RTTI (quando presente).

### Name mangling
C++ codifica assinaturas nos nomes de símbolo: `_ZN6Classe6metodoEi` = `Classe::metodo(int)`.
Desfaça com `c++filt`:
```bash
echo _ZN6Classe6metodoEi | c++filt      # Classe::metodo(int)
```
Ghidra e `nm -C` já desmanglam automaticamente. Isso te devolve **nomes e tipos de graça** em
binários C++ não-stripped.

---

## 6. Enums, flags e switch

- **Enum:** vira apenas inteiros constantes; o *nome* se perde, o valor fica (`cmp eax, 3`).
- **Flags/bitmask:** operações `and`/`or`/`test` com potências de 2 (`test eax, 4` = "o bit 2
  está ligado?"). Reconhecer `and`/`or` com `0x1,0x2,0x4,0x8…` = campo de flags.
- **switch grande:** o compilador gera uma **jump table** — um array de endereços indexado pelo
  valor: `jmp [tabela + rax*8]`. Ver esse padrão = um `switch`/`case` denso. Ghidra reconstrói
  o switch e rotula os casos.

---

## 7. Heap vs. stack (onde o dado mora)

- **Stack:** locais e argumentos; endereços `[rbp-N]`/`[rsp+N]`; vida curta (some no `ret`).
- **Heap:** memória de `malloc`/`new`; endereços vindos do retorno de `malloc` (RAX);
  vida controlada por `free`/`delete`. Estruturas dinâmicas (listas, buffers de tamanho
  variável) moram aqui. Bugs de heap (use-after-free, double-free) são um capítulo de
  segurança ([`21`](21-vulnerabilidades.md)); ferramentas como `pwndbg heap`/`bins` mostram o
  estado do alocador.

---

## 8. Fluxo de trabalho para reconstruir dados no Ghidra

1. Ache um ponteiro acessado em vários offsets fixos → hipótese de struct.
2. `Data Type Manager` → nova `struct`; adicione campos nos offsets observados (respeite o padding).
3. Aplique o tipo à variável (botão direito → *Retype Variable*). O pseudo-C vira `p->campo`.
4. Se vir `call [ptr]` após `mov reg,[obj]` → é vtable; reconstrua a classe.
5. Renomeie campos conforme entende o uso. Itere. **Bom RE de dados é iterativo e manual.**

---

## Autoteste

1. Você vê `[rbp + rax*4 - 0x30]` num laço. Que estrutura é, e o que a escala `4` diz?
2. Por que o offset de um campo de struct não é a soma dos tamanhos anteriores? Dê um exemplo.
3. Como você distingue uma string C de uma string UTF-16 no binário?
4. Qual padrão de assembly denuncia uma **chamada de método virtual** em C++? Por quê?
5. Desmangle mentalmente/na ferramenta: o que `_ZN3Foo3barEv` representa?
6. Como um `switch` grande costuma ser compilado, e como você o reconhece?
7. Descreva o passo a passo no Ghidra para transformar acessos `[rdi+0]/[rdi+8]` em `p->campo`.
