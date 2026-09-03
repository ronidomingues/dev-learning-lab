# Projeto-modelo — `agente-tarefas`

**Nível:** intermediário · **Testado em:** Python 3.10.12, Claude Code 2.1.231,
Ubuntu 22.04 (Linux 6.8), em 13/08/2026.

Uma aplicação pequena e **inteira**: um gerenciador de tarefas exposto a um
agente de IA por duas vias diferentes, com o mesmo domínio nas duas.

O que ele existe para ensinar, em uma frase: **o domínio é um só; o que muda
é o arnês.**

```
                       ┌──────────────────────┐
       .mcp.json  ───▶ │  Claude Code (arnês) │──┐
                       └──────────────────────┘  │   JSON-RPC 2.0
                                                 │   sobre stdio
                       ┌──────────────────────┐  │
  agente_minimo.py ───▶│  seu laço (arnês)    │──┼──▶ mcp_tarefas.py
       (Claude API)    └──────────────────────┘  │      ├── camada MCP
                                                 │      └── domínio ──▶ SQLite
                       ┌──────────────────────┐  │
     teste_mcp.py ────▶│  cliente de teste    │──┘
                       └──────────────────────┘
```

---

## Pré-requisitos

| Item | Versão mínima | Verificar com | Obrigatório? |
|---|---|---|---|
| Python | 3.10 | `python3 --version` | sim |
| Claude Code | 2.1.0 | `claude --version` | só para a parte MCP |
| `anthropic` (pip) | 0.60 | `python3 -c "import anthropic"` | só para `agente_minimo.py` |
| `ANTHROPIC_API_KEY` | — | `echo $ANTHROPIC_API_KEY` | só para `agente_minimo.py` |

Nada além da biblioteca padrão é necessário para o servidor MCP e para os
testes. Isso é deliberado: dependência a menos é uma variável a menos quando
algo quebra.

---

## Rodar

### 1. Os testes (nem rede, nem chave, nem custo)

```bash
cd 07-projeto-modelo
python3 teste_mcp.py
```

Saída esperada — 19 verificações, todas `ok`:

```
handshake
  ok   serverInfo.name = tarefas
  ok   declara capability tools
catálogo
  ok   quatro ferramentas publicadas
  ok   detalhe interno _fn não vaza no protocolo
  ok   toda ferramenta tem descrição
banco vazio
  ok   lista vazia
caminho feliz
  ok   criar_tarefa não é erro
  ok   id 1 atribuído
  ok   duas tarefas listadas
  ok   concluir_tarefa #1
  ok   filtro por status funciona
  ok   estatísticas corretas
erros de domínio viram isError=True, não erro de protocolo
  ok   concluir duas vezes não é erro JSON-RPC
  ok   isError=True
  ok   mensagem explica o motivo (o modelo precisa ler isso)
  ok   prioridade inválida rejeitada
erros de protocolo viram erro JSON-RPC
  ok   ferramenta inexistente = -32602
  ok   argumento desconhecido = -32602
  ok   método desconhecido = -32601

Todos os testes passaram.
```

Se der `FALHA` em qualquer linha, pare aqui: o resto não vai funcionar.

### 2. Conversar com o servidor na unha (opcional, mas faça uma vez)

MCP não tem mágica. É uma linha de JSON entrando e uma saindo:

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | python3 mcp_tarefas.py
```

Você verá duas linhas de JSON. A segunda é o catálogo que o modelo lê para
decidir o que chamar. **É esse texto que determina se sua ferramenta será
usada corretamente ou ignorada.**

### 3. Com o Claude Code

```bash
cd 07-projeto-modelo
claude
```

Na sessão:

```
/mcp
```

`tarefas` deve aparecer como `connected`. Se aparecer `failed`, rode
`claude --debug=mcp` e leia o erro — quase sempre é caminho de `python3`.

Então peça, em português normal:

```
anote com prioridade alta: revisar o contrato do fornecedor
o que está aberto?
gere o relatório
```

O terceiro pedido dispara a skill `.claude/skills/relatorio/` — repare que ela
**não** estava no contexto até ser necessária.

### 4. Com o seu próprio agente

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install anthropic
python3 agente_minimo.py "quais tarefas estão abertas?"
```

O `stderr` mostra cada volta do laço:

```
  [volta 1] listar_tarefas({"status": "aberta"})
```

Mesmas ferramentas, mesmo banco, outro arnês.

### Zerar

```bash
rm -f tarefas.db
```

---

## Estrutura, comentada

```
07-projeto-modelo/
├── mcp_tarefas.py       ── servidor MCP + domínio, ZERO dependências
│                           ├─ funções de domínio: não sabem o que é MCP
│                           ├─ lista FERRAMENTAS: nome, descrição, schema
│                           └─ tratar(): despacho JSON-RPC 2.0
├── teste_mcp.py         ── teste de CONTRATO: sobe o servidor como
│                           subprocesso e fala o protocolo de verdade
├── agente_minimo.py     ── o laço agêntico escrito à mão, ~120 linhas
├── CLAUDE.md            ── regras do projeto, carregadas toda sessão
├── .mcp.json            ── registra o servidor para o Claude Code
└── .claude/
    ├── settings.json    ── permissões + hook PostToolUse (roda os testes)
    ├── skills/
    │   └── relatorio/
    │       └── SKILL.md ── procedimento carregado sob demanda
    └── agents/
        └── revisor-de-ferramentas.md  ── subagente somente-leitura
```

---

## O que cada decisão de projeto ensina

### Domínio e protocolo em camadas separadas

`listar_tarefas()` não importa `json` nem sabe o que é JSON-RPC. Consequência
prática: o mesmo código serve o MCP, o `agente_minimo.py` e um `main()` de
linha de comando, sem adaptador. Se o seu domínio precisa de um `if
chamado_por_mcp:` em algum lugar, a fronteira está no lugar errado.

