# 12 · O modelo por dentro — o mínimo que um dev precisa saber

**Nível:** intermediário · **Escrito em:** 20/08/2026

> Você não precisa saber treinar um modelo. Precisa saber o suficiente para
> **prever o comportamento dele** — porque quem não entende o mecanismo briga
> com o sintoma para sempre.
>
> Este arquivo cobre só o que muda decisão prática. A teoria completa está em
> [engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md) e em
> [bert](../bert/00-MAPA.md).

---

## 1 · O que o modelo faz, em uma linha

Recebe uma sequência de *tokens* e produz uma distribuição de probabilidade
sobre o próximo *token*. Um deles é escolhido. Ele é acrescentado à sequência.
Repete.

É isso. Tudo o mais — raciocínio, uso de ferramenta, agente — é construído em
cima dessa operação.

```
"def somar(a, b):\n    return " → P(próximo token)
                                  "a"     0.71
                                  "sum"   0.09
                                  "(a"    0.06
                                  "0"     0.02
                                  ...
```

### Consequência prática nº 1

**Ele não tem um plano.** Quando ele "explica o que vai fazer" e depois faz, a
explicação não é um plano executado — é texto que aumentou a probabilidade dos
tokens seguintes ficarem coerentes com ela.

Isso não a torna inútil: pelo contrário, **é exatamente por isso que pedir o
plano antes funciona**. O plano na janela condiciona o que vem depois. Você não
está lendo a intenção dele; está *criando* a intenção dele.

### Consequência prática nº 2

**Ele não sabe que não sabe.** Não há sinal interno de "isso eu não vi no
treino". Há uma distribuição, e algum token sempre é o mais provável. Onde o
conhecimento é raso, a distribuição é mais achatada — mas a saída sai com a
mesma cadência confiante.

Por isso "não alucine" não funciona como instrução: você está pedindo que ele
use um sinal que ele não tem.

---

## 2 · Token — a unidade de tudo

**Token** é um pedaço de texto do vocabulário do modelo. Não é caractere nem
palavra: fica no meio.

| Texto | Tokens aproximados |
|---|---|
| `hello world` | 2 |
| `olá mundo` | 3–4 |
| `calcularTotalDoPedido` | 4–6 |
| `calcular_total_do_pedido` | 5–7 |
| `a1b2c3d4e5f6` (hash) | ~12 |
| 1 KB de código-fonte | ~250–350 |

### Três consequências que mudam decisão

**a) Português custa mais que inglês.** O vocabulário é dominado por inglês; um
texto em português vira ~20–30% mais tokens que o equivalente em inglês. Em
volume alto, isso é dinheiro.

**b) Modelo não conta letras direito.** "Quantos 'r' tem morango?" é difícil
porque ele não vê letras, vê tokens. Isso parece curiosidade e tem consequência
real: **não peça manipulação de caractere, contagem exata, ou aritmética
precisa a um LLM. Peça o código que faz isso.** Ferramenta é determinística;
modelo não é.

**c) Identificador longo custa e atrapalha.** `usuarioAtivoComAssinaturaVigente`
vira muitos tokens e a busca por ele no repositório é menos eficiente.

### Novidade de 2026 que vale saber

Modelos recentes da Anthropic (Claude 4.7 em diante) usam um tokenizador novo
que **produz ~30% mais tokens para o mesmo texto**, em troca de melhor
desempenho. Ou seja: contagem de tokens não é comparável entre gerações, e uma
mesma tarefa pode custar mais tokens num modelo melhor sem que nada tenha
piorado. Se você monitora custo por token, ajuste a linha de base ao trocar de
modelo.

---

## 3 · Janela de contexto — o que existe e o que não existe

**Janela de contexto** é o número máximo de tokens que o modelo processa de uma
vez. Em 2026, os modelos de ponta chegam a **1 milhão de tokens**.

O que ocupa a janela numa sessão de agente:

```
┌───────────────────────────────────────────────┐
│ prompt de sistema da ferramenta      ~2–10k   │  fixo
│ definições das ferramentas           ~1–3k    │  fixo
│ AGENTS.md / CLAUDE.md                ~0,5–3k  │  fixo
│ ─────────────────────────────────────────────  │
│ seu pedido                           ~0,1–1k  │
│ arquivos lidos                       ~5–200k  │  cresce
│ saída de comandos                    ~1–50k   │  cresce
│ raciocínio e respostas anteriores    ~5–100k  │  cresce
└───────────────────────────────────────────────┘
```

### Fato central: **fora da janela não existe**

Não é que ele "esqueceu". É que aquilo nunca esteve lá. A instrução que você deu
há 40 minutos, se o histórico foi comprimido, simplesmente não faz parte da
entrada.

**Daí a regra:** o que precisa valer sempre mora em **arquivo** (`AGENTS.md`),
não em mensagem. Arquivo é relido; mensagem é descartada.

### Degradação antes do limite: "perdido no meio"

