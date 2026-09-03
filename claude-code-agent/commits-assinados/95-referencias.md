# 95 · Referências — specs, papers, docs e código

> Nível: todos · Verificado em 13/08/2026

Fontes primárias. Quando houver conflito entre um blog e algo desta lista, esta lista vence.

---

## 1. Especificações e padrões

### OpenPGP

| Documento | O que é | Data |
|---|---|---|
| **[RFC 9580](https://www.rfc-editor.org/rfc/rfc9580.html)** | **OpenPGP atual** — a "crypto refresh" | julho de 2024 |
| [RFC 4880](https://www.rfc-editor.org/rfc/rfc4880.html) | OpenPGP anterior; ainda é o que a maioria das implantações fala | novembro de 2007 |
| [RFC 2440](https://www.rfc-editor.org/rfc/rfc2440.html) | o primeiro padrão OpenPGP | novembro de 1998 |
| [RFC 6637](https://www.rfc-editor.org/rfc/rfc6637.html) | curvas elípticas em OpenPGP | junho de 2012 |

### SSH

| Documento | O que é |
|---|---|
| **[`PROTOCOL.sshsig`](https://github.com/openssh/openssh-portable/blob/master/PROTOCOL.sshsig)** | **a especificação do formato de assinatura SSH.** Duas páginas. Leitura obrigatória para o [14](14-ssh-signing-a-fundo.md) |
| [`ssh-keygen(1)`](https://man.openbsd.org/ssh-keygen.1) | manual — seções `-Y sign`, `-Y verify`, `-Y find-principals`, e o formato do `allowed_signers` |
| [RFC 4251–4254](https://www.rfc-editor.org/rfc/rfc4251.html) | arquitetura do protocolo SSH |
| [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html) | **EdDSA (Ed25519)** — o algoritmo usado por padrão |
| [`PROTOCOL.certkeys`](https://github.com/openssh/openssh-portable/blob/master/PROTOCOL.certkeys) | certificados SSH ([14 § 4](14-ssh-signing-a-fundo.md)) |

### Outros

| Documento | O que é |
|---|---|
| [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322.html) | formato de mensagem — origem da convenção de cabeçalho com continuação recuada, usada no campo `gpgsig` |
| [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161.html) | carimbo de tempo — o que a assinatura sozinha **não** faz ([60 § 2](60-teoria-avancada.md)) |
| [FIPS 204 — ML-DSA](https://csrc.nist.gov/pubs/fips/204/final) | assinatura pós-quântica baseada em reticulados |
| [FIPS 205 — SLH-DSA](https://csrc.nist.gov/pubs/fips/205/final) | assinatura pós-quântica baseada em hash |
| [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962.html) | Certificate Transparency — a origem das árvores de Merkle e provas de inclusão do [60 § 5](60-teoria-avancada.md) |

---

## 2. Documentação oficial

### GitHub

| Página | Para quê |
|---|---|
| **[About commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification)** | o comportamento do selo, os estados, e a nota sobre verificação congelada |
| [Telling Git about your signing key](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key) | os comandos, por sistema operacional |
| [Displaying verification statuses for all of your commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/displaying-verification-statuses-for-all-of-your-commits) | vigilant mode |
| [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) | exigir assinatura ([18](18-politica-de-equipe.md)) |
| [REST — commits](https://docs.github.com/en/rest/commits/commits) | o objeto `verification` e os valores de `reason` |
| [REST — SSH signing keys](https://docs.github.com/en/rest/users/ssh-signing-keys) | `GET /users/{username}/ssh_signing_keys`, público |
| [Artifact attestations](https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds) | proveniência de build ([17](17-automacao-e-ci.md)) |
| [Changelog — SSH commit verification (23/08/2022)](https://github.blog/changelog/2022-08-23-ssh-commit-verification-now-supported/) | a data em que o assunto mudou |

### Git e GnuPG

| Recurso | Para quê |
|---|---|
| [`git-config` — seção `gpg.*`](https://git-scm.com/docs/git-config) | todas as opções de configuração |
| [`git-commit` — `-S`, `--no-gpg-sign`](https://git-scm.com/docs/git-commit) | — |
| [`git-log` — `%G?`, `%GS`, `%GK`, `%GF`, `%GT`](https://git-scm.com/docs/git-log) | os placeholders da tabela do [05](05-manual-de-uso.md) |
| [`git-verify-commit`](https://git-scm.com/docs/git-verify-commit) · [`git-verify-tag`](https://git-scm.com/docs/git-verify-tag) | verificação com código de saída |
| [Manual do GnuPG](https://www.gnupg.org/documentation/manuals/gnupg/) | referência completa |
| [GnuPG — notícias e ciclo de vida](https://www.gnupg.org/news.html) | onde se confirma que a série 2.4 saiu de suporte em 30/06/2026 |
| [OpenSSH — Release Notes](https://www.openssh.com/releasenotes.html) | onde se confirma o SSHSIG na 8.1 e o ML-DSA na 10.4 |

---

## 3. Papers

| Paper | Autores | Ano | Por que importa |
|---|---|---|---|
| **[SHA-1 is a Shambles](https://eprint.iacr.org/2020/014)** | Gaëtan Leurent, Thomas Peyrin | 2020 | primeira colisão de **prefixo escolhido** em SHA-1, complexidade ~2⁶³·⁴; a aplicação demonstrada foi contra a **rede de confiança do PGP** |
| **[SHAttered](https://shattered.io/)** | Marc Stevens et al. (Google + CWI) | 2017 | primeira colisão prática de SHA-1 |
| [The first collision for full SHA-1](https://link.springer.com/chapter/10.1007/978-3-319-63688-7_19) | Stevens et al. | 2017 | a versão acadêmica do anterior |
| [Finding Collisions in the Full SHA-1](https://link.springer.com/chapter/10.1007/11535218_2) | Wang, Yin, Yu | 2005 | o ataque teórico que iniciou tudo |
| [New directions in cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf) | Diffie, Hellman | 1976 | a origem da criptografia de chave pública |
| [A method for obtaining digital signatures...](https://people.csail.mit.edu/rivest/Rsapaper.pdf) | Rivest, Shamir, Adleman | 1978 | RSA |
| [High-speed high-security signatures](https://ed25519.cr.yp.to/ed25519-20110926.pdf) | Bernstein et al. | 2011 | **Ed25519** |
| [Algorithms for quantum computation](https://ieeexplore.ieee.org/document/365700) | Peter Shor | 1994 | por que a criptografia atual cai com computador quântico |
| [Sigstore: Software Signing for Everybody](https://dl.acm.org/doi/10.1145/3548606.3560596) | Newman, Meyers, Torres-Arias et al. | 2022 | o desenho de assinatura sem chave, CCS 2022 |
| [in-toto: Providing farm-to-table guarantees](https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias) | Torres-Arias et al. | 2019 | proveniência de cadeia de suprimentos |

---

## 4. Código-fonte — quando a documentação não basta

| Onde | O que ver |
|---|---|
| [`gpg-interface.c`](https://github.com/git/git/blob/master/gpg-interface.c) | **o coração do assunto no Git**: como ele chama `gpg` e `ssh-keygen`, e como traduz a saída nos códigos de `%G?` |
| [`commit.c`](https://github.com/git/git/blob/master/commit.c) | montagem do objeto commit e inserção do campo `gpgsig` |
| [`sha1collisiondetection`](https://github.com/cr-marcstevens/sha1collisiondetection) | a biblioteca que salva o Git do SHA-1 ([60 § 3](60-teoria-avancada.md)) |
| [`sshsig.c`](https://github.com/openssh/openssh-portable/blob/master/sshsig.c) | implementação do SSHSIG |
| [`sigstore/gitsign`](https://github.com/sigstore/gitsign) | assinatura sem chave |
| [`sigstore/rekor`](https://github.com/sigstore/rekor) | o log de transparência |

**Dica de leitura:** se você quiser entender de verdade a tabela de `%G?`, abra
`gpg-interface.c` e procure por `GPG_STATUS_` e pelas constantes de saída. São umas cinquenta
linhas e valem mais que qualquer explicação de terceiros — inclusive a minha.

---

## 5. Pessoas e projetos para acompanhar

| Quem | Por quê |
|---|---|
| **Junio Hamano** | mantenedor do Git desde 2005; as notas de release dele são a fonte sobre o que muda |
| **Fabian Stelzer** | autor da implementação de assinatura SSH no Git (2.34) |
| **Werner Koch** (g10 Code) | autor e mantenedor do GnuPG |
| **Damien Miller**, **Theo de Raadt** e o time OpenBSD | OpenSSH |
| **Marc Stevens** (CWI) | criptanálise do SHA-1 e a biblioteca de detecção de colisão |
| **OpenSSF** | Open Source Security Foundation — cursos, Scorecard, SLSA |
| **Sigstore** | assinatura sem chave |

---

## 6. Ferramentas mencionadas no curso

| Ferramenta | Onde | Para quê |
|---|---|---|
| `gh` | <https://cli.github.com/> | cadastrar chaves, consultar o veredito do GitHub |
| `gitsign` | <https://github.com/sigstore/gitsign> | assinatura sem chave |
| `cosign` | <https://github.com/sigstore/cosign> | assinar artefatos e imagens |
| `git-filter-repo` | <https://github.com/newren/git-filter-repo> | reescrever histórico (com cuidado) |
| Secretive | <https://github.com/maxgoedjen/secretive> | chave no Secure Enclave (macOS) |
| Gpg4win | <https://gpg4win.org/> | GnuPG no Windows |
| SLSA | <https://slsa.dev/> | níveis de proveniência de build |

---

## 7. Onde confirmar versões e datas

| O quê | Onde |
|---|---|
| Git | <https://git-scm.com/> · notas de release do mantenedor |
| OpenSSH | <https://www.openssh.com/releasenotes.html> |
| GnuPG | <https://www.gnupg.org/news.html> e `/download` |
| Gpg4win | <https://gpg4win.org/change-history.html> |
| GitHub CLI | <https://github.com/cli/cli/releases> |
| gitsign | <https://github.com/sigstore/gitsign/releases> |
| Cyber Resilience Act | <https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act> |

---

## Autoteste

1. Qual RFC define o OpenPGP atual, e de quando é?
2. Onde está a especificação do formato de assinatura SSH?
3. Qual arquivo do código do Git traduz a saída do verificador nos códigos de `%G?`?
4. Qual paper demonstrou colisão de prefixo escolhido em SHA-1, e contra o que ele foi
   aplicado?
5. Qual endpoint da API do GitHub devolve as chaves de **assinatura** de um usuário, sem
   autenticação?
6. Onde se confirma que a série 2.4 do GnuPG saiu de suporte?

*(Respostas: 1 — RFC 9580, de julho de 2024. 2 — `PROTOCOL.sshsig`, no repositório do OpenSSH.
3 — `gpg-interface.c`. 4 — *SHA-1 is a Shambles* (Leurent & Peyrin, 2020), aplicado à rede de
confiança do PGP. 5 — `GET /users/{username}/ssh_signing_keys`. 6 — gnupg.org/news.html.)*

---

**Próximo:** [GLOSSARIO.md](GLOSSARIO.md).
