# 13 · Ferramentas e uso de ferramentas

**Nível:** intermediário · Atualizado em 13/08/2026

> **A tese deste capítulo:** o conjunto de ferramentas que você oferece a um
> agente é uma decisão de projeto tão determinante quanto a escolha do modelo.
> O SWE-agent demonstrou isso em 2024 e chamou de **ACI — Agent–Computer
> Interface**. Com o mesmo modelo, ferramentas melhores mudaram a taxa de
> sucesso de forma drástica.

---

## 1. O que é uma ferramenta, mecanicamente

Três partes, e só:

```json
{
  "name": "ler_arquivo",
  "description": "Lê o conteúdo de um arquivo de texto do projeto. Use antes de editar qualquer arquivo — nunca edite baseado em suposição sobre o conteúdo.",
  "input_schema": {
    "type": "object",
    "properties": {
      "caminho": { "type": "string", "description": "Caminho relativo à raiz do projeto." },
      "linhas":  { "type": "string", "description": "Faixa opcional, ex.: '10-40'. Omita para o arquivo inteiro." }
    },
    "required": ["caminho"],
    "additionalProperties": false
  }
}
```

O que o modelo vê é **exatamente isso**: nome, descrição, esquema. Ele nunca
vê a sua implementação. Portanto: se o comportamento real diverge da
descrição, o modelo usa errado, e nenhum ajuste de prompt conserta.

**Chamada estrita.** Marcar `"strict": true` (com `additionalProperties:
false` e `required` preenchido) faz a API garantir que o `input` valida contra
o esquema. Vale sempre que a ferramenta tem efeito colateral: você troca uma
classe inteira de erro em tempo de execução por uma garantia.

---

## 2. A descrição é prompt, não documentação

Este é o parágrafo mais lucrativo do capítulo.

| ❌ | ✅ |
|---|---|
| `"Busca no banco de dados."` | `"Busca clientes por nome, e-mail ou CNPJ. Use sempre que a pergunta envolver um cliente específico — nunca responda de memória, pois o cadastro muda. Não use para relatórios agregados: para isso use relatorio_clientes."` |

O que a versão boa acrescenta, em quatro movimentos:

1. **O que faz**, com precisão (por quais campos busca).
2. **Quando usar** — o gatilho. *Sem gatilho, a ferramenta é ignorada quando o
   modelo "acha que já sabe".*
3. **Quando NÃO usar**, apontando a alternativa. Sem isso, ferramentas
   parecidas se confundem.
4. **Por que confiar nela em vez da memória** — a razão, não só a ordem.

Regra prática: **3 a 4 frases é o piso, não o teto.** O erro comum em
descrições de ferramenta não é excesso, é escassez. (O oposto do que vale para
prompts de sistema, onde o excesso atrapalha.)

E o inverso também é verdade: descrição com urgência inflada — `"CRITICAL:
você DEVE sempre usar esta ferramenta"` — causa *sobre-disparo* nos modelos
atuais, que seguem instruções de perto. Diga o que você quer, em volume
normal.

---

## 3. Bash ou ferramenta dedicada?

O dilema central de projeto. Uma ferramenta `bash` dá ao agente alavancagem
quase ilimitada. Mas dá ao **seu arnês** apenas uma string opaca — a mesma
forma para qualquer ação.

Promova uma ação a ferramenta dedicada quando você precisar de:

| Necessidade | Por que o bash não serve |
|---|---|
| **Aprovar antes** | `enviar_email(...)` é fácil de barrar; `bash -c "curl -X POST ..."` não |
| **Checar consistência** | um `edit` dedicado pode recusar a escrita se o arquivo mudou desde a leitura |
| **Renderizar na interface** | uma pergunta ao usuário pode virar um diálogo, não texto solto |
| **Paralelizar com segurança** | dá para marcar `grep` como seguro para paralelo; `bash` genérico, não — o arnês precisa serializar |
| **Auditar** | argumentos tipados entram no log estruturados |

> **Regra de bolso:** comece com `bash` para ter alcance. Promova a ferramenta
> dedicada quando precisar **barrar, renderizar, auditar ou paralelizar**
> aquela ação específica.

---

## 4. As ferramentas embutidas do Claude Code

Os nomes abaixo são as strings exatas que você usa em regras de permissão, em
`tools:` de subagente e em `matcher` de hook. (Claude Code 2.1.231; a lista
cresce a cada versão — `/help` e a documentação são a fonte viva.)

