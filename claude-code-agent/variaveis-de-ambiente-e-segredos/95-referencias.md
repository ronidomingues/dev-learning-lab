# 95 · Referências — specs, docs oficiais, código-fonte e papers

`Nível: todos` · `Atualizado em: 14/08/2026`

Fontes primárias. Quando houver divergência entre este curso e uma destas, **a fonte
primária ganha** — e me avise.

---

## 1. Especificações e normas

| Documento | Onde | O que define |
|---|---|---|
| **POSIX.1-2017 / IEEE 1003.1** | [pubs.opengroup.org/onlinepubs/9699919799](https://pubs.opengroup.org/onlinepubs/9699919799/) | `environ`, `getenv`, `execve`, a convenção de nomes |
| **`man 7 environ`** | `man 7 environ` | a lista das variáveis padronizadas e o comportamento |
| **`man 2 execve`** | `man 2 execve` | ⭐ **a fonte primária de tudo neste curso**: como o ambiente é entregue |
| **`man 5 proc`** | `man 5 proc` | `/proc/[pid]/environ` e suas limitações |
| **`sysexits.h`** | `/usr/include/sysexits.h` | os códigos de saída, inclusive `EX_CONFIG = 78` |
| **RFC 3986** | [rfc-editor.org/rfc/rfc3986](https://www.rfc-editor.org/rfc/rfc3986) | URI — por que uma senha com `@` quebra a `DATABASE_URL` |
| **RFC 7519 / 7515** | rfc-editor.org | JWT e JWS — base de OIDC e SVID |
| **NIST SP 800-38D** | [csrc.nist.gov](https://csrc.nist.gov/publications/detail/sp/800-38d/final) | AES-GCM, e a exigência de nonce único |
| **NIST SP 800-57** | csrc.nist.gov | gestão de chaves: tamanhos, prazos, ciclo de vida |
| **NIST SP 800-63B** | [pages.nist.gov/800-63-3/sp800-63b.html](https://pages.nist.gov/800-63-3/sp800-63b.html) | autenticação; a posição contra rotação periódica forçada |
| **Lei 13.709/2018 (LGPD)** | [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm) | obrigações em caso de vazamento de dados pessoais |
| **Resoluções da ANPD sobre incidentes** | [gov.br/anpd](https://www.gov.br/anpd/pt-br) | prazo e forma de comunicação de incidente |
| **PCI-DSS v4.0** | pcisecuritystandards.org | requisitos 3 e 8 — armazenamento e rotação de credenciais |

**Não existe especificação para o formato `.env`.** Isso é um fato, não um descuido
desta lista — ver [12-formato-dotenv.md §7](12-formato-dotenv.md).

---

## 2. Documentação oficial

### Runtimes

| Plataforma | Link |
|---|---|
| Node.js — `--env-file` e `process.loadEnvFile` | [nodejs.org/api/cli.html](https://nodejs.org/api/cli.html#--env-fileconfig) |
| Python — `os.environ` | [docs.python.org/3/library/os.html](https://docs.python.org/3/library/os.html#os.environ) |
| PHP — `getenv` e `variables_order` | [php.net/manual/pt_BR/function.getenv.php](https://www.php.net/manual/pt_BR/function.getenv.php) · [php.net/manual/ini.core.php](https://www.php.net/manual/en/ini.core.php#ini.variables-order) |
| Java — `System.getenv` | docs.oracle.com |
| Go — pacote `os` | [pkg.go.dev/os](https://pkg.go.dev/os) |
| Rust — `std::env` | [doc.rust-lang.org/std/env](https://doc.rust-lang.org/std/env/) |
| .NET — Configuration | [learn.microsoft.com](https://learn.microsoft.com/aspnet/core/fundamentals/configuration/) |

### Frameworks

| Framework | Link |
|---|---|
| Spring Boot — Externalized Configuration | docs.spring.io |
| Laravel — Configuration | laravel.com/docs/configuration |
| Symfony — Configuring Environments / Secrets | symfony.com/doc/current/configuration.html |
| Django — Settings | docs.djangoproject.com |
| Next.js — Environment Variables | nextjs.org/docs |
| Vite — Env Variables and Modes | vite.dev/guide/env-and-mode |

### Plataformas

| Plataforma | Link |
|---|---|
| Docker — secrets em build e runtime | [docs.docker.com/build/building/secrets](https://docs.docker.com/build/building/secrets/) |
| Docker Swarm — secrets | docs.docker.com/engine/swarm/secrets |
| Kubernetes — Secrets | [kubernetes.io/docs/concepts/configuration/secret](https://kubernetes.io/docs/concepts/configuration/secret/) |
| Kubernetes — Encrypting Data at Rest | [kubernetes.io/docs/tasks/administer-cluster/encrypt-data](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) |
| Kubernetes — KMS provider (v2) | kubernetes.io/docs/tasks/administer-cluster/kms-provider |
| systemd — `systemd.exec` (Environment, LoadCredential) | [freedesktop.org/software/systemd/man/systemd.exec.html](https://www.freedesktop.org/software/systemd/man/systemd.exec.html) |
| systemd — `systemd-creds` | freedesktop.org/software/systemd/man/systemd-creds.html |
| AWS Secrets Manager | docs.aws.amazon.com/secretsmanager |
| AWS — IMDSv2 | docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html |
| Google Secret Manager | cloud.google.com/secret-manager/docs |
| Azure Key Vault | learn.microsoft.com/azure/key-vault |
| GitHub Actions — security hardening | [docs.github.com/actions/security-guides](https://docs.github.com/en/actions/security-guides) |
| GitHub — OIDC | docs.github.com/actions/deployment/security-hardening-your-deployments |
| GitLab CI — variables | docs.gitlab.com/ee/ci/variables |

---

## 3. Código-fonte que vale ler

Ler o código é a forma mais rápida de acabar com dúvida sobre comportamento.

| Projeto | Onde | O que ver |
|---|---|---|
| **Node — carregador de `.env`** | github.com/nodejs/node · `src/node_dotenv.cc` | o parser nativo, em C++. ~200 linhas. Explica por que `#` trunca o valor |
| **`dotenv`** | [github.com/motdotla/dotenv](https://github.com/motdotla/dotenv) | a regex de parsing; compare com a do Node |
| **`python-dotenv`** | [github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) | o parser, e a implementação da expansão de variáveis |
| **`vlucas/phpdotenv`** | [github.com/vlucas/phpdotenv](https://github.com/vlucas/phpdotenv) | leia o `UPGRADING.md` antes de atualizar |
| **SOPS** | [github.com/getsops/sops](https://github.com/getsops/sops) | a implementação da criptografia de envelope |
| **age** | [github.com/FiloSottile/age](https://github.com/FiloSottile/age) | ~1.000 linhas. Exemplo de projeto criptográfico legível |
| **OpenBao** | [github.com/openbao/openbao](https://github.com/openbao/openbao) | motores de segredos e métodos de autenticação |
| **gitleaks** | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | as regras em `config/gitleaks.toml` — útil para escrever as suas |
| **External Secrets Operator** | [github.com/external-secrets/external-secrets](https://github.com/external-secrets/external-secrets) | o laço de reconciliação |
| **SPIRE** | [github.com/spiffe/spire](https://github.com/spiffe/spire) | atestação de carga de trabalho, na prática |

---

## 4. Papers

| Paper | Autores | Ano | Por que importa |
|---|---|---|---|
| *On the (Im)possibility of Obfuscating Programs* | Barak, Goldreich, Impagliazzo, Rudich, Sahai, Vadhan, Yang | 2001 | ⭐ prova que ofuscação de caixa preta é impossível. **É o teorema por trás de "não existe segredo no front-end"** |
| *Candidate Indistinguishability Obfuscation…* | Garg, Gentry, Halevi, Raykova, Sahai, Waters | 2013 | introduz iO como noção alcançável |
| *Indistinguishability Obfuscation from Well-Founded Assumptions* | Jain, Lin, Sahai | 2021 (STOC) | marco teórico; ainda impraticável |
| *A Fully Homomorphic Encryption Scheme* | Craig Gentry | 2009 | tese que abriu a FHE |
| *How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories* | Meli, McNiece, Reaves | 2019 (NDSS) | ⭐ **o estudo empírico definitivo sobre vazamento no GitHub.** Mede escala e velocidade da exploração |
| *Argon2: New Generation of Memory-Hard Functions* | Biryukov, Dinu, Khovratovich | 2016 | a função de derivação recomendada hoje |
| *Foreshadow / SGAxe / ÆPIC Leak* | vários | 2018–2022 | os ataques que quebraram o Intel SGX repetidamente — a nota de ceticismo de [60 §6.4](60-teoria-avancada.md) |

---

## 5. Vulnerabilidades históricas que ensinam

| CVE / caso | Ano | Lição |
|---|---|---|
| **CVE-2014-6271 (Shellshock)** | 2014 | variável de ambiente vira execução de código. Origem: CGI colocando dado do usuário no ambiente ([11 §2](11-historia.md)) |
| **Capital One** | 2019 | SSRF + IMDSv1 → credenciais da instância → ~100 milhões de registros. Motivo pelo qual **IMDSv2 é obrigatório** |
| **Codecov bash uploader** | 2021 | script de CI comprometido exfiltrou variáveis de ambiente de milhares de pipelines. Motivo de fixar dependências por hash |
| **Pacotes npm comprometidos que varrem `process.env`** | recorrente | por que o CI não deve ter mais segredos do que precisa, e por que `postinstall` é perigoso |
| **CVE em `python-dotenv` (`set_key` seguindo symlink)** | corrigido na 1.2.2 | até a biblioteca de segredos tem falha; mantenha atualizado |

---

## 6. Pessoas e organizações para acompanhar

| Quem | Onde | Por quê |
|---|---|---|
| **OWASP** | owasp.org | Top 10, Cheat Sheets, ASVS |
| **CNCF TAG Security** | tag-security.cncf.io | avaliações de segurança de projetos (SOPS, ESO) |
| **Filippo Valsorda** | filippo.io | autor do `age`; escreve com clareza rara sobre criptografia aplicada |
| **Jean-Philippe Aumasson** | aumasson.jp | autor de *Serious Cryptography* |
| **Bruce Schneier** | schneier.com | segurança como sistema socioeconômico, não só técnico |
| **Tavis Ormandy / Project Zero** | googleprojectzero.blogspot.com | como falhas reais são encontradas |
| **CERT.br / NIC.br** | cert.br | incidentes e boas práticas no contexto brasileiro |
| **ANPD** | gov.br/anpd | regulamentação de LGPD, inclusive incidentes |

---

## 7. Ferramentas citadas neste curso

| Ferramenta | Repositório | Licença |
|---|---|---|
| SOPS | github.com/getsops/sops | MPL 2.0 |
| age | github.com/FiloSottile/age | BSD-3 |
| gitleaks | github.com/gitleaks/gitleaks | MIT |
| trufflehog | github.com/trufflesecurity/trufflehog | AGPL-3.0 |
| OpenBao | github.com/openbao/openbao | MPL 2.0 |
| External Secrets Operator | github.com/external-secrets/external-secrets | Apache 2.0 |
| Sealed Secrets | github.com/bitnami-labs/sealed-secrets | Apache 2.0 |
| SPIRE | github.com/spiffe/spire | Apache 2.0 |
| direnv | github.com/direnv/direnv | MIT |
| git-filter-repo | github.com/newren/git-filter-repo | MIT |
| pre-commit | github.com/pre-commit/pre-commit | MIT |
| mise | github.com/jdx/mise | MIT |

---

## 8. Como verificar uma afirmação deste curso

1. **Comportamento de runtime:** reproduza. Todo experimento deste curso tem o comando.
2. **Versão de ferramenta:** `<ferramenta> --version` na sua máquina. As versões aqui
   são de 14/08/2026.
3. **Preço:** vá à página oficial de preços. Preço sem data é desinformação, e a
   data de todos os preços deste curso é 14/08/2026.
4. **Licença:** leia o `LICENSE` do repositório, não o blog que fala dele.
5. **Comportamento do sistema operacional:** `man`. É a fonte primária.

---

## Autoteste

1. Qual página de `man` é a fonte primária de tudo neste curso, e por quê?
2. Onde está definido o código de saída 78, e o que ele significa?
3. Existe especificação para o formato `.env`? Qual é a consequência prática disso?
4. Qual RFC explica por que uma senha com `@` quebra a `DATABASE_URL`?
5. Qual documento do NIST desaconselha rotação periódica forçada, e para que tipo de credencial?
6. Qual paper de 2001 é o teorema por trás de "não existe segredo no front-end"?
7. Qual estudo mede empiricamente a escala e a velocidade do vazamento de segredos no GitHub?
8. Que lição o incidente da Capital One (2019) deixou sobre metadados de instância?
9. Onde você confirma a licença de um projeto: no repositório ou no blog que fala dele? Por quê?

---

**Próximo:** [GLOSSARIO.md](GLOSSARIO.md) · Voltar ao [mapa](00-MAPA.md)
