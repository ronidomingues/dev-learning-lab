# 60 · Teoria avançada — os limites e os motores da automação

**Nível:** pesquisa · **Data:** 03/09/2026

Até aqui, técnica. Agora a **teoria** que sustenta e limita tudo: por que certos problemas de
RE são *impossíveis* no caso geral, e quais ferramentas matemáticas (execução simbólica, SMT,
análise de fluxo de dados, IR) empurram a fronteira do que dá para automatizar.

---

## 1. O teto teórico: indecidibilidade

Muitos problemas centrais de RE são **indecidíveis** — não existe algoritmo que os resolva
para *todo* programa. Isso decorre do **problema da parada** (Turing, 1936): não há algoritmo
que decida, para qualquer programa e entrada, se ele termina.

Consequências diretas para o RE (via redução ao problema da parada e ao **Teorema de Rice** —
*qualquer* propriedade semântica não-trivial de programas é indecidível):

- **Separar código de dados** num binário arbitrário: indecidível. Por isso desmontadores
  erram, e anti-disassembly funciona ([`14`](14-analise-estatica.md), [`19`](19-anti-analise.md)).
- **Determinar o alvo de todo salto/chamada indireta** (`call rax`): indecidível no geral —
  o valor pode depender de qualquer computação anterior.
- **Provar equivalência de dois programas**, ou que um trecho é "código morto": indecidível.
- **Detecção perfeita de malware:** indecidível (Cohen, 1987) — não há detector que acerte
  sempre. Por isso antivírus usam heurísticas e assinaturas, nunca uma prova.

**O que isso NÃO significa:** que RE seja inútil ou impossível na prática. Significa que toda
ferramenta faz **aproximações** — conservadoras (podem errar para o lado seguro) e incompletas.
A arte da pesquisa é achar aproximações **úteis** para os casos que aparecem, não resolver o
caso geral (que é impossível).

---

## 2. Análise estática formal — os frameworks

Ferramentas de descompilação e verificação se apoiam em teoria de compiladores:

- **Grafo de fluxo de controle (CFG):** blocos básicos + arestas de salto. Base de tudo.
- **Dominadores / SSA (Static Single Assignment):** forma em que cada variável é atribuída uma
  única vez; simplifica análise de fluxo de dados. Descompiladores elevam o assembly a uma IR
  em SSA para raciocinar.
- **Análise de fluxo de dados:** *reaching definitions*, *liveness*, *constant propagation* —
  responde "de onde vem este valor?", "este registrador ainda será usado?". É como o
  descompilador elimina código morto e recupera variáveis.
- **Interpretação abstrata** (Cousot & Cousot, 1977): executar o programa sobre um domínio
  *abstrato* (ex.: intervalos, sinais) em vez de valores concretos, para provar propriedades
  para *todas* as entradas de uma vez. Fundamento de analisadores como Astrée e de recuperação
  de tipos/ranges. Trade-off central: **precisão × terminação** (mais preciso → pode não
  terminar; por isso se abstrai).

---

## 3. Execução simbólica — o motor da automação

Em vez de rodar com valores concretos, trate as entradas como **variáveis simbólicas** e
propague **fórmulas**. Cada caminho acumula uma **path condition** (as restrições que o levam
até ali). Para achar uma entrada que alcança um ponto, peça a um solucionador que resolva a
fórmula.

Exemplo intuitivo (o nível 3 do projeto-modelo): a entrada `serial` é simbólica; o motor
percorre o código de validação acumulando `len==14 ∧ soma==42 ∧ bloco1 % 7 == 0`; o
solucionador **produz um serial concreto** que satisfaz tudo. Nenhuma força bruta.

**A explosão de caminhos** é o calcanhar de Aquiles: o número de caminhos cresce
exponencialmente com ramos e laços. Mitigações: *concolic* (misturar concreto e simbólico),
poda de caminhos, *merging* de estados, e limitar profundidade/laços. Ferramentas: **angr**,
**KLEE**, **S2E**, **Triton**, **Manticore**.

