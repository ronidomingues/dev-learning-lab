# Engenharia Reversa de Software — Mapa do Curso

> Do zero absoluto ao nível de pesquisa. Como um programa executável guarda
> segredos, e como um humano recupera a lógica que o compilador escondeu.

**Nível geral:** iniciante → pesquisa
**Idioma:** português do Brasil (termos técnicos em inglês na primeira ocorrência)
**Última atualização do mapa:** 03/09/2026

---

## O que você saberá ao final

- **Ler assembly x86-64 e ARM64** de cabeça: entender um binário sem o código-fonte.
- **Operar as ferramentas do ofício**: Ghidra, radare2/rizin, GDB, objdump, Frida, x64dbg,
  IDA Free, e a família Python (Capstone, angr, pwntools, LIEF).
- **Análise estática e dinâmica**: desmontar, descompilar, depurar, instrumentar em tempo de execução.
- **Entender o binário por dentro**: formato ELF/PE/Mach-O, ligação, relocação, ASLR, a pilha,
  a heap, as convenções de chamada, como uma `struct` de C vira offsets de memória.
- **Desfazer proteções**: packers, ofuscação, anti-debug, anti-VM — e por que quase nada é definitivo.
- **Aplicar a campos reais**: análise de malware, pesquisa de vulnerabilidades, interoperabilidade,
  auditoria de firmware, quebra de licenças (a parte legal e a ilegal, ditas com clareza).
- **A lei**: o que a Lei do Software brasileira (9.609/98), o DMCA §1201 e a diretiva europeia
  permitem e proíbem — e onde o Brasil é omisso.
- **A fronteira**: descompiladores neurais baseados em LLM, prova simbólica, o estado da arte de 2026.

---

## Roteiro de leitura

Leia na ordem numérica. O material é cumulativo: cada arquivo assume o anterior.
Se você já sabe programar em C e ler um pouco de assembly, pode saltar direto ao `10`
depois de instalar o ambiente (`03`).

```
Porta de entrada  →  01 02 03 04 05 06 07
Núcleo            →  10 11 12 13 14 15 16 17 18 19 20 21 22 23 60 65
Prática e erros   →  70 75
Economia          →  80 85
Fontes            →  90 95
Sempre à mão      →  GLOSSARIO.md
```

---

## Índice dos arquivos

### Bloco A · Porta de entrada (01–09)

| Arquivo | Conteúdo | Nível |
|---|---|---|
| [`01-introducao-leigo.md`](01-introducao-leigo.md) | O que é engenharia reversa, sem jargão. A analogia do bolo e do relógio. | iniciante |
| [`02-pre-requisitos.md`](02-pre-requisitos.md) | O que saber e ter antes. Tempo realista. Rota de resgate. | iniciante |
| [`03-instalacao.md`](03-instalacao.md) | **Manual de instalação** de todo o arsenal, por SO, com verificação e erros. | iniciante |
| [`04-como-comecar.md`](04-como-comecar.md) | Do binário à primeira função entendida, na tela, hoje. | iniciante |
| [`05-manual-de-uso.md`](05-manual-de-uso.md) | Referência consultável: GDB, radare2, objdump, Ghidra headless, Frida. | intermediário |
| [`06-exemplos.md`](06-exemplos.md) | 12 exemplos completos, do "hello world" reverso a dois casos de produção. | intermediário |
| [`07-projeto-modelo/`](07-projeto-modelo/) | Crackme completo + solucionador automático em Python. Roda de verdade. | intermediário |

### Bloco B · Núcleo (10–69)

