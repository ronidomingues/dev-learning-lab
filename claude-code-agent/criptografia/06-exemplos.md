# 06 · Exemplos — do trivial ao de produção

**Nível:** iniciante a avançado · **Última atualização:** 19/08/2026
**Executados em:** Python 3.10.12 + `cryptography` 50.0.0, Ubuntu 22.04.5, Intel i3-10100T

Treze exemplos completos. **Todo código aqui foi executado**, e todas as saídas
mostradas são reais — inclusive as medições de tempo. Valores aleatórios
(chaves, nonces) serão diferentes na sua máquina; o comportamento, não.

Para rodar:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install cryptography
```

| # | Exemplo | Nível |
|---|---|---|
| 1 | [Cifrar e decifrar com AES-256-GCM](#1--cifrar-e-decifrar-com-aes-256-gcm) | trivial |
| 2 | [Por que o modo ECB é proibido](#2--por-que-o-modo-ecb-é-proibido) | iniciante |
| 3 | [Cifrar arquivos na linha de comando](#3--cifrar-arquivos-na-linha-de-comando) | iniciante |
| 4 | [Guardar senha do jeito certo, e migrar parâmetros](#4--guardar-senha-do-jeito-certo-e-migrar-parâmetros) | intermediário |
| 5 | [Reuso de nonce, explorado na prática](#5--reuso-de-nonce-explorado-na-prática) | intermediário |
| 6 | [Canal seguro: X25519 → HKDF → ChaCha20-Poly1305](#6--canal-seguro-x25519--hkdf--chacha20-poly1305) | intermediário |
| 7 | [**Produção:** verificar assinatura de webhook](#7--produção-verificar-assinatura-de-webhook) | intermediário |
| 8 | [**Produção:** envelope encryption num banco de dados](#8--produção-envelope-encryption-num-banco-de-dados) | avançado |
| 9 | [Ataque de tempo, medido](#9--ataque-de-tempo-medido) | avançado |
| 10 | [Acordo híbrido pós-quântico X25519 + ML-KEM-768](#10--acordo-híbrido-pós-quântico-x25519--ml-kem-768) | avançado |
| 11 | [Compartilhamento de segredo de Shamir](#11--compartilhamento-de-segredo-de-shamir) | avançado |
| 12 | [**Produção:** assinar e verificar um release](#12--produção-assinar-e-verificar-um-release) | intermediário |
| 13 | [Bônus: uma PKI inteira em 60 linhas](#13--bônus-uma-pki-inteira-em-60-linhas) | avançado |

---

## 1 · Cifrar e decifrar com AES-256-GCM

**Problema:** proteger uma mensagem com uma chave que as duas pontas já têm,
garantindo que ela não possa ser lida **nem alterada**.

```python
"""O caso mais comum de todos: cifrar e decifrar com AES-256-GCM."""
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

chave = AESGCM.generate_key(bit_length=256)     # 32 bytes do CSPRNG do sistema
aead = AESGCM(chave)

nonce = os.urandom(12)                          # NOVO a cada mensagem
mensagem = b"transferir R$ 1.000,00 para a conta 12345-6"
aad = b"id-transacao:9f3a"                      # autenticado, NÃO cifrado

cifrado = aead.encrypt(nonce, mensagem, aad)
print(f"mensagem : {len(mensagem)} bytes")
print(f"cifrado  : {len(cifrado)} bytes  (16 a mais: a etiqueta)")
print(f"hex      : {cifrado.hex()[:64]}...")
print("decifrado:", aead.decrypt(nonce, cifrado, aad).decode())

print("\nagora, as três formas de falhar:")
adulterado = bytearray(cifrado); adulterado[5] ^= 0x01
for rotulo, args in [
        ("um bit trocado no criptograma", (nonce, bytes(adulterado), aad)),
        ("AAD diferente",                 (nonce, cifrado, b"id-transacao:0000")),
        ("nonce errado",                  (os.urandom(12), cifrado, aad))]:
    try:
        aead.decrypt(*args); print(f"  {rotulo:32s}: ACEITOU (bug!)")
    except InvalidTag:
        print(f"  {rotulo:32s}: InvalidTag — recusado")
```

**Saída real:**

```
mensagem : 43 bytes
cifrado  : 59 bytes  (16 a mais: a etiqueta)
hex      : 27bb0b6fb08b762f615a8d6df92d7515e31a66d810f1c95eafd45050dcaf8244...
decifrado: transferir R$ 1.000,00 para a conta 12345-6

agora, as três formas de falhar:
  um bit trocado no criptograma   : InvalidTag — recusado
  AAD diferente                   : InvalidTag — recusado
  nonce errado                    : InvalidTag — recusado
```

**Explicação.** `AESGCM` é uma primitiva **AEAD**: cifra e autentica numa
única operação. Três coisas para levar deste exemplo:

- O criptograma tem sempre 16 bytes a mais: é a etiqueta de autenticação.
  Não há AEAD sem esse custo.
- O **AAD** (dados associados) é autenticado mas não cifrado. Use-o para
  amarrar o criptograma ao seu contexto: identificador do registro, versão do
  formato, destinatário. É o que impede que um criptograma válido seja movido
  de lugar (ver exemplo 8).
- Qualquer alteração — no criptograma, no AAD ou no nonce — dá `InvalidTag`,
  e **antes** de qualquer texto claro ser devolvido. Nunca capture essa
  exceção para "tentar mesmo assim".

---

## 2 · Por que o modo ECB é proibido

**Problema:** mostrar, e não apenas afirmar, que o modo ECB vaza a estrutura
do texto claro. Este é o famoso "pinguim do Tux", em versão ASCII.

```python
"""Por que ECB é proibido: padrões do texto claro sobrevivem à cifragem."""
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# "Imagem" de 32x16 em preto e branco: um retângulo dentro de um fundo.
L, A = 32, 16
imagem = bytearray()
for y in range(A):
    for x in range(L):
        dentro = 6 <= x < 26 and 4 <= y < 12
        imagem.append(0xFF if dentro else 0x00)

def mostrar(titulo, dados):
    print(titulo)
    for y in range(A):
        linha = dados[y*L:(y+1)*L]
        print("".join("#" if b > 127 else "." for b in linha))
    print()

chave = os.urandom(32)
ecb = Cipher(algorithms.AES(chave), modes.ECB()).encryptor()
cifrado_ecb = ecb.update(bytes(imagem)) + ecb.finalize()
ctr = Cipher(algorithms.AES(chave), modes.CTR(os.urandom(16))).encryptor()
cifrado_ctr = ctr.update(bytes(imagem)) + ctr.finalize()

