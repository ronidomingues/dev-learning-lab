# 20 · Git e fluxo de trabalho com agentes

**Nível:** intermediário · **Escrito em:** 20/08/2026

---

## Por que o Git ficou mais importante, não menos

Git sempre foi rede de segurança. Com agentes, ele vira **infraestrutura
operacional**:

1. É o **botão de desfazer** que torna a delegação psicologicamente possível.
2. É o **isolamento** que permite paralelismo (*worktrees*).
3. É o **registro** de o que foi gerado, por quem, com que instrução.
4. É a **unidade de reversão** granular quando algo dá errado em produção.

Quem usa Git mal com agente sofre desproporcionalmente, porque o volume de
mudança por unidade de tempo aumentou.

---

## 1 · Regras não negociáveis

### Regra 1 — nunca solte um agente fora de um repositório

```bash
git init && git add -A && git commit -m "estado inicial"
```

Sem isso, "desfazer" não existe.

### Regra 2 — nunca solte um agente na `main`

```bash
git checkout -b tarefa/importar-csv
```

Motivo prático além do óbvio: com branch, `git diff main...HEAD` te dá o
resultado completo da sessão a qualquer momento. Na `main`, você perde essa
visão assim que commita.

### Regra 3 — commite antes de delegar

O ponto de retorno precisa existir **antes**, não depois.

```bash
git status --short   # vazio? então pode delegar
```

### Regra 4 — commits pequenos e atômicos

Não é estética. Commit grande destrói `git bisect` (ver
[exemplo 8](06-exemplos.md)) e impede reversão granular. Um commit gerado por
agente contendo "a feature inteira" é um commit que ninguém consegue reverter
parcialmente daqui a três meses.

---

## 2 · *Worktrees*: o padrão de paralelismo

```bash
git worktree add ../app-a -b feat/exportar-excel
git worktree add ../app-b -b fix/frete-cep-excecao
```

Duas cópias de trabalho, dois branches, um `.git` compartilhado. Um agente em
cada, em terminais separados.

| Comando | O que faz |
|---|---|
| `git worktree list` | Lista todos, com branch de cada |
| `git worktree remove ../app-a` | Remove (o branch continua existindo) |
| `git worktree remove ../app-a --force` | Remove mesmo com alterações |
| `git worktree prune` | Limpa registros de pastas apagadas na mão |

### Por que é melhor que clonar

| | *Worktree* | Clone |
|---|---|---|
| Espaço | Só a cópia de trabalho | Repositório inteiro de novo |
| Branches | Compartilhados | Precisa sincronizar |
| Velocidade | Instantâneo | Depende do tamanho |
| `git log` de um vê o commit do outro | Sim | Não sem `fetch` |

### O limite honesto

**Você é o gargalo.** Dois agentes é confortável; três é o teto para a maioria
das pessoas. Acima disso, a fila de revisão cresce e o trabalho vira estoque.

Sinal de que passou do ponto: você aprova um PR sem lembrar do que pediu.

---

## 3 · Mensagens de commit e atribuição

### Registre a origem

Não é confissão de culpa — é **metadado de investigação**. Saber que um trecho
veio de agente muda onde você procura o bug seis meses depois.

Duas convenções que funcionam:

```
feat(pedido): adiciona exportação em xlsx

Gerado por agente a partir de ESPEC.md#CA-01..CA-05.
Verificado: 12 testes novos, portão aprovado, revisão humana completa.

Co-authored-by: <ferramenta e versão>
```

Ou um *trailer* padronizado, mais fácil de consultar depois:

```
Assisted-by: claude-code/2.1.237
Review-level: full   # full | sampled | gate-only
```

Consultar depois:

```bash
git log --grep="Assisted-by" --oneline | wc -l
git log --grep="Review-level: gate-only" --oneline
```

### A política que eu recomendo

| Situação | Registre |
|---|---|
| Agente escreveu, você revisou linha a linha | `Assisted-by:` + `Review-level: full` |
| Agente escreveu, você revisou por amostragem | `Assisted-by:` + `Review-level: sampled` |
| Agente escreveu, só o portão verificou | `Assisted-by:` + `Review-level: gate-only` |
| Você escreveu com autocompletar | Nada. É o seu código |

A terceira linha é a que importa: **ela torna visível o risco que a equipe está
correndo**. Sem ela, o "gate-only" some no meio do resto.

> Discussão de licença, direito autoral e implicações contratuais está em
> [23-licenca-propriedade-e-lei](23-licenca-propriedade-e-lei.md).

---

## 4 · Ganchos de Git

