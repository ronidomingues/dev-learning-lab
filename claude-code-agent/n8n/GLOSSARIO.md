# Glossário

`Todos os termos técnicos usados neste curso` · `01/09/2026`

Termos em inglês aparecem como o campo os usa, com a tradução na definição.
Ordem alfabética. Links apontam para o arquivo que trata o assunto a fundo.

---

## A

**`.n8np` (pacote n8n)** — Formato de exportação de um conjunto (workflows, pastas,
projeto), com dependências de sub-workflow resolvidas. [23](23-ciclo-de-vida-e-versionamento.md)

**Agendador durável (*durable scheduler*)** — Modo em que os agendamentos ficam no
banco em vez da memória, sobrevivendo a reinício. Disponível a partir do n8n 2.36.0,
desligado por padrão. [16](16-gatilhos-e-webhooks.md)

**Agente (*AI Agent*)** — Nó raiz que deixa um modelo de linguagem decidir quais
ferramentas chamar e em que ordem. [24](24-ia-e-agentes.md)

**`Always Output Data`** — Configuração de nó que faz emitir um item vazio quando
não produziria nada, impedindo que o ramo morra em silêncio. [18](18-erros-e-confiabilidade.md)

**`Aggregate`** — Nó que transforma N itens em **um** item com um array. Inverso do
`Split Out`. [12](12-o-modelo-de-dados.md)

**`at-least-once` (ao menos uma vez)** — Garantia de que o trabalho acontece uma ou
mais vezes. É o que o n8n oferece. [60](60-teoria-avancada.md)

---

## B

**Batching (lotes)** — Agrupar itens e inserir pausa entre grupos, para respeitar
limite de taxa. Existe pronto no nó HTTP Request. [05](05-manual-de-uso.md)

**Binário (*binary data*)** — Arquivo carregado por um item, sob a chave `binary`,
identificado por **nome de propriedade** (não pelo nome do arquivo).
Armazenado em `filesystem`, `database` ou externo. [12](12-o-modelo-de-dados.md)

**Bull / BullMQ** — Biblioteca de fila sobre Redis usada pelo queue mode.
Aparece nas variáveis `QUEUE_BULL_*`. [21](21-escala-e-producao.md)

---

## C

**Canvas** — A tela onde se desenha o workflow.

**Cardinalidade** — Quantos itens um nó recebe e quantos produz. **A grandeza que
explica a maioria dos bugs.** [12](12-o-modelo-de-dados.md)

**Chain (cadeia)** — Nó raiz de IA com caminho fixo, sem decisão do modelo e **sem
memória**. Preferível ao agente quando o caminho é conhecido. [24](24-ia-e-agentes.md)

**Chunk** — Pedaço de documento indexado num RAG. Tamanho e sobreposição são o maior
fator de qualidade. [24](24-ia-e-agentes.md)

**Cluster node** — Arranjo de um **root node** com **sub-nodes** conectados por
linhas pontilhadas, que fornecem capacidade (modelo, memória, ferramenta). [24](24-ia-e-agentes.md)

**Code node** — Nó que executa JavaScript ou Python. Não acessa disco nem rede.
[17](17-code-node-e-task-runners.md)

**Community edition** — A edição gratuita. **Sem RBAC**, sem SSO, sem source
control. [80](80-custos-e-licencas.md)

**Community node** — Pacote npm de terceiros instalável como nó. Roda com os
privilégios do n8n. [14](14-nos-e-integracoes.md)

**Concorrência** — Quantas execuções de produção rodam ao mesmo tempo.
`N8N_CONCURRENCY_PRODUCTION_LIMIT` no modo regular; `--concurrency` por worker no
modo fila. [21](21-escala-e-producao.md)

**Conexão** — Aresta que liga uma **saída** de um nó a uma **entrada** de outro.
No JSON, indexada pelo **nome** do nó. [10](10-fundamentos.md)

**Credencial** — Segredo cifrado no banco com a `N8N_ENCRYPTION_KEY`. O workflow
guarda só a referência. [14](14-nos-e-integracoes.md)

