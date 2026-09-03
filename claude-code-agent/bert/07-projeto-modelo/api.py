"""Serve o classificador por HTTP.

Uso:
    uvicorn api:app --reload --port 8000

Depois:
    curl -X POST http://localhost:8000/prever \
         -H "Content-Type: application/json" \
         -d '{"texto": "não consigo emitir nota fiscal"}'

    curl http://localhost:8000/saude
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import config
from prever import carregar, prever


class Chamado(BaseModel):
    texto: str = Field(min_length=1, max_length=5000, examples=["minha fatura veio errada"])


class Resposta(BaseModel):
    categoria: str
    confianca: float
    probabilidades: dict[str, float]
    encaminhar_para_humano: bool
    latencia_ms: float


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Carrega o modelo na SUBIDA do serviço, não na primeira requisição.
    # Assim o primeiro usuário não paga os ~2 s de carregamento, e um erro de
    # instalação aparece no deploy — não em produção, para um cliente.
    carregar()
    yield


app = FastAPI(title="Triagem de chamados com BERT", version="1.0", lifespan=ciclo_de_vida)


@app.get("/saude")
def saude() -> dict:
    """Health check: usado por Kubernetes, load balancer e monitoração."""
    try:
        carregar()
        return {"status": "ok", "modelo": config.modelo_base, "limiar": config.limiar_confianca}
    except Exception as erro:  # noqa: BLE001 — aqui queremos capturar qualquer falha
        raise HTTPException(status_code=503, detail=f"modelo indisponível: {erro}") from erro


@app.post("/prever", response_model=Resposta)
def classificar(chamado: Chamado) -> Resposta:
    inicio = time.perf_counter()
    try:
        p = prever(chamado.texto)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    except FileNotFoundError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro

    return Resposta(
        categoria=p.categoria,
        confianca=round(p.confianca, 4),
        probabilidades=p.probabilidades,
        encaminhar_para_humano=p.encaminhar_para_humano,
        latencia_ms=round((time.perf_counter() - inicio) * 1000, 2),
    )
