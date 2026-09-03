# 70 · Prática — 14 laboratórios progressivos

`Nível: iniciante → avançado` · `01/09/2026`

---

**Como usar:** faça na ordem. Cada laboratório tem *objetivo*, *passos*,
*critério de aceitação* (como saber que deu certo) e *o que você aprendeu*.
Não pule o critério de aceitação — é ele que distingue "rodou" de "está certo".

Ambiente: qualquer instalação do [03](03-instalacao.md).

---

## Nível 1 — fundamentos (labs 1 a 4)

### Lab 1 · Contar itens

**Objetivo:** internalizar cardinalidade.

1. `Manual Trigger` → `Code` que devolve 7 itens:
   ```javascript
   return Array.from({ length: 7 }, (_, i) => ({ json: { n: i + 1 } }));
   ```
2. Acrescente um `Filter` com `n` par.
3. Acrescente um `Edit Fields` com um campo novo.
4. Acrescente um `Aggregate` (*All Item Data*).

**Aceitação:** você prevê, **antes de rodar**, a contagem em cada fio
(7 → 3 → 3 → 1) e acerta.

**Aprendeu:** todo nó tem um fator de cardinalidade ([12](12-o-modelo-de-dados.md)).

---

### Lab 2 · Um item com lista vs. lista de itens

**Objetivo:** matar o mal-entendido nº 1.

1. `Code` que devolve **um** item com `{ pedidos: [ {id:1}, {id:2}, {id:3} ] }`.
2. Ligue um `Edit Fields` que crie `marcado: true`. **Quantas vezes ele roda?**
3. Insira um `Split Out` no campo `pedidos` antes dele. **E agora?**
4. Volte ao formato original com `Aggregate`.

**Aceitação:** você explica em voz alta por que o passo 2 rodou uma vez e o 3, três.

