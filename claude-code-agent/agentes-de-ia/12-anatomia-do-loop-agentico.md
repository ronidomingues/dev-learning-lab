# 12 · Anatomia do laço agêntico

**Nível:** intermediário → avançado · Atualizado em 13/08/2026

O [10](10-fundamentos.md) mostrou o laço em doze linhas. Aqui abrimos cada
uma. Se você só vai ler um arquivo do Bloco B, leia este: quase todo bug de
agente mora em algum detalhe desta página.

---

## 1. A API é sem estado. Toda vez.

Isto surpreende quem vem de chatbots: **o modelo não guarda nada entre
chamadas.** Não existe "conversa" no servidor. Existe você reenviando o
histórico inteiro a cada turno.

```
turno 1:  [user]
turno 2:  [user, assistant, user]
turno 3:  [user, assistant, user, assistant, user]
turno N:  ... tudo, sempre
```

Três consequências que explicam quase tudo:

| Consequência | Efeito prático |
|---|---|
| O custo por turno **cresce** com a conversa | o turno 30 custa muito mais que o turno 1 |
| O contexto tem teto | 1 milhão de tokens; encheu, algo precisa sair ([14](14-contexto-memoria-compactacao.md)) |
| O histórico é seu | você pode editar, comprimir, apagar — e é isso que a compactação faz |

O cache de prompt existe justamente para atenuar o item 1: o prefixo repetido
é cobrado a ~10% quando é lido do cache. Por isso a ordem importa — conteúdo
estável primeiro, volátil depois. Uma data no prompt de sistema invalida o
cache de tudo que vem depois dela.

---

## 2. Uma mensagem é uma lista de blocos, não uma string

O erro número um de quem escreve o primeiro laço: tratar a resposta como
texto.

```python
# ❌ quebra no próximo turno
mensagens.append({"role": "assistant", "content": resposta.content[0].text})

# ✅
mensagens.append({"role": "assistant", "content": resposta.content})
```

`resposta.content` é uma **lista de blocos** e pode conter:

| Bloco | O que é |
|---|---|
| `text` | texto para o usuário |
| `thinking` | raciocínio interno (ver §4) |
| `tool_use` | o pedido de ferramenta: `id`, `name`, `input` |
| `server_tool_use` / `*_tool_result` | ferramentas executadas no servidor (busca web, execução de código) |

Guardar só o `text` joga fora os blocos de `thinking` e de `tool_use`. O
resultado é uma mensagem `tool_result` órfã — o pedido correspondente sumiu — e
a API rejeita, ou o modelo perde o fio.

**Regra:** o `content` da resposta volta para o histórico **inteiro e
inalterado**.

---

## 3. `stop_reason`: o comando do laço

| Valor | Significa | O que fazer |
|---|---|---|
| `end_turn` | terminou naturalmente | sair do laço, entregar o texto |
| `tool_use` | quer uma ou mais ferramentas | executar e continuar — **a única continuação** |
| `max_tokens` | bateu o teto de saída | aumentar `max_tokens` ou usar streaming |
| `refusal` | recusado por segurança | tratar; `content` pode estar vazio |
| `pause_turn` | ferramenta de servidor atingiu o limite de iterações | reenviar para continuar |
| `stop_sequence` | bateu numa sequência de parada sua | tratar |

**Sempre cheque `stop_reason` antes de ler `content`.** Numa recusa,
`content` pode ser uma lista vazia, e `resposta.content[0].text` estoura
`IndexError` — em produção, às três da manhã.

`pause_turn` merece atenção: acontece quando uma ferramenta do servidor (busca
web, por exemplo) atinge o limite interno de iterações. Você reenvia a
conversa com a resposta anexada, e o servidor retoma de onde parou. Não
adicione uma mensagem "continue" — o servidor detecta o bloco pendente
sozinho.

---

## 4. Pensamento (thinking)

Modelos atuais raciocinam antes de responder. Nos modelos Claude 4.6 e
posteriores isso é **adaptativo**: o modelo decide quanto pensar, por
requisição, em vez de você fixar um orçamento de tokens.

```python
thinking={"type": "adaptive"}
output_config={"effort": "high"}   # low | medium | high | xhigh | max
```

