# 65 · Estado da arte — a fronteira em setembro de 2026

**Nível:** pesquisa · **Data:** 03/09/2026 · *pesquisado na web em 03/09/2026*

Onde o campo está *agora*. O tema dominante da década é claro: **IA aplicada à engenharia
reversa** — descompilação neural, nomeação de variáveis por modelo, e assistentes que explicam
binários. Ao mesmo tempo, a base clássica (Ghidra, execução simbólica, fuzzing) continua
evoluindo. Como todo arquivo que envelhece, leia com a data em mente.

---

## 1. Descompilação neural com LLMs — o salto de 2024–2026

O trabalho que abriu a onda foi **LLM4Decompile** (Tan et al., arXiv 2403.05286, 2024): o
primeiro LLM open-source dedicado a descompilar. Traduz binários **x86-64 Linux** de volta para
**C legível**, cobrindo os níveis de otimização **O0 a O3** do GCC. A ideia: tratar
"binário → fonte" como um problema de *tradução* (como línguas naturais), treinando em milhões
de pares função-binário ↔ função-fonte.

Evolução até 2026 (fontes na web em 03/09/2026):
- **decompile-bench** (2025): dataset de ~2 milhões de pares binário↔fonte para treino e ~70 mil
  para avaliação — infraestrutura que faltava para comparar métodos com rigor.
- **SK²Decompile** (out/2025): abordagem em duas fases — primeiro recuperar a *estrutura*
  (esqueleto), depois *nomear* identificadores de forma legível (a "pele"). Separar forma de
  nomes melhora a qualidade.
- **Generalização para além do x86:** métodos LLM sendo aplicados a **WebAssembly** (WaDec, com
  >50% de recompilabilidade em casos reais) e a **bytecode de contratos inteligentes**
  (recuperar Solidity de bytecode EVM com LLMs adaptados via LoRA).
- **Mudança na forma de avaliar:** a comunidade migra de métricas textuais (parecença com o
  fonte) para métricas de **recompilabilidade e equivalência de execução** — "o C gerado
  compila e roda igual?" é o que importa, não se as palavras batem.

**Onde ainda falha (honesto):** LLMs alucinam — geram C plausível mas **semanticamente errado**,
especialmente em código otimizado, grande, ou fora da distribuição de treino. Não substituem o
descompilador determinístico; **complementam-no**. O uso maduro é híbrido: Ghidra/IDA para a
estrutura confiável + LLM para nomes, comentários e hipóteses de intenção, sempre **verificados**.

---

## 2. IA como assistente do reverser (o que já está em produção)

- **Nomeação de variáveis/funções por ML:** modelos que sugerem nomes significativos para
  `FUN_00101149`/`local_18` a partir do contexto. Linhagem: DIRTY, VarBERT, e sucessores
  integrados a plugins.
- **Plugins de LLM para Ghidra/IDA/Binary Ninja:** extensões que mandam a função descompilada a
  um modelo e recebem explicação em linguagem natural, sugestões de renome, ou identificação de
  algoritmo (ex.: "isto é AES", "isto é um parser de protocolo X"). Aceleram triagem.
