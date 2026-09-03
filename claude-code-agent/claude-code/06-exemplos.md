# 06 · Exemplos — 14 receitas completas

> **Nível:** iniciante → avançado · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231
> Todo arquivo aqui está **completo**. Nada de `...` escondendo a parte que importa.
> Os exemplos 1, 2, 12 e 13 foram **executados** nesta máquina; os demais estão marcados.

Formato de cada exemplo: **problema → solução → por que funciona**.

---

## 1 · Perguntar sem risco de alterar nada — *executado*

**Problema.** Você caiu num repositório desconhecido e precisa entender o que ele faz,
sem correr o risco de alterar arquivo nenhum.

**Solução.**

```bash
cd /caminho/do/repo
claude --permission-mode plan
```

```
mapeie este projeto: qual o ponto de entrada, quais são os módulos principais,
e qual comando roda os testes. responda em no máximo 10 linhas.
```

Ou, sem abrir sessão:

```bash
claude -p "responda apenas com a palavra: pronto"
```

Saída real desta máquina em 13/08/2026:

```
pronto
```

**Por que funciona.** `plan` deixa o agente só ler. Ele explora com `Glob`/`Grep`/`Read` e
não pode escrever nem executar. É o modo certo para código de terceiros, cliente novo ou
qualquer repositório em que um `Write` acidental teria consequência.

---

## 2 · Contar e medir sem abrir sessão — *executado*

**Problema.** Você quer um número, não uma conversa, e quer usá-lo num script.

**Solução.**

```bash
claude -p "Quantos blocos test( ) existem em test/tarefas.test.js? Responda so o numero." \
  --allowedTools "Read,Bash(grep *)" \
  --output-format json
```

Trecho **real** da resposta (projeto-modelo, 13/08/2026):

```json
{
  "is_error": false,
  "num_turns": 2,
  "session_id": "84a5e3a3-ca87-4178-a64c-414d8def8b6c",
  "total_cost_usd": 0.1906005,
  "usage": { "input_tokens": 4, "cache_read_input_tokens": 47811, "output_tokens": 147 }
}
```

Para extrair só o texto:

```bash
claude -p "…" --output-format json | jq -r '.result'
```

**Por que funciona.** `--output-format json` devolve metadados junto com a resposta: custo,
turnos, ID da sessão. Em automação, isso é o que permite medir e limitar. Repare que a
pergunta trivial custou **US$ 0,19** — quase tudo pago pelo contexto arrastado, não pela
resposta. Ver [`80`](80-custos-e-licencas.md).

---

## 3 · Fazer o agente consertar o próprio erro

**Problema.** Um teste falha e você não quer investigar.

**Solução.**

```
rode `npm test`. um teste está falhando. descubra a causa raiz, conserte,
e rode de novo até passar. não altere o teste para fazê-lo passar —
se o teste estiver errado, me diga em vez de mudá-lo.
```

**Por que funciona.** Três coisas fazem este prompt funcionar onde "conserta o teste" falha:

1. Existe **critério de sucesso automático** (a suíte passa ou não).
2. A frase "não altere o teste" fecha a saída fácil. Sem ela, o agente às vezes ajusta a
   asserção para o valor errado — tecnicamente "passou", semanticamente um desastre.
3. "me diga em vez de mudá-lo" dá uma saída legítima para o caso em que o teste é que está errado.

---

## 4 · Regra de projeto que o agente respeita de verdade

**Problema.** Você repete "use `node:test`, não instale Jest" toda sessão.

**Solução — as três camadas, em ordem crescente de força.**

Camada 1, `CLAUDE.md` (contexto — ele *deve* seguir):

```markdown
## Convenções
- Testes com `node:test`. **Não** adicione Jest, Vitest ou Mocha.
- Zero dependências de produção. Antes de sugerir um pacote, pergunte.
```

Camada 2, `.claude/settings.json` (permissão — ele *não consegue* rodar):

```json
{
  "permissions": {
    "deny": ["Bash(npm install *)", "Bash(npm i *)", "Bash(yarn add *)", "Bash(pnpm add *)"]
  }
}
```

Camada 3, hook (código — roda sempre, mesmo que o modelo tente contornar):

```bash
#!/usr/bin/env bash
# .claude/hooks/sem-dependencias.sh — PreToolUse, matcher Edit|Write
set -euo pipefail
entrada="$(cat)"
caminho="$(printf '%s' "$entrada" | jq -r '.tool_input.file_path // ""')"
conteudo="$(printf '%s' "$entrada" | jq -r '.tool_input.content // .tool_input.new_string // ""')"

if [[ "$(basename "$caminho")" == "package.json" ]] && \
   printf '%s' "$conteudo" | jq -e '.dependencies | length > 0' >/dev/null 2>&1; then
  jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",
    permissionDecisionReason:"Este projeto e zero-dependencia. Discuta antes de adicionar."}}'
  exit 0
fi
exit 0
```

