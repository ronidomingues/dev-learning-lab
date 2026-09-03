# 12 · O handshake, mensagem a mensagem

**Nível:** intermediário → avançado · **Data:** 31/08/2026

O handshake é o coração do TLS. Aqui ele é aberto inteiro: cada mensagem, cada
extensão, por que existe, e o que acontece se faltar.

**Sobre os bytes mostrados.** O `ClientHello` da §2 foi **capturado de verdade** em
31/08/2026 com `openssl s_client -connect example.com:443 -servername example.com
-trace`, no OpenSSL 3.0.2 desta máquina: é exatamente o que o cliente colocou no fio.
Os blocos do `ServerHello` em diante (§3) são **ilustrativos, no formato real** do
mesmo `-trace` — a máquina usada para escrever este material só sai para a internet
por proxy corporativo, que bloqueia a conexão TLS direta e portanto impede capturar a
resposta do servidor. Reproduza o comando acima na sua rede para ver o par completo.

---

## 1. A visão de 10 mil metros

### TLS 1.3 — uma ida e volta

```
CLIENTE                                              SERVIDOR
   │                                                     │
   │ ── ClientHello ───────────────────────────────────► │
   │    versões, cifras, grupos,                         │
   │    key_share (JÁ manda a chave pública efêmera),    │
   │    server_name, ALPN, signature_algorithms          │
   │                                                     │
   │ ◄─────────────────────────── ServerHello ────────── │
   │    cifra escolhida, key_share do servidor           │
   │    ══ daqui em diante TUDO é cifrado ══             │
   │ ◄── {EncryptedExtensions}                           │
   │ ◄── {CertificateRequest}      (só em mTLS)          │
   │ ◄── {Certificate}             (cadeia do servidor)  │
   │ ◄── {CertificateVerify}       (assina o transcript) │
   │ ◄── {Finished}                (MAC de tudo)         │
   │                                                     │
   │ ── {Certificate} ────────────────────────► (mTLS)   │
   │ ── {CertificateVerify} ──────────────────► (mTLS)   │
   │ ── {Finished} ────────────────────────────────────► │
   │                                                     │
   │ ══ dados de aplicação nos dois sentidos ══          │
```

**1 RTT.** O cliente já pode enviar `GET /` junto com o seu `Finished`.

### TLS 1.2 — duas idas e voltas

```
CLIENTE                                              SERVIDOR
   │ ── ClientHello ───────────────────────────────────► │
   │ ◄─── ServerHello, Certificate (EM CLARO!),          │
   │      ServerKeyExchange, ServerHelloDone ─────────── │
   │ ── ClientKeyExchange, ChangeCipherSpec, Finished ─► │
   │ ◄─────────────── ChangeCipherSpec, Finished ─────── │
   │ ══ dados ══                                         │
```

**2 RTT**, e o certificado do servidor viaja **em claro** — qualquer observador sabia
com quem você estava falando mesmo sem SNI. Essa é uma das melhorias mais subestimadas
do TLS 1.3.

**Quanto isso custa em tempo real:** com 100 ms de latência entre cliente e servidor,
o TLS 1.2 acrescenta ~200 ms antes do primeiro byte útil (além dos ~100 ms do
*three-way handshake* do TCP); o TLS 1.3 acrescenta ~100 ms; e o QUIC/HTTP-3 funde o
handshake de transporte com o de TLS, chegando a ~100 ms **no total**.

---

## 2. `ClientHello` — bytes reais

Capturado com `openssl s_client -connect example.com:443 -servername example.com -trace`
(saída real desta máquina, 31/08/2026):

```
Sent Record
Header:
  Version = TLS 1.0 (0x301)          ← MENTIRA deliberada; ver §2.1
  Content Type = Handshake (22)
  Length = 308
    ClientHello, Length=304
      client_version=0x303 (TLS 1.2) ← OUTRA mentira deliberada
      Random:
        gmt_unix_time=0x6E5121A8
        random_bytes (len=28): 7DE9EFBA8C9BEB951098539094AAD844...
      session_id (len=32): 4A37E19EA0FB513F9A26D2AB40DA3D2E...
      cipher_suites (len=62)
        {0x13, 0x02} TLS_AES_256_GCM_SHA384
        {0x13, 0x03} TLS_CHACHA20_POLY1305_SHA256
        {0x13, 0x01} TLS_AES_128_GCM_SHA256
        {0xC0, 0x2C} TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        ... (31 suites no total)
      compression_methods (len=1)
        No Compression (0x00)         ← única opção desde o CRIME
      extensions, length = 169
```

