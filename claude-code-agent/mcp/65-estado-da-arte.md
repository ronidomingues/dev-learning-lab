# 65 · Estado da arte — onde o MCP está em 01/09/2026

`Nível: pesquisa` · `Escrito em 01/09/2026` · **Este arquivo envelhece rápido. Revise a cada 3 meses.**

---

## 1. Onde estamos, em números

| Indicador | Valor | Data | Fonte |
|---|---|---|---|
| Revisão vigente | **`2026-07-28`** | 28/07/2026 | spec |
| Revisão anterior | `2025-11-25` | 25/11/2025 | spec |
| Dono do projeto | **Agentic AI Foundation** (Linux Foundation) | desde 09/12/2025 | Anthropic |
| SDKs Tier 1 | TypeScript, Python, C#, Go, Rust | 01/09/2026 | docs |
| SDKs Tier 2 | Java, Ruby | 01/09/2026 | docs |
| SDKs Tier 3 | Swift, PHP, Kotlin | 01/09/2026 | docs |
| Downloads mensais dos SDKs Tier 1 | **~meio bilhão/mês** | 28/07/2026 | blog oficial |
| Downloads totais | TypeScript e Python **passaram de 1 bilhão cada** | 28/07/2026 | blog oficial |
| Servidores públicos ativos | **mais de 10.000** | 09/12/2025 | Anthropic |
| SDK Python | `mcp` **2.1.1** (v2 estável desde 28/07/2026; v1 em manutenção) | 01/09/2026 | PyPI |
| SDK TypeScript | `@modelcontextprotocol/server` e `/client` **2.0.0** (v1 monolítico em 1.30.0) | 01/09/2026 | npm |
| Inspector | **2.4.0** | 01/09/2026 | npm |
| MCP Registry | em **pré-visualização** | 01/09/2026 | docs |