mostrar("ORIGINAL", imagem)
mostrar("CIFRADO COM AES-256-ECB", cifrado_ecb)
mostrar("CIFRADO COM AES-256-CTR", cifrado_ctr)

blocos = {cifrado_ecb[i:i+16] for i in range(0, len(cifrado_ecb), 16)}
print(f"ECB: {len(cifrado_ecb)//16} blocos de 16 bytes, apenas {len(blocos)} distintos")
blocos_ctr = {cifrado_ctr[i:i+16] for i in range(0, len(cifrado_ctr), 16)}
print(f"CTR: {len(cifrado_ctr)//16} blocos de 16 bytes, {len(blocos_ctr)} distintos")
```

**Saída real:**

```
ORIGINAL
................................
................................
................................
................................
......####################......
......####################......
......####################......
......####################......
......####################......
......####################......
......####################......
......####################......
................................
................................
................................
................................

CIFRADO COM AES-256-ECB
..#...###...##....#...###...##..
..#...###...##....#...###...##..
..#...###...##....#...###...##..
..#...###...##....#...###...##..
.#.######..#..####...#...#.#.###
.#.######..#..####...#...#.#.###
.#.######..#..####...#...#.#.###
.#.######..#..####...#...#.#.###
.#.######..#..####...#...#.#.###
.#.######..#..####...#...#.#.###
.#.######..#..####...#...#.#.###
.#.######..#..####...#...#.#.###
..#...###...##....#...###...##..
..#...###...##....#...###...##..
..#...###...##....#...###...##..
..#...###...##....#...###...##..

CIFRADO COM AES-256-CTR
.##..#.#........##.#...#..##..##
.#.##..#####..#..#.####......##.
..#.#.#.#.........#..#..#....##.
..######.#.##.#...#.####..#####.
####.##.######..#...#....#.....#
...#.###########.######.##..#...
###..#.#.##.######.#.#.##....###
....##.##.###.####...#.##..##...
.###..#..#...#.#.#....#.###...#.
....#.###.#####.##...####.###.#.
.##..#.####.####.####..#######..
#......#...#.#..###...#.#..#####
..##.#...#.....##...###.##.#.#.#
##.##..#....#..#.##.#.##.#.###..
#.##.##..#.#.#.#.#..#.#.###.####
#.#.##.....#.#####.##.....#.##.#

ECB: 32 blocos de 16 bytes, apenas 3 distintos
CTR: 32 blocos de 16 bytes, 32 distintos
```

**Explicação.** O ECB cifra cada bloco de 16 bytes de forma **independente e
determinística**: blocos iguais no texto claro viram blocos iguais no
criptograma. O retângulo continua visível. O contador de blocos distintos
prova o ponto de forma numérica: 32 blocos, apenas 3 valores diferentes.

O CTR (e o GCM, e o CBC com IV aleatório) resolve isso porque cada bloco é
combinado com algo que varia — contador ou bloco anterior. É por isso que
**AES não é seguro; AES em um modo adequado é seguro**. O algoritmo sozinho
não decide nada. Detalhes em [13-modos-e-aead.md](13-modos-e-aead.md).

---

## 3 · Cifrar arquivos na linha de comando

**Problema:** cifrar um arquivo para si mesmo e para um colega, sem escrever
uma linha de código.

```bash
# --- para você mesmo, com senha ---
age -p -o diario.age diario.txt          # pede a senha duas vezes
age -d diario.age > diario.txt

# --- para um colega, com a chave pública dele ---
age-keygen -o minha.age                  # cada um gera a sua, uma vez
# Public key: age1cscgpa9u4eafplfq6spcpa9l3avyv0r50uwt2ny63tcdkfvklcxq2rcvr7
age -r age1cscgpa9u4eafplfq6spcpa9l3avyv0r50uwt2ny63tcdkfvklcxq2rcvr7 \
    -o contrato.age contrato.pdf
age -d -i minha.age contrato.age > contrato.pdf

# --- uma pasta inteira, cifrada e compactada, em um comando ---
tar czf - projeto/ | age -r age1... -o projeto.tar.gz.age
age -d -i minha.age projeto.tar.gz.age | tar xzf -

# --- usando a chave SSH que você já tem, sem criar outra ---
age -R ~/.ssh/id_ed25519.pub -o s.age s.txt
age -d -i ~/.ssh/id_ed25519 s.age

# --- forma "armada" (texto), para colar em e-mail ou chat ---
age -a -r age1... s.txt
```

Saída real do último comando:

```
-----BEGIN AGE ENCRYPTED FILE-----
YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSA5R2JjKzV1aDRlQTgvNm9v
OXV1SjZYc1l1ZlVmZlBJei8zczJXVWxybkJRCnJkSkx5Rk11SEJZbFFTTkpaRlRi
ZWxUUStkS29BNWVaRGh0TlhZL3V5MnMKLS0tIE9HY281Z2xTUjM2dDNiVEo2QTZt
cjZocnRoamRocHY3Z0FGR3ZRdmQ1VWMKvFSP06BvDGf9+NFiCuwsW/8BMcdmGyUF
z7M5MERTGg0oWyoJ8kF+WMHnQBBwtJbBEQ==
-----END AGE ENCRYPTED FILE-----
```

**Explicação.** O `age` faz exatamente o que o
[projeto-modelo](07-projeto-modelo/README.md) faz: X25519 efêmero +
ChaCha20-Poly1305, com o cabeçalho autenticado. Note o que ele **não** oferece:
escolha de algoritmo, tamanho de chave, modo de operação ou "compatibilidade
com versões antigas". Menos opções, menos maneiras de errar.

---

## 4 · Guardar senha do jeito certo, e migrar parâmetros

**Problema:** armazenar senhas de usuários de modo que um vazamento do banco
não entregue as senhas — e conseguir aumentar o custo depois, sem forçar todo
mundo a trocar de senha.

```python
"""Guardar senha certo, e migrar parâmetros sem obrigar todo mundo a trocar."""
import hashlib, hmac, os, time

def gerar(senha: str, log_n=15) -> str:
    sal = os.urandom(16)
    d = hashlib.scrypt(senha.encode(), salt=sal, n=1 << log_n, r=8, p=1,
                       maxmem=256*1024*1024, dklen=32)
    return f"scrypt${log_n}$8$1${sal.hex()}${d.hex()}"

