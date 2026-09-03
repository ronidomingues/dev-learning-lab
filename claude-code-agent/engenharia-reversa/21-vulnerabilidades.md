# 21 · Achar vulnerabilidades em binários

**Nível:** avançado · **Data:** 03/09/2026

Reverter para **encontrar bugs exploráveis** é a base da pesquisa de segurança ofensiva e do
*bug bounty* em software fechado. Este arquivo cobre as classes clássicas de vulnerabilidade,
como reconhecê-las no binário, as proteções modernas, e o pipeline (fuzzing → triagem →
exploração) — com a moldura ética clara.

> **Escopo legal.** Encontrar e explorar bugs só é legítimo em alvos **seus**, em programas de
> *bug bounty*/divulgação responsável autorizados, em CTFs, ou sob contrato de pentest. Fora
> disso, é crime. Este arquivo ensina a técnica defensável; o uso é sua responsabilidade.

---

## 1. Por que bugs de memória importam

Linguagens como C/C++ não checam limites nem gerenciam memória automaticamente. Um erro deixa o
programa ler/escrever onde não devia — e um atacante pode transformar isso em **execução de
código**. A maioria das falhas críticas históricas é de **corrupção de memória**.

---

## 2. As classes clássicas — reconhecimento no binário

| Classe | O bug | Sinal no binário |
|---|---|---|
| **Stack buffer overflow** | Escreve além de um buffer local, atinge o endereço de retorno | `strcpy`/`gets`/`sprintf`/`memcpy` com tamanho controlado pela entrada; buffer local + cópia sem checagem |
| **Heap overflow** | Transborda um bloco de `malloc`, corrompe metadados/objetos vizinhos | `malloc(n)` com `n` da entrada; cópia sem validar |
| **Use-after-free (UAF)** | Usa memória já liberada (`free`), possivelmente realocada e controlada | `free` seguido de uso do mesmo ponteiro; ponteiro não zerado |
| **Double free** | Libera duas vezes o mesmo bloco | Dois `free` no mesmo ponteiro em caminhos que se cruzam |
| **Off-by-one** | Um byte além do limite (ex.: `<=` onde devia ser `<`) | Laços/índices com fronteira errada |
| **Integer overflow** | Cálculo de tamanho estoura e vira pequeno → aloca menos que copia | `mul`/`add` sobre tamanho antes de `malloc`; sem checagem de overflow |
| **Format string** | `printf(entrada)` — a entrada vira formato | `printf`/`fprintf` com 1º argumento controlado pelo usuário |
| **Type confusion** | Objeto tratado como tipo errado (comum em C++/navegadores) | Cast/vtable inconsistente |

O padrão mais rentável de procurar: **entrada do usuário → chega a uma operação de cópia/tamanho
sem validação**. Rastrear esse fluxo ("taint") é a essência do *source-to-sink*.

---

## 3. As proteções modernas (mitigations) — leia com `checksec`

```bash
checksec --file=./BIN
```
| Proteção | O que faz | Efeito no ataque |
|---|---|---|
| **NX / DEP** | Marca a pilha/heap como não-executável | Impede executar shellcode injetado → força **ROP** |
| **Stack canary** | Valor sentinela antes do end. de retorno, checado no epílogo | Detecta stack overflow linear → precisa vazar/contornar o canário |
| **ASLR** | Sorteia endereços de carga a cada execução | Endereços imprevisíveis → precisa de um **leak** de endereço |
| **PIE** | Executável reposicionável (ASLR também no código) | Nem o binário tem base fixa |
| **RELRO** | Torna a GOT somente-leitura (full RELRO) | Impede sobrescrever a GOT |
| **FORTIFY_SOURCE** | Versões checadas de `memcpy`/`strcpy` | Detecta alguns overflows em tempo de execução |

Exploração moderna é, em grande parte, **derrotar essas camadas uma a uma**: um *info leak*
vence ASLR; **ROP** vence NX; um *overflow* preciso ou um leak vence o canário.

---

## 4. ROP — Return-Oriented Programming (a resposta ao NX)

Com NX, você não pode injetar código executável. **ROP** contorna isso reutilizando pedacinhos
do **próprio** código do programa: sequências que terminam em `ret`, chamadas **gadgets**.
Encadeando endereços de gadgets na pilha, você "programa" com peças existentes.

