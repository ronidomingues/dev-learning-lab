# 65 · Estado da arte — setembro de 2026

> **Nível:** pesquisa · **Escrito em:** 02/09/2026
> **Este arquivo envelhece rápido.** A versão de referência é a **1.63.0**,
> publicada em 01/09/2026. Fontes no rodapé; tudo consultado em 02/09/2026.

---

## 1. Onde o Streamlit está

| | Valor | Como sei |
|---|---|---|
| Versão | **1.63.0** (01/09/2026) | PyPI |
| Licença | **Apache 2.0** | metadados do pacote instalado |
| Python | **≥ 3.10** | `Requires-Python` do pacote |
| Servidor | **Starlette + Uvicorn** (ASGI) | dependências do pacote; sem Tornado |
| Cadência | uma versão a cada 2–4 semanas | notas de versão de 2026 |
| Dono | Snowflake, desde março de 2022 | anúncio público |

**A mudança estrutural de 2026 é a troca do servidor.** Até a 1.56 era Tornado
(a partir da 1.53, opcional via `server.useStarlette`); a partir da **1.57**
(29/04/2026), Starlette com Uvicorn é o padrão. Consequências verificáveis:

- o pacote instalado hoje depende de `starlette`, `uvicorn`, `httptools`,
  `anyio`, `websockets` — e **não** traz Tornado;
- `st.App` permite montar a app dentro de outra aplicação ASGI, com rotas,
  *middleware*, `lifespan` e tratadores de exceção próprios;
- código antigo que estendia o servidor via Tornado quebrou.

---

## 2. O que 2026 trouxe, por tema

### 2.1 Desempenho: o modelo ganhando escapes

| Recurso | Versão | O que ataca |
|---|---|---|
| `st.dataframe(lazy=True)` | 1.61 (04/08) | volume enviado ao navegador; a tabela virou fluxo de pedaços (`dataframe_chunk` no protocolo) |
| `cache(refresh_mode="background")` | 1.61 | o usuário deixa de esperar o TTL expirar |
| `@st.fragment(parallel=True)` | 1.58 (28/05) | fragmentos de I/O deixam de esperar uns pelos outros |
| `st.pagination` | 1.58 | paginação nativa, sem gambiarra |

**A leitura:** os quatro atacam o mesmo problema — o custo do rerun completo — por
frentes diferentes. Nenhum muda o modelo; todos criam escapes. É o passo 3 do
padrão descrito em [11-historia.md](11-historia.md).

### 2.2 Estado e identidade

| Recurso | Versão | Por quê |
|---|---|---|
| identidade de widget **por chave** | 1.54 (04/02) | acabou com "mudei o rótulo e o usuário perdeu a seleção" |
| `bind="query-params"` | 1.55 (03/03) | estado na URL sem código: painel compartilhável por link |
| `persist_state="page"/"session"` | 1.5x | widget condicional deixa de perder o valor |
| contêineres dinâmicos com `on_change` | 1.55 | reação a mudança de aba, expander, popover |

**Minha leitura, e é opinião:** a ligação de widget a query params é a mudança de
2026 com maior efeito prático no dia a dia de quem faz painel. Ela transforma o
link em relatório, e era o que faltava para o Streamlit competir de igual para
igual com ferramenta de BI no quesito compartilhamento.

### 2.3 Aparência

Cores de gráfico no tema (1.54), fontes e pesos configuráveis, tema separado para
a barra lateral, `baseRadius`/`buttonRadius`, `:shimmer[]` (1.57),
`st.skeleton` (1.59), `st.space`, `st.bottom` (1.57), `st.mermaid_chart` (1.59).

**A leitura:** o objetivo declarado é fazer com que a app pareça um produto **sem
CSS**. Vale — porque CSS mirando classe interna do Streamlit é dívida garantida.

### 2.4 Segurança e requisitos corporativos

| Recurso | Versão |
|---|---|
| `client.disableDataExport` | 1.60 (21/07) |
| validação de mensagens do host, limite de query string | 1.60 |
| `server.allowedHosts` (contra *DNS rebinding*) | — |
| `server.trustedUserHeaders` (identidade vinda do proxy) | — |
| `st.user.tokens` | 1.53 |

**A leitura:** é o Streamlit atendendo à lista de exigências de time de segurança
corporativa. Sinal claro de para onde o produto está indo: uso interno em empresa
grande, não protótipo pessoal.

