# 14 · A criptografia do TLS, por dentro

**Nível:** avançado · **Data:** 31/08/2026
**Pré-requisito útil:** [criptografia](../criptografia/00-MAPA.md), blocos A e 10.

Sem caixas-pretas: o que cada primitiva faz, por que foi escolhida, e o que acontece
quando é usada errado. Se você só quer configurar TLS, [17](17-configuracao-de-servidores.md)
basta. Este arquivo é para entender **por que** as recomendações são as que são.

---

## 1. As quatro peças

Um handshake TLS combina quatro tipos de primitiva. Confundi-los é a origem de metade
das explicações erradas sobre TLS:

| Peça | Papel | No TLS 1.3 |
|---|---|---|
| **Acordo de chaves** | os dois lados chegam ao mesmo segredo sem transmiti-lo | (EC)DHE: X25519, P-256/384/521, ffdhe*; e agora os híbridos com ML-KEM |
| **Assinatura digital** | o servidor prova que é o dono do certificado | ECDSA, RSA-PSS, RSA-PKCS#1, Ed25519 |
| **Derivação de chaves** | transforma um segredo em várias chaves distintas | HKDF (Extract + Expand) sobre SHA-256/384 |
| **Cifra autenticada (AEAD)** | protege cada registro de dados | AES-GCM, ChaCha20-Poly1305, AES-CCM |

**Nota que evita confusão perpétua:** a criptografia assimétrica (acordo + assinatura)
é usada **só no handshake**, uma vez. Todo o tráfego é protegido pela cifra simétrica.
Assimétrico é caro; simétrico é barato. É por isso que TLS não "custa caro" em regime —
o custo está no *começo* da conexão. Ver [20-desempenho-e-operacao.md](20-desempenho-e-operacao.md).

---

## 2. Acordo de chaves: Diffie–Hellman efêmero

### 2.1 A ideia, com tinta

Whitfield Diffie e Martin Hellman, 1976. A analogia canônica:

1. Você e eu concordamos publicamente numa tinta amarela. Todos veem.
2. Cada um escolhe uma tinta secreta e mistura com a amarela.
3. Trocamos as misturas **em público**. Quem observa vê duas misturas.
4. Cada um mistura a sua tinta secreta com a mistura recebida.
5. Chegamos à **mesma** cor final. O observador não consegue — separar tintas é difícil.

Formalmente, com curvas elípticas:

```
Cliente: sorteia a  (privada)  →  envia  A = a·G   (pública)
Servidor: sorteia b (privada)  →  envia  B = b·G   (pública)

Cliente calcula:  a·B = a·(b·G) = ab·G
Servidor calcula: b·A = b·(a·G) = ab·G     ← o mesmo ponto
```

`G` é um ponto-base público da curva. A dificuldade é o **problema do logaritmo
discreto em curva elíptica**: dado `A` e `G`, achar `a` é inviável classicamente.

### 2.2 Por que **efêmero** (o "E" de ECDHE)

`a` e `b` são sorteados **para aquela conexão** e apagados ao final. Consequência:
mesmo que a chave privada do certificado do servidor vaze anos depois, ela **não
ajuda** a decifrar sessões passadas — ela nunca participou do cálculo do segredo.
Isso é **sigilo futuro** (*forward secrecy*), e é o motivo de o TLS 1.3 ter tornado
o efêmero obrigatório.

Contraste com o que se fazia antes: no RSA-transporte, o cliente sorteava o segredo,
cifrava com a chave pública do servidor e enviava. A chave privada de longo prazo do
servidor decifrava — hoje e daqui a dez anos.

### 2.3 As curvas, e por que X25519 venceu

| Grupo | Bits de segurança | Notas |
|---|---|---|
| **X25519** | ~128 | **preferido**. Projetada por Daniel J. Bernstein (2005); rápida, implementação naturalmente em tempo constante, sem parâmetros suspeitos |
| **secp256r1 (P-256)** | ~128 | padrão NIST, onipresente por compatibilidade; implementar sem canal lateral é mais difícil |
| **secp384r1 (P-384)** | ~192 | exigido por algumas políticas governamentais |
| **X448 / P-521** | ~224/~256 | raros; ganho prático discutível |
| **ffdhe2048–8192** | 112–200 | DH em corpo finito, com grupos **nomeados** (RFC 7919) |
| **X25519MLKEM768** | ~128 clássico **+** resistência quântica | híbrido; padrão de facto em 2026 |

