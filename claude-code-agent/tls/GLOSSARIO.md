# Glossário de TLS

**Data:** 31/08/2026 · ~150 termos. Termos em inglês mantidos onde é assim que o campo
os usa, com a tradução na definição. Links apontam para onde o termo é aprofundado.

---

## A

**ACME** (*Automatic Certificate Management Environment*) — protocolo padrão (RFC 8555) para obter e renovar certificados por API, sem humano. Base do Let's Encrypt. → [16](16-acme-e-automacao.md)

**AEAD** (*Authenticated Encryption with Associated Data*) — cifra que protege confidencialidade **e** integridade numa única operação. Exemplos: AES-GCM, ChaCha20-Poly1305. Único tipo admitido no TLS 1.3. → [14](14-criptografia-do-tls.md)

**AES** (*Advanced Encryption Standard*) — cifra simétrica de bloco padronizada em 2001. Usada em TLS nos modos GCM e CCM.

**AES-NI** — instruções de CPU que aceleram AES em hardware. Sua presença decide se AES-GCM ou ChaCha20 é mais rápido.

**AIA** (*Authority Information Access*) — extensão do certificado com a URL do respondedor OCSP e do certificado do emissor. Navegadores a usam para buscar intermediários faltantes.

**Alert** — mensagem de erro do TLS (`handshake_failure`, `unknown_ca`, `certificate_revoked`…). → [12 §6](12-handshake.md)

**ALPN** (*Application-Layer Protocol Negotiation*) — extensão que acorda no handshake qual protocolo de aplicação será usado (`h2`, `http/1.1`, `h3`).

**Âncora de confiança** (*trust anchor*) — certificado raiz em que o cliente confia por decisão prévia, não por validação.

**ASN.1** — notação de descrição de dados dos anos 1980 usada para definir certificados X.509. Codificada em DER. → [13 §7](13-certificados-e-pki.md)

**Autoassinado** (*self-signed*) — certificado cujo `issuer` é igual ao `subject`; assinado pela própria chave.

**Autoridade Certificadora** → ver **CA**.

**Autorização** — decidir **o que** uma identidade pode fazer. **Não** é feita pelo TLS. → [18 §2](18-mtls-e-pki-interna.md)

**Autenticação** — provar **quem** alguém é. É o que o TLS faz com certificados.

---

## B

**Baseline Requirements** — regras que toda CA pública deve seguir, publicadas pelo CA/Browser Forum.

**BEAST** — ataque de 2011 contra o IV previsível do CBC no TLS 1.0. → [21 §3.1](21-ataques-e-defesas.md)

**BoringSSL** — fork do OpenSSL feito pelo Google.

**BREACH** — ataque que explora a compressão do **HTTP**; **ainda viável**. → [21 §3.2](21-ataques-e-defesas.md)

---

## C

**CA** (*Certificate Authority*) — entidade que emite certificados assinando-os com sua chave privada. → [13](13-certificados-e-pki.md)

**CAA** (*Certification Authority Authorization*) — registro DNS que declara quais CAs podem emitir para o seu domínio. Verificação obrigatória desde 2017.

**CA/Browser Forum** — consórcio de CAs e fabricantes de navegadores que escreve as regras comuns. Não é órgão público.

**Cadeia** (*chain*) — sequência folha → intermediário(s) → raiz.

**Caddy** — servidor web que obtém e renova certificados automaticamente. → [16 §4](16-acme-e-automacao.md)

**CBC** (*Cipher Block Chaining*) — modo de operação de cifra de bloco. Origem de BEAST, Lucky13, POODLE. Removido do TLS 1.3.

**certbot** — cliente ACME oficial da EFF.

**Certificado** — declaração assinada que liga uma chave pública a um nome, por um prazo. → [13 §1](13-certificados-e-pki.md)

**CertificateVerify** — mensagem em que o servidor (ou cliente) assina o transcript do handshake, provando posse da chave privada. → [12 §3.4](12-handshake.md)

