# 13 · Formatos de binário — ELF, PE e Mach-O

**Nível:** intermediário · **Data:** 03/09/2026

Um executável não é só código: é um **contêiner** com cabeçalhos, seções, tabelas de símbolos
e instruções para o sistema operacional carregá-lo. Entender esse contêiner é meio caminho do
RE — é onde estão as strings, os imports (o que o programa chama de fora), o ponto de entrada e
as proteções.

Três formatos dominam:

| Formato | SO | Extensões típicas |
|---|---|---|
| **ELF** (Executable and Linkable Format) | Linux, BSD, Android (nativo), embarcados | (nenhuma), `.so`, `.o` |
| **PE** (Portable Executable) | Windows | `.exe`, `.dll`, `.sys` |
| **Mach-O** | macOS, iOS | (nenhuma), `.dylib` |

Todos compartilham a mesma **anatomia lógica**; muda o layout dos bytes.

---

## 1. Anatomia comum a todos

```
┌───────────────────────────┐
│  Cabeçalho (magic, arch,  │  "que tipo de arquivo, para qual CPU, onde começa a rodar"
│  ponto de entrada, ...)   │
├───────────────────────────┤
│  Tabela de seções/segmen. │  "onde está cada pedaço e como carregá-lo na memória"
├───────────────────────────┤
│  .text   (código)         │  as instruções executáveis
│  .rodata (const/strings)  │  strings literais, constantes  ← seu primeiro alvo
│  .data   (globais mutáveis)│  variáveis globais inicializadas
│  .bss    (globais zerados)│  ocupa 0 bytes no arquivo, alocado em memória
├───────────────────────────┤
│  Tabelas de símbolos e    │  nomes (se not stripped), imports/exports
│  relocação                │
└───────────────────────────┘
```

**Números mágicos** (os primeiros bytes — como você identifica o formato):
```bash
xxd BIN | head -1
```
| Formato | Bytes iniciais | ASCII |
|---|---|---|
| ELF | `7f 45 4c 46` | `.ELF` |
| PE | `4d 5a` … depois `50 45 00 00` | `MZ` … `PE\0\0` |
| Mach-O (64) | `cf fa ed fe` (ou `fe ed fa cf`) | — |
| Java class | `ca fe ba be` | — |

---

## 2. ELF em detalhe (o formato do curso)

### Cabeçalho
```bash
readelf -h ./crackme
```
Campos que importam:
- **Class:** ELF64 (64 bits) ou ELF32.
- **Type:** `EXEC` (executável de endereço fixo), `DYN` (**PIE** — executável reposicionável,
  o padrão moderno), `REL` (`.o`), `CORE` (dump).
- **Machine:** `x86-64`, `AArch64`, `RISC-V`, `MIPS`…
- **Entry point:** endereço da primeira instrução executada (não é o `main`; é o `_start` da
  libc, que depois chama `main`).

### Seções (visão do *linker*) × Segmentos (visão do *loader*)
- **Seções** (`.text`, `.rodata`, …) organizam o arquivo para o linker/ferramentas.
- **Segmentos** (Program Headers) dizem ao **loader** o que mapear na memória e com quais
  permissões (R/W/X).
```bash
readelf -S BIN     # seções
readelf -l BIN     # segmentos (program headers) e permissões
```
Seção crucial de RE: **`.text`** (código), **`.rodata`** (strings/constantes), **`.plt`/`.got`**
(mecanismo de chamada a funções de bibliotecas dinâmicas).

### PLT e GOT — como o programa chama `printf` sem saber seu endereço
Bibliotecas dinâmicas (`.so`) carregam em endereços que só se conhecem em tempo de execução.
Para chamar `printf`, o programa usa duas tabelas:
- **GOT** (Global Offset Table): tabela de endereços reais, preenchida em runtime.
- **PLT** (Procedure Linkage Table): trampolins que, na 1ª chamada, resolvem o endereço (*lazy
  binding*) e o gravam na GOT; nas próximas, pulam direto.

No assembly você verá `call printf@plt`. **Por que isso importa no RE:** ao ver `call
0x1050 <printf@plt>`, você sabe que ali é uma chamada externa — e a GOT é um alvo clássico de
ataque (sobrescrever uma entrada da GOT redireciona uma função). Ver [`21-vulnerabilidades.md`](21-vulnerabilidades.md).

### Símbolos e informação de debug
```bash
nm BIN            # símbolos (nomes) — vazio se stripped
nm -D BIN         # símbolos dinâmicos (imports/exports) — sobrevivem ao strip!
readelf -x .rodata BIN   # dump hex de uma seção
```
Mesmo *stripped*, os **símbolos dinâmicos** (funções importadas como `strcmp`, `malloc`,
`socket`) permanecem — porque o loader precisa deles. Eles são uma pista enorme sobre o que o
binário faz.