> ### Por que grupos **nomeados** e não parâmetros escolhidos pelo servidor
> Até o TLS 1.2, o servidor podia enviar parâmetros DH arbitrários. Duas consequências
> ruins: *(a)* o cliente não tinha como avaliar se o grupo era forte — e o **Logjam**
> (2015) explorou servidores usando grupos de 512 bits, herança das restrições de
> exportação; *(b)* pior, um punhado de grupos de 1024 bits era compartilhado por
> milhões de servidores, e o pré-cálculo contra **um** grupo (estimado como viável para
> um Estado) quebrava todos eles de uma vez. O TLS 1.3 só admite grupos nomeados de
> uma lista revisada. É o mesmo princípio do §7 de [10](10-fundamentos.md): **remover
> a opção elimina a classe inteira de erro**.

### 2.4 O híbrido pós-quântico

```
segredo_compartilhado = HKDF( X25519(a,B)  ‖  ML-KEM-768.Decaps(...) )
                              └─ clássico ─┘  └── pós-quântico ──┘
```

Ambos entram na derivação. Quebrar exige quebrar **os dois**. Custo: o `ClientHello`
cresce de ~300 bytes para ~1.200–1.700 bytes, o que às vezes ultrapassa um pacote
e revelou *middleboxes* que não lidavam com `ClientHello` fragmentado — mais um
capítulo de ossificação. Estado atual em [65-estado-da-arte.md](65-estado-da-arte.md).

---

## 3. Assinatura digital

| Algoritmo | Tamanho da assinatura | Notas |
|---|---|---|
| **ECDSA P-256** | ~64–72 bytes | rápido; **exige um nonce aleatório único por assinatura** |
| **Ed25519** | 64 bytes | melhor opção técnica: determinístico, sem o risco do nonce; **CAs públicas ainda não emitem** |
| **RSA-PSS 2048** | 256 bytes | preferido sobre PKCS#1 v1.5; obrigatório para assinar o handshake no TLS 1.3 |
| **RSA-PKCS#1 v1.5** | 256 bytes | permitido só em certificados legados; padding com histórico de ataques |

> ### O nonce do ECDSA — a armadilha que já custou uma plataforma inteira
> ECDSA precisa de um valor `k` aleatório, **único e secreto**, por assinatura.
> Se `k` se repetir em duas assinaturas com a mesma chave, **a chave privada é
> recuperável com álgebra de colégio**. Não é um enfraquecimento: é a chave inteira.
> Aconteceu de verdade: em 2010 a Sony usou um `k` **constante** para assinar
> software do PlayStation 3, e o grupo fail0verflow extraiu a chave mestra de
> assinatura do console. Aconteceu de novo, em 2013, em carteiras de Bitcoin em
> Android, por um gerador de aleatoriedade defeituoso.
> **A correção estrutural:** RFC 6979 (ECDSA determinístico, deriva `k` da chave e da
> mensagem) e, melhor ainda, **Ed25519**, que é determinístico por projeto e não
> oferece esse pé em que tropeçar. Este é o argumento central para preferir Ed25519
> onde ele for aceito.

**Por que RSA-PSS e não PKCS#1 v1.5:** o preenchimento PKCS#1 v1.5 rendeu 25 anos de
ataques (Bleichenbacher, 1998; ROBOT, 2017 — a mesma falha ressurgindo em produtos
diferentes). O PSS tem prova de segurança sob hipóteses razoáveis. O TLS 1.3 exige PSS
para assinar o handshake, mesmo quando o certificado é RSA clássico.

---

## 4. Derivação de chaves: HKDF

HKDF (RFC 5869) tem duas etapas com papéis distintos:

```
Extract(sal, material)   →  concentra a entropia num "pseudo-random key" (PRK)
Expand(PRK, rótulo, n)   →  produz n bytes de chave, ligados àquele rótulo
```

**Por que duas etapas, e não simplesmente `SHA256(segredo)`?**

*(1)* O segredo do ECDHE é um **ponto de curva** — não é uniformemente aleatório como
uma sequência de bits; tem estrutura matemática. `Extract` remove essa estrutura.
*(2)* Precisamos de **várias** chaves independentes (handshake e aplicação, cliente e
servidor, exportador, retomada). `Expand` produz cada uma com um rótulo distinto, de
modo que conhecer uma não revele as outras. *(3)* Os rótulos são **strings de contexto**
(`"tls13 c hs traffic"`, `"tls13 s ap traffic"`), o que impede que material derivado
para um propósito seja aceito em outro — a mesma defesa contra confusão de contexto
que aparece no `CertificateVerify` ([12 §3.4](12-handshake.md)).

