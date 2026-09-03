"""Formato de arquivo do cofre: cabeçalho versionado + AEAD.

Um formato de arquivo cifrado é onde a maioria dos projetos amadores se perde.
Os erros clássicos, todos evitados aqui de propósito:

  1. Não versionar. Aí o dia em que o algoritmo precisa mudar, nenhum arquivo
     antigo pode ser lido. Byte 6 deste formato é a versão.
  2. Não autenticar o cabeçalho. Se os parâmetros do scrypt ficam fora do AAD,
     o atacante troca N=2^15 por N=2^1 e o arquivo passa a ser quebrável por
     força bruta — sem tocar no criptograma.
  3. Guardar o sal ou o nonce "junto da chave" em vez de junto do arquivo.
     Sal e nonce são públicos; o que não pode faltar é UNICIDADE.
  4. Reaproveitar nonce. Ver o comentário no modo chave pública abaixo.

Layout (todos os inteiros são de 1 byte, sem endianness a discutir):

  comum
    0..5    b"COFRE1"      assinatura mágica
    6       versão         = 1
    7       modo           1 = senha (scrypt) | 2 = chave pública (X25519)

  modo 1 (senha)                        | modo 2 (chave pública)
    8       log2(N) do scrypt           |   8..39   chave pública efêmera
    9       r do scrypt                 |   40..    criptograma || etiqueta
    10      p do scrypt                 |
    11..26  sal (16 bytes)              |
    27..38  nonce (12 bytes)            |
    39..    criptograma || etiqueta     |

O cabeçalho inteiro (tudo antes do criptograma) entra como AAD.
"""

import os

from . import aead, kdf, x25519

MAGICO = b"COFRE1"
VERSAO = 1
MODO_SENHA = 1
MODO_CHAVE_PUBLICA = 2

TAMANHO_SAL = 16
TAMANHO_NONCE = 12

# Rótulo de separação de domínio do HKDF. Mudar esta string muda todas as
# chaves derivadas — por isso ela inclui o nome e a versão do formato.
INFO_HKDF = b"cofre v1 selo x25519-chacha20poly1305"


class ArquivoInvalido(Exception):
    """O arquivo não é um cofre, ou é de uma versão desconhecida."""


def _cabecalho_senha(log_n: int, r: int, p: int, sal: bytes, nonce: bytes) -> bytes:
    return (MAGICO + bytes([VERSAO, MODO_SENHA, log_n, r, p]) + sal + nonce)


def cifrar_com_senha(dados: bytes, senha: str, log_n: int = kdf.SCRYPT_LOG_N,
                     r: int = kdf.SCRYPT_R, p: int = kdf.SCRYPT_P) -> bytes:
    """Cifra `dados` com uma senha. Devolve o arquivo completo em bytes."""
    sal = os.urandom(TAMANHO_SAL)
    nonce = os.urandom(TAMANHO_NONCE)
    cabecalho = _cabecalho_senha(log_n, r, p, sal, nonce)
    chave = kdf.derivar_de_senha(senha, sal, log_n, r, p)
    return cabecalho + aead.cifrar(chave, nonce, dados, aad=cabecalho)


def cifrar_para_chave(dados: bytes, publica_destinatario: bytes) -> bytes:
    """Cifra `dados` para o dono de uma chave pública X25519.

    Quem cifra não precisa de chave própria: gera um par efêmero, faz o
    Diffie-Hellman com a pública do destinatário e joga a privada efêmera fora.
    Isso dá sigilo futuro (forward secrecy) do lado do remetente — nem ele
    consegue reabrir o arquivo depois.

    O nonce é ZERO, e isso é seguro AQUI por um motivo específico: a chave
    simétrica é derivada da chave efêmera, que é nova a cada arquivo, então o
    par (chave, nonce) nunca se repete. Copiar esse padrão para um contexto em
    que a chave é fixa seria catastrófico.
    """
    if len(publica_destinatario) != 32:
        raise ValueError("chave pública X25519 precisa ter 32 bytes")

    privada_efemera = os.urandom(32)
    publica_efemera = x25519.chave_publica(privada_efemera)
    segredo = x25519.segredo_compartilhado(privada_efemera, publica_destinatario)

    # As duas chaves públicas entram no sal do HKDF: assim o material derivado
    # fica amarrado a ESTE par de interlocutores, e não só ao segredo bruto.
    chave = kdf.hkdf(segredo, sal=publica_efemera + publica_destinatario,
                     info=INFO_HKDF, tamanho=32)

    cabecalho = MAGICO + bytes([VERSAO, MODO_CHAVE_PUBLICA]) + publica_efemera
    nonce = bytes(TAMANHO_NONCE)
    return cabecalho + aead.cifrar(chave, nonce, dados, aad=cabecalho)


def _validar_prefixo(arquivo: bytes) -> int:
    if len(arquivo) < 8 or arquivo[:6] != MAGICO:
        raise ArquivoInvalido("isto não é um arquivo do cofre (assinatura ausente)")
    if arquivo[6] != VERSAO:
        raise ArquivoInvalido(
            f"versão de formato {arquivo[6]} desconhecida; esta build lê a versão {VERSAO}")
    return arquivo[7]


def modo_do_arquivo(arquivo: bytes) -> int:
    """Descobre se o arquivo pede senha ou chave privada, sem decifrar nada."""
    return _validar_prefixo(arquivo)


def decifrar_com_senha(arquivo: bytes, senha: str) -> bytes:
    modo = _validar_prefixo(arquivo)
    if modo != MODO_SENHA:
        raise ArquivoInvalido("este arquivo foi selado para uma chave pública, não para senha")
    if len(arquivo) < 39 + 16:
        raise ArquivoInvalido("arquivo truncado")

    log_n, r, p = arquivo[8], arquivo[9], arquivo[10]
    if not 10 <= log_n <= 22:
        # Limite defensivo: log_n grande demais é um pedido de esgotamento de
        # memória disfarçado de arquivo; pequeno demais é senha fraca.
        raise ArquivoInvalido(f"parâmetro N do scrypt fora da faixa aceita (log2 N = {log_n})")

    sal = arquivo[11:11 + TAMANHO_SAL]
    nonce = arquivo[27:27 + TAMANHO_NONCE]
    cabecalho = arquivo[:39]
    corpo = arquivo[39:]

    chave = kdf.derivar_de_senha(senha, sal, log_n, r, p)
    return aead.decifrar(chave, nonce, corpo, aad=cabecalho)


def decifrar_com_chave(arquivo: bytes, privada: bytes) -> bytes:
    modo = _validar_prefixo(arquivo)
    if modo != MODO_CHAVE_PUBLICA:
        raise ArquivoInvalido("este arquivo foi cifrado com senha, não para uma chave")
    if len(arquivo) < 40 + 16:
        raise ArquivoInvalido("arquivo truncado")

    publica_efemera = arquivo[8:40]
    cabecalho = arquivo[:40]
    corpo = arquivo[40:]

    minha_publica = x25519.chave_publica(privada)
    segredo = x25519.segredo_compartilhado(privada, publica_efemera)
    chave = kdf.hkdf(segredo, sal=publica_efemera + minha_publica,
                     info=INFO_HKDF, tamanho=32)
    return aead.decifrar(chave, bytes(TAMANHO_NONCE), corpo, aad=cabecalho)