**Cron** — Sintaxe de agendamento (`0 7 * * *`). Interpretada no fuso de
`GENERIC_TIMEZONE`. [16](16-gatilhos-e-webhooks.md)

---

## D

**Data table** — Armazenamento tabular nativo do n8n, por projeto, com teto padrão
de 200 MiB. [12](12-o-modelo-de-dados.md)

**Dataflow (fluxo de dados)** — Paradigma em que o programa é um grafo de operadores
ligados por canais de dados. A família a que o n8n pertence. [60](60-teoria-avancada.md)

---

## E

**Edit Fields (Set)** — Nó para criar, renomear, remover campos e fixar tipos.
Prefira-o a um Code node de três linhas. [14](14-nos-e-integracoes.md)

**`.ee`** — Arquivos com `.ee.` no nome ou `.ee` no diretório do repositório **não**
estão sob a Sustainable Use License; exigem licença Enterprise. [80](80-custos-e-licencas.md)

**Error output (saída de erro)** — Segunda saída de um nó, criada por
*On Error → Continue (using error output)*, por onde saem os itens que falharam.
**O padrão de produção.** [18](18-erros-e-confiabilidade.md)

**Error Workflow** — Fluxo disparado quando outro falha. Configurado em
*Settings → Error Workflow*. [18](18-erros-e-confiabilidade.md)

**Evaluations** — Recursos de teste de fluxos, especialmente de IA: casos, métricas
e execução em paralelo. [23](23-ciclo-de-vida-e-versionamento.md)

**`exactly-once` (exatamente uma vez)** — Garantia **impossível** de ponta a ponta
em sistema distribuído. O que se obtém é `at-least-once` + idempotência. [60](60-teoria-avancada.md)

**Execution (execução)** — Uma rodada completa do workflow, com os dados de entrada
e saída de cada nó. [10](10-fundamentos.md)

**Expressão** — JavaScript avaliado dentro de um campo, entre `{{ }}`. No JSON, o
campo começa com `=`. [13](13-expressoes.md)

---

## F

**Fair-code** — Modelo de licenciamento com código aberto para leitura e extensão,
mas com restrições comerciais definidas pelo autor. **Não é open source pela OSI.**
[80](80-custos-e-licencas.md)

**Fan-out (leque)** — Uma saída ligada a vários nós. **Todos recebem todos os
itens** — não é divisão de carga. [12](12-o-modelo-de-dados.md)

**Filter** — Nó que descarta os itens que não passam na condição. Uma saída só. [15](15-fluxo-de-controle.md)

---

## G

**`GENERIC_TIMEZONE`** — Fuso usado pelos nós de agendamento. Padrão: UTC.
Diferente de `TZ`, que é o fuso do sistema no contêiner. [03](03-instalacao.md)

**Guardrails** — Nó que filtra entrada e saída de IA (PII, jailbreak, tópicos). [24](24-ia-e-agentes.md)

---

## H

**HMAC** — Assinatura com chave compartilhada, usada para autenticar webhooks.
Compare em tempo constante. [16](16-gatilhos-e-webhooks.md)

**HTTP Request** — O nó coringa: alcança qualquer API REST. Tem paginação, batching
e *Import cURL*. [14](14-nos-e-integracoes.md)

---

## I

**Idempotência** — Propriedade de uma operação cujo efeito é o mesmo executada uma
ou N vezes. **A única forma prática de correção em integração.** [18](18-erros-e-confiabilidade.md)

**Item** — A unidade de dado que trafega: `{ json: {...}, binary?: {...},
pairedItem?: ... }`. Sempre num array. [12](12-o-modelo-de-dados.md)

**Item linking** — A cadeia `pairedItem` que liga cada item de saída ao item de
entrada que o gerou. É o que faz `$('Nó').item` funcionar. [12](12-o-modelo-de-dados.md)

---

## J

**JMESPath** — Linguagem de consulta para JSON, disponível como `$jmespath()` nas
expressões. [13](13-expressoes.md)

---

## L

**LangChain** — Framework de aplicações com LLM. Os nós de IA do n8n implementam a
versão JavaScript. [24](24-ia-e-agentes.md)

