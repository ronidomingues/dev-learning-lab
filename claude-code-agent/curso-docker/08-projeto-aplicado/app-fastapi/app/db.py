"""Camada de banco: engine assíncrona, sessão e criação de schema.

SQLAlchemy 2.0 async. Os pontos que importam para Docker estão comentados.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base declarativa do SQLAlchemy 2.0 (substitui o antigo declarative_base())."""


# pool_pre_ping: antes de usar uma conexão do pool, o SQLAlchemy manda um
# "ping". Isso é ESSENCIAL em Docker: se o container do Postgres reiniciar,
# as conexões do pool viram zumbis e o app quebraria com "connection closed".
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

# expire_on_commit=False: sem isso, acessar um atributo do objeto depois do
# commit dispara um novo SELECT — que em código async explode com MissingGreenlet.
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependência do FastAPI: entrega uma sessão e garante o fechamento."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Cria as tabelas se não existirem.

    ATENÇÃO: isto é adequado para aprendizado e para SQLite. Em produção
    com Postgres, use Alembic (migrations versionadas). Ver o módulo 08.
    """
    from app import models  # noqa: F401 — registra os modelos no metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
