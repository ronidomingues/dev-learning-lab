# 70 · Prática — 12 laboratórios progressivos

**Nível:** todos (crescente) · **Data:** 03/09/2026

RE se aprende **com as mãos**. Estes 12 laboratórios vão do primeiro `strings` até unpacking e
execução simbólica. Cada um: **objetivo → passos → critério de sucesso → dica**. Use o ambiente
do [`03-instalacao.md`](03-instalacao.md). Faça na ordem; cada lab pressupõe o anterior.

> Ética: todos os alvos são **seus** (você os compila) ou desafios públicos feitos para treino
> (crackmes.one, picoCTF). É o campo legítimo. Nunca treine em software de terceiros.

---

## Lab 1 — `strings` e o primeiro segredo
**Objetivo:** achar uma senha em texto claro.
**Passos:** compile `ex1.c` do [`06-exemplos.md`](06-exemplos.md); rode `strings ex1 | less`;
identifique a senha; confirme com `./ex1 <senha>`.
**Sucesso:** o programa imprime "OK".
**Dica:** filtre com `grep`; a senha costuma destoar das strings de sistema.

---

## Lab 2 — Ler o assembly de um `if`
**Objetivo:** entender uma decisão sem descompilador.
**Passos:** compile `ex2.c` (`-O0`); `objdump -d -M intel ex2`; ache o `cmp`/`jz`; decodifique a
constante em hex; resolva a equação e passe o número certo.
**Sucesso:** achar a entrada aceita **lendo só o assembly**.
**Dica:** `0x7ea = 2026`. Todo `cmp reg, imm` é uma comparação com aquele valor.

---

## Lab 3 — Sua primeira sessão de Ghidra
**Objetivo:** descompilar e anotar uma função.
**Passos:** importe `ex2` no Ghidra; analise; abra `main` no *Decompile*; **renomeie** variáveis
e escreva um comentário explicando a lógica; exporte o pseudo-C.
**Sucesso:** um pseudo-C anotado que qualquer colega entenderia.
**Dica:** clique numa variável e tecle `L` para renomear; `;` para comentar.

---

## Lab 4 — GDB: ler argumentos ao vivo
**Objetivo:** vazar a senha esperada de um `strcmp` pela convenção de chamada.
**Passos:** `gdb ex1`; `set disassembly-flavor intel`; `break strcmp`; `run chute`;
`x/s $rdi` e `x/s $rsi`.
**Sucesso:** ver a senha esperada em RSI sem tê-la procurado com `strings`.
**Dica:** RSI é o 2º argumento em System V ([`16`](16-a-pilha-e-convencoes.md)).

---

## Lab 5 — O projeto-modelo, nível 1 e 2
**Objetivo:** resolver os dois primeiros níveis do crackme à mão.
**Passos:** `cd 07-projeto-modelo; make`; resolva o nível 1 com `strings`; para o nível 2, ache
o array cifrado (`objdump -s -j .rodata`) e o `xor 0x42`, reverta com Python.
**Sucesso:** `./crackme 1 ...` e `./crackme 2 ...` concedem acesso.
**Dica:** o gabarito comentado está em [`07-projeto-modelo/SOLUCAO.md`](07-projeto-modelo/SOLUCAO.md) — só depois de tentar.

---

## Lab 6 — Patching: "sempre conceder"
**Objetivo:** modificar o binário para aceitar qualquer entrada.
**Passos:** `r2 -w ex1`; `aaa`; ache o salto de decisão em `main`; inverta-o (`je`↔`jne`) ou
NOP-o com `wa`/`wx`; saia e teste com uma entrada errada.
**Sucesso:** `./ex1 qualquercoisa` imprime "OK".
**Dica:** identifique o `test eax,eax` após o `call` e o salto que o segue.

---

