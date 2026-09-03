# 21 · O "backend": banco de dados, conexões e persistência

> **Nível:** intermediário a avançado · **Escrito em:** 02/09/2026 · Streamlit 1.63.0
> Primeiro arquivo da resposta a **"como faço um site funcional com backend?"**.
> Continua em [22-autenticação](22-autenticacao-e-autorizacao.md),
> [23-arquitetura](23-arquitetura-de-app-real.md) e
> [24-tarefas-longas](24-tarefas-longas-e-concorrencia.md).

---

## 1. O mal-entendido de partida

> "O Streamlit tem backend?"

Ele **é** o backend. `streamlit run` sobe um servidor Python (desde a 1.57,
Starlette sobre Uvicorn) que executa o seu código no servidor. Tudo que você
escreve roda lá — não no navegador.

O que ele **não** traz pronto:

| Um framework web traz | Streamlit traz? |
|---|---|
| rotas HTTP | não (tem páginas, não rotas REST) |
| ORM / camada de dados | **não** |
| migrações de esquema | **não** |
| autenticação e sessão persistente | parcial (`st.login`, OIDC) |
| validação de entrada | não (use você, ou Pydantic) |
| fila de tarefas | **não** |
| API para outros sistemas | não (mas ver `st.App`) |

Ou seja: **você tem o servidor; precisa escrever o backend.** Este arquivo é
sobre a parte de dados.

---

## 2. Escolher o banco

| Banco | Use quando | Não use quando |
|---|---|---|
| **SQLite** | app de um processo só, leitura predominante, ≤ ~100 mil escritas/dia, um servidor | vários processos ou réplicas escrevendo; disco de rede (NFS, EFS) |
| **PostgreSQL** | o padrão para qualquer coisa séria | você não quer administrar um banco |
| **DuckDB** | análise sobre Parquet/CSV, leitura pesada, sem escrita concorrente | escrita concorrente |
| **Parquet + pandas/polars** | dado que muda uma vez por dia (carga em lote) | quando o app precisa escrever |
| **Snowflake / BigQuery** | já é a fonte de verdade da empresa | volume pequeno (custo por consulta) |
| **API/HTTP de terceiro** | o dado é de outro sistema | quando você pode ler direto do banco |

**Sobre SQLite, com honestidade.** Ele é subestimado: o
[projeto-modelo](07-projeto-modelo/) usa SQLite com 4.000 pedidos e responde em
milissegundos. Ele aguenta muito mais do que a fama sugere — **desde que** seja um
processo só, no disco local, com `journal_mode=WAL`. Ele quebra quando: você roda
várias réplicas do app; o arquivo está num disco de rede (onde o travamento é
notoriamente não confiável); ou há escrita concorrente pesada.

---

## 3. `st.connection`: o jeito nativo

```python
conn = st.connection("vendas", type="sql")

df = conn.query(
    "SELECT * FROM pedidos WHERE data BETWEEN :i AND :f",
    params={"i": inicio, "f": fim},
    ttl="5m",                       # cache embutido
)
```

`secrets.toml`:

```toml
[connections.vendas]
url = "postgresql+psycopg://usuario:senha@host:5432/base"
# ou, por partes:
# dialect = "postgresql"
# driver = "psycopg"
# host = "..."; port = 5432; database = "..."; username = "..."; password = "..."
```

**O que `st.connection` faz por você:** cria a `Engine` do SQLAlchemy uma vez
(equivale a um `@st.cache_resource` bem-feito), gerencia o *pool* de conexões,
e embute cache com TTL no `query`.

**Escrita** — `query` é para leitura; para escrever, use a sessão:

```python
from sqlalchemy import text

with conn.session as s:
    s.execute(text("UPDATE pedidos SET status = :st WHERE id = :id"),
              {"st": "faturado", "id": 42})
    s.commit()
```

Tipos disponíveis na 1.63.0 (`streamlit.connections.__all__`):
`SQLConnection`, `SnowflakeConnection`, `SnowflakeCallersRightsConnection`, e as
classes-base `BaseConnection` / `ExperimentalBaseConnection` para você escrever a
sua.

**Quando NÃO usar `st.connection`:** quando você quer separar o backend do
Streamlit de verdade (ver [23](23-arquitetura-de-app-real.md)). Aí você escreve
um `nucleo/db.py` que não importa `streamlit`, e o app só chama funções. É o que o
projeto-modelo faz, e é o que eu recomendo para qualquer coisa que vá durar.

---

## 4. Conexão à mão, com `cache_resource`

```python
from sqlalchemy import create_engine, text
import pandas as pd
import streamlit as st

@st.cache_resource
def engine():
    return create_engine(
        st.secrets["banco"]["url"],
        pool_size=5,             # conexões mantidas abertas
        max_overflow=5,          # extras sob pico
        pool_pre_ping=True,      # testa antes de usar: mata conexão morta
        pool_recycle=1800,       # recicla a cada 30 min
    )

@st.cache_data(ttl=300)
def consultar(sql: str, params: tuple) -> pd.DataFrame:
    with engine().connect() as con:
        return pd.read_sql(text(sql), con, params=dict(params))
```

