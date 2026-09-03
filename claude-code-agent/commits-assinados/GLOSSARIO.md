# Glossário

> Todos os termos técnicos usados no curso, definidos. Termos em inglês aparecem como o campo
> os usa, com tradução. Atualizado em 13/08/2026.

---

## A

**Agente (agent)** — programa que guarda a chave privada destravada em memória, para você não
digitar a frase secreta a cada operação. Ver `gpg-agent`, `ssh-agent`, e
[16](16-hardware-e-agentes.md).

**`allowed_signers`** — arquivo que liga chaves públicas SSH a rótulos de identidade
(*principals*), usado na verificação **local**. O Git o encontra por
`gpg.ssh.allowedSignersFile`. Não é consultado pelo GitHub.

**Armor (ASCII armor)** — codificação em texto de dados binários OpenPGP, delimitada por
`-----BEGIN ...-----` e `-----END ...-----`. Serve para colar chave em formulário.

**Assimétrica (criptografia)** — esquema com duas chaves distintas e relacionadas, uma pública
e uma privada. Oposto de simétrica, que usa a mesma chave para tudo.

**Assinatura digital** — valor calculado a partir do resumo de uma mensagem e de uma chave
privada, verificável com a chave pública correspondente.

**Atestação (attestation)** — declaração assinada sobre um artefato: quem o produziu, a partir
de qual código, com qual pipeline. Ver *proveniência*, SLSA, in-toto.

**Autenticação** — provar quem você é para obter acesso. **Não** é o mesmo que assinar: uma
protege a porta, a outra o conteúdo.

**Autoridade certificadora (CA)** — entidade em quem se confia para afirmar que uma chave
pertence a uma identidade. No contexto deste curso, o GitHub é a CA de fato.

## B

**Bad signature** — assinatura que não confere com o conteúdo. Código `%G?` = `B`. **Não
acontece por acidente.**

**Branch protection rule** — mecanismo antigo do GitHub para proteger ramos. Substituído na
prática pelos *rulesets*.

## C

**Certificado de revogação** — documento OpenPGP, gerado junto com a chave, que permite
declará-la inválida mesmo sem ter mais a chave privada. Fica em
`~/.gnupg/openpgp-revocs.d/`, com as linhas prefixadas por `:` por segurança.

**Certificado SSH** — chave pública assinada por uma autoridade, com validade e principais
embutidos. Permite que o `allowed_signers` tenha uma linha só para uma organização inteira.

**`cert-authority`** — opção do `allowed_signers` que marca uma chave como autoridade emissora
de certificados.

**Chave primária (mestra)** — no OpenPGP, a chave que define a identidade e pode certificar
subchaves e UIDs. Idealmente mantida offline.

**Chave privada** — a metade secreta do par. Assina. Nunca sai da sua máquina (ou do token).

**Chave pública** — a metade distribuível. Verifica. Pode ir para qualquer lugar.

**Colisão** — duas entradas diferentes com o mesmo resumo de hash.

**Colisão de prefixo escolhido** — colisão em que o atacante escolhe livremente os dois começos
das mensagens. Muito mais perigosa que a de prefixo idêntico. Demonstrada em SHA-1 em 2020.

**Committer** — quem aplicou o commit; pode diferir do *author* em rebase, cherry-pick e patch
por e-mail.

**`commit.gpgsign`** — configuração do Git que assina todo commit automaticamente.

**Cosign** — ferramenta do Sigstore para assinar artefatos e imagens de container.

## D

**DCO (Developer Certificate of Origin)** — declaração de que você tem o direito de contribuir
aquele código, expressa pela linha `Signed-off-by:` (`git commit -s`). **Texto, sem nenhuma
criptografia.** Não confundir com assinatura (`-S`).

**Digest** — ver *resumo*.

## E

**Ed25519** — esquema de assinatura sobre a curva Edwards25519. Padrão atual: rápido, chaves
de 256 bits, assinaturas de 64 bytes, sem parâmetros a escolher.

**EUF-CMA** — *Existential Unforgeability under Chosen Message Attack*: a propriedade formal de
segurança exigida de um esquema de assinatura. Ver [60 § 1](60-teoria-avancada.md).

**Expiração** — data a partir da qual uma chave deixa de ser aceita. Nativa no OpenPGP;
inexistente em chave SSH (fica no `allowed_signers`).

## F

**FIDO2 / `sk-ssh-ed25519`** — chave SSH cuja privada vive dentro de um token de hardware. O
arquivo em disco é apenas um identificador.

**Fulcio** — autoridade do Sigstore que emite certificados de curta duração a partir de
identidade OIDC.

