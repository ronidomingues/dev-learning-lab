import os
import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def servidor(tmp_path, monkeypatch):
    """Um servidor novo, com banco temporário, para cada teste.

    Importamos `servidor` DEPOIS de ajustar o ambiente, porque a configuração é
    lida na importação do módulo. Isso é deliberado: o processo do servidor é
    lançado uma vez pelo host, e recarregar configuração em runtime seria
    complexidade sem uso real.
    """
    monkeypatch.setenv("BIBLIOTECA_DB", str(tmp_path / "teste.db"))
    monkeypatch.setenv("BIBLIOTECA_LOG", "CRITICAL")
    import importlib
    import biblioteca.config
    import biblioteca.dados as dados
    import servidor as mod

    importlib.reload(biblioteca.config)
    importlib.reload(mod)
    dados.criar_esquema(mod.CFG.caminho_db)
    return mod.server
