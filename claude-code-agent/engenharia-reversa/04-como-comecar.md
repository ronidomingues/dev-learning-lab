# 04 · Como começar — reverta sua primeira função hoje

**Nível:** iniciante · **Pré-requisito:** ambiente do [`03-instalacao.md`](03-instalacao.md) pronto
(ou use godbolt.org/dogbolt.org, sem instalar nada).

O objetivo deste arquivo é levar você **do zero a "eu entendi um binário"** em uma sessão.
Sem teoria demais — a teoria vem depois ([`12`](12-arquitetura-e-assembly.md) em diante).
Aqui você **faz**.

---

## Passo 0 — o ciclo de trabalho do reverser

Toda sessão de RE é uma variação deste ciclo:

```
   compilar/obter binário  →  observar (estático)  →  hipótese
              ↑                                            │
              └────────  confirmar (dinâmico) ←───────────┘
```

Você olha o binário parado, forma uma teoria ("acho que essa função compara a senha"), e
confirma rodando/depurando. Repete até entender. **O binário é o oráculo:** na dúvida,
pergunte a ele.

---

## Passo 1 — crie um alvo que você entende

Comece revertendo algo que você mesmo escreveu — assim você confere se acertou.

```bash
mkdir -p ~/re-lab && cd ~/re-lab
cat > alvo.c <<'EOF'
#include <stdio.h>
#include <string.h>

int checar(const char *senha) {
    return strcmp(senha, "abrete-sesamo") == 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && checar(argv[1]))
        printf("Certo!\n");
    else
        printf("Errado.\n");
    return 0;
}
EOF
gcc -g -O0 -o alvo alvo.c        # -g: com símbolos; -O0: sem otimização (mais fácil)
./alvo teste                     # -> Errado.
```

**Verificação:** `./alvo teste` imprime `Errado.` e `./alvo abrete-sesamo` imprime `Certo!`.
Agora **finja que você não viu o código** e recupere a senha só do binário.

---

## Passo 2 — o triângulo básico: `file`, `strings`, `objdump`

### `file` — que tipo de bicho é este?
```bash
file alvo
# esperado: ELF 64-bit LSB pie executable, x86-64, ... dynamically linked, ... not stripped
```
Leia isso: é um **ELF** (formato Linux), **64 bits**, **x86-64**, ligado dinamicamente, e
**not stripped** (tem símbolos — nomes de função). "not stripped" é ótimo para você.

### `strings` — o texto que sobrou
```bash
strings alvo | grep -iE 'sesamo|certo|errado'
# esperado:
# abrete-sesamo
# Certo!
# Errado.
```
**Você já achou a senha.** Em binários ingênuos, `strings` resolve o caso. Confirme no oráculo:
```bash
./alvo abrete-sesamo    # -> Certo!
```
Esse é o seu primeiro "aha". Mas vamos além, porque nem sempre a senha está em texto claro.

### `objdump` — o assembly
```bash
objdump -d alvo | sed -n '/<checar>:/,/ret/p'
```
Você verá algo assim (endereços variam):
```asm
0000000000001149 <checar>:
    1149:  55                    push   %rbp
    114a:  48 89 e5              mov    %rsp,%rbp
    114d:  48 89 7d f8           mov    %rdi,-0x8(%rbp)   ; salva o argumento (a senha)
    ...
    115c:  48 8d 05 a1 0e 00 00  lea    0xea1(%rip),%rax  ; carrega endereço de "abrete-sesamo"
    ...
    116b:  e8 d0 fe ff ff        call   ...<strcmp>       ; chama strcmp
    1170:  85 c0                 test   %eax,%eax          ; strcmp==0 ?
    ...
```
Ainda não sabe ler assembly? Tudo bem. **Reconheça três coisas:** há um `call strcmp`
(comparação de string), um `lea` que carrega um endereço (a senha esperada), e um `test`
que checa se deu igual. Isso já conta a história: *"pega o argumento, compara com uma string
fixa"*. O nome exato da string você pega com `strings`.

> **Sem instalar nada?** Cole o `alvo.c` em https://godbolt.org e veja o assembly ao lado do
> C, coloridos e ligados linha a linha. É a melhor forma de aprender a ler assembly.

---

## Passo 3 — descompile no Ghidra (o "raio-X")

Assembly é detalhado demais para ler tudo. Um **descompilador** reconstrói algo parecido com
C. O Ghidra faz isso de graça.

1. Abra: `./ghidraRun` (ou `ghidra` se colocou no PATH).
2. `File → New Project → Non-Shared Project`, dê um nome, `Finish`.
3. `File → Import File` → escolha `~/re-lab/alvo`. Aceite os padrões.
4. Dê **duplo-clique** no arquivo importado. O Ghidra pergunta se quer analisar: **Yes**,
   deixe as opções padrão, `Analyze`. Espere alguns segundos.
5. Na janela **CodeBrowser**, painel *Symbol Tree* → *Functions* → clique em **`checar`**.
6. No painel **Decompile** (à direita), você vê:

```c
undefined8 checar(char *param_1) {
    int iVar1;
    iVar1 = strcmp(param_1, "abrete-sesamo");
    return (undefined8)(iVar1 == 0);
}
```

**Isso é engenharia reversa acontecendo.** O Ghidra reconstruiu a lógica: compara o argumento
com `"abrete-sesamo"` e retorna verdadeiro se igual. Você recuperou o comportamento sem o
fonte.

