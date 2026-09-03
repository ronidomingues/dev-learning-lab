# Painel Comercial — projeto-modelo

> **Nível:** intermediário · **Verificado em:** 02/09/2026, Ubuntu 22.04.5,
> Python 3.10.12, Streamlit 1.63.0, pandas 2.3.3, plotly 7.0.0.

Uma aplicação **pequena mas inteira**. Ela existe para responder às duas perguntas
que originaram este curso:

1. **Como se faz um dashboard profissional?** → `paginas/painel.py`, `ui/componentes.py`,
   `.streamlit/config.toml`.
2. **Como se faz um site funcional com backend?** → `nucleo/` (banco, migração,
   autenticação, regras), `paginas/pedidos.py` (CRUD completo), `paginas/admin.py`
   (importação, auditoria), `testes/`.

Não é um tutorial de "hello world" e não é um sistema de verdade. É o menor
programa que ainda tem tudo que um sistema de verdade tem: camadas separadas,
migração de banco, autenticação com papéis, validação, transação, cache com
invalidação, auditoria, testes, contêiner e verificação de saúde.

---

## Como rodar

### Caminho recomendado (uv — mais rápido)

```bash
cd 07-projeto-modelo
uv venv                      # cria .venv com o Python disponível
uv pip install -r requirements.txt
uv run streamlit run app.py
```

### Caminho universal (venv + pip)

```bash
cd 07-projeto-modelo
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Abra <http://localhost:8501>. Na primeira execução a app cria o banco em
`dados/painel.db` e o popula com 4.000 pedidos fictícios (leva ~1 segundo).

### Contas de demonstração

| E-mail | Senha | Papel | O que pode fazer |
|---|---|---|---|
| `admin@exemplo.com` | `admin123` | admin | tudo, inclusive importar e ver auditoria |
| `analista@exemplo.com` | `analista123` | analista | ler e escrever pedidos/clientes |
| `leitor@exemplo.com` | `leitor123` | leitor | só ler |

Senhas fracas de propósito: é uma demonstração local com dados inventados.

### Rodar os testes

```bash
python -m pytest testes/ -q
# esperado: 43 passed
```

### Rodar em contêiner

```bash
docker compose up --build
# http://localhost:8501 ; o banco fica no volume `painel-dados`
```

---

## Estrutura de pastas, comentada

```
07-projeto-modelo/
├── app.py                    # entrada: config da página, login, navegação. E MAIS NADA.
│
├── nucleo/                   # ── O "BACKEND" ── nenhum arquivo aqui importa streamlit
│   ├── config.py             #   configuração lida do ambiente e VALIDADA na partida
│   ├── db.py                 #   conexão, PRAGMAs, transação, migração versionada
│   ├── modelos.py            #   dataclasses do domínio (Usuario, Pedido, KPIs...)
│   ├── repositorio.py        #   o ÚNICO lugar com SQL; tudo parametrizado
│   ├── servicos.py           #   regras de negócio e agregações (pandas)
│   ├── auth.py               #   PBKDF2, comparação em tempo constante, papéis
│   └── seed.py               #   dados de demonstração determinísticos
│
├── ui/                       # ── APRESENTAÇÃO ── pode importar streamlit
│   ├── formatos.py           #   R$ 1.234,56 sem depender de locale do sistema
│   └── componentes.py        #   KPI, gráficos com layout único, tabela formatada
│
├── paginas/                  # ── AS TELAS ──
│   ├── _comum.py             #   cache, filtros da barra lateral, guarda de permissão
│   ├── painel.py             #   dashboard executivo
│   ├── exploracao.py         #   análise livre (tabela dinâmica, dispersão, fragment)
│   ├── pedidos.py            #   CRUD completo com diálogo, validação e auditoria
│   ├── clientes.py           #   edição em lote com st.data_editor
│   └── admin.py              #   importação de CSV, auditoria, diagnóstico
│
├── testes/
│   ├── conftest.py           #   fixtures: banco temporário por teste
│   ├── test_servicos.py      #   27 testes do núcleo — sem UI, milissegundos
│   └── test_app.py           #   16 testes da interface com AppTest — sem navegador
│
├── .streamlit/
│   ├── config.toml           #   tema e servidor (VERSIONADO)
│   └── secrets.toml.exemplo  #   modelo de segredos (o secrets.toml real NÃO se versiona)
│
├── Dockerfile · compose.yaml · requirements.txt · pyproject.toml
└── dados/                    #   banco SQLite (ignorado pelo Git)
```

---

## O que cada decisão de projeto ensina

| Decisão | Onde | O que ensina |
|---|---|---|
| `nucleo/` não importa `streamlit` | todo o pacote | Testar a regra de negócio sem subir servidor. Reaproveitar o mesmo código numa API ou num job. É a decisão mais importante do projeto. |
| Dinheiro em centavos, `int` | `db.py`, `servicos.py` | `float` não representa 0,1. Somar 4.000 pedidos em float erra centavos, e centavo errado em relatório financeiro vira reunião. |
| Migração versionada | `db.py:MIGRACOES` | O esquema evolui em passos numerados e idempotentes. Sem isso, "roda esse SQL no banco de produção" vira o processo de deploy. |
| `PRAGMA foreign_keys = ON` | `db.py` | SQLite ignora chave estrangeira por padrão. Há um teste que prova que o PRAGMA pegou. |
| SQL só no repositório, sempre parametrizado | `repositorio.py` | Injeção de SQL é o buraco nº 1 de app de dados. Há um teste que injeta `'; DROP TABLE pedidos; --`. |
| Lista branca para nome de coluna | `repositorio.py` | Valor pode ser parâmetro ligado; **nome de coluna não pode**. Aí a defesa é lista fixa. |
| Validação no serviço, não no formulário | `servicos.validar_pedido` | A mesma regra vale para o formulário, para a importação de CSV e para a API. Validar na tela é validar num lugar só. |
| `st.cache_resource` para o banco, `st.cache_data` para consultas | `app.py`, `_comum.py` | Recurso é compartilhado e não se serializa; dado é por chave de argumentos e se serializa. Trocar os dois é o erro de cache mais comum. |
| `ttl=300` no cache de consulta | `_comum.py` | Cache sem TTL em painel operacional é a causa nº 1 de "o número está errado" — está velho. |
| `invalidar_cache_de_pedidos()` depois de gravar | `pedidos.py` | Depois do INSERT o cache mente. Limpar só o que ficou velho, não tudo. |
| `bind="query-params"` nos filtros | `_comum.py` | A URL carrega o estado: o usuário compartilha o painel **já filtrado**. |
| `@st.fragment` na dispersão | `exploracao.py` | O rerun para na fronteira da função. Mexer no controle não refaz a consulta. |
| Guarda `exigir(("admin",))` no topo da página | `_comum.py`, `admin.py` | Esconder o botão não é controle de acesso. A página tem de parar (`st.stop()`). |
| `st.dialog` para criar e para excluir | `pedidos.py` | Ação destrutiva nunca acontece em um clique só. |
| Auditoria de toda escrita | `repositorio.registrar_auditoria` | "Quem mudou esse pedido?" é a primeira pergunta quando algo dá errado. |
| Importação tudo-ou-nada | `admin.py` | Importação parcial é pior que importação falha: você não sabe onde parou. |
| Estado vazio tratado em cada bloco | `componentes.py`, `servicos._vazio()` | "Sem dados" é um estado normal, não uma exceção. É o caminho que mais derruba painel. |
| Paleta **validada**, não escolhida por gosto | `ui/componentes.py` | A primeira versão usava vermelho e verde vizinhos: ΔE 1,4 em deuteranopia — a **mesma cor** para ~8% dos homens. A correção e a medição estão em [17](../17-graficos-e-visualizacao.md) §4. |
| Dispersão com `symbol=` além de `color=` | `paginas/exploracao.py` | Numa dispersão todos os pares de séries aparecem juntos; nenhuma paleta de 5 cores os separa. A forma do marcador é o segundo canal. |
| Paleta declarada no **tema** | `.streamlit/config.toml` | `chartCategoricalColors` (≥ 1.54) faz gráficos nativos e Plotly com `theme="streamlit"` herdarem as mesmas cores, sem repetir a lista. |
| `HEALTHCHECK` em `/_stcore/health` | `Dockerfile` | O orquestrador precisa de sinal melhor que "o processo está vivo". |
| `--server.address=0.0.0.0` | `Dockerfile` | Em contêiner, o padrão escuta só no localhost interno e a porta publicada não chega em ninguém. |
| Volume para `dados/` | `compose.yaml` | Sem volume, cada deploy apaga o banco. |