Janela grande não significa atenção uniforme. Há um efeito bem documentado —
*lost in the middle* (Liu et al., 2023) — em que a informação no **meio** de um
contexto longo é recuperada com muito menos confiabilidade que a do começo e a
do fim.

Modelos de 2026 são bem melhores nisso que os de 2023, mas o efeito não zerou.
Consequências operacionais:

| Faça | Não faça |
|---|---|
| Ponha a instrução crítica **no fim** do prompt | Enterrar a regra importante no meio de 200 linhas |
| Sessão curta, uma tarefa | Sessão de 3 horas com 5 tarefas |
| Deixe o agente buscar o trecho | Colar 30 arquivos "por garantia" |

> **Contraintuição importante:** encher a janela porque ela é grande **piora** o
> resultado. Contexto é como uma mesa de trabalho — mais espaço ajuda até o ponto
> em que você não acha mais nada em cima dela.

---

## 4 · Amostragem — por que a resposta muda a cada vez

Escolhido o próximo token a partir da distribuição, **como** se escolhe?

| Parâmetro | O que faz | Efeito prático |
|---|---|---|
| `temperature` | Achata (alto) ou aguça (baixo) a distribuição | 0 ≈ determinístico; 1 = criativo |
| `top_p` | Considera só os tokens que somam p de probabilidade | Corta a cauda improvável |
| `top_k` | Considera só os k mais prováveis | Idem, por contagem |

### Por que "temperatura 0" **não** garante repetibilidade

Isso confunde muita gente. Mesmo com temperatura 0:

- aritmética de ponto flutuante em GPU não é associativa, e a ordem de redução
  varia com o tamanho do lote;
- o provedor pode rotear para hardware diferente;
- o modelo por trás do mesmo nome pode ser atualizado.

**Conclusão operacional dura:** um sistema que depende de saída idêntica de LLM
é um sistema quebrado. Se você precisa de determinismo, ponha o determinismo do
lado de fora — no teste, no portão, no esquema de validação. É a razão de o
[projeto-modelo](07-projeto-modelo/README.md) não ter uma linha de IA dentro
dele.

### Como isso aparece no seu dia

- Rodar o mesmo pedido duas vezes dá resultados diferentes. **Isso é normal, não
  é bug.**
- Uma tentativa que falhou pode ter sido azar de amostragem. **Vale uma segunda
  tentativa com contexto limpo** antes de concluir que "o modelo não consegue".
- Se o resultado precisa ser sempre igual, você quer um script, não um agente.

---

## 5 · Raciocínio estendido (*extended thinking*)

Modelos de 2025–2026 podem gerar tokens de raciocínio antes da resposta.
Mecanicamente é simples: **mais tokens gerados antes da conclusão = mais
computação aplicada ao problema**.

Não é misticismo. É literalmente o modelo se dando mais passos.

| Vale a pena para | Não vale para |
|---|---|
| Bug com várias causas possíveis | Renomear variável |
| Decisão de arquitetura | Formatar JSON |
| Refatoração com muitas restrições | Escrever docstring |
| Depurar teste instável | Traduzir texto |

**Custa mais** (tokens de raciocínio são cobrados como saída, a mais cara) e
**demora mais**. A escolha do esforço é uma decisão de custo, exatamente como
escolher instância de servidor.

> **Efeito colateral de 2026 que muda prática:** com raciocínio embutido,
> escrever "pense passo a passo" no prompt virou redundante e às vezes
> prejudicial — você está pedindo ao modelo que simule por fora o que ele já faz
> por dentro. É um dos itens da tabela de obsoletos do
> [05-manual-de-uso](05-manual-de-uso.md).

---

## 6 · Cache de prompt — a economia que quase ninguém usa

O provedor pode guardar o estado interno correspondente a um prefixo do prompt.
Se a próxima requisição começar com **exatamente** o mesmo prefixo, ele reaproveita.

Números da Claude API (consultados em 20/08/2026):

| Operação | Multiplicador sobre o preço base de entrada |
|---|---|
| Escrita no cache (5 min) | 1,25× |
| Escrita no cache (1 h) | 2× |
| **Leitura do cache (acerto)** | **0,1×** |

Ou seja: **um acerto de cache custa 10% do preço normal de entrada.** O cache de
5 minutos se paga depois de **uma** leitura; o de 1 hora, depois de duas.

### O que isso exige de você

O cache casa por **prefixo exato**. Portanto:

| Faça | Por quê |
|---|---|
| Mantenha `AGENTS.md` estável durante a sessão | Editá-lo invalida todo o cache dali para a frente |
| Acrescente ao fim do contexto | Inserir no meio invalida o resto |
| Uma sessão longa por tarefa é melhor que 10 curtas idênticas | O prefixo se repete e o cache acerta |

Repare na tensão com a regra do §3 ("sessão curta"). As duas são verdadeiras e
se resolvem assim: **uma sessão por tarefa** — curta o bastante para não
degradar, longa o bastante para o cache acertar. Não pique a mesma tarefa em
cinco sessões.

---

## 7 · Ferramentas (*tool use*) — como o modelo ganha mãos