**ChaCha20-Poly1305** — cifra AEAD de Bernstein; mais rápida que AES em CPUs sem AES-NI.

**check_hostname** — verificação de que o nome acessado casa com o SAN. **Etapa separada** da validação de cadeia, e a mais esquecida. → [13 §4.1](13-certificados-e-pki.md)

**Cipher suite** — conjunto de algoritmos negociado. No TLS 1.3 são apenas 5. → [10 §7](10-fundamentos.md)

**ClientHello** — primeira mensagem do handshake; a única realmente em claro (salvo com ECH). → [12 §2](12-handshake.md)

**close_notify** — alerta que sinaliza fim limpo da conexão. Sem ele, não se distingue "acabou" de "cortaram".

**CN** (*Common Name*) — campo legado do `subject`. **Ignorado pelos navegadores desde 2017**; use o SAN.

**CRIME** — ataque de 2012 contra a compressão do TLS. Matou a compressão no protocolo.

**CRL** (*Certificate Revocation List*) — lista assinada de certificados revogados. → [15 §2](15-validacao-revogacao-transparencia.md)

**CRLite** — estrutura comprimida (filtros de Bloom em cascata) que leva todas as revogações ao navegador, offline. → [15 §5](15-validacao-revogacao-transparencia.md)

**CRLSets** — lista curada de revogações do Chrome.

**CSR** (*Certificate Signing Request*) — pedido de assinatura: chave pública + nomes + prova de posse da privada. A chave privada nunca sai da sua máquina.

**CT** (*Certificate Transparency*) — logs públicos append-only de tudo que foi emitido. → [15 §7](15-validacao-revogacao-transparencia.md)

---

## D

**DANE** — âncora de confiança publicada no DNSSEC (RFC 6698). Adoção baixa.

**DER** — codificação binária de ASN.1. É o "PEM sem o Base64".

**DHE / ECDHE** — Diffie–Hellman efêmero (em curva elíptica). Fonte do sigilo futuro. → [14 §2](14-criptografia-do-tls.md)

**Diffie–Hellman** — método de 1976 para dois lados combinarem um segredo sem transmiti-lo.

**DoH / DoT / DoQ** — DNS sobre HTTPS / TLS / QUIC. → [19 §2](19-tls-alem-do-https.md)

**Dolev–Yao** — modelo de adversário que controla toda a rede mas não quebra a criptografia. → [10 §5.1](10-fundamentos.md)

**Downgrade** — forçar versão ou cifra mais fraca. O TLS 1.3 tem defesa embutida no `ServerHello.random`.

**DROWN** — ataque de 2016 que usa um SSLv2 residual (com a mesma chave) para quebrar TLS moderno.

**DTLS** — TLS sobre UDP (datagramas). Base de VPNs e do WebRTC.

**DV** (*Domain Validated*) — nível de validação em que a CA só confirma controle do domínio. É o que o Let's Encrypt emite.

---

## E

**ECDSA** — assinatura digital em curva elíptica. Rápida, mas **exige nonce único por assinatura**. → [14 §3](14-criptografia-do-tls.md)

**ECH** (*Encrypted Client Hello*) — cifra o `ClientHello`, incluindo o SNI. RFC 9849, março de 2026. → [65 §4](65-estado-da-arte.md)

**Ed25519** — assinatura determinística sobre a curva Edwards25519. Tecnicamente superior ao ECDSA; CAs públicas ainda não emitem.

**EKU** (*Extended Key Usage*) — extensão que diz para que o certificado serve: `serverAuth`, `clientAuth`, etc.

**Efêmero** — chave gerada para uma conexão e descartada ao fim. É o "E" de ECDHE.

**Entropia** — aleatoriedade genuína. Sem ela, toda a criptografia cai.

**EV** (*Extended Validation*) — validação documental reforçada. **Criptograficamente idêntica ao DV**; o indicador visual foi removido dos navegadores em 2019.

