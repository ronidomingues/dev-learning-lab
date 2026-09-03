# 95 · Referências — fontes primárias

`Nível: todos` · **Todos os links verificados em 01/09/2026**

---

## 1. Documentação oficial

| Assunto | Link |
|---|---|
| Início | <https://docs.n8n.io/welcome> |
| **Índice completo (Markdown)** | <https://docs.n8n.io/sitemap.md> |
| **Documentação inteira em um arquivo** | <https://docs.n8n.io/llms-full.txt> |
| Escolher Cloud ou autogerido | <https://docs.n8n.io/choose-how-to-use-n8n> |
| Glossário de conceitos | <https://docs.n8n.io/key-concept-glossary> |
| Trilhas de aprendizado | <https://docs.n8n.io/learning-paths> |

> **Truque:** qualquer página vira Markdown limpo acrescentando `.md` à URL
> (`docs.n8n.io/welcome.md`). Também funciona o cabeçalho `Accept: text/markdown`.
> Foi assim que este curso conferiu cada afirmação técnica.

### Instalação e operação

| Assunto | Link |
|---|---|
| Opções de instalação | <https://docs.n8n.io/deploy/host-n8n/install-options> |
| **One-line setup** | <https://docs.n8n.io/deploy/host-n8n/install-options/one-line-setup> |
| Docker Compose | <https://docs.n8n.io/deploy/host-n8n/install-options/install-using-docker-compose> |
| Docker | <https://docs.n8n.io/deploy/host-n8n/install-options/install-with-docker> |
| npm (legado) | <https://docs.n8n.io/deploy/host-n8n/install-options/install-with-npm> |
| **Variáveis de ambiente** | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables> |
| Escalar | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling> |
| **Queue mode** | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode> |
| Concorrência | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/control-concurrency> |
| Dados de execução | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/manage-execution-data> |
| Medir desempenho | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/measure-performance> |
| **Task runners** | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/set-up-task-runners> |
| **Endurecer task runners** | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/harden-task-runners> |
| **Agendador durável** | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/durable-scheduler> |
| Segurança | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/security> |
| Proteção SSRF | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/enable-ssrf-protection> |
| Rotação de chave | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/rotate-encryption-keys> |
| Auditoria | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/run-security-audits> |
| Redigir dados de execução | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/redact-execution-data> |
| Módulos externos no Code | <https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/enable-modules-in-code-node> |

### Construir

| Assunto | Link |
|---|---|
| **Estrutura de dados** | <https://docs.n8n.io/build/work-with-data/understand-n8ns-data-structure> |
| **Item linking** | <https://docs.n8n.io/build/work-with-data/reference-data/link-data-items> |
| Erros de item linking | <https://docs.n8n.io/build/work-with-data/reference-data/link-data-items/item-linking-errors> |
| **Referência de expressões** | <https://docs.n8n.io/build/work-with-data/transform-data/expression-reference> |
| **Métodos e variáveis embutidos** | <https://docs.n8n.io/build/code-in-n8n/use-built-in-shortcuts> |
| Metadados do n8n (`$execution`, `$workflow`…) | <https://docs.n8n.io/build/code-in-n8n/use-built-in-shortcuts/n8n-metadata> |
| Node Code | <https://docs.n8n.io/build/code-in-n8n/using-the-code-node> |
| Cookbook do Code | <https://docs.n8n.io/build/code-in-n8n/cookbook/code-node> |
| Tratar erros | <https://docs.n8n.io/build/flow-logic/handle-errors-gracefully> |
| Converter em sub-workflow | <https://docs.n8n.io/build/flow-logic/convert-to-sub-workflows> |
| Dados customizados de execução | <https://docs.n8n.io/build/understand-workflows/understand-executions/customize-executions-data> |
| Data tables | <https://docs.n8n.io/build/work-with-data/data-tables> |
| Pacotes `.n8np` | <https://docs.n8n.io/build/manage-workflows/n8n-packages/how-import-works> |

### Nós

| Assunto | Link |
|---|---|
| Tipos de nó | <https://docs.n8n.io/integrations/builtin/node-types> |
| Webhook | <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook> |
| Schedule Trigger | <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger> |
| Error Trigger | <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger> |
| Data Table | <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.datatable> |
| Cluster nodes (IA) | <https://docs.n8n.io/integrations/builtin/cluster-nodes> |
| MCP Server Trigger | <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger> |
| MCP Client | <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcpclient> |
| Guardrails | <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.guardrails> |

### IA

| Assunto | Link |
|---|---|
| **LangChain no n8n** | <https://docs.n8n.io/build/integrate-ai/langchain-in-n8n> |
| Componentes de IA | <https://docs.n8n.io/build/integrate-ai/understand-ai-components> |

### Changelog — **leia antes de atualizar**

| Assunto | Link |
|---|---|
| Changelog | <https://docs.n8n.io/changelog> |
| Notas de versão | <https://docs.n8n.io/changelog/release-notes> |
| **Quebras do 2.0** | <https://docs.n8n.io/changelog/v20-breaking-changes> |
| **Ferramenta de migração 2.0** | <https://docs.n8n.io/changelog/v20-migration-tool> |
| **Quebras do 3.0 (out/2026)** | <https://docs.n8n.io/changelog/v30-breaking-changes> |

---

## 2. Código-fonte

