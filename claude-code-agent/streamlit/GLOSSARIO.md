# Glossário

> Todos os termos técnicos usados no curso. Termo em inglês entre parênteses
> quando é assim que o campo o usa. Verificado contra o Streamlit **1.63.0**.
> Ordem alfabética. `→` indica onde o termo é tratado a fundo.

---

## A

**AppSession** — a representação, no servidor, de **uma aba de navegador**
conectada. Guarda o `session_state`, o estado dos widgets e a fila de mensagens.
Uma aba = uma sessão. → [10](10-fundamentos.md)

**AppTest** (`st.testing.v1.AppTest`) — o framework de testes do Streamlit, desde
a versão 1.28 (outubro de 2023). Executa a app **sem navegador** e devolve a
árvore de elementos para inspeção. → [30](30-testes.md)

**Apache Arrow** — formato binário colunar em que os dados tabulares trafegam
entre servidor e navegador. É por isso que `pyarrow` é dependência obrigatória.

**Argon2id** — algoritmo moderno de hash de senha, resistente a ataque com GPU.
Preferível a PBKDF2 quando disponível. → [22](22-autenticacao-e-autorizacao.md)

**ASGI** (*Asynchronous Server Gateway Interface*) — o padrão de interface entre
servidor e aplicação Python assíncrona. O Streamlit adotou ASGI (Starlette) como
padrão na versão 1.57, em abril de 2026.

**Autenticação** — descobrir **quem** é o usuário. Resolvida por `st.login()` ou
por um proxy. Não confundir com autorização. → [22](22-autenticacao-e-autorizacao.md)

**Autorização** — decidir **o que** o usuário pode fazer. É sempre
responsabilidade sua, nunca do provedor de identidade.

---

## B

**BackMsg** — mensagem do **navegador para o servidor** (Protocol Buffers, pelo
WebSocket). Carrega, tipicamente, "reexecute com este estado de widgets".

**BLAKE2b** — função de hash rápida usada pelo Streamlit no cálculo de identidade
de elemento (com digest de 16 bytes; cai para MD5 em builds FIPS). Não é uso
criptográfico. → [60](60-teoria-avancada.md)

**Bloqueio otimista** (*optimistic locking*) — técnica de concorrência: cada
registro tem uma versão; a atualização só acontece se a versão não mudou desde a
leitura. Evita que a última gravação apague silenciosamente a primeira.
→ [21](21-backend-dados-e-conexoes.md)

---

## C

**Cache** — memorização do resultado de uma função, indexada pelos argumentos.
No Streamlit, `@st.cache_data` (dados) e `@st.cache_resource` (recursos).
→ [14](14-cache-e-dados.md)

**`cache_data`** — guarda uma **cópia serializada** do retorno. Cada chamador
recebe a sua cópia. Para DataFrame, lista, dicionário, resultado de consulta.

**`cache_resource`** — guarda **a referência** ao objeto, compartilhado por todas
as sessões. Para conexão de banco, cliente de API, modelo de ML.

**Callback** — função passada em `on_change` / `on_click`. **Roda antes do corpo
do script**, no mesmo rerun — o que é o que permite escrever na chave de um
widget. → [13](13-session-state-e-widgets.md)

**Chave de cache** (*cache key*) — o hash dos argumentos de uma função cacheada.
Argumentos com prefixo `_` **não** entram na chave.

**Chave de widget** (`key`) — identificador estável de um widget. Desde a 1.54, é
a **identidade principal**: com `key`, mudar rótulo ou opções não faz o usuário
perder a seleção. Use em todo widget de app real.

**`column_config`** — o dicionário que transforma um despejo de DataFrame num
relatório: formatos, rótulos, colunas fixadas, minigráficos, botões.
→ [18](18-tabelas-e-edicao.md)

**Componente customizado** — extensão em React/HTML que roda num **iframe** e
conversa com o Python por `Streamlit.setComponentValue()`.
→ [25](25-componentes-customizados.md)

**Contêiner** — um bloco que agrupa elementos: `st.container`, `st.columns`,
`st.tabs`, `st.expander`, `st.sidebar`, `st.form`, `st.popover`, `st.bottom`.

---

## D

**Daltonismo** (*color vision deficiency*, CVD) — deficiência de visão de cores;
atinge cerca de 8% dos homens. Deuteranopia, protanopia e tritanopia são os
tipos. Motivo pelo qual a cor nunca pode ser o **único** diferenciador num
gráfico. → [17](17-graficos-e-visualizacao.md)

**Delta** — a instrução "coloque este elemento nesta posição da árvore". É a
unidade de atualização de tela do Streamlit.

**`delta_path`** — a posição de um elemento na árvore, como lista de índices
(ex.: `[0, 3, 1]`). A identidade dos elementos é **posicional**.

**`DeltaGenerator`** — o objeto devolvido por todo comando de escrita; funciona
como um cursor que aponta para uma posição da árvore. É o que permite escrever
fora de ordem.