**Arquivos**

| Ferramenta | O que faz |
|---|---|
| `Read` | lê arquivos — texto, imagens, PDFs, notebooks |
| `Write` | cria ou sobrescreve |
| `Edit` | substituição pontual dentro de um arquivo |
| `NotebookEdit` | células de Jupyter |

**Busca**

| Ferramenta | O que faz |
|---|---|
| `Glob` | acha arquivos por padrão de nome |
| `Grep` | busca conteúdo por regex (ripgrep) |
| `LSP` | inteligência de código: ir para definição, referências, erros de tipo |

**Execução**

| Ferramenta | O que faz |
|---|---|
| `Bash` | comandos de shell |
| `PowerShell` | idem, nativo no Windows |
| `Monitor` | roda em segundo plano e devolve cada linha de saída ao Claude, para ele reagir a logs ao vivo |

**Web**

| `WebSearch` | busca | `WebFetch` | busca uma URL e responde sobre ela |
|---|---|---|---|

**Orquestração**

| Ferramenta | O que faz |
|---|---|
| `Agent` | cria um subagente com contexto próprio |
| `Skill` | executa uma skill na conversa atual |
| `Workflow` | roda um workflow dinâmico (muitos subagentes, em script) |
| `TaskCreate` / `TaskList` / `TaskGet` / `TaskUpdate` / `TaskStop` | lista de tarefas |
| `SendMessage` / `ListAgents` | mensagens entre agentes e sessões |
| `EnterPlanMode` / `ExitPlanMode` | plan mode |
| `EnterWorktree` / `ExitWorktree` | worktrees isolados |
| `AskUserQuestion` | pergunta de múltipla escolha ao usuário |

**MCP e extensões**

| Ferramenta | O que faz |
|---|---|
| `ListMcpResourcesTool` / `ReadMcpResourceTool` | recursos expostos por servidores MCP |
| `ToolSearch` | carrega ferramentas adiadas sob demanda |
| `WaitForMcpServers` | espera servidores que ainda estão conectando |

**Outras**

`Artifact` (publica página no claude.ai) · `PushNotification` ·
`SendUserFile` · `CronCreate`/`CronList`/`CronDelete` (agendamento na sessão) ·
`ScheduleWakeup` · `RemoteTrigger` · `ReportFindings` · `EndConversation`

Ferramentas de servidores MCP aparecem como `mcp__<servidor>__<ferramenta>`.

**Restringir o conjunto:**

```bash
claude --tools "Read,Grep,Glob"        # só estas ferramentas embutidas
claude --disallowedTools "Bash(rm *)"  # nega um padrão, mantém a ferramenta
claude --disallowedTools "Edit"        # remove a ferramenta do contexto
```

Note a diferença: `--disallowedTools "Edit"` (nome puro) **remove a ferramenta
do contexto do modelo** — ele nem sabe que ela existe. `Bash(rm *)` (regra com
escopo) mantém a ferramenta e nega só as chamadas que casam. A primeira forma
é mais forte e mais barata em tokens; a segunda é mais cirúrgica.

---

## 5. Sete princípios de projeto de ferramenta

**1. Uma ferramenta, uma responsabilidade, uma fronteira clara.**
Duas ferramentas que se sobrepõem custam mais que uma ferramenta a menos:
o modelo hesita, escolhe errado, e você perde uma volta. Se precisar manter
as duas, cada descrição diz explicitamente o que **não** cobre.

**2. O retorno é para ser lido por um modelo.**
Devolver 4 000 linhas de JSON queima contexto para transmitir três fatos.
Devolva o essencial, formatado para leitura, com um caminho para o detalhe:
`"3 falhas. A primeira: tests/test_pag.py:41 — esperado 1500, obtido 1499.
Use ler_arquivo para ver as outras."`

