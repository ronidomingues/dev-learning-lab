# 70 · Prática — 12 laboratórios progressivos

> **Nível:** iniciante → avançado · **Atualizado em:** 13/08/2026 · Claude Code 2.1.231
> **Nenhum destes laboratórios foi executado automaticamente** — todos exigem sessão
> interativa sua. Os artefatos que eles constroem, porém, existem prontos e **verificados**
> em [`07-projeto-modelo/`](07-projeto-modelo/README.md), para comparação.

Faça-os na ordem. Cada um pressupõe o anterior. Tempo total estimado: 8 a 12 horas.

Ambiente: use o projeto-modelo como campo de treino.

```bash
cd claude-code/07-projeto-modelo
npm test          # esperado: 20 pass, 0 fail
```

---

## Lab 1 · Primeira sessão consciente (20 min) · iniciante

**Objetivo:** perceber o laço agêntico acontecendo.

1. `git add -A && git commit -m "antes do lab"` (rede de segurança).
2. `claude` no projeto-modelo.
3. Pergunte: *"o que este projeto faz e como rodo os testes? responda em 5 linhas"*.
4. **Observe as linhas de ferramenta** na tela: `Read`, `Glob`, `Grep`. Anote quantas foram.
5. Rode `/context`. Anote o total de tokens e o que ocupa mais espaço.
6. Rode `/usage`. Anote o custo.

**Critério de sucesso:** você sabe dizer quantas ferramentas foram usadas, quanto contexto
foi consumido e quanto custou.

**Pergunta para responder por escrito:** por que a mesma pergunta feita de novo, na mesma
sessão, custa menos?

---

## Lab 2 · Modo plano e interrupção (20 min) · iniciante

**Objetivo:** internalizar os dois hábitos de maior retorno.

1. `/plan adicionar um endpoint PATCH /tarefas/:id que altera o título`.
2. **Não aprove.** Leia o plano. Ele começa pelo domínio ou pelo servidor?
3. Responda corrigindo: *"comece por src/tarefas.js, e escreva o teste antes do HTTP"*.
4. Aprove o plano corrigido e deixe agir.
5. **Interrompa com `Esc`** no meio da segunda edição, mesmo que esteja indo bem.
6. Escreva: *"pare por aqui, mostre o que você já mudou"*.
7. `git checkout -- .` para desfazer.

**Critério:** você interrompeu sem hesitar e desfez sem drama.

---

## Lab 3 · `CLAUDE.md` que funciona (40 min) · iniciante

**Objetivo:** ver a diferença entre instrução vaga e instrução verificável.

1. Faça um backup: `cp CLAUDE.md /tmp/claude-md.bak`.
2. Substitua a seção "Convenções" por uma versão **vaga**: apenas `- escreva código limpo`.
3. `/clear`, depois: *"adicione um método `arquivar(id)` ao repositório"*.
4. Anote: seguiu o estilo do projeto? Escreveu teste? Usou o relógio injetado?
5. Restaure o `CLAUDE.md` original. `/clear`. Repita o mesmo pedido.
6. Compare os dois resultados lado a lado.

**Critério:** você consegue apontar **três diferenças concretas** entre os dois resultados.

---

## Lab 4 · Permissões calibradas (30 min) · iniciante

**Objetivo:** reduzir prompts sem perder o freio.

1. Trabalhe 15 minutos em modo `default`. Anote todo comando que exigiu aprovação.
2. Rode `/fewer-permission-prompts` e veja o que ele propõe.
3. Compare com a sua anotação: ele acertou?
4. Adicione ao `.claude/settings.json` só o que é comprovadamente seguro.
5. Peça: *"apague todos os arquivos de teste"*. Confirme que a regra de negação atua.
6. Confira o resultado em `/permissions`.

**Critério:** você tem uma allowlist justificada, item a item, e uma denylist que funciona.

---

## Lab 5 · Seu primeiro hook (45 min) · intermediário

**Objetivo:** a passagem de "pedir" para "obrigar".

1. Escreva `.claude/hooks/sem-console-log.sh`: bloqueia `Edit`/`Write` cujo conteúdo tenha
   `console.log` em arquivos de `src/`.