| Arquivo | Conteúdo | Nível |
|---|---|---|
| [`10-fundamentos.md`](10-fundamentos.md) | Do código-fonte ao binário: compilar, montar, ligar. O que se perde. | iniciante |
| [`11-historia.md`](11-historia.md) | De Reversing de fita a Ghidra: 50 anos do campo. | iniciante |
| [`12-arquitetura-e-assembly.md`](12-arquitetura-e-assembly.md) | CPU, registradores, memória, x86-64 e ARM64 do zero. | intermediário |
| [`13-formatos-de-binario.md`](13-formatos-de-binario.md) | ELF, PE, Mach-O byte a byte. Seções, símbolos, relocação. | intermediário |
| [`14-analise-estatica.md`](14-analise-estatica.md) | Desmontagem, descompilação, grafos de fluxo, recuperação de tipos. | intermediário |
| [`15-analise-dinamica.md`](15-analise-dinamica.md) | Depuradores, breakpoints, tracing, instrumentação, emulação. | intermediário |
| [`16-a-pilha-e-convencoes.md`](16-a-pilha-e-convencoes.md) | Stack frames, calling conventions, como uma chamada de função funciona. | intermediário |
| [`17-estruturas-de-dados-no-binario.md`](17-estruturas-de-dados-no-binario.md) | Como struct, array, vtable, string e C++ aparecem em assembly. | avançado |
| [`18-ofuscacao-e-packers.md`](18-ofuscacao-e-packers.md) | Como programas se escondem, e como se desfaz cada técnica. | avançado |
| [`19-anti-analise.md`](19-anti-analise.md) | Anti-debug, anti-VM, anti-disassembly. A corrida armamentista. | avançado |
| [`20-analise-de-malware.md`](20-analise-de-malware.md) | Triagem, sandbox, IOCs, unpacking, YARA, laboratório seguro. | avançado |
| [`21-vulnerabilidades.md`](21-vulnerabilidades.md) | Achar bugs em binários: overflow, use-after-free, fuzzing, ROP. | avançado |
| [`22-firmware-e-embarcados.md`](22-firmware-e-embarcados.md) | Extrair e reverter firmware, ARM/MIPS, JTAG, binwalk. | avançado |
| [`23-mobile-e-managed.md`](23-mobile-e-managed.md) | Android (APK/DEX), iOS, .NET e Java — bytecode gerenciado. | avançado |
| [`60-teoria-avancada.md`](60-teoria-avancada.md) | Execução simbólica, SMT, análise de fluxo de dados, decidibilidade. | pesquisa |
| [`65-estado-da-arte.md`](65-estado-da-arte.md) | Descompilação neural (LLM), 2026. Fronteiras abertas. | pesquisa |

### Bloco C · Prática e erros (70–79)

| Arquivo | Conteúdo | Nível |
|---|---|---|
| [`70-pratica.md`](70-pratica.md) | 12 laboratórios progressivos, do crackme ao unpacking real. | todos |
| [`75-armadilhas.md`](75-armadilhas.md) | Erros clássicos, mitos e más práticas — e por que persistem. | todos |

### Bloco D · Economia e ecossistema (80–89)

| Arquivo | Conteúdo | Nível |
|---|---|---|
| [`80-custos-e-licencas.md`](80-custos-e-licencas.md) | Preços das ferramentas (03/09/2026), licenças, custo oculto. | todos |
| [`85-cursos-e-certificacoes.md`](85-cursos-e-certificacoes.md) | Cursos gratuitos PT/EN/FR e certificações (GREM, OSED…). | todos |

### Bloco E · Fontes (90–99)

| Arquivo | Conteúdo | Nível |
|---|---|---|
| [`90-bibliografia.md`](90-bibliografia.md) | Livros comentados, com o que é legalmente gratuito. | todos |
| [`95-referencias.md`](95-referencias.md) | Specs, papers seminais, docs oficiais, pessoas do campo. | todos |
| [`GLOSSARIO.md`](GLOSSARIO.md) | Todos os termos técnicos definidos. | todos |

---

## Status de produção

| Bloco | Status | Observação |
|---|---|---|
| **A · Porta de entrada** | ✅ completo | 01–07, com projeto-modelo executável |
| **B · Núcleo** | ✅ completo | 10–23, 60, 65 |
| **C · Prática e erros** | ✅ completo | 70, 75 |
| **D · Economia** | ✅ completo | 80, 85 — pesquisados na web em 03/09/2026 |
| **E · Fontes** | ✅ completo | 90, 95, glossário |

**Ambiente de referência do curso:** Ubuntu 22.04.5 LTS, x86-64, GCC 11.4, GDB 12.1,
Python 3.10, binutils 2.38. Ferramentas de terceiros nas versões de agosto/2026
(Ghidra 12.1.3, radare2 6.2.0, Frida 17.17.0) — ver [`03-instalacao.md`](03-instalacao.md).

---

## Um aviso antes de começar

Engenharia reversa é uma faca. Serve para descobrir uma vulnerabilidade e corrigi-la,
para entender um malware que já está te atacando, para fazer seu programa conversar com
o de outro fabricante — e serve também para pirataria e crime. **Este curso ensina a técnica
e é explícito sobre onde a linha legal passa** (ver [`12-arquitetura-e-assembly.md`](12-arquitetura-e-assembly.md)
para a técnica e o arquivo de custos/ética adiante). A responsabilidade pelo uso é sua.
Estude em binários que você tem direito de analisar: os seus, os deste curso, crackmes
públicos feitos para isso, e programas sob autorização explícita.
