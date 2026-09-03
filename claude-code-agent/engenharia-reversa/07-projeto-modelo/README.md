# Projeto-modelo — Crackme de três níveis + solucionador automático

**Nível:** intermediário · alvo de treino de engenharia reversa

Um **crackme** é um programa feito de propósito para ser revertido. Este aqui pede uma
senha/serial e diz "Acesso concedido" ou "Acesso negado". Seu trabalho é descobrir, **olhando
o binário**, quais entradas o desbloqueiam — sem ler o código-fonte primeiro.

Vem com **três níveis** de dificuldade crescente e um **solucionador automático em Python**
(`solver.py`) que encontra as três respostas sozinho, ilustrando três técnicas reais de RE
automatizada. Tudo aqui **roda de verdade** — é verificado por `make check`.

> Ético e seguro: o programa só compara strings no console. Não faz rede, não escreve em
> disco, não é malicioso. É o campo de treino legítimo do RE.

---

## Pré-requisitos

- Linux (ou WSL2/macOS) com **GCC**, **make**, **binutils** e **Python 3** — ver
  [`../03-instalacao.md`](../03-instalacao.md), seção 2.
- Opcional, para reverter à mão: **GDB**, **Ghidra** e/ou **radare2**.
- Testado em: Ubuntu 22.04.5, GCC 11.4.0, GNU Make 4.3, Python 3.10.12, binutils 2.38 — em 03/09/2026.

---

## Comandos exatos

```bash
cd 07-projeto-modelo

make            # compila ./crackme (com símbolos de depuração — alvo mais fácil)
make stripped   # ./crackme_stripped (sem símbolos — mais realista)
make hard       # ./crackme_hard (-O2 + stripped — o mais difícil)

# Jogar manualmente (o programa é o oráculo):
./crackme 1 uma-tentativa
./crackme 2 outra-tentativa
./crackme 3 0000-0000-0000

# Ver as respostas corretas em ação (o "gabarito vivo"):
make run

# Deixar o solucionador automático achar as três respostas:
make solve      # equivale a: python3 solver.py ./crackme

# Rodar toda a verificação (compila as 3 variantes + testa + roda o solver):
make check

# Limpar:
make clean
```

**Saída esperada de `make solve`** (a resposta do nível 3 varia — há muitos seriais válidos):

```
nivel 1: 'engenharia-reversa-2026'  ->  CONFIRMADO
nivel 2: 'GhidraRadare'             ->  CONFIRMADO
nivel 3: '0000-9999-6000'           ->  CONFIRMADO
```

O solver leva **~6 segundos** e funciona **também no binário sem símbolos**
(`python3 solver.py ./crackme_stripped`) — porque nenhuma etapa depende de nomes de função,
só do comportamento observável.

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md      # este arquivo
├── crackme.c      # o alvo: 3 níveis (string clara, XOR, serial por regras)
├── Makefile       # compila 3 variantes de dificuldade; alvos run/solve/check
├── solver.py      # solucionador automático (3 técnicas de RE)
├── test.sh        # suíte de verificação (positivos + negativos + solver)
└── SOLUCAO.md     # o passo a passo de como reverter cada nível À MÃO (gabarito)
```

---

## Os três níveis e o que cada um ensina

| Nível | Proteção | Técnica de RE que ele treina |
|---|---|---|
| **1** | Senha em **texto claro** no binário | `strings`, inspeção de `.rodata`, o "oráculo" |
| **2** | Senha **cifrada** (XOR de byte único) — o texto claro não existe no arquivo | achar dados, entender uma transformação, revertê-la (XOR é reversível) |
| **3** | **Serial por regras** (formato + soma dos dígitos + múltiplo) | ler a *lógica* de validação em assembly e reconstruí-la como restrições |

Cada nível espelha um esquema de proteção real, do mais ingênuo ao mais parecido com uma
verificação de licença de verdade.

---

## O que cada decisão de projeto ensina

- **Compilar em 3 variantes (`-g`, `stripped`, `-O2 -s`)** mostra, no mesmo código, como
  **símbolos e otimização mudam drasticamente a dificuldade**. Compare no Ghidra: a versão
  `-g` tem nomes (`nivel1`, `SEGREDO_CIFRADO`); a `stripped` só tem endereços; a `-O2` tem o
  fluxo reorganizado pelo compilador. Essa é a diferença entre um CTF didático e um alvo real.
- **O binário como oráculo** (`solver.py` testa candidatos contra o programa real) ensina o
  princípio central do RE dinâmico: você não precisa provar sua teoria no papel — **pergunta
  ao programa**. É o que torna o solver imune à ofuscação de nomes.
- **Nível 3 com muitos seriais válidos** (não um único "serial correto") reflete como
  licenças reais funcionam: uma *fórmula* de validação, não uma senha fixa. É por isso que
  keygens existem — quem entende a fórmula gera infinitos seriais.
- **Coisas que tutoriais omitem e que estão aqui:** tratamento de argumentos inválidos
  (`uso()`), códigos de saída significativos (`0`/`1`/`2`), verificação de tamanho antes de
  ler memória (nível 2), e uma **suíte de testes com casos negativos** — não só o caminho feliz.

---

## Como usar para aprender (roteiro sugerido)

1. **Não olhe `SOLUCAO.md` ainda.** Compile com `make` e tente `./crackme 1 ...` no chute.
2. **Nível 1:** rode `strings ./crackme | less` e procure algo que pareça uma senha. Teste-a.
3. **Nível 2:** abra no Ghidra (ou `radare2 ./crackme`), ache a função do nível 2, veja o
   array de bytes e a operação XOR. Reverta à mão. Confira em [`SOLUCAO.md`](SOLUCAO.md).
4. **Nível 3:** leia a lógica de validação no descompilador. Anote as regras. Construa um
   serial que as satisfaça.
5. **Depois** leia `solver.py` para ver como automatizar cada ataque, e rode `make check`.
6. **Desafio extra:** compile com `make hard` e refaça tudo no binário otimizado e stripped.

---

## Autoteste

1. Por que o solver funciona igualmente no binário **sem símbolos**?
2. No nível 2, por que a senha correta **não** aparece em `strings ./crackme`, mas o solver
   ainda a encontra?
3. O que muda no Ghidra entre `./crackme` (`-g`) e `./crackme_hard` (`-O2 -s`)?
4. Por que o nível 3 aceita muitos seriais diferentes, e o que isso tem a ver com "keygens"?
5. Cite dois casos **negativos** que `test.sh` verifica e por que testar o negativo importa.

> Gabarito detalhado em [`SOLUCAO.md`](SOLUCAO.md). Volte ao [`04-como-comecar.md`](../04-como-comecar.md)
> e ao [`06-exemplos.md`](../06-exemplos.md) para mais alvos.
