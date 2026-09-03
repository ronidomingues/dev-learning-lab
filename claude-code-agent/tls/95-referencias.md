# 95 · Referências

**Nível:** todos · **Data:** 31/08/2026

Specs, papers, documentação oficial, código-fonte, ferramentas e pessoas.
Tudo verificável. **Nada aqui foi inventado**; onde não tive certeza da numeração ou da
data, o texto diz.

---

## 1. RFCs — as especificações

### 1.1 O núcleo

| RFC | Título | Ano | Por que importa |
|---|---|---|---|
| **8446** | **The Transport Layer Security (TLS) Protocol Version 1.3** | 2018 | ⭐ **A** especificação. Leia pelo menos as seções 1–4 |
| 5246 | TLS 1.2 | 2008 | obsoleta pela 8446, mas ainda em uso massivo |
| 8996 | Deprecating TLS 1.0 and TLS 1.1 | 2021 | o documento que enterrou formalmente as versões antigas |
| 7568 | Deprecating SSLv3 | 2015 | idem para o SSL 3.0 |
| 9147 | DTLS 1.3 | 2022 | TLS sobre UDP |

### 1.2 Certificados e PKI

| RFC | Título | Ano |
|---|---|---|
| **5280** | Internet X.509 PKI Certificate and CRL Profile | 2008 |
| **6125** | Representation and Verification of Domain-Based Application Service Identity | 2011 |
| 6960 | OCSP | 2013 |
| 6962 | Certificate Transparency | 2013 |
| 9162 | Certificate Transparency Version 2.0 | 2021 |
| 6844 / 8659 | DNS CAA Resource Record | 2013 / 2019 |
| 7633 | X.509 TLS Feature Extension (`must-staple`) | 2015 |
| **8555** | **Automatic Certificate Management Environment (ACME)** | 2019 |
| 8737 / 8738 | ACME TLS-ALPN-01 / ACME para endereços IP | 2020 |

### 1.3 Extensões e recursos

| RFC | Título | Ano |
|---|---|---|
| 6066 | TLS Extensions: Extension Definitions (inclui **SNI**) | 2011 |
| 7301 | **ALPN** | 2014 |
| 5746 | Renegociação segura | 2010 |
| 7507 | `TLS_FALLBACK_SCSV` | 2015 |
| 7919 | Grupos DH finitos nomeados | 2016 |
| 8879 | TLS Certificate Compression | 2020 |
| 5869 | **HKDF** | 2010 |
| **9848** | Bootstrapping TLS Encrypted ClientHello with DNS Service Bindings | **2026** |
| **9849** | **TLS Encrypted Client Hello (ECH)** | **2026** |

### 1.4 TLS em outros protocolos

| RFC | Título | Ano |
|---|---|---|
| 8314 | Cleartext Considered Obsolete: TLS para acesso a e-mail | 2018 |
| 8461 | **MTA-STS** | 2018 |
| 8460 | **TLS-RPT** | 2018 |
| 7672 | DANE para SMTP | 2015 |
| 6698 | **DANE** | 2012 |
| 7858 | **DNS over TLS** | 2016 |
| 8484 | **DNS over HTTPS** | 2018 |
| 9250 | **DNS over QUIC** | 2022 |
| **9000** | **QUIC: A UDP-Based Multiplexed and Secure Transport** | 2021 |
| 9001 | Using TLS to Secure QUIC | 2021 |
| 9114 | HTTP/3 | 2022 |
| 6797 | **HSTS** | 2012 |
| 9458 | Oblivious HTTP | 2024 |

### 1.5 Em elaboração (agosto de 2026)

| Documento | Grupo | Assunto |
|---|---|---|
| `draft-ietf-plants-merkle-tree-certs` | **PLANTS** | **Merkle Tree Certificates** — a resposta ao tamanho das assinaturas PQ ([65 §3](65-estado-da-arte.md)) |
| rascunhos de KEM híbrido para TLS | TLS WG | formalização do `X25519MLKEM768` e sucessores |

Onde acompanhar: <https://datatracker.ietf.org/wg/tls/documents/> e
<https://datatracker.ietf.org/wg/plants/documents/>.

**Como ler uma RFC sem sofrer:** vá direto às seções de *Overview* e aos diagramas de
mensagens; ignore a gramática formal na primeira leitura; use `Ctrl+F` para o campo que
te interessa; e leia a seção *Security Considerations* — é frequentemente a parte mais
instrutiva do documento.

---

## 2. Padrões e políticas

