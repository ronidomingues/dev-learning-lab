"""Teste de fumaça: exercita o ciclo completo da API.

Roda sem Docker e sem banco externo (SQLite em arquivo temporário).
"""


async def test_health_ok(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["database"] == "ok"


async def test_criar_e_listar(client):
    r = await client.post("/media", json={"titulo": "Blade Runner", "ano": 1982})
    assert r.status_code == 201
    criado = r.json()
    assert criado["id"] > 0

    r = await client.get(f"/media/{criado['id']}")
    assert r.status_code == 200
    assert r.json()["titulo"] == "Blade Runner"

    r = await client.get("/media")
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_validacao_rejeita_ano_absurdo(client):
    r = await client.post("/media", json={"titulo": "X", "ano": 1500})
    assert r.status_code == 422


async def test_404_em_id_inexistente(client):
    r = await client.get("/media/9999")
    assert r.status_code == 404
