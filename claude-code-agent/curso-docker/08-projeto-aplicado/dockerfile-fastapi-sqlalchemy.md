# Dockerfile real para FastAPI + SQLAlchemy async

> **Nível:** intermediário → avançado
> **Última verificação:** 18/08/2026
> **Projeto executável:** [`app-fastapi/`](app-fastapi/) — o código deste módulo existe de verdade na pasta ao lado.

Este é o módulo âncora do curso. Tudo que aparece aqui foi escrito, validado e
corrigido em cima de execução real — inclusive dois bugs que só apareceram
porque o código rodou. Eles estão documentados abaixo, com sintoma e causa raiz,
porque errar do mesmo jeito é o caminho mais rápido para aprender.

---

## 1. O problema antes da solução

Você tem uma API FastAPI que fala com Postgres via SQLAlchemy async. Ela roda
na sua máquina. Agora precisa rodar no servidor. As perguntas que o Docker
responde, nesta ordem:

1. **Como levar as dependências junto?** Não adianta mandar o `.py`: o servidor
   precisa do Python certo, do `asyncpg` compilado, da libpq.
2. **Como não mandar o compilador junto?** `asyncpg` tem extensão em C. Para
   *instalar* ele você precisa de `gcc`. Para *rodar*, não. Mandar o `gcc` para
   produção é ~300 MB de superfície de ataque a troco de nada.
3. **Como não rodar como root?** Por padrão, o processo dentro do container é
   root. Se sua API tiver uma falha de path traversal, o atacante é root no
   container — e a distância entre root no container e root no host é menor do
   que se imagina.
4. **Como o orquestrador sabe que a aplicação está viva?** "O processo está de
   pé" não é a mesma coisa que "a aplicação responde". Precisa de healthcheck.

Os quatro pontos acima são exatamente o que este Dockerfile resolve.

---

## 2. Anatomia do projeto

```
app-fastapi/
├── app/
│   ├── config.py        # settings via variáveis de ambiente (12-factor)
│   ├── db.py            # engine async, sessão, criação de schema
│   ├── models.py        # modelo ORM (SQLAlchemy 2.0, estilo Mapped[])
│   └── main.py          # rotas, lifespan, /health honesto
├── tests/
│   ├── conftest.py      # onde mora a lição sobre ordem de import
│   └── test_api.py      # 4 testes de fumaça
├── healthcheck.py       # healthcheck sem curl
├── Dockerfile           # multi-stage, não-root
├── compose.yaml         # api + postgres
├── compose.override.yaml# hot-reload de desenvolvimento
├── .dockerignore
└── requirements.txt     # versões fixadas
```

---

## 3. O Dockerfile, explicado linha a linha

### 3.1 Por que dois estágios

```dockerfile
FROM python:3.12-slim-trixie AS builder
...
FROM python:3.12-slim-trixie AS runtime
COPY --from=builder /opt/venv /opt/venv
```

O estágio `builder` instala `build-essential` (≈ 300 MB com dependências),
cria um virtualenv em `/opt/venv` e compila tudo dentro dele. O estágio
`runtime` começa **do zero** de uma imagem limpa e copia **só** a pasta
`/opt/venv`. O `gcc` nunca chega na imagem final — ele existiu apenas durante
o build, num estágio que é descartado.

A pergunta que fecha o raciocínio: *por que copiar um venv funciona?* Porque um
virtualenv é só um diretório com os pacotes e um `bin/`. Não há registro global
no sistema. Copiar a pasta e colocar `/opt/venv/bin` no `PATH` é uma instalação
completa. É o que torna o truque possível.

### 3.2 A ordem das instruções é o que decide o tempo de build

```dockerfile
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# ... só DEPOIS o código:
COPY --chown=appuser:appgroup app/ ./app/
```

O Docker guarda cache por camada. Uma camada é reaproveitada se a instrução e
os arquivos que ela toca não mudaram. Como o `requirements.txt` muda raramente
e o código muda o tempo todo, copiar as dependências **sozinhas e antes** faz o
`pip install` ser reaproveitado em quase todo build.

Inverta a ordem — `COPY . .` antes do `pip install` — e cada `print()` novo
invalida a camada de instalação, reinstalando tudo. Na prática, é a diferença
entre um build de ~2 s e um de ~90 s, repetida dezenas de vezes por dia.
Detalhes completos em [cache de camadas](../02-dockerfile/cache-de-camadas.md).

### 3.3 Usuário não-root, com UID numérico

```dockerfile
RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser
...
USER 10001:10001
```

Três decisões, cada uma com motivo:

