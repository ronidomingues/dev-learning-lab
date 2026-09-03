# 14 · Análise estática — ler sem executar

**Nível:** intermediário · **Data:** 03/09/2026

Análise **estática** é examinar o binário parado. É a base do RE: segura (não roda código
hostil), completa (vê todos os caminhos) e a única opção quando você não pode/deve executar o
alvo. Este arquivo cobre desmontagem, descompilação, grafos de fluxo e recuperação de tipos —
com as armadilhas de cada uma.

---

## 1. O fluxo de trabalho estático

```
 identificar → desmontar → descompilar → anotar → entender
   (file,        (linear/      (pseudo-C)   (renomear,   (o que a
   strings,      recursivo)                  tipar)       função faz?)
   checksec)
```
Anotar é o segredo: renomeie funções e variáveis conforme entende (`FUN_00101149` →
`valida_senha`), defina tipos, escreva comentários. Um binário bem anotado no Ghidra é como um
código-fonte que você reconstruiu — e é reutilizável.

---

## 2. Desmontagem: linear × recursiva (e por que ela às vezes erra)

Transformar bytes em instruções parece trivial, mas **não é** em x86, porque as instruções têm
tamanho variável (1 a 15 bytes) e código se mistura com dados. Há duas estratégias:

- **Varredura linear** (objdump): decodifica do início ao fim, sequencialmente. Simples, mas
  **tropeça** se houver dados no meio do código ou instruções desalinhadas — a partir dali,
  desmonta lixo.
- **Recursiva/por fluxo** (IDA, Ghidra, r2): segue os saltos e chamadas, decodificando só o que
  é alcançável como código. Bem mais precisa; é o que descompiladores usam.

**Consequência prática:** um objdump "sujo" no meio de uma função pode ser artefato da
varredura linear, não código real. Confie mais no Ghidra/IDA. E atacantes exploram isso de
propósito (**anti-disassembly**, [`19`](19-anti-analise.md)): inserem um byte que desalinha a
varredura linear e esconde o código real.

> Este é um caso concreto de um limite **teórico**: separar código de dados num binário
> arbitrário é, no geral, **indecidível** (redutível ao problema da parada). Por isso nenhum
> desmontador é perfeito. Ver [`60-teoria-avancada.md`](60-teoria-avancada.md).

---

## 3. Descompilação: assembly → pseudo-C

O descompilador (Ghidra, Hex-Rays) eleva o assembly a algo parecido com C: reconstrói
variáveis, laços, condicionais, chamadas. Multiplica sua produtividade por 5–10×.

**Como funciona por dentro (visão de alto nível):**
1. Desmonta e constrói o **grafo de fluxo de controle** (CFG).
2. Traduz para uma **representação intermediária** (IR: P-Code no Ghidra, microcode no IDA) —
   independente da arquitetura.
3. Faz **análise de fluxo de dados**: onde cada valor nasce e é usado, propagação, eliminação
   de código morto.
4. **Recupera estruturas de alto nível**: transforma saltos em `if`/`while`/`for` (algoritmos
   de "structuring"), infere tipos e assinaturas.
5. Emite pseudo-C.

**O que ele NÃO recupera:** nomes originais, comentários, e frequentemente os tipos exatos. Ele
*inventa* nomes (`local_18`, `uVar3`) e chuta tipos (`undefined8`). Você refina isso à mão.

---

## 4. As mentiras do descompilador (leia antes de confiar)

O pseudo-C é uma **interpretação**, não a verdade. Erros comuns:

- **Tipos errados:** trata um ponteiro como inteiro, um `int` como `char`, perde `unsigned`.
  Um cálculo "estranho" muitas vezes é tipo mal inferido — corrija o tipo e o código clareia.
- **Variáveis fundidas ou duplicadas:** o otimizador reusa registradores; o descompilador pode
  ver uma variável onde havia duas, ou vice-versa.
- **Aritmética de ponteiros disfarçada:** `*(int *)(base + i*4)` aparece cru quando ele não
  reconheceu o array. Definir a `struct`/array certa transforma isso em `arr[i]`.
