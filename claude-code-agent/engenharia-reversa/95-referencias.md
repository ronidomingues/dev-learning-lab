# 95 · Referências — specs, papers, docs e pessoas

**Nível:** todos · **Data:** 03/09/2026

Fontes primárias e verificáveis. Specs oficiais, papers seminais, documentação das ferramentas,
e pessoas/comunidades a acompanhar. Links podem mudar; nomes e identificadores, não.

---

## Especificações e manuais (a fonte da verdade)

- **Intel® 64 and IA-32 Architectures Software Developer's Manuals (SDM)** — Intel. O manual
  definitivo do x86-64 (instruções, codificação, semântica). Vol. 2 é a referência de
  instruções. intel.com/sdm.
- **AMD64 Architecture Programmer's Manual** — AMD. Complementar/alternativo ao Intel SDM.
- **Arm Architecture Reference Manual (ARM ARM)** — Arm Ltd. Referência de ARMv8/ARMv9 (AArch64).
  developer.arm.com.
- **System V Application Binary Interface (AMD64 ABI)** — a convenção de chamada do Linux/Unix
  x86-64 ([`16`](16-a-pilha-e-convencoes.md)). Mantida em gitlab.com/x86-psABIs.
- **Tool Interface Standard (TIS) ELF Specification** e **`man 5 elf`** — formato ELF
  ([`13`](13-formatos-de-binario.md)).
- **PE Format** — Microsoft Learn ("PE Format" / winnt.h). Referência do Portable Executable.
- **Mach-O / `LC_*` load commands** — Apple (docs de `Mach-O`), e o header `<mach-o/loader.h>`.
- **DWARF Debugging Standard** (dwarfstd.org) e **PDB** (formato de símbolos da Microsoft).
- **Itanium C++ ABI** (name mangling que o GCC/Clang usam) — itanium-cxx-abi.github.io.

---

## Papers e trabalhos seminais

**Fundamentos teóricos ([`60`](60-teoria-avancada.md)):**
- A. M. Turing, *On Computable Numbers…* (1936) — problema da parada.
- H. G. Rice (1953) — Teorema de Rice (propriedades semânticas são indecidíveis).
- S. A. Cook (1971) — SAT é NP-completo.
- P. Cousot & R. Cousot (1977) — Interpretação abstrata.
- F. Cohen (1987) — *Computer Viruses: Theory and Experiments* (indecidibilidade da detecção).
- J. C. King (1976) — *Symbolic Execution and Program Testing* (origem da execução simbólica).

**Ferramentas e técnicas modernas:**
- **angr**: Shoshitaishvili et al., *(State of) The Art of War: Offensive Techniques in Binary
  Analysis*, IEEE S&P 2016 — o paper do angr.
- **KLEE**: Cadar, Dunbar, Engler, OSDI 2008 — execução simbólica que gera testes.
- **Retypd**: Noonan et al., PLDI 2016 — recuperação de tipos por restrições.
- **ROP**: Shacham, *The Geometry of Innocent Flesh on the Bone: Return-into-libc without
  Function Calls*, CCS 2007 — a formalização do ROP.
- **AFL / fuzzing guiado por cobertura**: M. Zalewski, documentação do AFL (e AFL++, a
  continuação mantida).

**Descompilação neural / IA (2024–2026, [`65`](65-estado-da-arte.md)):**
- Tan et al., **LLM4Decompile**, arXiv:2403.05286 (2024); repositório `albertan017/LLM4Decompile`.
- Trabalhos subsequentes (2025–2026) sobre SK²Decompile, decompile-bench, WaDec (WebAssembly) e
  NeuroDeX (executáveis de redes neurais). *Verifique no arXiv pelos títulos, pois versões/links
  mudam.*

---

## Documentação oficial das ferramentas

- **Ghidra** — docs no próprio pacote (`docs/`), `GhidraDocs/`, e o repositório
  `NationalSecurityAgency/ghidra` (WhatsNew, Getting Started). API em `ghidra.re` e Javadoc.