---

## O que este projeto **não** faz (e o que fazer em produção)

Honestidade é parte do material. Ele **não** tem:

- **Sessão persistente.** `st.session_state` mora na memória do servidor: fechou a
  aba, acabou; reiniciou o processo, todo mundo caiu. Em produção use
  `st.login()` com OIDC ([22-autenticacao-e-autorizacao](../22-autenticacao-e-autorizacao.md)).
- **Bloqueio por tentativa, redefinição de senha, 2FA.** Ver `nucleo/auth.py`,
  que diz isso no próprio docstring.
- **Banco de verdade.** SQLite é ótimo até ~centenas de escritas por segundo e
  um único processo. Vários trabalhadores escrevendo no mesmo arquivo em rede é
  receita de corrupção. Ver [21-backend-dados-e-conexoes](../21-backend-dados-e-conexoes.md).
- **HTTPS.** É trabalho do proxy reverso. Ver [28-deploy-e-operacao](../28-deploy-e-operacao.md).
- **Concorrência de escrita.** Dois usuários editando o mesmo pedido: o último
  grava por cima. A solução é *optimistic locking* — que este repositório
  cobre em [`optimistic-locking`](../../optimistic-locking/00-MAPA.md).

---

## Exercícios sobre o projeto

1. Acrescente a coluna `desconto_percentual` em `pedidos` — **como migração nº 3**,
   sem editar a migração nº 1. Rode os testes.
2. Faça o painel mostrar a **meta do mês** e o percentual atingido, com a meta
   vindo de uma tabela nova.
3. Transforme a linha de KPIs em `@st.fragment(run_every="30s")` e veja o número
   atualizar sozinho sem recarregar a página.
4. Troque o SQLite por PostgreSQL usando `st.connection("sql")`. Quantos arquivos
   você precisou tocar? (Resposta desejada: dois — `db.py` e `repositorio.py`.)
5. Escreva um teste que prove que um `analista` **não** consegue importar CSV.
6. Meça: quanto tempo leva o painel com `ttl=300` e sem cache nenhum? Use
   `show_time=True` em `st.cache_data` para ver na tela.