2. `chmod +x`.
3. **Teste sem abrir sessão** (é o passo que separa quem sofre de quem não sofre):
   ```bash
   echo '{"tool_name":"Write","tool_input":{"file_path":"'"$PWD"'/src/x.js","content":"console.log(1)"}}' \
     | .claude/hooks/sem-console-log.sh
   ```
   Deve imprimir JSON com `permissionDecision: "deny"`.
4. Teste o caso que **deve passar**: conteúdo sem `console.log`. Deve sair vazio, código 0.
5. Registre em `settings.json` com matcher `Edit|Write`.
6. Na sessão: *"adicione um console.log de depuração em src/servidor.js"*. Deve ser barrado.
7. Rode `npm run verificar` e confirme que ele valida o hook novo.

**Critério:** o hook bloqueia o caso ruim, deixa passar o bom, e o validador aprova.

---

## Lab 6 · O hook que fecha o laço (45 min) · intermediário

**Objetivo:** ver o agente se corrigindo sozinho.

1. O `PostToolUse` já está configurado no projeto-modelo. Confirme com `/hooks`.
2. Peça: *"em src/tarefas.js, mude a prioridade padrão de 'media' para 'baixa'"*.
3. **Observe:** o hook roda a suíte, ela falha, e o agente recebe o erro no mesmo turno.
4. Anote o que ele fez a seguir: reverteu? consertou o teste (errado!)? perguntou?
5. Desligue o hook (comente no `settings.json`), `/clear`, repita o passo 2.
6. Compare os dois comportamentos.

**Critério:** você viu, com seus olhos, a diferença entre laço fechado e laço aberto.

---

## Lab 7 · Contexto sob controle (40 min) · intermediário

**Objetivo:** medir e reduzir contexto.

1. Numa sessão longa, rode `/context all`. Anote os cinco maiores consumidores.
2. Peça algo que gere saída volumosa: *"rode os testes em modo verboso e me explique cada um"*.
3. `/context all` de novo. Quanto cresceu?
4. Escreva um hook `PreToolUse` que reescreve `node --test` para `node --test 2>&1 | tail -40`
   usando `updatedInput`.
5. `/clear`, repita o passo 2, meça de novo.
6. Calcule a economia percentual.

**Critério:** você tem dois números e sabe explicar a diferença entre eles.

---

## Lab 8 · Regra com escopo de caminho (30 min) · intermediário

**Objetivo:** pagar contexto só onde ele rende.

1. Leia [`.claude/rules/testes.md`](07-projeto-modelo/.claude/rules/testes.md).
2. `/clear` e rode `/context`. A regra **não** deve aparecer.
3. Peça: *"leia test/tarefas.test.js e resuma o que ele cobre"*.
4. `/context` de novo — agora a regra apareceu.
5. Crie uma segunda regra, `.claude/rules/http.md`, com `paths: ["src/servidor.js"]`,
   contendo três convenções de HTTP.
6. Verifique que ela só carrega ao tocar naquele arquivo.

**Critério:** você demonstrou o carregamento condicional em `/context`, não por confiança.

---

## Lab 9 · Skill de procedimento (45 min) · intermediário

**Objetivo:** empacotar um processo que a ordem importa.

1. Leia [`novo-endpoint/SKILL.md`](07-projeto-modelo/.claude/skills/novo-endpoint/SKILL.md).
2. Rode `/novo-endpoint PATCH /tarefas/:id alterar o título de uma tarefa`.
3. Acompanhe: ele seguiu domínio → teste → HTTP → teste?
4. Desfaça tudo (`git checkout -- .`).
5. Agora peça a **mesma coisa** em linguagem natural, sem a skill.
6. Compare: onde ele começou? A regra de negócio vazou para `servidor.js`?
7. Escreva sua própria skill: `/preparar-release` — roda testes, verifica, gera changelog
   a partir de `git log`.

**Critério:** você tem uma skill sua funcionando e sabe dizer o que a ordem imposta evitou.

---

## Lab 10 · Subagente com poder restrito (45 min) · avançado

