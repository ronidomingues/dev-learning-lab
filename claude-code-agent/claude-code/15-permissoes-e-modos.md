# 15 · Permissões e modos — o freio, e como calibrá-lo

> **Nível:** intermediário · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231

Permissão é onde a maior parte das pessoas erra de um jeito ou do outro: ou se irrita com os
prompts e desliga tudo, ou deixa tudo no padrão e desperdiça meia hora por dia clicando
"sim". Existe um caminho do meio, e ele é configurável.

---

## 1. Os seis modos

| Modo | Roda sem perguntar | Para quê |
|---|---|---|
| `default` | Só leitura | Começar; código sensível |
| `acceptEdits` | Leitura, edições e comandos comuns de arquivo (`mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`) | Iterar em código que você vai revisar depois |
| `plan` | Só leitura, e propõe um plano antes de agir | **Toda tarefa não trivial** |
| `auto` | O que um classificador aprovar | Sessões longas com direção confiável |
| `dontAsk` | Só o que estiver pré-aprovado; o resto é **negado** | CI e automação travada |
| `bypassPermissions` | **Tudo** | Só dentro de contêiner |

Trocar durante a sessão: `Shift+Tab` cicla `default` → `acceptEdits` → `plan`.
`auto` entra no ciclo quando disponível; `bypassPermissions` só aparece se você iniciou com
a flag correspondente; `dontAsk` **nunca** entra no ciclo — só por `--permission-mode dontAsk`.

Padrão persistente:

```json
{ "permissions": { "defaultMode": "acceptEdits" } }
```

> **Mudança de calendário relevante:** segundo a documentação oficial consultada em
> 13/08/2026, **a partir de 14/08/2026 o modo `auto` passa a ser o padrão de novas sessões**
> nos planos Pro, Max e Team. Se você abriu este material depois dessa data e estranhou não
> receber prompts, é isto. Um padrão definido por você continua valendo.

---

## 2. Modo plano — o hábito de maior retorno

Em `plan` o Claude **só lê**. Ele explora, entende e apresenta um plano para você aprovar.

Por que insistir tanto: o erro caro de um agente quase nunca é sintático — é **entender
errado o pedido** e executar quinze passos na direção errada. O modo plano converte quinze
passos errados em um parágrafo errado. O custo de corrigir cai duas ordens de grandeza.

```
/plan migrar a autenticação de sessão para JWT
```

Ao apresentar o plano, você escolhe entre aprovar (e seguir em qual modo), recusar, ou
corrigir o rumo por escrito — sem perder o contexto já construído, que é a parte cara.

Quando **não** usar: tarefa de um passo e reversível ("adicione um log aqui"). Modo plano
para isso é burocracia.

---

## 3. Modo auto — como funciona de verdade

Um **modelo classificador separado** revisa cada ação antes de executar e bloqueia o que
escapa do escopo do seu pedido. Não é uma lista fixa; é julgamento automatizado.

Requisitos: conta elegível (Pro, Max, Team, Enterprise); em Team/Enterprise vem ligado por
padrão e o administrador pode desativar com `permissions.disableAutoMode`. Se o Claude Code
diz que auto mode está indisponível, é requisito não atendido — não é instabilidade.

Ajuste do classificador:

```json
{
  "autoMode": {
    "soft_deny": ["$defaults", "Nunca rode terraform apply"],
    "hard_deny": ["Nunca escreva em diretórios de produção"],
    "classifyAllShell": true
  }
}
```

`"$defaults"` herda as regras embutidas; sem ele, você as substitui.

> **Aviso honesto, que a própria documentação faz:** modo auto **reduz prompts, não garante
> segurança**. É para tarefas em que você confia na direção geral, não substituto de revisão
> em operação sensível. Minha recomendação: excelente para refatoração e testes; evite em
> qualquer coisa que toque infraestrutura, credenciais ou migração de dados.

---

## 4. Regras de permissão

### Sintaxe