### Protocolo escrito à mão

O SDK oficial (`pip install mcp`) é o certo em produção. Aqui ele seria uma
caixa-preta em cima de outra. As 60 linhas de `tratar()` mostram que MCP é
JSON-RPC 2.0 com quatro métodos que importam: `initialize`, `tools/list`,
`tools/call`, `ping`. Depois de ver isso, depurar um servidor MCP que "não
conecta" deixa de ser adivinhação.

### `isError: true` em vez de exceção

A distinção mais importante do arquivo, e a que quase todo tutorial erra:

| Situação | Resposta | Por quê |
|---|---|---|
| Ferramenta não existe, argumento desconhecido | **erro JSON-RPC** (`-32602`) | O cliente montou a chamada errado. É bug do arnês, não do modelo. |
| Tarefa já concluída, prioridade inválida | **resultado com `isError: true`** | O modelo montou uma chamada válida com um argumento ruim. Ele precisa **ler** o motivo e tentar outra coisa. |

Um erro de protocolo aborta; um `isError: true` vira contexto. Por isso a
mensagem `"tarefa #1 não existe ou já está concluída"` é código de produção:
é literalmente o que o modelo lê para se corrigir. Trate mensagens de erro de
ferramenta como você trataria uma mensagem de erro de compilador.

### Descrições que dizem *quando*, não só *o quê*

Compare:

> ❌ `"Lista tarefas."`
> ✅ `"Lista as tarefas registradas. Use sempre antes de responder qualquer pergunta sobre o que está pendente (…) — nunca responda de memória."`

A primeira é ignorada quando o modelo "acha que já sabe". A segunda instala
um gatilho. Descrição de ferramenta é *prompt*, não documentação — e é o
fator isolado que mais mexe no comportamento do agente.

### Teste de contrato, não teste de unidade

`teste_mcp.py` não importa `mcp_tarefas`; ele **sobe o processo** e fala o
protocolo. É mais lento e é o que pega o que interessa: `_fn` vazando no
catálogo, `isError` no lugar errado, código JSON-RPC trocado — bugs que um
teste de unidade da função `criar_tarefa()` jamais veria.

### Hook em vez de instrução no prompt

`"sempre rode os testes depois de editar"` no `CLAUDE.md` é uma sugestão que o
modelo pode esquecer no meio de uma sessão longa. O hook `PostToolUse` roda os
testes de verdade, toda vez, porque quem executa é o Claude Code, não o
modelo. **Regra: o que precisa acontecer sempre vira hook; o que depende de
julgamento fica no prompt.**

### `deny` no `tarefas.db`

A regra `Read(./tarefas.db)` existe para forçar o caminho pelas ferramentas.
Sem ela, o modelo mais cedo ou mais tarde faz `sqlite3 tarefas.db "select *"` —
funciona, e demole a lição. Permissão aqui é pedagogia; em produção seria
para impedir que dados sensíveis entrem no contexto.

### Subagente somente-leitura

`revisor-de-ferramentas` recebe `tools: Read, Grep, Glob` e roda em `sonnet`.
Duas lições: o contexto dele é separado (a revisão não polui a sua conversa) e
**um revisor que pode editar deixa de ser revisor** — ele conserta em vez de
apontar, e você perde a lista de achados.

---

## O que projetos reais têm e tutoriais omitem — e está aqui

- **Tratamento de erro em duas categorias** (protocolo × domínio), acima.
- **Configuração fora do código**: `TAREFAS_DB` permite ao teste usar um banco
  descartável sem tocar no servidor.
- **Teste automatizado** que roda em qualquer máquina, sem rede e sem custo.
- **Idempotência**: `CREATE TABLE IF NOT EXISTS` a cada conexão; o servidor
  pode ser reiniciado a qualquer momento.
- **Limite de voltas** (`max_voltas=10`) no `agente_minimo.py`: sem isso, um
  agente que erra em ciclo queima créditos até o teto da conta.

---

## O que foi e o que não foi executado

**Executado e verificado em 13/08/2026** (Python 3.10.12, Linux):

- `python3 teste_mcp.py` — 19 verificações, todas passando. A saída mostrada
  acima é a saída real.
- Diálogo JSON-RPC manual (`initialize` + `tools/list`).

**Não executado, declarado como tal:**

- `agente_minimo.py` — exige `ANTHROPIC_API_KEY` e consome créditos.
- A sessão do Claude Code (`/mcp`, skill, hook, subagente) — exige assinatura
  ativa. As configurações seguem os esquemas da documentação oficial
  consultada em 13/08/2026 (ver [95-referencias.md](../95-referencias.md)),
  mas o comportamento em tela não foi verificado aqui.

---

## Exercícios

1. Apague a palavra `sempre` da descrição de `listar_tarefas`, reinicie a
   sessão e pergunte duas vezes seguidas "o que está aberto?". Observe se a
   segunda resposta vem de memória.
2. Faça `concluir_tarefa` levantar apenas `raise ValueError("falhou")`.
   Peça ao agente para concluir uma tarefa já concluída e veja quantas voltas
   ele desperdiça sem a mensagem explicativa.
3. Adicione `remover_tarefa`. Rode `@revisor-de-ferramentas` sobre ela antes
   de considerar pronta.
4. Troque o hook `PostToolUse` por `PreToolUse` com `matcher: "Bash"` que
   bloqueia qualquer comando contendo `sqlite3`. Compare com a regra `deny`.

---

Voltar ao [00-MAPA.md](../00-MAPA.md) · seguir para
[70-pratica.md](../70-pratica.md).