---

## 3. PE (Windows) — o essencial

Estrutura: cabeçalho **DOS** (`MZ`, com o famoso stub "This program cannot be run in DOS mode")
→ cabeçalho **PE** (`PE\0\0`) → **Optional Header** (ponto de entrada, base de carga,
subsistema) → **tabela de seções** (`.text`, `.rdata`, `.data`, `.rsrc`).

Conceitos de RE específicos de PE:
- **Import Address Table (IAT):** equivalente da GOT — lista as funções importadas de DLLs
  (`kernel32.dll!CreateFileW`, `ws2_32.dll!connect`). **Ler a IAT é triagem instantânea de
  malware**: se importa `CreateRemoteThread`, `VirtualAllocEx`, `WriteProcessMemory`, cheira a
  injeção de código.
- **Seção `.rsrc`:** recursos (ícones, diálogos, e às vezes *payloads* embutidos).
- **Assinaturas Authenticode:** binários assinados; malware às vezes rouba/forja certificados.

Ferramentas: **PE-bear**, **CFF Explorer**, `pefile` (Python), e Ghidra/IDA leem PE nativamente.

---

## 4. Mach-O (macOS/iOS) — o essencial

- **Fat/Universal binaries:** um único arquivo pode conter *várias* arquiteturas (x86-64 **e**
  ARM64). `lipo -info BIN` lista; `lipo -thin` extrai uma.
- **Load commands** em vez de "program headers": dizem quais dylibs carregar, onde está o
  entrypoint (`LC_MAIN`), assinatura de código (`LC_CODE_SIGNATURE`).
- **Objective-C / Swift metadata:** binários Apple carregam metadados ricos de classes/métodos
  ObjC — o Ghidra 12.x melhorou muito a recuperação de `_objc_msgSend` (ver notas de release).
  Isso torna o RE de apps iOS mais produtivo do que parece.
- Ferramentas: `otool`, `nm`, **Hopper** (comercial, popular no Mac), Ghidra/IDA.

---

## 5. Tabela comparativa

| Conceito | ELF (Linux) | PE (Windows) | Mach-O (Apple) |
|---|---|---|---|
| Magic | `7f ELF` | `MZ`/`PE\0\0` | `cf fa ed fe` |
| Tabela de imports | GOT/PLT + `.dynsym` | IAT | stubs + `LC_LOAD_DYLIB` |
| "Seções" | Sections/Segments | Sections | Segments/Sections + Load Commands |
| Multi-arquitetura | não (um por arquivo) | não | **sim** (fat binary) |
| Metadados ricos | DWARF (se `-g`) | PDB (separado) | ObjC/Swift metadata |
| Reposicionável moderno | PIE (`DYN`) | ASLR + `/DYNAMICBASE` | PIE (padrão) |

---

## 6. Por que o loader importa para o RE

Quando você depura, os endereços "de arquivo" não são os "de memória": o loader mapeia
segmentos, aplica **relocações** e, com **ASLR**, sorteia a base de carga a cada execução.
Por isso:
- No GDB, use `vmmap` (pwndbg) para ver onde cada segmento caiu **nesta** execução.
- Ghidra mostra endereços com uma "imagebase"; ao depurar, some/subtraia o *slide* de ASLR.
- Para estudo estável, desabilite ASLR (`set disable-randomization on` no GDB, ou
  `echo 0 > /proc/sys/kernel/randomize_va_space` — só no laboratório).

ASLR, NX, PIE, RELRO e canário são **proteções** que você lê com `checksec` e que definem o
quão difícil é explorar um bug — assunto de [`21-vulnerabilidades.md`](21-vulnerabilidades.md).

---

## Autoteste

1. Qual comando e quais bytes você olha para saber se um arquivo é ELF, PE ou Mach-O?
2. Diferencie **seções** de **segmentos** num ELF: quem usa cada um?
3. Explique o papel da dupla **PLT/GOT**. Por que a GOT é alvo de ataque?
4. Mesmo num binário *stripped*, que símbolos sobrevivem e por quê são úteis?
5. Ao triar um `.exe` suspeito, por que ler a **IAT** é tão informativo? Dê 3 imports que
   levantam suspeita.
6. O que é um *fat binary* Mach-O e como você extrai uma arquitetura dele?
7. Por que os endereços que você vê no Ghidra podem não bater com os do GDB em execução?
