# 14 · Ferramentas — o que o agente pode fazer, e a que preço

> **Nível:** intermediário · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

Ferramenta é o que transforma um modelo de texto em agente. Este arquivo cobre o que existe,
o que cada uma custa em contexto e permissão, e **como o modelo escolhe** entre elas — porque
entender a escolha é o que permite influenciá-la.

---

## 1. Como uma ferramenta é apresentada ao modelo

Cada ferramenta entra no contexto como nome + descrição + esquema de argumentos. Isso tem
duas consequências que quase ninguém considera:

1. **Toda ferramenta disponível custa contexto, mesmo sem ser usada.** Um servidor MCP com
   40 ferramentas pode consumir dezenas de milhares de tokens em toda mensagem.
2. **A descrição é o que guia a escolha.** O modelo decide qual usar lendo a descrição. Uma
   ferramenta MCP mal descrita é ignorada, ou usada na hora errada — e a culpa parece ser
   do modelo.

Por isso o Claude Code **adia** as definições de ferramentas MCP por padrão: só os nomes
entram no contexto, e o esquema completo é carregado sob demanda pela ferramenta
`ToolSearch`. É uma otimização com um efeito colateral: uma chamada extra antes do uso.

---

## 2. Catálogo, agrupado por função

### Leitura e busca — baratas, sem permissão dentro do diretório

| Ferramenta | O que faz | Custo de contexto |
|---|---|---|
| `Read` | Lê arquivo (texto, imagem, PDF, notebook) | **Alto** — o conteúdo inteiro entra |
| `Glob` | Encontra arquivos por padrão (`src/**/*.ts`) | Baixo (só nomes) |
| `Grep` | Busca conteúdo com ripgrep | Baixo a médio (só as linhas que casam) |
| `LSP` | Ir para definição, referências, tipos | Baixo e **preciso** |

**O padrão que separa uso amador de uso profissional:** `Glob`/`Grep` primeiro para
localizar, `Read` depois e só nos arquivos certos. `Read` num arquivo de 2 mil linhas para
achar uma função é desperdiçar 25 mil tokens. Se seu projeto tem language server, os plugins
de inteligência de código fazem `LSP` substituir vários `Grep` + `Read` por uma chamada exata.

Estas ferramentas **não pedem permissão** dentro do diretório de trabalho. Fora dele, pedem.

### Escrita — sempre pedem permissão

| Ferramenta | O que faz | Cuidado |
|---|---|---|
| `Edit` | Substituição exata de um trecho | Falha se o texto não bater exatamente. É proteção, não defeito |
| `Write` | Cria ou **sobrescreve** o arquivo inteiro | O risco real: sobrescrever apagando o que não devia |
| `NotebookEdit` | Célula de Jupyter | — |

`Edit` exige que o arquivo tenha sido lido antes na mesma sessão. Isso evita a classe de
erro mais destrutiva: editar às cegas por suposição.

### Execução — o poder e o risco

| Ferramenta | O que faz |
|---|---|
| `Bash` | Comandos de shell. Suporta execução em segundo plano |
| `PowerShell` | Idem, em PowerShell (Windows, ou com `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`) |
| `Monitor` | Roda em segundo plano e observa até uma condição |

`Bash` pede permissão, **exceto** por um conjunto embutido de comandos só-leitura (`ls`,
`cat`, `git status`, `git diff`…). Comandos que buscam conteúdo da rede (`curl`, `wget`)
**não** são auto-aprovados, mesmo sendo "leitura" — a razão é injeção de prompt ([`24`](24-seguranca.md)).

Duas propriedades importantes:

- **Detecção de injeção de comando**: um `Bash` suspeito pede aprovação mesmo que uma regra
  já o permita. `echo $(rm -rf /)` é verificado por dentro.
- **Casamento que falha fechado**: o que não casa nenhuma regra **pergunta**, nunca passa.

### Delegação e organização

| Ferramenta | O que faz |
|---|---|
| `Agent` | Cria um subagente com contexto próprio ([`19`](19-subagentes.md)) |
| `Skill` | Executa uma skill ([`18`](18-skills-e-comandos.md)) |
| `TodoWrite` | Lista de afazeres visível da sessão |
| `Task*` | Fila de tarefas e controle de trabalhos em background |
| `SendMessage`, `ListAgents` | Comunicação entre sessões e subagentes |
| `Workflow` | Orquestração determinística de vários subagentes |

`TodoWrite` parece cosmético e não é: ao dividir a tarefa em itens, o modelo mantém o plano
**dentro do contexto**, o que reduz o abandono de passos em tarefas longas. `Ctrl+T` mostra.

### Rede e saída para fora — sempre pedem permissão

| Ferramenta | O que faz | Por que exige cuidado |
|---|---|---|
| `WebFetch` | Busca uma URL e responde sobre ela | Conteúdo externo pode conter injeção. Roda em **contexto isolado** justamente por isso |
| `WebSearch` | Busca na web | Idem |
| `Artifact` | Publica página HTML/Markdown | Publica para fora |
| `PushNotification`, `SendUserFile` | Notifica, envia arquivo | Saem da máquina |
| `Cron*` | Agenda tarefas recorrentes | Executa sem você presente |

### Controle de fluxo

`EnterPlanMode`/`ExitPlanMode`, `EnterWorktree`/`ExitWorktree`, `AskUserQuestion`,
`ToolSearch`, `WaitForMcpServers`, `ReportFindings`, `ScheduleWakeup`, `EndConversation`.

`AskUserQuestion` merece nota: é o modelo **perguntando a você** em múltipla escolha, em vez
de adivinhar. Se ele nunca pergunta e sempre adivinha, seus prompts provavelmente estão
subespecificados.