**Verificação de que deu certo:** o pseudocódigo menciona `strcmp` e a string literal
`"abrete-sesamo"`, e a função tem um parâmetro (a senha). Se a janela Decompile mostrar isso,
o Ghidra está funcionando e você acabou de reverter sua primeira função.

> Prefere linha de comando? `radare2 -A alvo`, depois `s sym.checar; pdf` (ver
> [`05-manual-de-uso.md`](05-manual-de-uso.md)). Ou envie o binário para https://dogbolt.org
> e compare vários descompiladores.

---

## Passo 4 — confirme no depurador (a análise dinâmica)

Estático te deu a teoria; o **GDB** confirma vendo o programa rodar por dentro.

```bash
gdb ./alvo
```
No prompt do GDB (ou `pwndbg>`/`gef➤` se instalou o plugin):
```gdb
break checar          # pausa ao entrar na função checar
run senha-errada      # roda passando "senha-errada"
```
O programa para na entrada de `checar`. Veja o argumento (a senha) que chegou:
```gdb
x/s $rdi              # mostra a string apontada por RDI (1º argumento na convenção x86-64)
# esperado: 0x... : "senha-errada"
```
Continue até o `strcmp` e observe os dois lados sendo comparados. Depois:
```gdb
finish                # roda até a função retornar
# veja o valor de retorno em RAX: 0 = senhas diferentes
```
**O que você aprendeu observando:** o 1º argumento de uma função vai no registrador **RDI**;
o valor de retorno sai em **RAX**. Isso é a *convenção de chamada* x86-64
([`16-a-pilha-e-convencoes.md`](16-a-pilha-e-convencoes.md)) — a base de toda leitura de assembly.

---

## Passo 5 — o desafio de verdade: senha que não é string

Agora um alvo onde `strings` **não** entrega a senha (como o nível 2 do projeto-modelo):

```bash
cat > alvo2.c <<'EOF'
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc != 2) return 1;
    char esperado[8];
    // "SENHA123" ofuscada byte a byte, montada em tempo de execução
    unsigned char e[] = {0x53,0x45,0x4e,0x48,0x41,0x31,0x32,0x33};
    memcpy(esperado, e, 8);
    if (memcmp(argv[1], esperado, 8) == 0) printf("Certo!\n");
    else printf("Errado.\n");
    return 0;
}
EOF
gcc -g -O0 -o alvo2 alvo2.c
strings alvo2 | grep -i senha    # (nada — a senha não é uma string literal)
```
Aqui você **precisa** do descompilador ou do depurador. No Ghidra, a função `main` mostra o
array `{0x53,0x45,...}`. Traduza de hex para ASCII:
```bash
python3 -c "print(bytes([0x53,0x45,0x4e,0x48,0x41,0x31,0x32,0x33]).decode())"
# esperado: SENHA123
```
Ou, no GDB, pare no `memcmp` e leia o segundo argumento:
```gdb
break memcmp
run qualquercoisa12
x/s $rsi          # 2º argumento (a senha esperada) na convenção x86-64
```
Confirme: `./alvo2 SENHA123` → `Certo!`. **Este é o padrão que se repete no curso inteiro:
quando o estático não basta, o dinâmico entrega.**

---

## Os primeiros cinco erros de quem começa (no uso, não na instalação)

1. **Ler assembly linha a linha tentando entender cada instrução.** Não faça isso. Reconheça
   *padrões* (chamada de função, laço, comparação) e use o descompilador para o resto.
2. **Confiar cegamente no descompilador.** Ele erra tipos, inventa variáveis e às vezes mente.
   Cruze com o assembly quando algo não fizer sentido ([`75-armadilhas.md`](75-armadilhas.md)).
3. **Esquecer que otimização muda tudo.** `-O0` é fácil; `-O2` reordena e funde código. Comece
   sempre com `-O0` nos seus alvos de treino, depois suba.
4. **Não usar o oráculo.** Ficar teorizando no papel quando bastava `./alvo tentativa` ou um
   breakpoint para confirmar em 5 segundos.
5. **Analisar malware na máquina de trabalho.** Nunca. Use VM isolada
   ([`20-analise-de-malware.md`](20-analise-de-malware.md)). Para crackmes inofensivos como
   estes, tudo bem.

---

## Onde ir depois

- Mais alvos resolvidos, do trivial ao de produção: [`06-exemplos.md`](06-exemplos.md).
- O projeto-modelo completo (crackme de 3 níveis + solver): [`07-projeto-modelo/`](07-projeto-modelo/).
- A referência das ferramentas: [`05-manual-de-uso.md`](05-manual-de-uso.md).
- Para *entender* o que você está vendo: [`10-fundamentos.md`](10-fundamentos.md) e
  [`12-arquitetura-e-assembly.md`](12-arquitetura-e-assembly.md).

---

## Autoteste

1. Descreva o ciclo de trabalho do reverser em uma frase.
2. Que informação o comando `file` te dá, e por que "not stripped" facilita sua vida?
3. Em `alvo`, `strings` bastou. Em `alvo2`, não. Por quê exatamente?
4. Na convenção x86-64, onde chega o 1º argumento de uma função e onde sai o valor de retorno?
5. O descompilador do Ghidra é confiável a ponto de você nunca olhar o assembly? Justifique.
6. Você tem um crackme. Qual a primeira coisa que roda (mais barata) antes de abrir o Ghidra?