> ⚠️ **Sobre números de terceiros.** Circulam estimativas de blogs e consultorias
> (contagens de repositórios com o tópico `mcp-server`, percentuais de "empresas em
> produção", crescimento de servidores remotos). São **não auditados** e frequentemente
> se contradizem. Este material só usa como fato os números publicados pelo blog oficial
> do MCP e pela Anthropic; o resto está deliberadamente fora.

---

## 2. O que mudou desde a revisão anterior

A revisão `2026-07-28` é a maior reescrita desde a criação. Em uma frase: **o MCP virou
um protocolo HTTP comum, sem estado.**

| Mudança | O que significa na prática |
|---|---|
| **Núcleo sem estado** | de bidirecional com estado para requisição/resposta. Roda atrás de balanceador comum, sem gestão de sessão |
| **MRTR** | substitui os fluxos iniciados pelo servidor: a ferramenta pede entrada no meio da execução, o cliente repete com a resposta. Confirmação sem conexão persistente |
| **Roteamento por cabeçalho** | método e nome da ferramenta viajam em cabeçalhos HTTP; gateways roteiam e autorizam **sem abrir o corpo** |
| **Respostas cacheáveis** | listagens carregam `ttlMs` e `cacheScope` |
| **Endurecimento da autorização** | validação de `iss` (RFC 9207); DCR → Client ID Metadata Documents; credencial atrelada ao emissor |
| **Framework de extensões** | Tasks sai do núcleo experimental para extensão formal, ao lado de MCP Apps e Enterprise-Managed Authorization |
| **Política de depreciação** | janela formal de **doze meses**. Roots, Sampling, Logging e HTTP+SSE seguem funcionando durante a transição |

Estado dos SDKs no lançamento: **os quatro Tier 1 (TypeScript, Python, Go, C#) suportaram
a nova spec no dia**, com o Rust em beta. Há guias de migração para as quebras.

---

## 3. O roadmap oficial — as cinco frentes

Publicado em **22/08/2026**. Horizonte de seis a doze meses. Não são compromissos firmes;
SEPs dentro dessas áreas recebem revisão acelerada.

### 3.1 Primitivas de mensagem para agentes

*Core Maintainers: Caitie McCaffrey, Clare Liguori, Peter Alexander.*

O problema declarado: MCP tem **três respostas** para "o servidor ainda não terminou" —
Tasks, `subscriptions/listen` e notificações de progresso — espalhadas por Working Groups
diferentes, sem ciclo de vida, modelo de cancelamento ou superfície de erro comuns.
"O risco é ter três respostas que não compõem."

Deste período:
- **Eventos iniciados pelo servidor** (Triggers & Events WG): canais e assinaturas para
  entrega *push*, inclusive **webhooks** — para o servidor avisar que o trabalho acabou,
  sem polling caro do cliente;
- **Revisão de composição** (Agents, Transports, Triggers & Events): garantir que Tasks e
  Triggers componham entre si e sirvam a casos concretos.

Além disso, continuação do trabalho em Tasks ([SEP-2663](https://modelcontextprotocol.io/seps/2663-tasks-extension))
rumo à **inclusão eventual no núcleo**.

### 3.2 Unificação e endurecimento do transporte HTTP-nativo

*Core Maintainers: Kurtis Van Gent, Nick Cooper.*

O problema: a `2026-07-28` fez do servidor remoto uma carga HTTP normal, e passou a
depender de especificidades de HTTP (cabeçalhos, códigos de status). Consequência: **todo
recurso HTTP-nativo precisa de um segundo desenho específico para stdio, ou não funciona
localmente.** Os SDKs mantêm dois pipelines, e o metadado está duplicado entre cabeçalhos
e corpo, com validação cruzada.

Deste período:
- **HTTP sobre stdio** (Transports WG): Streamable HTTP como **binding único**, falado
  sobre stdin/stdout para servidores locais. A hipótese é usar **HTTP/2 sobre stdio**,
  ganhando multiplexação e mantendo as garantias de segurança e ciclo de vida do
  subprocesso. **Se der certo, é a mudança mais elegante do roadmap.**
- **Caching**: estender a abordagem de `ttlMs`/`cacheScope` com **ETags**, permitindo
  versionar resultados de primitivas — inclusive de chamadas de ferramenta.

Fora do período nomeado: tratamento de erro padronizado em todas as superfícies; escopo de
capacidade para listas de ferramenta depois do SEP-2575; e configuração segura de servidor.

### 3.3 Identidade de agente e segurança para empresa

*Core Maintainers: Paul Carleton, Den Delimarsky.*

O problema declarado, com todas as letras: **"a autorização do MCP pressupõe uma pessoa
com um navegador no momento do consentimento."** Cada vez mais o chamador é um agente:
uma carga na nuvem com identidade própria, agindo por um usuário ausente, ou gerando
subagentes que deveriam receber autoridade **menor** que a do pai. E os servidores hoje se
apoiam em chave de API colada e refresh token de vida longa.

Deste período:
- **DPoP** (Agent Identity WG, em formação): finalizar a especificação de prova de posse e
  buscar adoção ampla;
- **Identidade de agente e delegação**: Workload Identity Federation
  ([SEP-1933](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1933)),
  o ID-JAG usado pela Enterprise-Managed Authorization, e troca de token
  ([RFC 8693](https://www.rfc-editor.org/rfc/rfc8693)), coordenados com os grupos
  **OAuth** e **WIMSE** do IETF.

Em discussão: **atestação de presença humana**, para distinguir cliente interativo de
agente sem cabeça.

> **Opinião:** esta é a frente que mais importa para adoção corporativa, e a mais difícil.
> "Quem é o agente, e com que autoridade ele age em nome de quem" é um problema que a
> indústria de identidade ainda não resolveu fora do MCP.

### 3.4 Primitivas melhores

*Core Maintainers: Kurtis Van Gent, Peter Alexander, Den Delimarsky.*

O problema, admitido no próprio roadmap: `tools/call` permite devolver `content` **e**
`structuredContent` ao mesmo tempo, o que "confundiu autores de servidor e de cliente e
produziu implementações divergentes".

Deste período:
- **Forma do resultado de ferramenta** (Core Primitives WG, em formação): redesenhar a
  interface de `tools/call`, resolvendo as disparidades de fidelidade entre tipos de
  retorno e simplificando o tratamento de saída estruturada e não estruturada;
- **Descoberta progressiva**: o cliente aprende ferramentas e recursos **à medida que
  precisa**, em vez de ingerir o catálogo inteiro, articulado com o trabalho de caching.
  É a resposta à tensão descrita em [60 §5](60-teoria-avancada.md);
- **Anotações de primitiva**: as anotações de conteúdo (`audience`, `priority`) declaram
  público e importância. Aplicá-las a resultados e recursos poderia resolver a confusão de
  visibilidade do [SEP-2200](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2200) —
  mas a maioria dos implementadores não as adotou e talvez nem saiba para que servem.
  **"Se não forem úteis, devemos considerar depreciá-las."**

Em paralelo, o File Uploads WG segue em operações de arquivo com escopo e semântica de
recurso tipo sistema de arquivos (leitura por faixa, listagem hierárquica).

### 3.5 Experiência de desenvolvimento dos SDKs

*Core Maintainers: Den Delimarsky, David Soria Parra.*

O problema: SDKs, servidores de referência e quickstarts são mantidos à mão. A tese é que
**a especificação mais uma suíte de conformidade revisada por humanos podem ser a fonte da
verdade** de que esses artefatos são gerados, para serem regenerados e revalidados a cada
release, em vez de consertados depois dela.

Deste período:
- **Contrato de extensão** (SDK WG): qual papel uma extensão vincula (host, cliente,
  servidor, agente); o que os SDKs devem suportar nativamente; como extensões são
  empacotadas; adição de capacidade como mudança versionada; autorização como área própria;
- **Experimento de artefatos gerados**: gerar um SDK Tier 1 candidato **e** os exemplos de
  quickstart a partir da especificação, validar contra a suíte de conformidade, e publicar
  o resultado com recomendação — inclusive dizendo quais camadas devem ser geração
  determinística e quais assistidas por modelo.

---

## 4. Governança — como se contribui hoje

Estruturada em `2025-11-25` e refinada em `2026-07-28`.

| Camada | O que é |
|---|---|
| **Core Maintainers** | autoridade final sobre SEPs |
| **Working Groups** | Agents, File Uploads, Inspector V2, Interceptors, Registry, SDK, Server Card, Skills Over MCP, Transports, Triggers & Events |
| **Interest Groups** | Authorization, Enterprise, Enterprise-Managed Authorization, Financial Services, Primitive Grouping, Security, Tool Annotations |
| **SEPs** | fluxo baseado em PR, arquivos markdown em `seps/`, numeração derivada do PR, patrocinador responsável, status por rótulo |
| **Tiers de SDK** | requisitos claros de suporte a recursos e compromisso de manutenção |
| **Ciclo de vida** | Active / Deprecated / Removed, janela mínima de 12 meses, registro público de depreciados |

Como entrar: identifique a área prioritária do seu SEP; leve-o ao Working Group
correspondente; traga o apoio do grupo. SEPs com WG por trás e ligação clara ao roadmap
andam mais rápido. Há também o caminho de **extensão experimental**
([SEP-2133](https://modelcontextprotocol.io/seps/2133-extensions)), em repositórios
`experimental-ext-`, antes de qualquer SEP formal.

---

## 5. Segurança — a fronteira aberta

O que aconteceu de mais relevante:

- **20/05/2026**: o **AI Security Center da NSA** publicou a *Cybersecurity Information
  Sheet* "Model Context Protocol (MCP): Security Design Considerations for AI-Driven
  Automation" — a primeira orientação de segurança de MCP vinda de uma agência estatal.
  Cobre controle de acesso, tratamento de prompt, execução de ferramenta, permissões de
  agente, auditabilidade e governança de integrações de terceiros; aponta risco em
  execução arbitrária de código, autenticação e autorização insuficientes, serialização
  insegura de dados de contexto, fluxos fracos de aprovação, gestão de token e sessão, e
  log de auditoria inadequado. Recomenda escrutínio elevado em produção.
- **Literatura acadêmica** consolidou taxonomia e ferramental: *tool poisoning*,
  *shadowing*, *rug pull*, *line jumping*; análises com taint em servidores MCP; toolkits
  unificados de análise; e trabalho sobre ocultação de metadados por **blocos TAG do
  Unicode**, demonstrada em três servidores independentes — a "lacuna de fidelidade da
  visão de aprovação", em que o que o humano vê não é o que o modelo lê.
- **CVE-2025-54136** (CVSS 7.2, "MCPoison", Check Point Research) tornou *rug pull* um
  problema com número, não só um conceito.

**O que a spec fez em resposta:** página normativa de boas práticas; validação de `iss`;
CIMD no lugar de DCR; `requestState` com exigência de integridade; regras estritas de
`$ref` e de composição em JSON Schema; requisitos de segurança para ícones; consentimento
explícito para configuração de servidor local com um clique.

**O que continua sem solução:** injeção de prompt. Ver [60 §2](60-teoria-avancada.md).
Nenhuma das mitigações é completa, e a postura defensável continua sendo poucos
servidores, de origem conhecida, com privilégio mínimo, em sandbox, com auditoria.

---

## 6. Debates em aberto na comunidade

Com opinião marcada como opinião.

### 6.1 Recursos e prompts sobreviverão?

Fato: adoção baixa nos clientes; a maioria dos servidores só implementa tools.
**Opinião:** recursos sobrevivem, porque `resource_link` é a resposta correta ao problema
de contexto, e a descoberta progressiva vai depender de algo parecido. Prompts são mais
frágeis — não têm um problema técnico que só eles resolvam, e concorrem com os mecanismos
de "skills"/comandos dos próprios hosts. O Working Group **Skills Over MCP** sugere que
essa fronteira está em disputa.

### 6.2 Tasks entra no núcleo?

O roadmap diz explicitamente "rumo à inclusão eventual da extensão no núcleo".
**Opinião:** entra, mas só depois da revisão de composição — porque incorporar Tasks sem
resolver a sobreposição com `subscriptions/listen` e progresso congelaria três respostas
para a mesma pergunta.

### 6.3 HTTP/2 sobre stdio dá certo?

**Opinião:** é a ideia mais elegante do roadmap. Elimina o binding duplo que hoje força
todo recurso a ser desenhado duas vezes. Riscos: complexidade de implementação em
linguagens sem biblioteca HTTP/2 servidor decente sobre um fluxo arbitrário, e a perda da
propriedade que faz o MCP ser fácil — hoje um servidor stdio é `readline` + `json.loads`.
Se a facilidade de escrever servidor se perder, o princípio de projeto nº 1 foi trocado
por elegância de arquitetura, e isso seria um mau negócio.

### 6.4 A depreciação de Sampling foi certa?

**Opinião: sim.** Sampling prometia servidor sem LLM próprio, mas nunca foi implementado
o bastante para se poder depender dele, embaralhava a fronteira de "o servidor não vê a
conversa", e não tinha modelo de custo. Chamar a API do provedor diretamente é mais
simples, mais audível e funciona em qualquer cliente. Quem perde são os servidores
comunitários gratuitos, que agora precisam de chave própria — perda real, mas menor que o
custo de manter um recurso que quase ninguém suporta.

### 6.5 MCP × A2A e outros protocolos de agente

MCP conecta agente a **ferramentas**. Protocolos de agente-para-agente tratam de
**agentes conversando entre si**. São camadas diferentes e não concorrentes por natureza.
**Opinião:** a pressão de convergência é real, e a criação do Agents WG e da AAIF (com
goose e AGENTS.md ao lado do MCP) sugere que a fronteira será negociada dentro da mesma
fundação em vez de virar guerra de padrões — o que é o melhor resultado possível.

---

## 7. O que observar nos próximos meses

| Sinal | Onde | Por que importa |
|---|---|---|
| SEPs de Triggers & Events | repositório de SEPs | define como o servidor avisa que terminou |
| Protótipo de HTTP/2 sobre stdio | Transports WG | pode unificar os dois transportes |
| Formação do Agent Identity WG | comunidade | DPoP e delegação |
| Redesenho de `tools/call` | Core Primitives WG | **mudança que quebra** para todo servidor |
| Descoberta progressiva | Core Primitives WG | resolve a escala de catálogo |
| Registry saindo de preview | registry | distribuição confiável |
| Experimento de SDK gerado | SDK WG | muda como os SDKs são mantidos |
| Remoção de Roots/Sampling/Logging | ≥ 12 meses após 28/07/2026, ou seja **não antes de 28/07/2027** | prazo real de migração |

---

## 8. Autoteste

1. Qual é a revisão vigente e qual foi a mudança de manchete dela?
2. Por que "roteamento por cabeçalho" importa para quem opera gateway?
3. Qual problema o roadmap identifica em ter Tasks, `subscriptions/listen` e progresso ao mesmo tempo?
4. Qual é o custo, segundo o roadmap, de o MCP ser HTTP-nativo? Qual a solução proposta?
5. Qual pressuposto da autorização do MCP o roadmap declara ultrapassado, e por quê?
6. Que defeito de `tools/call` o roadmap admite, e o que se planeja fazer?
7. O que o roadmap propõe fazer com as anotações de conteúdo, e sob qual condição?
8. Qual foi a primeira orientação estatal de segurança sobre MCP, de quem e quando?
9. Qual é a data mais cedo em que Roots, Sampling e Logging podem ser removidos? Por quê?
10. Escolha um dos debates da seção 6 e defenda a posição contrária à do texto.

---

**Anterior:** [60 · Teoria avançada](60-teoria-avancada.md) · **Próximo:** [70 · Prática](70-pratica.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Fontes: [Roadmap de 22/08/2026](https://modelcontextprotocol.io/development/roadmap),
[Blog · A especificação 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/),
[Changelog 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog),
[SDKs e tiers](https://modelcontextprotocol.io/docs/2026-07-28/sdk),
[Grupos de trabalho](https://modelcontextprotocol.io/community/working-interest-groups),
[Ciclo de vida de recursos](https://modelcontextprotocol.io/community/feature-lifecycle),
[Anthropic · doação à AAIF (09/12/2025)](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation),
[NSA · CSI sobre segurança do MCP (20/05/2026)](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/).
Versões de pacote conferidas em PyPI e npm nesta máquina em 01/09/2026.
As opiniões da seção 6 são deste material e estão declaradas como tais.*
