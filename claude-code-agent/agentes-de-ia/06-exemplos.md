# 06 · Exemplos

**Nível:** iniciante → avançado · Atualizado em 13/08/2026

Doze receitas, do trivial ao que se usa em produção. Cada uma: **problema →
solução → por que funciona**. Tudo copiável; nada com `...` no meio.

Os exemplos 1–8 rodam com o Claude Code instalado. Os 9–12 exigem uma chave de
API (`ANTHROPIC_API_KEY`) e o pacote `anthropic`.

| # | Assunto | Nível |
|---|---|---|
| [1](#1-entender-um-repositório-que-você-nunca-viu) | Reconhecimento de repositório | trivial |
| [2](#2-corrigir-um-bug-com-teste-que-reproduz) | Bug com teste | trivial |
| [3](#3-refatoração-segura-com-plan-mode) | Plan mode | básico |
| [4](#4-usar-a-saída-de-um-comando-como-contexto) | Prefixo `!` | básico |
| [5](#5-transformar-uma-tarefa-repetitiva-em-skill) | Skill | intermediário |
| [6](#6-hook-que-impede-o-erro-em-vez-de-pedir-para-não-errar) | Hook | intermediário |
| [7](#7-subagente-para-não-poluir-o-contexto) | Subagente | intermediário |
| [8](#8-servidor-mcp-em-40-linhas) | MCP | intermediário |
| [9](#9-o-laço-agêntico-em-30-linhas-de-python) | Laço à mão | intermediário |
| [10](#10-claude-code-como-comando-de-shell) | Headless | avançado |
| [11](#11-produção-triagem-de-issues-no-ci) | **produção** | avançado |
| [12](#12-produção-migração-de-500-arquivos) | **produção** | avançado |

---

## 1. Entender um repositório que você nunca viu

**Problema.** Você entrou num projeto de 80 mil linhas e precisa achar onde
mexer.

**Solução.**

```bash
cd ~/projeto-desconhecido
claude
```

```
não altere nada. me explique, em no máximo 15 linhas:
1. o que este sistema faz, do ponto de vista do usuário
2. qual é o ponto de entrada
3. como um pedido HTTP atravessa o código até o banco
4. quais são os 3 arquivos que eu leria primeiro para entender o domínio
```

**Por que funciona.** Três coisas: "não altere nada" tira a ansiedade de
permissão; o limite de 15 linhas impede a resposta enciclopédica que ninguém
lê; e as quatro perguntas são específicas o bastante para ele ter de *procurar*
em vez de generalizar.

**Variação melhor ainda** — deixe o resultado no repositório:

```
faça o mesmo e escreva em docs/ARQUITETURA.md, com links para os arquivos
citados no formato caminho:linha
```

---

## 2. Corrigir um bug com teste que reproduz

**Problema.** Bug reportado, você não sabe a causa.

**Solução — sempre nesta ordem:**

```
escreva primeiro um teste que FALHE reproduzindo este bug:
"na fatura parcelada, a última parcela vem 1 centavo menor que as outras
quando o total não é divisível por 3"

não corrija ainda. me mostre o teste falhando.
```

Depois de conferir que o teste realmente reproduz:

```
agora corrija, mantendo o teste. rode a suíte inteira no final.
```

**Por que funciona.** O teste que falha é o "palito no bolo": transforma
"acho que consertei" em um sinal binário e verificável. Separar em dois turnos
evita o padrão mais comum de falha — ele escrever um teste que passa com o
código errado, e depois "corrigir" nada.

---

## 3. Refatoração segura com plan mode

**Problema.** Refatoração grande, você não quer descobrir o desastre depois de
pronto.

**Solução.**

```bash
claude --permission-mode plan
```
Ou, dentro da sessão, `Shift+Tab` duas vezes.

```
o módulo de notificação está espalhado entre 6 arquivos e mistura envio de
e-mail com push. quero separar em duas interfaces com uma fábrica.

não implemente. leia os 6 arquivos e me proponha um plano com:
- quais arquivos mudam e o que acontece em cada
- em que ordem, para a suíte ficar verde a cada passo
- o que pode quebrar em quem consome esse módulo
```

Leia o plano. Corrija por conversa:

```
o passo 3 quebra a compatibilidade com o webhook do Stripe. inverta a ordem
de 3 e 4 e mantenha o adaptador antigo até o final.
```

Só então saia do plan mode e mande executar.

**Por que funciona.** Corrigir um plano custa uma frase. Corrigir uma
implementação errada custa a tarefa inteira — e você ainda precisa entender
o que ele fez para desfazer. Plan mode é a operação de maior retorno sobre
esforço do curso inteiro.

---

## 4. Usar a saída de um comando como contexto

**Problema.** Ele responde sobre um estado desatualizado do sistema.

**Solução.** O prefixo `!` roda o comando e coloca a saída no contexto:

```
!docker compose ps
```
```
!npm test 2>&1 | tail -40
```
```
por que o container do redis está reiniciando em loop? use a saída acima.
```

**Por que funciona.** Você elimina a decisão dele de rodar (ou não) o comando
certo, e elimina a chance de ele responder de memória. Custa um turno e
resolve metade dos "ele está confuso".

**Caso frequente:**

```
!git log --oneline -20
!git diff origin/main --stat
escreva a descrição do PR a partir disso, em português, com uma seção de
"como testar".
```

---

## 5. Transformar uma tarefa repetitiva em skill

**Problema.** Toda semana você cola o mesmo bloco de instruções sobre como
escrever a nota de release.

**Solução.** `.claude/skills/release-notes/SKILL.md`:

```markdown
---
name: release-notes
description: Escreve a nota de release da versão a partir dos commits desde a última tag. Use quando pedirem "nota de release", "changelog" ou "o que mudou nesta versão".
---

# Nota de release

1. `git describe --tags --abbrev=0` para achar a última tag.
2. `git log <tag>..HEAD --oneline` para os commits.
3. Agrupe em: **Novidades**, **Correções**, **Interno** (não sai na nota
   pública, mas liste para eu conferir).
4. Escreva do ponto de vista de quem usa, não de quem programou:
   "agora dá para exportar em CSV", não "adicionado CsvExporter".
5. Cada item em uma linha, sem ponto final, começando com verbo no infinitivo.
6. Se houver mudança incompatível, abra a nota com um bloco
   `> **Atenção:**` explicando a migração.

Não invente item que não tenha commit correspondente.
```

Usar:

```
/release-notes
```

**Por que funciona.** O corpo da skill **não ocupa contexto** até ser
invocado. Só a linha `description` fica visível ao modelo. Isso é a diferença
entre uma skill e uma seção do `CLAUDE.md`: a seção custa em toda sessão, a
skill custa quando é usada.

---

## 6. Hook que impede o erro, em vez de pedir para não errar

**Problema.** Você escreveu no `CLAUDE.md` "sempre rode o lint depois de
editar". Ele obedece nos primeiros vinte minutos e esquece no resto.

**Solução.** `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && ruff check --fix . 2>&1 | tail -20"
          }
        ]
      }
    ]
  }
}
```

Para *bloquear* em vez de corrigir, use `PreToolUse` e saia com código 2:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/bloqueia-prod.sh" }
        ]
      }
    ]
  }
}
```

```bash
#!/usr/bin/env bash
# .claude/bloqueia-prod.sh  — chmod +x
entrada=$(cat)
if echo "$entrada" | grep -qE 'psql.*prod|DROP TABLE|rm -rf /'; then
  echo "Bloqueado: comando toca produção ou é destrutivo. Use o ambiente de staging." >&2
  exit 2   # código 2 = bloqueia a ferramenta e devolve o stderr ao modelo
fi
exit 0
```

**Por que funciona.** Um hook é executado pelo Claude Code, não decidido pelo
modelo. Ele acontece **sempre**. A regra vale a pena decorar:

> O que precisa acontecer toda vez vira **hook**.
> O que depende de julgamento fica no **prompt**.

Detalhes e a lista de eventos: [17](17-hooks-permissoes-seguranca.md).

---

## 7. Subagente para não poluir o contexto

**Problema.** Você pede "descubra onde ficam todas as chamadas ao serviço de
pagamento" e a sua conversa recebe 4 mil linhas de resultado de busca que
você nunca mais vai olhar.

**Solução.** `.claude/agents/investigador.md`:

```markdown
---
name: investigador
description: Faz buscas amplas e leituras exploratórias no repositório e devolve só a conclusão. Use quando a resposta exigir varrer muitos arquivos.
tools: Read, Grep, Glob
model: sonnet
effort: low
---

Você investiga e resume. Nunca edite arquivo nenhum.

Devolva no máximo 20 linhas:
- a resposta direta à pergunta, primeiro
- a lista de `caminho:linha` que a sustenta
- o que você procurou e NÃO achou (isso costuma valer mais que o que achou)

Se a pergunta for ambígua, escolha a leitura mais provável, responda, e diga
em uma linha qual leitura você escolheu.
```

Na conversa:

```
@investigador onde o valor do frete é calculado, e quantos lugares diferentes
fazem esse cálculo?
```

**Por que funciona.** O subagente tem **janela de contexto própria**. As 4 mil
linhas de busca ficam lá; para a sua conversa volta só o resumo de 20 linhas.
Além disso, `tools: Read, Grep, Glob` garante, por construção, que ele não
edita nada — não é uma promessa no prompt, é uma restrição do arnês.

---

## 8. Servidor MCP em 40 linhas

**Problema.** Você tem uma API interna e quer que o agente a use sem você
colar `curl` toda vez.

**Solução.** Com o SDK oficial (`pip install mcp`):

```python
# mcp_estoque.py
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("estoque")
BASE = "https://estoque.interno.empresa.com/v1"

@mcp.tool()
def consultar_saldo(sku: str) -> str:
    """Consulta o saldo em estoque de um SKU.

    Use sempre que a pergunta envolver disponibilidade, quantidade em
    estoque ou se um produto pode ser vendido. Nunca responda de memória:
    o saldo muda a cada minuto.

    Args:
        sku: código do produto, ex.: 'CAM-AZ-M'.
    """
    r = httpx.get(f"{BASE}/saldo/{sku}", timeout=10)
    if r.status_code == 404:
        return f"Erro: SKU '{sku}' não existe. Confira o código."
    r.raise_for_status()
    d = r.json()
    return f"{sku}: {d['disponivel']} disponíveis, {d['reservado']} reservados"

@mcp.tool()
def listar_baixo_estoque(limite: int = 10) -> str:
    """Lista SKUs abaixo do ponto de reposição, do mais crítico ao menos.

    Args:
        limite: quantos SKUs retornar. Padrão 10, máximo 100.
    """
    limite = min(max(limite, 1), 100)
    r = httpx.get(f"{BASE}/baixo-estoque", params={"limite": limite}, timeout=10)
    r.raise_for_status()
    itens = r.json()["itens"]
    if not itens:
        return "Nenhum SKU abaixo do ponto de reposição."
    return "\n".join(f"{i['sku']}: {i['disponivel']} (mínimo {i['minimo']})" for i in itens)

if __name__ == "__main__":
    mcp.run()
```

Registre em `.mcp.json`, na raiz do projeto:

```json
{
  "mcpServers": {
    "estoque": { "command": "python3", "args": ["mcp_estoque.py"] }
  }
}
```

Confira com `/mcp` — deve aparecer `connected`. Depois:

```
quais produtos estão para acabar? e o CAM-AZ-M, tem saldo para 30 unidades?
```

**Por que funciona.** MCP é o "USB-C das ferramentas": você escreve o servidor
uma vez e ele serve o Claude Code, o app de desktop, o seu próprio agente e
qualquer outro cliente MCP. A versão **sem nenhuma dependência**, com o
protocolo cru, está no [projeto-modelo](07-projeto-modelo/mcp_tarefas.py).

**Repare no detalhe que decide tudo:** os docstrings dizem *quando* chamar,
não só o que a função faz. Descrição sem gatilho = ferramenta ignorada.

---

## 9. O laço agêntico em 30 linhas de Python

**Problema.** Você quer entender o que o Claude Code faz por dentro, ou
construir o seu próprio agente.

**Solução.**

```python
# laco.py  —  pip install anthropic ; export ANTHROPIC_API_KEY=...
import json, subprocess, anthropic

FERRAMENTAS = [{
    "name": "shell",
    "description": (
        "Executa um comando de shell no diretório atual e devolve stdout+stderr. "
        "Use para inspecionar o sistema (ls, cat, git, ps). Não use para comandos "
        "interativos nem para nada destrutivo."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"comando": {"type": "string", "description": "o comando"}},
        "required": ["comando"],
    },
}]

def shell(comando: str) -> tuple[str, bool]:
    p = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=60)
    saida = (p.stdout + p.stderr)[:4000] or "(sem saída)"
    return saida, p.returncode != 0

cliente = anthropic.Anthropic()
mensagens = [{"role": "user", "content": "quantos arquivos .py existem aqui, e qual é o maior?"}]

for _ in range(10):                                   # o limite de voltas não é opcional
    r = cliente.messages.create(
        model="claude-opus-5", max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=FERRAMENTAS, messages=mensagens,
    )
    if r.stop_reason != "tool_use":                   # única condição de parada normal
        print("".join(b.text for b in r.content if b.type == "text"))
        break

    mensagens.append({"role": "assistant", "content": r.content})   # o content INTEIRO
    resultados = []
    for b in r.content:
        if b.type == "tool_use":
            print(f"  → {b.input['comando']}")
            texto, erro = shell(**b.input)
            resultados.append({"type": "tool_result", "tool_use_id": b.id,
                               "content": texto, "is_error": erro})
    mensagens.append({"role": "user", "content": resultados})       # TODOS numa mensagem só
```

```bash
python3 laco.py
```
```
  → ls *.py | wc -l
  → ls -S *.py | head -1
Há 7 arquivos .py neste diretório. O maior é laco.py, com 1,8 KB.
```

**Por que funciona.** É literalmente tudo o que um agente é. Quatro detalhes
que separam este código de um que quebra em produção:

| Detalhe | Se você errar |
|---|---|
| guardar `r.content` inteiro | perde os blocos de `thinking` e `tool_use`; o próximo turno quebra |
| todos os `tool_result` numa mensagem só | ensina o modelo a parar de pedir ferramentas em paralelo |
| `is_error=True` em vez de exceção | o agente morre no primeiro comando que falha em vez de se corrigir |
| limite de voltas | um agente em ciclo queima créditos até o teto da conta |

⚠️ **Este exemplo dá shell irrestrito ao modelo.** Rode em contêiner
descartável, nunca na sua máquina de trabalho.

---

## 10. Claude Code como comando de shell

**Problema.** Você quer usar o agente dentro de um pipeline, não numa conversa.

**Solução — modo headless (`-p`):**

```bash
# resumo do dia, direto para o Slack
git log --since=yesterday --oneline \
  | claude -p --bare "resuma em 3 bullets, em português, para um gerente não-técnico" \
  | curl -sS -X POST -H 'Content-type: application/json' \
      --data @- "$SLACK_WEBHOOK"
```

**Saída estruturada, validada por schema:**

```bash
claude -p --json-schema '{
  "type": "object",
  "properties": {
    "severidade": {"type": "string", "enum": ["baixa", "media", "alta", "critica"]},
    "componente": {"type": "string"},
    "resumo":     {"type": "string"}
  },
  "required": ["severidade", "componente", "resumo"],
  "additionalProperties": false
}' "classifique este erro: $(cat /var/log/app/erro.log)" > triagem.json

jq -r .severidade triagem.json
```

**Com teto de gasto e de voltas:**

```bash
claude -p --max-turns 5 --max-budget-usd 0.50 --output-format json \
  "verifique se o README está desatualizado em relação ao código" \
  | jq -r '.result'
```

**Por que funciona.** `--json-schema` devolve JSON **validado**, não texto
para você tentar extrair com regex. `--bare` pula hooks, plugins e
`CLAUDE.md`, então parte rápido e sem depender da configuração da máquina —
exatamente o que se quer em CI. `--max-budget-usd` é a diferença entre um job
que custa centavos e um que custa o orçamento do mês.

---

## 11. **Produção:** triagem de issues no CI

**Problema.** Um repositório aberto recebe 40 issues por semana. Alguém gasta
duas horas rotulando.

**Solução.** `.github/workflows/triagem.yml`:

```yaml
name: Triagem de issues
on:
  issues:
    types: [opened]

permissions:
  issues: write
  contents: read

jobs:
  triar:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - name: Instalar Claude Code
        run: curl -fsSL https://claude.ai/install.sh | bash

      - name: Classificar
        id: classificar
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          CORPO: ${{ github.event.issue.body }}
          TITULO: ${{ github.event.issue.title }}
        run: |
          ~/.local/bin/claude -p --bare \
            --max-turns 8 --max-budget-usd 0.30 \
            --allowedTools "Read" "Grep" "Glob" \
            --json-schema '{
              "type":"object",
              "properties":{
                "tipo":       {"type":"string","enum":["bug","feature","duvida","docs","spam"]},
                "area":       {"type":"string"},
                "duplicada":  {"type":"boolean"},
                "arquivos":   {"type":"array","items":{"type":"string"}},
                "justificativa": {"type":"string"}
              },
              "required":["tipo","area","duplicada","arquivos","justificativa"],
              "additionalProperties": false
            }' \
            "Classifique esta issue. Procure no código quais arquivos são
             prováveis responsáveis (campo arquivos, no máximo 3, no formato
             caminho:linha). Não invente caminho: só liste o que você leu.

             Título: $TITULO
             Corpo: $CORPO" > /tmp/triagem.json
          echo "tipo=$(jq -r .tipo /tmp/triagem.json)" >> "$GITHUB_OUTPUT"
          echo "area=$(jq -r .area /tmp/triagem.json)" >> "$GITHUB_OUTPUT"

      - name: Rotular e comentar
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue edit ${{ github.event.issue.number }} \
            --add-label "${{ steps.classificar.outputs.tipo }}" \
            --add-label "area:${{ steps.classificar.outputs.area }}"
          jq -r '"Triagem automática:\n\n- **Tipo:** \(.tipo)\n- **Área:** \(.area)\n- **Possíveis arquivos:** \(.arquivos | join(", "))\n\n\(.justificativa)\n\n_Classificação automática — corrija os rótulos se estiver errada._"' \
            /tmp/triagem.json | gh issue comment ${{ github.event.issue.number }} --body-file -
```

**Por que funciona em produção, e não só na demo:**

- **`--allowedTools "Read" "Grep" "Glob"`** — somente leitura. Uma issue é
  **entrada de terceiro não confiável**; sem essa restrição, o corpo da issue
  vira um vetor de injeção de prompt com acesso a `Bash`. Isto não é
  paranoia: é a superfície de ataque número um de agentes em CI.
- **`--max-budget-usd 0.30`** — 40 issues/semana × US$ 0,30 é um teto
  conhecido. Sem ele, uma issue com 200 KB de log pode custar dólares.
- **`--json-schema`** — o passo seguinte é `jq`, não parsing frágil.
- **"não invente caminho"** — a instrução mais importante do prompt. Sem ela,
  o campo `arquivos` vem plausível e errado, que é pior que vazio.
- **"corrija os rótulos se estiver errada"** — o humano continua no laço, e o
  comentário assume isso em vez de fingir autoridade.

---

## 12. **Produção:** migração de 500 arquivos

**Problema.** Trocar de biblioteca de datas (`moment` → `date-fns`) em 500
arquivos. Manual leva semanas; um `sed` não entende os casos irregulares.

**Solução — três fases. Não pule nenhuma.**

**Fase 1: medir, com plan mode.**

```bash
claude --permission-mode plan
```
```
levante o escopo da migração de moment para date-fns:
- quantos arquivos importam moment
- quais padrões de uso aparecem, e quantas vezes cada um
- quais são os 5 casos que NÃO têm equivalente direto em date-fns
- se existe teste cobrindo cada padrão

não proponha solução ainda. só o levantamento, em tabela.
```

**Fase 2: o piloto, à mão, num arquivo difícil.**

```
migre APENAS src/relatorios/consolidado.ts, que é o caso mais complicado da
tabela. rode os testes desse arquivo. quando terminar, escreva o que você
aprendeu em docs/MIGRACAO-DATAS.md: os padrões de substituição que
funcionaram e as armadilhas.
```

Esse `docs/MIGRACAO-DATAS.md` é o ativo mais valioso da migração: vira o
briefing dos 499 arquivos restantes.

**Fase 3: o leque.**

```
/batch migre os arquivos restantes de moment para date-fns, seguindo
exatamente os padrões de docs/MIGRACAO-DATAS.md. um PR por diretório de
primeiro nível. cada PR precisa ter a suíte verde antes de abrir.
```

O `/batch` decompõe em 5–30 unidades independentes, roda cada uma num
**worktree git isolado** com um subagente próprio, e abre um PR por unidade.

**Por que a ordem importa mais que a ferramenta.**

Quem pula direto para a fase 3 recebe 30 PRs escritos com 30 interpretações
diferentes do problema, e revisar isso custa mais que a migração manual. A
fase 2 existe para **transformar julgamento em documento** antes de
paralelizar. É o mesmo motivo pelo qual um humano faria um piloto.

E o isolamento em worktree não é detalhe: 30 subagentes editando a mesma
árvore de arquivos se atropelam. Um worktree por unidade é o que torna o
paralelismo real em vez de teatral.

**Custo, sendo honesto.** Uma migração desse tamanho consome tokens de forma
significativa — na ordem de dezenas de dólares em API, ou uma boa fatia dos
limites de um plano Max. Rode `/usage` depois da fase 2 e multiplique pelo
número de unidades antes de mandar a fase 3.

---

## Autoteste

1. No exemplo 2, por que o teste é pedido em um turno separado da correção?
2. Qual é a vantagem concreta do `!` sobre pedir "rode `npm test`"?
3. Por que o corpo de uma skill não custa contexto e uma seção do `CLAUDE.md`
   custa?
4. Reescreva "sempre rode o lint depois de editar" como hook. Qual evento?
5. No exemplo 7, qual linha do frontmatter garante que o subagente não edita
   arquivos — e por que isso é mais forte que pedir no prompt?
6. No exemplo 8, o que a frase "nunca responda de memória: o saldo muda a cada
   minuto" faz de diferente?
7. No exemplo 9, o que acontece se você guardar só o texto da resposta em vez
   de `r.content` inteiro?
8. No exemplo 11, qual é a razão de segurança para `--allowedTools "Read"
   "Grep" "Glob"`? Que ataque isso previne?
9. No exemplo 12, o que se perde ao pular a fase 2?
10. Cite duas flags que você usaria em **qualquer** invocação de `claude -p`
    dentro de CI, e por quê.