**Extensão** (do certificado) — campo adicional do X.509v3 que carrega quase toda a semântica moderna (SAN, EKU, basicConstraints…).

**Extensão** (do TLS) — campo opcional do `ClientHello`/`ServerHello`. O TLS 1.3 vive delas.

---

## F

**Fallback** — tentar de novo com versão mais antiga após falha. Anula a proteção de versão; morto nos navegadores.

**FREAK** — ataque de 2015 que força cifras RSA de exportação (512 bits).

**Fullchain** — arquivo com folha + intermediários. **É o que o servidor deve servir.**

---

## G

**GCM** (*Galois/Counter Mode*) — modo AEAD do AES. **Nunca reutilize nonce com a mesma chave.**

**goto fail** — bug da Apple em 2014 que pulava a verificação de assinatura por uma linha duplicada. → [21 §4.2](21-ataques-e-defesas.md)

---

## H

**Handshake** — a negociação inicial do TLS. → [12](12-handshake.md)

**Heartbleed** — CVE-2014-0160; leitura de memória do servidor pelo OpenSSL, incluindo chaves privadas.

**HelloRetryRequest** — resposta do servidor quando o `key_share` do cliente usa um grupo que ele não aceita. Custa um RTT extra.

**HKDF** — função de derivação de chaves em duas etapas (Extract + Expand). → [14 §4](14-criptografia-do-tls.md)

**HPKP** — fixação de chave por cabeçalho HTTP. **Removido dos navegadores em 2018** por ser um tiro no pé.

**HSM** (*Hardware Security Module*) — dispositivo que guarda chaves privadas sem nunca as exportar.

**HSTS** (*HTTP Strict Transport Security*) — cabeçalho que obriga HTTPS e remove o botão de "prosseguir mesmo assim". Cuidado com `includeSubDomains` e `preload`. → [17 §9](17-configuracao-de-servidores.md)

**Híbrido** (pós-quântico) — combinação de um esquema clássico e um pós-quântico, exigindo quebrar os dois. Ex.: `X25519MLKEM768`.

---

## I

**Intermediário** — CA que fica entre a raiz e a folha. Existe para que a chave da raiz possa ficar offline. → [13 §4](13-certificados-e-pki.md)

**Issuer** — quem assinou o certificado.

---

## K

**KDF** — função de derivação de chaves.

**KEM** (*Key Encapsulation Mechanism*) — mecanismo para combinar uma chave secreta. ML-KEM é o padrão pós-quântico.

**KEMTLS** — proposta acadêmica de autenticar por KEM em vez de assinatura. Não foi o caminho da indústria. → [60 §6.1](60-teoria-avancada.md)

**key_share** — extensão em que o cliente já envia a chave pública efêmera, apostando no grupo. É o que dá o 1-RTT.

**KeyUpdate** — mensagem do TLS 1.3 que troca as chaves de tráfego numa conexão longa.

**Key Usage** — extensão que diz o que a chave pode fazer (assinar, cifrar, assinar certificados…).

---

## L

**Let's Encrypt** — CA gratuita e automatizada da ISRG, aberta em 2015. Mudou a economia do HTTPS. → [11 §8](11-historia.md)

**LibreSSL** — fork do OpenSSL feito pelo OpenBSD após o Heartbleed. É o que o macOS envia.

**Logjam** — ataque de 2015 contra grupos DH fracos e compartilhados.

**Lucky13** — ataque de canal lateral por tempo contra o preenchimento do CBC.

---

## M

**MAC** — código de autenticação de mensagem.

**MAC-then-Encrypt** — ordem usada até o TLS 1.2; origem de uma família inteira de ataques.

**Middlebox** — equipamento intermediário que inspeciona tráfego. Causa da **ossificação**. → [12 §2.1](12-handshake.md)

**MITM** (*man-in-the-middle*) — atacante que se põe entre as pontas e se passa pelas duas.

**mkcert** — ferramenta que cria uma CA local confiável pelo seu sistema, para desenvolvimento.

