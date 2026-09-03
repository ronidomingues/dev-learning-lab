"""Configuração dos testes.

LIÇÃO IMPORTANTE (custou um bug real durante a escrita deste curso):
o app lê DATABASE_URL no momento em que `app.config` é importado.
Portanto a variável precisa estar no ambiente ANTES de qualquer import
de `app.*`. Por isso o os.environ é mexido aqui no topo do conftest,
que o pytest carrega antes de coletar os testes.

A tentação é usar importlib.reload() para "recarregar com a env nova".
Não funcione: reload(app.db) cria um Base novo, mas app.models continua
apontando para o Base antigo. O create_all roda num metadata vazio e os
testes quebram com "no such table: media".
"""
import os
import tempfile
from pathlib import Path

_TMPDIR = tempfile.mkdtemp(prefix="curso-docker-")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{Path(_TMPDIR) / 'test.db'}"
os.environ["APP_ENV"] = "test"
os.environ["APP_VERSION"] = "test"

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402


@pytest.fixture
async def client():
    # Import tardio: só aqui, com a env já ajustada acima.
    from app.db import Base, engine
    from app.main import app

    # Cada teste começa com o schema limpo.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