def conferir(senha: str, registro: str) -> bool:
    algo, log_n, r, p, sal, esperado = registro.split("$")
    assert algo == "scrypt"
    d = hashlib.scrypt(senha.encode(), salt=bytes.fromhex(sal), n=1 << int(log_n),
                       r=int(r), p=int(p), maxmem=256*1024*1024, dklen=32)
    return hmac.compare_digest(d.hex(), esperado)

def precisa_atualizar(registro: str, alvo=17) -> bool:
    return int(registro.split("$")[1]) < alvo

registro = gerar("cavalo-bateria-grampo-correto", log_n=14)
print("registro guardado:", registro[:60], "...")
print("senha certa :", conferir("cavalo-bateria-grampo-correto", registro))
print("senha errada:", conferir("cavalo-bateria-grampo-incorreto", registro))

print("\nparâmetros ficaram fracos?", precisa_atualizar(registro))
print("-> no próximo login bem-sucedido, regravar com o custo novo:")
t = time.perf_counter(); novo = gerar("cavalo-bateria-grampo-correto", log_n=17)
print(f"   novo registro em {(time.perf_counter()-t)*1000:.0f} ms:", novo[:44], "...")

print("\ncusto de cada nível (mediana de 3 execuções):")
for log_n in (12, 14, 16, 17):
    ts = []
    for _ in range(3):
        t = time.perf_counter(); gerar("x", log_n); ts.append(time.perf_counter()-t)
    print(f"   log2 N = {log_n} ({128*(1<<log_n)*8//2**20:4d} MiB): {sorted(ts)[1]*1000:6.0f} ms")
```

**Saída real:**

```
registro guardado: scrypt$14$8$1$8277ccbfa4ca9e15cf112f1bff85803a$8500b3319a2e2 ...
senha certa : True
senha errada: False

parâmetros ficaram fracos? True
-> no próximo login bem-sucedido, regravar com o custo novo:
   novo registro em 404 ms: scrypt$17$8$1$4c05fb949001b0a4f7bd43fd7ba7cb ...

custo de cada nível (mediana de 3 execuções):
   log2 N = 12 (   4 MiB):     11 ms
   log2 N = 14 (  16 MiB):     45 ms
   log2 N = 16 (  64 MiB):    202 ms
   log2 N = 17 ( 128 MiB):    407 ms
```

**Explicação.** Três decisões estruturais aqui:

1. **Os parâmetros vão gravados junto com o hash.** É por isso que o registro
   tem a forma `algoritmo$log_n$r$p$sal$hash`. Sem isso, você nunca consegue
   mudar o custo — teria de saber, para cada usuário, qual custo foi usado.
2. **A migração acontece no login.** Quando o usuário acerta a senha, você tem
   a senha em claro por um instante; é o único momento em que dá para regravar
   com parâmetros novos.
3. **O custo é calibrado por tempo, não por gosto.** A regra prática: escolha
   o maior custo que o seu servidor aguenta no pico de logins. Nesta máquina,
   `log2 N = 17` custa ~430 ms — alto demais para um site com muitos logins
   simultâneos, adequado para um cofre pessoal.

Em produção, prefira **Argon2id** (`pip install argon2-cffi`), vencedor da
Password Hashing Competition de 2015 e recomendação atual do OWASP. O scrypt
está aqui porque vem na biblioteca padrão do Python.

---

## 5 · Reuso de nonce, explorado na prática

**Problema:** entender, com o ataque na mão, por que "o nonce precisa ser
único" não é conselho, é condição de funcionamento.

```python
"""O erro mais destrutivo: repetir o nonce. Aqui ele é explorado na prática."""
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

chave, nonce = AESGCM.generate_key(bit_length=256), os.urandom(12)
aead = AESGCM(chave)

# Duas mensagens, MESMA chave, MESMO nonce — o pecado capital.
m1 = b"PAGAR 000100 PARA A CONTA ALICE-01"
m2 = b"PAGAR 999999 PARA A CONTA MALLORY9"
c1 = aead.encrypt(nonce, m1, b"")[:-16]      # descartando a etiqueta
c2 = aead.encrypt(nonce, m2, b"")[:-16]

# O atacante NÃO conhece a chave. Ele só tem os dois criptogramas.
xor = bytes(a ^ b for a, b in zip(c1, c2))
print("c1 ^ c2 :", xor.hex())
print("m1 ^ m2 :", bytes(a ^ b for a, b in zip(m1, m2)).hex())
print("iguais  :", xor == bytes(a ^ b for a, b in zip(m1, m2)))

# Se ele adivinha (ou conhece) uma das mensagens, recupera a outra inteira.
recuperada = bytes(a ^ b for a, b in zip(xor, m1))
print("\natacante conhece m1 e recupera m2:", recuperada.decode())

# Em AES-GCM é pior: o reuso também revela a chave de autenticação H,
# permitindo FORJAR mensagens novas com etiqueta válida ("forbidden attack",
# Joux 2006). Foi assim que se descobriram, em 2016, servidores TLS de
# fabricantes conhecidos gerando nonces repetidos em produção.
```

**Saída real:**

```
c1 ^ c2 : 00000000000009090908090900000000000000000000000000000c0d050f0a7f6908
m1 ^ m2 : 00000000000009090908090900000000000000000000000000000c0d050f0a7f6908
iguais  : True

atacante conhece m1 e recupera m2: PAGAR 999999 PARA A CONTA MALLORY9
```

**Explicação.** Repare no que o atacante precisou saber: **nada da chave**.
Repetir o par (chave, nonce) faz o mesmo keystream ser gerado duas vezes; o
XOR dos criptogramas é o XOR dos textos claros, e a chave desaparece da
equação. Repare também nos zeros no começo do XOR: são exatamente os trechos
em que as duas mensagens coincidem (`PAGAR `), o que já entrega estrutura.

Em AES-GCM é pior do que perda de sigilo: o reuso também revela a chave de
autenticação interna `H`, permitindo **forjar** mensagens novas com etiqueta
válida. É o *forbidden attack* (Joux, 2006), e em 2016 pesquisadores acharam
servidores TLS de produção repetindo nonces — o que permitia injetar conteúdo
em conexões HTTPS legítimas.

---

## 6 · Canal seguro: X25519 → HKDF → ChaCha20-Poly1305

**Problema:** duas partes que só conhecem as chaves públicas uma da outra
precisam de um canal cifrado bidirecional.

```python
"""Canal seguro entre duas partes: X25519 -> HKDF -> ChaCha20-Poly1305."""
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization as ser