O escalonamento completo está no [12 §4](12-handshake.md).

---

## 5. AEAD: a cifra que também autentica

### 5.1 O que AEAD resolve

Antes, cifra e autenticação eram construídas separadamente e **combinadas pelo
implementador** — que podia errar a ordem:

| Ordem | Quem usava | Veredito |
|---|---|---|
| **MAC-then-Encrypt** | TLS até 1.2 | ❌ origem de BEAST, Lucky13, POODLE |
| **Encrypt-and-MAC** | SSH | ⚠️ vaza informação sobre o texto claro |
| **Encrypt-then-MAC** | IPsec | ✅ provadamente seguro |
| **AEAD** | TLS 1.3 | ✅✅ uma primitiva única, sem ordem para errar |

O problema do MAC-then-Encrypt: para verificar o MAC, é preciso **decifrar primeiro**.
Ou seja, você processa dados não autenticados — e o tempo que leva para rejeitá-los
vaza informação. Foi exatamente isso o Lucky13.

### 5.2 AES-GCM

AES em modo contador (CTR) para cifrar + GHASH para autenticar, numa construção única.

```
nonce (12 bytes) = IV_estático XOR número_de_sequência
                   └ derivado do handshake ┘   └ contador implícito ┘
saída = ciphertext ‖ tag de 16 bytes
```

**A regra absoluta:** *nunca reutilize um nonce com a mesma chave.* Em GCM, a
reutilização não enfraquece — **destrói**: um atacante que veja dois textos cifrados
com o mesmo nonce recupera a chave de autenticação (a subchave do GHASH) e passa a
**forjar mensagens válidas** à vontade.

Por isso o TLS 1.3 **fixou a construção do nonce** no padrão: IV derivado do handshake
XOR o número de sequência do registro, que é monotônico. Não sobrou escolha para o
implementador. (No TLS 1.2, parte do nonce era escolhida pela implementação, e houve
produtos que geravam nonces repetidos.)

Limite prático: o TLS 1.3 obriga a **rechaveamento** (`KeyUpdate`) antes de aproximar-se
do limite de registros por chave — cerca de 2^24,5 registros para AES-GCM. Em conexões
longuíssimas (streaming, WebSocket persistente) isso acontece de verdade.

### 5.3 ChaCha20-Poly1305

Cifra de fluxo ChaCha20 (Bernstein) + autenticador Poly1305.

**Quando ela vence o AES:** em CPUs **sem instruções AES-NI** — celulares mais simples,
roteadores, IoT, e algumas VMs. Sem aceleração de hardware, o AES em software é lento
**e** difícil de implementar em tempo constante (as tabelas de consulta vazam por
cache). ChaCha20 usa só somas, XOR e rotações de 32 bits: rápido e naturalmente em
tempo constante em qualquer CPU.

Regra prática de servidor: ofereça as duas e **não force a preferência do servidor**
(`ssl_prefer_server_ciphers off`). O cliente sabe melhor que você se tem AES-NI.
Essa é a razão real da recomendação que aparece em [17](17-configuracao-de-servidores.md).

### 5.4 As cinco suites do TLS 1.3

| Suite | Quando usar |
|---|---|
| `TLS_AES_128_GCM_SHA256` | padrão. 128 bits é suficiente e mais rápido |
| `TLS_AES_256_GCM_SHA384` | quando uma política exige "256 bits" |
| `TLS_CHACHA20_POLY1305_SHA256` | clientes sem AES-NI |
| `TLS_AES_128_CCM_SHA256` | dispositivos restritos |
| `TLS_AES_128_CCM_8_SHA256` | IoT; tag de 8 bytes (menos segurança de integridade, menos bytes) |

> **AES-128 é suficiente?** Sim. 2^128 operações está fora do alcance de qualquer
> tecnologia concebível; e mesmo o algoritmo de Grover (quântico) só reduziria a
> ~2^64 operações **quânticas**, o que continua inviável na prática por décadas.
> Usar AES-256 em vez de AES-128 é uma decisão de política e conformidade, não de risco real.
> (Opinião profissional, com consenso amplo entre criptógrafos.)

