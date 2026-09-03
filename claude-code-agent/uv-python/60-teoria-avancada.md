# 60 · Teoria avançada — complexidade, PubGrub formal e resolução universal

> **Nível:** pesquisa · **Atualizado em:** 31/08/2026
> Pré-requisitos: lógica proposicional, noção de NP-completude, e o
> [13-resolucao-de-dependencias.md](13-resolucao-de-dependencias.md).

---

## 1. Formalização do problema

Seja:

- **P** o conjunto de nomes de pacotes;
- para cada `p ∈ P`, **V(p)** o conjunto (finito, totalmente ordenado pela PEP 440) das
  versões de `p`;
- para cada par `(p, v)` com `v ∈ V(p)`, o conjunto de dependências
  **D(p, v) ⊆ { (q, S) : q ∈ P, S ⊆ V(q) }`**, onde `S` é o conjunto de versões
  aceitáveis de `q` (expresso por um especificador da PEP 440);
- **R ⊆ { (p, S) }** o conjunto de requisitos de topo.

Uma **solução** é uma função parcial `σ : P ⇀ V(p)` tal que:

1. para todo `(p, S) ∈ R`: `σ(p)` está definida e `σ(p) ∈ S`;
2. para todo `p` no domínio de `σ` e todo `(q, S) ∈ D(p, σ(p))`: `σ(q)` está definida e
   `σ(q) ∈ S`;
3. o domínio de `σ` é minimal (não há pacotes supérfluos).

**Problema de decisão (VERSION-SOLVING):** existe tal `σ`?

**Problema de otimização:** entre todas as `σ` válidas, encontrar a que maximiza
lexicograficamente as versões, segundo uma ordem de prioridade dos pacotes.

---

## 2. Complexidade

### 2.1 VERSION-SOLVING é NP-completo

**Está em NP:** dada uma `σ` candidata (polinomial no tamanho da entrada — no máximo uma
versão por pacote), verificar as condições 1–3 é polinomial: basta percorrer as
dependências de cada par escolhido.

**É NP-difícil:** redução a partir de 3-SAT. Dada uma fórmula `φ` com variáveis
`x₁..xₙ` e cláusulas `c₁..cₘ`:

- para cada variável `xᵢ`, crie o pacote `Xᵢ` com **duas** versões: `1.0` (representando
  `xᵢ = falso`) e `2.0` (`xᵢ = verdadeiro`). A restrição "exatamente uma versão por
  pacote" dá gratuitamente a atribuição booleana total;
- para cada cláusula `cⱼ = (l₁ ∨ l₂ ∨ l₃)`, crie o pacote `Cⱼ` com **três** versões,
  `1.0`, `2.0` e `3.0`. A versão `k` de `Cⱼ` depende do pacote e versão que satisfazem o
  literal `l_k` (por exemplo, se `l₂ = ¬x₅`, então `Cⱼ 2.0` depende de `X₅ ==1.0`);
- o pacote-raiz depende de `C₁, ..., Cₘ` (sem restrição de versão).

Escolher uma versão de `Cⱼ` é escolher **qual literal satisfaz aquela cláusula**; a
dependência força a atribuição correspondente da variável. Existe solução se e somente se
`φ` é satisfatível. A construção é claramente polinomial. ∎

**Referência:** a formulação para gerenciadores de pacote reais é de
Mancinelli, Boender, Di Cosmo, Vouillon, Durak, Leroy e Treinen, *"Managing the
Complexity of Large Free and Open Source Package-Based Software Distributions"*,
ASE 2006 — o trabalho que originou o projeto EDOS/Mancoosi para o Debian.

### 2.2 A versão de otimização

Maximizar versões sujeito às restrições é um problema de otimização sobre um espaço
NP-difícil; ele é **NP-difícil** e sua versão de decisão associada ("existe solução com
`σ(p) ≥ v`?") permanece em NP. Na hierarquia polinomial, o problema de encontrar o
**ótimo lexicográfico** está em FP^NP (resolvível em tempo polinomial com um oráculo NP,
por busca binária sobre as versões).

### 2.3 Por que, então, funciona na prática

Três propriedades empíricas dos grafos reais:

1. **Esparsidade.** A distribuição do grau de saída (número de dependências diretas) é
   fortemente concentrada em valores baixos; a esmagadora maioria dos pacotes do PyPI tem
   menos de 5 dependências diretas.
2. **Restrições frouxas.** A cultura Python desencoraja limites superiores especulativos
   (ver §5). A maioria dos especificadores é `>=x` sem teto, o que torna os conjuntos `S`
   grandes e a satisfação fácil.
3. **Estrutura quase-arbórea.** O grafo tem poucos ciclos e uma componente central
   pequena (`certifi`, `urllib3`, `typing-extensions`, `packaging`...) da qual quase todo
   mundo depende, com versões amplamente compatíveis.

O caso patológico existe e aparece exatamente quando (2) é violado: pilhas com muitos
tetos rígidos (o ecossistema de ML com CUDA é o exemplo canônico) produzem os tempos de
resolução de minutos e as falhas insolúveis.

---

## 3. PubGrub, formalmente

PubGrub é CDCL aplicado a um domínio de **termos sobre intervalos de versão** em vez de
literais booleanos.

### 3.1 Termos

Um **termo** é um par `(p, S)` com sinal, onde `S` é um conjunto de versões (na prática,
uma união finita de intervalos):

- termo positivo `p ∈ S`: "a versão escolhida de `p` está em `S`";
- termo negativo `p ∉ S`: "a versão escolhida de `p` **não** está em `S`" (satisfeito
  também quando `p` não é selecionado).

Operações (a álgebra que a implementação precisa suportar):

| Operação | Definição |
|---|---|
| Negação | `¬(p ∈ S) = (p ∉ S)` |
| Interseção | `(p ∈ S₁) ∧ (p ∈ S₂) = (p ∈ S₁ ∩ S₂)` |
| Relação | `t₁` **satisfaz** `t₂` se todo modelo de `t₁` é modelo de `t₂` |
| Relação | `t₁` **contradiz** `t₂` se nenhum modelo de `t₁` é modelo de `t₂` |
| Relação | caso contrário, `t₁` é **inconclusivo** para `t₂` |

Os conjuntos `S` formam uma **álgebra booleana de intervalos** — é a estrutura que o
`pubgrub-rs` abstrai no traço `VersionSet`, e o que permite reusar a mesma implementação
para versões SemVer, PEP 440 ou qualquer domínio ordenado.

### 3.2 Incompatibilidades

Uma **incompatibilidade** é uma conjunção de termos `{t₁, ..., tₖ}` que não pode ser
inteiramente satisfeita. Equivale à cláusula `¬t₁ ∨ ... ∨ ¬tₖ`.

Fontes de incompatibilidades:

- **dependência:** `(p, v)` depende de `q ∈ S` gera `{ p ∈ [v, v⁺), q ∉ S }`;
- **conflito de raiz:** os requisitos de topo;
- **derivadas:** produzidas pela análise de conflito (§3.4).

### 3.3 Propagação unitária

Dada a solução parcial `A` (conjunto de atribuições) e uma incompatibilidade `I`:

- se **todos** os termos de `I` são satisfeitos por `A` → **conflito**;
- se todos menos um (`tⱼ`) são satisfeitos e `tⱼ` é inconclusivo → **derivar `¬tⱼ`**, e
  registrar `I` como a *causa* dessa derivação.

Isto é exatamente a propagação unitária de um solucionador SAT, elevada a intervalos.

### 3.4 Análise de conflito (resolução de cláusulas)

Ao detectar um conflito com a incompatibilidade `I`:

```
enquanto I não for "quase satisfeita no nível de decisão anterior":
    seja t o termo de I satisfeito mais recentemente em A
    se t veio de uma DECISÃO:
        pare  (I é a incompatibilidade a aprender)
    seja C a causa da derivação de t
    I ← resolvente prévio de I e C sobre o pacote de t