**ML-DSA** — assinatura pós-quântica padronizada (FIPS 204). Assinaturas de ~2,4 KB.

**ML-KEM** — encapsulamento de chave pós-quântico (FIPS 203, antes Kyber). Já em produção, em modo híbrido.

**MTA-STS** — política publicada por HTTPS que exige TLS válido na entrega de e-mail.

**MTC** (*Merkle Tree Certificates*) — arquitetura em que a CA assina uma raiz de árvore de Merkle e o handshake carrega uma prova de inclusão. Resposta ao tamanho das assinaturas PQ. → [65 §3](65-estado-da-arte.md)

**mTLS** — TLS mútuo: os dois lados se autenticam por certificado. → [18](18-mtls-e-pki-interna.md)

**must-staple** — extensão que exige a presença do OCSP stapling. Quase ninguém usa, por risco operacional.

---

## N

**nameConstraints** — extensão que limita uma CA a determinados domínios.

**Nonce** — valor que nunca se repete com a mesma chave. Reutilizá-lo em GCM destrói a segurança.

---

## O

**OCSP** — consulta on-line de revogação, um certificado por vez. Vaza privacidade e sofre de soft-fail. Em desativação. → [15 §3](15-validacao-revogacao-transparencia.md)

**OCSP stapling** — o servidor anexa a resposta OCSP ao handshake. Resolve privacidade e latência, não o soft-fail.

**OpenSSL** — a biblioteca e o canivete suíço do TLS. Apache 2.0 desde a versão 3.0.

**Ossificação** — enrijecimento da internet por causa de intermediários que assumem formatos permanentes. Fez o TLS 1.3 se disfarçar de 1.2 e o QUIC cifrar seus cabeçalhos.

**OV** (*Organization Validated*) — a CA valida também a existência legal da organização.

---

## P

**PEM** — formato Base64 entre `-----BEGIN X-----` e `-----END X-----`. O padrão de facto em Unix.

**PKCS#1 / #7 / #8 / #12** — famílias de formatos: preenchimento RSA legado / conjunto de certificados / chave privada moderna / "cofre" com chave + certificados. → [05 §3](05-manual-de-uso.md)

**PKI** (*Public Key Infrastructure*) — o sistema de CAs, certificados e políticas que liga chaves a nomes.

**PLANTS** — grupo de trabalho da IETF criado em 2026 para padronizar Merkle Tree Certificates.

**Pinning** — fixar uma chave ou CA específica, ignorando o root store. Poderoso e perigoso. → [06 Exemplo 7](06-exemplos.md)

**POODLE** — ataque de 2014 que enterrou o SSL 3.0.

**PSK** (*Pre-Shared Key*) — chave previamente compartilhada. No TLS 1.3, é também o mecanismo de retomada.

---

## Q

**QUIC** — transporte sobre UDP que **incorpora** o TLS 1.3. Base do HTTP/3. → [19 §3](19-tls-alem-do-https.md)

---

## R

**Raiz** (*root*) — certificado autoassinado no topo da cadeia, guardado offline.

**Record Protocol** — a metade do TLS que cifra e autentica cada bloco de dados. → [10 §3.2](10-fundamentos.md)

**Renegociação** — refazer o handshake numa conexão viva. **Removida no TLS 1.3.**

**Retomada de sessão** (*session resumption*) — reaproveitar uma sessão anterior, pulando o handshake completo.

**Revogação** — declarar um certificado inválido antes do vencimento. Historicamente, nunca funcionou bem. → [15](15-validacao-revogacao-transparencia.md)

**ROBOT** — ressurgimento em 2017 do ataque Bleichenbacher de 1998.

**Root store** — a lista de raízes confiáveis do sistema ou do navegador.

**RSA-PSS** — preenchimento moderno para assinatura RSA, com prova de segurança. Obrigatório no handshake do TLS 1.3.

**RTT** (*round-trip time*) — tempo de ida e volta na rede. A moeda em que se mede o custo de um handshake.