## G

**`gpgsig`** — o campo do objeto commit onde a assinatura é guardada. Chama-se assim mesmo
quando a assinatura é SSH, por compatibilidade retroativa desde 2012.

**`gpg-agent`** — o agente do GnuPG.

**`gpg.format`** — configuração do Git: `openpgp` (padrão), `ssh` ou `x509`.

**`GPG_TTY`** — variável de ambiente que diz ao GnuPG em qual terminal pedir a frase secreta.
Sua ausência causa `Inappropriate ioctl for device`.

**GnuPG / GPG** — GNU Privacy Guard: a implementação livre do padrão OpenPGP.

## H

**Hash (função de hash criptográfica)** — função que transforma entrada de tamanho arbitrário
em saída de tamanho fixo, de forma determinística, com resistência a pré-imagem e a colisão.

**Hook** — script executado pelo Git em pontos do fluxo (`pre-commit`, `pre-push`). Local,
não versionado, e contornável com `--no-verify`: é ergonomia, não controle.

## I

**Impressão digital (fingerprint)** — hash da chave pública, usado para identificá-la de forma
curta e comparável. 40 hex no OpenPGP; `SHA256:...` no SSH.

**`includeIf`** — diretiva do `~/.gitconfig` que aplica configuração diferente por diretório
ou por *remote*.

**in-toto** — arcabouço de proveniência de cadeia de suprimentos; formato usado pelas
atestações do GitHub.

## K

**KDF (Key Derivation Function)** — função que transforma sua frase secreta na chave que cifra
a chave privada em disco.

**`keytocard`** — subcomando do `gpg --edit-key` que **move** uma subchave para um cartão
inteligente, destruindo a cópia local. Exige backup prévio.

**KRL (Key Revocation List)** — lista de revogação do OpenSSH. Pouco usada na prática.

## M

**Merkle (árvore de)** — estrutura em árvore de hashes que permite provar inclusão e
consistência em tempo logarítmico. Base dos logs de transparência.

**`merge.verifySignatures`** — configuração que recusa mesclar um ramo cuja **ponta** não
esteja assinada. Só a ponta.

**ML-DSA** — *Module-Lattice Digital Signature Algorithm* (antes Dilithium), FIPS 204.
Assinatura pós-quântica de uso geral.

## N

**Namespace (SSHSIG)** — rótulo que separa domínios de uso de uma assinatura (`git`, `file`,
…). Faz parte do que é assinado, o que impede reaproveitamento entre domínios.

## O

**Objeto (Git)** — unidade de armazenamento do Git: *blob*, *tree*, *commit* ou *tag*, cada uma
endereçada pelo hash do próprio conteúdo.

**OIDC (OpenID Connect)** — protocolo de identidade federada; base da identidade efêmera do
Sigstore.

**OpenPGP** — o padrão (RFC 9580, antes RFC 4880) que o GnuPG implementa.

**Ownertrust** — no GnuPG, o nível de confiança que **você** atribui a cada chave. Exportável
com `gpg --export-ownertrust`.

## P

**Par de chaves** — chave privada e a chave pública correspondente.

**Payload** — no contexto de assinatura de commit, o objeto commit **sem** o campo `gpgsig`.
É exatamente isso que é assinado.

**PGP (Pretty Good Privacy)** — o programa original de Phil Zimmermann (1991) que deu origem
ao padrão OpenPGP.

**`pinentry`** — programa que exibe o pedido de frase secreta para o `gpg-agent`. No macOS,
`pinentry-mac` é obrigatório na prática.

**Pós-quântico (PQC)** — criptografia resistente a computadores quânticos. Ver ML-DSA, SLH-DSA.

**Principal** — o rótulo de identidade numa linha do `allowed_signers`. Costuma ser um e-mail,
e **não é validado contra o autor do commit**.

**Proveniência (provenance)** — declaração verificável sobre a origem de um artefato: de que
código e de que pipeline ele veio. Responde a pergunta que a assinatura de commit não responde.

## R

**Rebase** — reescrita de commits sobre outra base. Cria objetos **novos**, com hashes novos;
por isso "perde" a assinatura original.

**Rekor** — o log de transparência do Sigstore.

**Revogação** — declaração de que uma chave não deve mais ser aceita. Código `%G?` = `R`.
Diferente de expiração: retroage.

**RFC 9580** — o padrão OpenPGP atual, de julho de 2024.

**Resumo (digest)** — a saída de uma função de hash.