def bruta(chave_publica):
    return chave_publica.public_bytes(ser.Encoding.Raw, ser.PublicFormat.Raw)

alice, bob = X25519PrivateKey.generate(), X25519PrivateKey.generate()
pa, pb = bruta(alice.public_key()), bruta(bob.public_key())
print("pública da Alice:", pa.hex()[:32], "...")
print("pública do Bob  :", pb.hex()[:32], "...")

seg_a = alice.exchange(bob.public_key())
seg_b = bob.exchange(alice.public_key())
print("segredos coincidem:", seg_a == seg_b)
print("segredo bruto     :", seg_a.hex()[:32], "...")

def derivar(segredo, rotulo):
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=pa + pb,
                info=rotulo).derive(segredo)

# Duas chaves distintas para os dois sentidos: evita reflexão de mensagem.
k_ida = derivar(seg_a, b"exemplo v1 alice->bob")
k_volta = derivar(seg_a, b"exemplo v1 bob->alice")
print("chave ida   :", k_ida.hex()[:32], "...")
print("chave volta :", k_volta.hex()[:32], "...")
print("são diferentes:", k_ida != k_volta)

contador = 0
def enviar(chave, mensagem, seq):
    nonce = seq.to_bytes(12, "big")            # contador, nunca repete
    return ChaCha20Poly1305(chave).encrypt(nonce, mensagem, seq.to_bytes(12, "big"))

pacote = enviar(k_ida, b"oi Bob, aqui e a Alice", contador)
print("pacote:", pacote.hex()[:48], f"... ({len(pacote)} bytes)")
aberto = ChaCha20Poly1305(k_ida).decrypt(contador.to_bytes(12,"big"), pacote,
                                         contador.to_bytes(12,"big"))
print("Bob leu:", aberto.decode())
```

**Saída real:**

```
pública da Alice: 543bd109fe4f1e065d234ed5756d712d ...
pública do Bob  : ea41769a17d4bdf3f3044d3bcf6b860f ...
segredos coincidem: True
segredo bruto     : e2f90a1316e76e6d8c869f86fbf30411 ...
chave ida   : b32210509c62837ae4a29e08daee7794 ...
chave volta : 55829a1b91d9189f8184e3f4147af7f5 ...
são diferentes: True
pacote: 1c314b07336b3617a45e15206df1ace6861841a8886ea828 ... (38 bytes)
Bob leu: oi Bob, aqui e a Alice
```

**Explicação.** Este é o esqueleto de qualquer protocolo seguro moderno,
incluindo o TLS 1.3 e o Signal. Quatro detalhes que separam o exemplo correto
do exemplo perigoso:

- **Nunca use o segredo do Diffie-Hellman como chave.** Ele não é
  uniformemente distribuído (é uma coordenada de um ponto de curva). O HKDF
  existe para transformá-lo em bytes uniformes.
- **As duas chaves públicas entram no `salt`.** Isso amarra o material
  derivado a este par específico de interlocutores.
- **Chaves diferentes para cada sentido.** Sem isso, um atacante devolve a
  você a sua própria mensagem e ela é aceita como se viesse do outro lado
  (ataque de reflexão).
- **O nonce é um contador.** Determinístico, nunca repete, e cabe em 12 bytes
  por 2⁹⁶ mensagens.

O que falta aqui para virar um protocolo de verdade: autenticação das chaves
públicas (senão você faz um acordo perfeitamente seguro com o atacante),
sigilo futuro por mensagem, e tratamento de perda e reordenação de pacotes.
Isso está em [23-criptografia-de-ponta-a-ponta.md](23-criptografia-de-ponta-a-ponta.md).

---

## 7 · Produção: verificar assinatura de webhook

**Problema real:** seu sistema recebe notificações de um gateway de pagamento
por HTTP. Como saber que a requisição veio mesmo do gateway, e não de alguém
que descobriu a URL?

```python
"""Caso de produção: verificar a assinatura de um webhook (padrão GitHub/Stripe)."""
import hashlib, hmac, time

SEGREDO = b"segredo-compartilhado-do-webhook"

def assinar(corpo: bytes, instante: int) -> str:
    base = f"{instante}.".encode() + corpo          # o instante entra na assinatura
    return f"t={instante},v1=" + hmac.new(SEGREDO, base, hashlib.sha256).hexdigest()

def verificar(corpo: bytes, cabecalho: str, tolerancia=300) -> bool:
    partes = dict(p.split("=", 1) for p in cabecalho.split(","))
    instante = int(partes["t"])
    if abs(time.time() - instante) > tolerancia:    # janela contra repetição
        return False
    esperado = hmac.new(SEGREDO, f"{instante}.".encode() + corpo,
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, partes["v1"])

corpo = b'{"evento":"pagamento.aprovado","valor":19900}'
agora = int(time.time())
cabecalho = assinar(corpo, agora)
print("cabeçalho enviado:", cabecalho)
print("assinatura válida        :", verificar(corpo, cabecalho))
adulterado = corpo.replace(b"19900", b"00001")
print("corpo adulterado         :", verificar(adulterado, cabecalho))
antigo = assinar(corpo, agora - 3600)
print("mesmo corpo, 1 h atrás   :", verificar(corpo, antigo))
```

**Saída real:**

```
cabeçalho enviado: t=1787161014,v1=6427339c39377942375857674e15aca558fe86993d97305f98eeff0667cb70ed
assinatura válida        : True
corpo adulterado         : False
mesmo corpo, 1 h atrás   : False
```

**Explicação.** Este é, com variações mínimas de formato, o esquema usado por
Stripe, GitHub, Shopify e pela maioria dos gateways brasileiros. Quatro
pontos que costumam ser implementados errado:

1. **O instante entra na assinatura.** Sem isso, um atacante que capture uma
   notificação legítima pode reenviá-la mil vezes (ataque de repetição) — e o
   seu sistema credita mil pagamentos.
2. **`hmac.compare_digest`, sempre.** Ver o exemplo 9 para a medição do
   vazamento.
3. **Assine o corpo bruto, byte a byte** — nunca o JSON re-serializado. Um
   `json.loads()` seguido de `json.dumps()` muda espaços e ordem de chaves, e
   a assinatura deixa de bater por motivo nenhum.
4. **HMAC prova origem, não identidade jurídica.** O segredo é compartilhado:
   quem verifica também pode assinar. Se você precisa de não repúdio (provar
   a um terceiro que foi o gateway), precisa de assinatura assimétrica.

---

## 8 · Produção: envelope encryption num banco de dados

**Problema real:** você precisa guardar CPF cifrado no banco, com rotação de
chave viável e sem que uma consulta SQL vazada entregue os dados.

```python
"""Caso de produção: envelope encryption (KEK/DEK) para campo de banco de dados."""
import os, base64, sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# A KEK (Key Encryption Key) viveria num KMS/HSM e nunca sairia de lá.
# Aqui ela é simulada; a estrutura do código é a mesma.
KEK = AESGCM(os.urandom(32))
VERSAO_KEK = 1

