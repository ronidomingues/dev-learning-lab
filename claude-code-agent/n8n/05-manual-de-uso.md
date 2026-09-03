# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Referência` · `n8n 2.36.9 · verificado em 01/09/2026`

---

Organizado **por tarefa**, não por ordem alfabética. Use o índice, não leia de cabo a rabo.

- [1. Escolher o nó certo](#1-escolher-o-nó-certo-por-tarefa)
- [2. Expressões](#2-expressões)
- [3. Variáveis e métodos embutidos](#3-variáveis-e-métodos-embutidos)
- [4. Funções de transformação de dados](#4-funções-de-transformação-de-dados)
- [5. Datas com Luxon](#5-datas-com-luxon)
- [6. Node Code](#6-node-code)
- [7. HTTP Request](#7-http-request-o-nó-coringa)
- [8. Configurações de nó que salvam produção](#8-configurações-de-nó-que-salvam-produção)
- [9. Configurações de workflow](#9-configurações-de-workflow)
- [10. CLI](#10-cli-linha-de-comando)
- [11. Variáveis de ambiente essenciais](#11-variáveis-de-ambiente-essenciais)
- [12. API pública](#12-api-pública-rest)
- [13. Atalhos de teclado](#13-atalhos-de-teclado)
- [14. Obsoleto — não use](#14-obsoleto--não-use)

---

## 1. Escolher o nó certo, por tarefa

### Iniciar um fluxo

| Quero | Nó |
|---|---|
| Receber uma chamada HTTP | **Webhook** |
| Rodar em horário/intervalo | **Schedule Trigger** |
| Rodar quando eu mandar | **Manual Trigger** |
| Um formulário pronto | **n8n Form Trigger** |
| Uma janela de chat | **Chat Trigger** |
| Reagir a falhas de outros fluxos | **Error Trigger** |
| Ser chamado por outro fluxo | **Execute Sub-workflow Trigger** |
| Reagir a evento de um app | Gatilho do app (`Gmail Trigger`, `Slack Trigger`, …) |

### Mexer nos dados

| Quero | Nó | Observação |
|---|---|---|
| Criar/renomear/remover campos | **Edit Fields (Set)** | O mais usado de todos |
| Transformar com código | **Code** | JavaScript ou Python |
| Manter só itens que passam num teste | **Filter** | Uma saída só |
| Separar em caminhos | **IF** (2 saídas) / **Switch** (N saídas) | |
| Um item com array → vários itens | **Split Out** | Resolve o erro nº 2 do iniciante |
| Vários itens → um item com array | **Aggregate** | |
| Juntar dois fluxos | **Merge** | Modos: append, combine by key, combine by position, SQL |
| Remover duplicados | **Remove Duplicates** | Inclusive entre execuções |
| Ordenar | **Sort** | |
| Limitar quantidade | **Limit** | |
| Resumir (soma, média, contagem) | **Summarize** | Um `GROUP BY` visual |
| Renomear muitas chaves | **Rename Keys** | |
| Converter tipos | **Edit Fields** com tipo explícito | |

### Arquivos e formatos

| Quero | Nó |
|---|---|
| Ler/gravar arquivo no disco do servidor | **Read/Write Files from Disk** |
| Transformar itens em arquivo (CSV, JSON, XLSX, texto) | **Convert to File** |
| Ler um arquivo binário e virar itens | **Extract from File** |
| Compactar/descompactar | **Compression** |
| Editar imagem | **Edit Image** |
| Criptografia/hash | **Crypto** |

### Fluxo e tempo

| Quero | Nó | Cuidado |
|---|---|---|
| Repetir em lotes | **Loop Over Items (Split in Batches)** | Precisa do fio de volta para o próprio nó |
| Esperar | **Wait** | Espera longa libera o processo e retoma depois |
| Abortar com erro claro | **Stop and Error** | |
| Chamar outro fluxo | **Execute Sub-workflow** | Modo *Run once with all items* vs *for each item* muda tudo |
| Não fazer nada (juntar fios) | **No Operation** | Útil para organizar o canvas |

### IA

| Quero | Nó |
|---|---|
| Um agente com ferramentas | **AI Agent** |
| Só chamar um modelo | **Basic LLM Chain** ou o nó do provedor (`OpenAI`, `Anthropic`, `Google Gemini`) |
| Busca semântica | **Vector Store** (Qdrant, PGVector, Pinecone, In-Memory) |
| Memória de conversa | **Memory** (Buffer Window, Postgres, Redis) |
| Dar uma ferramenta ao agente | Qualquer nó marcado como **Tool**, ou **MCP Client** |
| Expor seu fluxo como ferramenta MCP | **MCP Server Trigger** |
| Extrair dado estruturado do texto | **Information Extractor** / *Structured Output Parser* |
| Barreiras de segurança | **Guardrails** |

---

## 2. Expressões

Sintaxe: `{{ ... }}` dentro de um campo em modo *Expression*. É **JavaScript**,
avaliado sobre o item corrente.

| Escrever | Devolve |
|---|---|
| `{{ $json.campo }}` | Campo do item atual |
| `{{ $json["campo com espaço"] }}` | Campo com nome difícil |
| `{{ $json.a?.b ?? 'padrão' }}` | Acesso seguro com valor padrão |
| `{{ $binary.arquivo.fileName }}` | Nome do arquivo binário |
| `{{ $('Nó Anterior').item.json.x }}` | Campo do **item correspondente** de outro nó |
| `{{ $('Nó').first().json.x }}` | Primeiro item daquele nó |
| `{{ $('Nó').last().json.x }}` | Último item |
| `{{ $('Nó').all() }}` | Todos os itens (array) |
| `{{ $('Nó').all()[3].json.x }}` | Item por índice |
| `{{ $input.all().length }}` | Quantos itens entraram neste nó |
| `{{ $itemIndex }}` | Índice do item atual (só em expressões) |
| `{{ $now }}` | Agora (objeto Luxon `DateTime`) |
| `{{ $today }}` | Hoje à meia-noite |
| `{{ $execution.id }}` | ID da execução |
| `{{ $workflow.name }}` | Nome do fluxo |
| `{{ $vars.minhaVar }}` | Variável do ambiente (recurso licenciado) |
| `{{ $env.MINHA_VAR }}` | Variável de ambiente do host (⚠️ desligável) |

**Concatenar:** `{{ 'Olá, ' + $json.nome + '!' }}` ou `` {{ `Olá, ${$json.nome}!` }} ``

**Cuidado com o `=` invisível:** no JSON do workflow, um campo em modo expressão
começa com `=`. Por isso `"value": "={{ $json.x }}"`. Ao editar JSON na mão,
esquecer o `=` faz o texto virar literal.

---

## 3. Variáveis e métodos embutidos

Tabela conferida na documentação oficial em 01/09/2026. A coluna final diz se
funciona também dentro do **node Code** (não é tudo).

| Variável | O que é | No Code node? |
|---|---|---|
| `$json` | O item atual | ✅ (em modo *each item*: `$json`; em *all items*, use `items`) |
| `$binary` | Binários do item atual | ✅ |
| `$input.all()` / `.first()` / `.last()` / `.item` | Itens de entrada | ✅ |
| `$('<nó>')` | Acessa a saída de outro nó | ✅ |
| `$('<nó>').isExecuted` | Se aquele nó já rodou | ✅ |
| `$prevNode.name` / `.outputIndex` / `.runIndex` | De onde veio o dado atual | ✅ |
| `$runIndex` | Quantas vezes este nó já rodou (base 0) | ✅ |
| `$itemIndex` | Índice do item | ❌ |
| `$execution.id` / `.mode` / `.resumeUrl` / `.customData` | Sobre a execução | ✅ |
| `$workflow.id` / `.name` / `.active` | Sobre o fluxo | ✅ |
| `$nodeVersion` | Versão do nó atual | ✅ |
| `$version` | Versão do nó | ❌ |
| `$vars` | Variáveis do ambiente | ✅ |
| `$secrets` | Cofre externo de segredos (Enterprise) | ❌ |
| `$env` | Variáveis de ambiente do processo n8n | ✅ |
| `$getWorkflowStaticData(type)` | Estado que **sobrevive entre execuções** | ✅ |
| `$now`, `$today` | Data/hora (Luxon) | ✅ |
| `$if()`, `$jmespath()`, `$max()`, `$min()`, `$ifEmpty()` | Funções auxiliares | ❌ **só no editor de expressões** |

> **Armadilha documentada:** o node Code roda **JavaScript puro com Luxon nativo**,
> não o motor de expressões do n8n. Métodos marcados como "Custom n8n functionality"
> (por exemplo `DateTime.format()`) **não existem** lá. Sintoma: `... is not a function`,
> ou pior, resultado silenciosamente errado. Um caso concreto: nas expressões,
> `plus(7, 'days')` funciona; no Code node, o Luxon nativo só aceita `plus({ days: 7 })`
> — **e não dá erro**, só faz outra coisa.

### `$getWorkflowStaticData` — o único estado persistente sem banco

```javascript
const dados = $getWorkflowStaticData('global'); // ou 'node'
dados.ultimoId = dados.ultimoId ?? 0;
// ... use e altere
```
Serve para "lembrar" onde parou entre execuções (polling incremental, por exemplo).
**Não persiste em execução de teste** — o fluxo precisa estar publicado e ter sido
disparado por um gatilho de verdade.

---

## 4. Funções de transformação de dados

O n8n estende os tipos nativos com métodos utilitários, disponíveis **nas expressões**.
Os mais usados no dia a dia:

| Tipo | Método | Exemplo |
|---|---|---|
| String | `.toDateTime()` | `{{ $json.data.toDateTime() }}` |
| String | `.extractEmail()`, `.extractUrl()`, `.extractDomain()` | `{{ $json.texto.extractEmail() }}` |
| String | `.isEmail()`, `.isNumeric()`, `.isUrl()` | validação rápida |
| String | `.removeMarkdown()`, `.removeTags()` | limpar HTML/markdown |
| String | `.toSnakeCase()`, `.toTitleCase()` | |
| String | `.hash('sha256')` | chave de deduplicação |
| String | `.base64Encode()` / `.base64Decode()` | |
| Array | `.first()`, `.last()`, `.unique()`, `.sum()`, `.average()`, `.chunk(n)` | `{{ $json.valores.sum() }}` |
| Array | `.pluck('campo')` | extrai uma coluna |
| Array | `.compact()` | remove nulos/vazios |
| Object | `.keys()`, `.values()`, `.hasField('x')`, `.removeField('x')` | |
| Object | `.toJsonString()` | |
| Number | `.round(2)`, `.floor()`, `.format()` | |
| Todos | `$if(cond, a, b)` | ternário legível |
| Todos | `$ifEmpty(valor, padrão)` | |
| Todos | `$jmespath(obj, "expr")` | consulta em JSON aninhado |

Referência completa: [Expression reference](https://docs.n8n.io/build/work-with-data/transform-data/expression-reference.md).

---

## 5. Datas com Luxon

O n8n usa **Luxon**, não `moment` nem `Date`.

| Quero | Expressão |
|---|---|
| Agora em ISO | `{{ $now.toISO() }}` |
| Formatar | `{{ $now.toFormat('dd/MM/yyyy HH:mm') }}` |
| Somar 7 dias (expressão) | `{{ $now.plus(7, 'days') }}` |
| Somar 7 dias (Code node) | `$now.plus({ days: 7 })` |
| Início do mês | `{{ $now.startOf('month') }}` |
| Diferença em dias | `{{ $now.diff($json.data.toDateTime(), 'days').days }}` |
| Outro fuso | `{{ $now.setZone('America/Sao_Paulo').toFormat('HH:mm') }}` |
| String → data | `{{ DateTime.fromFormat($json.d, 'dd/MM/yyyy') }}` |

> Fuso é fonte inesgotável de bug. O fuso padrão vem de `GENERIC_TIMEZONE`; cada
> workflow pode sobrescrevê-lo em *Settings → Timezone*. **Guarde sempre em UTC,
> formate na hora de mostrar.**

---

## 6. Node Code

Dois modos:

| Modo | O código roda | `return` deve devolver |
|---|---|---|
| **Run Once for All Items** | uma vez | array de itens |
| **Run Once for Each Item** | uma vez por item | um item |

```javascript
// Modo: all items
const itens = $input.all();                    // [{json:{...}}, ...]
return itens
  .filter(i => i.json.valor > 100)
  .map(i => ({ json: { ...i.json, faixa: 'alto' } }));
```

```javascript
// Modo: each item
return { json: { ...$json, total: $json.qtd * $json.preco } };
```

**O que o Code node NÃO faz:** acessar o sistema de arquivos e fazer requisições
HTTP. Isso é proposital — use os nós **Read/Write Files from Disk** e **HTTP Request**.

**Módulos externos:** só em instância autogerida, e é preciso liberar por variável
de ambiente ([guia oficial](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/enable-modules-in-code-node.md)).
No Cloud, você tem apenas `crypto` e `moment`.

**Python:** desde n8n 2.0, só o **Python nativo** via task runners. O antigo Pyodide
(Python compilado para WebAssembly) **foi removido**. Diferenças que quebram código antigo:
- só `_items` (modo all) e `_item` (modo each) existem — as outras variáveis embutidas, não;
- **acesso só por colchetes**: `item["json"]["campo"]`, e não `item.json.campo`;
- bibliotecas só se a imagem `n8nio/runners` as incluir **e** elas estiverem na lista de permissão.

---

## 7. HTTP Request (o nó coringa)

| Campo | Uso |
|---|---|
| Method / URL | O básico |
| Authentication | *Predefined* (usa credencial de um serviço conhecido) ou *Generic* (Basic, Header, OAuth2, Query) |
| Send Query / Headers / Body | Ligue e preencha por pares chave-valor, ou como JSON |
| **Batching** | Agrupa itens e insere pausa — evita bater no limite de taxa da API |
| **Pagination** | Paginação automática (por página, por cursor, por link `next`) sem laço manual |
| **Retry On Fail** | Tentativas com intervalo |
| Response → Format | `JSON`, `Text`, `File` |
| Response → Never Error | Não falha em status 4xx/5xx; você trata o código na mão |
| Optimize Response | Reduz o payload devolvido (útil quando o nó vira ferramenta de IA) |

> **Paginação e batching são os dois recursos que o pessoal reimplementa com Code
> sem saber que existem.** Antes de escrever um laço, olhe as opções do nó.

---

## 8. Configurações de nó que salvam produção

Abra qualquer nó → aba **Settings**:

| Opção | O que faz | Quando usar |
|---|---|---|
| **Always Output Data** | Se o nó não produzir nada, emite um item vazio | Evita que o ramo morra em silêncio |
| **Execute Once** | Roda uma vez só, mesmo com N itens | Notificação de resumo |
| **Retry On Fail** + *Max Tries* + *Wait Between Tries* | Repete o nó | API instável. Só se a operação for **idempotente** |
| **On Error** | `Stop workflow` (padrão) · `Continue` · `Continue (using error output)` | *Error output* dá ao nó uma segunda saída vermelha — o jeito certo de tratar falha por item |
| **Notes** / *Display note in flow* | Documentação no canvas | Seu eu do futuro agradece |

---

## 9. Configurações de workflow

*Menu ⋯ → Settings*:

| Opção | Efeito |
|---|---|
| **Error Workflow** | Fluxo chamado quando este falhar. **Configure sempre** |
| **Timezone** | Sobrescreve o `GENERIC_TIMEZONE` neste fluxo |
| **Save failed / successful production executions** | Quanto histórico guardar. Desligar o "success" economiza muito banco |
| **Save manual executions** | Histórico dos seus testes |
| **Timeout Workflow** | Mata a execução após N segundos |
| **Caller policy** | Quem pode chamar este fluxo como sub-workflow |
| **Execution order** | `v1` (recomendado) ou `v0` (legado) |

---

## 10. CLI (linha de comando)

Comandos reais do n8n 2.36.9 (`n8n --help`, executado em 01/09/2026).
No Docker: `docker compose exec n8n n8n <comando>`.

| Comando | Para quê |
|---|---|
| `n8n start` | Sobe a interface e os fluxos ativos |
| `n8n worker` | Sobe um worker (queue mode) |
| `n8n webhook` | Sobe um processo só para webhooks de produção |
| `n8n execute --id=<id>` | Executa um fluxo (aceita `--rawOutput`) |
| `n8n execute-batch` | Executa vários — útil em teste de regressão |
| `n8n list:workflow` | Lista `id|nome` |
| `n8n export:workflow --all --separate --output=<dir>` | Exporta fluxos |
| `n8n import:workflow --separate --input=<dir>` | Importa fluxos |
| `n8n export:credentials --all [--decrypted]` | Exporta credenciais (⚠️ `--decrypted` = texto claro) |
| `n8n import:credentials --input=<arq>` | Importa credenciais |
| `n8n export:entities` / `import:entities` | Exporta/importa entidades do banco |
| `n8n publish:workflow` | **Publica** uma versão do fluxo |
| `n8n unpublish:workflow` | Despublica |
| `n8n update:workflow` | **[DEPRECADO]** use `publish:`/`unpublish:` |
| `n8n audit` | Relatório de auditoria de segurança da instância |
| `n8n user-management:reset` | ⚠️ Zera os usuários (recuperar acesso perdido) |
| `n8n mfa:disable` | Desliga MFA de um usuário |
| `n8n license:info` / `license:clear` | Licença |
| `n8n db:revert` | Desfaz a última migração de banco |
| `n8n export:nodes` | Exporta os tipos de nó para JSON |

**Duas pegadinhas verificadas na prática:**

1. **Importar exige `id` no JSON.** Um arquivo de workflow sem a chave `id` falha com
   `SQLITE_CONSTRAINT: NOT NULL constraint failed: workflow_entity.id`.
2. **Alterações feitas pela CLI não aparecem numa instância em execução.**
   O próprio comando avisa: *"Changes will not take effect if n8n is running.
   Please restart n8n"*. Reinicie o contêiner depois de ativar/publicar pela CLI.

---

## 11. Variáveis de ambiente essenciais

Só as que você realmente usa. A lista completa está na
[documentação oficial](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables.md).

| Variável | Padrão | Para quê |
|---|---|---|
| `N8N_ENCRYPTION_KEY` | gerada | Cifra as credenciais. **Guarde** |
| `N8N_HOST` / `N8N_PORT` / `N8N_PROTOCOL` | `localhost` / `5678` / `http` | Como o editor monta URLs |
| `WEBHOOK_URL` | — | URL pública dos webhooks (atrás de proxy/túnel) |
| `N8N_PROXY_HOPS` | `0` | Proxies à frente |
| `GENERIC_TIMEZONE` | `UTC` | Fuso dos agendamentos |
| `DB_TYPE` | `sqlite` | `postgresdb` em produção |
| `DB_POSTGRESDB_*` | — | Conexão com o Postgres |
| `EXECUTIONS_MODE` | `regular` | `queue` liga o modo fila |
| `QUEUE_BULL_REDIS_HOST` / `_PORT` | — | Redis do modo fila |
| `EXECUTIONS_DATA_PRUNE` | `true` | Poda o histórico |
| `EXECUTIONS_DATA_MAX_AGE` | `336` (h) | Idade máxima do histórico |
| `EXECUTIONS_DATA_PRUNE_MAX_COUNT` | `10000` | Teto de execuções guardadas |
| `N8N_DEFAULT_BINARY_DATA_MODE` | `filesystem` (regular) / `database` (queue) | Onde vive o binário. **O modo `memory` foi removido no 2.0** |
| `N8N_CONCURRENCY_PRODUCTION_LIMIT` | `-1` | Execuções simultâneas |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | `false` | Bloqueia `$env` nas expressões |
| `N8N_DIAGNOSTICS_ENABLED` | `true` | Telemetria — desligue se quiser |
| `N8N_DATA_TABLES_MAX_SIZE_BYTES` | 200 MiB | Teto das data tables |
| `N8N_PUBLIC_API_DISABLED` | `false` | Desliga a API pública |
| `NODE_EXTRA_CA_CERTS` | — | CA interna da empresa |

---

## 12. API pública (REST)

Autenticação por **API key** no cabeçalho `X-N8N-API-KEY` (crie em
*Settings → n8n API*). Base: `https://<seu-n8n>/api/v1`.

| Recurso | Exemplos |
|---|---|
| `/workflows` | listar, criar, atualizar, ativar, desativar |
| `/executions` | listar, ver, apagar |
| `/credentials` | criar, apagar (não devolve segredos) |
| `/tags`, `/projects`, `/users` | organização |
| `/datatables` | data tables |
| `/audit` | relatório de auditoria |
| `/source-control/pull` | puxar do Git (licenciado) |

```bash
curl -s https://seu-n8n/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY" | jq '.data[] | {id, name, active}'
```

Documentação com o OpenAPI: `https://<seu-n8n>/api/v1/docs`.

---

## 13. Atalhos de teclado

| Atalho | Ação |
|---|---|
| `Tab` | Abrir o painel de nós |
| `Ctrl/Cmd + S` | Salvar |
| `Ctrl/Cmd + C` / `V` | Copiar/colar nós (**funciona como JSON, fora do n8n também**) |
| `Ctrl/Cmd + A` | Selecionar tudo |
| `D` | Ativar/desativar o nó selecionado |
| `P` | Fixar (pin) os dados do nó |
| `F2` | Renomear nó |
| `Delete` | Remover |
| `Ctrl/Cmd + Z` / `Shift+Z` | Desfazer/refazer |
| `Ctrl/Cmd + Enter` | Executar o workflow |
| `1` / `0` | Ajustar zoom / voltar a 100% |
| `Shift + S` | Adicionar *sticky note* |

---

## 14. Obsoleto — não use

| Obsoleto | Desde | Use no lugar |
|---|---|---|
| Nós **Function** e **Function Item** | 0.198.0; **removidos no 3.0** | **Code** |
| Nó **Item Lists** | **removido no 3.0** | **Split Out**, **Aggregate**, **Sort**, **Limit**, **Remove Duplicates** |
| **Python via Pyodide** | removido no 2.0 | Python nativo com task runners |
| `N8N_RUNNERS_ENABLED` | depreciada no 2.0 | nada — já é o padrão |
| Modo de binário `memory` | removido no 2.0 | `filesystem` ou `database` |
| `n8n update:workflow` | depreciado no 2.x | `publish:workflow` / `unpublish:workflow` |
| Instalação por **npm/npx** | **removida no 3.0 (out/2026)** | Docker |
| **AI Agent** v1 (modos SQL, Conversational, OpenAI Functions, Plan-and-Execute, ReAct) | **removidos no 3.0** | AI Agent atual (Tools Agent) |
| `$getPairedItem` | **removido no 3.0** | `$('nó').item` / `itemMatching()` |
| Importar workflow por URL no editor | **removido no 3.0** | Colar o JSON |

---

## Autoteste

1. Qual nó converte "um item com um array" em "vários itens"? E o inverso?
2. Escreva a expressão que pega o campo `email` do **item correspondente** do nó
   chamado `Buscar Cliente`.
3. Por que `plus(7, 'days')` funciona na expressão e falha (silenciosamente) no
   node Code?
4. Cite dois recursos do nó HTTP Request que evitam escrever laços à mão.
5. Qual configuração de nó cria uma segunda saída para tratar erro por item?
6. Qual comando da CLI publica um workflow? Qual está depreciado?
7. Por que importar um workflow pela CLI pode falhar com `NOT NULL constraint failed`?
8. Quais variáveis controlam o crescimento do banco de execuções?
9. Onde vive o dado binário por padrão no n8n 2.x, e o que foi removido?
10. Cite três recursos removidos no n8n 3.0 e seus substitutos.

---

*Fontes: documentação oficial consultada em 01/09/2026 e `n8n --help` executado na
versão 2.36.9. Links: [Built-in methods](https://docs.n8n.io/build/code-in-n8n/use-built-in-shortcuts.md),
[Expression reference](https://docs.n8n.io/build/work-with-data/transform-data/expression-reference.md),
[v3.0 breaking changes](https://docs.n8n.io/changelog/v30-breaking-changes).*

*Anterior: [04-como-comecar.md](04-como-comecar.md) · Próximo: [06-exemplos.md](06-exemplos.md)*