### 2.1 As três mentiras do `ClientHello`, explicadas

Este é o melhor exemplo de **ossificação da internet** que existe, e vale entender:

| Campo | Diz | Verdade | Por quê |
|---|---|---|---|
| `Version` do registro | TLS 1.0 (0x0301) | irrelevante | equipamentos antigos descartavam registros com versão que não conheciam |
| `client_version` | TLS 1.2 (0x0303) | pode ser 1.3 | *middleboxes* travavam ao ver 0x0304 |
| `session_id` de 32 bytes | uma sessão | é aleatório e descartável | finge ser um handshake TLS 1.2 com retomada, para os mesmos equipamentos |

A versão **real** vai na extensão `supported_versions`, que os equipamentos velhos
ignoram por não conhecer. Ou seja: **o TLS 1.3 se disfarça de TLS 1.2 no fio.**

> ### Por que a internet obriga um protocolo a mentir
> Percorrendo os porquês: *(1)* Por que mentir? Porque conexões TLS 1.3 honestas eram
> derrubadas. *(2)* Por quem? Por *middleboxes* — firewalls, balanceadores, appliances
> de inspeção — que analisam o TLS no meio do caminho. *(3)* Por que eles derrubam?
> Porque foram escritos assumindo que o formato do TLS 1.2 era permanente, e rejeitam
> o que não reconhecem em vez de repassar. *(4)* Por que fizeram assim? Porque "rejeitar
> o desconhecido" parece seguro, e porque o equipamento foi vendido e nunca mais
> atualizado. *(5)* Por que ninguém atualiza? **Trade-off econômico:** o fabricante não
> ganha nada atualizando firmware de um produto já vendido, e o comprador não troca
> equipamento que "está funcionando". **A parada é econômica, não técnica.**
> Consequência de longo prazo: o QUIC foi projetado para cifrar quase todo o cabeçalho,
> de modo que nenhum intermediário consiga depender do formato — e portanto não consiga
> impedir a evolução do protocolo. Ossificação foi uma lição cara o bastante para
> redesenhar a camada de transporte.

### 2.2 As extensões — onde o TLS 1.3 realmente vive

Capturadas na mesma execução real:

```
extension_type=server_name(0), length=16
  0000 - 00 0e 00 00 0b 65 78 61-6d 70 6c 65 2e 63 6f   .....example.co
  000f - 6d                                             m
```

**Ali está `example.com` em texto puro.** É o SNI. Qualquer um no caminho lê. Esta é a
maior fuga de privacidade do TLS moderno, e o motivo de existir o ECH
([65-estado-da-arte.md](65-estado-da-arte.md)).

```
extension_type=supported_groups(10), length=22
  ecdh_x25519 (29)          ← preferido
  secp256r1 (P-256) (23)
  ecdh_x448 (30)
  secp521r1 (P-521) (25)
  secp384r1 (P-384) (24)
  ffdhe2048 (256) ... ffdhe8192 (260)
```

Os grupos para a troca de chaves. Com OpenSSL 3.5+ apareceria aqui também o
`X25519MLKEM768`, híbrido pós-quântico.

```
extension_type=supported_versions(43), length=5
  TLS 1.3 (772)             ← A VERSÃO DE VERDADE
  TLS 1.2 (771)
```

```
extension_type=signature_algorithms(13), length=42
  ecdsa_secp256r1_sha256 (0x0403)
  ed25519 (0x0807)
  rsa_pss_rsae_sha256 (0x0804)
  rsa_pkcs1_sha256 (0x0401)
  ... (20 algoritmos)
```

Quais assinaturas o cliente aceita — tanto no certificado quanto no
`CertificateVerify`. É por isso que um servidor com certificado Ed25519 hoje falha em
clientes antigos: não está na lista deles.

**Tabela das extensões que importam:**