---

## S

**SAN** (*Subject Alternative Name*) — extensão que lista os nomes cobertos pelo certificado. **É o que realmente vale.**

**SCT** (*Signed Certificate Timestamp*) — prova de que o certificado foi submetido a um log de CT. Obrigatório no Chrome desde 2018.

**Serial Number** — identificador único do certificado dentro da CA. Precisa de entropia suficiente.

**ServerHello** — resposta do servidor com a cifra escolhida e o `key_share`. A partir dela, tudo é cifrado.

**Sigilo futuro** (*forward secrecy*) — propriedade de que o vazamento futuro da chave de longo prazo não decifra sessões passadas. Obrigatório no TLS 1.3.

**SNI** (*Server Name Indication*) — extensão que diz qual site o cliente quer. Viaja **em claro**, salvo com ECH.

**Soft-fail** — seguir em frente quando a verificação de revogação falha. Torna a revogação inútil contra um atacante de rede. → [15 §3.3](15-validacao-revogacao-transparencia.md)

**SPIFFE ID** — identidade no formato `spiffe://dominio/ns/.../sa/...`, publicada no SAN como URI. Substitui o CN em PKI moderna. → [18 §3](18-mtls-e-pki-interna.md)

**SSL** — nome antigo do protocolo (1994–1996). Todas as versões estão mortas. "Certificado SSL" é vocabulário fossilizado.

**SSLKEYLOGFILE** — variável que grava os segredos da sessão para permitir decifrar no Wireshark. **Só em laboratório.**

**STARTTLS** — comando que promove uma conexão em claro para TLS. Sujeito a *stripping*. → [19 §1.2](19-tls-alem-do-https.md)

**SSL stripping** — ataque que impede o usuário de chegar ao HTTPS, interceptando a primeira requisição em HTTP. Defesa: HSTS.

**Subject** — a quem o certificado pertence.

**Sweet32** — ataque de 2016 contra cifras de bloco de 64 bits (3DES).

---

## T

**TLS** (*Transport Layer Security*) — o protocolo. Versões vivas: 1.2 e 1.3.

**Ticket de sessão** — estado da sessão cifrado pelo servidor e guardado pelo cliente. A chave de ticket precisa ser rotacionada. → [17 §2.1](17-configuracao-de-servidores.md)

**Transcript** — o registro de todas as mensagens do handshake. Assinado no `CertificateVerify` e autenticado no `Finished`.

**Truncamento** — ataque que corta a conexão sem `close_notify`.

---

## V

**Validação de cadeia** — o processo de dez passos que vai da folha à raiz. → [13 §4.1](13-certificados-e-pki.md)

---

## W

**Wildcard** (curinga) — certificado do tipo `*.exemplo.com`. Cobre **um** nível; não cobre o apex.

**WireGuard** — VPN que **não** usa TLS: primitivas fixas, sem negociação. → [19 §4](19-tls-alem-do-https.md)

---

## X

**X.509** — o padrão de formato de certificado, herdado do X.500 da ITU-T (1988).

**X25519** — curva de Bernstein usada para acordo de chaves. O grupo preferido hoje.

**X25519MLKEM768** — grupo híbrido pós-quântico, padrão de facto em 2026.

---

## Números

**0-RTT** — envio de dados junto com o `ClientHello` na retomada. Rápido e **sujeito a repetição**. → [12 §5.2](12-handshake.md)

**1-RTT** — o handshake do TLS 1.3, que custa uma ida e volta.

**200 dias** — validade máxima de certificado público desde 15/03/2026. Vai a 100 em 2027 e a 47 em 2029.

**6 dias (160 h)** — validade do perfil `shortlived` do Let's Encrypt, disponível desde 15/01/2026.

**443** — porta padrão do HTTPS.

**16.384 bytes** — tamanho máximo de um registro TLS.

---

**Voltar ao mapa:** [00-MAPA.md](00-MAPA.md)