**Por que funciona.** Esta é a lição central do curso, em forma de receita:
**`CLAUDE.md` pede, permissão restringe, hook obriga.** Escolha a camada pela consequência
do erro. Regra de estilo? Camada 1 basta. Regra que, violada, quebra a produção? Camada 3.

---

## 5 · Migração mecânica em muitos arquivos

**Problema.** Trocar `require()` por `import` em 40 arquivos, sem quebrar nada.

**Solução.**

```
/plan converter todos os arquivos de src/ de CommonJS para ESM.

restrições:
- um arquivo por vez, rodando `npm test` depois de cada um
- se um arquivo quebrar a suíte, reverta SÓ ele e continue nos outros
- ao final, me dê a lista dos que você não conseguiu converter e por quê
```

**Por que funciona.** Três decisões salvam esta tarefa:

- **Modo plano primeiro**: você vê a lista de arquivos antes de qualquer escrita.
- **Um por vez com teste no meio**: transforma um "deu errado" difuso num arquivo específico.
- **"reverta só ele e continue"**: sem isso, o agente trava no primeiro problema, ou pior,
  força a conversão quebrando o teste.

Para escala maior (centenas de arquivos), `/batch` decompõe o trabalho em worktrees git
paralelos ([`22`](22-git-github-e-ci.md)).

---

## 6 · Revisão de código antes do PR

**Problema.** Você quer uma segunda opinião antes de pedir revisão humana.

**Solução.** Dentro da sessão:

```
/code-review high
```

Ou, num script, sem sessão:

```bash
#!/usr/bin/env bash
# revisar.sh — revisão de segurança de um PR do GitHub
set -euo pipefail
gh pr diff "$1" | claude -p \
  --append-system-prompt "Você é um engenheiro de segurança. Aponte só vulnerabilidades reais e exploráveis, com arquivo:linha. Se não houver nenhuma, diga 'nenhuma'." \
  --output-format json | jq -r '.result'
```

```bash
bash revisar.sh 123
```

**Por que funciona.** O diff chega **canalizado**, então o agente não precisa de permissão
de `Bash` nem de acesso ao repositório — a superfície de risco encolhe. E
`--append-system-prompt` muda o papel sem reescrever o prompt de sistema inteiro.

**Não executado aqui** (exige um PR real do GitHub).

---

## 7 · Portão de qualidade no CI

**Problema.** Toda alteração num arquivo sensível deveria passar por uma checagem que
nenhum linter expressa.

**Solução — GitHub Actions:**

```yaml
# .github/workflows/revisao-claude.yml
name: Revisão automática
on:
  pull_request:
    paths: ["src/**"]

jobs:
  revisar:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Instalar Claude Code
        run: curl -fsSL https://claude.ai/install.sh | bash

      - name: Revisar o diff
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          PATH: ${{ env.PATH }}:/home/runner/.local/bin
        run: |
          git diff origin/${{ github.base_ref }}...HEAD -- src/ > /tmp/diff.txt
          claude --bare -p "Analise este diff. Responda no formato JSON pedido." \
            --max-budget-usd 1.00 \
            --max-turns 5 \
            --output-format json \
            --json-schema '{
              "type":"object",
              "properties":{
                "aprovado":{"type":"boolean"},
                "problemas":{"type":"array","items":{
                  "type":"object",
                  "properties":{"arquivo":{"type":"string"},"linha":{"type":"integer"},"descricao":{"type":"string"}},
                  "required":["arquivo","linha","descricao"]}}},
              "required":["aprovado","problemas"]
            }' < /tmp/diff.txt | jq '.structured_output' > /tmp/resultado.json
          cat /tmp/resultado.json
          test "$(jq -r '.aprovado' /tmp/resultado.json)" = "true"
```

**Por que funciona.**

- `--bare` ignora hooks, skills e MCP da máquina do runner: **mesmo resultado em qualquer runner**.
- `--json-schema` garante saída estruturada, validada antes de chegar a você — não há
  "parsear a resposta do modelo com regex".
- `--max-budget-usd` e `--max-turns` são o freio de emergência. **Nunca** rode um agente em
  CI sem os dois.
- O `test` final transforma o veredito em código de saída, que é o que o CI entende.