**ΔE (Delta E)** — medida numérica de diferença entre duas cores. Usada para
verificar se duas séries continuam distinguíveis sob daltonismo (alvo ≥ 8) e para
visão normal (piso 15).

---

## E

**Escopo de cache** (`scope`) — `"global"` (padrão; compartilhado por todas as
sessões) ou `"session"` (por aba). Em app com dado segmentado por usuário, use
`"session"`.

**Estado da sessão** → ver *`session_state`*.

**Estado vazio** — a situação em que o filtro não devolve nada. É um estado
**normal**, não uma exceção, e é o caminho que mais derruba painel.
→ [16](16-layout-e-design.md)

---

## F

**Fragmento** (`@st.fragment`) — função que **reexecuta sozinha**, sem reexecutar
o script inteiro. Estável desde a 1.37 (julho de 2024). Aceita `run_every`,
`parallel` e `key`. → [15](15-fragments-e-performance.md)

**`ForwardMsg`** — mensagem do **servidor para o navegador**. Campos incluem
`delta`, `new_session`, `script_finished`, `navigation`, `auto_rerun`,
`dataframe_chunk`, entre outros.

**Formulário** (`st.form`) — agrupa widgets de modo que **nenhum** deles dispare
rerun; só o `form_submit_button` dispara.

---

## G

**GIL** (*Global Interpreter Lock*) — o travamento do CPython que permite só uma
thread executando bytecode Python por vez. É liberado durante I/O e dentro de
código C (numpy, pandas). Explica por que duas sessões fazendo laço Python puro
competem, e duas fazendo consulta ao banco, não. → [60](60-teoria-avancada.md)

---

## H

**Hasher** — o componente que calcula a chave de cache a partir dos argumentos.
Conhece explicitamente pandas, polars, numpy, PIL, Pydantic, entre outros; para o
resto, levanta `UnhashableTypeError`.

**Hibernação** (*app sleeping*) — no Community Cloud, o adormecimento da app após
12 horas sem tráfego. Qualquer visitante a acorda.

---

## I

**Identidade de elemento** (*element ID*) — o identificador calculado por
`_compute_element_id` a partir do tipo, da `key`, dos argumentos, do hash do
script ativo e do contêiner. → [60](60-teoria-avancada.md)

**Injeção de SQL** — ataque em que a entrada do usuário vira código SQL. Defesa:
parâmetros ligados (`?`), sempre; e lista branca para nomes de coluna.
→ [29](29-seguranca.md)

**Invalidação de cache** — apagar entradas que ficaram velhas. Depois de gravar no
banco, `funcao.clear()` é obrigatório — sem ele, "salvei e não apareceu".

---

## L

**`lazy=True`** — parâmetro de `st.dataframe` (desde a 1.61) que carrega as linhas
sob demanda, em pedaços, em vez de mandar a tabela inteira ao navegador.

---

## M

**Magic** — a escrita automática de uma expressão solta numa linha, sem
`st.write`. Implementada por reescrita da árvore sintática do script. Desligável
com `runner.magicEnabled = false`.

**Material Symbols** — o conjunto de ícones do Google, usado com a sintaxe
`:material/nome:`. Preferível a emoji, que muda de aparência por sistema
operacional.

**Migração** (de esquema) — passo numerado e idempotente que altera a estrutura do
banco. Nunca se edita uma migração já publicada; acrescenta-se outra.
→ [21](21-backend-dados-e-conexoes.md)

---

## O

**OIDC** (*OpenID Connect*) — protocolo de autenticação sobre OAuth 2.0. É o que
`st.login()` implementa. Diz **quem** é o usuário; não diz o que ele pode fazer.

---

## P

**Paleta categórica** — conjunto de cores usado para distinguir **identidades**
(séries). A **ordem** faz parte da validação: as cores foram ordenadas para que
os pares vizinhos se separem.

**Paleta sequencial** — um **único** matiz, do claro ao escuro, para representar
magnitude. Nunca arco-íris.

**Paleta divergente** — dois matizes opostos com **cinza** no meio, para
representar polaridade (acima/abaixo de uma referência).

**PBKDF2** — algoritmo de derivação de chave usado para hash de senha, com sal e
custo alto (iterações). Usado no projeto-modelo. Menos moderno que Argon2id, e
muito melhor que SHA-256 puro.

**PEP 668** — a especificação que faz o `pip` recusar instalar no Python do
sistema (`externally-managed-environment`). A resposta certa é criar um ambiente
virtual. → [03](03-instalacao.md)

**Pool de conexões** — conjunto de conexões de banco mantidas abertas e
reutilizadas. `pool_pre_ping=True` testa a conexão antes de usar, e resolve o
"funciona de manhã, quebra à tarde".

**Protocol Buffers** (protobuf) — formato binário de serialização usado nas
mensagens entre servidor e navegador.