Dois pontos que pegam quem migra de modelo antigo:

1. **`budget_tokens` foi removido** nos modelos atuais (Opus 4.7 em diante e
   Sonnet 5). Enviar retorna erro 400. Use `effort`.
2. **O texto do pensamento vem vazio por padrão** (`display: "omitted"`) nos
   modelos recentes. Para exibir um resumo, peça
   `thinking={"type": "adaptive", "display": "summarized"}`. Se você mostra o
   raciocínio na sua interface e ela ficou em branco depois de trocar de
   modelo, é isto.

No Claude Code, o equivalente é `/effort` e `Alt+T`.

**Por que o pensamento importa no laço, e não só na resposta final:** entre
uma chamada de ferramenta e a seguinte, o modelo pensa sobre o resultado que
acabou de receber. É aí que a correção de rota acontece. Um agente com
pensamento desligado tende a insistir no plano original mesmo depois de a
ferramenta dizer que ele está errado.

---

## 5. Ferramentas em paralelo

O modelo pode pedir várias ferramentas numa mesma resposta. Duas regras:

```python
# execute todas — de preferência concorrentemente
resultados = [executar(b) for b in r.content if b.type == "tool_use"]

# e devolva TODAS numa ÚNICA mensagem de usuário
mensagens.append({"role": "user", "content": resultados})
```

Dividir os resultados em várias mensagens não dá erro. Faz algo pior: **ensina
o modelo, na própria conversa, que pedidos paralelos não funcionam bem**, e
ele volta a pedir um de cada vez. Você perde latência sem nunca ver uma
mensagem de erro.

---

## 6. Erro de ferramenta é conteúdo, não exceção

A distinção que mais separa agente robusto de agente frágil:

```python
try:
    saida = executar(nome, argumentos)
    erro = False
except Exception as e:
    saida = f"Erro: {e}"     # a mensagem vira contexto
    erro = True

resultados.append({
    "type": "tool_result",
    "tool_use_id": bloco.id,     # tem de casar com o id do pedido
    "content": saida,
    "is_error": erro,
})
```

Um agente que levanta exceção na primeira ferramenta que falha não é um
agente — é um script. O modelo **precisa** receber a falha para se corrigir, e
é isso que ele faz bem hoje.

Corolário: **a mensagem de erro é código de produção.** Compare:

```
❌ "Erro: operação inválida"
✅ "Erro: tarefa #1 não existe ou já está concluída. Chame listar_tarefas
    para ver os ids válidos."
```

A primeira produz uma segunda tentativa idêntica. A segunda produz a chamada
certa. Escreva mensagens de erro como você escreveria para um colega novo.

---

## 7. Condições de parada — e todas as que faltam

O laço para sozinho quando `stop_reason == "end_turn"`. Na prática você
precisa de mais quatro travas:

| Trava | Por quê | Como |
|---|---|---|
| **Voltas** | um agente em ciclo não para sozinho | `--max-turns`; `for _ in range(N)` |
| **Orçamento** | tokens custam dinheiro real | `--max-budget-usd`; `task_budget` na API |
| **Tempo** | um `subprocess` travado trava o laço | timeout em toda ferramenta |
| **Humano** | o objetivo mudou | `Esc`; interrupção |

O **task budget** (beta) é interessante porque é diferente das outras: você
informa ao modelo quantos tokens ele tem para a tarefa inteira, e ele **vê o
contador**. Em vez de ser cortado no meio, ele se organiza para terminar. É
uma sugestão que o modelo enxerga, não um teto imposto — `max_tokens` continua
sendo o teto imposto, e o modelo não o enxerga.

---

## 8. Um turno, medido

Onde vai o tempo e o dinheiro numa volta típica de agente de código:

```
┌─ chamada ao modelo ──────────────────────── 2 a 30 s ──┐
│  entrada:  sistema + histórico + arquivos lidos        │  ← cresce a cada volta,
│  saída:    pensamento + texto + tool_use               │    cache ajuda muito
└────────────────────────────────────────────────────────┘
┌─ execução da ferramenta ─────────── 0,01 s a minutos ──┐
│  Read/Grep:     milissegundos                          │
│  Edit:          milissegundos                          │
│  Bash (testes): segundos a minutos  ← o gargalo real   │
│  WebFetch:      segundos                               │
└────────────────────────────────────────────────────────┘
```