---

## 6. Como os números de segurança se comparam

| "Bits de segurança" | Simétrico | RSA | Curva elíptica | Comentário |
|---|---|---|---|---|
| 80 | — | 1024 | 160 | **quebrado na prática**; não use |
| 112 | 3DES | 2048 | 224 | mínimo aceitável hoje |
| 128 | AES-128 | 3072 | **256** | **o ponto ideal** |
| 192 | AES-192 | 7680 | 384 | conformidade |
| 256 | AES-256 | 15360 | 521 | paranoia útil só contra Grover |

Repare na coluna do RSA: para acompanhar AES-256 seria preciso RSA de 15.360 bits —
absurdamente lento. É por isso que a criptografia de curva elíptica dominou: mesma
segurança, chaves ~12× menores, operações muito mais rápidas.

---

## 7. Os canais laterais

A matemática pode estar perfeita e a implementação vazar tudo. Canais laterais são
informações que escapam pelo **comportamento físico** do código:

| Canal | Como vaza | Defesa |
|---|---|---|
| **tempo** | comparar bytes com saída antecipada revela quantos bateram | comparação em tempo constante (`CRYPTO_memcmp`) |
| **cache** | tabelas de consulta do AES em software deixam rastro no cache da CPU | AES-NI (hardware), ou ChaCha20 |
| **ramificação** | `if (segredo)` muda o preditor de desvios | código sem desvio dependente de segredo |
| **energia/EM** | consumo elétrico correlaciona com bits da chave | mascaramento; relevante em cartões e HSMs |
| **oráculo de erro** | mensagens de erro distintas para "padding errado" e "MAC errado" | erro único e genérico, tempo constante |

> **A lição de projeto:** "funciona e dá o resultado certo" não é o critério em
> criptografia. O critério é "não revela nada além do resultado". Por isso você **não
> deve implementar primitivas criptográficas**; use uma biblioteca revisada. Este curso
> implementa uma **CA** e um **serviço mTLS** ([projeto-modelo](07-projeto-modelo/README.md)),
> não uma cifra — e isso é deliberado.

---

## 8. O que a mudança quântica realmente quebra

| Primitiva | Ameaça quântica | Situação |
|---|---|---|
| **RSA, DH, ECDH, ECDSA** | algoritmo de **Shor** quebra por completo | precisam ser substituídas |
| **AES-128/256** | algoritmo de **Grover** reduz a raiz quadrada do esforço | AES-256 fica com ~128 bits efetivos; **AES-128 continua fora de alcance prático** |
| **SHA-256/384** | Grover, idem | seguras |

Ou seja: **a criptografia simétrica está essencialmente bem**; o problema é toda a
assimétrica. É exatamente por isso que a migração começou pela troca de chaves
(ML-KEM), que é onde o dano do "colher agora, decifrar depois" seria imediato, e as
assinaturas ficaram para depois — uma assinatura só precisa resistir **no momento** em
que é verificada.

---

## Autoteste

1. Quais são as quatro primitivas de um handshake e qual delas protege o tráfego em regime?
2. Explique o acordo Diffie–Hellman com a analogia da tinta e depois com a notação de curvas.
3. O que o "E" de ECDHE garante que o RSA-transporte não garantia?
4. Por que o TLS 1.3 só admite grupos DH **nomeados**?
5. O que acontece se um nonce `k` do ECDSA se repetir? Cite o caso real.
6. Por que RSA-PSS é preferível a PKCS#1 v1.5?
7. Por que o HKDF tem duas etapas em vez de um hash simples?
8. Por que MAC-then-Encrypt rendeu 15 anos de ataques?
9. O que acontece se um nonce for reutilizado em AES-GCM, e como o TLS 1.3 impede isso?
10. Quando ChaCha20-Poly1305 é melhor que AES-GCM, e como o servidor deve tratar essa escolha?
11. AES-128 é suficiente? Justifique, inclusive contra Grover.
12. Por que a migração pós-quântica começou pela troca de chaves e não pelas assinaturas?

*Respostas: §1, §2.1, §2.2, §2.3, §3, §3, §4, §5.1, §5.2, §5.3, §5.4, §8.*

---

**Próximo:** [15-validacao-revogacao-transparencia.md](15-validacao-revogacao-transparencia.md) — e por que revogação nunca funcionou.