### 2.5 Entrada e interação

Validação no cliente e tipos (`email`, `url`, `phone`, `search`) em
`st.text_input` (1.62), `ButtonColumn` (1.59), seleção programática em dataframe
(1.56), `filter_mode="fuzzy"` em seletores (1.56), `st.menu_button` e `st.iframe`
(1.56), `wrap` em layouts (1.62), atalho de teclado em botões.

### 2.6 IA como público-alvo declarado

`streamlit skills` (1.58) instala, no seu projeto, instruções que os agentes de
código (Claude Code e compatíveis) leem para escrever Streamlit idiomático **da
versão que você tem instalada**:

```bash
streamlit skills            # no projeto
streamlit skills --global   # uma vez, para todos os projetos
```

**Isto é notável e vale um parágrafo.** Um framework passar a distribuir
documentação **para máquinas** junto com o pacote é um reconhecimento explícito de
que boa parte do código que o usa hoje é escrita com assistência de IA. É a
primeira vez que vejo isso empacotado com a biblioteca em vez de publicado num
site à parte. Se a prática pegar, muda como bibliotecas versionam documentação.

---

## 3. Streamlit in Snowflake: o produto pago

Marcos de 2026, com data (documentação da Snowflake):

- **09/03/2026** — *container runtime* em disponibilidade geral: as apps rodam em
  Snowpark Container Services, com **GPU**, pacotes Python amplos e **sem
  hibernação por inatividade**;
- **01/06/2026** — *Streamlit in Snowflake in Workspaces* em disponibilidade
  geral: edição em arquivos dentro do Snowsight, com publicação separada da
  edição;
- **1.53** — conexões com escopo de sessão e *caller's rights*.

**O que isso significa:** o modelo de negócio está claro. O Streamlit
código-aberto é gratuito e continua sendo; o dinheiro está na computação vendida
quando a app roda **dentro** do Snowflake, cobrada em créditos. Ver
[80-custos-e-licencas.md](80-custos-e-licencas.md).

**A tensão a observar, e é opinião:** recursos que só fazem sentido dentro do
Snowflake recebem investimento; recursos que só interessam a quem roda em outro
lugar disputam prioridade. Até agora isso não prejudicou o projeto aberto — as
melhorias de 2026 listadas acima beneficiam todo mundo. É algo para acompanhar,
não para alarmar.

---

## 4. O ecossistema em 2026

| Ferramenta | Posição em setembro de 2026 |
|---|---|
| **Streamlit** | o padrão de fato para painel e app de dados em Python |
| **Gradio** | domina demonstração de modelo de IA; ligado ao Hugging Face |
| **Dash** | firme no analítico complexo, corporativo |
| **Reflex** | é para onde vão os projetos que **cresceram demais** para o Streamlit: rotas, estado de verdade, tarefas em segundo plano |
| **marimo** | notebook **reativo** com grafo de dependências de verdade; ocupa o espaço entre notebook e app |
| **Shiny for Python** | o modelo reativo formal, para quem quer granularidade sem sair do Python |
| **NiceGUI** | app interno com interação por eventos |
| **Panel / Holoviz** | científico, volumes grandes |

**marimo merece atenção**, e não é concorrente direto: ele resolve o problema do
notebook (ordem de execução, irreprodutibilidade) com um grafo de dependências
entre células — exatamente a reatividade que o Streamlit recusa a construir
([ver 60, seção 7](60-teoria-avancada.md)). Para trabalho exploratório, é hoje
uma escolha melhor que Jupyter; para entregar um painel a alguém, o Streamlit
continua sendo mais direto.

**Reflex ganhou tração como "o próximo passo"**, e a própria comunicação deles é
essa. Se você bateu no teto do Streamlit, é o candidato mais óbvio.

---

## 5. Debates em aberto

**1. O modelo de rerun escala como padrão, ou virou legado?**
A cada versão saem mais escapes (fragmentos, paralelismo, `lazy`, refresh em
segundo plano). Em algum ponto, um sistema feito só de escapes deixa de ter um
modelo simples. *Minha aposta:* o rerun continua sendo o padrão por bons anos,
porque é ele que torna a curva de entrada baixa — e a curva de entrada baixa é o
produto.

