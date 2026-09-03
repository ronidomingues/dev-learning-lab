# 18 · Skills e comandos — empacotar procedimento

> **Nível:** intermediário · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

Skill é um procedimento escrito em markdown que **só entra no contexto quando é usado**.
É a resposta para o `CLAUDE.md` que virou manual de 800 linhas.

> **Nota de nomenclatura:** comandos personalizados **foram fundidos em skills**.
> `.claude/commands/deploy.md` e `.claude/skills/deploy/SKILL.md` criam ambos o `/deploy` e
> funcionam igual. Os arquivos antigos continuam válidos; skills acrescentam pasta de apoio,
> frontmatter mais rico e invocação automática pelo modelo.

---

## 1. Quando criar uma skill

Crie quando:

- você cola as mesmas instruções no chat pela terceira vez;
- uma seção do `CLAUDE.md` deixou de ser **fato** e virou **procedimento**;
- existe um processo do time que precisa ser seguido na ordem certa;
- você quer material de referência longo disponível, mas sem custo permanente de contexto.

Não crie quando:

- é um fato que vale sempre → `CLAUDE.md`;
- é convenção de uma área do código → `.claude/rules/` com `paths:`;
- é uma regra que **não pode** ser violada → hook.

---

## 2. Formato

```
.claude/skills/
└── revisar-pr/
    ├── SKILL.md            # obrigatório
    ├── checklist.md        # apoio, lido sob demanda
    └── scripts/
        └── coletar.sh
```

```markdown
---
name: revisar-pr
description: Revisa um PR contra o checklist do time, verificando testes, migrações e segurança.
argument-hint: [número-do-pr]
disable-model-invocation: true
allowed-tools: Bash(gh pr *), Read, Grep
---

Revise o PR **$1**.

1. `gh pr diff $1` para ver as mudanças.
2. `gh pr view $1 --json title,body` para o contexto declarado.
3. Aplique o checklist em `${CLAUDE_SKILL_DIR}/checklist.md`.
4. Rode a suíte no branch do PR.
5. Responda no formato: VEREDITO / ACHADOS / TESTES.

Não aprove nada com teste falhando. Não comente estilo — o formatador cuida disso.
```

Invocação: `/revisar-pr 123`.

---

## 3. Frontmatter — referência

Todos os campos são opcionais; `description` é o que realmente importa.

| Campo | Para quê |
|---|---|
| `name` | Nome exibido. Padrão: o nome da pasta |
| `description` | **O mais importante.** É por aqui que o Claude decide quando usar. Ponha o caso de uso primeiro: `description` + `when_to_use` são cortados em 1.536 caracteres na listagem |
| `when_to_use` | Frases-gatilho e exemplos de pedido |
| `argument-hint` | Dica no autocompletar: `[número-do-pr]` |
| `arguments` | Nomes posicionais para substituição por `$nome` |
| `disable-model-invocation` | `true` = só roda quando **você** digitar `/nome` |
| `user-invocable` | `false` = some do menu `/` (conhecimento de fundo) |
| `allowed-tools` | Ferramentas pré-aprovadas **durante o turno** que invocou a skill |
| `disallowed-tools` | Ferramentas removidas enquanto a skill está ativa |
| `model`, `effort` | Modelo e esforço enquanto a skill está ativa |
| `context: fork` | Roda num subagente que herda a conversa |
| `agent` | Qual tipo de subagente usar com `context: fork` |
| `background` | Com `fork`, `false` espera o resultado no mesmo turno |
| `paths` | Só ativa automaticamente ao trabalhar com arquivos que casam |
| `hooks` | Hooks com escopo de vida desta skill |
| `shell` | `bash` (padrão) ou `powershell` para os blocos `!` |

### Substituições disponíveis no corpo

