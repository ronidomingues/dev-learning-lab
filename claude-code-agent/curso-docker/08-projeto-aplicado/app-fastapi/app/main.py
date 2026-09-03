"""API FastAPI mínima porém completa, pronta para container.

O que este arquivo demonstra que tutoriais costumam omitir:
  - /health que realmente testa a dependência (o banco), não devolve 200 fixo
  - lifespan (startup/shutdown) em vez do @app.on_event depreciado
  - tratamento de erro que não vaza stacktrace para o cliente
"""
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session, init_db
from app.models import Media

# Log em stdout: em container, log é stream, não arquivo. O Docker captura
# stdout/stderr e entrega em `docker logs`. Escrever em arquivo dentro do
# container é o erro nº 1 de observabilidade.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    log.info("subindo aplicacao env=%s versao=%s", settings.app_env, settings.app_version)
    # Para SQLite garantimos que a pasta do arquivo existe (é um volume no compose).
    if settings.database_url.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
    await init_db()
    log.info("schema pronto")
    yield
    # shutdown
    log.info("encerrando aplicacao")


app = FastAPI(title="Catálogo de Mídias", version=settings.app_version, lifespan=lifespan)


class MediaIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    ano: int = Field(ge=1888, le=2200)  # 1888 = filme mais antigo preservado


class MediaOut(MediaIn):
    id: int

    model_config = {"from_attributes": True}


@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    """Healthcheck com verdade.

    Um /health que só devolve {"status":"ok"} mente: o container fica
    "healthy" com o banco fora do ar. Aqui a gente executa um SELECT 1.
    """
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        log.error("healthcheck falhou: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "unreachable"},
        )
    return {"status": "ok", "database": "ok", "version": settings.app_version}


@app.get("/media", response_model=list[MediaOut])
async def listar(session: AsyncSession = Depends(get_session)):
    resultado = await session.execute(select(Media).order_by(Media.id))
    return list(resultado.scalars().all())


@app.post("/media", response_model=MediaOut, status_code=status.HTTP_201_CREATED)
async def criar(payload: MediaIn, session: AsyncSession = Depends(get_session)):
    item = Media(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    log.info("media criada id=%s titulo=%s", item.id, item.titulo)
    return item


@app.get("/media/{media_id}", response_model=MediaOut)
async def obter(media_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(Media, media_id)
    if item is None:
        raise HTTPException(status_code=404, detail="mídia não encontrada")
    return item
