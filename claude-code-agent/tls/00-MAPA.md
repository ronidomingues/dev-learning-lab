# TLS — mapa do curso

**Última atualização:** 31/08/2026 · **Nível global:** do leigo total à pesquisa
**Status:** Blocos A, B, C, D e E completos

TLS (*Transport Layer Security*, "segurança da camada de transporte") é o protocolo
que põe o **S** no HTTPS. É a peça de criptografia mais usada do planeta: praticamente
todo byte que sai do seu navegador passa por ele.

Este curso vai da analogia do envelope lacrado até a análise formal do handshake,
passando por instalar tudo, configurar nginx/Caddy/Node/Python, emitir certificados
com Let's Encrypt, montar uma CA interna, fazer mTLS, e entender por que o
certificado que durava 1 ano agora dura 200 dias — e vai durar 47.

---

## O que você saberá ao final

1. Explicar para um leigo o que TLS resolve e por que existe.
2. Ler um handshake TLS 1.3 pacote a pacote e dizer o que cada mensagem faz.
3. Emitir, instalar, renovar e revogar certificados — públicos (ACME) e internos (CA própria).
4. Configurar TLS corretamente em nginx, Apache, Caddy, HAProxy, Node.js e Python.
5. Implementar mTLS (autenticação mútua) entre serviços.
6. Diagnosticar falhas de TLS com `openssl s_client`, `curl -v`, `testssl.sh` e Wireshark.
7. Saber quais ataques históricos existiram, o que cada um explorou, e o que sobrou deles hoje.
8. Entender a criptografia por baixo: KEM, AEAD, HKDF, assinatura, sigilo futuro.
9. Explicar a transição pós-quântica (ML-KEM híbrido) e o que ela muda na prática.
10. Estimar custo real de TLS — em dinheiro, em CPU e em trabalho operacional.

---

## Roteiro de leitura

| Se você… | Leia nesta ordem |
|---|---|
| nunca ouviu falar do assunto | 01 → 10 → 11 → 13 |
| precisa colocar HTTPS no ar **hoje** | 03 → 04 → 16 → 17 → 75 |
| é dev e quer usar direito | 04 → 05 → 06 → 07 → 12 → 13 → 21 → 75 |
| é sysadmin/SRE | 03 → 16 → 17 → 15 → 20 → 70 → 75 |
| quer entender por dentro | 10 → 12 → 14 → 13 → 15 → 60 |
| quer nível de pesquisa | 60 → 65 → 90 → 95 |
| vai fazer PKI interna / mTLS | 13 → 18 → 07-projeto-modelo → 70 |

---

## Estado dos arquivos

### Bloco A · Porta de entrada (01–09) — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | iniciante | o que é, sem jargão: o cartão-postal, o envelope, o cartório |
| [02-pre-requisitos.md](02-pre-requisitos.md) | iniciante | o que saber e ter antes; tempo realista; rota de resgate |
| [03-instalacao.md](03-instalacao.md) | iniciante | manual de campo: OpenSSL, curl, mkcert, certbot, nginx, Caddy, Wireshark, testssl.sh, nos três SOs |
| [04-como-comecar.md](04-como-comecar.md) | iniciante | do ambiente pronto ao primeiro HTTPS funcionando, com saídas reais |
| [05-manual-de-uso.md](05-manual-de-uso.md) | intermediário | referência por tarefa: `openssl`, `curl`, `certbot`, diretivas de servidor |
| [06-exemplos.md](06-exemplos.md) | intermediário | 14 exemplos completos e executáveis, 3 de produção |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | intermediário | `cofre-tls`: CA própria + servidor/cliente mTLS em Python puro, com testes |

### Bloco B · Núcleo (10–69) — ✅ completo

