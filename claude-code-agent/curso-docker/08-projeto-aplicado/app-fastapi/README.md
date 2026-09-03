# Catálogo de Mídias — projeto modelo do curso

API FastAPI + SQLAlchemy async, pequena mas **inteira**: configuração por
ambiente, tratamento de erro, healthcheck honesto, testes e container
endurecido. É o projeto de referência do
[módulo 08](../dockerfile-fastapi-sqlalchemy.md).

## Pré-requisitos

| Item | Versão | Obrigatório? |
|---|---|---|
| Docker Engine | 20.10+ (testado com CLI 29.1.3) | para o caminho com container |
| Docker Compose | v2+ (testado com v5.5.0) | para subir API + Postgres |
| Python | 3.10+ (imagem usa 3.12) | só para o caminho sem container |

## Rodar com Docker (recomendado)

```bash
docker compose up --build
```

Sobe a API em `http://localhost:8000` e um Postgres. O `compose.override.yaml`
é lido automaticamente e liga o hot-reload.

Validar:

```bash
curl -s http://localhost:8000/health
# {"status":"ok","database":"ok","version":"dev"}

curl -s -X POST http://localhost:8000/media \
  -H 'Content-Type: application/json' -d '{"titulo":"Duna","ano":2021}'
# {"titulo":"Duna","ano":2021,"id":1}

docker compose exec api id     # uid=10001 -> não é root
docker compose ps              # STATUS deve mostrar (healthy)
```

Derrubar:

```bash
docker compose down      # mantém os dados no volume
docker compose down -v   # APAGA o volume junto — cuidado
```

Só a API, com SQLite e sem Postgres:

```bash
docker build -t catalogo-api:dev .
docker run --rm -p 8000:8000 catalogo-api:dev
```

## Rodar sem Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Testes:

```bash
pytest -q
# esperado: 4 passed
```

## Estrutura e o que cada decisão ensina

| Arquivo | Decisão de projeto | O que ela ensina |
|---|---|---|
| `app/config.py` | config só por variável de ambiente | 12-factor; é o que o `environment:` do compose alimenta |
| `app/db.py` | `pool_pre_ping=True` | conexão do pool vira zumbi quando o container do banco reinicia |
| `app/db.py` | `expire_on_commit=False` | sem isso, ler atributo após commit dispara SELECT e quebra em async |
| `app/main.py` | `/health` roda `SELECT 1` | healthcheck que não testa dependência mente |
| `app/main.py` | log em stdout | em container, log é stream capturado pelo Docker — nunca arquivo |
| `app/main.py` | `lifespan` | substitui o `@app.on_event` depreciado |
| `healthcheck.py` | `ProxyHandler({})` | `HTTP_PROXY` no ambiente quebra healthcheck em localhost |
| `Dockerfile` | multi-stage | `gcc` existe no build, não na imagem final |
| `Dockerfile` | `COPY requirements.txt` antes do código | preserva o cache do `pip install` |
| `Dockerfile` | `USER 10001:10001` | numérico para o Kubernetes provar `runAsNonRoot` |
| `.dockerignore` | ignora `.env` e `.git` | build rápido e segredo fora da imagem |
| `tests/conftest.py` | env antes do import, sem `reload` | config é lida uma vez, na importação |

## Variáveis de ambiente

| Variável | Padrão | Para que serve |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/app.db` | destino do banco |
| `APP_ENV` | `development` | ambiente em execução |
| `APP_VERSION` | `dev` | build reportado pelo `/health` |

Copie `.env.example` para `.env` para desenvolvimento local fora de container.
O `.env` está no `.gitignore` e no `.dockerignore` — não commite, não empacote.

## Endpoints

| Método | Rota | Resposta |
|---|---|---|
| GET | `/health` | 200 se o banco responde; 503 se não |
| GET | `/media` | lista |
| POST | `/media` | 201; 422 se o payload for inválido |
| GET | `/media/{id}` | 200 ou 404 |
| GET | `/docs` | Swagger UI (gerado pelo FastAPI) |

## Limites conhecidos

`init_db()` usa `create_all`: cria tabela ausente, mas **não** altera coluna
existente. Para evoluir schema em produção, use Alembic. Ver a seção 8 do
[módulo 08](../dockerfile-fastapi-sqlalchemy.md).
