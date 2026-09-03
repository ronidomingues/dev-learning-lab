# 60 · Teoria avançada — o que é possível, o que é caro, o que é impossível

> **Nível:** pesquisa · **Atualizado em:** 13/08/2026
> Pré-requisitos: [`10`](10-fundamentos.md) e [`12`](12-anatomia-de-uma-sessao.md).
> Aqui as afirmações são matemáticas ou vêm de literatura citada; onde há especulação, está marcado.

---

## 1. Por que contexto é caro: a atenção quadrática

O transformador calcula, para cada token, uma comparação com todos os outros. Com sequência
de comprimento $n$ e dimensão $d$:

$$\text{Atenção}(Q,K,V) = \text{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V$$

A matriz $QK^{\top}$ tem $n^2$ entradas. Custo de tempo e de memória: $O(n^2 d)$.

| Contexto | Custo relativo de atenção |
|---|---|
| 10 mil tokens | 1× |
| 100 mil | 100× |
| 1 milhão | **10.000×** |

Isso explica, de uma vez, três fatos práticos:

1. Por que existe limite de janela, e por que ele custa caro.
2. Por que **cache de prompt** muda tanto a economia: o prefixo já processado não precisa
   ser recalculado, e o custo de um turno cai de $O(n^2)$ para algo próximo de linear no que
   é novo.
3. Por que "só aumentar a janela" não resolve engenharia de contexto.

### O que a pesquisa tentou

| Abordagem | Ideia | Situação em ago/2026 |
|---|---|---|
| Atenção esparsa (Longformer, BigBird, 2020) | cada token olha só uma vizinhança + alguns globais | usada em nichos; perde em qualidade geral |
| Atenção linear (Performer, Linear Transformers, 2020–21) | aproximar o softmax para custo $O(n)$ | aproximação degrada tarefas de recuperação precisa |
| FlashAttention (2022) e sucessores | **mesma** matemática, uso ótimo da memória da GPU | **adotada em toda parte** — ganho de constante, não de ordem |
| Espaço de estados / recorrentes (Mamba, RWKV, 2023–24) | estado de tamanho fixo, custo linear | promissores; ainda não substituíram atenção completa nos modelos de fronteira |
| Híbridos (atenção + recorrência) | poucos blocos de atenção completa | linha ativa em 2025–2026 |

**A leitura honesta:** o ganho prático de 2022 a 2026 veio muito mais de **constantes**
(FlashAttention, kernels, hardware) e de **cache** do que de derrubar o $O(n^2)$. Quem
promete "contexto infinito barato" está omitindo o custo ou a perda de qualidade.
**[avaliação do autor, sobre literatura pública]**

---

## 2. Degradação em contexto longo (*context rot*)

**[fato empírico, replicado em vários trabalhos desde 2023]** Modelos ficam mensuravelmente
piores em contexto muito longo, mesmo dentro da janela suportada. O padrão canônico é o
**"perdido no meio"** (Liu et al., 2023, *Lost in the Middle*): a recuperação de informação
posicionada no meio da janela é pior que nas pontas.

Consequências operacionais:

- Colocar 1 MB de código no contexto **não** equivale a o modelo "conhecer" o código.
- Informação crítica deve estar **perto do fim** — que é onde vai a sua última mensagem.
- Contexto curto e curado bate contexto longo e completo.

**Por que acontece.** Não há explicação única e consensual. As hipóteses com mais apoio:
distribuição de comprimentos no treino, viés posicional das codificações de posição
(RoPE e variantes), e diluição da distribuição de atenção sobre muitos tokens — com
softmax sobre $n$ itens, a massa por item cai. **[hipóteses, não consenso fechado]**

---

## 3. A composição de confiabilidade

Já vista no [`11`](11-historia.md), aqui formalizada. Se cada passo agêntico tem
probabilidade $p$ de estar correto e os erros fossem independentes, a tarefa de $n$ passos
termina certa com $p^n$:

| $p$ | $n=5$ | $n=20$ | $n=50$ |
|---|---|---|---|
| 0,90 | 59% | 12% | 0,5% |
| 0,95 | 77% | 36% | 8% |
| 0,99 | 95% | 82% | 61% |
| 0,999 | 99,5% | 98% | 95% |

**Mas a independência é falsa em duas direções, e as duas importam:**

**Correlação negativa (ajuda):** com verificação, um erro é detectado e corrigido. O laço
deixa de ser uma cadeia de multiplicações e passa a ter **recuperação**. Modelando uma
chance $r$ de recuperar cada erro detectado, a taxa efetiva por passo vira
$p' = p + (1-p)\,r$. Com $p=0{,}95$ e $r=0{,}8$, $p'=0{,}99$ — e a tarefa de 20 passos vai
de 36% para 82%.

**Este é o argumento matemático a favor do Pilar 1 do [`25`](25-o-oficio-do-profissional.md).**
Testes não melhoram o modelo; melhoram $r$. E $r$ entra na conta com o mesmo peso de $p$.

**Correlação positiva (atrapalha):** um erro no passo 3 contamina o contexto dos passos
seguintes. O modelo passa a raciocinar sobre uma premissa falsa que **ele mesmo** escreveu.
É o argumento matemático a favor de interromper cedo ([`25`](25-o-oficio-do-profissional.md),
Pilar 5): o custo de um erro não é local, é o resto da cadeia.

---

## 4. Limites de decidibilidade — o que **nenhum** agente pode garantir

Aqui não há avanço de modelo que resolva. São teoremas.

**Problema da parada (Turing, 1936).** Não existe algoritmo que decida, para todo programa,
se ele termina. Logo, nenhum agente pode garantir "este código não entra em laço infinito"
no caso geral.

**Teorema de Rice (1953).** *Toda* propriedade semântica não trivial de programas é
indecidível. "Este código está correto", "não tem vazamento de memória", "não tem
comportamento indefinido" — todas indecidíveis em geral.

**O que isso significa na prática, com precisão:**

| Afirmação | Status |
|---|---|
| "O agente garante que o código está correto" | **Impossível** em geral |
| "O agente garante que os testes passam" | Possível: é verificação empírica de casos finitos |
| "Os testes passando garantem correção" | **Falso** — Dijkstra, 1970: testes mostram a presença de bugs, nunca a ausência |
| "O verificador formal provou a propriedade P deste programa" | Possível, para P e programas restritos, com custo alto |
| "O agente encontrou todos os bugs" | **Impossível** em geral |

Nenhuma dessas limitações é sobre IA. Elas valem igualmente para um humano — e é por isso
que a engenharia de software inteira é construída sobre **evidência parcial** (testes,
tipos, revisão), não sobre prova. Um agente muda a velocidade de produzir evidência; não
muda a natureza dela.

---

## 5. O agente como sistema de busca

Formalização útil: um agente faz **busca em um espaço de estados**.

- Estado: (conteúdo do repositório, contexto).
- Ações: as ferramentas.
- Transição: efeito da ação no disco e no contexto.
- Função objetivo: seu critério de sucesso.
- Política: o modelo.

Sob essa lente, as práticas do [`25`](25-o-oficio-do-profissional.md) ganham nome técnico:

| Prática | Nome na busca |
|---|---|
| Verificação automática | **função de avaliação** — sem ela, busca cega |
| Modo plano | **busca antes de agir** — explora sem transição irreversível |
| `/rewind`, git | **retrocesso** (*backtracking*) |
| Interromper cedo | **poda** de ramo ruim |
| Contexto curado | **redução do fator de ramificação** |
| Subagentes | **decomposição** em subproblemas |

E a limitação também ganha nome: sem função de avaliação, o agente faz busca gulosa guiada
por uma heurística (a plausibilidade estimada pelo modelo) — que é exatamente o cenário em
que busca gulosa falha de forma característica: encontra um ótimo local plausível e para.

---

## 6. Cache e a economia do laço

Sem cache, um laço de $k$ turnos com contexto crescente custa aproximadamente

$$\sum_{i=1}^{k} c \cdot n_i$$

onde $n_i$ é o tamanho do contexto no turno $i$. Como $n_i$ cresce, o custo é
**superlinear em $k$**.

Com cache do prefixo, o custo de reler o prefixo cai para uma fração $\alpha$ (bem menor
que 1). O termo dominante passa a ser $\alpha \cdot n_i$ mais o custo integral só do que é
novo. É o que se vê no JSON real medido neste curso:

```
"input_tokens": 4,  "cache_read_input_tokens": 47811
```

**Consequências não óbvias, e é aqui que muita intuição erra:**

1. **Recomeçar sessão a cada pergunta é caro**, porque paga o prefixo cheio toda vez.
2. **Continuar sessão longa também é caro**, porque $n_i$ é grande mesmo com desconto.
3. O ótimo é **sessão contínua por tarefa, e `/clear` entre tarefas** — que é exatamente a
   recomendação prática, aqui derivada da economia e não do bom senso.
4. O **tempo de vida do cache** (1 h em assinatura; 5 min com créditos de uso ou chave de
   API) cria um efeito de borda: voltar do almoço reprocessa tudo. Uma tarefa longa
   interrompida é mais cara que a mesma tarefa contínua.

---

## 7. Injeção de prompt como propriedade estrutural

Formalizando o que o [`24`](24-seguranca.md) descreve. Seja $C$ o contexto e $M$ o modelo.
A saída é $M(C)$. Não existe partição $C = C_{\text{instrução}} \sqcup C_{\text{dados}}$ que
$M$ **respeite por construção**: $M$ é uma função de todo $C$, e a distinção só existe se o
próprio $M$ a implementar — probabilisticamente.

Compare com SQL parametrizado: ali, o *parser* é um programa determinístico e separado, e o
valor **nunca** pode virar estrutura sintática. A separação é garantida por fora do
processamento de dados. Num LLM, o "parser" é a própria rede.

**Consequência teórica:** defesas dentro do modelo (treino, marcação, delimitadores) reduzem
probabilidade; não estabelecem invariante. Defesas fora do modelo (permissões, sandbox,
fronteira de diretório) estabelecem invariantes — sobre **ações**, não sobre saída de texto.

É por isso que o desenho do Claude Code coloca a barreira no executor e não no modelo, e por
que a documentação oficial diz explicitamente que nenhum sistema é imune. **[fato + análise]**

---

## 8. Questões em aberto

**[especulação fundamentada]** O que eu observo como problema não resolvido, em agosto de 2026:

1. **Verificação escalável.** Como saber que uma mudança grande está certa, sem revisão
   humana proporcional ao tamanho? Prova assistida? Testes gerados por outro modelo (e quem
   verifica o verificador)? É o gargalo real do campo.
2. **Memória entre sessões.** `CLAUDE.md` e memória automática são aproximações grosseiras.
   Não há representação persistente e composicional do conhecimento de um projeto.
3. **Composição de agentes.** Times de agentes multiplicam custo e trazem os problemas
   clássicos de sistemas distribuídos (consistência, ordenação, deadlock) sem as ferramentas
   correspondentes.
4. **Avaliação honesta.** Benchmarks de código (SWE-bench e sucessores) sofrem contaminação e
   medem tarefas com oráculo claro — que são justamente as fáceis para agentes. O trabalho
   difícil é o que não tem oráculo, e é o que não é medido.
5. **Atribuição de responsabilidade.** Se um agente introduz uma vulnerabilidade que passa
   pela revisão, de quem é a responsabilidade? Questão jurídica e organizacional em aberto.

---

## 9. Leituras

| Trabalho | Por que importa |
|---|---|
| Vaswani et al., *Attention Is All You Need* (2017) | a arquitetura; a origem do $O(n^2)$ |
| Liu et al., *Lost in the Middle* (2023) | evidência da degradação posicional |
| Dao et al., *FlashAttention* (2022) | por que o ganho foi de constante, não de ordem |
| Gu & Dao, *Mamba* (2023) | a alternativa recorrente mais séria |
| Rice (1953) | indecidibilidade de propriedades semânticas |
| Dijkstra, *Notes on Structured Programming* (1970) | "testes mostram presença, não ausência de bugs" |
| Yao et al., *ReAct* (2022) | formalização do laço raciocínio + ação |
| Jimenez et al., *SWE-bench* (2023) | como se mede agente de código, e os limites disso |

Referências completas em [`95-referencias.md`](95-referencias.md).

---

## Autoteste

1. Por que a atenção custa $O(n^2)$, e por que "só aumentar a janela" não resolve engenharia de contexto?
2. O ganho prático de 2022–2026 veio de derrubar a ordem quadrática ou de outra coisa?
3. O que é *lost in the middle* e que decisão prática ele sustenta?
4. Deduza $p' = p + (1-p)r$ e mostre o efeito com $p=0{,}95$, $r=0{,}8$, $n=20$.
5. Por que erros num laço agêntico têm correlação positiva, e que prática isso justifica?
6. Enuncie o teorema de Rice e diga o que ele torna impossível para qualquer agente.
7. Traduza cinco práticas do [`25`](25-o-oficio-do-profissional.md) para o vocabulário de busca em espaço de estados.
8. Derive, da economia do cache, por que "sessão contínua por tarefa, `/clear` entre tarefas" é o ótimo.
9. Por que a separação instrução/dados de SQL parametrizado não tem análogo num LLM?