| Decisão | Por quê |
|---|---|
| `--system` | conta de serviço: sem senha, sem shell de login, fora da faixa de UID de humanos |
| `--uid 10001` fixo | permissões de volume ficam previsíveis entre máquinas; UID sorteado muda e quebra o acesso ao volume |
| `USER 10001:10001` numérico | o Kubernetes precisa avaliar `runAsNonRoot` **sem** abrir a imagem para ler o `/etc/passwd`. Com nome, ele não consegue provar que não é root e recusa o pod |

O linter `hadolint` cobra exatamente isso na regra **DL3066** — e cobrou de mim
durante a escrita (a saída real está na seção 6).

### 3.4 Healthcheck que diz a verdade

O endpoint não devolve `{"status":"ok"}` fixo. Ele executa um `SELECT 1`:

```python
@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "degraded", ...})
    return {"status": "ok", "database": "ok", ...}
```

Um `/health` que devolve 200 sem checar nada é pior que não ter healthcheck:
ele afirma que está tudo bem enquanto o banco está fora, e o orquestrador
manda tráfego para um container quebrado.

E o `HEALTHCHECK` do Dockerfile não usa `curl`:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]
```

Porque `python:slim` **não tem curl**. Instalar curl só para o healthcheck
adiciona pacote e CVEs à imagem final. A imagem já tem Python.

O `--start-period=10s` merece atenção: durante esse período inicial, falhas
**não contam** para o `retries`. Sem ele, uma aplicação que leva 8 s para subir
é marcada `unhealthy` e reiniciada em loop, para sempre.

### 3.5 `CMD` em forma exec, e por que isso não é frescura

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Na forma *shell* (`CMD uvicorn app.main:app`), o Docker roda
`/bin/sh -c "uvicorn ..."`. O PID 1 vira o `sh`, e o `sh` **não repassa
SIGTERM** para o filho. Resultado: `docker stop` não é obedecido, o Docker
espera 10 s e mata com SIGKILL. Conexões abertas caem no meio, transações não
fazem rollback limpo.

Na forma *exec* (array JSON), o uvicorn é o PID 1 e recebe o SIGTERM
diretamente, fazendo shutdown gracioso.

E `--host 0.0.0.0`, não `127.0.0.1`: dentro do container, `127.0.0.1` só aceita
conexão de dentro do próprio container. O `-p 8000:8000` nunca alcançaria.
É o erro nº 1 de quem containeriza uma API pela primeira vez.

---

## 4. O `.dockerignore` não é opcional

Sem ele, o `docker build` empacota o diretório inteiro — incluindo `.git`,
`.venv` e caches — e manda para o daemon. Três consequências: build lento,
cache invalidado a cada commit (porque `.git/` muda), e o risco sério de um
`COPY . .` levar seu `.env` com senha para dentro da imagem, onde qualquer um
com a imagem lê com `docker history`.

As linhas que mais importam:

```
.git
.venv
.env
.env.*
!.env.example
data/
```

---

## 5. Como rodar (com Docker disponível)

```bash
cd 08-projeto-aplicado/app-fastapi

# Build da imagem
docker build -t catalogo-api:dev .

# Subir API + Postgres
docker compose up --build

# Em outro terminal — validar:
curl -s http://localhost:8000/health
# esperado: {"status":"ok","database":"ok","version":"dev"}

curl -s -X POST http://localhost:8000/media \
  -H 'Content-Type: application/json' \
  -d '{"titulo":"Duna","ano":2021}'
# esperado: {"titulo":"Duna","ano":2021,"id":1}

# Conferir que o processo NÃO é root:
docker compose exec api id
# esperado: uid=10001 gid=10001

# Conferir o healthcheck:
docker compose ps
# a coluna STATUS deve mostrar (healthy)
```

Rodar sem Postgres, só com SQLite:

```bash
docker build -t catalogo-api:dev .
docker run --rm -p 8000:8000 catalogo-api:dev
```

---

## 6. Verificação real executada — o que foi testado e como

**Contexto honesto:** na máquina onde este curso foi escrito o daemon do Docker
não estava acessível (socket `root:docker`, usuário fora do grupo, `sudo` com
senha). Então a validação foi feita em duas frentes, e é importante você saber
exatamente o que foi e o que não foi provado.

### ✅ Validado por execução real

**1. Dependências resolvem nas versões fixadas**

```bash
pip install -r requirements-dev.txt
python -c "import fastapi,sqlalchemy;print(fastapi.__version__, sqlalchemy.__version__)"
# saída obtida: 0.141.1 2.0.52
```

**2. Suíte de testes**

```bash
python -m pytest -q
# saída obtida: 4 passed in 0.66s
```

**3. A aplicação sobe e responde — com o mesmo comando do `CMD`**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

curl -s -w "\nHTTP %{http_code}\n" http://127.0.0.1:8000/health
# saída obtida: {"status":"ok","database":"ok","version":"dev"}
#               HTTP 200

curl -s -X POST http://127.0.0.1:8000/media \
  -H 'Content-Type: application/json' -d '{"titulo":"Duna","ano":2021}'
# saída obtida: {"titulo":"Duna","ano":2021,"id":1}   HTTP 201
```

