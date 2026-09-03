# 02 · Pré-requisitos

`Nível: iniciante` · `Escrito em 01/09/2026`

---

## 1. Conhecimento

### 1.1 Indispensável

Sem isto, você vai travar no primeiro erro e não vai saber o que perguntar.

| O que | Por que precisa | Onde aprender |
|---|---|---|
| **Terminal / linha de comando** | Você vai rodar servidores, ler `stderr`, editar arquivos de configuração. Todo servidor MCP local é um processo que alguém lança. | [Curso de Docker · linha de comando](../curso-docker/) · `man bash` · [Missing Semester (MIT)](https://missing.csail.mit.edu/) |
| **JSON** | O protocolo inteiro é JSON. Você precisa ler um objeto aninhado sem sofrer. | [json.org](https://www.json.org/json-pt.html) — 20 minutos bastam |
| **Uma linguagem: Python ou TypeScript** | Funções, tipos básicos, e o que é `async`/`await`. Os dois SDKs Tier 1 são assíncronos. | [uv-python](../uv-python/00-MAPA.md) para o ambiente Python |
| **Cliente/servidor e processos** | Entender que "servidor" aqui pode ser um processo filho no seu laptop, não uma máquina na nuvem. | [portas-de-rede](../portas-de-rede/00-MAPA.md) |
| **Noção do que é um LLM** | Saber que o modelo *escolhe* chamar a ferramenta, e que ele pode escolher errado. | [agentes-de-ia](../agentes-de-ia/00-MAPA.md) · [engenharia-de-prompt](../engenharia-de-prompt/00-MAPA.md) |

### 1.2 Ajuda muito (mas dá para começar sem)

| O que | Onde entra no MCP | Onde aprender |
|---|---|---|
| **HTTP: métodos, cabeçalhos, códigos de status** | O transporte remoto é HTTP puro: POST, 200/400/403/405, cabeçalhos `Mcp-*`. | [apis](../apis/00-MAPA.md) |
| **JSON Schema** | Toda ferramenta declara `inputSchema` e opcionalmente `outputSchema` em JSON Schema 2020-12. | [json-schema.org/learn](https://json-schema.org/learn) |
| **JSON-RPC 2.0** | É a moldura de toda mensagem MCP. Spec curta, lê-se em 30 minutos. | [jsonrpc.org/specification](https://www.jsonrpc.org/specification) |
| **OAuth 2.1 / OIDC** | Obrigatório para servidor remoto autenticado. É a parte mais difícil do MCP. | [jwt](../jwt/00-MAPA.md) · [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728) |
| **TLS** | Servidor remoto sem HTTPS é inaceitável em produção. | [tls](../tls/00-MAPA.md) |
| **SSE (Server-Sent Events)** | Respostas em fluxo e `subscriptions/listen` usam SSE. | [MDN · Server-sent events](https://developer.mozilla.org/docs/Web/API/Server-sent_events) |
| **Docker** | Muitos servidores de terceiros são distribuídos como imagem; é também a forma sã de isolar servidor de origem duvidosa. | [curso-docker](../curso-docker/) |

### 1.3 O que você **não** precisa saber

Diga-se, para não intimidar ninguém:

- **Não** precisa saber treinar modelos, nem nada de machine learning.
- **Não** precisa saber a API da Anthropic/OpenAI para escrever um servidor.
- **Não** precisa saber Rust, Go, C# ou Java — há SDK, mas Python e TypeScript
  cobrem 95% do que se escreve.

---

## 2. Ambiente

### 2.1 Requisitos mínimos, por caminho

| Caminho | Mínimo | Recomendado (testado em 01/09/2026) |
|---|---|---|
| **Python** | Python **3.10** (`mcp` 2.x exige `>=3.10`) | Python 3.12 ou 3.13 via `uv` 0.12.7 |
| **TypeScript/Node** | Node **20** (`@modelcontextprotocol/server` 2.0.0 exige `>=20`) | Node **22.19+**, porque o **Inspector 2.4.0 exige `node >=22.19.0`** |
| **Inspector** | Node ≥ 22.19.0 | Node 24.18.0 |
| **Host para testar** | qualquer um: Claude Code, Claude Desktop, VS Code, Cursor | Claude Code (CLI, dá para versionar a config) |

### 2.2 Hardware

Modesto. Um servidor MCP é um processo pequeno.

- **RAM:** 2 GB livres cobrem tranquilamente Node + Python + Inspector.
  Se você for rodar 10 servidores stdio simultâneos (o Claude Desktop com muitos
  conectores), conte ~50–150 MB cada. É o número que estoura a máquina de gente
  que instala 30 servidores "para experimentar".
- **Disco:** ~1,5 GB para Node + Python + as duas SDKs + Inspector. O `node_modules`
  do Inspector sozinho passa de 200 MB.
- **Arquitetura:** x86-64 e arm64 (Apple Silicon) são de primeira classe nos dois SDKs.
- **Rede:** não é preciso rede para servidor stdio local. Só a instalação precisa.

### 2.3 Contas e cadastros

| Serviço | Precisa? | Cartão de crédito? |
|---|---|---|
| Escrever e testar um servidor MCP | **Não** | Não |
| Usar o MCP Inspector | **Não** | Não |
| Claude Code / Claude Desktop (host) | Sim, conta Anthropic | Plano gratuito existe; ver [80](80-custos-e-licencas.md) |
| Publicar no **MCP Registry** | Conta GitHub, ou domínio próprio para verificação por DNS | Não |
| Servidor MCP remoto de terceiro (Sentry, GitHub, Linear…) | Conta no serviço | Depende do serviço |

> **Ponto importante:** para **aprender MCP inteiro** — escrever servidor, cliente,
> testar, depurar, ler a fita JSON-RPC — você **não precisa de nenhuma conta em
> lugar nenhum e não precisa de nenhum LLM**. O host pode ser o Inspector, e o
> Inspector é local, gratuito e MIT.

---

## 3. Tempo realista até cada nível

Números honestos, para alguém que já programa e estuda com foco. Se você estuda
1 h por dia com interrupções, multiplique por 2.

| Nível | O que você consegue fazer | Tempo |
|---|---|---|
| **Entender o conceito** | explicar MCP para um colega, saber quando usar | **2–3 h** (arquivos 01, 10, 12) |
| **Primeiro servidor rodando** | 2 ferramentas, testado no Inspector, ligado ao seu host | **3–5 h** (arquivos 03, 04) |
| **Servidor útil de verdade** | erros tratados, schemas bons, sem estourar contexto, com teste | **15–25 h** (arquivos 05, 06, 07, 23) |
| **Servidor remoto com HTTP** | Streamable HTTP, Docker, deploy, TLS | **+15–25 h** (arquivos 14, 24) |
| **Servidor remoto autenticado** | OAuth 2.1, PRM, escopos, audiência validada | **+25–50 h** — é aqui que dói ([18](18-autorizacao.md)) |
| **Cliente/host próprio** | consumir servidores, aprovação humana, MRTR | **+25–40 h** ([16](16-primitivas-do-cliente.md), [20](20-clientes-e-hosts.md)) |
| **Nível "leio a spec e discordo dela"** | acompanhar SEPs, contribuir, projetar extensões | **150–300 h** e alguns meses de calendário |

**Onde as pessoas subestimam, sempre:** autorização (item 5) e projeto de ferramentas
(item 3). Escrever `tools/call` é trivial; escrever uma ferramenta que um modelo usa
*corretamente* na décima vez, sem alucinar argumentos e sem entupir o contexto, é
engenharia de verdade.

---

## 4. Rota de resgate — se faltar um pré-requisito

Não pare o estudo. Faça o desvio mínimo e volte.

| Falta | Desvio mínimo (não o curso inteiro) | Volte para |
|---|---|---|
| **Terminal** | Aprenda 8 comandos: `cd`, `ls`, `cat`, `less`, `which`, `export`, `\|`, `>`. Uma tarde. | [03](03-instalacao.md) |
| **Python moderno** | Só `uv`: `uv init`, `uv add`, `uv run`. Não aprenda `venv`/`pip`/`poetry` agora. | [uv-python](../uv-python/00-MAPA.md), 2 h |
| **async/await** | Leia só o conceito de "corrotina que espera E/S". Nos dois SDKs você escreve funções normais; o SDK cuida do resto. Adiar é legítimo. | [04](04-como-comecar.md) |
| **JSON Schema** | Aprenda 5 coisas: `type`, `properties`, `required`, `description`, `enum`. O resto depois. Nos SDKs você nem escreve o schema: ele é gerado das anotações de tipo. | [05](05-manual-de-uso.md) |
| **HTTP** | Adie. Comece com **stdio**, que não usa HTTP nenhum. Só vá para HTTP quando precisar de servidor remoto. | [14](14-transportes.md) |
| **OAuth** | Adie agressivamente. Escreva 3 servidores stdio antes de encostar em OAuth. É o conselho mais útil deste arquivo. | [18](18-autorizacao.md) |
| **Não tenho como instalar nada** | Use um playground/container: veja a seção "Alternativa sem instalar nada" em [03](03-instalacao.md#12-alternativa-sem-instalar-nada). | [04](04-como-comecar.md) |
| **Não tenho conta em LLM nenhum** | Use o **MCP Inspector** como host. Ele exercita 100% do protocolo sem nenhum modelo. | [04](04-como-comecar.md) |

---

## 5. Ordem de leitura recomendada

Se você quer **resultado rápido**:
[03](03-instalacao.md) → [04](04-como-comecar.md) → [07](07-projeto-modelo/README.md) → [06](06-exemplos.md) → volte para [10](10-fundamentos.md).

Se você quer **entender antes de fazer**:
[01](01-introducao-leigo.md) → [10](10-fundamentos.md) → [12](12-arquitetura.md) → [13](13-json-rpc-e-a-camada-base.md) → [03](03-instalacao.md) → [04](04-como-comecar.md).

Se você vai **decidir se a empresa adota**:
[01](01-introducao-leigo.md) → [19](19-seguranca.md) → [80](80-custos-e-licencas.md) → [65](65-estado-da-arte.md) → [75](75-armadilhas.md).

---

## 6. Autoteste

1. Qual a versão mínima de Python para o SDK `mcp` 2.x? E de Node para o Inspector 2.4.0?
2. Você precisa de uma conta em algum LLM para aprender MCP a fundo? Justifique.
3. Qual pré-requisito este arquivo manda **adiar agressivamente**, e por quê?
4. Por que "async/await" pode ser adiado mesmo os SDKs sendo assíncronos?
5. Quanto tempo, honestamente, até um servidor remoto autenticado com OAuth?
6. Se você não pode instalar nada na máquina, qual é a rota?
7. Quantos MB de RAM, aproximadamente, custa cada servidor stdio ativo?

---

**Anterior:** [01 · Introdução](01-introducao-leigo.md) · **Próximo:** [03 · Instalação](03-instalacao.md) · **Índice:** [00-MAPA](00-MAPA.md)

*Versões conferidas em 01/09/2026 na própria máquina: `mcp` 2.1.1 (`Requires-Python: >=3.10`),
`@modelcontextprotocol/server` 2.0.0 (`engines.node >=20`), `@modelcontextprotocol/inspector`
2.4.0 (`engines.node >=22.19.0`), `uv` 0.12.7, Node 24.18.0, npm 12.0.1.*