- **Convenções e otimizações agressivas** (`-O2`/`-O3`): funções *inline*, laços desenrolados,
  `switch` viram tabelas de salto — o pseudo-C fica denso e menos fiel.
- **Divisão por constante** vira `imul` por número mágico + shift (você viu no projeto-modelo:
  `imul 0x92492493` = `% 7`). Bons descompiladores já mostram `% 7`; outros não.

**Regra de ouro:** quando o pseudo-C não fizer sentido, **desça para o assembly**. O assembly
não mente — é o que a CPU executa.

---

## 5. Grafo de fluxo de controle (CFG)

O **CFG** representa a função como blocos básicos (sequências sem desvio) ligados por arestas
(saltos). É a forma mais rápida de *ver a forma* de uma função:

```
        ┌──────────┐
        │  entrada │
        └────┬─────┘
        cmp/ jne
        ┌────┴─────┐
        ▼          ▼
   ┌────────┐  ┌────────┐
   │ ramo A │  │ ramo B │
   └───┬────┘  └───┬────┘
       └─────┬─────┘
             ▼
        ┌────────┐
        │ saída  │
        └────────┘
```
- No **Ghidra**: janela *Function Graph*. No **radare2**: `VV`. No **IDA**: a visão gráfica padrão.
- Um losango (dois ramos) = um `if`. Uma aresta de volta ao topo = um laço. Muitos ramos
  paralelos = um `switch`. Você *lê a estrutura* antes de ler o código.

---

## 6. Recuperação de tipos e estruturas

Metade do trabalho estático é reconstruir **os dados**. Pistas:
- **Tamanho de acesso:** `mov al,` (1 byte = char/bool), `mov eax,` (4 = int/float), `mov rax,`
  (8 = long/ponteiro).
- **Escala em `[base + i*N]`:** N revela `sizeof` do elemento (1/4/8).
- **Offsets constantes a partir de um ponteiro** (`[rdi+0]`, `[rdi+8]`, `[rdi+16]`) = campos de
  uma `struct`. Você define a struct no Ghidra e ele reescreve tudo como `p->campo`.
- **Chamada a `*(reg+offset)`** (chamada indireta via ponteiro dentro de um objeto) = **vtable**
  de C++ → herança/polimorfismo ([`17`](17-estruturas-de-dados-no-binario.md)).

Definir os tipos certos é o que transforma um pseudo-C ilegível em algo que você entende. É
trabalho manual, iterativo, e é *a* habilidade que separa iniciante de avançado.

---

## 7. Ferramentas estáticas e quando usar cada uma

| Objetivo | Ferramenta |
|---|---|
| Triagem rápida | `file`, `strings`, `nm -D`, `checksec`, `capa` |
| Desmontar um trecho | `objdump -d -M intel` |
| Descompilar / anotar / projeto grande | **Ghidra** (ou IDA) |
| Scriptar / grafo no terminal | **radare2/rizin** + Cutter |
| Comparar descompiladores | **dogbolt.org** |
| Identificar bibliotecas estáticas embutidas | **FLIRT** (IDA) / assinaturas de função |

---

## 8. Diffing de binários (bindiff) — um superpoder subestimado

Comparar **duas versões** de um binário revela exatamente o que mudou — usadíssimo para
descobrir **qual bug um patch corrigiu** (*patch diffing*, base de muitos 1-days). Ferramentas:
**BinDiff** (grátis, do Google/Zynamics), **Diaphora** (para IDA/Ghidra), `radiff2` (radare2).
Você alinha funções entre as versões e olha só as que mudaram.

---

## Autoteste

1. Por que a desmontagem linear pode "desmontar lixo", e como a recursiva evita isso?
2. Qual limite **teórico** explica por que nenhum desmontador é perfeito?
3. Liste três coisas que o descompilador **inventa** ou **erra**, e como você as corrige.
4. Quando o pseudo-C não faz sentido, qual a regra de ouro?
5. Olhando um CFG, como você reconhece um `if`, um laço e um `switch`?
6. Você vê acessos `[rdi+0]`, `[rdi+8]`, `[rdi+16]`. O que isso sugere e o que você faz no Ghidra?
7. O que é *patch diffing* e por que atacantes o usam?