**3. Mensagem de erro é interface.**
Diga como corrigir, não só que falhou. Ver [12 §6](12-anatomia-do-loop-agentico.md#6-erro-de-ferramenta-é-conteúdo-não-exceção).

**4. Parâmetros expressivos economizam prompt.**
Um `enum` com os valores válidos carrega mais informação — e mais barato — que
um parágrafo de descrição explicando quais strings são aceitas.

**5. Idempotência quando possível.**
O agente vai repetir chamadas. `criar_ou_atualizar` é melhor que `criar` que
estoura no segundo uso.

**6. Poucas ferramentas, bem escolhidas.**
Cada definição ocupa contexto **em toda chamada**. Acima de algumas dezenas,
use *tool search* (carrega o esquema sob demanda) em vez de despejar tudo.

**7. Nomeie no domínio de quem lê.**
`buscar_cliente` vence `db_query_customers_v2`. O modelo lê o nome como parte
do gatilho.

---

## 6. Ferramentas do cliente × do servidor

| | Cliente | Servidor |
|---|---|---|
| Onde executa | sua máquina / seu processo | infraestrutura da Anthropic |
| Exemplos | `Bash`, `Edit`, MCP, suas funções | busca web, busca de URL, execução de código |
| Você implementa? | sim | não |
| Enxerga seus arquivos? | sim | não |
| Ponto de controle | seu, integral | limitado |

A regra que decorre disso: **o que precisa tocar no seu ambiente é ferramenta
de cliente.** É por isso que o Claude Code executa localmente, e é por isso
que a fronteira de confiança fica na sua máquina — ver
[10, os cinco porquês](10-fundamentos.md#os-cinco-porquês-por-que-o-modelo-não-executa-a-ferramenta-ele-mesmo).

---

## 7. Chamada programática de ferramenta (PTC)

Um padrão recente que vale conhecer. No uso normal, cada chamada é uma ida e
volta: o modelo chama, o resultado entra no contexto dele, ele raciocina,
chama de novo. Três chamadas encadeadas = três voltas, e todo o dado
intermediário passa pelo contexto.

Com **programmatic tool calling**, o modelo escreve um *script* que chama as
ferramentas. O script roda no contêiner de execução; quando invoca uma
ferramenta, a chamada é executada e o resultado volta **para o código**, não
para o contexto. Laços, filtros e condicionais acontecem em Python. Só a saída
final volta ao modelo.

Quando compensa: muitas chamadas sequenciais, ou resultados intermediários
grandes que você quer filtrar antes que cheguem à janela de contexto.

---

## 8. Erros clássicos de projeto de ferramenta

| Erro | Sintoma | Correção |
|---|---|---|
| Descrição de uma linha | ferramenta ignorada, ou usada na hora errada | 3–4 frases, com gatilho |
| Descrição sem "quando NÃO usar" | ferramentas parecidas se confundem | fronteira explícita, apontando a alternativa |
| `MUST`/`CRITICAL` em caixa alta | sobre-disparo | volume normal |
| Retorno gigante | contexto estoura em 5 voltas | resuma, ofereça caminho para o detalhe |
| Erro genérico | o agente repete a mesma chamada | mensagem que diz como corrigir |
| 40 ferramentas sempre carregadas | caro em toda chamada, escolha ruim | tool search / carregamento adiado |
| Exemplo de diálogo dentro da descrição | ocupa tokens em toda requisição, restringe a exploração | material didático vai para skill |
| Instrução de conversa na descrição (`"depois de mostrar, sempre recomende..."`) | contrato virou prompt | descrição é contrato; comportamento vai para o prompt de sistema |

---

## 9. Exercício

Pegue a ferramenta `criar_tarefa` do
[projeto-modelo](07-projeto-modelo/mcp_tarefas.py) e degrade-a de propósito:

```python
"description": "Cria tarefa."
```

Reinicie a sessão e peça: *"preciso lembrar de revisar o contrato"*. Depois
restaure a descrição original e repita o mesmo pedido. A diferença de
comportamento — se a ferramenta é chamada, e com que argumentos — é o
capítulo inteiro, medido.

---

## Autoteste

1. O que exatamente o modelo enxerga de uma ferramenta?
2. Quais são os quatro movimentos de uma boa descrição?
3. Por que `CRITICAL: você DEVE...` piora o comportamento nos modelos atuais?
4. Quando promover uma ação de `bash` para ferramenta dedicada? Cite três
   critérios.
5. Diferença prática entre `--disallowedTools "Edit"` e `--disallowedTools
   "Bash(rm *)"`.
6. Por que o retorno de uma ferramenta deve ser desenhado para ser lido por um
   modelo, e o que isso muda concretamente?
7. Explique a tese da ACI e por que ela é uma boa notícia para o engenheiro.
8. Você tem 60 ferramentas MCP conectadas e o contexto começa cheio. Qual é a
   correção estrutural?
9. Por que idempotência importa mais em ferramenta de agente que em API comum?
10. Um exemplo de diálogo dentro da `description` "melhora a taxa de chamada"
    em um teste seu. Por que ainda assim é má ideia?