- **radare2 / rizin** — "The radare2 book" (book.rada.re), `rizin.re/docs`.
- **GDB** — manual GNU (`sourceware.org/gdb`), e docs do **pwndbg**/**GEF**.
- **Frida** — frida.re/docs (JavaScript API, Interceptor, Stalker).
- **angr** — docs.angr.io (API e exemplos).
- **Capstone / Keystone / Unicorn** — capstone-engine.org, keystone-engine.org, unicorn-engine.org.
- **LIEF** — lief.re. **pwntools** — docs.pwntools.com. **YARA** — yara.readthedocs.io.
- **x64dbg** — help.x64dbg.com. **jadx** / **apktool** — wikis nos repositórios GitHub.

---

## Legislação e referências jurídicas (para [`80`](80-custos-e-licencas.md) e a ética)

- **Brasil — Lei 9.609/1998 (Lei do Software)** — Planalto (planalto.gov.br). **Omissa** sobre
  engenharia reversa; art. 6º trata de limitações (cópia de salvaguarda, etc.).
- **Brasil — Lei 9.610/1998 (Direitos Autorais)** e **Lei 12.737/2012** ("Lei Carolina
  Dieckmann", invasão de dispositivo informático) — Planalto.
- **EUA — DMCA §1201** (17 U.S.C. §1201) e as **isenções trienais** do U.S. Copyright Office
  (9º ciclo, regra efetiva em 28/10/2024) — copyright.gov/1201. Isenções permanentes para
  interoperabilidade (§1201(f)) e pesquisa de segurança.
- **EUA — CFAA** (Computer Fraud and Abuse Act, 18 U.S.C. §1030).
- **UE — Diretiva 2009/24/CE** (proteção jurídica de programas de computador) — EUR-Lex.
  Autoriza descompilação para **interoperabilidade** (art. 6).
- **Jurisprudência (EUA):** *Sega v. Accolade* (9th Cir., 1992); *Sony v. Connectix* (9th Cir.,
  2000) — RE para interoperabilidade como *fair use*.

> *Isto é referência, não aconselhamento jurídico.* Leis mudam e variam por jurisdição; consulte
> um advogado para casos concretos.

---

## Comunidades, plataformas e prática

- **crackmes.one** — repositório de crackmes por dificuldade. Campo de treino legítimo.
- **picoCTF** (picoctf.org), **pwn.college**, **CTFtime.org** (calendário de CTFs).
- **VirusTotal**, **MalwareBazaar** (bazaar.abuse.ch), **any.run**, **Hybrid Analysis** —
  triagem/sandbox de amostras.
- **MITRE ATT&CK** (attack.mitre.org) — taxonomia de táticas/técnicas para IOCs
  ([`20`](20-analise-de-malware.md)).
- **No More Ransom** (nomoreransom.org) — decryptors públicos (fruto de RE de ransomware).
- **Mente Binária** (mentebinaria.com.br) — comunidade brasileira de RE.

---

## Pessoas e blogs a acompanhar (referência, não endosso pessoal)

- **Ilfak Guilfanov** — criador da IDA (blog Hex-Rays).
- **pancake (Sergi Àlvarez)** — criador do radare2.
- **Ole André V. Ravnås** — criador do Frida.
- **NSA Research** — mantenedores do Ghidra.
- **Yan Shoshitaishvili / equipe angr / pwn.college** (ASU).
- **Amanda Rousseau (Malware Unicorn)** — workshops de RE.
- **Dennis Yurichev** — autor do RE4B (gratuito).
- Blogs/relatórios de **threat intel** (Mandiant, Kaspersky GReAT, ESET, Check Point) —
  writeups de RE de malware real, ótimos para ver o ofício aplicado.

---

## Autoteste

1. Qual é a **fonte da verdade** para a semântica de uma instrução x86, e onde a encontra?
2. Cite o paper e o ano que formalizou o **ROP**.
3. Que documento define a convenção de chamada do Linux x86-64?
4. Onde você confirma o que a lei dos EUA permite sobre **contornar proteção** para pesquisa?
5. Qual diretiva da UE autoriza descompilação para interoperabilidade, e qual jurisprudência
   americana firmou algo parecido?
6. Cite duas plataformas legítimas para **praticar** e duas para **triagem de amostras**.
7. Qual paper de 2024 abriu a onda de descompilação neural, e onde o encontra?
