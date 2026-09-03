# n8n — do zero absoluto à operação em produção

`Curso completo` · `Escrito e verificado em 01/09/2026` · `n8n 2.36.9`

---

## O que você saberá ao final

- **Explicar** o que é n8n para alguém que nunca ouviu falar, e dizer quando **não** usá-lo.
- **Instalar** n8n em Linux, macOS e Windows (WSL2), com Docker, Postgres, proxy
  corporativo, TLS e desinstalação limpa.
- **Construir** fluxos que tratam erro, não duplicam efeito e não falham em silêncio.
- **Entender** o modelo de itens, item linking, expressões e a semântica de execução.
- **Operar** em produção: queue mode, workers, poda de execuções, backup, monitoramento.
- **Proteger**: task runners, credenciais, SSRF, injeção, dados de execução.
- **Usar IA** com critério — e saber quando um agente é a escolha errada.
- **Decidir** com números: custo, licença, e o que a Sustainable Use License permite.
- **Discutir** os limites teóricos: por que *exactly-once* não existe e por que o
  n8n não faz streaming.

---

## Como ler

| Você é… | Comece em | Depois |
|---|---|---|
| **Nunca ouvi falar** | [01](01-introducao-leigo.md) | siga a ordem numérica |
| **Quero rodar hoje** | [03 · alternativa sem instalar](03-instalacao.md#alternativa-sem-instalar-nada) | [04](04-como-comecar.md) → [07](07-projeto-modelo/README.md) |
| **Já uso, quero parar de sofrer** | [12](12-o-modelo-de-dados.md) | [18](18-erros-e-confiabilidade.md) → [75](75-armadilhas.md) |
| **Vou pôr em produção** | [18](18-erros-e-confiabilidade.md) | [21](21-escala-e-producao.md) → [22](22-seguranca.md) |
| **Decisão de compra** | [80](80-custos-e-licencas.md) | [65](65-estado-da-arte.md) |
| **Quero profundidade** | [20](20-arquitetura-interna.md) | [60](60-teoria-avancada.md) |

Trilha de 12 semanas com material externo: [85 · seção 6](85-cursos-e-certificacoes.md#6-trilha-de-estudo-sugerida-12-semanas-6-hsemana).

---

## Mapa dos arquivos

### Bloco A · Porta de entrada (01–09) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | Analogia da esteira, o que é, para que serve, o que **não** é, comparação com Zapier/Make/Airflow, os cinco porquês |
| 02 | [pre-requisitos](02-pre-requisitos.md) | Conhecimento indispensável × opcional, hardware real, tempo honesto por nível, **rota de resgate** |
| 03 | [instalacao](03-instalacao.md) | **Manual de campo**: Docker em Debian/Fedora/macOS/Windows-WSL2, one-line setup, Compose com Postgres, npm (legado), PATH, permissões, **proxy corporativo**, CA interna, versões paralelas, atualizar, desinstalar, **19 erros literais**, checklist |
| 04 | [como-comecar](04-como-comecar.md) | Primeiro acesso, tour da interface, webhook funcionando em 6 passos com **saídas reais**, ciclo de trabalho, 5 erros de iniciante |
| 05 | [manual-de-uso](05-manual-de-uso.md) | Referência por tarefa: nós, expressões, variáveis embutidas, Luxon, Code, HTTP Request, **CLI real da 2.36.9**, variáveis de ambiente, API, atalhos, **o que está obsoleto** |
| 06 | [exemplos](06-exemplos.md) | **14 exemplos completos**, três executados de verdade, dois de produção (webhook assíncrono com HMAC; sincronização incremental com marca-d'água) |
| 07 | [projeto-modelo/](07-projeto-modelo/README.md) | **`central-de-pedidos`**: API de pedidos em n8n + Postgres, 4 workflows, idempotência por chave primária, Error Workflow, relatório agendado, Makefile e teste de ponta a ponta |

### Bloco B · Núcleo (10–69) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | Os sete conceitos, grafo, taxonomia de nós, item, execução, credencial, gatilho, `Save`×`Publish` |
| 11 | [historia](11-historia.md) | EAI → ESB → Yahoo Pipes → Zapier → n8n; funding até a Série C; por que a licença é assim |
| 12 | [o-modelo-de-dados](12-o-modelo-de-dados.md) | Estrutura do item, **cardinalidade**, item linking com código, binário, limites reais |
| 13 | [expressoes](13-expressoes.md) | Sintaxe, todas as variáveis, funções estendidas, Luxon e **a pegadinha do Code node**, padrões prontos, segurança |
| 14 | [nos-e-integracoes](14-nos-e-integracoes.md) | Anatomia de um nó, HTTP Request a fundo, credenciais e OAuth local, community nodes, **as cinco perguntas** |
| 15 | [fluxo-de-controle](15-fluxo-de-controle.md) | Ordem de execução v1, IF/Switch/Filter, Merge, Loop, Wait, sub-workflows, padrões de composição |
| 16 | [gatilhos-e-webhooks](16-gatilhos-e-webhooks.md) | Push × polling com a conta, webhook a fundo, cron, **agendador durável** e políticas de misfire |
| 17 | [code-node-e-task-runners](17-code-node-e-task-runners.md) | Quando usar Code, Python nativo × Pyodide, **modo interno × externo e o que isso significa para segurança** |
| 18 | [erros-e-confiabilidade](18-erros-e-confiabilidade.md) | Os quatro estados, error output, retry × idempotência, Error Workflow, garantias de entrega, observabilidade, **checklist** |
| 20 | [arquitetura-interna](20-arquitetura-interna.md) | As peças, ciclo de vida da execução, onde mora cada estado, banco, modos, como um nó é implementado, limites |
| 21 | [escala-e-producao](21-escala-e-producao.md) | Quando escalar, queue mode com compose de referência, concorrência, disco, memória, HA, monitoramento, backup, dimensionamento |
| 22 | [seguranca](22-seguranca.md) | Modelo de ameaça, dez medidas, chave de criptografia, RBAC, injeção, SSRF, superfície, passivo de dados, **checklist** |
| 23 | [ciclo-de-vida-e-versionamento](23-ciclo-de-vida-e-versionamento.md) | `Save`×`Publish`, ambientes com e sem licença, pacotes `.n8np`, atualizar com segurança, **preparar-se para o 3.0**, testar, documentar |
| 24 | [ia-e-agentes](24-ia-e-agentes.md) | Cluster nodes, mapa LangChain→n8n, agente × chain, tools, memória, RAG, MCP, guardrails, custo, LangSmith |
| 25 | [api-e-integracao-externa](25-api-e-integracao-externa.md) | API pública, padrão multi-tenant, **Embed e o que ele exige**, acoplamento, CI/CD |
| 60 | [teoria-avancada](60-teoria-avancada.md) | Formalização como dataflow, modelo de disparo, proveniência, **impossibilidade de exactly-once**, Turing-completude, complexidade, comparação com Airflow e Temporal, problemas abertos |
| 65 | [estado-da-arte](65-estado-da-arte.md) | Números verificados, **o que o 3.0 remove**, convergência automação×agentes, commoditização da IA, MCP, concorrência |

### Bloco C · Prática e erros (70–79) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 70 | [pratica](70-pratica.md) | **14 laboratórios** com critério de aceitação + desafio final com 7 critérios |
| 75 | [armadilhas](75-armadilhas.md) | **22 armadilhas, 12 mitos, 7 más práticas** e o teste de fogo |

### Bloco D · Economia e ecossistema (80–89) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | Preços com data e câmbio, custo real do autogerido, **a licença explicada com o texto original**, o que pode e o que não pode, comparação com Zapier/Make, alternativas abertas |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | n8n Academy, cursos gratuitos em **PT, EN e FR** pesquisados na web, **a verdade sobre certificações**, trilha de 12 semanas |

### Bloco E · Fontes (90–99) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | **Por que não há bom livro de n8n**, e os livros de fundamentos que valem — com os gratuitos marcados |
| 95 | [referencias](95-referencias.md) | Toda a documentação oficial, código-fonte, comunidade, specs, e **as fontes deste curso com data** |
| — | [GLOSSARIO](GLOSSARIO.md) | ~110 termos definidos, com link para o arquivo que aprofunda |

---

## O que foi executado de verdade

Este curso não foi escrito de memória. Verificado em **01/09/2026**, com
**n8n 2.36.9** (Node 24.18.0, Ubuntu 22.04.5):

- ✅ n8n instalado e **em execução**; `/healthz` respondendo `{"status":"ok"}`.
- ✅ `n8n --help` executado — a tabela de CLI do arquivo 05 é a saída real, incluindo
  `publish:workflow` e o aviso de que `update:workflow` está depreciado.
- ✅ `n8n export:nodes` — **910 tipos de nó** na instalação padrão.
- ✅ Workflow de itens executado: `1 → 3 → 3 → 1` pelos nós Code → Split Out →
  Code → Aggregate, com as saídas reais reproduzidas no arquivo 06.
- ✅ Webhook de ponta a ponta: publicado, registrado no `webhook_entity` e
  respondendo — corpo válido e corpo inválido, com os JSON reais no arquivo 04.
- ✅ Os quatro workflows do projeto-modelo **importados** e **publicados** numa
  instância real; `POST /webhook/pedido` devolveu **400** com a lista de erros e
  **202** com o pedido aceito.
- ✅ `import:credentials` a partir de JSON em texto claro — confirmado.
- ✅ Versões, preços, licença, cursos e estado da arte **pesquisados na web** na data.

**O que não foi executado:** o trecho do projeto-modelo que depende do Postgres em
contêiner. A máquina em que o material foi escrito alcança a internet apenas por
proxy corporativo e o *daemon* do Docker não tem esse proxy configurado, o que
impede baixar as imagens. Os comandos e o SQL estão corretos e o `make testar`
verifica exatamente esses pontos. Está dito de novo, com detalhe, no
[README do projeto](07-projeto-modelo/README.md#o-que-foi-verificado-e-o-que-não-foi--honestamente).

---

## Manutenção

| Quando | O quê |
|---|---|
| Mensal | Ler o [changelog](https://docs.n8n.io/changelog) |
| Trimestral | Reavaliar [65-estado-da-arte](65-estado-da-arte.md) |
| Semestral | Reavaliar [80-custos-e-licencas](80-custos-e-licencas.md) e [03-instalacao](03-instalacao.md) |
| **Outubro de 2026** | **Revisar o curso inteiro** — o n8n 3.0 remove npm, nós legados e o AI Agent v1 |

---

*Índice geral do repositório: [../INDICE.md](../INDICE.md)*
