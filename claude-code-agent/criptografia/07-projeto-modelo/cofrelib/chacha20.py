"""ChaCha20 (RFC 8439, seções 2.1 a 2.4), em Python puro.

Cifra de fluxo (stream cipher): transforma uma chave de 32 bytes e um nonce de
12 bytes num fluxo pseudoaleatório de bytes ("keystream"), que é combinado com
o texto claro por XOR.

Regra de ouro que este arquivo existe para ensinar:
    NUNCA reutilize o par (chave, nonce).
Se você usar o mesmo par duas vezes, o mesmo keystream é gerado duas vezes, e
XOR dos dois criptogramas cancela a chave: c1 ^ c2 == m1 ^ m2. O sigilo acaba
ali, sem que ninguém precise atacar a matemática.
"""

# Constante "expand 32-byte k" em ASCII, lida como quatro palavras de 32 bits
# little-endian. Não é segredo, não é aleatória: serve para que o estado inicial
# nunca seja todo zeros e para separar ChaCha de outras construções.
CONSTANTES = (0x61707865, 0x3320646E, 0x79622D32, 0x6B206574)

MASCARA32 = 0xFFFFFFFF


def _rotl32(valor: int, deslocamento: int) -> int:
    """Rotação circular à esquerda em 32 bits."""
    valor &= MASCARA32
    return ((valor << deslocamento) | (valor >> (32 - deslocamento))) & MASCARA32


def quarter_round(estado: list, a: int, b: int, c: int, d: int) -> None:
    """A operação elementar do ChaCha, aplicada in-place sobre 4 palavras.

    RFC 8439 §2.1:
        a += b; d ^= a; d <<<= 16;
        c += d; b ^= c; b <<<= 12;
        a += b; d ^= a; d <<<= 8;
        c += d; b ^= c; b <<<= 7;

    Só três operações aparecem aqui: soma módulo 2^32, XOR e rotação — o famoso
    "ARX" (Add-Rotate-Xor). Nenhuma delas depende de tabela em memória, e é por
    isso que ChaCha é naturalmente resistente a ataques de cache-timing, ao
    contrário de implementações de AES em software com S-box tabelada.
    """
    estado[a] = (estado[a] + estado[b]) & MASCARA32
    estado[d] = _rotl32(estado[d] ^ estado[a], 16)

    estado[c] = (estado[c] + estado[d]) & MASCARA32
    estado[b] = _rotl32(estado[b] ^ estado[c], 12)

    estado[a] = (estado[a] + estado[b]) & MASCARA32
    estado[d] = _rotl32(estado[d] ^ estado[a], 8)

    estado[c] = (estado[c] + estado[d]) & MASCARA32
    estado[b] = _rotl32(estado[b] ^ estado[c], 7)


def _estado_inicial(chave: bytes, contador: int, nonce: bytes) -> list:
    """Monta a matriz 4x4 de 32 bits descrita em RFC 8439 §2.3."""
    if len(chave) != 32:
        raise ValueError("ChaCha20 exige chave de 32 bytes (256 bits)")
    if len(nonce) != 12:
        raise ValueError("ChaCha20 exige nonce de 12 bytes (96 bits)")
    if not 0 <= contador <= MASCARA32:
        raise ValueError("contador de bloco fora da faixa de 32 bits")

    estado = list(CONSTANTES)
    estado += [int.from_bytes(chave[i:i + 4], "little") for i in range(0, 32, 4)]
    estado.append(contador)
    estado += [int.from_bytes(nonce[i:i + 4], "little") for i in range(0, 12, 4)]
    return estado


def bloco(chave: bytes, contador: int, nonce: bytes) -> bytes:
    """Função de bloco do ChaCha20: 64 bytes de keystream (RFC 8439 §2.3)."""
    estado = _estado_inicial(chave, contador, nonce)
    trabalho = list(estado)

    # 20 rodadas = 10 iterações de (rodada de coluna + rodada de diagonal).
    for _ in range(10):
        # Colunas.
        quarter_round(trabalho, 0, 4, 8, 12)
        quarter_round(trabalho, 1, 5, 9, 13)
        quarter_round(trabalho, 2, 6, 10, 14)
        quarter_round(trabalho, 3, 7, 11, 15)
        # Diagonais.
        quarter_round(trabalho, 0, 5, 10, 15)
        quarter_round(trabalho, 1, 6, 11, 12)
        quarter_round(trabalho, 2, 7, 8, 13)
        quarter_round(trabalho, 3, 4, 9, 14)

    # A soma final com o estado original é o que torna a função irreversível:
    # sem ela, as 20 rodadas seriam uma permutação invertível e o keystream
    # entregaria a chave.
    saida = bytearray()
    for original, misturado in zip(estado, trabalho):
        saida += ((original + misturado) & MASCARA32).to_bytes(4, "little")
    return bytes(saida)


def cifrar(chave: bytes, contador: int, nonce: bytes, dados: bytes) -> bytes:
    """XOR de `dados` com o keystream (RFC 8439 §2.4).

    Cifrar e decifrar são a MESMA função — essa é a natureza de uma cifra de
    fluxo. Isso também explica por que ela, sozinha, não protege integridade:
    quem intercepta pode inverter qualquer bit do texto claro invertendo o bit
    correspondente do criptograma. É para isso que existe o Poly1305.
    """
    saida = bytearray(len(dados))
    for indice in range(0, len(dados), 64):
        pedaco = dados[indice:indice + 64]
        fluxo = bloco(chave, contador + indice // 64, nonce)
        for j, byte in enumerate(pedaco):
            saida[indice + j] = byte ^ fluxo[j]
    return bytes(saida)