| Extensão | Papel | Se faltar |
|---|---|---|
| `server_name` (SNI) | qual site quero | servidor com vários domínios manda o certificado errado |
| `supported_versions` | a versão real | fica-se preso ao TLS 1.2 |
| `supported_groups` | curvas/grupos aceitos | sem grupo em comum → `handshake_failure` |
| `key_share` | **a chave pública efêmera já enviada** | o servidor responde `HelloRetryRequest` e custa 1 RTT extra |
| `signature_algorithms` | assinaturas aceitas | `handshake_failure` se o certificado usar outra |
| `application_layer_protocol_negotiation` (ALPN) | `h2`, `http/1.1`, `h3` | sem HTTP/2 — cai para HTTP/1.1 |
| `psk_key_exchange_modes` + `pre_shared_key` | retomada de sessão | handshake completo sempre |
| `early_data` | 0-RTT | sem 0-RTT |
| `status_request` | quero OCSP stapling | cliente precisa consultar a CA por conta própria |
| `encrypted_client_hello` | ECH | SNI em claro |

### 2.3 O `key_share` e a aposta

No TLS 1.3, o cliente **adivinha** qual grupo o servidor vai escolher e já manda a
chave pública desse grupo. Quase sempre acerta (X25519). Se errar, o servidor responde
`HelloRetryRequest` dizendo qual grupo quer, e o cliente refaz — custando **um RTT extra**.

É uma troca deliberada: gastar alguns bytes a mais no caso comum para economizar uma
viagem de rede. Como um RTT intercontinental custa 150–250 ms e alguns bytes custam
microssegundos, a aposta compensa esmagadoramente.

---

## 3. `ServerHello` e o resto, cifrado

```
Version = TLS 1.2 (0x303)              ← mentira de novo
cipher_suite = TLS_AES_256_GCM_SHA384  ← escolha final
extension_type=supported_versions(43)
  TLS 1.3 (772)                        ← a verdade
extension_type=key_share(51)
  ecdh_x25519 (29), key_exchange (32 bytes)
```

**A partir daqui, tudo é cifrado.** Os dois lados já têm o segredo compartilhado
(a partir dos dois `key_share`), derivam as *handshake traffic keys* e passam a cifrar
até o resto do handshake.

### 3.1 A defesa anti-downgrade escondida no `random`

O `ServerHello.random` tem 32 bytes aleatórios — **exceto** que, se o servidor fala
TLS 1.3 mas negociou 1.2 (ou 1.1) por causa do cliente, ele coloca um valor **fixo**
nos últimos 8 bytes:

```
negociou TLS 1.2 mas suporta 1.3:  ...44 4F 57 4E 47 52 44 01     ("DOWNGRD" + 0x01)
negociou TLS 1.1 ou menos:         ...44 4F 57 4E 47 52 44 00     ("DOWNGRD" + 0x00)
```

Um cliente TLS 1.3 que negociou 1.2 e vê esses bytes sabe que **um atacante forçou o
downgrade** (porque um servidor honesto que suporta 1.3 teria negociado 1.3 com ele)
e aborta. Como o `random` está coberto pelo `Finished`, o atacante não consegue
alterá-lo. É uma defesa elegante que custa zero bytes extras.

### 3.2 `EncryptedExtensions`

Extensões que não são necessárias para estabelecer as chaves e que, portanto, podem
esperar até estarem protegidas: ALPN, tamanho máximo de registro, e outras. Não existia
no TLS 1.2 — lá tudo ia em claro.

### 3.3 `Certificate`

A cadeia do servidor: folha primeiro, depois os intermediários. **A raiz não deve ser
enviada** (o cliente já a tem; mandá-la só desperdiça bytes em todo handshake).

No TLS 1.3 isso vai **cifrado**. Consequência prática enorme para privacidade: no TLS
1.2, um observador via o certificado e portanto o site, mesmo sem SNI.

### 3.4 `CertificateVerify` — a mensagem que faz o certificado valer alguma coisa

O servidor assina, com a chave privada correspondente ao certificado, um valor
derivado de **todo o transcript do handshake até aqui**:

```
assinatura = Sign( chave_privada,
                   0x20 repetido 64 vezes            ‖   (preenchimento anti-confusão)
                   "TLS 1.3, server CertificateVerify" ‖  (rótulo de contexto)
                   0x00                                ‖
                   Hash(todas as mensagens até agora) )
```

**Por que isso é essencial.** Sem essa mensagem, qualquer um que tivesse uma **cópia**
do certificado (que é público!) poderia apresentá-lo. A assinatura prova posse da
**chave privada**. E como ela cobre o transcript inteiro, prova posse **nesta conversa
específica** — não numa gravada ontem.

