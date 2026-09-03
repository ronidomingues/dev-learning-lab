# 05 · Manual de uso — referência por tarefa

**Nível:** iniciante a intermediário · **Última atualização:** 19/08/2026
**Testado em:** OpenSSL 3.0.2, GnuPG 2.2.27, age v1.3.1, Python 3.10.12 (Ubuntu 22.04.5)

Organizado por **o que você quer fazer**, não por ordem alfabética. Use o
índice, copie o comando, leia a coluna "cuidado".

## Índice

- [A. Escolher o algoritmo certo](#a-escolher-o-algoritmo-certo-a-tabela-que-resolve-90-das-dúvidas)
- [B. Aleatoriedade](#b-aleatoriedade)
- [C. Hash e resumo](#c-hash-e-resumo)
- [D. Senhas](#d-senhas)
- [E. Cifrar e decifrar arquivos](#e-cifrar-e-decifrar-arquivos)
- [F. Chaves assimétricas](#f-chaves-assimétricas)
- [G. Assinar e verificar](#g-assinar-e-verificar)
- [H. Certificados e TLS](#h-certificados-e-tls)
- [I. GnuPG do começo ao fim](#i-gnupg-do-começo-ao-fim)
- [J. Python — receituário mínimo](#j-python--receituário-mínimo)
- [K. Obsoleto: o que não usar mais](#k-obsoleto-o-que-não-usar-mais)
- [L. Atalhos de quem usa há anos](#l-atalhos-de-quem-usa-há-anos)

---

## A. Escolher o algoritmo certo (a tabela que resolve 90% das dúvidas)

| Preciso... | Use | Não use |
|---|---|---|
| Cifrar dados com chave compartilhada | **AES-256-GCM** ou **ChaCha20-Poly1305** | AES-CBC sozinho, AES-ECB, RC4, DES, 3DES |
| Cifrar arquivo grande em disco | **age** ou AES-GCM em blocos com nonce por bloco | GCM num único fluxo acima de 64 GiB |
| Hash de propósito geral | **SHA-256**, SHA-512 ou **BLAKE2b/BLAKE3** | MD5, SHA-1 |
| Guardar senha | **Argon2id**, **scrypt** ou **bcrypt** | SHA-256, mesmo "com sal"; MD5 |
| Derivar chave de um segredo forte | **HKDF-SHA256** | usar o segredo diretamente |
| Autenticar mensagem com chave compartilhada | **HMAC-SHA256** ou o próprio AEAD | "hash da chave + mensagem" |
| Assinatura digital | **Ed25519**; **ECDSA P-256** se exigido por norma | RSA-1024, DSA, ECDSA com nonce previsível |
| Acordo de chaves | **X25519** | Diffie-Hellman clássico com primo < 2048 bits |
| Assinatura resistente a quântico | **ML-DSA-65** (FIPS 204) ou SLH-DSA | esperar 2035 |
| Acordo resistente a quântico | **X25519MLKEM768** (híbrido) | ML-KEM puro, sem componente clássica |

Regra geral: **prefira AEAD** (cifragem autenticada) a qualquer combinação
manual de cifra + MAC. Se você está escolhendo modo de operação na mão, pare e
pergunte por quê ([13-modos-e-aead.md](13-modos-e-aead.md)).

---

## B. Aleatoriedade

| Tarefa | Comando |
|---|---|
| 16 bytes em hexadecimal | `openssl rand -hex 16` |
| 32 bytes em Base64 | `openssl rand -base64 32` |
| Arquivo de 1 MiB aleatório | `openssl rand -out ruido.bin 1048576` |
| Em Python | `secrets.token_bytes(32)` · `secrets.token_hex(16)` · `secrets.token_urlsafe(32)` |
| Senha aleatória de 20 caracteres | `openssl rand -base64 15` |
| Ler o CSPRNG do kernel direto | `head -c 32 /dev/urandom \| xxd` |

**Cuidado:** `/dev/random` e `/dev/urandom` são equivalentes no Linux moderno
(desde o kernel 5.6, e definitivamente desde o 5.18). A ideia de que
`/dev/random` é "mais seguro" é folclore de 2005 que sobrevive em tutoriais.
Em Python, `random` **não serve**; `secrets` e `os.urandom` servem.

---

## C. Hash e resumo

| Tarefa | Comando |
|---|---|
| SHA-256 de um arquivo | `sha256sum arquivo` |
| SHA-256 de um texto, sem quebra de linha | `echo -n "texto" \| sha256sum` |
| SHA-512, BLAKE2 | `sha512sum arquivo` · `b2sum arquivo` |
| Via OpenSSL | `openssl dgst -sha256 arquivo` |
| Conferir uma lista de hashes | `sha256sum -c SHASUMS256.txt` |
| Em Python | `hashlib.sha256(b"dados").hexdigest()` |
| Hash de arquivo grande, sem carregar na RAM | `hashlib.file_digest(open("f","rb"), "sha256")` (3.11+) |

**Comparação de desempenho medida nesta máquina (19/08/2026, i3-10100T):**
SHA-256 a 406 MiB/s; BLAKE2b a 541 MiB/s. Em CPUs com extensões SHA-NI a
diferença se inverte.

**Cuidado:** hash **não** é criptografia — não tem chave e não há o que
decifrar. "Descriptografar um MD5" é impossível no sentido literal; o que se
faz é adivinhar a entrada e comparar.

---

## D. Senhas

| Tarefa | Comando |
|---|---|
| Hash de senha no formato do `/etc/shadow` (yescrypt/SHA-512) | `openssl passwd -6 senha` |
| Argon2id em Python | `pip install argon2-cffi` → `PasswordHasher().hash("senha")` |
| scrypt em Python (stdlib) | `hashlib.scrypt(b"senha", salt=os.urandom(16), n=2**15, r=8, p=1, maxmem=128*1024*1024, dklen=32)` |
| bcrypt em Python | `pip install bcrypt` → `bcrypt.hashpw(senha, bcrypt.gensalt(12))` |
| Verificar sem vazar tempo | `hmac.compare_digest(a, b)` |

Saída real de `openssl passwd -6 -salt abcdefgh senha123`:

```
$6$abcdefgh$.8KK0VIa8Y1pYzj8zjjDgwJjGUnaeddDMDM2JBB0eiVxHt.18CmokxU63XgCMtbd4qWca4sTEcKYrs0R39sre/
```

Leia o formato: `$6$` = SHA-512-crypt, `abcdefgh` = sal, o resto = o hash.
**Nunca** passe a senha real como argumento (aparece em `ps`); em produção,
leia da entrada padrão.

---

## E. Cifrar e decifrar arquivos

### Com `age` (recomendado)

| Tarefa | Comando |
|---|---|
| Gerar par de chaves | `age-keygen -o minha.age` |
| Ver a pública de uma privada | `age-keygen -y minha.age` |
| Cifrar para uma chave pública | `age -r age1... -o s.age s.txt` |
| Cifrar para vários destinatários | `age -r age1abc... -r age1def... -o s.age s.txt` |
| Cifrar com senha | `age -p -o s.age s.txt` |
| Saída em texto (para colar em e-mail) | `age -a -r age1... s.txt` |
| Decifrar | `age -d -i minha.age s.age` |
| Cifrar uma pasta inteira | `tar czf - pasta/ \| age -r age1... -o pasta.tar.gz.age` |
| Usar sua chave SSH como destinatário | `age -R ~/.ssh/id_ed25519.pub -o s.age s.txt` |

O `age` **não tem** opção para escolher algoritmo, tamanho de chave ou modo.
Isso é a característica principal do projeto, não uma limitação: cada opção é
uma chance de errar.

### Com OpenSSL (quando `age` não está disponível)

```bash
openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -in claro.txt -out cifrado.bin
openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -in cifrado.bin -out claro.txt
```

**Três avisos sobre `openssl enc`:**

1. **Sempre** inclua `-pbkdf2 -iter 600000`. Sem isso, versões antigas usam uma
   derivação de chave de 1996 com **uma única** iteração de MD5 — quebrável
   por dicionário em segundos.
2. `-aes-256-cbc` **não autentica**. O arquivo pode ser adulterado sem que a
   decifragem acuse. Para autenticação, use `age`.
3. `openssl enc` não suporta AES-GCM de forma utilizável na linha de comando.
   Se você precisa de AEAD aqui, é sinal de que a ferramenta é a errada.

---

## F. Chaves assimétricas

| Tarefa | Comando |
|---|---|
| Ed25519 (padrão para assinar) | `openssl genpkey -algorithm ed25519 -out chave.pem` |
| X25519 (para acordo de chaves) | `openssl genpkey -algorithm x25519 -out acordo.pem` |
| ECDSA P-256 | `openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out ec.pem` |
| RSA 3072 | `openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out rsa.pem` |
| Extrair a pública | `openssl pkey -in chave.pem -pubout -out publica.pem` |
| Inspecionar | `openssl pkey -in chave.pem -noout -text` |
| Proteger a privada com senha | `openssl pkcs8 -topk8 -in chave.pem -out chave-protegida.pem` |
| Chave SSH Ed25519 | `ssh-keygen -t ed25519 -C "voce@maquina"` |
| Permissão obrigatória | `chmod 600 chave.pem` |

Tamanhos equivalentes de segurança (NIST SP 800-57, tabela clássica):

| Segurança | Simétrico | RSA / DH | Curva elíptica |
|---|---|---|---|
| 112 bits | 3DES (obsoleto) | 2048 | 224 |
| **128 bits** | **AES-128** | **3072** | **256** (P-256, X25519) |
| 192 bits | AES-192 | 7680 | 384 |
| 256 bits | AES-256 | 15360 | 512 (P-521) |

É por isso que ninguém usa RSA-15360: a chave ficaria com 2 KB e a assinatura
seria ~50× mais lenta que uma curva equivalente.

---

## G. Assinar e verificar

### Ed25519 (assina o conteúdo bruto, sem hash prévio)

```bash
openssl pkeyutl -sign   -inkey chave.pem  -rawin -in doc.txt -out doc.sig
openssl pkeyutl -verify -pubin -inkey publica.pem -rawin -in doc.txt -sigfile doc.sig
# saída esperada: Signature Verified Successfully
```

### ECDSA e RSA (assinam o hash)

```bash
openssl dgst -sha256 -sign   ec.pem    -out doc.sig doc.txt
openssl dgst -sha256 -verify ecpub.pem -signature doc.sig doc.txt
# saída esperada: Verified OK
```

**Cuidado:** `-rawin` é para Ed25519/Ed448 (que fazem o hash internamente).
Usar `dgst -sign` com Ed25519 gera erro; usar `pkeyutl -rawin` com RSA
também. A mensagem de erro do OpenSSL nesse caso é críptica — se aparecer
algo sobre "operation not supported", é quase sempre esse par trocado.

**Sempre verifique o código de saída em script:**

```bash
if openssl dgst -sha256 -verify pub.pem -signature doc.sig doc.txt > /dev/null 2>&1; then
    echo "assinatura válida"
else
    echo "ASSINATURA INVÁLIDA — não use este arquivo" >&2; exit 1
fi
```

---

## H. Certificados e TLS

| Tarefa | Comando |
|---|---|
| Certificado autoassinado para teste | `openssl req -x509 -newkey ed25519 -keyout k.pem -out c.crt -days 30 -nodes -subj "/CN=exemplo.local"` |
| Ver conteúdo de um certificado | `openssl x509 -in c.crt -noout -text` |
| Só o essencial | `openssl x509 -in c.crt -noout -subject -issuer -dates` |
| Gerar uma CSR | `openssl req -new -key k.pem -out pedido.csr -subj "/CN=exemplo.com"` |
| Ver a CSR | `openssl req -in pedido.csr -noout -text -verify` |
| Baixar o certificado de um site | `openssl s_client -connect site:443 -servername site </dev/null 2>/dev/null \| openssl x509 -out site.crt` |
| Testar TLS de um servidor | `openssl s_client -connect site:443 -tls1_3` |
| Ver a cadeia inteira | `openssl s_client -connect site:443 -showcerts` |
| Verificar cadeia local | `openssl verify -CAfile ca.crt servidor.crt` |
| Ver detalhes pelo curl (funciona atrás de proxy) | `curl -v https://site 2>&1 \| grep -E "SSL connection\|subject:\|issuer:\|expire"` |
| Servidor TLS de brinquedo | `openssl s_server -accept 4433 -cert c.crt -key k.pem -www` |
| Ver o que o cliente propõe | `openssl s_client -connect site:443 -msg` |

Saída real de `openssl x509 -noout -subject -issuer -dates` num certificado
autoassinado criado para este manual:

```
subject=CN = CA de teste
issuer=CN = CA de teste
notBefore=Aug 19 17:28:04 2026 GMT
notAfter=Sep 18 17:28:04 2026 GMT
```

Quando `subject` e `issuer` são iguais, o certificado é **autoassinado** —
por definição, uma raiz ou um certificado de teste.

**Cuidado com o `-servername`:** sem ele, servidores com muitos sites por IP
(quase todos) entregam o certificado errado. É o SNI (*Server Name
Indication*), e esquecê-lo é a causa nº 1 de "o `s_client` mostra um
certificado diferente do que o navegador mostra".

---

## I. GnuPG do começo ao fim

O GPG tem fama de difícil e a fama é merecida: são 30 anos de opções
acumuladas. Este é o caminho curto que funciona.

| Tarefa | Comando |
|---|---|
| Gerar chave moderna (Ed25519) | `gpg --quick-generate-key "Seu Nome <voce@dominio>" ed25519 sign,cert 2y` |
| Acrescentar subchave de cifragem | `gpg --quick-add-key <FPR> cv25519 encr 2y` |
| Listar chaves | `gpg --list-keys --keyid-format=long` |
| Ver a impressão digital | `gpg --fingerprint voce@dominio` |
| Exportar a pública | `gpg --armor --export voce@dominio > minha-publica.asc` |
| Importar a de alguém | `gpg --import dele.asc` |
| Assinar deixando o texto legível | `gpg --clearsign doc.txt` |
| Assinatura em arquivo separado | `gpg --detach-sign --armor doc.txt` |
| Verificar | `gpg --verify doc.txt.asc` |
| Cifrar para alguém | `gpg --encrypt -r dele@dominio -o doc.gpg doc.txt` |
| Cifrar e assinar | `gpg --encrypt --sign -r dele@dominio doc.txt` |
| Decifrar | `gpg --decrypt doc.gpg` |
| Cifrar só com senha | `gpg --symmetric --cipher-algo AES256 doc.txt` |
| Fazer cópia de segurança de tudo | `tar czf gnupg-backup.tar.gz -C ~ .gnupg` |
| Gerar certificado de revogação | `gpg --gen-revoke <FPR> > revogar.asc` |

Saída real de uma verificação bem-sucedida (locale em português):

```
gpg: Assinatura feita qua 19 ago 2026 14:28:19 -03
gpg:                usando EDDSA chave 0D75024DFB54B11772EFEFC23D0B3B17E2815F93
gpg: Assinatura correta de "Teste Curso <teste@exemplo.org>" [final]
```

**Três coisas que confundem todo mundo no GPG:**

1. **`[final]`, `[desconhecido]`, `[não confiável]`** falam da confiança que
   *você* atribuiu ao dono, não da validade matemática da assinatura. Uma
   assinatura pode ser matematicamente correta e vir de uma chave em que você
   não confia. São duas perguntas diferentes.
2. **Gere o certificado de revogação hoje**, e guarde-o fora da máquina. Se
   você perder a chave privada, sem ele não há como avisar ao mundo que a
   chave não vale mais.
3. **`gpg: signing failed: Inappropriate ioctl for device`** significa que o
   `pinentry` não achou terminal. Corrija com `export GPG_TTY=$(tty)` no seu
   perfil.

**Opinião profissional:** para trocar arquivos cifrados hoje, use `age`. Para
assinar *releases* e pacotes, e sempre que houver a exigência de interoperar
com o ecossistema OpenPGP (Debian, Git, Linux distros), use GPG. O GPG carrega
decisões dos anos 1990 — formato complexo, algoritmos negociáveis, ergonomia
hostil — que hoje se resolveriam de outro jeito.

---

## J. Python — receituário mínimo

```python
# ---- cifragem autenticada (o padrão para 90% dos casos) ----
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

chave = AESGCM.generate_key(bit_length=256)   # ou os.urandom(32)
nonce = os.urandom(12)                        # NOVO a cada mensagem, sempre
cifrado = AESGCM(chave).encrypt(nonce, b"mensagem", b"cabecalho-autenticado")
claro = AESGCM(chave).decrypt(nonce, cifrado, b"cabecalho-autenticado")

# ---- hash e HMAC ----
import hashlib, hmac
resumo = hashlib.sha256(b"dados").digest()
etiqueta = hmac.new(chave, b"mensagem", hashlib.sha256).digest()
ok = hmac.compare_digest(etiqueta, etiqueta_recebida)     # nunca use ==

# ---- senha ----
sal = os.urandom(16)
derivada = hashlib.scrypt(b"senha", salt=sal, n=2**15, r=8, p=1,
                          maxmem=128*1024*1024, dklen=32)

# ---- assinatura ----
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
privada = Ed25519PrivateKey.generate()
assinatura = privada.sign(b"documento")
privada.public_key().verify(assinatura, b"documento")     # levanta exceção se falhar

# ---- acordo de chaves ----
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
segredo = a.exchange(b.public_key())                      # == b.exchange(a.public_key())

# ---- derivação a partir do segredo do acordo ----
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
chave_sessao = HKDF(algorithm=hashes.SHA256(), length=32,
                    salt=None, info=b"meu-app v1 sessao").derive(segredo)

# ---- pós-quântico (cryptography >= 46) ----
from cryptography.hazmat.primitives.asymmetric import mlkem, mldsa
k = mlkem.MLKEM768PrivateKey.generate()
segredo, criptograma = k.public_key().encapsulate()       # nesta ordem
assert k.decapsulate(criptograma) == segredo
s = mldsa.MLDSA65PrivateKey.generate()
s.public_key().verify(s.sign(b"msg"), b"msg")
```

Todos os trechos acima foram executados em 19/08/2026 com `cryptography`
50.0.0. Tamanhos medidos do ML-KEM-768: pública 1 184 B, criptograma 1 088 B,
segredo 32 B. ML-DSA-65: pública 1 952 B, assinatura 3 309 B.

**A regra do `nonce`:** ele precisa ser único por chave, não secreto nem
imprevisível. Duas estratégias corretas: 12 bytes aleatórios (seguro até
~2³² mensagens por chave) ou um contador persistente que jamais reinicia.
Nunca zero fixo com chave fixa.

---

## K. Obsoleto: o que não usar mais

| Não use | Desde quando | Use |
|---|---|---|
| **MD5** | colisão prática em 2004; forja de certificado em 2008 | SHA-256, BLAKE2 |
| **SHA-1** | teoricamente quebrado em 2005; colisão real (SHAttered) em 2017; *chosen-prefix* em 2020 | SHA-256 |
| **DES / 3DES** | DES quebrado em 1998 (56 h); 3DES proibido pelo NIST para novos usos desde 2023 (Sweet32) | AES-256 |
| **RC4** | vieses conhecidos desde 2001; proibido no TLS pela RFC 7465 (2015) | ChaCha20 |
| **SSL 2.0/3.0, TLS 1.0/1.1** | POODLE (2014); depreciados pela RFC 8996 (2021) | TLS 1.3, ou 1.2 no mínimo |
| **AES-ECB** | nunca deveria ter sido usado para dados | AES-GCM |
| **RSA PKCS#1 v1.5 para cifrar** | Bleichenbacher, 1998, e ressurgindo até hoje (ROBOT, 2017) | RSA-OAEP, ou melhor: ECIES/HPKE |
| **RSA < 2048 bits** | RSA-768 fatorado em 2009; RSA-829 em 2020 | 3072+ ou curvas |
| **DSA** | tamanhos pequenos, nonce frágil | Ed25519 |
| **`openssl enc` sem `-pbkdf2`** | derivação de 1 iteração de MD5 | `-pbkdf2 -iter 600000`, ou `age` |
| **PGP para e-mail** | opinião: EFAIL (2018) e a complexidade do ecossistema | Signal, ou `age` para arquivos |

---

## L. Atalhos de quem usa há anos

```bash
# Ver certificado de um site em uma linha, incluindo SANs
openssl s_client -connect exemplo.com:443 -servername exemplo.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -dates -ext subjectAltName

# Quantos dias faltam para o certificado vencer
echo | openssl s_client -connect exemplo.com:443 -servername exemplo.com 2>/dev/null \
  | openssl x509 -noout -checkend $((30*86400)) && echo "vale por mais de 30 dias"

# Conferir que uma chave privada corresponde a um certificado (devem bater)
openssl pkey -in chave.pem -pubout | openssl sha256
openssl x509 -in cert.crt -pubkey -noout | openssl sha256

# Converter entre formatos
openssl x509 -in cert.der -inform DER -out cert.pem -outform PEM
openssl pkcs12 -export -out tudo.p12 -inkey chave.pem -in cert.crt   # para Windows/Java

# Ver o que há dentro de qualquer estrutura ASN.1
openssl asn1parse -in cert.pem

# Gerar uma senha decente
openssl rand -base64 24

# Hash de todos os arquivos de uma pasta, com registro para conferir depois
find . -type f -exec sha256sum {} + > INVENTARIO.sha256
sha256sum -c INVENTARIO.sha256 | grep -v OK    # mostra só o que mudou

# Benchmark local do seu processador
openssl speed -evp aes-256-gcm
openssl speed -evp chacha20-poly1305

# Descobrir se seu OpenSSL tem pós-quântico
openssl list -kem-algorithms | grep -i ml-kem
```

**Sobre `openssl speed`:** rode antes de discutir "AES ou ChaCha20". Nesta
máquina (i3-10100T com AES-NI, 19/08/2026): AES-256-GCM a 3 596 MB/s e
ChaCha20-Poly1305 a 1 917 MB/s, em blocos de 16 KiB. Num celular antigo sem
aceleração de AES, a ordem se inverte — e foi exatamente por isso que o Google
levou o ChaCha20 para o TLS em 2014.

---

## Autoteste

1. Qual algoritmo para guardar senha, e por que SHA-256 com sal não serve?
2. Qual a diferença entre `openssl pkeyutl -rawin` e `openssl dgst -sign`, e
   quando usar cada um?
3. O que `-servername` faz no `s_client`, e o que acontece se você esquecer?
4. Por que `openssl enc` sem `-pbkdf2` é perigoso?
5. Uma verificação GPG diz "Assinatura correta" mas a chave aparece como
   `[desconhecido]`. O que isso significa exatamente?
6. Quantos bits de RSA equivalem a uma curva de 256 bits? E qual a
   consequência prática disso?
7. Escreva o comando que mostra os dias restantes de um certificado remoto.
8. Em Python, qual o problema de comparar duas etiquetas HMAC com `==`?
9. Quais tamanhos tem uma chave pública ML-KEM-768 e uma assinatura ML-DSA-65?

---

**Anterior:** [04-como-comecar.md](04-como-comecar.md) ·
**Próximo:** [06-exemplos.md](06-exemplos.md)