| Documento | Órgão | Onde |
|---|---|---|
| **CA/Browser Forum Baseline Requirements** | CA/B Forum | <https://cabforum.org/baseline-requirements-documents/> |
| **Ballot SC-081v3** — cronograma de redução de validade | CA/B Forum | <https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/> |
| **Mozilla Root Store Policy** | Mozilla | <https://www.mozilla.org/about/governance/policies/security-group/certs/policy/> |
| **Chrome Root Program Policy** | Google | <https://g.co/chrome/root-policy> |
| **FIPS 203** — ML-KEM | NIST | <https://csrc.nist.gov/pubs/fips/203/final> |
| **FIPS 204** — ML-DSA | NIST | <https://csrc.nist.gov/pubs/fips/204/final> |
| **FIPS 205** — SLH-DSA | NIST | <https://csrc.nist.gov/pubs/fips/205/final> |
| **NIST SP 800-52 Rev. 2** — diretrizes de TLS | NIST | <https://csrc.nist.gov/pubs/sp/800/52/r2/final> |
| **Recommandations de sécurité relatives à TLS** | **ANSSI** (França) | <https://cyber.gouv.fr/publications> |
| **BSI TR-02102-2** | BSI (Alemanha) | <https://www.bsi.bund.de/> |

---

## 3. Papers

### 3.1 Análise formal e provas

| Paper | Autores | Onde |
|---|---|---|
| *On the Security of TLS-DHE in the Standard Model* (o paper do **ACCE**) | Jager, Kohlar, Schäge, Schwenk | CRYPTO 2012 |
| *A Comprehensive Symbolic Analysis of TLS 1.3* | Cremers, Horvat, Hoyland, Scott, van der Merwe | ACM CCS 2017 · <https://acmccs.github.io/papers/p1773-cremersA.pdf> |
| *Automated Analysis and Verification of TLS 1.3: 0-RTT, Resumption and Delayed Authentication* | Cremers, Horvat, Scott, van der Merwe | IEEE S&P 2016 · <https://people.cispa.io/cas.cremers/downloads/papers/CHSV2016-TLS13.pdf> |
| *Verified Models and Reference Implementations for the TLS 1.3 Standard Candidate* | Bhargavan, Blanchet, Kobeissi | IEEE S&P 2017 |
| *A tale of two models: formal verification of KEMTLS via Tamarin* | Celi, Hülsing, Stebila, Wiggers et al. | <https://eprint.iacr.org/2022/1111> |

### 3.2 Ataques

| Ataque | Referência |
|---|---|
| Bleichenbacher (1998) | *Chosen Ciphertext Attacks Against Protocols Based on the RSA Encryption Standard PKCS #1*, CRYPTO '98 |
| BEAST (2011) | Duong & Rizzo |
| CRIME (2012) | Rizzo & Duong |
| Lucky13 (2013) | AlFardan & Paterson · <https://www.isg.rhul.ac.uk/tls/Lucky13.html> |
| POODLE (2014) | Möller, Duong, Kotowicz (Google) |
| Heartbleed (2014) | CVE-2014-0160 · <https://heartbleed.com/> |
| FREAK (2015) | Beurdouche et al. · <https://mitls.org/pages/attacks/SMACK> |
| Logjam (2015) | Adrian et al. · <https://weakdh.org/> |
| DROWN (2016) | Aviram et al. · <https://drownattack.com/> |
| Sweet32 (2016) | Bhargavan & Leurent · <https://sweet32.info/> |
| ROBOT (2017) | Böck, Somorovsky, Young · <https://robotattack.org/> |
| Raccoon (2020) | Merget et al. · <https://raccoon-attack.com/> |

### 3.3 Ecossistema e implementação

| Paper | Por quê |
|---|---|
| ⭐ *The Most Dangerous Code in the World: Validating SSL Certificates in Non-Browser Software* — Georgiev et al., **CCS 2012** | **Leia este.** Mostra quão disseminada é a validação quebrada fora dos navegadores, e por que a culpa é do desenho das APIs |
| *Post-Quantum TLS Without Handshake Signatures* — Schwabe, Stebila, Wiggers, **CCS 2020** | KEMTLS |
| *Analysis of SSL certificate reissues and revocations in the wake of Heartbleed* — Zhang et al., IMC 2014 | por que a revogação não funcionou |
| *CRLite: A Scalable System for Pushing All TLS Revocations to All Browsers* — Larisch et al., IEEE S&P 2017 | a melhor solução técnica para revogação |

---

## 4. Documentação oficial e ferramentas

| Recurso | Onde |
|---|---|
| **OpenSSL** — docs e releases | <https://openssl-library.org/> · <https://docs.openssl.org/> |
| **Mozilla Server Side TLS** | <https://wiki.mozilla.org/Security/Server_Side_TLS> |
| ⭐ **Gerador de configuração da Mozilla** | <https://ssl-config.mozilla.org/> |
| **Let's Encrypt** — documentação | <https://letsencrypt.org/docs/> |
| **certbot** | <https://certbot.eff.org/> |
| **Caddy** — automatic HTTPS | <https://caddyserver.com/docs/automatic-https> |
| **mkcert** | <https://github.com/FiloSottile/mkcert> |
| **step-ca** (Smallstep) | <https://smallstep.com/docs/step-ca/> |
| **cert-manager** | <https://cert-manager.io/docs/> |
| **SPIFFE / SPIRE** | <https://spiffe.io/> |
| **testssl.sh** | <https://github.com/testssl/testssl.sh> |
| **SSL Labs Server Test** | <https://www.ssllabs.com/ssltest/> |
| **Hardenize** | <https://www.hardenize.com/> |
| **badssl.com** — sites quebrados de propósito | <https://badssl.com/> |
| **crt.sh** — busca em logs de Certificate Transparency | <https://crt.sh/> |
| **Cert Spotter** (SSLMate) — monitoramento de CT | <https://sslmate.com/certspotter/> |
| **Censys** / **Shodan** | <https://censys.io/> · <https://www.shodan.io/> |
| **Cloudflare Radar** | <https://radar.cloudflare.com/> |
| **Wireshark** | <https://www.wireshark.org/> |
| **mitmproxy** | <https://mitmproxy.org/> |
| ⭐ **The Illustrated TLS 1.3 Connection** | <https://tls13.xargs.org/> |
| **Cloudflare Learning Center — SSL/TLS** | <https://www.cloudflare.com/learning/ssl/> |
| **OWASP TLS Cheat Sheet** | <https://cheatsheetseries.owasp.org/> |
| **IANA TLS Parameters** (registro oficial de cipher suites, extensões, alertas) | <https://www.iana.org/assignments/tls-parameters/> |