**Não executado aqui** (exige repositório no GitHub com chave configurada).

---

## 8 · Subagente que revisa sem poder editar

**Problema.** Você quer uma revisão isolada, e quer garantia de que o revisor não vai
"consertar em silêncio" o que deveria apontar.

**Solução.** `.claude/agents/revisor.md`:

```markdown
---
name: revisor
description: Revisa mudanças procurando bug de correção, não estilo. Use após qualquer alteração em src/.
tools: Read, Grep, Glob, Bash
disallowedTools: Edit, Write
model: sonnet
color: cyan
---

Você revisa código. Você **não edita arquivos**.

1. `git diff` para ver o que mudou.
2. Leia os arquivos tocados por inteiro, não só o diff.
3. Rode a suíte e reporte o resultado **real**.
4. Responda só neste formato:

VEREDITO: aprovado | aprovado com ressalvas | reprovado
ACHADOS:
1. [alta|média|baixa] arquivo:linha — problema. Correção: o que fazer.

Se não houver achado, escreva `ACHADOS: nenhum`. Não invente problema para parecer útil.
```

Uso: *"use o agente revisor para revisar o que mudou"*.

**Por que funciona.** Duas propriedades, ambas valiosas:

- **Contexto isolado**: o `git diff` inteiro e a leitura dos arquivos ficam no contexto do
  subagente. Só o veredito volta para a conversa principal.
- **Poder restrito**: `disallowedTools: Edit, Write` é garantia estrutural, não pedido.

Versão completa e executável em [`07-projeto-modelo/.claude/agents/revisor-api.md`](07-projeto-modelo/.claude/agents/revisor-api.md).

---

## 9 · Skill que impõe a ordem certa de trabalho

**Problema.** Toda vez que alguém adiciona um endpoint, a regra de negócio acaba vazando
para a camada HTTP — porque a pessoa (ou o agente) começa pelo roteador.

**Solução.** `.claude/skills/novo-endpoint/SKILL.md`:

```markdown
---
name: novo-endpoint
description: Adiciona endpoint seguindo a arquitetura do projeto — domínio primeiro, HTTP por último.
argument-hint: [método] [rota] [o que faz]
disable-model-invocation: true
allowed-tools: Read, Edit, Bash(npm test)
---

Adicione o endpoint: **$ARGUMENTS**

1. Implemente no domínio (`src/tarefas.js`). Erros de entrada → `ErroDeValidacao`.
2. Teste do domínio: caso feliz, caso inválido, e fronteira se houver limite.
3. Só agora a camada HTTP (`src/servidor.js`). Zero `if` de negócio.
4. Teste HTTP: um status de sucesso e um de erro.
5. `npm test`. Se falhar, conserte antes de responder.
6. Documente a rota no README.

Ao final mostre apenas: rotas novas, testes adicionados, contagem da suíte.
```

Uso: `/novo-endpoint PATCH /tarefas/:id alterar o título`

**Por que funciona.** O procedimento fica **fora** do `CLAUDE.md`: ele só entra em contexto
quando invocado, então pode ser detalhado sem custar nada nas outras sessões.
`disable-model-invocation: true` garante que só roda quando você pede.

---

## 10 · Hook que devolve a falha ao agente — *executado*

**Problema.** O agente edita, quebra a suíte, e só você descobre — depois.

**Solução.** `.claude/hooks/testa-apos-edicao.sh` (versão completa em
[`07-projeto-modelo/.claude/hooks/testa-apos-edicao.sh`](07-projeto-modelo/.claude/hooks/testa-apos-edicao.sh)):

```bash
#!/usr/bin/env bash
set -uo pipefail
entrada="$(cat)"
caminho="$(printf '%s' "$entrada" | jq -r '.tool_input.file_path // ""')"
case "$caminho" in *"/src/"*.js|*"/test/"*.js) ;; *) exit 0 ;; esac

cd "${CLAUDE_PROJECT_DIR:-.}"
saida="$(node --test 2>&1)"; codigo=$?
if [ $codigo -ne 0 ]; then
  { echo "A suite quebrou depois de editar $caminho. Conserte antes de seguir."
    printf '%s\n' "$saida" | tail -40; } >&2
  exit 2
fi
exit 0
```

Registro em `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/testa-apos-edicao.sh",
        "args": [],
        "timeout": 120,
        "statusMessage": "rodando a suíte de testes"
      }]
    }]
  }
}
```

**Executado nesta máquina.** Com a prioridade padrão trocada de propósito em
`src/tarefas.js`, o hook saiu com código 2 e devolveu ao agente:

```
A suite quebrou depois de editar .../src/tarefas.js. Conserte antes de seguir.
--- saida do node --test (ultimas 40 linhas) ---
✖ cria tarefa com valores padrão (3.81658ms)
  AssertionError: Expected values to be strictly equal:
  'baixa' !== 'media'
ℹ pass 19
ℹ fail 1
```

**Por que funciona.** O `exit 2` faz o `stderr` ir **para o Claude**, não para você. O laço
de verificação fecha dentro do turno: ele quebra, vê que quebrou, conserta. É a mudança de
maior impacto que se pode fazer num repositório, e custa 15 linhas de bash.

---

## 11 · Cortar o custo de uma sessão pela metade

**Problema.** `/usage` mostra gasto alto e você não sabe de onde vem.

**Solução.**

```
/context all
```

Leia a grade. Os suspeitos, em ordem de frequência:

| O que aparece grande | Correção |
|---|---|
| Definições de ferramentas MCP | `/mcp` e desabilite servidores não usados; prefira a CLI (`gh`, `aws`) |
| `CLAUDE.md` gigante | Mova procedimento para skills, detalhe para `.claude/rules/` com `paths:` |
| Arquivos lidos de tarefas antigas | `/clear` |
| Histórico longo da mesma tarefa | `/compact foque nas decisões de API e nos testes` |
| Saída de comandos volumosos | Delegue a subagente, ou filtre num hook |

Filtrar saída num hook, antes de o agente ver:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{ "type": "command", "command": "~/.claude/hooks/filtrar-teste.sh" }]
    }]
  }
}
```

```bash
#!/usr/bin/env bash
# ~/.claude/hooks/filtrar-teste.sh — reescreve o comando para mostrar só falhas
entrada=$(cat)
cmd=$(echo "$entrada" | jq -r '.tool_input.command')
if [[ "$cmd" =~ ^(npm\ test|pytest|go\ test) ]]; then
  filtrado="$cmd 2>&1 | grep -A 5 -E '(FAIL|ERROR|error:|✖)' | head -100"
  jq -n --arg c "$filtrado" '{hookSpecificOutput:{hookEventName:"PreToolUse",
    permissionDecision:"allow",updatedInput:{command:$c}}}'
else
  echo '{}'
fi
```

**Por que funciona.** Um `npm test` de projeto grande cospe 10 mil linhas; 9.900 delas são
`✔`. O hook reescreve o comando **antes** de rodar, e o agente vê 100 linhas em vez de
10.000. A economia é de ordens de grandeza, não de percentual.

---

## 12 · Validar a própria configuração — *executado*

**Problema.** Você configurou hooks, skills e agentes, e nada acontece. Configuração de
agente falha em silêncio.

**Solução.** Rode o validador do projeto-modelo:

```bash
cd claude-code/07-projeto-modelo
npm run verificar
```

Saída **real** de 13/08/2026:

```
=== Verificação da configuração de Claude Code ===

  ok   arquivo presente: CLAUDE.md
  ok   .claude/settings.json é JSON válido
  ok   3 hook(s) de comando verificados
  ok   6 regra(s) de negação ativa(s)
  ok   agente válido: revisor-api
  ok   skill válida: checar-tudo
  ok   skill válida: novo-endpoint
  ok   CLAUDE.md com 32 linhas (limite recomendado: 200)
  ok   testes: 20 passaram, 0 falharam

17 verificação(ões) ok, 0 problema(s).
```

E, para o que o validador não cobre:

```bash
claude doctor    # instalação, settings inválidos, resultado do último update
```

**Por que funciona.** As cinco falhas silenciosas mais comuns — JSON inválido, hook sem
`chmod +x`, hook sem shebang, skill sem `description`, `name` de agente com maiúscula ou
`:` — todas produzem o mesmo sintoma ("o Claude ignora minha configuração") e nenhuma
produz mensagem de erro. Código-fonte do validador em
[`07-projeto-modelo/scripts/verificar-configuracao.mjs`](07-projeto-modelo/scripts/verificar-configuracao.mjs).

---

## 13 · Testar hooks sem abrir sessão — *executado*

**Problema.** Escrever hook às cegas é lento: você edita, abre sessão, tenta provocar o
evento, e não sabe se falhou o hook ou o gatilho.

**Solução.** Hooks recebem JSON no `stdin`. Você pode simular:

```bash
export CLAUDE_PROJECT_DIR="$PWD"

# 1. deve BLOQUEAR
echo '{"hook_event_name":"PreToolUse","tool_name":"Write",
       "tool_input":{"file_path":"/home/x/projeto/.env","content":"SEGREDO=1"}}' \
  | .claude/hooks/bloqueia-segredos.sh