---

## Q

**Query params** — os parâmetros da URL (`?uf=SP`). Acessíveis por
`st.query_params`, ou ligados diretamente a um widget com `bind="query-params"`
(desde a 1.55). É o que torna um painel compartilhável por link.

---

## R

**Rerun** (reexecução) — a execução completa do script, do topo até o fim ou até
`st.stop()`, com o estado dos widgets fixado no início. **A ideia central do
Streamlit.** → [12](12-modelo-de-execucao-e-rerun.md)

**`run_every`** — parâmetro de `@st.fragment` que faz o fragmento reexecutar em
intervalos. O temporizador vive no **cliente**: fechar a aba interrompe o ciclo.

---

## S

**Sal** (*salt*) — valor aleatório, por usuário, misturado à senha antes do hash.
Faz com que duas pessoas com a mesma senha tenham hashes diferentes.

**`ScriptRunner`** — a thread que executa o script de uma sessão. Emite eventos
(`SCRIPT_STARTED`, `SCRIPT_STOPPED_FOR_RERUN`, `SCRIPT_STOPPED_WITH_SUCCESS`,
`FRAGMENT_STOPPED_WITH_SUCCESS`, `SHUTDOWN`).

**`SCRIPT_STOPPED_FOR_RERUN`** — o evento de **preempção**: chegou estado novo, o
run em andamento é abandonado. É por isso que efeito colateral precisa ser
transacional.

**Segredos** (`st.secrets`) — valores sensíveis lidos de `.streamlit/secrets.toml`
ou do ambiente. O arquivo **nunca** é versionado.

**Sessão** → ver *AppSession*.

**`session_state`** — dicionário **por aba** que sobrevive aos reruns. Some no F5,
no fechar da aba e no reinício do servidor. Não é banco de dados.
→ [13](13-session-state-e-widgets.md)

**Sessão fixa** (*sticky session*) — configuração do balanceador que faz todas as
requisições de um usuário irem ao mesmo processo. **Obrigatória** com mais de uma
réplica, porque o `session_state` mora na memória do processo.

**Starlette** — o framework ASGI que virou o servidor padrão do Streamlit na
versão 1.57 (abril de 2026), substituindo o Tornado.

**`st.App`** — ponto de entrada ASGI (desde a 1.53) que permite montar a app
Streamlit dentro de uma aplicação maior, com rotas e middleware próprios.
Recurso novo; use com cautela.

**`st.empty()`** — espaço reservado. Escrever nele **substitui** o conteúdo, em
vez de acrescentar. É o único jeito de substituir algo na tela.

**`st.stop()`** — encerra o rerun atual imediatamente. Ferramenta canônica de
guarda: sem permissão, sem dados, sem login → mensagem e `st.stop()`.

---

## T

**Tema** — o conjunto de cores, fontes, raios e cores de gráfico definido em
`[theme]` no `config.toml`. Desde 2025–2026 cobre fontes, cores de gráfico e um
tema separado para a barra lateral. → [20](20-tema-e-identidade-visual.md)

**Tornado** — o servidor assíncrono usado pelo Streamlit **até a versão 1.56**.
Não é mais dependência do pacote.

**Transação** — bloco de operações de banco que acontece por inteiro ou não
acontece. No Streamlit é **requisito**, não boa prática, porque o script pode ser
interrompido no meio.

**TTL** (*time to live*) — prazo de validade de uma entrada de cache. Escolhê-lo é
uma decisão **de negócio**: quão velho o número pode estar.

---

## U

**`UnhashableTypeError`** — erro do cache quando o *hasher* não sabe resumir um
argumento. Saídas: prefixo `_`, `hash_funcs`, ou mudar a assinatura.

---

## W

**WebSocket** — o protocolo de conexão persistente e bidirecional entre navegador
e servidor. É por ele que o Streamlit empurra atualizações. Todo proxy no caminho
**precisa** repassá-lo, com tempo limite longo — do contrário, "Connecting..."
para sempre. → [28](28-deploy-e-operacao.md)

**Widget** (controle) — elemento com que o usuário interage e que devolve um
valor: botão, campo, seletor, controle deslizante, tabela com `on_select`.

**`WidgetState`** — o dicionário `{id do widget: valor}` mantido pela sessão. É
fixado no início de cada rerun.

---

## X

**XSRF / CSRF** (*cross-site request forgery*) — ataque em que um site malicioso
faz o navegador da vítima enviar requisições à sua app. O Streamlit protege por
padrão (`server.enableXsrfProtection`); **não desligue** para "consertar" upload
atrás de proxy — conserte o proxy.

**XSS** (*cross-site scripting*) — ataque em que código JavaScript do atacante
executa no navegador de outro usuário. No Streamlit, o vetor é
`unsafe_allow_html=True` (ou `st.html`) com conteúdo dinâmico.
→ [29](29-seguranca.md)
