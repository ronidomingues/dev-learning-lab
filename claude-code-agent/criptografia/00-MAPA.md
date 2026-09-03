# Criptografia — mapa do curso

**Última atualização:** 19/08/2026 · **Status:** Bloco A completo · Bloco B em produção

Do zero absoluto (o que é uma cifra) até o nível de pesquisa (provas de
segurança, reticulados, fronteira pós-quântica). Português do Brasil, termos
técnicos em inglês quando é assim que o campo os usa.

---

## Roteiro de leitura

**Se você nunca ouviu falar do assunto:** 01 → 02 → 03 → 04 → 10 → 11.
**Se você programa e quer usar direito hoje:** 04 → 05 → 06 → 07 → 13 → 15 → 75.
**Se você quer entender por dentro:** 10 → 12 → 13 → 14 → 17 → 18 → 19 → 20.
**Se você quer nível de pesquisa:** 60 → 65 → 90 → 95.

---

## Estado dos arquivos

### Bloco A · Porta de entrada — ✅ completo

| Arquivo | Conteúdo |
|---|---|
| [01-introducao-leigo.md](01-introducao-leigo.md) | o que é, sem jargão: bilhete, tintas, cadeado, impressão digital |
| [02-pre-requisitos.md](02-pre-requisitos.md) | o que saber e ter; tempo realista; rota de resgate |
| [03-instalacao.md](03-instalacao.md) | manual de campo: Python, OpenSSL, GnuPG, age, bibliotecas, nos três SOs |
| [04-como-comecar.md](04-como-comecar.md) | do ambiente pronto a assinar, cifrar e espiar TLS, com saídas reais |
| [05-manual-de-uso.md](05-manual-de-uso.md) | referência por tarefa: OpenSSL, GPG, age, Python; o que está obsoleto |
| [06-exemplos.md](06-exemplos.md) | 13 exemplos executados, 3 deles de produção |
| [07-projeto-modelo/](07-projeto-modelo/README.md) | `cofre`: ChaCha20-Poly1305 + X25519 + scrypt em Python puro, 46 testes |

### Bloco B · Núcleo — 🟡 em produção

| Arquivo | Estado |
|---|---|
| [10-fundamentos.md](10-fundamentos.md) | ✅ vocabulário, níveis de segurança, modelo de ameaça, o que "provado seguro" significa |
| [11-historia.md](11-historia.md) | ✅ de al-Kindi ao pós-quântico, com as lições que ainda valem |
| 12-criptografia-simetrica.md | ⬜ AES por dentro, ChaCha20, cifras de bloco e de fluxo |
| 13-modos-e-aead.md | ⬜ ECB/CBC/CTR/GCM, AEAD, limites de uso por chave |
| 14-funcoes-hash.md | ⬜ Merkle–Damgård, esponja, aniversário, extensão de comprimento |
| 15-mac-e-derivacao-de-chaves.md | ⬜ HMAC, Poly1305, HKDF, scrypt/Argon2 |
| 16-aleatoriedade.md | ⬜ entropia, CSPRNG, falhas reais |
| 17-chave-publica-rsa.md | ⬜ teoria dos números do zero, prova do RSA, preenchimento, ataques |
| 18-curvas-elipticas.md | ⬜ lei de grupo, ECDLP, Curve25519 |
| 19-assinaturas-e-acordo.md | ⬜ DH, ECDSA, EdDSA, falhas de nonce |
| 20-tls-por-dentro.md | ⬜ handshake 1.3 mensagem a mensagem |
| 21-pki-e-certificados.md | ⬜ X.509, cadeias, CT, ACME, prazos de 2026 |
| 22-senhas-e-armazenamento.md | ⬜ hash de senha, cifragem de disco, gestão de segredos |
| 23-criptografia-de-ponta-a-ponta.md | ⬜ Signal, X3DH/PQXDH, duplo catraca, MLS |
| 24-gerenciamento-de-chaves.md | ⬜ ciclo de vida, KMS, HSM, rotação |
| 25-canais-laterais-e-implementacao.md | ⬜ tempo, cache, energia, falhas; código de tempo constante |
| 26-protocolos-avancados.md | ⬜ conhecimento zero, MPC, FHE, limiar |
| 60-teoria-avancada.md | ⬜ jogos IND-CPA/CCA, reduções, oráculo aleatório, reticulados |
| 65-estado-da-arte.md | ⬜ situação em agosto de 2026 |

### Blocos C, D, E — ⬜ pendentes

| Arquivo | Estado |
|---|---|
| 70-pratica.md | ⬜ laboratórios progressivos |
| 75-armadilhas.md | ⬜ erros clássicos e mitos |
| 80-custos-e-licencas.md | ⬜ KMS, HSM, chaves em hardware, licenças |
| 85-cursos-e-certificacoes.md | ⬜ cursos PT/EN/FR e certificações |
| 90-bibliografia.md | ⬜ livros comentados |
| 95-referencias.md | ⬜ RFCs, FIPS, papers |
| GLOSSARIO.md | ⬜ |

---

## O que você saberá ao final

- Explicar cada peça sem jargão e escolher a certa para cada problema.
- Usar OpenSSL, GPG e `age` com segurança, e revisar código alheio.
- Ler um handshake TLS 1.3 e uma cadeia de certificados.
- Implementar e testar primitivas contra vetores oficiais.
- Discutir a migração pós-quântica com números e prazos.
- Acompanhar a literatura de pesquisa do campo.