| Placeholder | Vira |
|---|---|
| `$ARGUMENTS` | tudo que veio depois do comando, como digitado |
| `$0`, `$1`, … | argumentos posicionais (com aspas para agrupar palavras) |
| `$nome` | argumento nomeado, declarado em `arguments` |
| `${CLAUDE_SKILL_DIR}` | pasta da skill — use para referenciar arquivos de apoio |
| `${CLAUDE_PROJECT_DIR}` | raiz do projeto |
| `${CLAUDE_SESSION_ID}` | id da sessão |

Para escrever um `$` literal antes de dígito ou de `ARGUMENTS`, escape com barra: `\$1.00`.

### Executar shell dentro do corpo

```markdown
Rotas atualmente implementadas:

!`grep -n "url.pathname" src/servidor.js`

Com base apenas nisso e em @src/servidor.js, monte a tabela de rotas.
```

O `` !`comando` `` roda e o resultado é embutido antes de o texto chegar ao modelo. `@arquivo`
inclui o conteúdo. Exemplo real e funcional em
[`07-projeto-modelo/.claude/commands/rotas.md`](07-projeto-modelo/.claude/commands/rotas.md).

> `disableSkillShellExecution: true` desliga essa execução — organizações costumam querer.

---

## 4. `context: fork` — rodar em subagente

```yaml
---
name: checar-tudo
description: Roda a verificação completa e relata o que quebrou, em uma tela.
context: fork
background: false
disable-model-invocation: true
allowed-tools: Bash(npm run verificar), Read
---
```

Com `context: fork`, a skill roda num subagente que **herda a conversa e o prompt de sistema**.
A saída ruidosa fica lá; só o resumo volta. Use sempre que a skill produzir muitas linhas.

`background: true` (padrão) devolve o resultado depois, como notificação; `false` espera no
mesmo turno. Exemplo real em
[`07-projeto-modelo/.claude/skills/checar-tudo/SKILL.md`](07-projeto-modelo/.claude/skills/checar-tudo/SKILL.md).

---

## 5. Escrever uma `description` que funciona

O Claude escolhe a skill lendo a `description`. É engenharia de prompt aplicada a uma linha.

| Ruim | Bom |
|---|---|
| `description: Ajuda com PRs` | `description: Revisa um PR contra o checklist do time — testes, migrações e segurança. Use quando pedirem revisão de PR ou antes de aprovar.` |
| `description: Deploy` | `description: Publica em produção pelo pipeline aprovado. Use só quando pedirem deploy explicitamente; nunca automaticamente.` |

Regras:

1. **Caso de uso primeiro** — o corte em 1.536 caracteres começa a apagar pelo fim.
2. **Diga quando NÃO usar**, se houver risco de acionamento indevido.
3. **Use as palavras que a pessoa realmente digita** ("subir", "publicar", "deploy").
4. Se a skill for perigosa, ponha `disable-model-invocation: true` e durma tranquilo.

---

## 6. Skill × comando antigo × `CLAUDE.md` × hook

| | `CLAUDE.md` | `.claude/rules/` | Skill | Hook |
|---|---|---|---|---|
| Carrega | toda sessão | ao casar `paths:` | ao ser usada | evento do ciclo de vida |
| Custo quando não usada | alto | zero | zero | zero |
| Garantia | baixa | baixa | média | **total** |
| Bom para | fatos | convenções por área | procedimentos | regras invioláveis |

O erro clássico é usar `CLAUDE.md` para tudo. Um `CLAUDE.md` de 800 linhas custa contexto em
toda sessão **e** é seguido pior do que um de 100 linhas — você paga mais para obter menos.

---

## 7. Skills embutidas

O Claude Code já vem com várias, invocáveis como comandos:

| Skill | O que faz |
|---|---|
| `/code-review [low…ultra] [--fix] [--comment] [alvo]` | Revisão de diff ou PR; `ultra` roda multiagente na nuvem |
| `/security-review` | Varredura de segurança no diff |
| `/debug` | Liga log de depuração e investiga a sessão |
| `/doctor` | Diagnóstico de instalação e configuração |
| `/deep-research <pergunta>` | Pesquisa web multifrente com síntese citada |
| `/batch <instrução>` | Mudança em larga escala, decomposta em worktrees |
| `/loop [intervalo] [prompt]` | Repete um prompt |
| `/dataviz`, `/claude-api` | Guias de domínio específicos |
| `/fewer-permission-prompts` | Propõe allowlist a partir do seu histórico |

Desligar todas: `disableBundledSkills: true` ou `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1`.

---

## 8. Distribuir

| Escopo | Onde | Alcance |
|---|---|---|
| Pessoal | `~/.claude/skills/` | todos os seus projetos |
| Projeto | `.claude/skills/` | quem clonar o repositório |
| Organização | plugin em marketplace | todos os times ([`21`](21-plugins-e-marketplaces.md)) |

Depois de criar ou editar: `/reload-skills` (ou reinicie).

Fora do Claude Code, a especificação [Agent Skills](https://agentskills.io) aceita apenas
`name`, `description`, `license`, `compatibility`, `metadata` e `allowed-tools` — os demais
campos são específicos daqui.

---

## 9. Sete práticas

1. **Uma skill, um procedimento.** Skill que faz cinco coisas nunca é acionada na hora certa.
2. **Corpo curto.** Uma vez carregada, ela fica no contexto pelos turnos seguintes. Detalhe
   longo vai para arquivo de apoio, referenciado com `${CLAUDE_SKILL_DIR}`.
3. **Diga o que fazer, não por quê.** Justificativa é custo recorrente de token.
4. **Imponha a ordem quando a ordem importa.** É o que a skill `novo-endpoint` faz: domínio
   → teste → HTTP → teste. Sem ela, regra de negócio vaza para o roteador.
5. **`disable-model-invocation: true`** em tudo que for destrutivo.
6. **`allowed-tools` casando exatamente com o comando do corpo** evita prompt no meio do fluxo.
7. **Termine com o formato de resposta.** "Ao final, mostre apenas X, Y e Z" corta relatório
   de três páginas para três linhas.

---

## 10. Os cinco porquês: por que o Claude não usa minha skill sozinho?

1. **Por que ele ignora a skill?**
   A `description` não casa com o que você pediu. É por ela que ele escolhe.
2. **Por que não pelo nome ou pelo conteúdo?**
   O conteúdo não está no contexto — é justamente o que torna skills baratas. Só o nome e a
   descrição ficam visíveis na listagem.
3. **Por que não carregar tudo, já que ficaria mais preciso?**
   Porque aí seriam `CLAUDE.md`s, com o custo de todas somado em toda sessão.
4. **Por que não deixar o modelo "abrir" skills para ver o conteúdo antes de escolher?**
   É o que ele faz ao invocar. A listagem é o índice; abrir é a leitura. Um índice bom torna
   a leitura desnecessária.
5. **Então a lição?**
   **A `description` é a interface pública da sua skill.** Trate-a com o mesmo cuidado com
   que trataria a assinatura de uma função pública. *(Parada legítima: trade-off explícito
   entre custo de contexto e precisão de seleção.)*

---

## Autoteste

1. Quando criar skill e quando o caso é de `CLAUDE.md`, `rules/` ou hook?
2. Qual campo do frontmatter determina se o Claude usa a skill sozinho, e como escrevê-lo bem?
3. O que `context: fork` resolve? Dê um caso concreto.
4. Diferença entre `$ARGUMENTS`, `$1` e `${CLAUDE_SKILL_DIR}`.
5. Por que o corpo da skill deve ser curto, mesmo carregando sob demanda?
6. Como evitar que uma skill perigosa seja acionada automaticamente?
7. Por que "a `description` é a interface pública da skill"?
8. Comandos em `.claude/commands/` estão obsoletos? Responda com precisão.