- **RAG sobre binários:** indexar funções por *embeddings* para busca semântica ("ache funções
  parecidas com esta rotina de cripto") em coleções grandes de malware.

**Cautela profissional (opinião marcada):** essas ferramentas são multiplicadores de
produtividade fantásticos para *triagem* e *documentação*, mas perigosas como *fonte de verdade*
— a alucinação convincente é o risco. Trate a saída de LLM como a de um estagiário brilhante e
apressado: ótimas pistas, sempre conferidas contra o assembly.

---

## 3. Binary Code Similarity — casar funções por semântica, não por bytes

Um problema central (achar código conhecido/vulnerável dentro de binários stripped) migrou de
heurísticas (assinaturas FLIRT) para **embeddings neurais** que capturam a *semântica* da
função, robustos a mudança de compilador, otimização e arquitetura. Usos: encontrar bibliotecas
vulneráveis embutidas em firmware, atribuição de malware, e *patch presence* (a correção do
CVE-X está neste binário?). Linhagem: Gemini, SAFE, jTrans, e trabalhos de 2025–2026 sobre
similaridade *cross-architecture*.

---

## 4. A base clássica continua avançando

- **Ghidra 12.x (2026):** melhorias reais em recuperação de **bitfields**, análise moderna de
  **Objective-C** (`_objc_msgSend` resolvido para o método real), suporte a **debuginfod**
  (baixar símbolos DWARF), novos processadores (Hexagon), e **PyGhidra** (Python 3) no lugar do
  Jython. Confirmado nas notas de release da 12.1 (18/08/2026).
- **Execução simbólica + fuzzing (concolic)** cada vez mais integrados; fuzzers guiados por
  cobertura com feedback de sanitizers são o padrão de descoberta de bugs.
- **Emulação de firmware** (FirmAE e sucessores) tornando testes dinâmicos de IoT escaláveis.

---

## 5. A corrida da ofuscação × desofuscação

- **Do lado da defesa:** virtualização de código (VMProtect/Themida/Denuvo) e ofuscação
  assistida por ML; tentativas de ofuscação especificamente para **confundir LLMs** de análise.
- **Do lado do ataque:** desofuscadores baseados em execução simbólica e, agora, em ML;
  *lifting* de bytecode de VM para IR analisável. O equilíbrio não muda: é econômico, não
  absoluto ([`18`](18-ofuscacao-e-packers.md)).

---

## 6. Fronteiras abertas (problemas não resolvidos)

- **Descompilação neural confiável:** eliminar alucinação semântica; garantias de correção
  (descompilação *verificada*).
- **Recuperação de tipos/estruturas de alto nível** (C++ templates, Rust, Go, closures) —
  ainda fraca; linguagens modernas com *runtimes* ricos são um osso duro.
- **RE de modelos de IA compilados:** reverter *executáveis de redes neurais* (pesos e grafos
  embutidos) — trabalhos como NeuroDeX (2025) começam a atacar isso; é um alvo totalmente novo.
- **Escala:** analisar milhões de binários (app stores, firmware) automaticamente e com
  precisão. Similaridade + LLM apontam o caminho, mas custo e falsos positivos limitam.
- **Contra-IA:** ofuscação desenhada para derrotar modelos de análise, e a resposta defensiva.

---

## 7. Implicações e a foto de 2026

O RE em 2026 é **híbrido**: ferramentas determinísticas maduras (Ghidra/IDA/angr) + camada de
IA para acelerar leitura, nomear e sugerir. A barreira de entrada caiu (Ghidra grátis + LLMs
explicando assembly), mas os **limites teóricos** do [`60`](60-teoria-avancada.md) não mudaram —
IA aproxima melhor, não torna o indecidível decidível, nem a alucinação, verdade. O profissional
que se destaca é o que **combina** o rigor clássico com as novas alavancas, sabendo onde cada
uma mente.

---

## Autoteste

1. O que o LLM4Decompile propôs, e por que enquadrar descompilação como "tradução" faz sentido?
2. Qual a principal falha dos descompiladores neurais, e por que o uso maduro é *híbrido*?
3. Por que a avaliação migrou de "parecença textual" para "recompilabilidade/equivalência"?
4. O que é *binary code similarity* por embeddings, e cite dois usos defensivos reais.
5. Cite duas melhorias concretas do Ghidra 12.x (2026) e por que importam.
6. Liste três fronteiras abertas do campo em 2026.
7. Verdadeiro/falso: "IA torna decidíveis os problemas indecidíveis do RE." Justifique.

---

*Fontes consultadas em 03/09/2026:* arXiv 2403.05286 (LLM4Decompile) e repositório
`albertan017/LLM4Decompile`; sínteses sobre SK²Decompile, decompile-bench, WaDec e NeuroDeX
(2025–2026); notas de release do Ghidra 12.1 (NSA, 18/08/2026, WhatsNew: bitfields, Objective-C,
debuginfod, PyGhidra, Hexagon); levantamentos sobre *binary code similarity* neural (2025–2026).