**4. O healthcheck nos dois estados**

```bash
python healthcheck.py   # com o app no ar  -> exit=0  (healthy)
python healthcheck.py   # com o app parado -> exit=1  (unhealthy)
```

**5. Dockerfile auditado pelo `hadolint` 2.15.1**

```bash
hadolint Dockerfile
# saída final obtida: (vazio) — zero avisos
```

**6. Compose validado pelo schema oficial (Compose v5.5.0)**

```bash
docker compose config --quiet                  # base + override -> OK
docker compose -f compose.yaml config --quiet  # só produção      -> OK
```

**7. Tags de imagem base conferidas na API do Docker Hub**

`python:3.12-slim-trixie`, `postgres:17-alpine` — existência, data de
atualização e tamanho confirmados em 18/08/2026.

### ❌ NÃO validado

- `docker build` de fato (o daemon estava inacessível);
- `docker run` / `docker compose up` de fato;
- portanto: tamanho final da imagem, tempo de build e o `(healthy)` do
  `docker compose ps` são **expectativas fundamentadas, não medições**.

Quando você tiver acesso ao daemon, rode a seção 5 e confira. Se algo divergir,
o que está escrito aqui é o que deve ser corrigido.

---

## 7. Erros que você provavelmente vai cometer

Estes dois não são hipotéticos — **aconteceram** durante a escrita deste módulo.

### Bug real nº 1 — `no such table: media`

**Sintoma.** Dois testes falharam:

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: media
FAILED tests/test_api.py::test_criar_e_listar
FAILED tests/test_api.py::test_404_em_id_inexistente
```

Curioso: `test_health_ok` **passou** — porque `SELECT 1` não precisa de tabela.

**Causa raiz.** A primeira versão do teste usava `importlib.reload()` para
recarregar os módulos depois de mudar `DATABASE_URL`. Só que
`reload(app.db)` cria um objeto `Base` **novo**, enquanto `app.models` continua
apontando para o `Base` **antigo**. O `create_all` rodou sobre um metadata
vazio: nenhuma tabela foi criada.

**Correção.** Eliminar o `reload`. A variável de ambiente é definida no
`tests/conftest.py`, que o pytest carrega **antes** de importar qualquer
`app.*`. Sem malabarismo, sem estado duplicado.

**A lição que vale para Docker:** configuração é lida **uma vez**, na
importação. É por isso que a configuração precisa vir do ambiente antes do
processo começar — e é exatamente isso que o `environment:` do compose faz.

### Bug real nº 2 — container `unhealthy` com a aplicação no ar

**Sintoma.** `curl http://127.0.0.1:8000/health` devolvia **200**, mas o
`healthcheck.py` no mesmo endereço saía com **exit 1**.

```
urllib.error.HTTPError: HTTP Error 502: cannotconnect
```

**Causa raiz.** A máquina tinha `HTTP_PROXY` definido e o `no_proxy` estava
escrito com **espaço depois da vírgula**:

```
no_proxy=localhost, 127.0.0.0/8, ::1
```

O `curl` tolera o espaço e faz o bypass. O `urllib` do Python **não** — ele não
casa a entrada `" 127.0.0.0/8"` com espaço à esquerda, conclui que precisa de
proxy, e manda uma requisição para `127.0.0.1` através do proxy corporativo,
que responde 502.

**Correção.** Um opener imune a variáveis de ambiente:

```python
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
```

**Por que isso importa muito em Docker:** este é o retrato do bug que consome um
dia inteiro. O container é marcado `unhealthy`, o orquestrador o reinicia em
loop, e todo teste manual que você faz com `curl` diz que está tudo bem.
Chamada a `localhost` **nunca** deve passar por proxy. Se sua empresa injeta
`HTTP_PROXY` nas imagens, garanta `no_proxy` **sem espaços** e prefira clientes
que ignoram proxy explicitamente em healthchecks.

### Bug real nº 3 — o pino de versão que quebraria o seu build

