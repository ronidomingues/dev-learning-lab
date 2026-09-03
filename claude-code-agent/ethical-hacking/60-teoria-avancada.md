# 60 · Teoria avançada — os limites do que se pode saber

`Nível: pesquisa` · `Última atualização: 12/08/2026`

Por que a segurança é um problema *sem solução final*, e não só um problema difícil? Este
arquivo desce ao nível teórico: indecidibilidade, os limites da análise de programas, a corrida
entre mitigações e contornos de memória, e a fronteira formal.

---

## 1. O teorema que garante emprego: indecidibilidade

**Problema da parada (Turing, 1936):** não existe algoritmo que, dado um programa qualquer e
uma entrada, decida sempre se ele vai parar ou rodar para sempre. Provado por diagonalização.

**Teorema de Rice (1953):** generaliza. **Qualquer propriedade semântica não trivial** de
programas é indecidível. "Este programa é seguro?" é uma propriedade semântica não trivial.
Logo:

> Não existe, e **não pode existir**, um programa que decida corretamente, para todo programa,
> se ele contém uma vulnerabilidade.

Isto não é limitação de tecnologia atual — é limite matemático. Consequências práticas:
- **Todo scanner** tem falso-positivo e falso-negativo, necessariamente. "Não encontrou" nunca
  prova "não existe".
- **Análise estática** completa e correta é impossível no caso geral; ferramentas fazem
  aproximações (sobre- ou subaproximação).
- É por isso que a segurança é **prática contínua**, não teorema a ser provado uma vez. E é por
  isso que o julgamento humano ([`13`](13-metodologias-e-frameworks.md)) não é substituível por
  ferramenta — no caso geral, é matematicamente insubstituível.

**A parada legítima aqui é uma lei matemática** (a indecidibilidade), no sentido da regra dos
cinco porquês. Não há "por quê" mais fundo: é assim porque a lógica é assim.

## 2. Análise de programas: as aproximações e seus limites

Como Rice impede a resposta exata, as ferramentas aproximam:

| Técnica | Como funciona | Limite |
|---|---|---|
| **Análise estática (SAST)** | analisa o código sem executar; *taint analysis* rastreia source→sink | falsos positivos (aproxima demais) e negativos (aproxima de menos) |
| **Análise dinâmica (DAST)** | executa e observa | só cobre os caminhos que executou |
| **Fuzzing** | gera entradas aleatórias/guiadas para provocar falha | acha o que dispara crash; não prova ausência |
| **Execução simbólica** | trata entradas como símbolos, resolve caminhos com SMT solver | explosão de caminhos (exponencial) |
| **Verificação formal** | prova matematicamente propriedades | caríssimo; só escala para código pequeno/crítico |

**Fuzzing** merece destaque: é a técnica mais produtiva da pesquisa de vulnerabilidade moderna.
**AFL++**, **libFuzzer**, e o **OSS-Fuzz** do Google acharam dezenas de milhares de bugs em
software real. *Coverage-guided fuzzing* usa cobertura de código como feedback para evoluir
entradas que exploram novos caminhos — uma busca guiada, não cega. Mas continua sendo teste:
acha bug, não prova segurança.

**Execução simbólica** (KLEE, angr) explora caminhos resolvendo as condições com um *SMT
solver*. Poderosa para achar a entrada exata que atinge um caminho, mas sofre da **explosão de
caminhos**: o número de caminhos cresce exponencialmente com ramificações. *Concolic* (mistura
concreto + simbólico) mitiga.

**Verificação formal** é o oposto: prova. O microkernel **seL4** foi formalmente verificado —
prova matemática de ausência de certas classes de bug. Custou ~20 anos-pessoa para ~10 mil
linhas. Mostra que é **possível** software provadamente correto, e por que **não escala** para
sistemas grandes (o trade-off econômico de [`01`](01-introducao-leigo.md) §6, agora com números).

## 3. A corrida da corrupção de memória (a fronteira ofensiva clássica)

[`16`](16-vulnerabilidades-e-exploracao.md) mostrou o overflow básico e as mitigações. No nível
de pesquisa, é uma escalada dialética — cada defesa gera um contorno:

```
Overflow simples          → mitigado por  → Stack canary
Injetar shellcode         → mitigado por  → NX/DEP (pilha não-executável)
  ↳ contornado por        → ROP (reusar código existente: gadgets + ret)
Endereços fixos           → mitigado por  → ASLR/PIE (randomização)
  ↳ contornado por        → info leak (vazar um endereço) → derrota ASLR
ROP genérico              → mitigado por  → CFI (Control-Flow Integrity)
  ↳ contornado por        → COOP, ataques a dados (data-only), JOP
Ponteiros corrompíveis    → mitigado por  → CET (shadow stack, hw), PAC (ARM), MTE
```

- **ROP (Return-Oriented Programming):** encadear pequenos trechos de código legítimo
  ("gadgets" terminados em `ret`) para computar o que quiser, sem injetar código novo — derrota
  o NX. `ROPgadget`, `ropper` procuram gadgets.
- **Info leak:** a chave contra ASLR. Vazar **um** endereço revela a base randomizada e
  reconstrói o mapa. Por isso bugs de leitura (como Heartbleed) são tão valiosos combinados com
  bugs de escrita.
- **Data-only attacks:** não sequestram o fluxo (driblam CFI); corrompem **dados** que decidem
  o fluxo (uma flag `is_admin`).
