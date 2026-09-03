# Projeto-modelo — API de Tarefas com um repositório configurado para agente

> Nível: iniciante → intermediário · Testado em Node v24.18.0, Claude Code 2.1.231, Ubuntu 22.04, em 13/08/2026.

Este projeto tem **duas metades, e a segunda é a que importa para o curso**:

1. Uma API HTTP de tarefas em Node, **sem nenhuma dependência externa**, com 20 testes.
   Ela existe para ser o *alvo*: um agente precisa de código real para editar, testes reais
   para quebrar e rotas reais para revisar.
2. Um diretório `.claude/` **completo** — memória, regras com escopo de caminho, três hooks,
   um subagente, duas skills, um comando no formato antigo e uma política de permissões.
   Mais um script que **valida essa configuração**, porque configuração de agente é código
   que ninguém compila e falha em silêncio.

O que este projeto ensina, em uma frase: **um profissional de Claude Code não digita
prompts melhores — ele monta o repositório para que qualquer prompt dê certo.**

---

## Pré-requisitos

| Item | Versão mínima | Como conferir |
|---|---|---|
| Node.js | 20.6.0 (testado em 24.18.0) | `node --version` |
| npm | qualquer (só usamos scripts) | `npm --version` |
| git | 2.x | `git --version` |
| Claude Code | 2.0+ (testado em 2.1.231) | `claude --version` |
| `jq` | opcional | `jq --version` — sem ele os hooks usam um fallback com `grep` |

Nada é instalado: **não há `npm install`**. Isso é proposital — dependência é a maior
fonte de "funcionou na sua máquina" em material didático.

---

## Rodar

```bash
# 1. entrar no projeto
cd claude-code/07-projeto-modelo

# 2. rodar a suíte  (esperado: 20 pass, 0 fail)
npm test

# 3. validar a configuração do .claude/ + a suíte
npm run verificar

# 4. subir o servidor  (Ctrl+C encerra graciosamente)
npm start
# esperado: servidor de tarefas ouvindo em http://localhost:3000
```

Saída real de `npm run verificar` nesta máquina, em 13/08/2026:

```
=== Verificação da configuração de Claude Code ===

  ok   arquivo presente: CLAUDE.md
  ok   arquivo presente: .claude/settings.json
  ...
  ok   3 hook(s) de comando verificados
  ok   6 regra(s) de negação ativa(s)
  ok   agente válido: revisor-api
  ok   skill válida: checar-tudo
  ok   skill válida: novo-endpoint
  ok   CLAUDE.md com 32 linhas (limite recomendado: 200)
  ok   testes: 20 passaram, 0 falharam

17 verificação(ões) ok, 0 problema(s).
```

### Exercitar a API à mão

```bash
PORTA=3131 npm start &     # sobe em outra porta
curl -s localhost:3131/saude
# {"status":"ok","tarefas":0}

curl -s -i -X POST localhost:3131/tarefas \
  -H 'content-type: application/json' \
  -d '{"titulo":"escrever o 03-instalacao","prioridade":"alta"}' | head -3
# HTTP/1.1 201 Created
# location: /tarefas/1

curl -s -X POST localhost:3131/tarefas \
  -H 'content-type: application/json' -d '{"titulo":""}'
# {"erro":"titulo é obrigatório"}
```

Todas as saídas acima foram **executadas**, não transcritas de memória.

---

## Endpoints

| Método | Rota | Sucesso | Erros |
|---|---|---|---|
| `GET` | `/saude` | 200 `{status, tarefas}` | — |
| `GET` | `/tarefas?concluida=&prioridade=` | 200 lista ordenada | — |
| `POST` | `/tarefas` | 201 + cabeçalho `Location` | 400 título vazio/longo, prioridade inválida, JSON quebrado |
| `GET` | `/tarefas/:id` | 200 | 404 |
| `POST` | `/tarefas/:id/concluir` | 200 (idempotente) | 404 |
| `DELETE` | `/tarefas/:id` | 204 sem corpo | 404 |
| qualquer | rota inexistente | — | 404 |
| método errado | `/tarefas` | — | 405 |