Os três detalhes do formato existem por razões de segurança concretas:

- **os 64 bytes 0x20** e o **rótulo de contexto** impedem *cross-protocol confusion*:
  que uma assinatura produzida num contexto (por exemplo, cliente) seja aceita em
  outro (servidor), ou que uma assinatura de outro protocolo seja reaproveitada aqui;
- **o hash do transcript** garante que a assinatura não possa ser reaproveitada em
  outra sessão.

### 3.5 `Finished`

Um HMAC sobre todo o transcript, com uma chave derivada do segredo da sessão.
Prova que os dois lados chegaram ao **mesmo** segredo e que **ninguém alterou nada**
da negociação. É a resposta final ao problema descoberto em 1995 no SSL 2.0.

Ordem obrigatória: quem recebe **verifica o `Finished` antes de aceitar qualquer
dado de aplicação**. Aceitar dados antes é um bug de implementação clássico.

---

## 4. Derivação de chaves — o escalonamento HKDF

O TLS 1.3 não usa uma chave: usa uma **árvore** delas, derivadas por HKDF-Extract e
HKDF-Expand. Simplificado:

```
                      0 (PSK ausente)
                       │
                  HKDF-Extract
                       ▼
              ┌── Early Secret ────► binder_key, early_traffic_secret (0-RTT)
              │
        Derive-Secret + HKDF-Extract(segredo ECDHE)
                       ▼
              ┌── Handshake Secret ─┬─► client_handshake_traffic_secret
              │                     └─► server_handshake_traffic_secret
              │                          (cifram o resto do handshake)
        Derive-Secret + HKDF-Extract(0)
                       ▼
              └── Master Secret ────┬─► client_application_traffic_secret
                                    ├─► server_application_traffic_secret
                                    ├─► exporter_master_secret
                                    └─► resumption_master_secret
```

Cada seta é uma derivação com um **rótulo** distinto. Três propriedades importantes:

1. **Chaves diferentes por direção.** Cliente→servidor e servidor→cliente usam chaves
   distintas. Sem isso, um atacante poderia refletir uma mensagem de volta ao remetente
   e ela seria aceita como legítima (*reflection attack*).
2. **Chaves diferentes por fase.** As chaves do handshake não servem para os dados,
   e vice-versa.
3. **Separação por rótulo.** Vazar uma chave derivada não permite recuperar o segredo
   pai nem as chaves irmãs — é a propriedade unidirecional do HKDF.

O `exporter_master_secret` merece nota: permite que a **aplicação** derive material
criptográfico ligado à sessão TLS (por exemplo, para *channel binding* em autenticação —
amarrar um token à conexão TLS exata, de modo que roubá-lo não adiante).

---

## 5. Retomada de sessão e 0-RTT

### 5.1 Retomada

Depois de um handshake completo, o servidor pode mandar um `NewSessionTicket`. Numa
conexão futura, o cliente apresenta esse ticket como **PSK** (*pre-shared key*), e o
handshake pula certificado e assinatura — economizando CPU e bytes.

Duas implementações:

| Mecanismo | Como | Trade-off |
|---|---|---|
| **Session cache** | o servidor guarda o estado, indexado por ID | seguro; não funciona entre máquinas sem estado compartilhado |
| **Session tickets** | o servidor cifra o estado e entrega ao cliente | sem estado no servidor; **a chave de ticket vira um segredo de longo prazo** |

> **O risco do ticket.** Se a chave que cifra os tickets não for rotacionada e vazar,
> um atacante que gravou o tráfego decifra as sessões retomadas — **anulando o sigilo
> futuro** que o ECDHE deu. O nginx só rotaciona ao reiniciar; por isso a recomendação
> comum é `ssl_session_tickets off`, ou rotação explícita por cron.
> Recomende-se sempre `psk_dhe_ke` (retomada **com** nova troca ECDHE), que é o padrão
> do TLS 1.3 e restaura o sigilo futuro mesmo na retomada.

### 5.2 0-RTT (*early data*)

O cliente envia dados de aplicação **junto** com o `ClientHello`, cifrados com uma
chave derivada do PSK. Latência de aplicação: **zero**.