```
NomeDaFerramenta(padrão)
```

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run test *)",
      "Bash(git diff *)",
      "Read(~/.zshrc)",
      "Edit(./src/**)"
    ],
    "ask": ["Bash(git push *)", "Bash(git commit *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Bash(curl *)", "Bash(rm -rf *)"]
  }
}
```

### As sete regras que evitam surpresa

1. **`deny` vence `allow`**, sempre, em qualquer escopo.
2. Regras **somam** entre escopos (gerenciado + usuário + projeto + local) em vez de substituir.
3. **O espaço antes do `*` importa.** `Bash(git diff *)` casa `git diff HEAD`;
   `Bash(git diff*)` casa também `git diff-index`. A segunda forma é quase sempre engano.
4. **Comandos encadeados são avaliados um a um.** `npm test && git push` verifica os dois.
5. **`$(...)` e crases são inspecionados.** `echo $(rm -rf /)` não passa por ser um `echo`.
6. **Casa fechado:** o que não bate nenhuma regra **pergunta**. Nunca "passa por omissão".
7. **Comandos suspeitos pedem aprovação mesmo estando na allowlist** — a detecção de injeção
   tem prioridade.

### Fronteira de diretório

O Claude Code só escreve na pasta onde foi aberto e abaixo dela. Leitura fora dela pede
aprovação. Para ampliar:

```bash
claude --add-dir ../biblioteca-compartilhada ../apps
```
ou `/add-dir` na sessão, ou `additionalDirectories` nas configurações.

### Caminhos protegidos

Existe um conjunto de caminhos cuja **escrita nunca é auto-aprovada** — nem por regras
`allow`, nem em `acceptEdits`. A checagem acontece antes da avaliação das regras.

Diretórios: `.git`, `.config/git`, `.vscode`, `.idea`, `.husky`, `.cargo`, `.devcontainer`,
`.yarn`, `.mvn`, `.claude` (exceto `.claude/worktrees`).

Arquivos: `.gitconfig`, `.gitmodules`, arquivos de perfil de shell (`.bashrc`, `.zshrc`,
`.profile`…), `.npmrc`, `.yarnrc`, `.pnpmfile.cjs`, `bunfig.toml`, `.bazelrc`,
`.pre-commit-config.yaml`, `lefthook.*`, wrappers de Gradle e Maven, `.devcontainer.json`,
`.ripgreprc`, `pyrightconfig.json`, `.mcp.json`, `.claude.json`.

**Por que exatamente esses?** Todos são arquivos que **executam código** ou **alteram o que
executa código**: hook de git, configuração de gerenciador de pacotes, wrapper de build,
configuração do próprio agente. Escrever num deles é escapar do sistema de permissões pela
porta dos fundos. Em `dontAsk` a escrita neles é negada; em `bypassPermissions`, liberada —
mais uma razão para esse modo só existir dentro de contêiner.

---

## 5. Reduzir prompts sem perder o freio

Ordem correta de tentativa:

**1. `/fewer-permission-prompts`** — analisa seus transcritos, encontra as chamadas
repetidas e seguras, e propõe uma allowlist para o `.claude/settings.json` do projeto.
É o caminho mais rápido e o mais bem calibrado.

**2. Allowlist manual do que é comprovadamente seguro:**

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)", "Bash(npm run lint)", "Bash(npm run build)",
      "Bash(git status *)", "Bash(git diff *)", "Bash(git log *)",
      "Bash(ls *)", "Bash(cat *)"
    ]
  }
}
```

**3. `acceptEdits` para edição, mantendo `Bash` sob controle.** Boa configuração default
para trabalho diário: você revisa por `git diff` depois, e comandos continuam pedindo.

**4. `auto`, se disponível e se a tarefa não toca em nada crítico.**

**5. `bypassPermissions` — somente em contêiner.** Ver [`24`](24-seguranca.md).

> **A escolha errada**, que muita gente faz no segundo dia: `--dangerously-skip-permissions`
> na máquina de trabalho. Você não removeu o incômodo; removeu a única barreira entre uma
> injeção de prompt num README e o seu `~/.ssh`. O nome da flag não é acidental.

---

## 6. Regras de negação que todo projeto deveria ter

