# 10 · Fundamentos — do código-fonte ao binário (e o que se perde)

**Nível:** iniciante → intermediário · **Data:** 03/09/2026

Para *reverter* um binário, você precisa entender como ele foi *construído*. Este arquivo
percorre o caminho `código-fonte → executável` e marca, em cada etapa, **o que sobra e o que
é jogado fora** — porque a engenharia reversa é, exatamente, o trabalho de reconstruir o que
foi jogado fora.

---

## 1. O pipeline de build, etapa por etapa

Pegue `soma.c`:
```c
int soma(int a, int b) { return a + b; }
```

A transformação em executável tem **quatro** etapas (o `gcc` esconde todas atrás de um comando):

```
soma.c ──(1)pré-processador──▶ soma.i ──(2)compilador──▶ soma.s ──(3)montador──▶ soma.o ──(4)linker──▶ executável
 (texto C)                     (C expandido)             (assembly)             (obj/machine)          (ELF final)
```

| # | Etapa | Ferramenta | Entrada → Saída | O que faz |
|---|---|---|---|---|
| 1 | Pré-processamento | `cpp` | `.c` → `.i` | Resolve `#include`, `#define`, `#ifdef`. Comentários **somem aqui**. |
| 2 | Compilação | `cc1` (parte do gcc) | `.i` → `.s` | Traduz C para **assembly**. Aqui nasce a decisão de registradores, otimização, layout. |
| 3 | Montagem | `as` | `.s` → `.o` | Assembly → **código de máquina** (bytes) num *object file* relocável. |
| 4 | Ligação | `ld` | `.o` (+ libs) → executável | Junta objetos, resolve símbolos externos (`printf`), fixa endereços. |

Veja cada etapa você mesmo:
```bash
gcc -E soma.c -o soma.i     # 1: pré-processado (abra e veja o C expandido)
gcc -S soma.c -o soma.s     # 2: assembly legível
gcc -c soma.c -o soma.o     # 3: object file (binário; veja com: objdump -d soma.o)
gcc soma.c -o soma          # 4: executável final
```

O assembly gerado (etapa 2, `-O0`, Intel):
```asm
soma:
    push rbp
    mov  rbp, rsp
    mov  DWORD PTR [rbp-0x4], edi   ; guarda 'a' (1º arg em EDI)
    mov  DWORD PTR [rbp-0x8], esi   ; guarda 'b' (2º arg em ESI)
    mov  edx, DWORD PTR [rbp-0x4]
    mov  eax, DWORD PTR [rbp-0x8]
    add  eax, edx                   ; a + b
    pop  rbp
    ret                             ; retorna em EAX
```

---

## 2. A regra dos cinco porquês — "por que não dá para desfazer?"

**Pergunta:** por que reverter não devolve o `soma.c` original?

1. *Por quê?* Porque nomes, comentários e a formatação **não existem** no binário.
2. *Por que não existem?* Porque o compilador só precisa deles para *entender* o código; o
   processador executa por endereços e registradores, não por nomes. Guardá-los seria peso morto.
3. *Por que seria peso morto?* Porque cada byte a mais no executável custa disco, memória e
   tempo de carga — e o processador nunca lê o nome `soma`, só pula para o endereço dela.
4. *Por que o processador não usa nomes?* Porque a CPU é uma máquina de endereços e opcodes
   fixos, projetada para velocidade; resolver nomes em tempo de execução seria absurdamente lento.
5. *Por que essa é a fronteira?* Aqui paramos numa **decisão de projeto de hardware/economia**:
   CPUs trocam legibilidade por velocidade. Não é arbitrário nem um padrão que "só é assim" —
   é um trade-off físico (velocidade) e econômico (custo por byte) documentado desde os anos 1950.

**Conclusão fundamental:** a compilação é uma função **com perda** (*lossy*), como comprimir
uma foto em JPEG. Você recupera *uma* imagem parecida, nunca os pixels exatos. Reverter
reconstrói **comportamento equivalente**, não o texto original. Guarde isso — é o teorema
central do campo.

---

## 3. O que sobrevive e o que morre na compilação

| Elemento do fonte | Sobrevive no binário? | Observação para o reverser |
|---|---|---|
| **Lógica / algoritmo** | ✅ Sim (é o ponto) | Vira assembly; é o que você reconstrói |
| **Literais de string** | ✅ Sim, em `.rodata` | `strings` acha; a 1ª pista sempre |
| **Constantes numéricas** | ✅ Sim, como imediatos | `cmp eax, 0x7ea` = comparação com 2026 |
| **Estrutura de controle** (if/while) | ⚠️ Parcial | Vira saltos; o descompilador *reconstrói* if/while |
| **Nomes de função/variável** | ❌ Não (se *stripped*) | Só sobrevivem com símbolos de debug (`-g`) ou tabela de símbolos |
| **Tipos** (int, struct, float) | ⚠️ Inferível | Some o *nome* do tipo; o *tamanho* e uso deixam pistas |
| **Comentários** | ❌ Nunca | Removidos no pré-processamento |
| **Formatação, nomes de arquivo** | ❌ Nunca | Salvo em info de debug DWARF |