### `pre-commit` — barato e local

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
set -e
python3 -m portao --staged --sem-cor
npm run lint -- --quiet
EOF
chmod +x .git/hooks/pre-commit
```

Melhor: use o framework `pre-commit` (ver [03-instalacao](03-instalacao.md)),
que versiona a configuração e instala igual para todo mundo.

### `pre-push` — o último ponto barato

```bash
cat > .git/hooks/pre-push <<'EOF'
#!/usr/bin/env bash
set -e
npm test
EOF
chmod +x .git/hooks/pre-push
```

### O limite dos ganchos

Ganchos locais podem ser pulados com `--no-verify` e não existem para quem
clonou e não instalou. **Eles são conveniência, não controle.** O controle mora
no CI, com proteção de branch. Ver
[21-ci-cd-e-agentes-em-producao](21-ci-cd-e-agentes-em-producao.md).

---

## 5 · Recuperação

| Situação | Comando |
|---|---|
| Jogar fora mudanças não commitadas | `git checkout .` |
| Idem, incluindo arquivos novos | `git clean -nd` (ver) → `git clean -fd` (fazer) |
| Desfazer commit, manter arquivos | `git reset --soft HEAD~1` |
| Desfazer commit e arquivos | `git reset --hard HEAD~1` |
| Reverter commit já publicado | `git revert <sha>` |
| Achar um commit "perdido" | `git reflog` |
| Recuperar arquivo apagado | `git checkout HEAD~1 -- caminho` |
| Ver só o que mudou num arquivo | `git diff main...HEAD -- caminho` |

### `git reflog`, a rede que ninguém conhece

O `reflog` registra toda posição por onde o `HEAD` passou, por padrão durante
**90 dias**. Enquanto um commit existiu, ele está recuperável — mesmo depois de
`reset --hard`.

```bash
git reflog
# a1b2c3d HEAD@{0}: reset: moving to HEAD~1
# e4f5g6h HEAD@{1}: commit: trabalho que eu achei que tinha perdido
git checkout -b resgate e4f5g6h
```

**Por que isso importa psicologicamente:** saber que a volta é barata muda o que
você permite ao agente tentar. Quem não conhece `reflog` delega com medo, e medo
produz microgerenciamento — que anula o ganho.

---

## 6 · Fluxo completo, do pedido ao merge

```
 1. git checkout main && git pull
 2. git checkout -b tarefa/xyz          (ou worktree)
 3. escrever ESPEC.md com CA-01..CA-nn
 4. escrever/gerar testes → falham
 5. git commit -m "test: critérios CA-01..CA-05 (falhando)"
 6. delegar a implementação ao agente
 7. rodar você mesmo: make check
 8. python3 -m portao --diff <(git diff main...HEAD)
 9. revisar (método do arquivo 18)
10. git commit com Assisted-by e Review-level
11. git push -u origin tarefa/xyz
12. gh pr create --fill --label gerado-por-agente
13. CI decide. Você não.
14. merge
```

### O passo 5 é o mais importante e o mais pulado

Commitar os testes falhando **antes** da implementação cria uma marca no
histórico:

- prova que os testes existiam antes e não foram moldados ao código;
- permite `git checkout HEAD~1 && make test` para ver a falha original;
- torna impossível o agente "adaptar" o teste sem que apareça no diff.

É a versão em Git da regra "não altere o teste para fazer passar".

---

## 7 · Erros comuns

| Erro | Consequência | Correção |
|---|---|---|
| Delegar com trabalho não commitado | Perde o seu trabalho junto | `git status` antes, sempre |
| Um commit gigante no fim da sessão | Sem `bisect`, sem reversão granular | Commite a cada passo verificável |
| Deixar o agente fazer `git push` | Publica o que você não revisou | `deny: Bash(git push:*)` |
| Deixar o agente fazer `git commit --amend` | Reescreve histórico já publicado | Proíba nas permissões |
| Deixar o agente resolver conflito de merge sozinho | Ele escolhe um lado sem entender a intenção | Resolva você |
| Não limpar *worktrees* | Pastas órfãs, confusão sobre onde está o código | `git worktree prune` no fim |
| `git add -A` sem olhar | Entra artefato, log, `.env` | `git status --short` antes; `.gitignore` bom |

> **O quinto item merece ênfase.** Conflito de merge é o lugar onde a intenção
> de duas pessoas colide, e resolver exige saber o que cada uma queria. Um agente
> escolhe o lado que parece mais completo. Já vi isso apagar silenciosamente uma
> correção de segurança feita em paralelo.

---

## Autoteste

1. Cite as quatro regras não negociáveis de Git com agentes.
2. Por que branch é melhor que `main` além do óbvio?
3. Por que *worktree* é melhor que clone? Cite duas razões.
4. Qual é o limite honesto de paralelismo e qual é o sinal de que passou dele?
5. Por que registrar a origem do código não é confissão de culpa?
6. Qual é o valor específico de `Review-level: gate-only` no histórico?
7. Por que ganchos de Git são conveniência e não controle?
8. O que é `git reflog`, por quanto tempo ele guarda, e por que isso muda o seu
   comportamento ao delegar?
9. Por que o passo 5 do fluxo (commitar testes falhando) é o mais importante?
10. Por que não se deve deixar o agente resolver conflito de merge?

---

**Anterior:** [19-arquitetura-para-maquina](19-arquitetura-para-maquina.md) ·
**Próximo:** [21-ci-cd-e-agentes-em-producao](21-ci-cd-e-agentes-em-producao.md)