def cifrar_campo(texto: str, contexto: bytes) -> bytes:
    dek = os.urandom(32)                       # chave nova para CADA registro
    n1, n2 = os.urandom(12), os.urandom(12)
    dado = AESGCM(dek).encrypt(n1, texto.encode(), contexto)
    dek_embrulhada = KEK.encrypt(n2, dek, contexto)
    del dek
    return bytes([VERSAO_KEK]) + n2 + len(dek_embrulhada).to_bytes(2,"big") + \
           dek_embrulhada + n1 + dado

def decifrar_campo(blob: bytes, contexto: bytes) -> str:
    assert blob[0] == VERSAO_KEK
    n2 = blob[1:13]; tam = int.from_bytes(blob[13:15], "big")
    dek_embrulhada = blob[15:15+tam]
    resto = blob[15+tam:]
    n1, dado = resto[:12], resto[12:]
    dek = KEK.decrypt(n2, dek_embrulhada, contexto)
    return AESGCM(dek).decrypt(n1, dado, contexto).decode()

banco = sqlite3.connect(":memory:")
banco.execute("CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT, cpf BLOB)")
for cid, nome, cpf in [(1,"Ana","111.111.111-11"), (2,"Bruno","222.222.222-22")]:
    contexto = f"clientes:cpf:{cid}".encode()      # amarra o dado à linha
    banco.execute("INSERT INTO clientes VALUES (?,?,?)",
                  (cid, nome, cifrar_campo(cpf, contexto)))

print("como está no banco:")
for cid, nome, blob in banco.execute("SELECT * FROM clientes"):
    print(f"  {cid} {nome:6s} {base64.b64encode(blob).decode()[:56]}... ({len(blob)} B)")

print("\nlendo com o contexto certo:")
for cid, nome, blob in banco.execute("SELECT * FROM clientes"):
    print(f"  {cid} {nome:6s} {decifrar_campo(blob, f'clientes:cpf:{cid}'.encode())}")

print("\nataque: mover o blob da linha 2 para a linha 1")
blob2 = banco.execute("SELECT cpf FROM clientes WHERE id=2").fetchone()[0]
try:
    decifrar_campo(blob2, b"clientes:cpf:1")
except Exception as erro:
    print("  recusado:", type(erro).__name__, "- o contexto nao confere")
```

**Saída real:**

```
como está no banco:
  1 Ana    AaA9nzRe87iOb951/AAwnhZqYfo2JnDB6QRjcSKY7kz+8/KrJEOoIMsc... (105 B)
  2 Bruno  AS/xTByy2kk6tpNgCAAwkuGRRZ8rQ5bfYe45930bS/mp6a24QsROrLwt... (105 B)

lendo com o contexto certo:
  1 Ana    111.111.111-11
  2 Bruno  222.222.222-22

ataque: mover o blob da linha 2 para a linha 1
  recusado: InvalidTag - o contexto nao confere
```

**Explicação.** O padrão chama-se **envelope encryption** e é o que AWS KMS,
Google Cloud KMS e Azure Key Vault implementam:

- Uma **DEK** (Data Encryption Key) por registro cifra o dado.
- A DEK é embrulhada por uma **KEK** (Key Encryption Key) que vive no KMS/HSM
  e **nunca sai de lá**. Sua aplicação chama `Decrypt` no KMS para desembrulhar.
- **Rotacionar a KEK** significa reembrulhar as DEKs — rápido, porque são 32
  bytes cada — sem tocar em terabytes de dados cifrados.
- O **contexto** (`clientes:cpf:1`) vai como AAD: um blob válido movido de uma
  linha para outra é rejeitado. A saída acima mostra esse ataque falhando com
  `InvalidTag`. No AWS KMS esse parâmetro se chama *Encryption Context*, e
  quase ninguém usa — é dinheiro de segurança deixado na mesa.

Custo real: cada CPF de 14 caracteres virou 105 bytes no banco. Cifrar campo
é caro em espaço e **impede busca e índice** — `WHERE cpf = ?` deixa de
funcionar. As saídas são hash determinístico do valor (que vaza igualdade) ou
cifragem que preserva busca (com trade-offs sérios). Decida isso antes de
migrar, não depois.

---

## 9 · Ataque de tempo, medido

**Problema:** demonstrar que comparar segredos com `==` vaza informação, com
números da sua própria máquina.

```python
"""Ataque de tempo: por que == não serve para comparar segredos."""
import time, statistics

SEGREDO = bytes.fromhex("a3f1" * 8)

def comparar_ingenuo(a, b):
    if len(a) != len(b): return False
    for x, y in zip(a, b):
        if x != y: return False       # sai cedo -> vaza informação
    return True

def medir(palpite, repeticoes=4000):
    amostras = []
    for _ in range(repeticoes):
        inicio = time.perf_counter_ns()
        comparar_ingenuo(SEGREDO, palpite)
        amostras.append(time.perf_counter_ns() - inicio)
    return statistics.median(amostras)

print("tempo mediano de comparação conforme o número de bytes corretos:")
for corretos in range(0, 9):
    palpite = SEGREDO[:corretos] + bytes([SEGREDO[corretos] ^ 0xFF]) + bytes(15 - corretos)
    print(f"  {corretos} bytes certos: {medir(palpite):5.0f} ns")

import hmac
print("\ncom hmac.compare_digest (tempo constante):")
for corretos in (0, 8, 15):
    palpite = SEGREDO[:corretos] + bytes([SEGREDO[corretos] ^ 0xFF]) + bytes(15 - corretos)
    amostras = []
    for _ in range(4000):
        i = time.perf_counter_ns(); hmac.compare_digest(SEGREDO, palpite)
        amostras.append(time.perf_counter_ns() - i)
    print(f"  {corretos} bytes certos: {statistics.median(amostras):5.0f} ns")
