from pathlib import Path

import pytest

from lockspect import Lock, ler_lock

DADOS = Path(__file__).parent / "dados"


@pytest.fixture(scope="session")
def lock_exemplo() -> Lock:
    """O lockfile de teste, lido uma vez por sessão."""
    return ler_lock(DADOS / "exemplo.uv.lock")