# 2. deve DEIXAR PASSAR (saída vazia = sem decisão)
echo '{"hook_event_name":"PreToolUse","tool_name":"Edit",
       "tool_input":{"file_path":"'"$PWD"'/src/tarefas.js"}}' \
  | .claude/hooks/bloqueia-segredos.sh
```

Saída **real** do caso 1, em 13/08/2026:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Arquivo de segredo (/home/x/projeto/.env) e protegido pelo hook bloqueia-segredos.sh."
  }
}
```

O caso 2 não imprimiu nada e saiu com código 0 — exatamente o esperado: "sem decisão,
siga o fluxo normal de permissão".

**Por que funciona.** O contrato do hook é `stdin` → `stdout` + código de saída. Sendo um
contrato de processo, ele é testável como qualquer script. **Todo hook seu deveria ter esses
dois testes**: um que bloqueia e um que deixa passar. O segundo é o que pega o hook
paranoico que trava tudo.

---

## 14 · Caso real de produção — investigar um incidente

**Problema.** Erro 500 intermitente em produção desde ontem. Você tem logs, métricas e
o commit de ontem, mas nenhuma pista.

**Solução — a sequência que funciona na prática:**

```bash
# 1. dê o dado ANTES de abrir a sessão, filtrado — não deixe o agente caçar
grep -c "500" /var/log/app/*.log > /tmp/contagem.txt
grep -B2 -A20 "500" /var/log/app/app.log | head -200 > /tmp/amostra.txt
git log --since="2 days ago" --oneline > /tmp/commits.txt

claude
```

Dentro da sessão:

```
temos 500 intermitente em produção desde ontem ~14h.

@/tmp/contagem.txt @/tmp/amostra.txt @/tmp/commits.txt

antes de propor qualquer correção:
1. liste as 3 hipóteses mais prováveis, ordenadas, com a evidência de cada uma
2. para cada hipótese, diga que dado confirmaria ou descartaria ela
3. NÃO edite nada ainda
```

Depois de escolher a hipótese, e só então:

```
/plan corrigir a hipótese 2. inclua um teste que falharia com o bug presente.
```

**Por que funciona — e por que a ordem é essa:**

- **Dado filtrado, entregue pronto.** Um agente vasculhando logs de 2 GB gasta o contexto
  inteiro e acha menos que um `grep` seu. Você conhece o formato do log; ele não.
- **Hipóteses antes de correção.** Sem essa instrução, o agente conserta a primeira coisa
  suspeita que encontra. Em incidente, a primeira coisa suspeita quase nunca é a causa.
- **"que dado confirmaria ou descartaria"** força raciocínio falsificável em vez de
  narrativa plausível. É a pergunta que separa diagnóstico de chute bem escrito.
- **"inclua um teste que falharia com o bug presente"** garante que a correção é real:
  se o teste passa com e sem a correção, você não corrigiu nada.

**Não executado aqui** (não há incidente de produção para investigar).

---

## Tabela-resumo: qual receita para qual situação

| Situação | Exemplo |
|---|---|
| Repositório desconhecido | 1 |
| Preciso de um número num script | 2 |
| Teste falhando | 3 |
| Regra que ele ignora | 4 |
| Migração em muitos arquivos | 5, 7 |
| Revisão antes do PR | 6, 8 |
| Portão automático no CI | 7 |
| Tarefa ruidosa poluindo a sessão | 8, 11 |
| Procedimento repetitivo do time | 9 |
| Ele quebra a suíte e não percebe | 10 |
| Sessão cara demais | 11 |
| "Minha configuração não funciona" | 12, 13 |
| Incidente em produção | 14 |

---

## Autoteste

1. No exemplo 4, qual camada usar para "não instale dependências" num projeto onde isso é
   crítico, e por quê?
2. Por que canalizar o diff (exemplo 6) é melhor do que dar permissão de `Bash` ao agente?
3. Quais duas flags **nunca** devem faltar num agente rodando em CI?
4. No exemplo 8, o que `disallowedTools: Edit, Write` garante que o prompt não garantiria?
5. Explique por que o hook do exemplo 10 usa `exit 2` e não `exit 1`.
6. No exemplo 11, por que filtrar a saída **antes** do comando rodar é melhor que resumir depois?
7. Quais dois testes todo hook deveria ter, e o que o segundo pega?
8. No exemplo 14, por que exigir "que dado confirmaria ou descartaria" muda a qualidade da resposta?