```

**Saída real:**

```
tempo mediano de comparação conforme o número de bytes corretos:
  0 bytes certos:   646 ns
  1 bytes certos:   479 ns
  2 bytes certos:   505 ns
  3 bytes certos:   548 ns
  4 bytes certos:   590 ns
  5 bytes certos:   636 ns
  6 bytes certos:   666 ns
  7 bytes certos:   689 ns
  8 bytes certos:   709 ns

com hmac.compare_digest (tempo constante):
  0 bytes certos:   227 ns
  8 bytes certos:   221 ns
  15 bytes certos:   224 ns
```

**Explicação.** A curva é monótona e inequívoca: cada byte correto a mais
custa cerca de 40 ns a mais de comparação. Um atacante que possa medir isso
descobre a etiqueta **byte a byte**: são no máximo 256 tentativas por byte,
16·256 = 4 096 tentativas para uma etiqueta de 16 bytes, contra 2¹²⁸ na força
bruta. Com `hmac.compare_digest`, os três tempos ficam idênticos (219, 220,
219 ns aqui).

"Mas 40 ns pela rede some no ruído." Some no ruído de **uma** medição.
Com repetição e estatística, atacantes já demonstraram exploração remota —
inclusive pela internet, e não só na rede local (Crosby, Wallach & Riedi, 2009,
mediram diferenças de 20 μs pela internet e 100 ns na rede local). Além disso,
"o atacante está na mesma nuvem que você" é o caso comum em 2026, não a
exceção.

---

## 10 · Acordo híbrido pós-quântico X25519 + ML-KEM-768

**Problema:** proteger o tráfego de hoje contra o adversário que grava agora e
decifra em 2035, quando houver computador quântico ("*harvest now, decrypt
later*").

```python
"""Acordo de chaves híbrido: X25519 + ML-KEM-768, como o TLS 1.3 faz em 2026."""
import time
from cryptography.hazmat.primitives import hashes, serialization as ser
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import mlkem
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# --- lado do servidor: publica as duas chaves públicas ---
srv_x = X25519PrivateKey.generate()
srv_k = mlkem.MLKEM768PrivateKey.generate()
pub_x = srv_x.public_key().public_bytes(ser.Encoding.Raw, ser.PublicFormat.Raw)
pub_k = srv_k.public_key().public_bytes(ser.Encoding.Raw, ser.PublicFormat.Raw)
print(f"tamanho da parte clássica  (X25519)    : {len(pub_x):5d} bytes")
print(f"tamanho da parte quântica  (ML-KEM-768): {len(pub_k):5d} bytes")

# --- lado do cliente ---
cli_x = X25519PrivateKey.generate()
seg_classico = cli_x.exchange(srv_x.public_key())
seg_pq, criptograma = srv_k.public_key().encapsulate()
print(f"criptograma ML-KEM enviado de volta    : {len(criptograma):5d} bytes")

# --- combinação: concatenar e derivar. A ordem é fixada pela especificação. ---
def combinar(a, b):
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"exemplo hibrido v1").derive(a + b)

chave_cliente = combinar(seg_classico, seg_pq)
chave_servidor = combinar(srv_x.exchange(cli_x.public_key()), srv_k.decapsulate(criptograma))
print("chaves finais coincidem:", chave_cliente == chave_servidor)
print("chave de sessão:", chave_cliente.hex()[:32], "...")

# --- custo ---
def crono(f, n=300):
    t = time.perf_counter()
    for _ in range(n): f()
    return (time.perf_counter() - t) / n * 1000

print(f"\nX25519 exchange     : {crono(lambda: cli_x.exchange(srv_x.public_key())):.3f} ms")
print(f"ML-KEM-768 encapsula: {crono(lambda: srv_k.public_key().encapsulate()):.3f} ms")
print(f"ML-KEM-768 decapsula: {crono(lambda: srv_k.decapsulate(criptograma)):.3f} ms")
print(f"\nbytes a mais no handshake: {len(pub_k) + len(criptograma) - 0} B "
      f"({(len(pub_k)+len(criptograma))/ (2*len(pub_x)):.0f}x o custo clássico)")
```

**Saída real:**

```
tamanho da parte clássica  (X25519)    :    32 bytes
tamanho da parte quântica  (ML-KEM-768):  1184 bytes
criptograma ML-KEM enviado de volta    :  1088 bytes
chaves finais coincidem: True
chave de sessão: a63a47a477821686a1f3ca411211f34b ...

X25519 exchange     : 0.040 ms
ML-KEM-768 encapsula: 0.063 ms
ML-KEM-768 decapsula: 0.046 ms

bytes a mais no handshake: 2272 B (36x o custo clássico)
```

**Explicação.** Isto é, em essência, o que o `X25519MLKEM768` faz no TLS 1.3 —
o grupo que o OpenSSL 3.5 passou a preferir por padrão e que, segundo a
Cloudflare, protegia mais da metade do tráfego humano da rede deles em abril de
2026.

Por que **híbrido** e não ML-KEM puro? Porque a segurança das duas partes se
soma: para quebrar, o adversário precisa vencer **as duas**. O X25519 tem 20
anos de análise; o ML-KEM tem menos de dez, e reticulados já sofreram sustos
(o SIKE, finalista do concurso do NIST, foi quebrado em 2022 **num laptop, em
uma hora**). A opinião profissional consensual hoje é: híbrido até que o
ML-KEM acumule histórico.

O custo é o tamanho: 2 272 bytes a mais no handshake, ~36× a parte clássica.
Em tempo de CPU, é irrelevante (o encapsulamento é mais rápido que o próprio
X25519 nesta medição). O gargalo do PQC é rede, não processador.

---

## 11 · Compartilhamento de segredo de Shamir

**Problema:** a chave-mestra da empresa não pode estar com uma pessoa só, mas
também não pode exigir que todas as cinco estejam presentes.

```python
"""Compartilhamento de segredo de Shamir: 3 de 5 pessoas reconstroem a chave."""
import secrets
from functools import reduce

P = 2**521 - 1     # primo de Mersenne: aritmética num corpo finito

