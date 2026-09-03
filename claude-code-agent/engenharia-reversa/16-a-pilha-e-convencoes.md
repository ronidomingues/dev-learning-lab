# 16 · A pilha e as convenções de chamada

**Nível:** intermediário · **Data:** 03/09/2026 · sintaxe Intel.

Toda leitura de assembly depende de entender **como uma função chama outra**: onde vão os
argumentos, onde volta o resultado, e como a **pilha** guarda o estado. Domine isto e você lê
qualquer função. Erre isto e nada faz sentido.

---

## 1. A pilha (stack) — o que é e por que existe

A **pilha** é uma região de memória usada como estrutura LIFO (último a entrar, primeiro a
sair) para: endereços de retorno, variáveis locais e argumentos extras. **Cresce para baixo**
(em direção a endereços menores) — uma convenção histórica que virou universal.

- **RSP** (stack pointer) aponta para o **topo** da pilha (o endereço mais baixo em uso).
- **RBP** (base pointer) aponta para a **base da moldura** da função atual (opcional em `-O2`).
- `push X` = `RSP -= 8; [RSP] = X`. `pop X` = `X = [RSP]; RSP += 8`.

```
   endereços ALTOS
   ┌───────────────────────┐
   │  argumentos extras     │
   │  endereço de retorno   │  ← push automático do 'call'
   │  RBP salvo             │  ← push rbp (prólogo)
   │  variáveis locais       │  ← [rbp-0x8], [rbp-0x10], ...
   │  ...                    │  ← RSP (topo)
   └───────────────────────┘
   endereços BAIXOS  (a pilha cresce nesta direção ↓)
```

**Por que cresce para baixo?** Cinco porquês: (1) convenção; (2) porque em máquinas antigas a
pilha crescia de cima da memória para baixo enquanto o *heap*/dados cresciam de baixo para
cima, (3) para os dois compartilharem o mesmo espaço se encontrando no meio, (4) maximizando o
uso de memória escassa e cara nos anos 1960–70, (5) parada legítima: **trade-off econômico
histórico** (memória cara) que se cristalizou em convenção de hardware. Não é lei física; é
herança que ninguém teve motivo de mudar.

---

## 2. Stack frame (moldura de função)

Cada função ativa tem uma **moldura** na pilha: seu espaço de trabalho. O prólogo a cria, o
epílogo a destrói.

**Prólogo típico (x86-64):**
```asm
push rbp            ; salva a base do chamador
mov  rbp, rsp       ; RBP marca a base desta moldura
sub  rsp, 0x20      ; reserva 32 bytes para locais
```
**Epílogo:**
```asm
leave               ; = mov rsp, rbp ; pop rbp  (desfaz a moldura)
ret                 ; pop do endereço de retorno para RIP
```
Com `-O2`, o compilador muitas vezes **omite RBP** (usa RSP direto para tudo) — a moldura
existe, mas sem o "âncora" RBP. Os endereços de locais viram `[rsp+N]` em vez de `[rbp-N]`.

---

## 3. Convenções de chamada — o contrato

Uma **convenção de chamada** (*calling convention*) é o acordo sobre: onde ficam os argumentos,
onde fica o retorno, e quem preserva quais registradores. Muda por plataforma. As duas que você
mais verá:

### System V AMD64 (Linux, macOS, BSD)
- **Argumentos inteiros/ponteiro (1º→6º):** `RDI, RSI, RDX, RCX, R8, R9`.
- **Argumentos de ponto flutuante:** `XMM0–XMM7`.
- **Mais de 6 argumentos:** o excedente vai na **pilha** (empilhado da direita para a esquerda).
- **Retorno:** `RAX` (e `RDX` para 128 bits; `XMM0` para float).
- **Preservados pelo chamado (callee-saved):** `RBX, RBP, R12–R15` — se a função os usa, deve
  restaurá-los.