**LangSmith** — Plataforma de rastreamento de execuções de LLM. Integrável em n8n
**autogerido**, em todas as edições; **não** existe no Cloud. [24](24-ia-e-agentes.md)

**Loop Over Items (*Split in Batches*)** — Nó de repetição por lotes. Tem saídas
`done` e `loop`, e exige o fio de volta. [15](15-fluxo-de-controle.md)

**Low-code** — Abordagem em que a maior parte é desenhada e só o necessário é
escrito em código.

**Luxon** — Biblioteca de datas usada pelo n8n. `$now` e `$today` são objetos
`DateTime`. Cuidado: a assinatura de `plus()` difere entre expressões e Code node.
[13](13-expressoes.md)

---

## M

**Main (instância principal)** — O processo que serve o editor, os gatilhos e cria
as execuções. Em queue mode, não as executa. [21](21-escala-e-producao.md)

**MCP (*Model Context Protocol*)** — Protocolo para expor ferramentas a modelos de
linguagem. O n8n é cliente (MCP Client) e servidor (MCP Server Trigger). [24](24-ia-e-agentes.md)

**Memory (memória de IA)** — Sub-node que guarda o histórico da conversa,
chaveado por *session ID*. **Só se conecta ao AI Agent.** [24](24-ia-e-agentes.md)

**Merge** — Nó que junta dois fluxos: append, por chave, por posição, todas as
combinações, ou SQL. [15](15-fluxo-de-controle.md)

**Misfire policy** — O que fazer com um agendamento perdido: descartar (padrão) ou
executar uma recuperação. [16](16-gatilhos-e-webhooks.md)

**Modo de execução** — `regular` (executa no processo principal) ou `queue`
(executa em workers via Redis). [20](20-arquitetura-interna.md)

---

## N

**`N8N_ENCRYPTION_KEY`** — Chave que cifra as credenciais. **Perdê-la é perder todas
as credenciais**, mesmo com backup do banco. [22](22-seguranca.md)

**n8n** — Lê-se "n-eight-n". Numerônimo de *nodemation* (*node* + *automation*).

**Node (nó)** — Unidade de trabalho: recebe itens, produz itens. [10](10-fundamentos.md)

---

## O

**`ON CONFLICT DO NOTHING`** — Cláusula SQL que torna um `INSERT` idempotente.
A garantia mora no banco, não no `if`. [18](18-erros-e-confiabilidade.md)

**Ollama** — Executor local de modelos de linguagem. Relevante para quem autogere
justamente para não mandar dados para fora. [24](24-ia-e-agentes.md)

---

## P

**`pairedItem`** — Campo do item que aponta para o índice do item de entrada que o
originou. Ver *item linking*. [12](12-o-modelo-de-dados.md)

**Paginação** — Recurso do nó HTTP Request que busca várias páginas sozinho.
**Sempre limite o número de páginas.** [06](06-exemplos.md)

**Pin data** — Congela a saída de um nó para desenvolver sem chamar a API de verdade.
Despine antes de publicar. [04](04-como-comecar.md)

**Polling** — Gatilho que pergunta periodicamente se há novidade. Gasta execução
mesmo sem evento. [16](16-gatilhos-e-webhooks.md)

**Proveniência (*provenance*)** — Rastro de quais dados de entrada contribuíram para
um dado de saída. O `pairedItem` é uma aproximação disso. [60](60-teoria-avancada.md)

**`Publish`** — Ato explícito de promover a versão salva para produção. Separado do
`Save` desde o n8n 2.0. [23](23-ciclo-de-vida-e-versionamento.md)

**Push** — Gatilho em que o serviço externo chama você (webhook). Preferível ao
polling. [16](16-gatilhos-e-webhooks.md)

**Pyodide** — CPython compilado para WebAssembly, usado para Python no n8n 1.x.
**Removido no 2.0.** [17](17-code-node-e-task-runners.md)

---

## Q

**Queue mode (modo fila)** — Arquitetura com main + Redis + workers. Exige Postgres
e binário fora do `filesystem`. [21](21-escala-e-producao.md)

---

## R

