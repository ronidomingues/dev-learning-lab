"""lockspect — inspeciona um `uv.lock` e explica o que há dentro dele.

Projeto-modelo do curso de uv. Ele foi escolhido de propósito: ler um lockfile
obriga a entender o que o uv escreve nele, que é o coração da reprodutibilidade.
"""

from lockspect.leitor import LockInvalido, ler_lock
from lockspect.modelo import Lock, Pacote

__version__ = "0.1.0"

__all__ = ["Lock", "LockInvalido", "Pacote", "__version__", "ler_lock"]
