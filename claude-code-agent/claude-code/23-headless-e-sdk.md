# 23 · Headless e SDK — Claude Code como peça de software

> **Nível:** avançado · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

O mesmo agente que roda no seu terminal roda em uma linha de script. É o que permite usá-lo
como etapa de pipeline, como *linter* semântico, como ferramenta de triagem — coisas que a
interface interativa não alcança.

---

## 1. O básico

```bash
claude -p "explique o módulo de autenticação"
```

Saída **real** desta máquina, 13/08/2026:

```bash
claude -p "responda apenas com a palavra: pronto"
# pronto
```

Código de saída 0 em sucesso, diferente de zero em falha — dá para ramificar em script.
Entrada canalizada funciona (limite: **10 MB**):

```bash
cat build-error.txt | claude -p "explique concisamente a causa raiz deste erro" > saida.txt
```

---

## 2. `--bare` — o modo certo para automação

```bash
claude --bare -p "Resuma README.md" --allowedTools "Read"
```

`--bare` **ignora**: hooks, skills, plugins, servidores MCP, memória automática e `CLAUDE.md`.

Por que isso importa: sem ele, um hook no `~/.claude` de um colega ou um MCP no `.mcp.json`
do projeto entram na execução — e o resultado deixa de ser reprodutível entre máquinas.

> **A pegadinha comprovada aqui:** em modo `--bare`, o Claude Code **não lê credenciais OAuth**.
> Rodando com login por assinatura, a saída real foi:
> ```json
> {"is_error":true, …, "result":"Not logged in · Please run /login"}
> ```
> Em `--bare`, defina `ANTHROPIC_API_KEY` (ou use as credenciais do seu provedor de nuvem).

Para carregar seletivamente:

| Precisa de | Flag |
|---|---|
| Instruções de sistema | `--append-system-prompt`, `--append-system-prompt-file` |
| Configurações | `--settings <arquivo-ou-json>` |
| Servidores MCP | `--mcp-config <arquivo-ou-json>` |
| Subagentes | `--agents <json>` |
| Um plugin | `--plugin-dir <caminho>`, `--plugin-url <url>` |

A documentação avisa que `--bare` deve virar o padrão de `-p` numa versão futura.

---

## 3. Formatos de saída

### `text` (padrão)
Só a resposta. Bom para canalizar.

### `json`
Resposta + metadados. Trecho **real** (projeto-modelo, 13/08/2026):

```json
{
  "is_error": false,
  "duration_api_ms": 4411,
  "num_turns": 2,
  "session_id": "84a5e3a3-ca87-4178-a64c-414d8def8b6c",
  "total_cost_usd": 0.1906005,
  "usage": {
    "input_tokens": 4,
    "cache_creation_input_tokens": 16300,
    "cache_read_input_tokens": 47811,
    "output_tokens": 147
  },
  "modelUsage": { "claude-opus-5[1m]": { "contextWindow": 1000000, "costUSD": 0.1906005 } },
  "permission_denials": [],
  "result": "…"
}
```

`total_cost_usd` é **estimativa do lado do cliente** — calculada a partir de contagens de
token a preços de tabela. Não reflete desconto contratual. Serve para orçamento e alerta,
não para conciliação contábil.

### `stream-json`
Eventos linha a linha, para interface própria:

```bash
claude -p "Escreva um poema" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

Eventos úteis: `system/init` (modelo, ferramentas, plugins, MCP e erros de carregamento),
`system/api_retry` (tentativa, atraso, categoria do erro), e a última linha `result`.

### `--json-schema` — saída estruturada validada

```bash
claude -p "Extraia os nomes de função de auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
  | jq '.structured_output'
```

**É o recurso que torna o agente utilizável dentro de software.** Sem ele, você extrairia
dados da prosa com expressão regular — frágil por construção. Com ele, ou o esquema é
respeitado, ou você recebe erro.

Nota: o `format` do JSON Schema (`"format": "email"`) é aceito como anotação, mas **não é
validado**.

---

## 4. Controles obrigatórios em automação

```bash
claude --bare -p "…" \
  --max-turns 5 \
  --max-budget-usd 1.00 \
  --permission-mode dontAsk \
  --allowedTools "Read,Grep" \
  --output-format json
```

| Flag | Por que é obrigatória |
|---|---|
| `--max-turns` | Um laço agêntico sem teto pode iterar indefinidamente |
| `--max-budget-usd` | Teto de gasto. Sem ele, um laço patológico vira fatura |
| `--permission-mode dontAsk` | Em CI não há ninguém para responder; `dontAsk` **nega** o não pré-aprovado |
| `--allowedTools` | Princípio do menor privilégio |
| `--bare` | Reprodutibilidade entre máquinas |

> `dontAsk` é a escolha certa para CI, e não `bypassPermissions`: o primeiro nega o que não
> foi liberado; o segundo libera tudo. Num runner com credenciais, a diferença é grande.

---

## 5. Padrões que funcionam

### Linter semântico no `package.json`

```json
{
  "scripts": {
    "lint:claude": "git diff main | claude -p \"você é um verificador de typos. para cada typo neste diff, reporte arquivo:linha numa linha e o problema na seguinte. não devolva mais nada.\""
  }
}
```

### Triagem de issue

```bash
gh issue view "$1" --json title,body | \
  claude --bare -p "Classifique esta issue." \
    --output-format json \
    --json-schema '{"type":"object","properties":{
      "tipo":{"enum":["bug","feature","duvida","spam"]},
      "prioridade":{"enum":["p0","p1","p2","p3"]},
      "componente":{"type":"string"},
      "resumo":{"type":"string"}},
      "required":["tipo","prioridade","componente","resumo"]}' \
  | jq '.structured_output'
