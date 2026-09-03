# 60 · Teoria avançada

**Nível:** pesquisa
**Data:** 14/08/2026
**Pré-requisitos:** [`16`](16-dax-contexto-de-avaliacao.md), [`21`](21-vertipaq-por-dentro.md),
[`22`](22-desempenho.md). Alguma familiaridade com lógica, álgebra relacional e
complexidade computacional ajuda, mas cada conceito é definido aqui.

Este capítulo trata do que é **verdade** sobre o DAX e o modelo tabular, independentemente
de versão. É onde as regras práticas dos capítulos anteriores encontram sua justificação.

---

## 1. O modelo formal do contexto de filtro

### 1.1 Definição

Seja um modelo $M = (T, R)$, com $T = \{T_1, \dots, T_n\}$ tabelas e $R$ relacionamentos.
Cada tabela $T_i$ tem colunas $C_{i1}, \dots, C_{ik}$, cada uma com um domínio
$\text{dom}(C_{ij})$.

> **Contexto de filtro** $F$ é uma função que associa a cada coluna $C$ do modelo um
> subconjunto do seu domínio:
> $$F(C) \subseteq \text{dom}(C)$$

O contexto **vazio** é $F_\emptyset(C) = \text{dom}(C)$ para toda $C$ — nada filtrado.

Uma linha $r$ de uma tabela $T_i$ é **visível** em $F$ se, para toda coluna $C$ de $T_i$,
$r[C] \in F(C)$.

### 1.2 Composição

Filtros de origens diferentes (visual, segmentação, página) compõem-se por **interseção**:

$$(F_1 \sqcap F_2)(C) = F_1(C) \cap F_2(C)$$

Esta operação é **associativa**, **comutativa** e **idempotente** — ou seja, os contextos de
filtro sob $\sqcap$ formam um **semirreticulado inferior** (*meet-semilattice*), com
$F_\emptyset$ como elemento neutro.

**Consequência prática:** a ordem em que segmentações, filtros de página e filtros de
visual são aplicados **não importa**. É o teorema que garante o comportamento previsível
descrito em [`19-interatividade-e-relatorios.md`](19-interatividade-e-relatorios.md) §1.

### 1.3 `CALCULATE` não é uma operação de reticulado

`CALCULATE` **substitui** o filtro de uma coluna:

$$\text{CALC}(F, C, S)(C') = \begin{cases} S & \text{se } C' = C \\ F(C') & \text{caso contrário}\end{cases}$$

Isso **não é** uma interseção — e é exatamente por isso que `CALCULATE` quebra a
comutatividade e exige `KEEPFILTERS` quando você quer a interseção:

$$\text{KEEP}(F, C, S)(C) = F(C) \cap S$$

**Este é o conteúdo formal da "regra 1 de `CALCULATE`"** de
[`15-dax-fundamentos.md`](15-dax-fundamentos.md) §7. A substituição é uma operação
fundamentalmente diferente da composição de filtros, e é a origem de toda a confusão
prática com a função.

---

## 2. Propagação de filtro como problema em grafos

### 2.1 O grafo do modelo

O modelo é um **grafo direcionado** $G = (V, E)$ onde $V$ são as tabelas e cada aresta
$(T_i \to T_j) \in E$ é um relacionamento com direção de filtro de $T_i$ para $T_j$.

Filtrar $T_i$ propaga para toda $T_j$ **alcançável** a partir de $T_i$ em $G$.

### 2.2 Ambiguidade

> Um modelo é **ambíguo** se existem duas tabelas $T_a, T_b$ com **mais de um caminho
> direcionado** distinto de $T_a$ para $T_b$.

Com direção única e esquema estrela, $G$ é uma **árvore direcionada com raízes nas
dimensões** — não há ciclos e há no máximo um caminho entre quaisquer duas tabelas.
**Ambiguidade é estruturalmente impossível.**

Filtro bidirecional transforma arestas direcionadas em não direcionadas, criando ciclos.
Em um grafo com ciclos, múltiplos caminhos existem, e o resultado da propagação depende de
qual caminho o motor escolhe.

**O motor detecta alguns casos e recusa a relação** (`would create ambiguity`); em outros,
aceita e escolhe silenciosamente. **Este é o conteúdo formal do alerta de
[`14-modelagem-dimensional.md`](14-modelagem-dimensional.md) §7:** o problema do
bidirecional não é de desempenho — é de **boa definição**.

### 2.3 Complexidade

Determinar se um modelo com $n$ tabelas e $m$ relacionamentos é ambíguo é decidível em
tempo polinomial (contagem de caminhos em DAG, ou detecção de ciclos). O motor faz isso na
criação da relação. Não é o caso difícil — o caso difícil é o humano entender **o que** o
caminho escolhido significa para o negócio.

---

## 3. Expressividade do DAX

### 3.1 Onde o DAX se situa

| Linguagem | Expressividade |
|---|---|
| Álgebra relacional | Consultas de primeira ordem, sem recursão |
| SQL-92 | ≈ álgebra relacional + agregação |
| SQL com `WITH RECURSIVE` | Ponto fixo (Datalog); mais expressivo |
| **DAX** | Álgebra relacional + agregação + **iteração aninhada arbitrária** + funções de ordem superior sobre tabelas |
| Turing-completo | Não |

**O DAX não é Turing-completo**: não há recursão irrestrita nem laço com condição de
parada arbitrária. Toda expressão DAX **termina**. Isso é uma escolha de projeto valiosa —
significa que nenhuma medida pode travar o servidor indefinidamente por não terminar.

**O que o DAX tem além do SQL-92:**

- **iteradores aninhados** com acesso a contextos externos — o que dá poder de expressar
  cálculos "por linha em relação ao conjunto" sem correlação explícita;
- **transição de contexto**, que não tem análogo direto em SQL;
- **funções de tabela como valores de primeira classe** (tabelas passadas como argumento).

**O que o DAX não tem:**

- recursão real (você não escreve um cálculo de explosão de lista de materiais de
  profundidade arbitrária);
- laços com condição de parada;
- estado mutável.

### 3.2 O caso da recursão

Uma explosão de BOM (*bill of materials*) de profundidade **arbitrária** não é expressável
em DAX. As saídas:

1. **Achatar na fonte** (SQL recursivo, `WITH RECURSIVE`), materializando o caminho.
2. **`PATH` e `PATHITEM`** para hierarquias pai-filho — mas com **profundidade máxima
   fixa** definida em tempo de modelagem.
3. Aceitar um limite.

**Isso não é limitação de implementação: é consequência de o DAX não ter recursão.** E a
ausência de recursão é o que garante terminação. É um trade-off, não um defeito.

---

## 4. Complexidade de consulta

### 4.1 O modelo de custo

Para uma medida agregada simples sobre uma tabela de $N$ linhas com $c$ colunas
relevantes, comprimida com fator $\rho$:

$$T_{SE} \approx \frac{N \cdot c \cdot b}{\rho \cdot p \cdot \beta}$$

onde $b$ é bits por valor, $p$ o número de núcleos e $\beta$ a largura de banda de memória.

É **linear em $N$** e **inversamente proporcional ao paralelismo**. Este é o caso bom.

### 4.2 Onde a complexidade explode

**Iterador sobre iterador.** `SUMX(A, SUMX(B, ...))` com $|A| = n$ e $|B| = m$ custa
$O(n \cdot m)$ **no motor de fórmula**, que é sequencial.

**Transição de contexto em iterador.** `SUMX(T, [Medida])` sobre $|T| = n$ dispara $n$
reconstruções de contexto de filtro. Se cada uma custa $O(k)$, o total é $O(n \cdot k)$ —
**sequencial**.

Esta é a justificativa formal da regra prática de
[`16-dax-contexto-de-avaliacao.md`](16-dax-contexto-de-avaliacao.md) §4.3: itere
dimensões ($n$ pequeno), não fatos ($n$ enorme).

**`DISTINCTCOUNT`.** Não é decomponível por segmento: você não pode contar distintos de
cada segmento e somar. Exige uma estrutura global (bitmap, tabela hash), o que impede o
paralelismo puro e força materialização. É, previsivelmente, a agregação mais cara.

**Ranking (`RANKX`) no total.** Avaliar a posição no contexto do total exige materializar
todo o conjunto de comparação. É $O(n \log n)$ no melhor caso, no FE.

### 4.3 Por que agregações funcionam

Uma agregação pré-calculada com $N' \ll N$ linhas reduz o custo por um fator $N/N'$. Isso
funciona **porque agregações aditivas são associativas**: somar as somas parciais dá a
soma total.

Formalmente, uma agregação $f$ é **decomponível** se existem $g, h$ com

$$f(X \cup Y) = h(g(X), g(Y))$$

`SUM`, `COUNT`, `MIN`, `MAX` são decomponíveis. `AVERAGE` é, se você guardar soma e
contagem. **`DISTINCTCOUNT` e `MEDIAN` não são** — e por isso não podem ser
pré-agregadas exatamente.

**Este é o teorema por trás da tabela de agregação** de
[`20-modos-de-armazenamento.md`](20-modos-de-armazenamento.md) §7. Não é heurística; é a
condição algébrica que torna a técnica correta.

---

## 5. Limites de compressão

### 5.1 O piso da entropia

Para uma coluna com $N$ linhas e distribuição de probabilidade $\{p_1, \dots, p_k\}$ sobre
$k$ valores distintos, o **teorema da codificação de fonte de Shannon** (1948) estabelece
que o tamanho comprimido esperado por símbolo é limitado inferiormente pela entropia:

$$H = -\sum_{i=1}^{k} p_i \log_2 p_i \quad \text{bits por valor}$$

Nenhum codificador sem perda atinge menos que $H$ em média.

**Casos extremos:**

- **Valores uniformemente distribuídos e todos distintos** ($k = N$, $p_i = 1/N$):
  $H = \log_2 N$. Para $N = 10^8$, são ~26,6 bits por valor, **irredutíveis**.
- **Um valor dominante** ($p_1 \to 1$): $H \to 0$. Compressão quase total.

**Isto é o "por quê" final de [`21-vertipaq-por-dentro.md`](21-vertipaq-por-dentro.md) §10:**
alta cardinalidade é cara **por teorema**, não por limitação do VertiPaq. Nenhum
algoritmo, presente ou futuro, muda isso.

### 5.2 O que o VertiPaq realmente otimiza

O motor **não** tenta atingir o limite de Shannon — ele busca um ponto na fronteira entre
**taxa de compressão** e **custo de acesso**. Um código de Huffman ótimo comprime melhor
que RLE + dicionário, mas exige decodificação bit a bit, sequencial e não vetorizável.

O VertiPaq escolhe deliberadamente codificações **subótimas em taxa** e **ótimas em
acesso**: bits fixos por valor, decodificação por deslocamento e máscara, varredura
vetorizável.

**Isto é o "por quê" de não usar gzip:** o objetivo não é o menor arquivo, é o menor
**tempo de consulta**. São problemas de otimização diferentes.

### 5.3 Ordenação ótima de linhas

Encontrar a ordem de linhas que maximiza a compressão RLE conjunta de todas as colunas é
um problema de otimização combinatória. Formulado como busca da permutação que minimiza o
número total de "quebras de sequência" em todas as colunas, ele é aparentado a problemas
NP-difíceis clássicos (é redutível a variantes do problema do caixeiro-viajante sobre o
espaço de permutações de linhas).

**Por isso o VertiPaq usa heurísticas** e testa um número limitado de ordens, controlado
por parâmetros de processamento. Não é preguiça de implementação: é intratabilidade.

---

## 6. O teorema de Rice e o total da matriz

Em [`16-dax-contexto-de-avaliacao.md`](16-dax-contexto-de-avaliacao.md) §11 afirmei que o
motor não pode decidir se uma medida é aditiva. Vale formalizar.

> **Teorema de Rice (1953).** Toda propriedade **não trivial** da função computada por um
> programa é **indecidível**.

"Não trivial" = verdadeira para alguns programas e falsa para outros. "Aditividade" é
exatamente isso: verdadeira para `SUM(T[X])`, falsa para `DIVIDE(a,b)`.

**Ressalva honesta e importante:** o teorema de Rice se aplica a linguagens
Turing-completas, e o DAX **não é** Turing-completa (§3.1). Rigorosamente, portanto, Rice
não se aplica diretamente. Em princípio, a aditividade de uma expressão DAX é decidível —
o espaço é finito e analisável.

**Mas o argumento prático sobrevive**, por dois motivos:

1. **Custo.** A análise exigiria verificar a igualdade semântica de expressões com
   iteradores aninhados e transições de contexto sobre dados arbitrários. Isso encosta em
   verificação de equivalência de programas, que é intratável mesmo quando decidível.
2. **Dependência dos dados.** Uma expressão pode ser aditiva **para certos dados** e não
   para outros: `IF(SUM(T[X]) > 0, SUM(T[X]), 0)` é aditiva se todos os valores forem
   positivos. Uma análise estática correta teria de ser conservadora e, na prática,
   rejeitaria quase tudo.

**Conclusão:** a regra "sempre reavalia o total" não decorre de indecidibilidade estrita,
mas de **intratabilidade prática mais dependência dos dados**. O efeito é o mesmo, e a
decisão de projeto está correta. Prefiro esta versão precisa à invocação folclórica de
Rice que se vê em material de BI.

---

## 7. Consistência e o teorema CAP aplicado ao BI

Um relatório publicado é um **sistema distribuído**: fonte, gateway, capacidade, cache do
navegador.

**Modelo Import.** O sistema escolhe **disponibilidade** e **tolerância a partição**
(AP no CAP): o relatório responde mesmo com a fonte fora do ar, mas os dados podem estar
desatualizados — **consistência eventual**, com janela igual ao intervalo de refresh.

**Modelo DirectQuery.** Aproxima-se de **consistência** e **tolerância a partição**
(CP): o dado é sempre o atual, mas se a fonte cai o relatório cai junto.

**A escolha do modo de armazenamento é, literalmente, a escolha do vértice do CAP.**
[`20-modos-de-armazenamento.md`](20-modos-de-armazenamento.md) descreve as consequências
práticas; aqui está a razão de elas serem inevitáveis.

**Direct Lake** é uma tentativa de mover o ponto de operação: consistência quase imediata
(reapontamento após escrita no Delta) com disponibilidade alta (dados em memória). Não
escapa do teorema; apenas encurta a janela de inconsistência.

**Um detalhe sutil:** a **atomicidade do refresh** também importa. Se `fVendas` atualiza às
6h e `dProduto` às 6h05, existe uma janela em que o modelo é **internamente
inconsistente** — vendas de produtos ainda não cadastrados. O motor tabular processa em
transação, o que evita isso dentro de um refresh; mas em arquiteturas com dataflows
encadeados, a garantia se perde. É a origem de bugs que aparecem uma vez por mês, às 6h03.

---

## 8. Privacidade e o limite da RLS

A vulnerabilidade descrita em [`24-seguranca-e-governanca.md`](24-seguranca-e-governanca.md)
§2.4 tem nome na literatura: **ataque de reconstrução por consultas agregadas**.

> **Teorema fundamental da reconstrução de bases de dados** (Dinur–Nissim, 2003).
> Se um sistema responde a um número suficiente de consultas agregadas com erro limitado,
> um adversário pode reconstruir quase toda a base subjacente.

Formalmente: com $n$ registros e respostas com erro $o(\sqrt{n})$, é possível reconstruir
$1 - o(1)$ da base com um número polinomial de consultas.

**Aplicação ao Power BI:** a RLS filtra **linhas**, mas permite consultas agregadas sobre
o conjunto completo (via `REMOVEFILTERS`). Um usuário paciente, cruzando recortes, pode
inferir valores que a RLS pretendia esconder.

**A defesa da literatura é a privacidade diferencial:** adicionar ruído calibrado às
respostas, com um orçamento de privacidade $\varepsilon$ que se esgota.

**O Power BI não implementa isso**, e provavelmente nunca implementará — ruído é
inaceitável em relatório financeiro, onde os números precisam fechar exatamente.

**Portanto, a conclusão prática é a única disponível:** se o agregado é sensível, **ele não
pode estar no mesmo modelo**. Separação física, não lógica. Isso é uma consequência
matemática, não uma limitação de produto.

---

## 9. A ordem de execução como semântica denotacional

Vale explicitar o que `CALCULATE` faz, formalmente, porque é a fonte de erro mais comum.

Seja $\llbracket e \rrbracket_F$ a denotação da expressão $e$ no contexto $F$.

$$\llbracket \text{CALCULATE}(e, f_1, \dots, f_k) \rrbracket_F = \llbracket e \rrbracket_{F'}$$

onde
$$F' = \text{aplicar}\Big(\text{transição}(F),\ \llbracket f_1 \rrbracket_F,\ \dots,\ \llbracket f_k \rrbracket_F\Big)$$

**Note o índice $F$ nos argumentos de filtro.** Eles são avaliados no contexto **original**,
não no modificado. Esta é a fonte de metade das surpresas com `CALCULATE`, e a expressão
acima é a formulação precisa da §5.1 de
[`16-dax-contexto-de-avaliacao.md`](16-dax-contexto-de-avaliacao.md).

**Corolário:** `CALCULATE` **não é composicional da forma ingênua**:

$$\text{CALCULATE}(\text{CALCULATE}(e, f_1), f_2) \neq \text{CALCULATE}(e, f_1, f_2)$$

em geral, porque no lado esquerdo $f_1$ é avaliado no contexto já modificado por $f_2$.
Este é um resultado que quase ninguém conhece e que explica bugs sutis em medidas
aninhadas.

---

## 10. Problemas em aberto e áreas de pesquisa

Do ponto de vista de quem estuda o campo, o que continua não resolvido:

1. **Otimização automática de DAX.** Não existe um "reescritor" que transforme DAX
   ineficiente em eficiente preservando a semântica. Reescritas seguras exigem provar
   equivalência de expressões com transição de contexto — problema aberto na prática.

2. **Verificação de modelos semânticos.** Não há sistema de tipos ou verificador que prove
   propriedades como "esta medida é aditiva sobre esta dimensão" ou "esta RLS é completa".
   O Best Practice Analyzer é sintático, não semântico.

3. **Camada semântica interoperável.** Cada ferramenta tem a sua (DAX, LookML, MetricFlow,
   Cube). Não há padrão. É a maior fonte de aprisionamento no campo hoje.

4. **Verificação de saída de LLM sobre modelos semânticos.** Como provar que uma medida
   gerada por IA computa o que se pediu? Verificação por testes é o estado da arte, e é
   fraca.

5. **Privacidade em BI corporativo.** Nenhuma solução prática entre "todos veem os
   agregados" e "modelos separados".

6. **Compressão adaptativa.** As escolhas do VertiPaq são feitas no processamento, com
   amostragem. Adaptar ao padrão real de consulta observado é uma direção óbvia e não
   explorada publicamente.

---

## 11. Autoteste

1. Defina contexto de filtro formalmente e mostre por que a ordem de aplicação de
   segmentações não importa.
2. Por que `CALCULATE` não é uma operação do semirreticulado, e o que `KEEPFILTERS` faz
   formalmente?
3. Defina ambiguidade em termos de grafos e explique por que a estrela a torna impossível.
4. O DAX é Turing-completo? Que consequência prática isso tem?
5. Dê a condição algébrica de decomponibilidade e diga por que `DISTINCTCOUNT` não a
   satisfaz.
6. Enuncie o limite de Shannon e aplique-o a uma coluna com 10⁸ valores distintos.
7. Por que o VertiPaq não busca compressão ótima?
8. Por que a afirmação "Rice impede o motor de decidir aditividade" precisa de ressalva, e
   qual é o argumento correto?
9. Mapeie Import e DirectQuery nos vértices do CAP.
10. Enuncie o resultado de Dinur–Nissim e explique sua consequência para a RLS.
11. Escreva a denotação de `CALCULATE` e explique o corolário sobre aninhamento.
12. Cite três problemas em aberto no campo.

---

**Próximo:** [`65-estado-da-arte.md`](65-estado-da-arte.md).

---

*Referências: Shannon, C. E. "A Mathematical Theory of Communication", Bell System Technical Journal, 1948. Rice, H. G. "Classes of Recursively Enumerable Sets and Their Decision Problems", Transactions of the AMS, 1953. Dinur, I.; Nissim, K. "Revealing Information While Preserving Privacy", PODS 2003. Dwork, C. "Differential Privacy", ICALP 2006. Brewer, E. "Towards Robust Distributed Systems" (conjectura CAP), PODC 2000; Gilbert, S.; Lynch, N. "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services", SIGACT News, 2002. Abadi, D.; Boncz, P.; Harizopoulos, S. "The Design and Implementation of Modern Column-Oriented Database Systems", Foundations and Trends in Databases, 2013.*