aprender I; retroceder ao nível em que I passa a ser unitária
```

O "resolvente prévio" é a regra de resolução da lógica proposicional, adaptada: dos dois
conjuntos, remove-se o termo do pacote em questão e faz-se a união dos demais,
intersectando termos do mesmo pacote.

**Teorema (correção e terminação).** O laço termina, e ou produz uma atribuição total
consistente, ou deriva a incompatibilidade vazia a partir do pacote-raiz (prova de
insatisfatibilidade). *Esboço:* o conjunto de pares (pacote, versão) é finito; cada
incompatibilidade aprendida é implicada pelo conjunto original e exclui pelo menos a
atribuição atual; nenhuma é aprendida duas vezes. Logo o número de aprendizados é
limitado pelo número de subconjuntos relevantes, e o algoritmo não pode ciclar.
(A prova completa está na documentação do `pub` de Natalie Weizenbaum e no artigo de
formalização do `pubgrub-rs`.)

**Complexidade de pior caso:** exponencial — como todo CDCL, e como tem de ser, dado §2.1.

### 3.5 A propriedade que interessa ao usuário

A cadeia de derivações que leva à incompatibilidade final **é uma prova de
insatisfatibilidade em forma de árvore**. Percorrê-la de trás para frente produz uma
explicação em linguagem natural — que é literalmente como o uv gera:

```
Because only httpx<=1.0.dev6 is available and your project depends on
httpx>=2.34.2, we can conclude that your project's requirements are unsatisfiable.
```

Este é o argumento técnico central a favor do PubGrub sobre backtracking simples: **a
explicabilidade não é um recurso adicionado por cima; ela é um subproduto do algoritmo.**

---

## 4. Resolução universal — a extensão do uv

### 4.1 O problema

Introduza um **espaço de ambientes** `E`, onde cada ambiente `e ∈ E` é uma valoração dos
marcadores da PEP 508 (`python_version`, `sys_platform`, `platform_machine`, ...).

Uma resolução tradicional produz `σ` para **um** `e`. Uma **resolução universal** produz
uma função `Σ : E → (P ⇀ V)` tal que, para todo `e ∈ E` admissível, `Σ(e)` é uma solução
válida no ambiente `e`.

Como `E` é infinito em princípio (versões futuras de Python, plataformas), o que se
representa de fato é uma **partição finita** de `E` em regiões, cada uma com uma solução
constante:

```
Σ = { (m₁, σ₁), (m₂, σ₂), ..., (mₖ, σₖ) }
```
com `mᵢ` marcadores mutuamente exclusivos cuja disjunção cobre `E`.

### 4.2 Forking

O uv começa tentando `k = 1`: uma solução única para todo `E`. Quando encontra uma
incompatibilidade cuja causa é **dependente do ambiente** (uma dependência com marcador,
ou um `requires-python` que exclui parte do espaço), ele **divide** a região corrente em
duas ou mais sub-regiões disjuntas e resolve cada uma independentemente.

```
resolver(R, m):
    tentar PubGrub sobre R restrito ao espaço marcado por m
    se conflito com causa dependente de ambiente, com marcador μ:
        return resolver(R, m ∧ μ) ∪ resolver(R, m ∧ ¬μ)
    senão:
        return { (m, σ) }