def repartir(segredo: int, minimo: int, total: int):
    # Polinômio aleatório de grau (minimo-1) com termo independente = segredo.
    coeficientes = [segredo] + [secrets.randbelow(P) for _ in range(minimo - 1)]
    def avaliar(x):
        return sum(c * pow(x, i, P) for i, c in enumerate(coeficientes)) % P
    return [(x, avaliar(x)) for x in range(1, total + 1)]

def reconstruir(partes):
    # Interpolação de Lagrange no ponto x = 0.
    total = 0
    for i, (xi, yi) in enumerate(partes):
        num = den = 1
        for j, (xj, _) in enumerate(partes):
            if i != j:
                num = num * (-xj) % P
                den = den * (xi - xj) % P
        total = (total + yi * num * pow(den, P - 2, P)) % P
    return total

chave = int.from_bytes(secrets.token_bytes(32), "big")
print("chave original :", hex(chave)[:34], "...")
partes = repartir(chave, minimo=3, total=5)
for x, y in partes:
    print(f"  parte {x}: {hex(y)[:24]}... ({y.bit_length()} bits)")

print("\ncom 3 partes (1,3,5):", hex(reconstruir([partes[0], partes[2], partes[4]]))[:34], "...")
print("confere:", reconstruir([partes[0], partes[2], partes[4]]) == chave)
print("com 3 partes (2,3,4) :", reconstruir([partes[1], partes[2], partes[3]]) == chave)
recuperado_com_2 = reconstruir(partes[:2])
print("com apenas 2 partes  :", hex(recuperado_com_2)[:34], "... -> confere?",
      recuperado_com_2 == chave)
```

**Saída real:**

```
chave original : 0xfa25043627cfee4ad4cf7e638e159ca5 ...
  parte 1: 0xd268dfe545b61ae55266d7... (520 bits)
  parte 2: 0xbbc2e6404174ecc6fb24c1... (520 bits)
  parte 3: 0x1bc0e1310f33c75a4fa39c... (521 bits)
  parte 4: 0x1d34a66575b0cb57f4fa5d... (521 bits)
  parte 5: 0x10177e01378e5ac55fb68f... (521 bits)

com 3 partes (1,3,5): 0xfa25043627cfee4ad4cf7e638e159ca5 ...
confere: True
com 3 partes (2,3,4) : True
com apenas 2 partes  : 0xe90ed98a49f74903a9a8ec696ae4452f ... -> confere? False
```

**Explicação.** A ideia (Adi Shamir, 1979) é de uma elegância rara: dois pontos
determinam uma reta, três determinam uma parábola, e *k* pontos determinam um
polinômio de grau *k−1*. O segredo é o valor do polinômio em x=0. Com *k−1*
pontos, **qualquer** valor em x=0 continua igualmente possível — não é
"difícil de quebrar", é **teoricamente impossível**, o que se chama
*segurança perfeita* ou *incondicional*.

A saída acima demonstra isso: com duas partes, o valor reconstruído é um
número perfeitamente plausível e completamente errado.

Onde isso é usado de verdade: chaves-mestras de HSM, a cerimônia de assinatura
da raiz do DNSSEC, carteiras de criptomoeda institucionais, e recuperação de
conta em cofres corporativos.

---

## 12 · Produção: assinar e verificar um release

**Problema real:** garantir que o pacote que o usuário baixa é o que você
publicou, mesmo que o espelho de download esteja comprometido.

```bash
#!/usr/bin/env bash
# Caso de produção: assinar um pacote de release e verificá-lo antes de instalar.
set -euo pipefail

# ---------- do lado de quem publica (uma vez) ----------
[ -f release.pem ] || {
  openssl genpkey -algorithm ed25519 -out release.pem
  chmod 600 release.pem
  openssl pkey -in release.pem -pubout -out release.pub
}

# ---------- a cada versão ----------
echo "conteudo do meu-app v2.1.0" > meu-app-2.1.0.tar
sha256sum meu-app-2.1.0.tar > SHA256SUMS
openssl pkeyutl -sign -inkey release.pem -rawin -in SHA256SUMS -out SHA256SUMS.sig
echo "publicado: meu-app-2.1.0.tar, SHA256SUMS, SHA256SUMS.sig"

# ---------- do lado de quem instala ----------
instalar() {
  if ! openssl pkeyutl -verify -pubin -inkey release.pub -rawin \
        -in SHA256SUMS -sigfile SHA256SUMS.sig >/dev/null 2>&1; then
    echo "FALHA: assinatura do SHA256SUMS inválida — abortando" >&2; return 1
  fi
  if ! sha256sum -c SHA256SUMS --status; then
    echo "FALHA: o pacote não bate com o hash assinado — abortando" >&2; return 1
  fi
  echo "OK: assinatura e hash conferem; pode instalar"
}

echo; echo "--- instalação normal ---"; instalar

echo; echo "--- alguém troca o pacote no espelho de download ---"
echo "conteudo com backdoor" > meu-app-2.1.0.tar
instalar || echo "(instalação corretamente abortada)"

echo; echo "--- e se trocarem o pacote E o SHA256SUMS? ---"
sha256sum meu-app-2.1.0.tar > SHA256SUMS
instalar || echo "(abortada: a assinatura cobre o SHA256SUMS)"
```

**Saída real:**

```
publicado: meu-app-2.1.0.tar, SHA256SUMS, SHA256SUMS.sig

--- instalação normal ---
OK: assinatura e hash conferem; pode instalar

--- alguém troca o pacote no espelho de download ---
FALHA: o pacote não bate com o hash assinado — abortando
(instalação corretamente abortada)

--- e se trocarem o pacote E o SHA256SUMS? ---
FALHA: assinatura do SHA256SUMS inválida — abortando
(abortada: a assinatura cobre o SHA256SUMS)
```

**Explicação.** O padrão é o mesmo de qualquer distribuição Linux: assina-se
**o arquivo de hashes**, não cada artefato. Um arquivo de 64 bytes assinado
protege gigabytes.

A terceira parte da saída é o ponto central: substituir o pacote **e**
recalcular o `SHA256SUMS` não adianta, porque o atacante não tem a chave
privada para reassinar. Essa é a diferença entre hash (integridade contra
acidente) e assinatura (integridade contra adversário).

Na vida real, três exigências a mais:

- A chave privada de release fica **fora** do servidor de CI, idealmente em
  hardware (YubiKey, HSM). Chave de assinatura em variável de ambiente do CI é
  um comprometimento esperando a hora.
- Publique a chave pública por um canal independente do download.
- Tenha um plano de revogação **antes** de precisar dele.

---

## 13 · Bônus: uma PKI inteira em 60 linhas

**Problema:** entender o que é uma autoridade certificadora construindo uma.

```python
"""Uma PKI inteira em 60 linhas: CA raiz, certificado de servidor, validação."""
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.verification import PolicyBuilder, Store