O provedor descreve funções disponíveis num esquema. O modelo, em vez de texto,
emite uma **chamada estruturada**. O programa hospedeiro executa de verdade e
devolve o resultado como mais uma mensagem.

```
você:    "quantos testes existem?"
modelo:  → chamada: Bash(command="rg -c 'def test_' tests/ | wc -l")
sistema: ← resultado: "49"
modelo:  "49 testes."
```

**O modelo nunca executa nada.** Ele pede; o programa decide se executa. Essa
separação é toda a base de permissões do [05](05-manual-de-uso.md) e toda a base
de segurança do [22](22-seguranca.md).

Custo escondido: a definição das ferramentas ocupa contexto a cada requisição —
algumas centenas de tokens por conjunto, mais o esquema de cada uma. Conectar 15
servidores MCP "por precaução" gasta contexto em toda mensagem e piora a
qualidade da escolha de ferramenta. **Menos ferramentas, melhor uso.**

---

## 8 · Por que ele erra onde erra — o mapa

Junte tudo e você consegue **prever** onde o modelo falha. Esta tabela é, na
prática, o resumo utilizável do arquivo.

| Onde ele acerta muito | Por quê |
|---|---|
| Padrões com muito exemplo público (REST, testes, SQL, Docker) | Densidade de treino altíssima |
| Traduzir entre formatos e linguagens | Tarefa de mapeamento, não de invenção |
| Explicar código existente | O código está na janela; é leitura, não geração |
| Listar dimensões de um problema conhecido | Memória estatística ampla |
| Boilerplate | Definição de repetição |

| Onde ele erra — e erra com confiança | Por quê |
|---|---|
| A sua regra de negócio | Nunca viu. Extrapola |
| Nome de API ou pacote pouco comum | Interpola pelo padrão dos nomes → inventa o plausível |
| Versão recente de biblioteca | Corte de treino; ele conhece a API de 18 meses atrás |
| Aritmética exata, contagem, datas | Tokens não são números |
| Consistência num arquivo muito longo | Atenção não uniforme |
| Concorrência e ordem temporal | Pouco exemplo correto no treino; o código errado sobre concorrência é abundante |
| Saber que não sabe | Não há sinal interno para isso |

> **Use esta tabela antes de delegar.** Se a tarefa cai na segunda metade, ou
> você não delega, ou constrói a verificação primeiro. Ela é a forma operacional
> da regra de ouro do [10](10-fundamentos.md).

---

## 9 · Os cinco porquês: por que ele inventa nome de pacote

**Por que o modelo inventa `starlette-reverse-proxy`?**
Porque, dado o contexto, essa sequência de tokens é altamente provável.

**Por que ela é provável se o pacote não existe?**
Porque o modelo aprendeu a **morfologia** dos nomes de pacote:
`<framework>-<função>` é um padrão realizado milhares de vezes
(`starlette-context`, `fastapi-users`, `django-cors-headers`). O nome inventado
obedece perfeitamente ao padrão.

**Por que ele não confere se existe?**
Porque não há passo de conferência. A geração é um processo de amostragem, não
de consulta. Sem uma ferramenta de busca acionada, não há a quê conferir.

**Por que não colocaram uma conferência embutida?**
Porque exigiria que o modelo tivesse uma lista autoritativa e atualizada de todo
pacote de todo ecossistema dentro dos pesos — impossível, porque os pesos são
congelados no treino e o registro muda a cada minuto. A solução real é externa:
dar a ele uma ferramenta de busca, ou verificar depois.

**Por que isso não é consertável no modelo, em princípio?**
Porque é a mesma limitação de qualquer sistema que comprime conhecimento em
parâmetros fixos: **fato que muda mais rápido que o treino não pode viver nos
pesos.** Essa é a parada legítima — é uma restrição estrutural, não um defeito
de implementação. E é por isso que a defesa contra *slopsquatting* é um portão,
não um prompt melhor.

---

## Autoteste

1. Descreva em uma frase o que o modelo faz. Que duas consequências práticas
   isso tem?
2. Por que "não alucine" não funciona como instrução?
3. Por que pedir o plano antes funciona, se o modelo "não tem um plano"?
4. Por que português custa mais que inglês? Que decisão isso muda?
5. Por que não se deve pedir aritmética exata a um LLM, e o que se pede no lugar?
6. O que significa "fora da janela não existe" e onde deve morar a informação
   permanente?
7. Por que encher a janela grande piora o resultado?
8. Por que temperatura 0 não garante repetibilidade? Qual é a conclusão
   operacional?
9. Um acerto de cache custa 10% da entrada. O que você precisa fazer para
   conseguir acerto de cache?
10. Cite quatro situações da tabela do §8 onde o modelo erra com confiança, e
    diga por quê em cada uma.
11. Aplique os cinco porquês: por que o modelo inventa nome de pacote e por que
    isso não é consertável nos pesos?

---

**Anterior:** [11-historia](11-historia.md) ·
**Próximo:** [13-os-quatro-modos-de-uso](13-os-quatro-modos-de-uso.md)