**RAG (*Retrieval-Augmented Generation*)** — Buscar trechos relevantes antes de
gerar a resposta. [24](24-ia-e-agentes.md)

**RBAC** — Controle de acesso por papéis. **Recurso licenciado**; ausente na edição
Community. [22](22-seguranca.md)

**`Retry On Fail`** — Configuração que repete o nó em caso de falha. **Só use se a
operação for idempotente.** [18](18-erros-e-confiabilidade.md)

**Root node / sub-node** — Nó principal de um cluster de IA e os nós que lhe
fornecem capacidade por linha pontilhada. [24](24-ia-e-agentes.md)

**`runData`** — Estrutura que guarda entrada e saída de cada nó de uma execução.
Origem da boa depuração e do crescimento do banco. [20](20-arquitetura-interna.md)

---

## S

**Session ID** — Chave da memória de conversa. Mal definida, faz duas pessoas
compartilharem histórico. [24](24-ia-e-agentes.md)

**Split Out** — Nó que transforma um item com array em N itens. **Resolve o
mal-entendido nº 1 do n8n.** [12](12-o-modelo-de-dados.md)

**SSRF (*Server-Side Request Forgery*)** — Ataque em que o servidor é induzido a
chamar destinos internos. [22](22-seguranca.md)

**`staticData`** — Estado que sobrevive entre execuções, acessado por
`$getWorkflowStaticData()`. **Só grava em execução de produção** e não é seguro sob
concorrência. [13](13-expressoes.md)

**Sticky note** — Caixa de texto no canvas (`Shift+S`). Documente o **porquê**. [23](23-ciclo-de-vida-e-versionamento.md)

**Sub-workflow** — Workflow chamado por outro. Dois modos: uma execução para todos
os itens, ou uma por item. [15](15-fluxo-de-controle.md)

**Sustainable Use License** — A licença do n8n. Uso e modificação para **fins
internos de negócio** ou uso pessoal; distribuição só gratuita e não comercial.
[80](80-custos-e-licencas.md)

**Switch** — Nó de roteamento com N saídas mais *fallback*. **Conecte sempre o
fallback.** [15](15-fluxo-de-controle.md)

---

## T

**Task broker / task requester / task runner** — Os três papéis da execução de
código: o n8n coordena (broker), o Code node pede (requester) e o runner executa.
[17](17-code-node-e-task-runners.md)

**Task runner — modo interno × externo** — Interno lança um processo filho com o
mesmo usuário (**sem isolamento real**); externo usa contêiner separado
(`n8nio/runners`). **Produção exige externo.** [17](17-code-node-e-task-runners.md)

**Tool (ferramenta)** — Capacidade que um agente pode invocar. A **descrição** é o
principal parâmetro de qualidade. [24](24-ia-e-agentes.md)

**Trigger (gatilho)** — Nó que inicia execuções: webhook, agendamento, polling,
manual, chat, formulário, erro, sub-workflow, MCP. [16](16-gatilhos-e-webhooks.md)

**`typeValidation`** — Opção das condições: `strict` (comparar tipos diferentes dá
erro) ou `loose` (converte). **Prefira `strict`.** [15](15-fluxo-de-controle.md)

**`typeVersion`** — Versão do nó. O n8n cria versões novas em vez de alterar as
antigas, para não quebrar fluxos existentes. [10](10-fundamentos.md)

---

## W

**Webhook** — Endpoint HTTP que dispara um fluxo. Tem URL de **teste**
(`/webhook-test/...`) e de **produção** (`/webhook/...`). [16](16-gatilhos-e-webhooks.md)

**`WEBHOOK_URL`** — Variável que define a URL pública mostrada nos nós de webhook.
Obrigatória atrás de proxy ou túnel. [03](03-instalacao.md)

**Worker** — Processo que executa as execuções em queue mode. Precisa da mesma
chave de criptografia e do seu próprio sidecar de task runner. [21](21-escala-e-producao.md)

**Workflow** — Grafo dirigido acíclico de nós conectados, persistido como JSON.
[10](10-fundamentos.md)

---

*Voltar ao [00-MAPA.md](00-MAPA.md)*
