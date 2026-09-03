"""Derivação de chaves: scrypt (senha -> chave) e HKDF (segredo -> chaves).

São duas famílias que resolvem problemas DIFERENTES e não se substituem.

scrypt (RFC 7914) — para entrada de baixa entropia (senha humana).
    Precisa ser LENTO e caro em memória, de propósito, para que testar bilhões
    de palpites custe caro ao atacante. Sem isso, uma GPU testa 10^10 senhas
    por segundo contra um SHA-256 puro.

HKDF (RFC 5869) — para entrada de alta entropia (segredo Diffie-Hellman).
    Precisa ser RÁPIDO. O segredo já é imprevisível; o trabalho aqui é
    espalhar essa entropia uniformemente e separar contextos, de modo que a
    chave usada para cifrar não seja igual à usada para outra finalidade.

Usar scrypt onde cabe HKDF só desperdiça tempo. Usar HKDF onde cabe scrypt é
uma falha grave: transforma "senha do usuário" em "chave crackeável".
"""

import hashlib
import hmac

# Parâmetros scrypt padrão deste projeto.
# N = 2^15 = 32768, r = 8, p = 1  ->  128 * N * r  =  32 MiB de RAM por tentativa.
# Referência: RFC 7914 §2 sugere N=2^14/r=8/p=1 para uso interativo (2016) e a
# regra prática desde então é dobrar N a cada ~2 anos de hardware.
SCRYPT_LOG_N = 15
SCRYPT_R = 8
SCRYPT_P = 1
# hashlib.scrypt herda um teto de memória do OpenSSL (32 MiB). Como pedimos
# exatamente 32 MiB, é preciso levantar o teto explicitamente, ou a chamada
# falha com "memory limit exceeded" — erro clássico de quem usa scrypt no
# Python pela primeira vez.
SCRYPT_MAXMEM = 128 * 1024 * 1024


def derivar_de_senha(senha: str, sal: bytes, log_n: int = SCRYPT_LOG_N,
                     r: int = SCRYPT_R, p: int = SCRYPT_P,
                     tamanho: int = 32) -> bytes:
    """scrypt: transforma uma senha em uma chave de `tamanho` bytes.

    O sal não é secreto e não precisa ser: ele existe para que a mesma senha
    gere chaves diferentes em arquivos diferentes, o que inviabiliza tabelas
    pré-computadas (rainbow tables) e o ataque em lote contra muitos arquivos
    de uma vez. Sal repetido anula os dois benefícios.
    """
    if len(sal) < 16:
        raise ValueError("use um sal de pelo menos 16 bytes")
    return hashlib.scrypt(
        senha.encode("utf-8"),
        salt=sal,
        n=1 << log_n,
        r=r,
        p=p,
        maxmem=SCRYPT_MAXMEM,
        dklen=tamanho,
    )


def hkdf_extract(sal: bytes, material: bytes) -> bytes:
    """Etapa 1 do HKDF (RFC 5869 §2.2): concentra a entropia em 32 bytes."""
    if not sal:
        sal = bytes(32)
    return hmac.new(sal, material, hashlib.sha256).digest()


def hkdf_expand(prk: bytes, info: bytes, tamanho: int = 32) -> bytes:
    """Etapa 2 do HKDF (RFC 5869 §2.3): expande para o tamanho pedido.

    O campo `info` é a separação de domínio: derivar duas chaves do mesmo
    segredo com `info` diferentes garante que elas sejam independentes. É o
    que permite ter "chave de ida" e "chave de volta" numa sessão sem risco
    de reflexão de mensagem.
    """
    if tamanho > 255 * 32:
        raise ValueError("HKDF-SHA256 expande no máximo 8160 bytes")
    saida = b""
    bloco = b""
    contador = 1
    while len(saida) < tamanho:
        bloco = hmac.new(prk, bloco + info + bytes([contador]), hashlib.sha256).digest()
        saida += bloco
        contador += 1
    return saida[:tamanho]


def hkdf(material: bytes, sal: bytes = b"", info: bytes = b"",
         tamanho: int = 32) -> bytes:
    """HKDF completo: extract + expand."""
    return hkdf_expand(hkdf_extract(sal, material), info, tamanho)