- **Voláteis (caller-saved):** `RAX, RCX, RDX, RSI, RDI, R8–R11` — podem ser destruídos.
- **Red zone:** 128 bytes abaixo de RSP que funções-folha podem usar sem ajustar RSP.

### Microsoft x64 (Windows)
- **Argumentos (1º→4º):** `RCX, RDX, R8, R9`. Resto na pilha.
- **Shadow space:** o chamador reserva 32 bytes na pilha para os 4 primeiros argumentos.
- **Retorno:** `RAX`.
- Diferente do System V — **por isso importa saber em qual SO o binário roda**.

### ARM64 (AAPCS)
- **Argumentos (1º→8º):** `X0–X7`. **Retorno:** `X0`. **Endereço de retorno:** `LR` (`X30`).

> Tabela mnemônica (System V): "**Di**ana **Si**lva **d**eu **c**afé **8** e **9**" →
> RDI, RSI, RDX, RCX, R8, R9. Bobo, mas cola.

---

## 4. Lendo uma chamada de função no assembly

```c
resultado = soma(10, 20, 30);
```
vira (System V):
```asm
mov edx, 30         ; 3º arg -> RDX
mov esi, 20         ; 2º arg -> RSI
mov edi, 10         ; 1º arg -> RDI
call soma
mov  [rbp-0x4], eax ; resultado = valor de retorno (RAX)
```
**Ao reverter, leia de trás para frente:** encontre o `call`, e os `mov` para RDI/RSI/RDX
imediatamente antes são os argumentos, na ordem. O `mov` de EAX logo depois é o uso do retorno.
Esse é o padrão que você reconhece milhares de vezes.

**Chamada a função externa:** `call strcmp@plt` — via PLT/GOT ([`13`](13-formatos-de-binario.md)).
Parar aqui no GDB e ler RDI/RSI entrega os dois lados da comparação.

---

## 5. Por que isso é a chave do RE

- **Identificar argumentos** de uma função desconhecida = entender o que ela recebe = metade de
  entender o que ela faz.
- **Rastrear o retorno** = saber o que a função produz e como o resultado é usado.
- **Saber quais registradores são preservados** = seguir um valor através de várias chamadas
  sem se perder.
- No **Ghidra**, definir a assinatura correta (nº e tipos de argumentos) faz o descompilador
  reescrever a função inteira de forma legível. A convenção é o que ele usa para isso.

---

## 6. A pilha como superfície de ataque (ponte para vulns)

Como o **endereço de retorno** fica na pilha, junto de buffers locais, um buffer que transborda
pode **sobrescrever o endereço de retorno** e desviar a execução — o clássico *stack buffer
overflow*. Defesas: **canário de pilha** (um valor sentinela antes do endereço de retorno,
checado no epílogo), **NX** (pilha não-executável), **ASLR**, **PIE**. Tudo isso você lê com
`checksec` e explora/entende em [`21-vulnerabilidades.md`](21-vulnerabilidades.md).

```
   [ buffer local ]  ← overflow escreve daqui...
   [ canário      ]  ← ...passa por aqui (se mudar, o programa aborta)
   [ RBP salvo    ]
   [ end. retorno ]  ← ...até aqui: controlar isto = controlar RIP
```

---

## Autoteste

1. Em que direção a pilha cresce, e qual o trade-off histórico por trás dessa escolha?
2. Escreva o prólogo e o epílogo típicos de uma função x86-64 e diga o que cada instrução faz.
3. Na convenção System V, quais registradores levam os 4 primeiros argumentos inteiros?
4. Um binário Windows passa o 1º argumento em qual registrador? E o Linux? Por que a diferença importa?
5. Diferencie registradores *callee-saved* de *caller-saved* e por que isso te ajuda a seguir um valor.
6. Ao ver um `call` no assembly, como você identifica os argumentos e o uso do retorno?
7. Explique como a posição do endereço de retorno na pilha habilita um stack overflow, e o que o canário faz.