**`pool_pre_ping=True` é o parâmetro que resolve o bug mais chato de app de
dados**: "funciona de manhã, quebra à tarde". O banco (ou o firewall) derruba
conexões ociosas; sem o *pre-ping*, o app tenta usar uma conexão morta e devolve
um erro incompreensível.

**Dimensionar o pool:** `pool_size × número de processos do app` não pode passar do
`max_connections` do banco. Com 4 réplicas e `pool_size=10`, são 40 conexões — e o
PostgreSQL padrão aceita 100, contando tudo que mais existe.

---

## 5. Migrações: o esquema também é código

Sem migração versionada, o processo de deploy vira "alguém roda esse SQL no
banco". Isso funciona até o dia em que não funciona.

**Mínimo viável, sem dependência** (é o do projeto-modelo):

```python
MIGRACOES = [
    "CREATE TABLE clientes (...);",                       # versão 1
    "ALTER TABLE clientes ADD COLUMN obs TEXT DEFAULT '';" # versão 2
]

def migrar(caminho):
    with transacao(caminho) as con:
        con.execute("CREATE TABLE IF NOT EXISTS schema_versao (versao INTEGER)")
        atual = con.execute("SELECT MAX(versao) FROM schema_versao").fetchone()[0] or 0
        for numero, script in enumerate(MIGRACOES, start=1):
            if numero > atual:
                con.executescript(script)
                con.execute("INSERT INTO schema_versao VALUES (?)", (numero,))
```

**Duas regras que valem para qualquer ferramenta de migração:**

1. **Nunca edite uma migração já publicada.** Quem já a aplicou não a aplicará de
   novo. Acrescente outra.
2. **Migração precisa ser idempotente na prática**: rodar duas vezes não faz nada
   na segunda. O contador de versão garante isso.

**Para projeto sério, use Alembic** (do SQLAlchemy): gera migração comparando os
modelos com o banco, suporta *downgrade*, e integra com o SQLAlchemy que você já
tem.

**Onde chamar a migração:** na partida da app, dentro de um `@st.cache_resource`,
para rodar uma vez por processo:

```python
@st.cache_resource
def preparar():
    migrar(caminho)
    return config
```

> **Cuidado com réplicas.** Com N processos subindo ao mesmo tempo, N migrações
> disparam juntas. Em SQLite isso é resolvido pelo travamento do arquivo; em
> PostgreSQL, use um *advisory lock* ou — melhor — rode a migração num passo de
> deploy separado, antes de subir a app.

---

## 6. Transações: tudo ou nada

```python
from contextlib import contextmanager

@contextmanager
def transacao(caminho):
    con = conexao(caminho)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
```

Uso:

```python
with transacao(caminho) as con:
    con.execute("INSERT INTO pedidos ...")
    con.execute("UPDATE estoque SET qtd = qtd - ? ...")
    # se a segunda falhar, a primeira é desfeita
```

**Por que isso importa especialmente no Streamlit:** lembre do
[modelo de execução](12-modelo-de-execucao-e-rerun.md) — se o usuário interage
durante um rerun, o run em andamento é **abandonado no meio**. Sem transação, você
fica com meia gravação e nenhum registro de que isso aconteceu.

Regra prática: **escrita só por botão ou por submit de formulário**, e sempre em
transação. Escrita disparada por `slider` é pedir problema.

---

## 7. SQL sem injeção

```python
# NUNCA
sql = f"SELECT * FROM pedidos WHERE canal = '{canal}'"

# SEMPRE
con.execute("SELECT * FROM pedidos WHERE canal = ?", (canal,))
```

**Listas de valores** — gere os `?` a partir do tamanho, nunca do conteúdo:

```python
marcadores = ",".join("?" * len(canais))
con.execute(f"SELECT * FROM pedidos WHERE canal IN ({marcadores})", list(canais))
```

**Nome de coluna ou tabela não pode ser parâmetro ligado.** Aí a única defesa é
lista branca:

```python
PERMITIDAS = {"data", "valor", "cliente"}
if coluna not in PERMITIDAS:
    raise ValueError(f"coluna '{coluna}' não permitida")
sql = f"SELECT * FROM pedidos ORDER BY {coluna}"       # seguro: veio da lista
```

O [`nucleo/repositorio.py`](07-projeto-modelo/nucleo/repositorio.py) do
projeto-modelo faz as três coisas, e os testes incluem uma tentativa de injeção
com `'; DROP TABLE pedidos; --`.

---

## 8. Dinheiro, datas e fuso

**Dinheiro em inteiro, em centavos.** `float` não representa 0,1 em binário;
somar milhares de valores acumula erro. Guarde `valor_centavos INTEGER`, faça
toda conta em inteiro, e divida por 100 **só na hora de mostrar**.

```python
valor_centavos = int(round(preco_centavos * qtd * (1 - desconto)))
```

**Datas com fuso explícito.** Guarde em UTC (`datetime.now(timezone.utc)`),
converta para o fuso do usuário na exibição. O Streamlit ajuda:

```python
st.context.timezone           # ex.: "America/Sao_Paulo"
st.context.timezone_offset    # em minutos
```

Guardar hora local sem fuso é o que produz relatório com uma hora a mais em
outubro e a menos em fevereiro — em países que ainda praticam horário de verão.

---

## 9. Concorrência de escrita

Duas pessoas editam o mesmo registro. O que acontece por padrão: **a última
gravação vence**, silenciosamente, e a primeira pessoa nunca sabe que seu trabalho
foi perdido.

Isso não é problema de Streamlit — é problema de sistema com vários usuários. A
solução padrão é **bloqueio otimista**: cada registro tem uma versão; o `UPDATE`
inclui a versão que você leu; se não bater, ninguém atualiza e você avisa.

```sql
UPDATE pedidos SET quantidade = ?, versao = versao + 1
 WHERE id = ? AND versao = ?
```

```python
linhas = cur.rowcount
if linhas == 0:
    st.error("Alguém alterou este pedido enquanto você editava. "
             "Recarregue e tente de novo.", icon=":material/sync_problem:")
```

Este repositório tem um assunto inteiro sobre o tema, com as variantes e os
trade-offs: [`optimistic-locking`](../optimistic-locking/00-MAPA.md).

---

## 10. Falar com API em vez de banco

```python
import httpx
import streamlit as st

@st.cache_resource
def cliente() -> httpx.Client:
    return httpx.Client(
        base_url=st.secrets["api"]["url"],
        headers={"Authorization": f"Bearer {st.secrets['api']['token']}"},
        timeout=httpx.Timeout(10.0, connect=5.0),      # SEMPRE defina timeout
    )

@st.cache_data(ttl=300, show_spinner="Consultando a API...")
def buscar(rota: str, params: tuple) -> dict:
    r = cliente().get(rota, params=dict(params))
    r.raise_for_status()
    return r.json()
```

Três coisas que faltam em quase todo código de API que eu vejo em painel:

1. **timeout** — sem ele, uma API travada trava a sessão para sempre;
2. **`raise_for_status()`** — senão um 500 vira um `dict` vazio e o painel mostra
   zero como se fosse um número real;
3. **tratamento na tela** — `try/except httpx.HTTPError` com uma mensagem em
   português e `st.stop()`.

---

## 11. Arquivos: onde guardar o que o usuário envia

**Não guarde no disco do contêiner.** Ele é efêmero: no próximo deploy, some.

| Destino | Quando |
|---|---|
| memória (só processar e descartar) | o padrão; a maioria dos casos |
| volume persistente (Docker, PVC) | um servidor só, arquivos pequenos |
| S3 / GCS / Azure Blob | qualquer coisa séria |
| coluna `BLOB` no banco | arquivos pequenos (< 1 MB) e poucos |

```python
arquivo = st.file_uploader("Comprovante", type=["pdf", "png"])
if arquivo is not None:
    dados = arquivo.getvalue()          # bytes, em memória
    if len(dados) > 5 * 1024 * 1024:
        st.error("Arquivo maior que 5 MB.")
        st.stop()
    chave = f"comprovantes/{uuid4()}.pdf"
    s3.put_object(Bucket=..., Key=chave, Body=dados)
    repositorio.registrar_anexo(pedido_id, chave)
```

Mais em [26-arquivos-e-uploads.md](26-arquivos-e-uploads.md).

---

## 12. Checklist do backend

- [ ] Nenhum arquivo do `nucleo/` importa `streamlit`.
- [ ] Toda consulta usa parâmetro ligado; nome de coluna vem de lista branca.
- [ ] Toda escrita está em transação.
- [ ] Migrações versionadas e idempotentes.
- [ ] `pool_pre_ping=True` (ou `validate=` no `cache_resource`).
- [ ] Dinheiro em inteiro; datas em UTC.
- [ ] Cache invalidado depois de cada escrita.
- [ ] Toda chamada externa tem timeout e tratamento de erro.
- [ ] Concorrência de escrita: decidida conscientemente (mesmo que a decisão seja
      "aceitamos o último vence").
- [ ] Segredos fora do Git.

---

## Autoteste

1. O Streamlit "tem backend"? Liste três coisas de framework web que ele não traz.
2. Quando SQLite serve e quando não serve? Cite as três condições que o quebram.
3. O que `st.connection` faz por você, e quando é melhor não usá-lo?
4. Que problema `pool_pre_ping=True` resolve, e como ele se manifesta?
5. Por que nunca editar uma migração já publicada?
6. Por que transação importa **especialmente** no modelo de execução do Streamlit?
7. Como filtrar por uma lista de valores sem abrir brecha de injeção? E como
   ordenar por uma coluna escolhida pelo usuário?
8. Por que dinheiro em `float` é um erro? Qual é o padrão correto?
9. Duas pessoas editam o mesmo registro. O que acontece por padrão e qual é a
   solução?
10. Três coisas que faltam em quase todo código de chamada de API em painel.
