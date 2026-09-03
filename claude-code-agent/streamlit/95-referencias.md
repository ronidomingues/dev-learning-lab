# 95 · Referências — documentação, código-fonte, specs e pessoas

> **Nível:** todos · **Verificado em:** 02/09/2026 · Streamlit 1.63.0
> Aqui só entram fontes primárias: documentação oficial, código-fonte,
> especificações e canais dos mantenedores.

---

## 1. Oficial

| Recurso | Endereço |
|---|---|
| Documentação | <https://docs.streamlit.io> |
| Referência de API | <https://docs.streamlit.io/develop/api-reference> |
| Conceitos → arquitetura | <https://docs.streamlit.io/develop/concepts/architecture> |
| Tutoriais | <https://docs.streamlit.io/develop/tutorials> |
| Notas de versão | <https://docs.streamlit.io/develop/quick-reference/release-notes> |
| Notas de 2026 | <https://docs.streamlit.io/develop/quick-reference/release-notes/2026> |
| Cheat sheet | <https://docs.streamlit.io/develop/quick-reference/cheat-sheet> |
| Referência de configuração | <https://docs.streamlit.io/develop/api-reference/configuration/config.toml> |
| Deploy | <https://docs.streamlit.io/deploy> |
| Community Cloud | <https://docs.streamlit.io/deploy/streamlit-community-cloud> |
| App testing | <https://docs.streamlit.io/develop/concepts/app-testing> |
| Galeria de apps | <https://streamlit.io/gallery> |
| Componentes | <https://streamlit.io/components> |
| Blog | <https://blog.streamlit.io> |
| Fórum | <https://discuss.streamlit.io> |
| Site | <https://streamlit.io> |

No terminal: `streamlit docs` abre a documentação da **sua** versão.

---

## 2. Código-fonte

Repositório: <https://github.com/streamlit/streamlit> · licença **Apache 2.0**