```

### Conversa multi-etapa em script

```bash
sessao=$(claude -p "Comece a revisão deste repositório" --output-format json | jq -r '.session_id')
claude -p "Agora foque nas consultas ao banco" --resume "$sessao"
claude -p "Resuma tudo que encontrou"          --resume "$sessao"
```
A partir da 2.1.223, você pode retomar por ID **de qualquer diretório** da máquina.

### Portão de CI

Ver [`06`](06-exemplos.md), exemplo 7 — receita completa de GitHub Actions com esquema JSON
e teto de gasto.

---

## 6. Agent SDK

Para controle programático de verdade (callbacks de aprovação, objetos de mensagem
tipados, ferramentas próprias), existem pacotes **Python** e **TypeScript** do Agent SDK.
Eles expõem o mesmo laço, as mesmas ferramentas e a mesma gestão de contexto do Claude Code.

Quando usar o quê:

| Necessidade | Use |
|---|---|
| Script, CI, pipeline | `claude -p` |
| Precisa aprovar ferramentas programaticamente | SDK |
| Construir um produto com agente embutido | SDK |
| Ferramentas customizadas em processo | SDK |
| Só quer o resultado em JSON | `claude -p --json-schema` |

Documentação: `code.claude.com/docs/en/agent-sdk/overview`.
**Não exercitado neste curso** — o foco aqui é a CLI.

---

## 7. Comportamentos que surpreendem em automação

| Comportamento | Detalhe |
|---|---|
| Tarefas Bash em segundo plano | Encerradas ~5 s depois do resultado final |
| Subagentes em background | `-p` **espera** por eles, com teto de 10 min (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`) |
| SIGTERM | Aborta o turno, mata a árvore de processos, roda hooks `SessionEnd`, sai com **143** |
| Verificação de confiança | **Desativada** com `-p` — em automação, você é responsável pelo que roda |
| Comandos de barra | Funcionam em `-p`: inclua `/skill` no texto do prompt |
| `--mcp-config` com `-p` | Espera servidores pendentes até `MCP_TIMEOUT` (30 s por padrão) |
| Erro de carregamento de plugin/MCP | Aparece em `plugin_errors` / `mcp_server_errors` no evento `system/init` — use para falhar o CI |

Esse último merece uma linha de CI:

```bash
claude --bare -p "…" --output-format stream-json --verbose \
  | tee /tmp/eventos.jsonl >/dev/null
jq -e 'select(.type=="system" and .subtype=="init") | .mcp_server_errors // [] | length == 0' /tmp/eventos.jsonl
```

---

## 8. Os cinco porquês: por que `--bare` deveria virar o padrão de `-p`?

1. **Por que `--bare` existe?**
   Porque `-p` carrega, por padrão, tudo que uma sessão interativa carrega — inclusive
   configuração da máquina hospedeira.
2. **Por que isso é ruim em automação?**
   Porque o mesmo comando produz resultados diferentes em máquinas diferentes. Um hook no
   `~/.claude` de um dev entra no seu pipeline sem que ninguém tenha decidido isso.
3. **Por que o padrão foi esse, então?**
   Porque `-p` nasceu como "a mesma sessão, sem interface". A simetria era a propriedade
   desejada; automação veio depois.
4. **Por que não mudar imediatamente?**
   Mudar o padrão quebra scripts que dependem, hoje, do carregamento implícito. A
   documentação anuncia a mudança para uma versão futura.
5. **Qual é a lição?**
   **Padrão bom para uso interativo raramente é padrão bom para automação.** A propriedade
   que você quer no terminal é conveniência; em pipeline, é reprodutibilidade — e elas
   se opõem. *(Parada legítima: decisão de projeto documentada, com migração anunciada.)*

---

## Autoteste

1. O que `--bare` desliga? Qual é a pegadinha de autenticação, comprovada neste curso?
2. Quais cinco flags são obrigatórias ao rodar agente em CI, e por quê cada uma?
3. Por que `dontAsk` e não `bypassPermissions` em CI?
4. O que `--json-schema` permite que sem ele seria frágil?
5. O `total_cost_usd` serve para conciliação contábil? Por quê?
6. Como detectar, em CI, que um servidor MCP não carregou?
7. Quando usar o Agent SDK em vez de `claude -p`?
8. Por que "padrão bom para uso interativo raramente é padrão bom para automação"?