```

**Propriedades:**

- **Corretude:** cada `σᵢ` é solução válida em toda a sua região, porque foi obtida por
  PubGrub sobre exatamente as restrições ativas ali.
- **Cobertura:** por construção, `⋁ mᵢ ≡ ⊤` sobre `E`, já que cada divisão é `μ ∨ ¬μ`.
- **Disjunção:** as regiões são mutuamente exclusivas pela mesma razão.
- **Custo:** no pior caso, exponencial no número de pontos de divisão. Daí a importância
  de restringir `E` com `[tool.uv] environments` — é a otimização de maior impacto
  disponível ao usuário.

### 4.3 Estratégias de fork como objetivos de otimização

| Estratégia | Objetivo |
|---|---|
| `requires-python` (padrão) | maximizar `σᵢ(p)` **por região** — versões mais novas em cada ambiente |
| `fewest` | minimizar `\|{ σᵢ(p) : i }\|` para cada `p` — menos versões distintas no total |

São objetivos genuinamente conflitantes: a primeira maximiza atualidade, a segunda
minimiza a entropia do lockfile (o que facilita auditoria e reduz o tamanho do arquivo).
Não existe escolha universalmente correta; é uma decisão de projeto do usuário.

### 4.4 Uma pergunta em aberto

**Existe uma partição mínima?** Isto é: dado `R` e `E`, qual o menor `k` para o qual
existe uma `Σ` válida com `k` regiões? Isto é um problema de **cobertura mínima** sobre
um espaço já NP-difícil, e não conheço tratamento formal publicado no contexto de
empacotamento Python. O algoritmo do uv é guloso — divide quando encontra conflito — e
não busca minimalidade. É, na minha avaliação, um problema aberto interessante e de valor
prático imediato (locks menores, auditorias mais simples).

---

## 5. Sobre limites superiores: o argumento formal

A prática cultural do Python de **não** colocar tetos especulativos (`<2.0`) tem uma
justificativa que pode ser dita com precisão.

Seja `T(p)` o conjunto de restrições sobre `p` induzidas por todos os pacotes do grafo.
A satisfatibilidade exige `⋂ T(p) ≠ ∅`. Cada teto adicionado **reduz** monotonicamente
`⋂ T(p)`. Em um grafo com `n` pacotes que dependem de `p`, com tetos independentes e
distribuídos ao longo do tempo, a probabilidade de a interseção ficar vazia **cresce com
`n`** e com a taxa de lançamento de `p`.

O ponto econômico é assimétrico:

- um teto **correto** (a próxima versão realmente quebra) evita um bug **que apareceria
  em tempo de execução**, e que poderia ser corrigido depois pelo mantenedor;
- um teto **especulativo e errado** produz um conflito **insolúvel para todos os
  usuários a jusante**, que **não podem corrigi-lo** sem override — porque o teto está no
  `pyproject.toml` de terceiro.

O custo do falso positivo é distribuído por todo o ecossistema e é irreparável localmente;
o custo do falso negativo é local e reparável. Daí a assimetria de recomendação.

**Referências do debate:** Henry Schreiner, *"Should You Use Upper Bound Version
Constraints?"* (2021); a mudança de posição do Poetry após a discussão de 2021; a
orientação atual em `packaging.python.org`.

---

## 6. Modelos alternativos, e por que o Python não os usa

| Modelo | Quem usa | Ideia | Por que não no Python |
|---|---|---|---|
| **Instalação múltipla** (várias versões do mesmo pacote coexistindo) | npm, Cargo | resolução por caminho; cada consumidor vê sua versão | `sys.modules` é global por processo — exigiria mudar o `import` do CPython |
| **MVS** (*Minimal Version Selection*) | Go | escolha a **menor** versão que satisfaz; sem resolvedor, sem backtracking | requer que todo módulo declare versões exatas de tudo e siga import compatibility rigorosamente; incompatível com a cultura de faixas do PyPI |
| **SAT/PMS completo** | Debian (apt/aptitude), Eclipse P2 | resolvedor SAT com otimização multiobjetivo | é o que o PubGrub é, com melhor explicabilidade |
| **Ambientes funcionais** | Nix, Guix | cada dependência num caminho único e imutável; sem resolução, só composição | resolve por construção, mas exige refazer o empacotamento do mundo |
| **Sem resolução** | Bazel, Pants (com pins) | o humano fixa tudo | funciona em monorepo fechado, não num ecossistema aberto |

> **Observação:** o Nix é o único que elimina o problema em vez de resolvê-lo, ao permitir
> que versões diferentes coexistam com caminhos distintos. O custo é reempacotar todo o
> universo. É uma troca legítima e bem estudada — e é por isso que Nix e uv se combinam
> bem (`uv` dentro de uma `devShell`), em vez de competirem.

---

## 7. Problemas em aberto que eu acho interessantes

1. **Partição universal mínima** (§4.4).
2. **Resolução incremental.** Dado um lock existente e uma mudança em um requisito, qual
   é a solução válida mais próxima (menor distância de edição)? O uv já prefere versões
   já travadas por heurística; não conheço uma formulação e prova de otimalidade.
3. **Resolução com objetivo de segurança.** Minimizar CVEs conhecidas junto com maximizar
   versões: um problema multiobjetivo cujo espaço de Pareto ninguém explorou publicamente
   no contexto Python.
4. **Explicações mínimas.** A prova produzida pelo CDCL não é necessariamente a *menor*
   explicação possível. Minimizar a prova (um problema conhecido em SAT como *minimal
   unsatisfiable subset*) daria mensagens de erro melhores ainda.
5. **Interoperação formal entre lockfiles.** Existe uma tradução que preserve semântica
   entre `uv.lock`, `poetry.lock` e `pylock.toml`? A PEP 751 supõe que sim para o caso de
   instalação; para o caso universal, é uma questão em aberto.

---

## Autoteste

1. Construa a redução de 3-SAT para VERSION-SOLVING e explique por que ela é polinomial.
2. Por que verificar uma solução candidata é polinomial?
3. Defina termo, incompatibilidade e propagação unitária no PubGrub.
4. Descreva o laço de análise de conflito e diga o que ele "aprende".
5. Por que a explicabilidade das mensagens do uv é um subproduto do algoritmo?
6. Defina resolução universal como uma função `Σ` e diga o que garante cobertura e disjunção.
7. Por que restringir `[tool.uv] environments` tem impacto de complexidade, não só de estilo?
8. Formule o argumento assimétrico contra limites superiores especulativos.
9. Por que o modelo do npm (múltiplas versões) não é aplicável ao Python?
10. Escolha um dos cinco problemas em aberto e esboce como você o atacaria.

---

**Fontes:**
Mancinelli et al., *"Managing the Complexity of Large Free and Open Source Package-Based
Software Distributions"*, ASE 2006 ·
[a especificação do PubGrub, por Natalie Weizenbaum](https://github.com/dart-lang/pub/blob/master/doc/solver.md) ·
[github.com/pubgrub-rs/pubgrub](https://github.com/pubgrub-rs/pubgrub) ·
[docs.astral.sh/uv/reference/internals/resolver](https://docs.astral.sh/uv/reference/internals/resolver/) ·
[docs.astral.sh/uv/concepts/resolution](https://docs.astral.sh/uv/concepts/resolution/) ·
Henry Schreiner, *"Should You Use Upper Bound Version Constraints?"* (2021) ·
Russ Cox, *"Minimal Version Selection"* (2018), para o modelo do Go ·
Dolstra, *"The Purely Functional Software Deployment Model"* (tese, 2006), para o Nix.
Consultas de 31/08/2026. As provas dos teoremas de §3.4 estão esboçadas, não desenvolvidas
— a versão completa está nas fontes citadas.

**Próximo:** [65-estado-da-arte.md](65-estado-da-arte.md)