---

## 5. Código-fonte que vale ler

| Projeto | Linguagem | Por que ler |
|---|---|---|
| **rustls** | Rust | <https://github.com/rustls/rustls> — a implementação mais legível que existe. **Comece por aqui** se quiser entender como se escreve uma pilha TLS |
| **BoringSSL** | C | <https://boringssl.googlesource.com/boringssl/> — o OpenSSL sem 20 anos de bagagem; muito mais fácil de acompanhar |
| **Go `crypto/tls`** | Go | <https://cs.opensource.google/go/go/+/master:src/crypto/tls/> — biblioteca padrão, código limpo e comentado |
| **s2n-tls** (AWS) | C | <https://github.com/aws/s2n-tls> — projetado para ser pequeno e auditável |
| **OpenSSL** | C | <https://github.com/openssl/openssl> — a referência de facto. Difícil de ler; útil como fonte de verdade |
| **miTLS / Project Everest** | F* | <https://github.com/project-everest> — implementação com prova formal |
| **Python `ssl` / `_ssl.c`** | Python/C | como uma linguagem embrulha o OpenSSL |

---

## 6. Pessoas e blogs a acompanhar

| Quem | Onde | Por quê |
|---|---|---|
| **Ivan Ristić** | <https://blog.ivanristic.com/> | autor do *Bulletproof TLS* e do SSL Labs |
| **Adam Langley** ("agl") | <https://www.imperialviolet.org/> | ex-Google, TLS/BoringSSL; os textos sobre revogação e soft-fail são canônicos |
| **Filippo Valsorda** | <https://filippo.io/> | ex-Go crypto lead, autor do mkcert; escreve muito bem sobre criptografia aplicada |
| **Cloudflare Blog** | <https://blog.cloudflare.com/> | onde o pós-quântico, o ECH e o QUIC são explicados com dados reais de rede |
| **Let's Encrypt Blog** | <https://letsencrypt.org/blog/> | anúncios de vida curta, certificados de IP, PQC |
| **Google Security Blog** | <https://security.googleblog.com/> | Chrome Root Program, MTC, política de certificados |
| **Hussein Nasser** | <https://www.youtube.com/@hnasr> | o melhor conteúdo gratuito em vídeo sobre TLS |
| **Scott Helme** | <https://scotthelme.co.uk/> | análises práticas de HSTS, CSP, certificados curtos |
| **Feisty Duck Newsletter** | <https://www.feistyduck.com/newsletter/> | boletim de TLS/PKI; a melhor forma de acompanhar o campo |
| **Bóson Treinamentos** | <https://www.bosontreinamentos.com.br/> | referência técnica em português |

---

## 7. Como se manter atualizado

| Frequência | O quê |
|---|---|
| **semanal** | Feisty Duck Newsletter; `apt list --upgradable \| grep -i ssl` |
| **mensal** | Cloudflare Blog; Let's Encrypt Blog; rodar `testssl.sh` nos seus domínios |
| **trimestral** | CA/Browser Forum — ballots aprovados; Mozilla e Chrome root program |
| **quando sair** | novas RFCs do grupo TLS: <https://datatracker.ietf.org/wg/tls/documents/> |

---

## Autoteste

1. Qual RFC é **a** especificação do TLS 1.3, e quais RFCs de 2026 tratam de ECH?
2. Qual RFC define ACME? E qual define Certificate Transparency 2.0?
3. Onde estão as regras que as CAs públicas precisam seguir, e quem as escreve?
4. Qual paper mostra que a validação de certificados fora dos navegadores é amplamente quebrada?
5. Qual implementação de TLS é a mais legível para estudo, e por quê?
6. Onde consultar o registro oficial de cipher suites e extensões?
7. Cite três ferramentas online que não exigem instalar nada.
8. Qual boletim acompanhar para se manter atualizado em TLS?

*Respostas: §1.1/§1.3, §1.2, §2, §3.3, §5, §4 (IANA), §4, §6/§7.*

---

**Próximo:** [GLOSSARIO.md](GLOSSARIO.md).
