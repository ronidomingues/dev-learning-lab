"""Leitura, escrita e codificação de chaves X25519.

Uma chave privada é 32 bytes aleatórios — nada além disso. Todo o resto deste
arquivo é sobre o problema que realmente derruba sistemas: onde esses 32 bytes
ficam guardados e quem consegue lê-los.
"""

import base64
import os
import stat

PREFIXO_PRIVADA = "COFRE-CHAVE-PRIVADA-V1:"
PREFIXO_PUBLICA = "cofre1pub:"


class ChaveMalFormada(Exception):
    """Arquivo de chave ilegível, truncado ou com prefixo errado."""


def _b64(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).decode("ascii").rstrip("=")


def _de_b64(texto: str) -> bytes:
    preenchimento = "=" * (-len(texto) % 4)
    try:
        return base64.urlsafe_b64decode(texto + preenchimento)
    except Exception as erro:      # base64 lança tipos variados
        raise ChaveMalFormada(f"base64 inválido: {erro}") from erro


def gerar_privada() -> bytes:
    """32 bytes do gerador do sistema operacional.

    os.urandom lê o CSPRNG do kernel (getrandom(2) no Linux, BCryptGenRandom no
    Windows). NÃO use `random` nem `numpy.random`: eles são Mersenne Twister,
    determinístico e reconstruível a partir de 624 saídas observadas.
    """
    return os.urandom(32)


def codificar_privada(privada: bytes) -> str:
    return PREFIXO_PRIVADA + _b64(privada)


def codificar_publica(publica: bytes) -> str:
    return PREFIXO_PUBLICA + _b64(publica)


def decodificar_privada(texto: str) -> bytes:
    texto = texto.strip()
    # Ignora linhas de comentário, para que o arquivo possa se documentar.
    linhas = [l for l in texto.splitlines() if l and not l.startswith("#")]
    if not linhas:
        raise ChaveMalFormada("arquivo de chave vazio")
    linha = linhas[-1].strip()
    if not linha.startswith(PREFIXO_PRIVADA):
        raise ChaveMalFormada(f"esperava uma linha começando com {PREFIXO_PRIVADA!r}")
    bruto = _de_b64(linha[len(PREFIXO_PRIVADA):])
    if len(bruto) != 32:
        raise ChaveMalFormada(f"chave privada com {len(bruto)} bytes; esperados 32")
    return bruto


def decodificar_publica(texto: str) -> bytes:
    linha = texto.strip()
    if not linha.startswith(PREFIXO_PUBLICA):
        raise ChaveMalFormada(f"esperava uma chave começando com {PREFIXO_PUBLICA!r}")
    bruto = _de_b64(linha[len(PREFIXO_PUBLICA):])
    if len(bruto) != 32:
        raise ChaveMalFormada(f"chave pública com {len(bruto)} bytes; esperados 32")
    return bruto


def gravar_privada(caminho: str, privada: bytes, publica: bytes) -> None:
    """Grava a chave privada com permissão 0600, sem janela de exposição.

    O detalhe que quase todo tutorial erra: criar o arquivo com permissão
    padrão e só depois chamar chmod deixa uma fresta de tempo em que qualquer
    usuário da máquina pode ler a chave. Aqui o modo já vai no os.open().
    """
    descritor = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                        stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
        arquivo.write("# chave privada do cofre - NAO COMPARTILHE ESTE ARQUIVO\n")
        arquivo.write(f"# chave publica correspondente: {codificar_publica(publica)}\n")
        arquivo.write(codificar_privada(privada) + "\n")


def ler_privada(caminho: str) -> bytes:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()
    modo = stat.S_IMODE(os.stat(caminho).st_mode)
    if os.name == "posix" and modo & 0o077:
        raise ChaveMalFormada(
            f"permissões frouxas em {caminho} ({oct(modo)}); corrija com: chmod 600 {caminho}")
    return decodificar_privada(conteudo)