**"Stripped" vs. "not stripped"** é a diferença mais importante para a sua dor de cabeça:
```bash
gcc -g soma.c -o soma_debug    # símbolos + info DWARF: fácil
gcc soma.c -o soma_normal      # símbolos básicos: médio
strip soma_normal              # remove símbolos: difícil, só endereços
nm soma_debug | head           # vê nomes
nm soma_normal 2>&1 | head     # "no symbols" após strip
```
Software comercial é quase sempre **stripped**. Malware costuma ser stripped **e** ofuscado.

---

## 4. Estático vs. dinâmico — as duas lentes (definições formais)

- **Análise estática:** examinar o binário **sem executá-lo**. Desmontagem, descompilação,
  leitura de strings/seções. *Vantagem:* vê todos os caminhos, seguro (não roda código
  hostil). *Limite:* não sabe valores de tempo de execução; ofuscação e packing atrapalham.
- **Análise dinâmica:** **executar** o binário e observar. Depurador, tracing,
  instrumentação. *Vantagem:* mostra o comportamento real, valores concretos, desempacota
  packers "de graça" (o próprio programa se desempacota). *Limite:* vê só os caminhos que
  você acionou; perigoso com malware (precisa de isolamento).

Reverter de verdade **alterna** entre as duas: estático para mapear, dinâmico para confirmar.
Detalhes em [`14-analise-estatica.md`](14-analise-estatica.md) e
[`15-analise-dinamica.md`](15-analise-dinamica.md).

---

## 5. Interpretado, JIT e bytecode — nem todo binário é código de máquina

O caminho acima é de linguagens **compiladas para nativo** (C, C++, Rust, Go). Há outros mundos:

| Categoria | Exemplos | O que você reverte | Ferramenta |
|---|---|---|---|
| **Nativo compilado** | C, C++, Rust, Go | Código de máquina (x86/ARM) | Ghidra, IDA, r2 |
| **Bytecode gerenciado** | Java (`.class`), C#/.NET | **Bytecode** de alto nível — reverte quase ao fonte! | jadx, ILSpy, dnSpy |
| **Bytecode de script** | Python (`.pyc`), Lua | Bytecode da VM | decompyle3, uncompyle |
| **Interpretado puro** | JavaScript, PHP | O próprio fonte (às vezes *minificado*/ofuscado) | deobfuscators, prettier |
| **Web** | WebAssembly (`.wasm`) | Bytecode Wasm | wasm-decompile, Ghidra |

**Insight crucial:** bytecode gerenciado (Java/.NET) guarda **muito mais** metadados (nomes de
classe, métodos, tipos) que o nativo — por isso descompiladores de .NET/Java chegam perto do
fonte original. É por isso que ofuscadores *comerciais* existem para essas plataformas: sem
ofuscação, o código está quase às claras ([`23-mobile-e-managed.md`](23-mobile-e-managed.md)).

---

## 6. Por que a engenharia reversa é *possível* (o argumento fundamental)

O executável **precisa** conter tudo que o processador executa — senão não rodaria. Toda a
lógica, todas as constantes, todo o fluxo estão ali, por definição. Ocultar é sempre *adiar*:
o código pode estar comprimido, cifrado ou embaralhado, mas **em algum momento ele se
desembaralha para rodar** — e nesse instante é observável.

Isso é um **teorema prático**, não um chute: *qualquer* proteção do lado do cliente é, em
princípio, contornável por quem controla a máquina onde o código roda, porque a máquina
precisa executar o código em claro. A única proteção real move o segredo para onde o atacante
**não** tem controle: um servidor, ou hardware seguro (enclave/TPM/HSM). Guarde isso — volta
em [`18`](18-ofuscacao-e-packers.md), [`19`](19-anti-analise.md) e no projeto-modelo.

---

## 7. Modelo mental para o resto do curso

```
   FONTE (C)            perde nomes/comentários/tipos        BINÁRIO (bytes)
   legível     ───────────────────────────────────────▶     ilegível, executável
      ▲                                                            │
      │            ENGENHARIA REVERSA reconstrói                   │
      │        comportamento equivalente (não o original)         │
      └────────────────────────────────────────────────────────────┘
                estático (ler) + dinâmico (rodar) + descompilar
```

Tenha esse diagrama na cabeça. Cada ferramenta do curso é uma forma de subir a seta de baixo.

---

## Autoteste

1. Liste as quatro etapas de `gcc soma.c -o soma` e o que cada uma produz.
2. Em qual etapa exata os comentários desaparecem, e por quê?
3. Aplique os cinco porquês: por que o binário não guarda o nome `soma`? Onde a cadeia para?
4. O que significa dizer que a compilação é uma função "com perda"? Dê a analogia.
5. Cite três coisas que **sobrevivem** e três que **morrem** na compilação de C para nativo.
6. Por que descompilar um `.dll` .NET chega mais perto do fonte que descompilar um `.exe` em C?
7. Enuncie, com suas palavras, por que RE é sempre *possível* em código do lado do cliente, e
   qual a única defesa que escapa dessa regra.
