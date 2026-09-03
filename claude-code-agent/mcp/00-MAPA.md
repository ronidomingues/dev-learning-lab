# MCP — Model Context Protocol · do zero absoluto ao nível de pesquisa

`Curso completo` · `Escrito e verificado em 01/09/2026` · `Protocolo 2026-07-28`
`SDK Python mcp 2.1.1` · `SDK TypeScript 2.0.0` · `Inspector 2.4.0`

---

## O que você saberá ao final

- **Explicar** o que é MCP para quem nunca ouviu falar — e dizer quando **não** usá-lo.
- **Instalar** todo o conjunto de tecnologias em Linux, macOS e Windows (WSL2), inclusive
  atrás de proxy corporativo, com desinstalação limpa.
- **Escrever** servidores MCP em Python e TypeScript que um modelo usa **corretamente**.
- **Ler e escrever** mensagens JSON-RPC do MCP à mão, sem SDK.
- **Entender por dentro**: os dois transportes, as três primitivas, capacidades, MRTR,
  e por que o protocolo virou **sem estado** em julho de 2026.
- **Proteger**: OAuth 2.1 com validação de audiência, e — mais importante — saber o que
  a segurança do MCP **não** resolve.
- **Operar** em produção: limites, cache, observabilidade, custo real em reais.
- **Decidir** com números: licença, preço de token, hospedagem, custo oculto.
- **Discutir** os limites teóricos: por que "exatamente uma vez" não existe, por que a
  injeção de prompt continua aberta, e por que o isolamento entre servidores não é o que
  parece.

---

## Como ler