```bash
ropper -f ./BIN --search "pop rdi; ret"     # achar um gadget que carrega RDI
ROPgadget --binary ./BIN | grep "pop rdi"
```
Uma *ROP chain* típica prepara argumentos em registradores (via gadgets `pop`) e chama, por
exemplo, `system("/bin/sh")` ou uma syscall `execve`. **pwntools** monta cadeias
semi-automaticamente (`ROP(elf)`). Variantes: **JOP** (jump-oriented), **ret2libc**,
**ret2dlresolve**, **SROP**.

---

## 5. Fuzzing — encontrar os bugs em escala

Você não acha a maioria dos bugs lendo; você os acha **jogando milhões de entradas
malformadas** e vendo o que quebra. Isso é *fuzzing*.

| Fuzzer | Estilo | Uso |
|---|---|---|
| **AFL++** | Guiado por cobertura, mutacional | O padrão; instrumenta o alvo e evolui entradas que exploram caminhos novos |
| **libFuzzer** | In-process, por função (harness) | Ideal para bibliotecas; compila com sanitizers |
| **honggfuzz** | Cobertura, robusto | Alternativa ao AFL++ |
| **Fuzzing de binário fechado** | QEMU-mode do AFL++, ou emulação | Quando não há fonte |

Combine com **sanitizers** (ASan, UBSan, MSan) que transformam corrupções silenciosas em
crashes imediatos e diagnósticos. O pipeline: **fuzz → coletar crashes → triar (dedupe,
minimizar) → avaliar explorabilidade → PoC**.

---

## 6. Execução simbólica — quando o fuzzing empaca

Fuzzing tem dificuldade com condições estreitas ("aceita só se a entrada == este hash"). A
**execução simbólica** ([`60-teoria-avancada.md`](60-teoria-avancada.md)) trata a entrada como
variável simbólica e usa um solucionador **SMT** (Z3) para calcular *exatamente* que entrada
alcança um ponto (ex.: um bloco vulnerável). **angr** e **KLEE** são as ferramentas. Na prática,
combina-se com fuzzing (*concolic*): o fuzzer explora o largo, o simbólico fura os gargalos.

---

## 7. O pipeline completo e a divulgação responsável

```
 alvo → fuzz/estático → crash → triagem → causa raiz (RE) → explorabilidade → PoC → REPORTE
```
Achado um bug real:
- **Divulgação responsável / coordenada:** reporte ao fornecedor, dê prazo (tipicamente 90
  dias), permita a correção antes de tornar público. Programas de *bug bounty* formalizam isso.
- **CVE:** registre o identificador; documente causa, impacto, versões afetadas, correção.
- **Não** explore em produção alheia, não venda para quem transforma em arma, não divulgue
  0-day sem correção disponível. A ética aqui é o que separa pesquisa de crime.

---

## 8. Ética e lei (releitura para este tema)

- **Legítimo:** seus sistemas; bug bounty/VDP autorizados; CTF; pentest sob contrato; pesquisa
  com divulgação responsável.
- **Zona de risco:** testar em software de terceiros sem autorização — mesmo "só para estudar"
  — pode violar leis de acesso não autorizado (CFAA nos EUA, Lei 12.737/2012 no Brasil) e o
  DMCA §1201 ao contornar proteção. As isenções de segurança de boa-fé existem, mas são
  específicas.
- **Regra prática:** sem autorização escrita ou um programa público de divulgação, não teste.
  Treine em CTFs e VMs vulneráveis feitas para isso (ver [`70-pratica.md`](70-pratica.md)).

---

## Autoteste

1. Qual o padrão geral que você procura ao caçar bugs de memória (fonte → sink)?
2. Explique como um stack overflow atinge o endereço de retorno e o que o **canário** faz contra isso.
3. Por que o NX "força ROP"? O que é um gadget e como você acha um?
4. Combine cada proteção (NX, ASLR, canário, RELRO) com o que o atacante precisa para vencê-la.
5. Por que um integer overflow no cálculo de tamanho leva a um heap overflow?
6. Quando a execução simbólica supera o fuzzing, e como as duas se combinam (concolic)?
7. Descreva a divulgação responsável e a linha ética/legal entre pesquisa e crime.