**Objetivo:** isolar contexto e restringir capacidade.

1. Faça uma mudança pequena em `src/servidor.js` (introduza de propósito um `500` onde
   deveria ser `400`).
2. Peça: *"use o agente revisor-api para revisar o que mudou"*.
3. Ele pegou o erro? Respeitou o formato de saída?
4. Rode `/context` **antes e depois**. Quanto do trabalho dele entrou no seu contexto?
5. Peça explicitamente: *"revisor-api, conserte o problema que você encontrou"*.
   Ele **não deve conseguir** — `disallowedTools: Edit, Write`.
6. Crie um segundo subagente, `explorador`, com `tools: Read, Grep, Glob` e `model: haiku`.
   Use-o para mapear onde `ErroDeValidacao` é lançado.

**Critério:** você mediu a economia de contexto e comprovou a restrição de poder.

---

## Lab 11 · Headless e CI (60 min) · avançado

**Objetivo:** usar o agente dentro de software.

1. ```bash
   claude -p "Quantos testes tem test/servidor.test.js? Responda só o número." \
     --allowedTools "Read" --output-format json | jq -r '.result'
   ```
2. Agora com esquema:
   ```bash
   git diff HEAD~1 | claude --bare -p "Analise este diff." \
     --max-turns 3 --max-budget-usd 0.50 --output-format json \
     --json-schema '{"type":"object","properties":{
        "aprovado":{"type":"boolean"},
        "problemas":{"type":"array","items":{"type":"string"}}},
        "required":["aprovado","problemas"]}' | jq '.structured_output'
   ```
   > Se der `Not logged in`, é a pegadinha do `--bare`: defina `ANTHROPIC_API_KEY`
   > ou remova o `--bare` ([`23`](23-headless-e-sdk.md)).
3. Escreva `revisar.sh` que sai com código diferente de zero quando `aprovado` for falso.
4. Adicione como script do `package.json` e rode.
5. **Opcional:** monte o workflow do GitHub Actions do [`06`](06-exemplos.md), exemplo 7.

**Critério:** você tem um portão automatizado que **falha** de verdade quando deve falhar.

---

## Lab 12 · Repositório inteiro preparado (120 min) · avançado

**Objetivo:** aplicar tudo em um repositório **seu**.

Num projeto real seu, entregue:

1. `CLAUDE.md` com menos de 200 linhas, só com o que o agente não descobre lendo o código.
2. `.claude/settings.json` com permissões `allow`/`ask`/`deny` justificadas.
3. Um hook `PostToolUse` que roda a verificação mais rápida disponível (teste, `tsc`, lint).
4. Um hook `PreToolUse` que protege o que é sensível no seu contexto.
5. Uma regra em `.claude/rules/` com `paths:`.
6. Uma skill para o procedimento que você mais repete.
7. Um subagente revisor que conhece o **seu** domínio.
8. Um script de verificação da configuração — adapte
   [`verificar-configuracao.mjs`](07-projeto-modelo/scripts/verificar-configuracao.mjs).

**Critério final:**

```bash
npm run verificar      # (ou equivalente) — 0 problemas
```

E o teste de fogo: **peça a um colega para clonar o repositório, abrir o Claude Code e fazer
uma tarefa pequena.** Se funcionar sem você explicar nada, você chegou lá.

---

## Autoavaliação

Depois dos 12:

- [ ] Sei explicar o laço agêntico apontando para a tela.
- [ ] Uso modo plano por reflexo em tarefa não trivial.
- [ ] Interrompo cedo sem hesitar.
- [ ] Sei se um problema é de `CLAUDE.md`, de permissão ou de hook — sem pensar.
- [ ] Já escrevi e **testei fora da sessão** pelo menos dois hooks.
- [ ] Sei medir contexto e reduzi-lo com número, não com sensação.
- [ ] Tenho uma skill e um subagente que uso de verdade.
- [ ] Rodei o agente em automação com teto de gasto.
- [ ] Um colega usou minha configuração sem eu explicar.

Sete ou mais: você é competente. Nove: você é a referência do seu time.