### MCP

Ferramentas de servidores externos aparecem como `mcp__<servidor>__<ferramenta>`. Regras de
permissão e matchers de hook usam esse nome ([`20`](20-mcp.md)).

---

## 3. Como o modelo escolhe — e como você influencia

A escolha vem de: descrição da ferramenta + contexto + instruções + histórico. Você controla
três alavancas:

**1. Restringir o conjunto.** Menos opções, escolha melhor:

```bash
claude --tools "Read,Grep,Glob"                # só estas existem
claude --allowedTools "Read,Bash(npm test)"    # estas não perguntam
claude --disallowedTools "WebFetch,WebSearch"  # estas somem
```

Em subagentes, `tools:` e `disallowedTools:` no frontmatter fazem o mesmo, de forma durável.

**2. Instruir no `CLAUDE.md`.** Influência, não garantia:

```markdown
- Para achar símbolos, use `Grep` antes de `Read`. Não leia arquivos inteiros para procurar.
- Para operações do GitHub, use a CLI `gh` via Bash, não servidor MCP.
```

**3. Interceptar com hook.** Garantia:

```bash
# PreToolUse com matcher "Bash" — reescreve o comando antes de rodar
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow",
 "updatedInput":{"command":"npm test 2>&1 | tail -40"}}}
```

---

## 4. Custo relativo — a tabela que muda decisões

| Ação | Ordem de grandeza em tokens | Comentário |
|---|---|---|
| `Glob` em 1.000 arquivos | ~1–3 mil | barato |
| `Grep` com 20 acertos | ~1–2 mil | barato e preciso |
| `Read` de arquivo de 500 linhas | ~6–8 mil | **caro** |
| `Read` de arquivo de 3.000 linhas | ~40 mil | **muito caro** |
| `Bash: npm test` verboso | 10–100 mil | **o maior vilão silencioso** |
| `Bash: npm test` filtrado por hook | ~1 mil | mesma informação útil |
| `WebFetch` de uma página | 5–30 mil | varia muito |
| Definições de um servidor MCP grande | 10–50 mil **por mensagem** | pior de todos, porque é recorrente |
| Subagente que explora 40 arquivos | ~200 mil no subagente, **~500 na sua conversa** | é para isso que ele existe |

Duas conclusões operacionais:

- **Filtrar saída de comando é a otimização de melhor retorno que existe.** Uma linha de
  `| tail -40` ou um hook de filtragem economiza mais que qualquer ajuste de prompt.
- **Servidor MCP é o único custo recorrente por mensagem.** Todos os outros são pontuais.
  Por isso a recomendação repetida: prefira CLI (`gh`, `aws`, `psql`) quando existir.

---

## 5. Sete práticas de quem usa há tempo

1. **`Grep` antes de `Read`, sempre.** Se você precisa instruir isso no `CLAUDE.md`, instrua.
2. **Não deixe `WebFetch` livre em repositório sensível.** Conteúdo externo é o vetor
   clássico de injeção; o contexto isolado ajuda, mas não elimina.
3. **`Bash` com `deny` em comandos destrutivos**, mesmo confiando: `rm -rf *`, `git push --force`,
   `DROP TABLE`. Custa nada e evita o dia ruim.
4. **Ligue os plugins de inteligência de código** se sua linguagem tem language server: `LSP`
   substitui buscas por navegação exata, e os erros de tipo chegam sozinhos depois de cada edição.
5. **Prefira `Monitor` a `Bash` com `sleep`** para esperar por condição — é feito para isso.
6. **`TodoWrite` visível (`Ctrl+T`)** em tarefas longas. Você percebe abandono de passo antes do fim.
7. **Um subagente com `tools: Read, Grep, Glob`** é a forma mais barata de dizer "explore, mas
   não estrague nada".

---

## 6. Os cinco porquês: por que `Edit` falha dizendo que não achou o texto?

1. **Por que ele reclama que a string não bate?**
   `Edit` exige correspondência **exata**, inclusive espaços e indentação.
2. **Por que exigir exatidão, se poderia ser tolerante?**
   Porque substituição aproximada em código é perigosa: casa no lugar errado e corrompe em
   silêncio — e o agente segue confiante.
3. **Por que não usar número de linha?**
   Linhas se deslocam a cada edição anterior. Uma sequência de edições por linha derruba a
   referência a partir da segunda.
4. **Por que não reescrever o arquivo inteiro com `Write`?**
   Porque `Write` sobrescreve tudo: se o modelo não reproduzir fielmente o que não muda, ele
   apaga código. `Edit` limita o estrago à região citada.
5. **Então por que falha tanto?**
   Quase sempre porque o arquivo mudou depois da leitura (outra edição, formatador, hook, ou
   você no editor). A correção é reler antes de editar — e é exatamente o que o agente faz ao
   receber o erro. *(Parada legítima: decisão de projeto sobre segurança de edição.)*

---

## Autoteste

1. Por que uma ferramenta disponível e nunca usada ainda custa dinheiro?
2. Qual é o padrão de busca correto, e quanto custa fazer errado num arquivo de 3.000 linhas?
3. Por que `curl` não é auto-aprovado, mesmo sendo "só leitura"?
4. Cite as três alavancas para influenciar a escolha de ferramenta, e qual delas é garantia.
5. Qual é o único custo de contexto **recorrente por mensagem**, e o que fazer a respeito?
6. Por que `Edit` exige correspondência exata? O que aconteceria se fosse tolerante?
7. Como configurar um subagente que pode explorar mas não pode estragar nada?