| Recurso | Link |
|---|---|
| Repositório | <https://github.com/n8n-io/n8n> |
| **Licença (leia)** | <https://github.com/n8n-io/n8n/blob/master/LICENSE.md> |
| Releases | <https://github.com/n8n-io/n8n/releases> |
| Exemplos de hospedagem | <https://github.com/n8n-io/n8n-hosting> |
| Launcher dos task runners | <https://github.com/n8n-io/task-runner-launcher> |
| Imagem do n8n (Docker Hub) | <https://hub.docker.com/r/n8nio/n8n> |
| Imagem dos runners | <https://hub.docker.com/r/n8nio/runners> |

**Onde olhar no código, quando a documentação não basta:**

| Quero entender | Olhe em |
|---|---|
| O motor de execução | `packages/core/src/execution-engine/` |
| Nós base | `packages/nodes-base/nodes/<Nome>/` |
| Comandos de CLI | `packages/cli/src/commands/` |
| Editor | `packages/frontend/editor-ui/` |

---

## 3. Comunidade e ecossistema

| Recurso | Link | Para quê |
|---|---|---|
| Fórum oficial | <https://community.n8n.io> | Perguntas; mantenedores respondem |
| **Templates de workflow** | <https://n8n.io/workflows/> | Milhares de fluxos prontos para ler e copiar |
| Blog | <https://blog.n8n.io> | Anúncios e análises do setor |
| n8n Academy | <https://learn.n8n.io/> | Cursos oficiais com certificado |
| Preços | <https://n8n.io/pricing/> | **Confira a data** |

---

## 4. Tecnologias vizinhas (documentação primária)

| Tecnologia | Link | Por que importa |
|---|---|---|
| Docker | <https://docs.docker.com/> | Forma oficial de rodar n8n |
| Docker Compose | <https://docs.docker.com/compose/> | |
| PostgreSQL | <https://www.postgresql.org/docs/> | Banco de produção |
| Redis | <https://redis.io/docs/> | Fila do queue mode |
| **Luxon** | <https://moment.github.io/luxon/> | **Datas nas expressões e no Code node** |
| **JMESPath** | <https://jmespath.org/> | `$jmespath()` |
| LangChain JS | <https://js.langchain.com/docs/> | Base dos nós de IA |
| LangSmith | <https://docs.smith.langchain.com/> | Rastrear agentes (só autogerido) |
| **Model Context Protocol** | <https://modelcontextprotocol.io/> | Especificação do MCP |
| Prometheus | <https://prometheus.io/docs/> | Métricas |
| OpenTelemetry | <https://opentelemetry.io/docs/> | Rastreamento |
| Caddy | <https://caddyserver.com/docs/> | Proxy reverso com TLS automático |
| Cloudflare Tunnel | <https://developers.cloudflare.com/cloudflare-tunnel/> | Expor webhook local |

---

## 5. Padrões e especificações

| Documento | Link | Relevância |
|---|---|---|
| RFC 9110 — HTTP Semantics | <https://www.rfc-editor.org/rfc/rfc9110> | Métodos, status, idempotência |
| RFC 6749 — OAuth 2.0 | <https://www.rfc-editor.org/rfc/rfc6749> | Credenciais OAuth |
| RFC 8259 — JSON | <https://www.rfc-editor.org/rfc/rfc8259> | O formato de tudo |
| RFC 2104 — HMAC | <https://www.rfc-editor.org/rfc/rfc2104> | Assinatura de webhook |
| Cron (POSIX) | <https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html> | Expressões do Schedule Trigger |
| Catálogo EIP | <https://www.enterpriseintegrationpatterns.com/patterns/messaging/> | Vocabulário de integração |
| Catálogo de microsserviços | <https://microservices.io/patterns/> | Saga, outbox |

---

## 6. Fontes usadas neste curso, com data

Toda afirmação técnica deste curso veio de uma destas fontes, consultadas em
**01/09/2026**:

| Tipo | Fonte |
|---|---|
| Versões e datas de release | [GitHub Releases](https://github.com/n8n-io/n8n/releases) e [API do GitHub](https://api.github.com/repos/n8n-io/n8n) |
| Comandos e comportamento | **Execução real de n8n 2.36.9** (Node 24.18.0, Ubuntu 22.04.5) — `n8n --help`, `import:workflow`, `execute --rawOutput`, `export:nodes`, chamadas de webhook com `curl` |
| Instalação e configuração | Documentação oficial (seção 1) |
| Licença | [`LICENSE.md`](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) do repositório |
| Preços | [n8n.io/pricing](https://n8n.io/pricing/) |
| Captação e avaliação | [PitchBook](https://pitchbook.com/news/articles/ai-agent-startup-n8n-lands-2-5b-valuation-with-180m-series-c) |
| Cursos | Buscas em PT, EN e FR + [n8n Academy](https://learn.n8n.io/) |
| Estado do setor | [Blog oficial da n8n](https://blog.n8n.io) e cobertura de terceiros, marcada como tal |

---

## 7. Como manter este material atualizado

O n8n muda rápido. Sugestão de rotina:

| Frequência | O quê |
|---|---|
| **Mensal** | Ler o [changelog](https://docs.n8n.io/changelog) |
| **Trimestral** | Reavaliar [65-estado-da-arte.md](65-estado-da-arte.md) |
| **Semestral** | Reavaliar [80-custos-e-licencas.md](80-custos-e-licencas.md) e [03-instalacao.md](03-instalacao.md) |
| **Em outubro de 2026** | **Revisar o curso inteiro** por causa do n8n 3.0 |

---

*Anterior: [90-bibliografia.md](90-bibliografia.md) · Próximo: [GLOSSARIO.md](GLOSSARIO.md)*
