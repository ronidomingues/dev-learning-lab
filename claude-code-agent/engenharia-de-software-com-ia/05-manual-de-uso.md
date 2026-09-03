# 5 · Manual de uso — referência consultável

**Nível:** intermediário · **Escrito em:** 20/08/2026

> Este arquivo é para **consulta**, não para leitura linear. Está organizado por
> tarefa: você chega com uma pergunta ("como faço para o agente não tocar em
> arquivo X?") e sai com a resposta.
>
> As versões conferidas em 20/08/2026: Claude Code 2.1.237 · Copilot CLI
> (`@github/copilot`) · Codex CLI (`@openai/codex`) · Gemini CLI
> (`@google/gemini-cli`) · Aider.

---

## Índice por tarefa

| Quero… | Seção |
|---|---|
| Começar uma sessão do jeito certo | [§1](#1--iniciar-e-encerrar-sessão) |
| Dar contexto sem colar arquivo | [§2](#2--dar-contexto) |
| Escrever instrução permanente do repositório | [§3](#3--instruções-permanentes-agentsmd) |
| Controlar o que o agente pode executar | [§4](#4--permissões-e-modos) |
| Fazer o agente planejar antes de agir | [§5](#5--planejar-antes-de-executar) |
| Rodar sem interação (CI, script) | [§6](#6--modo-não-interativo-headless) |
| Trabalhar em vários branches ao mesmo tempo | [§7](#7--paralelismo-com-worktrees) |
| Reduzir custo | [§8](#8--custo-e-modelo) |
| Formular o pedido | [§9](#9--anatomia-de-um-bom-pedido) |
| Sair de um beco sem saída | [§10](#10--recuperação) |
| Saber o que está obsoleto | [§11](#11--obsoleto) |

---

## 1 · Iniciar e encerrar sessão

### Comandos de entrada

| Ferramenta | Sessão interativa | Uma pergunta e sai | Continuar a última |
|---|---|---|---|
| Claude Code | `claude` | `claude -p "pergunta"` | `claude --continue` |
| Codex CLI | `codex` | `codex exec "pergunta"` | `codex resume` |
| Copilot CLI | `copilot` | `copilot -p "pergunta"` | — |
| Gemini CLI | `gemini` | `gemini -p "pergunta"` | — |
| Aider | `aider arquivo.py` | `aider --message "..."` | histórico automático |

### A regra de ouro do diretório

**Sempre inicie o agente na raiz do repositório.** Não numa subpasta, não em
`~`, não no `Desktop`.

Motivo: o agente monta o modelo mental do projeto a partir de onde foi aberto.
Aberto numa subpasta, ele não enxerga o `AGENTS.md`, não acha os testes, não
entende a estrutura — e passa a inventar.

```bash
cd ~/projetos/meu-app && claude
```

### Encerrar

| Ação | Claude Code | Por que importa |
|---|---|---|
| Limpar contexto, seguir na mesma pasta | `/clear` | Contexto novo por tarefa; ver [14](14-contexto-e-o-repositorio.md) |
| Sair | `Ctrl+D` ou `/exit` | — |
| Interromper o que está fazendo | `Esc` | **Aprenda este.** Interromper cedo economiza mais que qualquer otimização de prompt |

> **Hábito profissional nº 1:** `Esc` assim que o agente pega o caminho errado.
> A tentação é deixar terminar "para ver no que dá". Não deixe: cada passo errado
> entra no contexto e condiciona os próximos.

---

## 2 · Dar contexto

### Referenciar arquivo

| Ferramenta | Como |
|---|---|
| Claude Code | `@caminho/arquivo.py` no meio da frase |
| Codex CLI | `@arquivo` |
| Aider | `/add arquivo.py` (e `/drop` para remover) |
| Copilot CLI | `@arquivo` |

Exemplo:

```
Compare @src/auth/login.ts com @src/auth/refresh.ts e me diga onde a validação
do token diverge.
```

### Colar saída de comando

```
Rodei `npm test` e deu isto:

<cole a saída LITERAL, inteira, incluindo o stack trace>

Diagnostique. Não altere nada ainda.
```

**"Não altere nada ainda"** é a parte que a maioria esquece. Sem isso, você pede
diagnóstico e recebe uma refatoração.

### Deixar o agente buscar sozinho

Prefira isto a colar arquivo:

```
Procure onde a taxa de câmbio é aplicada. Comece por `rg -n "cambio|exchange" src/`.
```

Você dá a **estratégia de busca**, não o resultado. Isso gasta menos contexto e
funciona melhor em repositório grande.

### Imagem

Quase todos aceitam captura de tela colada (`Ctrl+V`). Usos que valem:

- print do erro no navegador (com o console aberto);
- mockup de tela para implementar;
- diagrama de arquitetura desenhado à mão.

---

## 3 · Instruções permanentes (`AGENTS.md`)

### Onde o arquivo mora e quem lê

| Arquivo | Lido por |
|---|---|
| `AGENTS.md` (raiz do repositório) | Codex, Cursor, Copilot, Gemini CLI, Aider, Zed, Jules, Devin, Windsurf, Amp, Junie, goose, Warp, RooCode e outros — 24 ferramentas listadas em agents.md |
| `CLAUDE.md` | Claude Code (que também lê `AGENTS.md`) |
| `AGENTS.md` em subpasta | O mais próximo do arquivo editado costuma ter precedência |
| `~/.claude/CLAUDE.md` | Instruções suas, válidas em todos os projetos |

### O que colocar (e o que não)

| Coloque | Não coloque |
|---|---|
| Comandos exatos: build, teste, lint, migração | Explicação do que é um teste |
| Convenções que o código **não** revela sozinho | O que já está óbvio no código |
| Armadilhas do projeto ("a tabela `user_v2` é a real; `user` está morta") | Filosofia genérica de engenharia |
| O que é proibido ("nunca edite `schema.sql` à mão") | Elogios ao agente |
| Onde ficam as coisas ("regras de negócio em `src/domain/`") | Documentação de API pública (isso é README) |

### Modelo mínimo que funciona

```markdown
# AGENTS.md

## Comandos
- Instalar: `npm ci`
- Testar: `npm test`
- Testar um arquivo: `npm test -- caminho/do/teste.test.ts`
- Lint: `npm run lint`
- Build: `npm run build`

## Estrutura
- `src/domain/` — regras de negócio, sem I/O, sem framework
- `src/adapters/` — banco, HTTP, fila
- `tests/` — espelha `src/`

## Regras
- Nunca edite arquivos em `tests/` para fazer um teste passar.
- Nunca adicione dependência sem me perguntar.
- Toda mudança de comportamento precisa de teste que falharia sem ela.
- Migrações são geradas por `npm run db:gen`, nunca escritas à mão.

## Armadilhas
- `src/legacy/billing.js` é intocável até a migração terminar (ver ADR-014).
- O campo `status` no banco tem valores em português por decisão de 2019.
```

### Como saber se está funcionando

Peça algo que viole uma regra e veja se ele questiona. Se obedecer cegamente, o
arquivo não está sendo lido — confira o nome e a localização.

> **Erro comum:** `AGENTS.md` de 400 linhas. Instrução que ninguém segue é ruído,
> e ruído compete por contexto com o código. **Se você não conseguiria fazer um
> humano novo seguir aquilo, o agente também não vai.** Corte para uma tela.
> A pesquisa sobre "*configuration smells*" em `AGENTS.md` (arXiv, 2026) aponta
> exatamente isto como o defeito mais comum.

---

## 4 · Permissões e modos

Este é o controle mais importante e o menos usado.

### Claude Code

| Modo | Comportamento | Quando usar |
|---|---|---|
| Padrão | Pergunta antes de editar arquivo ou rodar comando | Aprendendo o projeto ou o agente |
| `/permissions` | Abre a configuração de regras de permissão | Para automatizar o que você já aprovaria sempre |
| Plan mode (`Shift+Tab` alterna) | Só lê e propõe; não escreve nada | **Investigação, sempre** |
| `--dangerously-skip-permissions` | Não pergunta nada | **Só dentro de container descartável** |

Regras persistentes em `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test:*)",
      "Bash(npm run lint)",
      "Bash(git status)",
      "Bash(git diff:*)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(git push:*)",
      "Read(./.env)",
      "Read(./secrets/**)"
    ]
  }
}
```

**O que cada bloco faz:** `allow` aprova automaticamente comandos que você
aprovaria de qualquer jeito (elimina o clique repetitivo sem reduzir segurança).
`deny` bloqueia o que nunca deve acontecer sem você — inclusive **leitura** de
arquivos com segredo.

> **`Read(./.env)` no `deny` não é exagero.** Um agente que lê o `.env` põe as
> suas credenciais no contexto; e o contexto vai para o provedor, aparece no
> log da sessão, e pode ser reproduzido numa resposta. Ver
> [22-seguranca](22-seguranca.md).

### Equivalentes nas outras ferramentas

| Conceito | Codex CLI | Aider | Copilot CLI |
|---|---|---|---|
| Só leitura | `--sandbox read-only` | `--chat-mode ask` | modo de sugestão |
| Aprovar cada ação | `--ask-for-approval on-request` | padrão (mostra o diff) | padrão |
| Autonomia total | `--sandbox danger-full-access` | `--yes-always` | `--allow-all-tools` |

### A regra do isolamento

> Autonomia total é **aceitável** e às vezes ótima — desde que o raio de
> explosão seja finito.

Combinação profissional: agente com autonomia total **dentro** de um container
descartável, sem credenciais montadas, com o repositório num *worktree*
separado.

```bash
docker run --rm -it \
  -v "$PWD:/work" -w /work \
  --network none \
  node:22 bash
```

`--network none` corta o acesso à rede: o agente não pode exfiltrar nada nem
instalar pacote alucinado. (Você precisará religar a rede para o próprio agente
falar com a API — o padrão maduro é rede restrita por lista, não rede aberta.)

---

## 5 · Planejar antes de executar

O ganho mais barato disponível: **fazer o agente escrever o plano antes de tocar
em arquivo.**

| Ferramenta | Como |
|---|---|
| Claude Code | `Shift+Tab` até "plan mode"; ou peça explicitamente |
| Qualquer uma | "Não altere nada. Escreva o plano em `PLANO.md` e pare." |

Pedido padrão:

```
Modo de investigação. NÃO altere nenhum arquivo.

1. Leia o código relevante e me diga onde exatamente a mudança precisa acontecer.
2. Liste os arquivos que serão tocados e por quê.
3. Liste os riscos e o que pode quebrar.
4. Proponha como verificar que funcionou.

Pare depois disso e espere minha aprovação.
```

**Por que funciona:** corrigir um plano custa 30 segundos; corrigir 400 linhas
custa meia hora. E o plano é o artefato onde os mal-entendidos aparecem — quase
sempre no item 2, quando ele lista um arquivo que você não esperava.

---

## 6 · Modo não interativo (*headless*)

Para usar o agente dentro de scripts, ganchos de Git e CI.

```bash
claude -p "Resuma as mudanças deste diff em uma linha de commit convencional" \
  --output-format text
```

```bash
codex exec "Rode os testes e conserte falhas óbvias" --sandbox workspace-write
```

Exemplo real — gerar mensagem de commit a partir do diff em *staging*:

```bash
git diff --cached | claude -p "Escreva uma mensagem de commit no padrão
Conventional Commits para este diff. Só a mensagem, sem explicação." \
  --output-format text
```

**Cuidados obrigatórios em modo headless:**

| Risco | Mitigação |
|---|---|
| Sem humano para negar permissão | Rode em container, com permissões restritas |
| Injeção de prompt vindo do conteúdo processado | Trate a saída como **não confiável** — nunca `eval` |
| Custo sem teto | Limite tempo e número de passos; monitore gasto |
| Não-determinismo em CI | **Nunca** deixe o agente decidir se o build passa. Ele **propõe**; o CI decide |

Mais em [21-ci-cd-e-agentes-em-producao](21-ci-cd-e-agentes-em-producao.md).

---

## 7 · Paralelismo com *worktrees*

Padrão profissional para rodar mais de uma tarefa ao mesmo tempo sem conflito.

```bash
git worktree add ../app-tarefa-a -b feat/tarefa-a
git worktree add ../app-tarefa-b -b feat/tarefa-b
```

Abra um agente em cada pasta, em terminais diferentes.

| Comando | O que faz |
|---|---|
| `git worktree list` | Mostra todos os worktrees e seus branches |
| `git worktree remove ../app-tarefa-a` | Remove quando terminar |
| `git worktree prune` | Limpa registros órfãos |

**Limite honesto:** o gargalo passa a ser **você**. Dois agentes em paralelo é
confortável; três é o teto para a maioria das pessoas; acima disso você vira o
funil e o trabalho se acumula sem revisão. Trato disso em
[27-times-e-organizacao](27-times-e-organizacao.md).

---

## 8 · Custo e modelo

### Escolher modelo por tarefa

| Tarefa | Modelo |
|---|---|
| Renomear, formatar, converter formato, tarefa mecânica | O mais barato e rápido (classe Haiku) |
| Trabalho de feature, correção comum, revisão | Classe intermediária (Sonnet) |
| Arquitetura, bug difícil, refatoração ampla, decisão de projeto | O mais capaz (classe Opus) |

No Claude Code: `/model`. No Aider: `--model`. Preços exatos em
[80-custos-e-licencas](80-custos-e-licencas.md).

### As cinco alavancas de custo, em ordem de impacto

1. **Contexto menor.** O custo é dominado por tokens de entrada, e a entrada é
   reenviada a cada passo. Sessão limpa por tarefa é a maior economia disponível.
2. **Cache de prompt.** Um acerto de cache custa 10% do preço normal de entrada.
   Manter o começo do contexto estável (mesmo `AGENTS.md`, mesmos arquivos) faz o
   cache funcionar. Reorganizar o contexto a cada passo o destrói.
3. **Modelo adequado à tarefa.** Não use o modelo de arquitetura para renomear
   variável.
4. **Saída menor.** Peça o *diff*, não o arquivo inteiro reescrito.
5. **Parar cedo.** `Esc` quando o rumo está errado.

### Ver o gasto

| Ferramenta | Comando |
|---|---|
| Claude Code | `/cost` na sessão; `/usage` para os limites do plano |
| API | painel do provedor |

---

## 9 · Anatomia de um bom pedido

Referência rápida. O tratamento completo está em
[16-especificacao-e-plano](16-especificacao-e-plano.md) e no curso
[engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md).

### As seis partes

| Parte | Exemplo | O que acontece sem ela |
|---|---|---|
| **Objetivo** | "Adicionar paginação ao endpoint `GET /pedidos`" | Ele resolve outro problema |
| **Contexto** | "Ver `@src/routes/pedidos.ts`; seguimos o padrão de `@src/routes/clientes.ts`" | Ele inventa um padrão novo |
| **Restrição** | "Não mude a assinatura pública; não adicione dependência" | Escopo explode |
| **Critério de aceitação** | "Deve passar em `npm test -- pedidos`" | Você não tem como julgar |
| **Fora de escopo** | "Não mexa no frontend, não escreva README" | Diff de 12 arquivos |
| **Formato** | "Mostre o diff antes de aplicar" | Você descobre depois |

### Padrões que funcionam (idiomas do ofício)

| Padrão | Frase | Para quê |
|---|---|---|
| Teste primeiro | "Escreva um teste que falha reproduzindo o bug. Só depois conserte." | Prova que o bug existia e sumiu |
| Duas opções | "Proponha duas abordagens com trade-offs. Não implemente ainda." | Evita fixação na primeira ideia |
| Ancoragem em exemplo | "Siga exatamente o padrão de `@arquivo-modelo.ts`" | Consistência com o código existente |
| Autocrítica | "Revise o que você escreveu como se fosse de outra pessoa e liste 3 problemas." | Pega erro óbvio de graça |
| Explicar o porquê | "Por que você escolheu X em vez de Y?" | Você aprende; e às vezes ele percebe que errou |
| Regressão | "Antes de mudar, rode os testes e me diga quais passam. Depois, garanta os mesmos." | Impede quebra silenciosa |

### Padrões que **não** funcionam (e por quê)

| Antipadrão | Por que falha |
|---|---|
| "Seja cuidadoso" / "não erre" / "código de qualidade" | Adjetivo não é especificação. Não muda comportamento de forma mensurável |
| "Você é um engenheiro sênior com 20 anos de experiência" | Persona ajudava em modelos de 2023. Em modelos de 2026, ocupa contexto e muda pouco |
| "Isso é muito importante para minha carreira" | Manipulação emocional. Funcionava marginalmente em 2023; hoje é ruído |
| "Não alucine" | Ele não sabe que está alucinando. Se soubesse, não alucinaria |
| Prompt de 3.000 palavras com 40 regras | Regras no meio de texto longo são as menos seguidas. Corte, ou ponha as críticas no fim |

---

## 10 · Recuperação

### Desfazer

| Situação | Comando |
|---|---|
| Mudanças não commitadas, quero jogar fora | `git checkout .` |
| Idem, incluindo arquivos novos | `git clean -fd` (**confira antes com `git clean -nd`**) |
| Já commitei, quero desfazer mantendo os arquivos | `git reset --soft HEAD~1` |
| Já commitei, quero apagar tudo | `git reset --hard HEAD~1` |
| Perdi um commit e não sei onde está | `git reflog` — ele guarda tudo por 90 dias |

> **`git reflog` é a rede de segurança que quase ninguém conhece.** Enquanto o
> commit existiu, ele está lá. Isso muda a relação psicológica com o agente:
> você pode deixá-lo tentar coisas ousadas porque a volta é barata.

### Reverter uma sessão inteira

```bash
git checkout .
git clean -fd
```

E comece sessão nova. **Não tente consertar por cima.** Contexto contaminado
produz correção contaminada.

### Quando parar de insistir

Sinais de que a sessão não vai render, e é hora de recomeçar:

- Duas correções seguidas sem progresso mensurável.
- O agente começou a mudar código que não tem relação com o problema.
- Ele "consertou" desabilitando um teste, um lint ou uma validação.
- Ele afirma que algo funciona e você acabou de ver não funcionar.
- Você está lendo o diff e não entende mais o que está acontecendo.

**Custo de recomeçar:** 2 minutos. **Custo de insistir:** já vi virar meio dia.

---

## 11 · Obsoleto

O que era prática recomendada e não é mais. Isto envelhece rápido; a data importa.

| Prática | Status em 08/2026 | O que usar |
|---|---|---|
| Persona elaborada ("você é um sênior…") | **Obsoleto.** Ganho desprezível nos modelos atuais | Objetivo e restrição diretos |
| "Pense passo a passo" explícito | **Obsoleto** nos modelos com raciocínio embutido | Nada; ou o controle de esforço da ferramenta |
| Copiar e colar código no chat do navegador | **Obsoleto** para trabalho em repositório | Agente com acesso ao sistema de arquivos |
| `.cursorrules` como formato próprio | **Legado.** Ainda lido por compatibilidade | `AGENTS.md` |
| Colar o arquivo inteiro no contexto | **Ineficiente** com janelas de 1M tokens e ferramentas de busca | Deixe o agente buscar; dê a estratégia |
| Subornar / ameaçar / apelar emocionalmente | **Obsoleto** e sempre foi frágil | Especificação clara |
| Um `CLAUDE.md` gigante com tudo | **Antipadrão** | Um arquivo curto por escopo, no diretório certo |
| Confiar em número de benchmark de site agregador | **Nunca foi bom.** Muitos são gerados por IA e falsos | Leaderboard oficial; teste no seu código |

---

## Fontes consultadas

Consultadas em 20/08/2026:

- AGENTS.md — formato, adoção e ferramentas: https://agents.md/
- Claude Code — configurações e permissões: https://code.claude.com/docs/
- Codex CLI: https://developers.openai.com/codex
- GitHub Copilot CLI: https://docs.github.com/en/copilot/how-tos/copilot-cli
- *Configuration Smells in AGENTS.md Files*, arXiv 2606.15828
- *Instruction Adherence in Coding Agent Configuration Files*, arXiv 2605.10039

---

## Autoteste

1. Por que iniciar o agente na raiz do repositório e não numa subpasta?
2. Qual é o atalho mais importante do dia a dia, e por que interromper cedo
   economiza mais que otimizar prompt?
3. O que vai e o que não vai num `AGENTS.md`? Dê dois exemplos de cada.
4. Por que `Read(./.env)` deve estar na lista de negação?
5. Qual é a condição que torna autonomia total aceitável?
6. Por que pedir plano antes de execução é a otimização mais barata que existe?
7. Cite as cinco alavancas de custo em ordem de impacto e explique a primeira.
8. Por que "seja cuidadoso" não funciona como instrução?
9. Cite três sinais de que é hora de abandonar a sessão e recomeçar.
10. Cite três práticas que eram recomendadas em 2023 e hoje são obsoletas.

---

**Anterior:** [04-como-comecar](04-como-comecar.md) ·
**Próximo:** [06-exemplos](06-exemplos.md)