Não chegou a rodar porque foi pego na conferência, mas ia quebrar.

A primeira versão do Dockerfile trazia:

```dockerfile
FROM python:3.12-slim
RUN apt-get install -y build-essential=12.9
```

`12.9` é a versão do `build-essential` no Debian **bookworm**. Conferindo os
digests na API do Docker Hub:

```
python:3.12-slim         -> sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a
python:3.12-slim-trixie  -> sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a   ← idêntico
python:3.12-slim-bookworm-> sha256:a116514e19457bcb7af7efe9c3dd0b9b71e85b317694e7882a1c52aa15a78134
```

A tag `3.12-slim` **já aponta para trixie**, onde o `build-essential` é
**12.12**. O pino `=12.9` falharia com `Version '12.9' for 'build-essential'
was not found`.

**Duas lições.** Primeira: tag de suite implícita muda debaixo de você — fixe
`python:3.12-slim-trixie`, não `python:3.12-slim`. Segunda: pinar versão de
pacote apt em estágio de build é frequentemente contraprodutivo, porque o
Debian remove o `.deb` antigo do mirror ao publicar correção de segurança e o
build passa a falhar com 404. A reprodutibilidade que importa vem da tag de
suite fixa e do `requirements.txt` pinado.

### Outros quatro que você vai encontrar

| Erro no terminal | Causa raiz | Correção |
|---|---|---|
| `Connection refused` ao acessar a porta publicada | uvicorn subiu em `127.0.0.1` dentro do container | `--host 0.0.0.0` |
| `sqlalchemy.exc.MissingGreenlet` | `greenlet` ausente, ou atributo acessado após commit | instalar `greenlet`; usar `expire_on_commit=False` |
| `unable to open database file` (SQLite) | pasta `data/` não existe ou pertence a root, e o processo é UID 10001 | `mkdir -p /app/data && chown appuser:appgroup /app/data` **antes** do `USER` |
| `could not translate host name "db"` | container fora da rede do compose, ou nome do serviço diferente | usar o nome do serviço como host; ver [DNS interno](../05-redes/dns-interno-entre-servicos.md) |

---

## 8. O que este Dockerfile ainda não faz (e quando você vai precisar)

Honestidade sobre limites — nenhum destes é necessário agora, mas todos
aparecem quando o projeto cresce:

- **Migrations.** O `init_db()` com `create_all` cria tabela que não existe,
  mas **não** altera coluna existente. No dia que você renomear um campo em
  produção, precisa de **Alembic**. `create_all` é para aprendizado e SQLite.
- **Um init como PID 1.** O uvicorn não faz *reaping* de processos zumbis. Se
  a aplicação passar a criar subprocessos, use `--init` no run (ou
  `init: true` no compose), que coloca o `tini` como PID 1.
- **Imagem distroless.** Dá para reduzir mais trocando o runtime por
  `gcr.io/distroless/python3`. Ganha-se superfície de ataque menor; perde-se
  shell — sem `docker exec ... bash` para depurar.
- **Pinagem por digest.** `FROM python:3.12-slim-trixie@sha256:2c941e86...`
  congela o byte exato. Máxima reprodutibilidade, ao custo de atualizar o
  digest na mão a cada correção de segurança.
- **Build multi-arquitetura.** Se o servidor do FlixARD for ARM (Raspberry Pi,
  por exemplo) e você builda no x86, precisa de `docker buildx build
  --platform linux/amd64,linux/arm64`.

---

## 9. Autoteste

1. Por que o `gcc` precisa existir no build mas não na imagem final — e que
   mecanismo do Dockerfile garante isso?
2. O que muda no tempo de build se você trocar a ordem entre `COPY requirements.txt`
   e `COPY app/`? Por quê?
3. Por que `USER 10001:10001` e não `USER appuser`?
4. Qual é o problema de um `/health` que devolve `{"status":"ok"}` fixo?
5. O que acontece com o `docker stop` se o `CMD` estiver na forma shell?
6. Por que `--host 0.0.0.0` e não `127.0.0.1`?
7. Um container está marcado `unhealthy`, mas `curl` de dentro dele responde
   200. Cite duas causas possíveis.
8. Por que pinar `build-essential=12.9` quebrou, e o que substituiu esse pino
   como garantia de reprodutibilidade?
9. Para que serve `--start-period` no `HEALTHCHECK`, e o que acontece sem ele?

---

**Próximos passos:** [compose do FlixARD](compose-flixard.md) ·
[compose do sistema financeiro](compose-sistema-financeiro.md) ·
[voltar ao índice](../00-indice.md)
