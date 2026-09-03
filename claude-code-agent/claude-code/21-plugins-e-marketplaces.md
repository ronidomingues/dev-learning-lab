# 21 · Plugins e marketplaces — distribuir configuração

> **Nível:** avançado · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

Skills, subagentes e hooks resolvem o **seu** problema. Plugin resolve o problema do **time**:
empacotar tudo isso, versionar, distribuir e atualizar.

---

## 1. Standalone × plugin

| | `.claude/` standalone | Plugin |
|---|---|---|
| Nome das skills | `/revisar` | `/meu-plugin:revisar` |
| Distribuição | copiar e colar | `/plugin install` |
| Versionamento | nenhum | `version` no manifesto |
| Alcance | um projeto (ou seu `~`) | todos os times |
| Bom para | uso pessoal, experimento, configuração deste repositório | padrão da organização, ferramenta compartilhada |

**Caminho recomendado:** comece standalone em `.claude/`, itere até estabilizar, converta em
plugin quando outra pessoa pedir para usar. Plugin cedo demais é cerimônia sem público.

---

## 2. Estrutura

```
meu-plugin/
├── .claude-plugin/
│   └── plugin.json          # manifesto — SÓ ele fica aqui
├── skills/
│   └── revisar/SKILL.md
├── agents/
│   └── revisor.md
├── hooks/
│   └── hooks.json
├── .mcp.json                # servidores MCP do plugin
├── .lsp.json                # servidores de linguagem (inteligência de código)
├── monitors/monitors.json   # monitores em segundo plano
├── bin/                     # executáveis, entram no PATH do Bash enquanto ativo
├── settings.json            # configuração padrão (chaves `agent`, `subagentStatusLine`)
└── README.md
```

> ⚠️ **Erro nº 1:** colocar `skills/`, `agents/` ou `hooks/` **dentro** de `.claude-plugin/`.
> Só o `plugin.json` mora lá; todo o resto fica na raiz do plugin.

`plugin.json`:

```json
{
  "name": "padroes-do-time",
  "description": "Skills, revisor e hooks do time de plataforma",
  "version": "1.2.0",
  "author": { "name": "Time de Plataforma" },
  "homepage": "https://github.com/empresa/claude-plugins"
}
```

O `name` vira o **espaço de nomes**: uma skill em `skills/revisar/` passa a ser
`/padroes-do-time:revisar`. O prefixo é obrigatório e existe para evitar colisão entre plugins.

Um plugin com **uma única skill** pode pôr `SKILL.md` direto na raiz, sem a pasta `skills/`.

---

## 3. Criar e testar

```bash
claude plugin init minha-ferramenta
```
> Anda o esqueleto em `~/.claude/skills/minha-ferramenta/` com manifesto e `SKILL.md`.
> Carrega sozinho na próxima sessão como `minha-ferramenta@skills-dir`, sem marketplace.

Ou à mão, testando sem instalar:

```bash
claude --plugin-dir ./meu-plugin
```
```bash
claude --plugin-dir ./um --plugin-dir ./outro     # vários
claude --plugin-dir ./meu-plugin.zip              # arquivo empacotado
claude --plugin-url https://ci.empresa.com/artefatos/plugin.zip
```

Depois de editar: `/reload-plugins` — recarrega skills, agentes, hooks, MCP e LSP do plugin.

Validar antes de publicar:

```bash
claude plugin validate ./meu-plugin
# esperado: ✔ Validation passed  (ou "passed with warnings")
claude plugin validate ./meu-plugin --strict   # trata aviso como erro
```

Um plugin carregado por `--plugin-dir` **tem precedência** sobre um de mesmo nome já
instalado — o que permite testar mudanças sem desinstalar nada.

---

## 4. Marketplaces

Um marketplace é um repositório git com um catálogo:

```
meu-marketplace/
├── .claude-plugin/
│   └── marketplace.json
├── plugin-a/
└── plugin-b/
```

Instalar de um marketplace:

```bash
claude plugin marketplace add empresa/claude-plugins       # repo do GitHub
claude plugin install padroes-do-time@empresa-plugins
```

Marketplaces oficiais:

| Nome | O que é | Como adicionar |
|---|---|---|
| `claude-plugins-official` | Curado pela Anthropic. Registrado automaticamente na primeira sessão interativa | `claude plugin marketplace add anthropics/claude-plugins-official` |
| `claude-community` | Submissões de terceiros, após revisão | `/plugin marketplace add anthropics/claude-plugins-community` |

Para manter interno ao time, hospede o marketplace num **repositório privado** — o mecanismo
é o mesmo, o acesso é o do git.

Controles de organização:

```json
{
  "extraKnownMarketplaces": [{ "source": "github", "repo": "empresa/claude-plugins" }],
  "blockedMarketplaces": [{ "source": "github", "repo": "aleatorio/plugins" }],
  "strictKnownMarketplaces": true
}
```

