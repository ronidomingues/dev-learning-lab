# SOLUÇÃO — como reverter cada nível à mão

**Só leia depois de tentar.** Este é o gabarito comentado, com **desmontagem real** do
`./crackme` compilado no ambiente de referência (Ubuntu 22.04, GCC 11.4). Os endereços na
sua máquina podem diferir; a lógica não.

Ferramentas usadas: `strings`, `objdump`, `gdb`. Tudo funciona igual no Ghidra/radare2.

---

## Nível 1 — senha em texto claro

**Ataque:** a senha é comparada com um literal, que fica na seção `.rodata` (dados
somente-leitura). Literais de texto sobrevivem à compilação intactos.

```console
$ strings ./crackme | grep -i engenharia
engenharia-reversa-2026
```

Pronto. Teste no oráculo:

```console
$ ./crackme 1 engenharia-reversa-2026
[+] Acesso concedido ao nivel 1. ...
```

**Lição:** nunca guarde segredo como string literal num binário. `strings` é a primeira
coisa que qualquer analista roda. (Veja o dump da `.rodata` no nível 2 abaixo — a senha
está lá, à vista.)

---

## Nível 2 — senha cifrada com XOR de byte único

**Ataque:** a senha em texto claro **não** está no binário. Desmontando a função `nivel2`:

```asm
125d:  48 83 f8 0c            cmp    $0xc,%rax           ; compara tamanho com 0xc = 12
...                                                       ; (strlen(tentativa) != 12 -> falha)
1282:  0f b6 00               movzbl (%rax),%eax          ; carrega um byte do array cifrado
1285:  83 f0 42               xor    $0x42,%eax           ; <-- XOR com a chave 0x42
1296:  0f b6 00               movzbl (%rax),%eax          ; carrega um byte da SUA tentativa
1299:  38 45 f7               cmp    %al,-0x9(%rbp)        ; compara os dois
```

Três fatos saltam do assembly:
1. **`cmp $0xc`** → o tamanho esperado é **12**.
2. **`xor $0x42`** → cada byte cifrado é combinado com a chave **0x42** (66 decimal).
3. A comparação é byte a byte contra a sua entrada.

Onde está o array cifrado? No dump da `.rodata`, logo após a senha do nível 1:

```console
$ objdump -s -j .rodata ./crackme
 2020 052a2b26 30231023 26233027 00000000  .*+&0#.#&#0'....
```

Os 12 bytes: `05 2a 2b 26 30 23 10 23 26 23 30 27`. XOR é **reversível**: se `cifra = texto ^
chave`, então `texto = cifra ^ chave`. Aplicando `^ 0x42`:

```console
$ python3 -c "print(bytes(b^0x42 for b in bytes.fromhex('052a2b263023102326233027')).decode())"
GhidraRadare
```

Confirme:

```console
$ ./crackme 2 GhidraRadare
[+] Acesso concedido ao nivel 2. ...
```

**Lição:** XOR de byte único **não é criptografia**, é ofuscação — trivial de reverter
porque a chave está no próprio código (`xor $0x42`) e o dado cifrado, no binário. É o
"pig latin" da proteção de software. (Ainda assim, aparece em malware real o tempo todo,
justamente por ser rápido de aplicar.)

O `solver.py` faz isso **sem saber a chave**: tenta as 256 possíveis sobre os bytes das
seções de dados e confirma no oráculo.

---

## Nível 3 — serial validado por regras (a "fórmula de licença")

**Ataque:** não há senha fixa; há uma *fórmula*. Precisamos ler a lógica de validação.
Desmontando `nivel3`, os números mágicos contam a história:

```asm
130a:  48 83 f8 0e            cmp    $0xe,%rax            ; tamanho == 0xe = 14
1325:  3c 2d                  cmp    $0x2d,%al            ; caractere == 0x2d = '-'
1334:  3c 2d                  cmp    $0x2d,%al            ; outro '-'  (2 hifens)
...
13ec:  83 7d b4 2a            cmpl   $0x2a,-0x4c(%rbp)    ; soma == 0x2a = 42
...
1409:  69 d0 e8 03 00 00      imul   $0x3e8,%eax,%edx     ; *0x3e8 = *1000
1420:  6b c0 64               imul   $0x64,%eax,%eax      ; *0x64  = *100
...
145f:  48 69 c0 93 24 49 92   imul   $0xffffffff92492493  ; <-- divisao magica por 7
```

Decodificando os números:
- **`cmp $0xe` (14):** o serial tem 14 caracteres.
- **`cmp $0x2d` duas vezes (`'-'`):** há dois hífens → formato `AAAA-BBBB-CCCC`.
- **`imul $1000` e `imul $100`:** o código monta o **primeiro bloco como número**
  (`d0*1000 + d1*100 + d2*10 + d3`).
- **`cmpl $0x2a` (42):** a **soma dos dígitos é 42**.
- **`imul $0x92492493`:** esse valor bizarro é o compilador implementando **`% 7`** sem
  usar a instrução de divisão (lenta). `0x92492493` é a "constante mágica" da divisão por 7
  (técnica do livro *Hacker's Delight*). Ou seja: **o primeiro bloco é múltiplo de 7.**

> **Como reconhecer divisão por constante?** Quando você vê um `imul` por um número enorme e
> aparentemente aleatório seguido de shifts, é quase sempre o compilador trocando uma divisão
> por multiplicação. Ferramentas como o Ghidra frequentemente já mostram `x % 7` no
> descompilador, poupando esse trabalho.

**As regras recuperadas:**
1. formato `AAAA-BBBB-CCCC` (14 chars, 12 dígitos + 2 hífens);
2. a soma dos 12 dígitos é **42**;
3. o primeiro bloco (como número de 4 dígitos) é **múltiplo de 7**.

**Construir um serial válido** (um keygen mental): escolha o bloco 1 múltiplo de 7 —
digamos `0700` (= 700, múltiplo de 7; dígitos somam 7). Faltam `42 − 7 = 35` a distribuir
nos 8 dígitos restantes: `9998` (soma 35) e `0000` (soma 0). Serial: `0700-9998-0000`.

```console
$ ./crackme 3 0700-9998-0000
[+] Acesso concedido ao nivel 3. ...
```

Existem **milhares** de seriais válidos — de propósito. É exatamente por isso que, quando
alguém reverte a fórmula de licença de um software real, consegue escrever um **keygen** que
gera infinitas chaves. A defesa real contra isso não é ocultar a fórmula (sempre reversível),
e sim **assinatura criptográfica**: a chave é assinada com uma chave privada que o atacante
não tem (ver [`../18-ofuscacao-e-packers.md`](../18-ofuscacao-e-packers.md) e
[`../criptografia`](../criptografia/)).

**Lição:** validação local de licença é sempre quebrável por quem tem o binário — o cliente
tem tudo que precisa. Isso é um limite teórico, não uma falha de implementação.

---

## Recapitulando as três técnicas

| Nível | Você usou | Ferramenta-chave | Defesa correta contra o ataque |
|---|---|---|---|
| 1 | Busca de strings | `strings` | Não guardar segredos no cliente |
| 2 | Reverter uma transformação | `objdump` + XOR | Cripto de verdade (a chave não pode estar no binário) |
| 3 | Reconstruir a lógica de validação | descompilador | Assinatura criptográfica do serial (servidor) |

O tema comum: **tudo que está no binário do lado do cliente é, em princípio, recuperável.**
Ofuscação aumenta o custo do ataque; não o impede. Guarde isso — é a lição mais importante
do curso inteiro.