---

## Estrutura, e o que cada decisão ensina

```
07-projeto-modelo/
├── CLAUDE.md                     # 32 linhas. Memória do projeto: comandos, arquitetura, proibições.
├── package.json                  # scripts: test, start, verificar. Zero dependências.
│
├── .claude/
│   ├── settings.json             # permissões (allow/ask/deny) + registro dos 3 hooks
│   │
│   ├── rules/
│   │   └── testes.md             # regra com `paths:` — só entra em contexto ao tocar src/ ou test/
│   │
│   ├── agents/
│   │   └── revisor-api.md        # subagente read-only: revisa, não edita. Contexto separado.
│   │
│   ├── skills/
│   │   ├── novo-endpoint/SKILL.md  # procedimento em 6 passos, invocado por /novo-endpoint
│   │   └── checar-tudo/SKILL.md    # `context: fork` — roda em subagente, devolve só o resumo
│   │
│   ├── commands/
│   │   └── rotas.md              # formato antigo, com `!`comando`` e @arquivo. Ainda funciona.
│   │
│   └── hooks/
│       ├── contexto-da-sessao.sh # SessionStart: injeta branch/Node/sujeira do git no contexto
│       ├── bloqueia-segredos.sh  # PreToolUse: nega Edit/Write em .env, *.pem, chaves
│       └── testa-apos-edicao.sh  # PostToolUse: roda a suíte e devolve a falha ao Claude
│
├── src/
│   ├── tarefas.js                # domínio puro, relógio injetado, erros com status
│   ├── servidor.js               # só traduz HTTP ↔ domínio
│   └── index.js                  # entrada + desligamento gracioso
│
├── test/
│   ├── tarefas.test.js           # 10 testes de domínio, incluindo fronteira e idempotência
│   └── servidor.test.js          # 10 testes de HTTP contra servidor real em porta 0
│
└── scripts/
    └── verificar-configuracao.mjs  # valida o .claude/ inteiro + roda a suíte
```

### As sete decisões, e a lição de cada uma

**1. `CLAUDE.md` com 32 linhas, não 300.**
O arquivo entra no contexto de *toda* sessão. Acima de ~200 linhas o custo sobe e a
aderência cai — o modelo passa a "ver" a regra sem segui-la. O detalhe foi empurrado
para `rules/` (carrega sob demanda) e para as skills (carregam quando invocadas).
Lição: **CLAUDE.md é para fatos que valem sempre; procedimento vira skill.**

**2. Regra com `paths:` em vez de mais texto no CLAUDE.md.**
`.claude/rules/testes.md` tem `paths: ["test/**/*.js", "src/**/*.js"]`. Ela só entra em
contexto quando o Claude lê um arquivo que casa. Você pode escrever 60 linhas de
convenção de teste sem pagar por elas quando está mexendo no README.
Lição: **contexto é orçamento; gaste onde rende.**

**3. Hook `PreToolUse` em vez de "não edite `.env`" no CLAUDE.md.**
CLAUDE.md é *contexto* — o modelo pode não seguir. Hook é *código* — roda sempre.
Se a regra tem consequência real (segredo, produção, dinheiro), ela **não pode ser
uma frase em markdown**. Este é o erro conceitual mais caro de quem começa.
Lição: **contexto pede; hook obriga.**

**4. Hook `PostToolUse` que roda a suíte e devolve a falha ao *Claude*.**
Sem ele, o ciclo é: agente edita → você percebe depois → você reclama → agente conserta.
Com ele: agente edita → suíte quebra → agente vê o erro **no mesmo turno** → conserta
sozinho. Verificado: com um `padrão` trocado de propósito em `src/tarefas.js`, o hook
saiu com código 2 e mandou a mensagem `'baixa' !== 'media'` para o agente.
Lição: **feche o laço de verificação dentro do turno, não fora dele.**