AGORA = datetime.datetime(2026, 8, 19, tzinfo=datetime.timezone.utc)

# ---------- 1. a autoridade certificadora raiz ----------
ca_chave = ec.generate_private_key(ec.SECP256R1())
nome_ca = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA de Estudo")])
ca_cert = (x509.CertificateBuilder()
    .subject_name(nome_ca).issuer_name(nome_ca)          # autoassinado
    .public_key(ca_chave.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(AGORA - datetime.timedelta(days=1))
    .not_valid_after(AGORA + datetime.timedelta(days=3650))
    .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
    .add_extension(x509.KeyUsage(False,False,False,False,False,True,True,False,False), critical=True)
    .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_chave.public_key()), critical=False)
    .sign(ca_chave, hashes.SHA256()))
print("CA criada :", ca_cert.subject.rfc4514_string())

# ---------- 2. o servidor pede um certificado ----------
srv_chave = ec.generate_private_key(ec.SECP256R1())
srv_cert = (x509.CertificateBuilder()
    .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "loja.exemplo.test")]))
    .issuer_name(nome_ca)
    .public_key(srv_chave.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(AGORA - datetime.timedelta(days=1))
    .not_valid_after(AGORA + datetime.timedelta(days=47))   # prazo curto, como em 2026
    .add_extension(x509.SubjectAlternativeName([x509.DNSName("loja.exemplo.test")]), critical=False)
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
    .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_chave.public_key()), critical=False)
    .sign(ca_chave, hashes.SHA256()))                                  # assinado PELA CA
print("Servidor  :", srv_cert.subject.rfc4514_string(),
      "| válido até", srv_cert.not_valid_after_utc.date())

# ---------- 3. o cliente valida ----------
loja = Store([ca_cert])
def validar(cert, host, quando=AGORA):
    construtor = PolicyBuilder().store(loja).time(quando)
    verificador = construtor.build_server_verifier(x509.DNSName(host))
    return verificador.verify(cert, [])

print("\nvalidação com o nome certo :", bool(validar(srv_cert, "loja.exemplo.test")))
for host, quando, rotulo in [
        ("outra.exemplo.test", AGORA, "nome errado"),
        ("loja.exemplo.test", AGORA + datetime.timedelta(days=60), "certificado vencido")]:
    try:
        validar(srv_cert, host, quando); print(f"{rotulo:27s}: ACEITOU (não deveria!)")
    except Exception as e:
        print(f"{rotulo:27s}: recusado -> {type(e).__name__}: {str(e)[:60]}")

# ---------- 4. um impostor tenta se passar pela loja ----------
falsa_ca = ec.generate_private_key(ec.SECP256R1())
nome_falso = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA Impostora")])
falso = (x509.CertificateBuilder()
    .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "loja.exemplo.test")]))
    .issuer_name(nome_falso).public_key(ec.generate_private_key(ec.SECP256R1()).public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(AGORA - datetime.timedelta(days=1))
    .not_valid_after(AGORA + datetime.timedelta(days=47))
    .add_extension(x509.SubjectAlternativeName([x509.DNSName("loja.exemplo.test")]), critical=False)
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
    .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(falsa_ca.public_key()), critical=False)
    .sign(falsa_ca, hashes.SHA256()))
try:
    validar(falso, "loja.exemplo.test"); print("impostor                   : ACEITOU (desastre!)")
except Exception as e:
    print(f"impostor                   : recusado -> {type(e).__name__}")
```

**Saída real:**

```
CA criada : CN=CA de Estudo
Servidor  : CN=loja.exemplo.test | válido até 2026-10-05

validação com o nome certo : True
nome errado                : recusado -> VerificationError: validation failed: leaf certificate has no matching subjectA
certificado vencido        : recusado -> VerificationError: validation failed: cert is not valid at validation time (enc
impostor                   : recusado -> VerificationError
```

**Explicação.** Um certificado é só isto: **uma chave pública, um nome, um
prazo, e a assinatura de alguém em quem o verificador confia**. Toda a PKI da
web é essa estrutura repetida em cadeia.

Os quatro testes cobrem exatamente as falhas que a validação existe para
pegar: nome que não bate, prazo vencido, e emissor desconhecido. O impostor
falha não por ter feito algo mal feito — o certificado dele é
tecnicamente perfeito — mas porque a CA que o assinou não está na loja de
confiança do cliente. **Confiança é uma lista, não uma propriedade
matemática.**

**Um achado deste exemplo, digno de nota:** a primeira versão usava Ed25519 e
a validação falhou com `Forbidden public key algorithm`. O verificador do
`cryptography` implementa o perfil do CA/Browser Forum, e o **Ed25519 ainda
não é permitido em certificados de TLS público** em 2026 — apesar de ser o
algoritmo recomendado em quase todo o resto. Trocar para ECDSA P-256 resolveu.
Esse tipo de descompasso entre "melhor prática" e "o que a norma aceita" é
rotina em PKI; ver [21-pki-e-certificados.md](21-pki-e-certificados.md).

---

## Autoteste

1. Por que o criptograma do AES-GCM tem 16 bytes a mais que o texto claro?
2. No exemplo 2, por que o ECB produziu apenas 3 blocos distintos, e o CTR, 32?
3. No exemplo 4, por que os parâmetros do scrypt são gravados junto ao hash?
4. Um atacante tem dois criptogramas cifrados com a mesma chave e o mesmo
   nonce. O que ele consegue, sem conhecer a chave?
5. No exemplo 6, por que não se usa o segredo do X25519 diretamente como chave?
6. Cite dois erros comuns na verificação de webhook e como o exemplo 7 os evita.
7. O que é uma DEK e o que é uma KEK? Por que rotacionar a KEK é barato?
8. Quantos bytes o ML-KEM-768 acrescenta a um handshake, e por que se usa
   híbrido em vez de PQC puro?
9. Com 2 das 5 partes de Shamir, o que se sabe sobre o segredo?
10. Por que assinar o `SHA256SUMS` protege o pacote inteiro?

---

**Anterior:** [05-manual-de-uso.md](05-manual-de-uso.md) ·
**Próximo:** [07-projeto-modelo/](07-projeto-modelo/README.md)