```python
# Esqueleto conceitual em angr: achar entrada que imprime "Acesso concedido"
import angr
proj = angr.Project("./crackme", auto_load_libs=False)
simgr = proj.factory.simgr(proj.factory.full_init_state(args=["./crackme","2", angr.PointerWrapper(...)]))
simgr.explore(find=lambda s: b"concedido" in s.posix.dumps(1),
              avoid=lambda s: b"negado" in s.posix.dumps(1))
# simgr.found[0].posix.dumps(0)  -> a entrada que resolve
```

---

## 4. SMT/SAT — o solucionador por baixo

**SAT** (satisfatibilidade booleana) foi o primeiro problema provado **NP-completo**
(Cook, 1971). **SMT** (Satisfiability Modulo Theories) estende SAT com teorias: aritmética de
inteiros/bitvectors, arrays, ponto flutuante — exatamente o que se precisa para raciocinar
sobre programas. **Z3** (Microsoft Research) é o solucionador dominante.

- No RE, o SMT é o que **resolve** as path conditions da execução simbólica, **quebra** funções
  de checagem (encontra a entrada válida), e **prova** predicados opacos (mostra que um ramo é
  sempre morto) para desofuscar ([`18`](18-ofuscacao-e-packers.md)).
- SAT/SMT é NP-difícil no pior caso, mas solucionadores modernos (CDCL, heurísticas) resolvem
  instâncias enormes na prática. É o mesmo motor por trás de verificação formal e prova de
  teoremas.

---

## 5. Representações intermediárias (IR/IL) — a espinha da análise moderna

Analisar diretamente x86 (centenas de instruções, efeitos colaterais em flags) é penoso.
Ferramentas traduzem para uma **IR** simples e uniforme:

| IR | Ferramenta |
|---|---|
| **P-Code** | Ghidra |
| **VEX** | Valgrind, angr |
| **Microcode** | IDA/Hex-Rays |
| **BNIL** (LLIL/MLIL/HLIL) | Binary Ninja |
| **ESIL/RzIL** | radare2/rizin |
| **LLVM IR** | reotimização, *lifting* (McSema, RetDec) |

A IR: (1) normaliza arquiteturas diferentes numa linguagem só (escreva a análise uma vez, rode
em x86/ARM/MIPS); (2) torna explícitos os efeitos colaterais (flags viram variáveis); (3) é o
substrato para SSA, fluxo de dados e *structuring* que produzem o pseudo-C. Entender que o
descompilador raciocina sobre IR — e não sobre o assembly cru — explica seus acertos e seus
erros.

---

## 6. Recuperação de tipos e de estruturas — um problema de inferência

Reconstruir tipos a partir do binário é **inferência sob incerteza**: dado como um valor é
usado (tamanho de acesso, aritmética, argumentos de funções conhecidas), inferir seu tipo mais
provável. Abordagens: sistemas de restrições de tipo (TIE, Retypd usa teoria de reticulados/
subtipagem), e, cada vez mais, **aprendizado de máquina** treinado em pares binário↔fonte. É
uma fronteira ativa: nomes e tipos são justamente o que a compilação apaga, então recuperá-los
bem é o que separa um pseudo-C legível de um ilegível.

---

## 7. Verificação × RE — dois lados da mesma teoria

As mesmas ferramentas (SMT, interpretação abstrata, execução simbólica) sustentam a
**verificação formal** (provar que um programa está *correto*) e a **engenharia reversa**
(descobrir o que um programa *faz*). A diferença é o objetivo, não a matemática. Por isso
pesquisa em uma área alimenta a outra — e por que "reversos" avançados leem papers de
compiladores e de métodos formais.

---

## Autoteste

1. Enuncie o problema da parada e o Teorema de Rice, e derive por que "separar código de dados"
   é indecidível.
2. Se a detecção perfeita de malware é indecidível, como antivírus funcionam na prática?
3. O que é a **path condition** na execução simbólica, e como um serial válido "cai" dela?
4. Explique a **explosão de caminhos** e duas formas de mitigá-la.
5. Qual o papel do **Z3/SMT** no RE? Cite dois usos concretos.
6. Por que ferramentas modernas analisam uma **IR** em vez do assembly cru? Dê dois benefícios.
7. Em que sentido verificação formal e engenharia reversa são "a mesma matemática"?