Duas observações contraintuitivas:

- **O gargalo costuma ser a sua suíte de testes**, não o modelo. Uma suíte de
  4 minutos torna qualquer agente lento, porque o laço a executa várias vezes.
  Otimizar o teste rápido (`pytest -m "not slow"`) rende mais que trocar de
  modelo.
- **Saída custa ~5× a entrada.** Um agente que escreve muito texto explicativo
  a cada volta custa desproporcionalmente mais que um que age e resume no fim.
  Daí a instrução "não narre o que você fez com as ferramentas".

---

## 9. Onde o laço quebra na vida real

| Sintoma | Causa provável | Correção |
|---|---|---|
| Repete a mesma chamada de ferramenta | a mensagem de erro não diz o que corrigir | reescreva a mensagem (§6) |
| "Esquece" a instrução do começo | contexto compactado; a instrução era só da conversa | mova para o `CLAUDE.md` ([14](14-contexto-memoria-compactacao.md)) |
| Para de pedir ferramentas em paralelo | você devolveu os resultados em mensagens separadas | uma mensagem só (§5) |
| Erro de `tool_use_id` órfão | você guardou só o texto da resposta | guarde `content` inteiro (§2) |
| Fica caro sem explicação | histórico crescendo, cache invalidado | `/context`, `/compact`, prefixo estável (§1) |
| `IndexError` em `content[0]` | recusa ou resposta sem bloco de texto | cheque `stop_reason` antes (§3) |
| Insiste num plano já refutado | pensamento desligado | `thinking: adaptive` (§4) |
| Trava para sempre | ferramenta sem timeout | timeout em tudo (§7) |

---

## 10. Os cinco porquês: por que o agente às vezes anda em círculo?

**1. Por que ele repete a mesma ação que acabou de falhar?**
Porque a observação que ele recebeu não diferencia o estado atual do anterior.
`"Erro"` depois de `"Erro"` parece a mesma situação.

**2. Por que ele não percebe que já tentou isso?**
Ele percebe — o histórico está lá. Mas sem informação nova, a ação de maior
probabilidade continua sendo a mesma. Sem novidade na observação, não há
motivo para mudar de política.

**3. Por que não simplesmente proibir a repetição no arnês?**
Dá para fazer, e alguns arneses fazem. Mas repetir às vezes é **certo** —
`pytest` depois de editar deve rodar de novo. A proibição cega quebra o caso
legítimo.

**4. Então qual é a correção estrutural?**
Fazer a observação carregar informação: mensagens de erro específicas, saídas
que mostram o estado, ferramentas que devolvem o que mudou. Você conserta o
ciclo mudando o **ambiente**, não o modelo.

**5. Por que isso funciona?**
Porque o laço é um sistema de controle com realimentação. Se o sinal de
realimentação não carrega informação sobre o erro, nenhum controlador —
modelo ou humano — converge. É a mesma razão pela qual você não consegue
acertar um alvo com os olhos fechados, por mais preciso que seja o seu braço.

*Parada legítima:* é uma propriedade de sistemas de controle com
realimentação, anterior a IA e independente dela.

---

## Autoteste

1. Por que o custo do turno 30 é maior que o do turno 1, mesmo com o mesmo
   prompt?
2. O que quebra se você guardar `resposta.content[0].text` no histórico?
3. Liste os seis `stop_reason` e diga qual continua o laço.
4. Por que checar `stop_reason` antes de `content[0]` não é preciosismo?
5. O que acontece se você devolver dois `tool_result` em duas mensagens
   separadas? Aparece algum erro?
6. Reescreva `"Erro: operação inválida"` para uma mensagem que faça o agente se
   corrigir, e explique o critério que você usou.
7. Qual a diferença entre `max_tokens` e `task_budget`?
8. Cite duas travas de parada além de `end_turn` e diga o que cada uma evita.
9. Seu agente está lento. Antes de trocar de modelo, o que você mede?
10. Explique, pela ótica de controle com realimentação, por que um agente anda
    em círculo — e onde está a correção.