| Arquivo | Nível | Conteúdo |
|---|---|---|
| [10-fundamentos.md](10-fundamentos.md) | iniciante | as 4 garantias, o modelo de ameaça, o vocabulário inteiro |
| [11-historia.md](11-historia.md) | iniciante | de SSL 1.0 (nunca lançado) ao TLS 1.3 e ao pós-quântico |
| [12-handshake.md](12-handshake.md) | intermediário | o handshake TLS 1.3 mensagem a mensagem, byte a byte, com bytes reais |
| [13-certificados-e-pki.md](13-certificados-e-pki.md) | intermediário | X.509 campo a campo, cadeia, âncoras de confiança, quem confia em quem e por quê |
| [14-criptografia-do-tls.md](14-criptografia-do-tls.md) | avançado | cipher suites, KEM, AEAD, HKDF, sigilo futuro, escalonamento de chaves |
| [15-validacao-revogacao-transparencia.md](15-validacao-revogacao-transparencia.md) | avançado | CRL, OCSP, stapling, CT logs, por que revogação nunca funcionou |
| [16-acme-e-automacao.md](16-acme-e-automacao.md) | intermediário | ACME, Let's Encrypt, certbot, Caddy, certificados de 6 dias e de IP |
| [17-configuracao-de-servidores.md](17-configuracao-de-servidores.md) | intermediário | nginx, Apache, Caddy, HAProxy, Node, Python, Java — configuração real e comentada |
| [18-mtls-e-pki-interna.md](18-mtls-e-pki-interna.md) | avançado | autenticação mútua, CA interna, SPIFFE, service mesh, rotação |
| [19-tls-alem-do-https.md](19-tls-alem-do-https.md) | avançado | SMTP/STARTTLS, DoT/DoH, QUIC e HTTP/3, MQTT, LDAPS, VPN |
| [20-desempenho-e-operacao.md](20-desempenho-e-operacao.md) | avançado | retomada de sessão, 0-RTT, custo de CPU, terminação, observabilidade |
| [21-ataques-e-defesas.md](21-ataques-e-defesas.md) | avançado | BEAST a Heartbleed a Raccoon: o que cada um explorou e o que sobrou |
| [60-teoria-avancada.md](60-teoria-avancada.md) | pesquisa | modelo ACCE, verificação formal (Tamarin, miTLS), provas do TLS 1.3 |
| [65-estado-da-arte.md](65-estado-da-arte.md) | pesquisa | ago/2026: ML-KEM híbrido, ECH RFC 9849, 200 dias, assinaturas PQ |

### Bloco C · Prática e erros (70–79) — ✅ completo

| Arquivo | Conteúdo |
|---|---|
| [70-pratica.md](70-pratica.md) | 12 laboratórios progressivos, do primeiro certificado ao MITM controlado |
| [75-armadilhas.md](75-armadilhas.md) | 28 armadilhas clássicas + 12 mitos que não morrem |

### Bloco D · Economia e ecossistema (80–89) — ✅ completo

| Arquivo | Conteúdo |
|---|---|
| [80-custos-e-licencas.md](80-custos-e-licencas.md) | preços com data de consulta (28–31/08/2026), licenças, custo oculto, quem paga a conta do Let's Encrypt |
| [85-cursos-e-certificacoes.md](85-cursos-e-certificacoes.md) | cursos gratuitos PT/EN/FR pesquisados na web, certificações e o que valem |

### Bloco E · Fontes (90–99) — ✅ completo

| Arquivo | Conteúdo |
|---|---|
| [90-bibliografia.md](90-bibliografia.md) | livros com edição real, nível e o que envelheceu |
| [95-referencias.md](95-referencias.md) | RFCs, papers, código-fonte, ferramentas, pessoas a seguir |
| [GLOSSARIO.md](GLOSSARIO.md) | ~150 termos definidos |

---

## Assuntos vizinhos nesta pasta

- [criptografia](../criptografia/00-MAPA.md) — as primitivas que o TLS usa (AES, curvas, HMAC, KDF).
- [jwt](../jwt/00-MAPA.md) — token de autenticação que **depende** de TLS para ser seguro.
- [portas-de-rede](../portas-de-rede/00-MAPA.md) — 443, 853, 465, 993 e companhia.
- [commits-assinados](../commits-assinados/00-MAPA.md) — assinatura digital fora do TLS.
- [hospedagem-de-aplicacoes-web](../hospedagem-de-aplicacoes-web/00-MAPA.md) — onde o TLS vai morar.
- [variaveis-de-ambiente-e-segredos](../variaveis-de-ambiente-e-segredos/00-MAPA.md) — onde guardar a chave privada.

---

## Ambiente em que este material foi verificado

| Item | Versão | Como conferi |
|---|---|---|
| Sistema | Ubuntu 22.04.5 LTS | `/etc/os-release` |
| OpenSSL | 3.0.2 (15/03/2022) | `openssl version` |
| curl | 7.81.0, libcurl com OpenSSL 3.0.2 | `curl --version` |
| Python | 3.10.12 | `python3 --version` |
| Node.js | v24.18.0 | `node --version` |
| Docker | 29.7.2 | `docker --version` |

Data da verificação: **31/08/2026**. Onde uma versão mais nova muda o comportamento
(ex.: ML-KEM só existe no OpenSSL 3.5+), o texto avisa explicitamente.