**Ruleset** — o mecanismo atual do GitHub para impor regras a ramos e tags, inclusive
*Require signed commits*. Tem modo `evaluate`, que registra sem bloquear.

## S

**S/MIME** — assinatura baseada em certificados X.509, comum em ambiente corporativo com PKI.

**SHA-1** — função de hash usada pelo Git para nomear objetos. Quebrada (colisão prática em
2017, prefixo escolhido em 2020); mitigada no Git por detecção de colisão.

**SHA-256** — hash mais forte; formato de objeto alternativo no Git desde a versão 2.29,
pouco adotado por falta de interoperabilidade.

**SHAttered** — a primeira colisão prática de SHA-1, publicada em 2017 por Google e CWI.

**Sigstore** — projeto de assinatura sem chave de longa duração: Fulcio (certificados),
Rekor (log de transparência), Cosign (assinatura de artefatos), gitsign (commits).

**`--signoff` (`-s`)** — acrescenta a linha `Signed-off-by:` (DCO). **Não é assinatura.**

**SLH-DSA** — assinatura pós-quântica baseada apenas em hash (antes SPHINCS+), FIPS 205.

**SLSA** — *Supply-chain Levels for Software Artifacts*: níveis de garantia de proveniência de
build.

**Split-view attack (visão dividida)** — ataque em que um log de transparência apresenta
árvores diferentes a vítimas diferentes. Defesa requer *gossip* entre verificadores.

**`ssh-agent`** — o agente de chaves do OpenSSH.

**SSHSIG** — o formato de assinatura genérica do OpenSSH, introduzido na versão 8.1 (2019).
É o que o Git usa com `gpg.format ssh`.

**Subchave** — no OpenPGP, chave secundária certificada pela primária, com finalidade única
(`[S]` assinar, `[E]` cifrar, `[A]` autenticar). Permite trocar material criptográfico sem
trocar a identidade.

## T

**Tag anotada** — objeto Git próprio, com autor, data e mensagem, que **pode ser assinada**.

**Tag leve** — apenas um ponteiro para um commit. Não é objeto, não tem autor e **não pode ser
assinada**.

**Transparência (log de)** — registro público apenas-anexação, estruturado em árvore de
Merkle, que permite provar inclusão e consistência.

**Trustdb** — banco de dados de confiança do GnuPG.

## U

**UID (User ID)** — no OpenPGP, o par nome + e-mail associado a uma chave. Uma chave pode ter
vários.

## V

**`valid-after` / `valid-before`** — opções de data no `allowed_signers`. Comparadas com a
hora da **verificação**, não com a data do commit.

**Verificação (verify)** — conferir uma assinatura com a chave pública.

**`Verified`** — o selo do GitHub. Significa: assinatura válida + chave cadastrada em uma conta
como *signing key* + e-mail do commit verificado naquela conta.

**Vigilant mode** — configuração do GitHub que marca como `Unverified` **também** os commits
não assinados, transformando a ausência de assinatura em sinal.

## W

**WKD (Web Key Directory)** — mecanismo de publicação de chave OpenPGP no seu próprio domínio,
em `/.well-known/openpgpkey/`.

**Web of trust (rede de confiança)** — modelo do OpenPGP em que as pessoas assinam as chaves
umas das outras. Fracassou na prática; a rede de servidores que a sustentava colapsou em 2019.

**`web-flow`** — a conta com que o GitHub assina os commits criados no servidor (edição pela
web, merges, API).

---

## Os códigos de `%G?`, em um lugar só

| Código | Significa |
|---|---|
| `G` | boa, assinante conhecido |
| `B` | **ruim** — o conteúdo não confere |
| `U` | boa, mas o assinante não está na sua lista |
| `X` | assinatura com prazo próprio, vencida (raro) |
| `Y` | boa, feita por chave que **depois** expirou |
| `R` | chave **revogada** |
| `E` | não foi possível verificar |
| `N` | sem assinatura |

---

## Pares que se confundem

| | |
|---|---|
| **autenticar** × **assinar** | provar quem entra × carimbar o conteúdo |
| **`-s`** × **`-S`** | DCO (texto) × assinatura (criptografia) |
| **cifrar** × **assinar** | sigilo × procedência |
| **expirar** (`Y`) × **revogar** (`R`) | afeta o futuro × afeta também o passado |
| **`B`** × **`U`** | adulteração × desconhecimento |
| **integridade** × **autenticidade** | o conteúdo não mudou × o conteúdo é de quem diz ser |
| **tag anotada** × **tag leve** | objeto assinável × ponteiro |
| **chave de autenticação** × **chave de assinatura** | duas listas separadas no GitHub |