| Onde | O quê |
|---|---|
| [`lib/streamlit/`](https://github.com/streamlit/streamlit/tree/develop/lib/streamlit) | a biblioteca Python |
| [`frontend/`](https://github.com/streamlit/streamlit/tree/develop/frontend) | o front em React/TypeScript |
| [`proto/streamlit/proto/`](https://github.com/streamlit/streamlit/tree/develop/proto/streamlit/proto) | **o protocolo** — `ForwardMsg.proto`, `BackMsg.proto`, `Delta.proto` |
| [`component-template`](https://github.com/streamlit/component-template) | modelo para componente customizado |
| [`streamlit/docs`](https://github.com/streamlit/docs) | a documentação, em Markdown |
| [Issues](https://github.com/streamlit/streamlit/issues) | veja se o seu bug é conhecido antes de investigar sozinho |
| [Releases](https://github.com/streamlit/streamlit/releases) | detalhe técnico de cada versão |

### Ordem de leitura do código, para entender por dentro

Os caminhos são relativos a `lib/streamlit/` (ou ao seu
`site-packages/streamlit/`, que é onde eu os li para escrever o
[60-teoria-avancada.md](60-teoria-avancada.md)):

| Arquivo | O que ele responde |
|---|---|
| `runtime/scriptrunner/script_runner.py` | o laço principal, os eventos, a nota sobre threads |
| `runtime/app_session.py` | o ciclo de vida de uma sessão |
| `delta_generator.py` | como um `st.*` vira mensagem |
| `elements/lib/utils.py` | `_compute_element_id` — a identidade de widget |
| `runtime/state/session_state.py` | o estado e as regras de escrita |
| `runtime/caching/hashing.py` | o *hasher* do cache e os tipos que ele conhece |
| `runtime/caching/cache_data_api.py` / `cache_resource_api.py` | os dois decoradores |
| `runtime/fragment.py` | como o fragmento funciona |
| `config.py` | **todas** as opções de configuração, com descrição |
| `proto/ForwardMsg.proto` | o protocolo inteiro |

**Dica que economiza tempo:** a fonte mais confiável sobre a *sua* versão é a
*sua* instalação. Em vez de procurar na documentação:

```python
import inspect, streamlit as st
print(inspect.signature(st.metric))
print(inspect.getsource(st.fragment))
print([n for n in dir(st.column_config) if not n.startswith("_")])
```

Foi assim que as assinaturas do [05-manual-de-uso.md](05-manual-de-uso.md) foram
levantadas.

---

## 3. Especificações e padrões relevantes

| Spec | Onde | Por que importa |
|---|---|---|
| **OpenID Connect Core 1.0** | <https://openid.net/specs/openid-connect-core-1_0.html> | é o que `st.login()` implementa |
| **OAuth 2.0** (RFC 6749) | <https://datatracker.ietf.org/doc/html/rfc6749> | a base do OIDC |
| **WebSocket** (RFC 6455) | <https://datatracker.ietf.org/doc/html/rfc6455> | o transporte do Streamlit |
| **Protocol Buffers** | <https://protobuf.dev> | o formato das mensagens |
| **Apache Arrow** | <https://arrow.apache.org/docs/format/Columnar.html> | como os DataFrames trafegam |
| **ASGI** | <https://asgi.readthedocs.io> | o padrão do servidor desde a 1.57 |
| **PEP 668** | <https://peps.python.org/pep-0668/> | o `externally-managed-environment` do [03](03-instalacao.md) |
| **PEP 703** (CPython sem GIL) | <https://peps.python.org/pep-0703/> | o que mudaria o paralelismo — ver [65](65-estado-da-arte.md) |
| **WCAG 2.2** | <https://www.w3.org/TR/WCAG22/> | contraste e acessibilidade ([16](16-layout-e-design.md)) |
| **OWASP Top 10** | <https://owasp.org/www-project-top-ten/> | o mínimo de segurança ([29](29-seguranca.md)) |
| **Apache License 2.0** | <https://www.apache.org/licenses/LICENSE-2.0> | a licença do Streamlit |

---

## 4. Bibliotecas do ecossistema

| Biblioteca | Documentação | Papel |
|---|---|---|
| pandas | <https://pandas.pydata.org/docs/> | dependência obrigatória; 95% de um painel |
| numpy | <https://numpy.org/doc/> | dependência obrigatória |
| pyarrow | <https://arrow.apache.org/docs/python/> | serialização de tabelas |
| altair | <https://altair-viz.github.io> | **já vem instalado** |
| plotly | <https://plotly.com/python/> | gráficos interativos, o mais usado em painel |
| matplotlib | <https://matplotlib.org/stable/> | gráficos estáticos |
| pydeck | <https://deckgl.readthedocs.io> | mapas |
| SQLAlchemy | <https://docs.sqlalchemy.org> | extra `sql`, base do `st.connection` |
| Authlib | <https://docs.authlib.org> | extra `auth`, base do `st.login` |
| Starlette | <https://www.starlette.io> | o servidor, desde a 1.57 |
| Uvicorn | <https://www.uvicorn.org> | o executor ASGI |
| uv | <https://docs.astral.sh/uv/> | gerenciador de projeto recomendado |
| pytest | <https://docs.pytest.org> | testes |
| polars | <https://docs.pola.rs> | alternativa ao pandas; o cache do Streamlit já a conhece |

---

## 5. Componentes da comunidade

Catálogo: <https://streamlit.io/components>

| Componente | Repositório |
|---|---|
| streamlit-aggrid | <https://github.com/PablocFonseca/streamlit-aggrid> |
| streamlit-folium | <https://github.com/randyzwitch/streamlit-folium> |
| streamlit-extras | <https://github.com/arnaudmiribel/streamlit-extras> |
| streamlit-option-menu | <https://github.com/victoryhb/streamlit-option-menu> |
| streamlit-echarts | <https://github.com/andfanilo/streamlit-echarts> |
| streamlit-ace | <https://github.com/okld/streamlit-ace> |

Antes de adotar qualquer um, aplique os seis critérios do
[25-componentes-customizados.md](25-componentes-customizados.md).

---

## 6. Pessoas e canais

| Quem | Papel | Onde |
|---|---|---|
| **Adrien Treuille** | cofundador e primeiro CEO | posts históricos no blog do Streamlit |
| **Thiago Teixeira** | cofundador | idem |
| **Amanda Kelly** | cofundadora | idem |
| **Tyler Richards** | cientista de dados na Snowflake; autor do principal livro | <https://www.tylerjrichards.com> |
| **Chanin Nantasenamat** ("Data Professor") | o maior divulgador em vídeo | YouTube |
| **Equipe Streamlit** | responde no fórum e nas issues | <https://discuss.streamlit.io> |

---

## 7. Ferramentas alternativas — documentação oficial

Para a comparação de [31-quando-nao-usar-streamlit.md](31-quando-nao-usar-streamlit.md):

| Ferramenta | Documentação |
|---|---|
| Dash | <https://dash.plotly.com> |
| Gradio | <https://www.gradio.app/docs> |
| Reflex | <https://reflex.dev/docs> |
| NiceGUI | <https://nicegui.io/documentation> |
| Panel / Holoviz | <https://panel.holoviz.org> |
| Shiny for Python | <https://shiny.posit.co/py/> |
| marimo | <https://docs.marimo.io> |
| FastAPI | <https://fastapi.tiangolo.com> |

---

## 8. Streamlit in Snowflake

| Recurso | Endereço |
|---|---|
| Documentação SiS | <https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit> |
| Notas de versão da Snowflake | <https://docs.snowflake.com/en/release-notes/> |
| *Container runtime* GA (09/03/2026) | <https://docs.snowflake.com/en/release-notes/2026/other/2026-03-09-sis-container-runtime-ga> |
| *Workspaces* GA (01/06/2026) | <https://docs.snowflake.com/en/release-notes/2026/other/2026-06-01-streamlit-in-workspaces-ga> |

---

## 9. Assuntos relacionados neste repositório

| Assunto | Por que |
|---|---|
| [`uv-python`](../uv-python/00-MAPA.md) | o gerenciador recomendado no [03](03-instalacao.md) |
| [`sql`](../sql/00-MAPA.md) | filtrar no banco é a otimização nº 1 |
| [`postgresql`](../postgresql/00-MAPA.md) | o banco recomendado para produção |
| [`curso-docker`](../curso-docker/00-indice.md) | o deploy do [28](28-deploy-e-operacao.md) |
| [`hospedagem-de-aplicacoes-web`](../hospedagem-de-aplicacoes-web/00-MAPA.md) | proxy reverso, DNS, TLS |
| [`portas-de-rede`](../portas-de-rede/00-MAPA.md) | a porta 8501, firewall |
| [`tls`](../tls/00-MAPA.md) | HTTPS obrigatório |
| [`jwt`](../jwt/00-MAPA.md) | o token de identidade do OIDC |
| [`variaveis-de-ambiente-e-segredos`](../variaveis-de-ambiente-e-segredos/00-MAPA.md) | `secrets.toml` e o que não versionar |
| [`optimistic-locking`](../optimistic-locking/00-MAPA.md) | concorrência de escrita ([21](21-backend-dados-e-conexoes.md)) |
| [`testes-automatizados`](../testes-automatizados/00-MAPA.md) | a base da pirâmide do [30](30-testes.md) |
| [`estatistica-descritiva`](../estatistica-descritiva/00-MAPA.md) | o que os KPIs significam |
| [`power-bi`](../power-bi/00-MAPA.md) | a alternativa de BI do [31](31-quando-nao-usar-streamlit.md) |
| [`apis`](../apis/00-MAPA.md) | quando o backend é uma API |
| [`agentes-de-ia`](../agentes-de-ia/00-MAPA.md) | as interfaces de chat do [27](27-tempo-real-e-streaming.md) |
| [`engenharia-de-prompt`](../engenharia-de-prompt/00-MAPA.md) | idem |

---

## 10. Como este curso foi verificado

Para que você possa reproduzir ou desconfiar:

| O quê | Como |
|---|---|
| Versões e dependências | `importlib.metadata` sobre o pacote 1.63.0 instalado |
| Assinaturas de API | `inspect.signature` sobre a instalação |
| Opções de configuração | `streamlit.config._config_options`, enumeradas |
| Endpoints do servidor | `curl` contra um servidor 1.63.0 local |
| Comportamento do `AppTest` | scripts de teste executados, incluindo o defeito do `date_input` |
| Projeto-modelo | 43 testes executados; servidor levantado; banco populado |
| Paleta de cores | validador de daltonismo executado sobre a paleta original e a corrigida |
| Preços, cursos, livros | busca na web em 02/09/2026, com as fontes listadas em cada arquivo |

**Ambiente de referência:** Ubuntu 22.04.5 LTS, x86-64, Python 3.10.12,
Streamlit 1.63.0, pandas 2.3.3, plotly 7.0.0, uv 0.12.7.

---

## Autoteste

1. Qual é a fonte mais confiável sobre a API da **sua** versão, e como consultá-la?
2. Em que arquivo do código-fonte mora o cálculo de identidade de widget?
3. Onde está o protocolo inteiro, em um arquivo?
4. Que especificação `st.login()` implementa?
5. Qual PEP explica o `externally-managed-environment` da instalação?
6. Qual assunto deste repositório trata da concorrência de escrita?