**5. Subagente `revisor-api` com `disallowedTools: Edit, Write`.**
Um revisor que pode editar deixa de ser revisor: ele conserta em silêncio e você nunca
descobre o que estava errado. Além disso, ele roda em **contexto separado** — o `git diff`
inteiro e a leitura dos arquivos ficam lá, e só o veredito volta.
Lição: **subagente serve para isolar contexto e para restringir poder.**

**6. `checar-tudo` com `context: fork`.**
O script cospe dezenas de linhas. Rodando em fork, esse ruído morre no subagente.
Lição: **saída volumosa não deve tocar a conversa principal.**

**7. `scripts/verificar-configuracao.mjs`.**
Ele checa o que falha em silêncio: JSON inválido, hook sem `chmod +x`, hook sem shebang,
skill sem `description`, agente com `name` inválido, `deny` vazio, CLAUDE.md inchado.
Cada uma dessas falhas já custou horas a alguém — todas se parecem com "o Claude ignorou
minha configuração".
Lição: **configuração de agente precisa de teste, como qualquer outro código.**

---

## Roteiro guiado: use o Claude Code neste projeto

Abra o Claude Code **dentro desta pasta** (`cd 07-projeto-modelo && claude`). A ordem
abaixo demonstra, na prática, cada peça da configuração.

1. **`/context`** — veja o `CLAUDE.md` listado em *Memory files* e quanto ele custa.
   O hook `SessionStart` já injetou branch, versão do Node e nº de arquivos sujos.
2. **`/permissions`** — confira que `Bash(npm test)` está liberado e `Bash(curl *)` negado.
3. **Peça algo proibido:** *"crie um arquivo .env com a porta padrão"*. O hook
   `bloqueia-segredos.sh` nega antes de qualquer escrita, com a razão na tela.
4. **Quebre de propósito:** *"em src/tarefas.js, mude a prioridade padrão de 'media' para
   'baixa'"*. O hook `PostToolUse` roda a suíte, ela falha, e o Claude recebe o erro e
   reverte ou conserta **sem você pedir**.
5. **`/rotas`** — o comando no formato antigo roda `grep` no roteador e monta a tabela
   só com o que existe no código.
6. **`/novo-endpoint PATCH /tarefas/:id alterar o título de uma tarefa existente"`** —
   a skill impõe a ordem domínio → teste → HTTP → teste → `npm test` → README.
7. **"use o agente revisor-api para revisar o que mudou"** — revisão em contexto separado,
   sem poder de edição, com veredito em formato fixo.
8. **`/checar-tudo`** — diagnóstico completo em fork, resumo de uma tela.

---

## Adaptar para o seu repositório

O que copiar quase sem mudança: os três hooks, o script de verificação e a estrutura de
permissões. O que **precisa** ser reescrito: o `CLAUDE.md` (é sobre o seu projeto),
a regra em `rules/` e o subagente revisor (as checagens são do seu domínio).

Comece pequeno: `CLAUDE.md` + `permissions.deny` + o hook de teste. As outras peças só
compensam quando a dor aparece.

---

## Limitações declaradas

- Armazenamento é **em memória**: reiniciar o servidor apaga tudo. Persistência sairia
  do escopo (o assunto aqui é Claude Code, não banco de dados).
- Sem autenticação. Uma API real precisaria; ver [`../../apis/`](../../apis/00-MAPA.md).
- Os hooks são `bash`. No Windows nativo (sem WSL/Git Bash), reescreva em PowerShell e
  troque `"shell": "powershell"` na configuração do hook.
- O fluxo do roteiro guiado (passos 1–8) **não foi executado automaticamente** — ele
  depende de uma sessão interativa. Os hooks, o script de verificação, a suíte e a API,
  esses sim, foram executados nesta máquina em 13/08/2026.