- **Mitigações de hardware (2020s):** **CET** (Intel, shadow stack), **PAC** e **MTE** (ARM,
  autenticação de ponteiro e *tagging* de memória) elevam o custo do atacante em ordens de
  grandeza. A resposta ofensiva migra para bugs de lógica, *type confusion*, e as fronteiras
  onde memory-safe encontra código C.

**Ponto de pesquisa (2026):** a combinação de mitigações de hardware + adoção de Rust torna a
exploração de memória "artesanal" cada vez mais cara, empurrando a pesquisa para *use-after-free*
em navegadores (JS engines), *type confusion*, e a fronteira FFI entre Rust e C. Ver [`65`](65-estado-da-arte.md).

## 4. Criptografia: quebrar sem força bruta

Ataque a cripto raramente é força bruta na chave (inviável para chaves modernas). É:
- **Erro de implementação:** IV reusado, nonce repetido (quebrou o WEP, e ChaCha mal usado),
  gerador aleatório fraco (previsível → chave previsível).
- **Padding oracle:** o servidor revela, por mensagens de erro/tempo, se o padding decifrou —
  permite decifrar sem a chave (POODLE, ataques a CBC).
- **Canais laterais (timing, potência):** o tempo de uma comparação ou o consumo de energia
  vazam bits da chave. Por isso comparações de segredo devem ser de **tempo constante**
  (`crypto.timingSafeEqual`, usado no projeto-modelo). Ver [`22`](22-mobile-e-hardware.md) §4.
- **Downgrade:** forçar o uso de um algoritmo fraco que ainda é suportado.

A lição: cripto forte é quase sempre quebrada pela **implementação e pelo protocolo ao redor**,
não pela matemática. "Não role sua própria cripto" é consequência disso.

## 5. Modelos formais de segurança

Para quem vai a fundo em teoria:
- **Bell-LaPadula** (confidencialidade): "no read up, no write down" — modelo militar.
- **Biba** (integridade): o dual — "no write up, no read down".
- **Modelo do atacante Dolev-Yao:** em análise de protocolos, o atacante controla a rede
  inteira (lê, altera, injeta), mas a cripto é ideal. Base para provar protocolos.
- **Non-interference / information flow:** definir formalmente que dado secreto não influencia
  saída pública. Base de análises de *taint* rigorosas.

Ferramentas de verificação de protocolo (**ProVerif**, **Tamarin**) provaram (e refutaram)
propriedades de TLS 1.3, Signal, e outros — pesquisa ativa e de alto impacto.

## 6. O limite teórico da defesa e do ataque

Juntando tudo:
- **A defesa não pode ser completa** (Rice): não há como provar que um sistema arbitrário é
  seguro. Sempre há incerteza residual.
- **O ataque não pode ser garantido** tampouco: contra sistemas formalmente verificados e
  memory-safe, classes inteiras de ataque desaparecem por construção.
- O jogo real acontece no **meio**: sistemas grandes demais para verificar, escritos por
  humanos sob pressão econômica, com legado que não morre. É um equilíbrio econômico e
  dialético, não um problema com solução final.

Esta é a razão teórica de a profissão existir e persistir: não é que "ainda não resolvemos" —
é que, no caso geral, **não há solução final a ser encontrada**. Há gestão contínua de risco.

## 7. Os cinco porquês: por que não podemos provar que um sistema é seguro?

**Por quê 1** — Por que não existe scanner perfeito de vulnerabilidade?
Porque decidir se um programa tem uma propriedade semântica (como "é seguro") é indecidível
(Rice).

**Por quê 2** — Por que Rice implica isso?
Porque "ser seguro" é uma propriedade não trivial do **comportamento** do programa, e toda
propriedade não trivial de comportamento é indecidível — reduz-se ao problema da parada.

**Por quê 3** — Por que o problema da parada é indecidível?
Prova por diagonalização (Turing, 1936): supor uma máquina que decide a parada leva a uma
contradição lógica ao alimentá-la consigo mesma.

**Por quê 4** — Por que não contornar com "casos práticos" em vez do caso geral?
Contornamos — é o que SAST, fuzzing e verificação fazem, por aproximação ou em domínios
restritos. Mas cada contorno herda um custo: falsos resultados, cobertura parcial, ou não-escala.

**Por quê 5** — Qual é a parada?
Uma **lei matemática** (indecidibilidade), no sentido mais forte da regra dos cinco porquês.
Não há "por quê" mais fundo — é uma verdade da lógica, tão dura quanto a impossibilidade de um
número ser par e ímpar. É o alicerce teórico de tudo neste curso: a segurança é gestão de risco
contínua porque a alternativa (prova de segurança universal) é comprovadamente impossível.

---

## Autoteste

1. Enuncie o teorema de Rice e explique o que ele implica sobre scanners de vulnerabilidade.
2. Por que "o scanner não encontrou nada" nunca prova "não há vulnerabilidade"?
3. Diferencie fuzzing de execução simbólica; qual o limite de cada um?
4. O que o seL4 demonstra sobre verificação formal — o que é possível e por que não escala?
5. Explique como o ROP contorna o NX/DEP.
6. Por que um *info leak* é tão valioso contra ASLR?
7. Por que a criptografia forte é quase sempre quebrada pela implementação, não pela matemática?
8. Por que não podemos provar que um sistema arbitrário é seguro? Leve o porquê até a lei
   matemática.
