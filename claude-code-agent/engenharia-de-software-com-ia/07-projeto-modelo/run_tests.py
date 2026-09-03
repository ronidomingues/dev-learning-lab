#!/usr/bin/env python3
"""Executor de testes sem dependência nenhuma.

`python3 run_tests.py` roda tudo. `python3 run_tests.py -v` mostra cada teste.
Existe para que o portão possa ser verificado em qualquer container mínimo,
sem `pip install` — que é justamente o passo que ele existe para vigiar.
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))


def main() -> int:
    verbosidade = 2 if "-v" in sys.argv else 1
    suite = unittest.defaultTestLoader.discover(str(RAIZ / "tests"), top_level_dir=str(RAIZ))
    resultado = unittest.TextTestRunner(verbosity=verbosidade).run(suite)
    return 0 if resultado.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