| Você é… | Comece em | Depois |
|---|---|---|
| **Nunca ouvi falar** | [01](01-introducao-leigo.md) | siga a ordem numérica |
| **Quero rodar hoje** | [03 · sem instalar nada](03-instalacao.md#12-alternativa-sem-instalar-nada) | [04](04-como-comecar.md) → [07](07-projeto-modelo/README.md) |
| **Já escrevi servidor, quero acertar** | [23](23-projeto-de-ferramentas.md) | [15](15-primitivas-do-servidor.md) → [75](75-armadilhas.md) |
| **Vou pôr em produção** | [19](19-seguranca.md) | [18](18-autorizacao.md) → [24](24-operacao-e-producao.md) |
| **Escrevo o cliente/host** | [20](20-clientes-e-hosts.md) | [16](16-primitivas-do-cliente.md) → [17](17-versionamento-e-compatibilidade.md) |
| **Vim de material de 2025** | [17 §8](17-versionamento-e-compatibilidade.md#8-migrando-de-1xlegado-para-2xmoderno) | [11 §3.5](11-historia.md) → [65](65-estado-da-arte.md) |
| **Decisão de adoção** | [01](01-introducao-leigo.md) | [19](19-seguranca.md) → [80](80-custos-e-licencas.md) |
| **Quero profundidade** | [13](13-json-rpc-e-a-camada-base.md) | [60](60-teoria-avancada.md) → [65](65-estado-da-arte.md) |

Trilha de 6 semanas com material externo:
[85 §6](85-cursos-e-certificacoes.md#6-trilha-sugerida--6-semanas-6-hsemana).

---

## ⚠️ Aviso de versão, antes de tudo

Em **28/07/2026** o MCP passou pela maior reescrita da sua história: **acabaram as
sessões, o handshake `initialize` e as requisições iniciadas pelo servidor.**

**Praticamente todo tutorial, curso ou livro publicado antes de agosto de 2026 ensina
uma mecânica que não existe mais.** Este curso cobre a revisão `2026-07-28` e traz a
tabela de tradução em [17 §8](17-versionamento-e-compatibilidade.md#8-migrando-de-1xlegado-para-2xmoderno).

---

## Mapa dos arquivos

### Bloco A · Porta de entrada (01–09) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 01 | [introducao-leigo](01-introducao-leigo.md) | A analogia do estagiário trancado, o problema M×N, os três papéis, um exemplo do começo ao fim com JSON real, o que MCP **não** é, quando **não** usar |
| 02 | [pre-requisitos](02-pre-requisitos.md) | Conhecimento indispensável × opcional, versões mínimas, hardware real, **tempo honesto por nível**, rota de resgate para cada lacuna |
| 03 | [instalacao](03-instalacao.md) | **Manual de campo**: Python/`uv`, Node/`fnm`, os dois SDKs, Inspector, Docker e host, nos três SOs; PATH, permissões, **proxy corporativo e CA interna**, convivência de versões, reprodutibilidade, atualizar, desinstalar por completo, **14 erros literais**, checklist |
| 04 | [como-comecar](04-como-comecar.md) | Primeiro servidor em Python e TypeScript, com **saídas reais**; cliente em processo; ciclo de trabalho; **os 5 primeiros erros de uso** |
| 05 | [manual-de-uso](05-manual-de-uso.md) | Referência por tarefa: métodos, `_meta`, códigos de erro, cabeçalhos HTTP, receituário dos dois SDKs, CLI `mcp`, **Inspector completo com códigos de saída**, config dos hosts, **o que está obsoleto** |
| 06 | [exemplos](06-exemplos.md) | **15 exemplos completos**, treze executados de verdade, dois de produção (banco somente-leitura; proxy de API com cache e limite de taxa) |
| 07 | [projeto-modelo/](07-projeto-modelo/README.md) | **`biblioteca-mcp`**: servidor completo com domínio separado, confirmação humana via MRTR, transações, **15 testes (9 de caminho ruim)**, Makefile |

### Bloco B · Núcleo (10–69) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 10 | [fundamentos](10-fundamentos.md) | Definição formal desmontada, os quatro princípios de projeto, as três primitivas e **quem controla cada uma**, capacidades, os três padrões de mensagem, **o modelo sem estado**, quatro modelos mentais |
| 11 | [historia](11-historia.md) | Plugins de ChatGPT, function calling, **o LSP como antepassado**; linha do tempo de 2024 a 2026; **revisão por revisão, com o porquê**; os cinco porquês da virada sem estado; por que venceu e o que quase o matou |
| 12 | [arquitetura](12-arquitetura.md) | As camadas, quem inicia o quê, negociação sem handshake, **as três fronteiras de confiança e o que cada uma não garante**, ciclo de vida, o que o host faz que o protocolo não impõe, quatro topologias reais |
| 13 | [json-rpc-e-a-camada-base](13-json-rpc-e-a-camada-base.md) | JSON-RPC em cinco minutos e **por que ele, não gRPC**; regras que o MCP acrescenta; `_meta` completo; `server/discover`; **política de faixas de erro**; JSON Schema, `$ref` e SSRF; **ler a fita crua** |
| 14 | [transportes](14-transportes.md) | stdio e Streamable HTTP em detalhe: enquadramento, `stderr`, ciclo de vida, **validação cabeçalho×corpo**, `x-mcp-header`, sentinela Base64, status codes, cancelamento, compatibilidade com o passado |
| 15 | [primitivas-do-servidor](15-primitivas-do-servidor.md) | Tools, resources e prompts com precisão; nomes; os dois tipos de erro; **ferramentas com estado e os quatro cuidados com handles**; `ttlMs`/`cacheScope`; por que recursos são subutilizados |
| 16 | [primitivas-do-cliente](16-primitivas-do-cliente.md) | **MRTR completo**, com as obrigações dos dois lados; elicitação em formulário e URL; **o ataque de phishing por elicitação**; Sampling e Roots depreciados, com o porquê; lista de verificação de cliente robusto |
| 17 | [versionamento-e-compatibilidade](17-versionamento-e-compatibilidade.md) | As duas eras; detecção por transporte; **matriz de compatibilidade**; extensões; **política de ciclo de vida**; checklists de migração de servidor, cliente e dos dois SDKs |
| 18 | [autorizacao](18-autorizacao.md) | OAuth 2.1 no MCP: papéis, PRM (RFC 9728), CIMD, o fluxo completo, `resource` (RFC 8707), **validação de `iss` (RFC 9207)**, a regra de audiência, escopos e step-up, refresh tokens |
| 19 | [seguranca](19-seguranca.md) | **O arquivo mais importante.** Confused deputy, token passthrough, SSRF, sequestro de handle, servidor local comprometido, URL maliciosa, proxy stdio, mix-up, minimização de escopo — e **tool poisoning, line jumping, shadowing e rug pull**, com os cinco porquês de por que não têm solução |
| 20 | [clientes-e-hosts](20-clientes-e-hosts.md) | O laço do host, desambiguação de nomes, **orçamento de contexto**, a tela de aprovação que funciona, o laço do MRTR, config dos hosts, **testar contra um servidor hostil** |
| 21 | [registro-e-distribuicao](21-registro-e-distribuicao.md) | O MCP Registry: o que é e o que **não** é; publicar passo a passo com `mcp-publisher`; namespaces e o que a verificação **não** garante; formas de distribuição; escolher servidor de terceiro |
| 22 | [extensoes](22-extensoes.md) | O modelo de extensões; **Tasks** completo; **MCP Apps** completo; extensões de autorização; como decidir adotar |
| 23 | [projeto-de-ferramentas](23-projeto-de-ferramentas.md) | **A engenharia que decide se funciona**: nomes, descrições, `instructions`, schemas, granularidade, retorno, erros, determinismo, idempotência, ferramentas destrutivas, como testar o **projeto** |
| 24 | [operacao-e-producao](24-operacao-e-producao.md) | Empacotamento, configuração, log estruturado, **OpenTelemetry**, métricas que valem, limites, cache, deploy sem quebrar, custo, falhas comuns, checklist de produção |
| 60 | [teoria-avancada](60-teoria-avancada.md) | Por que "exatamente uma vez" não existe; injeção de prompt como problema aberto; segurança por capacidade e delegado confuso; **por que sem estado, formalmente**; a tensão de contexto; **três provas e as ressalvas que as anulam**; problemas em aberto |
| 65 | [estado-da-arte](65-estado-da-arte.md) | Números de 01/09/2026; o que mudou em `2026-07-28`; **as cinco frentes do roadmap de 22/08/2026**; governança; a CSI da NSA; debates em aberto com opinião marcada; o que observar |

### Bloco C · Prática e erros (70–79) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 70 | [pratica](70-pratica.md) | **12 laboratórios** com critério de aprovação, do "ler a fita" ao **servidor hostil**; 8 projetos maiores |
| 75 | [armadilhas](75-armadilhas.md) | **38 armadilhas** com sintoma real e correção, em quatro categorias, e **12 mitos** desmontados |

### Bloco D · Economia e ecossistema (80–89) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 80 | [custos-e-licencas](80-custos-e-licencas.md) | Licenças (Apache-2.0 / MIT / CC-BY-4.0) e **quem paga a conta**; o que custa zero; **preços de token com data e em reais**; a conta que ninguém faz; hospedagem comparada; custos ocultos; como reduzir |
| 85 | [cursos-e-certificacoes](85-cursos-e-certificacoes.md) | Cursos em **PT, EN e FR**, pesquisados na web, com ano e avaliação franca; **quais são grátis de verdade**; por que **não existe certificação oficial**; trilha de 6 semanas |

### Bloco E · Fontes (90–99) — ✅ completo

| # | Arquivo | O que tem |
|---|---|---|
| 90 | [bibliografia](90-bibliografia.md) | Livros de MCP com edição conferida e **o aviso de que todos são anteriores à reescrita**; fundamentos que não envelhecem; o que ler por tempo disponível; nota sobre o campo acadêmico |
| 95 | [referencias](95-referencias.md) | Toda a spec por página, SDKs por tier, extensões, registry, governança, **os SEPs citados**, padrões externos (RFCs), segurança, e os assuntos vizinhos deste repositório |
| — | [GLOSSARIO](GLOSSARIO.md) | **~110 termos**, com ⚠️ no que está depreciado ou removido, e a tabela de códigos de erro |

---

## As 12 camadas de profundidade

| # | Camada | Onde |
|---|---|---|
| 1 | Intuição para leigo | [01 §1](01-introducao-leigo.md) |
| 2 | Definição informal | [01 §3–4](01-introducao-leigo.md) |
| 3 | Por que existe (história) | [01 §8](01-introducao-leigo.md), [11](11-historia.md) |
| 4 | Ambiente e primeiro uso | [03](03-instalacao.md), [04](04-como-comecar.md) |
| 5 | Fundamentos formais | [10](10-fundamentos.md), [12](12-arquitetura.md) |
| 6 | Mecânica interna | [13](13-json-rpc-e-a-camada-base.md), [14](14-transportes.md), [15](15-primitivas-do-servidor.md), [16](16-primitivas-do-cliente.md) |
| 7 | Implementação prática | [06](06-exemplos.md), [07](07-projeto-modelo/README.md), [70](70-pratica.md) |
| 8 | Casos de uso reais | [06 §13–14](06-exemplos.md), [12 §8](12-arquitetura.md), [24](24-operacao-e-producao.md) |
| 9 | Trade-offs e alternativas | [01 §6–7](01-introducao-leigo.md), [14 §4](14-transportes.md), [75](75-armadilhas.md) |
| 10 | Economia | [80](80-custos-e-licencas.md) |
| 11 | Profundidade de pesquisa | [60](60-teoria-avancada.md) |
| 12 | Estado da arte e fronteira | [65](65-estado-da-arte.md) |

---

## O que foi verificado de verdade

Este curso não foi escrito de memória. Em **01/09/2026**, em Ubuntu 22.04.5 LTS x86-64,
atrás de proxy corporativo:

- **SDK Python `mcp` 2.1.1** instalado com `uv` 0.12.7 (Python 3.12.14). Servidor e
  cliente escritos e executados; ferramentas, recursos e prompts exercitados.
- **SDK TypeScript** `@modelcontextprotocol/server` e `/client` **2.0.0** instalados
  (Node v24.18.0, npm 12.0.1). Servidor + cliente executados com `InMemoryTransport`.
- **JSON-RPC cru** capturado sobre stdio: `server/discover`, `tools/list`, `tools/call`,
  ferramenta inexistente e **erro `-32022` de versão não suportada**. Todo JSON deste
  curso marcado como "real" veio daí.
- **Streamable HTTP** exercitado com `curl`: `200` com JSON; **`400` + `-32020`** por
  `Mcp-Name` ausente; **`403`** por `Origin` inválido; e a divergência do SDK que
  responde `400` em vez de `405` ao `GET`.
- **MCP Inspector 2.4.0** executado em modo CLI contra o servidor local.
- **Descobertas de campo registradas:** `ToolError` × exceção crua (só a primeira entrega
  a mensagem ao modelo); retorno anotado como `dict`/`list` **não** gera `outputSchema`;
  `NoBackChannelError` ao usar `ctx.elicit()` direto; `camelCase` no fio × `snake_case`
  no objeto Python.
- **Projeto-modelo `biblioteca-mcp`**: `uv sync` + **15 testes executados e aprovados
  (3,96 s)**; `make inspecionar` listando as 6 ferramentas; `make http` + `curl
  server/discover` com a resposta reproduzida no README.
- **Pesquisado na web na mesma data:** especificação `2026-07-28` inteira e os changelogs
  das quatro revisões anteriores; roadmap de 22/08/2026; documentação do Inspector, do
  registry e das extensões; SDKs e tiers; preços de API e de hospedagem; câmbio; licenças
  (Apache-2.0/MIT/CC-BY-4.0); cursos em PT/EN/FR; edições dos livros.

---

## Status

| Bloco | Status | Arquivos |
|---|---|---|
| **A · Porta de entrada** | ✅ | 01, 02, 03, 04, 05, 06, 07 |
| **B · Núcleo** | ✅ | 10–24, 60, 65 |
| **C · Prática e erros** | ✅ | 70, 75 |
| **D · Economia** | ✅ | 80, 85 |
| **E · Fontes** | ✅ | 90, 95, GLOSSARIO |

**Total:** 30 documentos + projeto-modelo executável, ~12.000 linhas.

### Pendências e revisão

- **`65-estado-da-arte.md`**: revisar a cada **3 meses**. O roadmap prevê redesenho de
  `tools/call`, descoberta progressiva e HTTP/2 sobre stdio — todos com potencial de
  quebrar servidores.
- **`80-custos-e-licencas.md`** e **`03-instalacao.md`**: revisar a cada **6 meses**.
- **`85-cursos-e-certificacoes.md`**: revisar quando surgir material em vídeo cobrindo a
  revisão `2026-07-28` — hoje **não existe em português**.
- **Não executado nesta máquina:** as seções de macOS e Windows do arquivo 03 (marcadas
  com ⚠️); o fluxo completo de OAuth do arquivo 18 (exige um servidor de autorização
  real); e a publicação no MCP Registry do arquivo 21 (exige conta e pacote publicado).
  Os comandos vieram da documentação oficial e estão marcados como tal.
- **Data-limite natural de revisão geral:** **28/07/2027**, quando termina a janela de
  doze meses de Roots, Sampling, Logging e HTTP+SSE.

---

**Começar:** [01 · O que é MCP, para quem nunca ouviu falar](01-introducao-leigo.md)