Custam nada e evitam o dia ruim:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./**/*.pem)", "Read(./secrets/**)",
      "Bash(rm -rf /*)", "Bash(git push --force *)", "Bash(git reset --hard *)",
      "Bash(curl * | sh)", "Bash(curl * | bash)"
    ]
  }
}
```

Note `Read(./.env)`: não é o agente que vai roubar seu segredo — é que, uma vez lido, o
segredo está no **contexto**, e contexto vai para transcrições, resumos e às vezes para logs.
A regra existe para o segredo nunca entrar.

Para blindagem de verdade (garantia, não pedido), some um hook `PreToolUse` — exemplo real
executado em [`07-projeto-modelo/.claude/hooks/bloqueia-segredos.sh`](07-projeto-modelo/.claude/hooks/bloqueia-segredos.sh).

---

## 7. Sandbox

Onde disponível (macOS, Linux, WSL2 — **não** no Windows nativo), o sandbox isola sistema de
arquivos e rede dos comandos de shell. O ganho duplo: menos prompts **e** mais segurança,
porque o comando não alcança o que não deveria mesmo que rode.

```
/sandbox
```

É a resposta certa para "quero autonomia sem risco", e melhor do que
`bypassPermissions` fora de contêiner em quase todo cenário.

---

## 8. Os cinco porquês: por que ele pergunta sobre um comando que já aprovei?

1. **Por que ele pergunta de novo?**
   Provavelmente o comando não é idêntico: `npm test` foi aprovado, `npm test -- --watch` não.
2. **Por que não casa por prefixo automaticamente?**
   Porque prefixo é perigoso por padrão: `Bash(git *)` liberaria `git push --force` junto com
   `git status`. Você **pode** pedir prefixo com ` *`, mas assumindo a consequência.
3. **Por que não deixar o modelo julgar se é equivalente?**
   Porque ele é o componente que pode ser manipulado. Deixá-lo julgar o próprio limite
   fecharia o círculo: quem quer escapar do freio pediria ao freio para se abrir.
4. **Por que às vezes pergunta mesmo com a regra casando?**
   Detecção de injeção de comando: `$(...)`, crases e padrões suspeitos escalam para você,
   mesmo com allowlist.
5. **Isso não é paranoia?**
   É assimetria de custo. O incômodo de um prompt a mais é de segundos; o custo de um
   `rm -rf` no diretório errado, ou de uma chave vazada, é de horas a semanas. Com
   custos tão desiguais, errar para o lado do prompt é a decisão correta.
   *(Parada legítima: trade-off explícito de risco.)*

---

## 9. Configuração recomendada por perfil

| Perfil | Modo padrão | Extras |
|---|---|---|
| **Aprendendo** | `default` | nada; sinta o fluxo primeiro |
| **Dia a dia** | `acceptEdits` | allowlist de teste/lint/build + `deny` da seção 6 |
| **Refatoração longa** | `auto` ou `acceptEdits` | `/plan` antes, `git commit` limpo antes |
| **Código sensível** | `default` | `deny` amplo, hook `PreToolUse`, revisão de todo diff |
| **CI** | `dontAsk` | `--bare`, `--allowedTools` explícito, `--max-budget-usd`, `--max-turns` |
| **Contêiner descartável** | `bypassPermissions` | isolamento de rede, sem credenciais montadas |

---

## Autoteste

1. Cite os seis modos e o que cada um libera sem perguntar.
2. Por que o modo plano é o hábito de maior retorno? Quando ele é burocracia?
3. `Bash(git diff *)` × `Bash(git diff*)`: qual a diferença, e por que a segunda é geralmente engano?
4. O que são caminhos protegidos, por que **esses** caminhos, e em que modos a escrita neles é liberada?
5. Qual é a ordem correta para reduzir prompts, e qual é a saída errada?
6. Por que negar `Read(./.env)` mesmo confiando no agente?
7. Por que o modelo não pode julgar se um comando é "equivalente" a outro já aprovado?
8. Que configuração você usaria em CI, e quais duas flags jamais podem faltar?