**Aprendeu:** Split Out / Aggregate ([exemplo 2](06-exemplos.md#exemplo-2--um-item-com-lista-vs-lista-de-itens-o-mal-entendido-nº-1)).

---

### Lab 3 · Webhook eco

**Objetivo:** primeiro endpoint.

Refaça o [04-como-comecar.md](04-como-comecar.md), mas acrescente:
- responder `400` quando o corpo não tiver `nome`;
- devolver o cabeçalho `user-agent` no corpo da resposta.

**Aceitação:**
```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:5678/webhook/eco -d '{}' -H 'Content-Type: application/json'
# 400
curl -s -X POST localhost:5678/webhook/eco -H 'Content-Type: application/json' -d '{"nome":"Ana"}' | grep -q user_agent && echo OK
```

**Aprendeu:** envelope do webhook, Respond to Webhook, códigos de status.

---

### Lab 4 · Consumir uma API pública

**Objetivo:** o nó HTTP Request.

1. `Manual Trigger` → `HTTP Request` para `https://api.github.com/repos/n8n-io/n8n`.
2. `Edit Fields` deixando só `full_name`, `stargazers_count`, `open_issues_count`.
3. Troque para `https://api.github.com/repos/n8n-io/n8n/issues?per_page=5`.
   **Quantos itens saem agora? Por quê?**

**Aceitação:** você explica por que o passo 1 gera 1 item e o 3 gera 5.

**Aprendeu:** o HTTP Request converte array de resposta em itens automaticamente.

---

## Nível 2 — construir de verdade (labs 5 a 9)

### Lab 5 · Paginação sem laço

**Objetivo:** usar recurso pronto em vez de reinventar.

1. `HTTP Request` para `https://api.github.com/repos/n8n-io/n8n/issues`.
2. Ligue *Pagination*: `Update a Parameter in Each Request`, tipo `Query`,
   nome `page`, valor `{{ $pageCount + 1 }}`, completa quando a resposta for vazia.
3. **Ligue *Limit Pages Fetched* = 3.** Não pule este passo.

**Aceitação:** você recebe ~3 páginas de itens e explica **por que limitar páginas
é obrigatório**.

**Aprendeu:** paginação nativa; o perigo do laço infinito com custo por chamada.

---

### Lab 6 · Tratar erro por item

**Objetivo:** o padrão mais importante de produção.

1. `Code` gerando 5 itens, um deles com URL inválida (`https://nao-existe-xyz.invalid`).
2. `HTTP Request` usando `{{ $json.url }}`.
3. *Settings → On Error → Continue (using error output)*.
4. Ramo de sucesso: `Edit Fields` marcando `ok: true`.
5. Ramo de erro: `Code` que extrai `i.error?.message`.
6. `Merge` (append) para juntar os dois ramos.

**Aceitação:** a execução termina **verde**, com 4 sucessos e 1 falha registrada.

**Aprendeu:** error output, o padrão do [exemplo 6](06-exemplos.md#exemplo-6--tratar-erro-por-item-sem-derrubar-o-fluxo).

---

### Lab 7 · Idempotência de verdade

**Objetivo:** provar que reenviar não duplica.

Use o [projeto-modelo](07-projeto-modelo/README.md).

1. Envie o mesmo pedido **3 vezes**.
2. Confirme no banco: `select count(*) from pedidos where pedido_id = 'X';` → **1**.
3. Agora **remova** o `ON CONFLICT DO NOTHING` da query e repita.
4. Restaure.

**Aceitação:** você observa o erro de chave duplicada no passo 3 e explica por que
`ON CONFLICT` é melhor que um `SELECT` antes do `INSERT`.

**Aprendeu:** idempotência mora no banco, não no `if` ([18](18-erros-e-confiabilidade.md)).

---

### Lab 8 · Fluxo de erro global

1. Crie o fluxo `Alerta de falhas` do [exemplo 7](06-exemplos.md#exemplo-7--fluxo-de-erro-global-error-workflow).
2. Configure-o como *Error Workflow* de outro fluxo.
3. Force a falha (`Stop and Error`, ou desligue o banco).

**Aceitação:** o fluxo de alerta rodou e o registro traz o `execution.url` correto,
que abre a execução que falhou.

**Aprendeu:** sem Error Workflow, falha em produção é silenciosa.

---

### Lab 9 · Sub-workflow como biblioteca

1. Crie `util-normalizar-telefone` ([exemplo 10](06-exemplos.md#exemplo-10--sub-workflow-reutilizável)).
2. Chame-o de dois fluxos diferentes.
3. Teste os **dois** modos: *once with all items* e *once for each item*, com 20 itens.
4. Compare os tempos e o número de execuções no histórico.

**Aceitação:** você mede a diferença e sabe justificar a escolha.

**Aprendeu:** composição e o custo real de isolar por item.

---

## Nível 3 — operação (labs 10 a 12)

### Lab 10 · Encher e podar o banco

**Objetivo:** ver o problema nº 1 de produção acontecer.

1. Crie um fluxo com `Schedule Trigger` a cada minuto que gere **1.000 itens**.
2. Deixe rodar 15 minutos.
3. Meça: `select pg_size_pretty(pg_total_relation_size('execution_data'));`
4. Ligue `EXECUTIONS_DATA_PRUNE=true` e `EXECUTIONS_DATA_MAX_AGE=1`, reinicie, espere.
5. Meça de novo. **Despublique o fluxo.**

**Aceitação:** você viu o banco crescer e depois encolher, e sabe quanto custa por
execução no seu caso.

**Aprendeu:** por que a poda entra no primeiro dia ([21](21-escala-e-producao.md)).

---

### Lab 11 · Queue mode

1. Monte o compose de [21-escala-e-producao.md](21-escala-e-producao.md#23-compose-de-referência).
2. Suba com **1** worker; dispare 50 webhooks em paralelo:
   ```bash
   seq 50 | xargs -P50 -I{} curl -s -o /dev/null -X POST localhost:5678/webhook/pedido \
     -H 'Content-Type: application/json' \
     -d '{"pedido_id":"L11-{}","cliente":"Teste","valor":10,"itens":[{"sku":"A","qtd":1}]}'
   ```
3. Observe a fila: `docker compose exec redis redis-cli llen bull:jobs:wait`.
4. Suba para **3** workers e repita. Compare o tempo total.
5. Confirme que o banco tem exatamente 50 linhas.

**Aceitação:** o tempo cai com mais workers e **não há duplicata** — a idempotência
resistiu à concorrência.

**Aprendeu:** queue mode, concorrência e por que idempotência é pré-requisito de escala.

---

### Lab 12 · Backup e restauração de verdade

1. Faça `pg_dump` e guarde a `N8N_ENCRYPTION_KEY` **em outro lugar**.
2. `docker compose down -v` (⚠️ apaga tudo).
3. Suba de novo e restaure **só o banco**, com uma chave **diferente**.
4. Abra uma credencial. O que acontece?
5. Restaure com a chave **correta**. E agora?

**Aceitação:** você viu, com os próprios olhos, o que significa perder a chave.

**Aprendeu:** backup do banco sem a chave não é backup ([22](22-seguranca.md)).

---

## Nível 4 — IA (labs 13 e 14)

### Lab 13 · Chain antes de agente

1. `Chat Trigger` → **Basic LLM Chain** → modelo (Ollama local, se possível).
2. Peça uma classificação: "responda apenas com uma das palavras: RECLAMAÇÃO,
   DÚVIDA, ELOGIO".
3. Ligue um `Structured Output Parser` com esquema `{ categoria: enum }`.
4. Um `Switch` roteia por categoria, **com fallback conectado**.
5. Agora refaça com **AI Agent** e compare: número de chamadas, tempo, previsibilidade.

**Aceitação:** você conclui, com dados seus, que a chain é melhor **para este caso**.

**Aprendeu:** agente não é padrão ([24](24-ia-e-agentes.md#2-agent--chain-qual-usar)).

---

### Lab 14 · Agente com ferramenta determinística

1. `Chat Trigger` → `AI Agent` + Chat Model + Simple Memory.
2. Crie um sub-workflow `consultar_pedido` que consulta o banco do projeto-modelo.
3. Ligue-o como **Call n8n Workflow Tool**, com descrição explícita:
   *"Use quando a pergunta citar um número de pedido no formato P-NNNN.
   Recebe pedido_id. Devolve vazio se não existir."*
4. Pergunte: "qual o status do pedido P-1?" e "quanto é 2+2?".
5. **Piore a descrição** de propósito (`"ferramenta de dados"`) e repita.

**Aceitação:** com a descrição boa, o agente usa a ferramenta só quando deve; com a
ruim, erra. Você mediu a diferença.

**Aprendeu:** a descrição da ferramenta é o principal parâmetro de qualidade de um
agente — mais que o modelo.

---

## Desafio final

Construa, sozinho, um sistema completo:

> **Monitor de mudanças.** A cada 30 minutos, consulte três endpoints públicos.
> Detecte **o que mudou** desde a última vez. Notifique só as mudanças. Registre
> tudo. Não notifique duas vezes a mesma mudança. Sobreviva a reinício.
> Trate falha de qualquer endpoint sem perder os outros dois.

**Critérios de aceitação:**

- [ ] Reiniciar o n8n no meio não gera notificação duplicada nem perde mudança.
- [ ] Um endpoint fora do ar não impede os outros dois de serem verificados.
- [ ] Existe Error Workflow configurado e ele foi testado.
- [ ] Existe heartbeat que avisa se o fluxo **parar de rodar**.
- [ ] A poda de execuções está ligada.
- [ ] Um script externo testa o sistema de ponta a ponta.
- [ ] Outra pessoa consegue entender o canvas sem você explicar.

Se você fecha esses sete itens, você sabe n8n em nível profissional. Sério.

---

*Anterior: [65-estado-da-arte.md](65-estado-da-arte.md) · Próximo: [75-armadilhas.md](75-armadilhas.md)*