**2. `st.App` vai virar o caminho principal?**
Montar Streamlit dentro de FastAPI resolve um pedido antigo ("preciso de um
endpoint"). *Minha opinião:* continue com dois processos e um `nucleo/`
compartilhado, até `st.App` amadurecer e a documentação encorpar.

**3. Streamlit vira plataforma ou continua biblioteca?**
`streamlit init`, `streamlit skills`, tema completo, `st.App` — tudo aponta para
plataforma. O risco é o de sempre: cada peça a mais é superfície a manter.

**4. O que o CPython sem GIL (PEP 703) muda?**
Em teoria, `parallel=True` passa a valer para trabalho de CPU e um processo passa
a atender mais sessões ativas. Na prática, depende de todo o ecossistema de dados
(numpy, pandas, pyarrow) suportar bem o modo sem GIL. **Ainda não é o caso em
setembro de 2026.**

**5. Reatividade fina, algum dia?**
Tecnicamente possível (Shiny e marimo mostram como). Custaria o "é só Python
normal". *Minha opinião:* não vai acontecer, e é a decisão certa — quem quer isso
tem marimo, Shiny e Reflex.

---

## 6. O que observar nos próximos 12 meses

Sinais que vale acompanhar, e o que cada um significaria:

1. **`st.App` sair de experimental** → integração séria com o mundo ASGI.
2. **Alguma forma de sessão persistente** (estado fora do processo) → mudaria o
   deploy: réplicas sem sessão fixa, deploy sem derrubar sessões.
3. **Mais recursos exclusivos do Snowflake** → sinal de divergência entre o
   projeto aberto e o produto pago.
4. **Adoção de `streamlit skills`** por outras bibliotecas → nova prática de
   documentação versionada para agentes.
5. **Ecossistema de dados no CPython sem GIL** → destrava paralelismo real.
6. **`st.dataframe` lazy virar padrão** → o modelo "mande a tela inteira" cedendo
   por completo em dados tabulares.

---

## 7. Resumo em cinco frases

1. O Streamlit é o padrão de fato para painel e app de dados em Python, e não há
   sinal de mudança disso.
2. 2026 foi o ano da troca de motor: Tornado saiu, Starlette/ASGI entrou.
3. As melhorias do ano atacam o custo do rerun por escapes — não trocam o modelo.
4. O produto pago é *Streamlit in Snowflake*; o projeto aberto continua Apache 2.0
   e bem cuidado.
5. Quem cresce demais migra para Reflex; quem quer notebook reativo vai para
   marimo; quem quer reatividade formal vai para Shiny. O Streamlit continua sendo
   o caminho mais curto entre um script e um painel.

---

## Autoteste

1. Qual é a mudança estrutural de 2026, e como você a verifica no pacote instalado?
2. Cite quatro recursos de 2026 que atacam o custo do rerun, e o que cada um ataca.
3. Por que `bind="query-params"` é a mudança de maior efeito prático do ano?
4. O que `streamlit skills` faz, e por que isso é notável?
5. Quais foram os dois marcos de *Streamlit in Snowflake* em 2026, e o que eles
   revelam do modelo de negócio?
6. O que o marimo resolve que o Streamlit recusa a resolver?
7. Quando alguém deveria migrar para Reflex?
8. O que o CPython sem GIL mudaria, e por que ainda não muda?

---

## Fontes consultadas (02/09/2026)

- Notas de versão de 2026 — <https://docs.streamlit.io/develop/quick-reference/release-notes/2026>
- Pacote `streamlit` 1.63.0 no PyPI e seus metadados — verificação local
- `streamlit skills --help` da 1.63.0 — verificação local
- Endpoints do servidor 1.63.0 — verificação local (`/_stcore/health`, `/_stcore/stream`, `/_stcore/metrics`)
- Snowflake, notas de versão: *SiS container runtime GA* (09/03/2026) — <https://docs.snowflake.com/en/release-notes/2026/other/2026-03-09-sis-container-runtime-ga>
- Snowflake, notas de versão: *Streamlit in Snowflake in Workspaces GA* (01/06/2026) — <https://docs.snowflake.com/en/release-notes/2026/other/2026-06-01-streamlit-in-workspaces-ga>
- Comparativos de ecossistema, 2026 — reflex.dev/blog, deepnote.com/alternatives/streamlit, rguides.dev