---

## 5. O que vale empacotar

| Vale | Não vale |
|---|---|
| Padrões de revisão do time | Sua preferência pessoal de estilo |
| Subagente que conhece o domínio da empresa | Uma skill de três linhas |
| Hooks de conformidade (licença, segredo, lint) | Configuração que muda toda semana |
| LSP para linguagem interna | O que já existe no marketplace oficial |
| Fluxo de deploy padronizado | Coisas específicas de um repositório — deixe em `.claude/` |

Antes de escrever um LSP próprio, confira os plugins de inteligência de código oficiais:
TypeScript, Python, Rust e outros já existem, e eles reduzem contexto de forma mensurável
(navegação exata substitui `grep` + várias leituras).

---

## 6. Recursos que só existem em plugin

Três coisas que você **não** consegue com `.claude/` standalone:

**`bin/`** — executáveis do plugin entram no `PATH` da ferramenta `Bash` enquanto ele está
ativo. Permite distribuir um utilitário junto com as instruções que o usam.

**`monitors/monitors.json`** — monitores de segundo plano que observam logs e avisam o Claude
quando algo acontece:

```json
[
  { "name": "erros", "command": "tail -F ./logs/error.log", "description": "Log de erros da aplicação" }
]
```
Cada linha de `stdout` vira notificação na sessão. É o caminho para o agente **reagir** a
eventos, em vez de só responder a você.

**`settings.json` do plugin** — hoje aceita `agent` e `subagentStatusLine`. Definir `agent`
faz o plugin trocar o comportamento padrão do Claude Code inteiro:

```json
{ "agent": "revisor-de-seguranca" }
```

---

## 7. Migrar de `.claude/` para plugin

```bash
mkdir -p meu-plugin/.claude-plugin
# escreva o plugin.json
cp -r .claude/skills   meu-plugin/
cp -r .claude/agents   meu-plugin/
cp -r .claude/commands meu-plugin/
mkdir meu-plugin/hooks
# copie o objeto "hooks" do settings.json para meu-plugin/hooks/hooks.json — o formato é o mesmo
claude --plugin-dir ./meu-plugin
```

Detalhe importante ao migrar: **agentes de projeto/usuário com o mesmo nome têm precedência
sobre os do plugin.** Se você não apagar o original, o do plugin não entra em vigor. Skills,
por serem prefixadas, coexistem: `/revisar` e `/meu-plugin:revisar` passam a existir juntas.

---

## 8. Segurança

Instalar um plugin é executar código de terceiros com as suas permissões — ele traz hooks,
que rodam comandos, e servidores MCP, que injetam ferramentas.

Antes de instalar de fonte que você não controla:

1. Leia `hooks/hooks.json` e todo script referenciado.
2. Leia `.mcp.json`: para onde os dados vão?
3. Leia `bin/`: o que entra no seu `PATH`?
4. Prefira marketplaces internos ou o oficial.
5. Em organização, feche com `strictKnownMarketplaces` e `blockedMarketplaces`.

Plugins aprovados no marketplace da comunidade ficam presos a um **commit SHA específico**, e
o catálogo público sincroniza diariamente a partir do processo de revisão — o que dá alguma
rastreabilidade, mas **não** é auditoria de segurança.

---

## 9. Os cinco porquês: por que skills de plugin têm prefixo obrigatório?

1. **Por que `/meu-plugin:revisar` e não `/revisar`?**
   Para evitar colisão: dois plugins com uma skill `revisar` conviveriam sem se anular.
2. **Por que não resolver colisão por ordem de instalação?**
   Porque o comportamento dependeria da ordem — a mesma configuração daria resultados
   diferentes em máquinas diferentes.
3. **Por que não avisar e deixar o usuário escolher?**
   Escala mal: com dez plugins e trinta skills, você viraria um resolvedor manual de conflitos.
4. **Por que skills locais não têm prefixo, então?**
   Porque são suas: você controla os nomes e sabe quando duplicou.
5. **Qual é a lição de projeto?**
   Espaço de nomes explícito é o preço da distribuição. Toda plataforma de pacotes chega à
   mesma conclusão — npm com escopos, Java com pacotes, Rust com crates.
   *(Parada legítima: decisão de projeto documentada, com o mesmo padrão em outros ecossistemas.)*

---

## Autoteste

1. Quando converter `.claude/` em plugin, e quando é cedo demais?
2. Qual é o erro nº 1 de estrutura de plugin?
3. Como testar um plugin sem instalar? E como recarregar depois de editar?
4. Cite os três recursos que só existem em plugin e para que servem.
5. Ao migrar, por que o agente do plugin pode não entrar em vigor?
6. Quais quatro arquivos ler antes de instalar plugin de fonte desconhecida?
7. Por que o prefixo de espaço de nomes é obrigatório em skills de plugin?
8. Como uma organização restringe de onde os plugins podem vir?