## Lab 7 — Tracing com ltrace e strace
**Objetivo:** entender comportamento sem ler assembly.
**Passos:** `ltrace ./crackme 2 chute` (veja as comparações); compile `ex9.c` do [`06`](06-exemplos.md)
e rode `strace -e trace=openat,read ./ex9`.
**Sucesso:** descrever o que cada programa faz só pela saída do tracer.
**Dica:** `ltrace` frequentemente entrega a senha de um crackme direto.

---

## Lab 8 — Frida: forçar um retorno
**Objetivo:** contornar uma checagem sem patch nem GDB.
**Passos:** compile uma função `int valido(){ return 0; }` chamada no `main`; escreva um hook
Frida que faz `onLeave(retval){ retval.replace(1); }`; rode `frida -l hook.js -f ./bin`.
**Sucesso:** o programa se comporta como se a checagem tivesse passado.
**Dica:** ache o nome do símbolo com `nm` ou use `Module.getExportByName`.

---

## Lab 9 — Reconhecer e desempacotar UPX
**Objetivo:** identificar packing e revertê-lo.
**Passos:** `gcc -O2 -o ex8 ex2.c && upx -9 ex8`; note que `strings` some; `file ex8` mostra UPX;
`upx -d -o ex8_orig ex8`; compare `objdump -d` antes e depois.
**Sucesso:** recuperar o código desempacotado e reverter normalmente.
**Dica:** meça entropia com `binwalk -E ex8` para ver a assinatura do packing.

---

## Lab 10 — Capstone: desmontar bytes crus
**Objetivo:** automatizar desmontagem em Python.
**Passos:** rode o script do exemplo 7 do [`06`](06-exemplos.md); depois extraia os bytes da
`.text` de um binário seu (com pyelftools/LIEF) e desmonte com Capstone.
**Sucesso:** imprimir instruções corretas a partir de bytes.
**Dica:** confira contra `objdump -d` para validar seu desmontador.

---

## Lab 11 — Execução simbólica com angr
**Objetivo:** deixar o solucionador achar a entrada.
**Passos:** instale angr (venv); escreva um script que carrega `./crackme`, explora até a saída
"concedido" e evita "negado", e imprime a entrada encontrada (esqueleto no [`60`](60-teoria-avancada.md)).
**Sucesso:** angr devolve uma entrada que passa no nível 2 ou 3.
**Dica:** comece pelo nível 2 (mais direto); use `state.posix.dumps(0)` para ler a entrada.

---

## Lab 12 — Desafio de CTF real
**Objetivo:** aplicar tudo num alvo que você não escreveu.
**Passos:** pegue um crackme em **crackmes.one** (nível "1"/"2") ou um desafio *reversing* do
**picoCTF**; resolva combinando estático (Ghidra), dinâmico (GDB/ltrace) e, se preciso, angr.
Escreva um pequeno *writeup* do seu método.
**Sucesso:** obter a flag/senha e explicar **como** — não só que resolveu.
**Dica:** o *writeup* é o que consolida o aprendizado e vira portfólio.

---

## Como continuar treinando

- **crackmes.one** — milhares de crackmes por dificuldade.
- **picoCTF / pwn.college / crackmes** — desafios com trilha.
- **Reverse Engineering challenges** de CTFs (CTFtime lista eventos).
- **Repita** um alvo com `make hard` (otimizado + stripped) para subir a dificuldade.
- **Reverta software livre** cujo fonte você tem: reverta o binário, compare com o fonte,
  meça o quanto acertou. É o melhor loop de feedback que existe.

---

## Autoteste (de método, não de fatos)

1. Qual a **primeira** ferramenta que você roda num alvo novo, e por quê ela primeiro?
2. Quando você escala de `ltrace` para GDB, e de GDB para Ghidra?
3. No lab 6, como você decidiu **qual** byte inverter, e como confirmou que funcionou?
4. Por que resolver o mesmo crackme com angr (lab 11) *depois* de fazê-lo à mão ensina mais?
5. O que um bom *writeup* de CTF deve conter além da resposta?