**O preço é estrutural, não um bug:** dados de 0-RTT **podem ser repetidos** por um
atacante. Como não houve troca nova, não há nada que prove frescor. Um atacante que
capture o pacote pode reenviá-lo N vezes.

Regra prática: **só use 0-RTT para requisições idempotentes** (`GET` sem efeito
colateral). Nunca para `POST /transferir`. Servidores sérios aplicam ainda uma janela
de tempo e um registro anti-repetição de tickets já usados — mitigações parciais.

---

## 6. Quando falha: os alertas

| Alerta | Significa | Causa típica |
|---|---|---|
| `handshake_failure` (40) | nada em comum | cifras/grupos/versões incompatíveis |
| `bad_certificate` (42) | certificado malformado | arquivo corrompido |
| `unsupported_certificate` (43) | tipo não aceito | Ed25519 num cliente antigo |
| `certificate_expired` (45) | fora da validade | esqueceu de renovar |
| `certificate_revoked` (44) | está na CRL/OCSP | revogado |
| `certificate_unknown` (46) | erro genérico de validação | — |
| `unknown_ca` (48) | emissor não confiado | CA privada, ou cadeia incompleta |
| `certificate_required` (116) | mTLS: cliente não mandou certificado | falta `--cert` |
| `access_denied` (49) | recusa por política | — |
| `protocol_version` (70) | versão não aceita | cliente só fala TLS 1.0 |
| `inappropriate_fallback` (86) | downgrade detectado | ataque, ou cliente com fallback ruim |
| `no_application_protocol` (120) | ALPN sem interseção | cliente pede `h2`, servidor só faz `http/1.1` |

Todos esses alertas apareceram, com nomes reais, nos testes do
[projeto-modelo](07-projeto-modelo/README.md) — `certificate_revoked`,
`certificate_expired`, `unknown_ca` e `certificate_required`.

Veja você mesmo, com bytes:

```bash
openssl s_client -connect exemplo.com:443 -servername exemplo.com -trace </dev/null 2>&1 | grep -A3 Alert
```

---

## 7. Comparação final TLS 1.2 × TLS 1.3

| Aspecto | TLS 1.2 | TLS 1.3 |
|---|---|---|
| RTTs do handshake | 2 | 1 (0 na retomada) |
| Certificado do servidor | **em claro** | cifrado |
| Extensões | em claro | maioria cifrada |
| Troca de chaves | RSA, DH, ECDHE (configurável) | **sempre** (EC)DHE |
| Sigilo futuro | opcional | obrigatório |
| Cifras | centenas, muitas inseguras | 5, todas AEAD |
| Negociação de assinatura | acoplada à suite | extensão separada |
| Renegociação | sim (histórico de ataques) | removida |
| Compressão | opcional (CRIME) | removida |
| Anti-downgrade | `TLS_FALLBACK_SCSV` (opcional) | embutido no `random` |
| Retomada | ID ou ticket | PSK unificado |
| 0-RTT | não | sim (com repetição possível) |

---

## Autoteste

1. Quantos RTTs custa o handshake em TLS 1.2, TLS 1.3 e TLS 1.3 com 0-RTT?
2. Cite as três "mentiras" do `ClientHello` e a razão econômica por trás delas.
3. Onde vai a versão real do TLS 1.3, se o campo `client_version` diz 1.2?
4. O que é o `key_share` antecipado e o que acontece quando o cliente erra a aposta?
5. Como o TLS 1.3 detecta um downgrade forçado, sem gastar bytes extras?
6. Por que o `CertificateVerify` existe, se o certificado já foi enviado?
7. Por que a assinatura do `CertificateVerify` inclui 64 bytes 0x20 e um rótulo de texto?
8. Por que existem chaves diferentes para cada direção da conexão?
9. Por que dados 0-RTT podem ser repetidos, e que tipo de requisição pode usá-los?
10. Por que `ssl_session_tickets off` é uma recomendação comum?
11. Você vê `unknown_ca` num cliente e o site funciona no navegador. Qual é a hipótese mais provável?

*Respostas: §1, §2.1, §2.2, §2.3, §3.1, §3.4, §3.4, §4, §5.2, §5.1, §6 + [04](04-como-comecar.md) erro 1.*

---

**Próximo:** [13-certificados-e-pki.md](13-certificados-e-pki.md) — o documento e o sistema de confiança.
