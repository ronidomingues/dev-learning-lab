# 5 · Manual de uso — referência

> Nível: iniciante → intermediário · Atualizado em 13/08/2026 · Testado com Git 2.34.1,
> GnuPG 2.2.27, OpenSSH 8.9p1

Referência para **consulta**, organizada por tarefa. Não é para ler do começo ao fim.

**Índice**
[Configurar](#1-configurar) ·
[Assinar](#2-assinar) ·
[Ler o status](#3-ler-o-status-de-uma-assinatura) ·
[Verificar](#4-verificar) ·
[`allowed_signers`](#5-o-arquivo-allowed_signers) ·
[Gerenciar chaves GPG](#6-gerenciar-chaves-gpg) ·
[Gerenciar chaves SSH](#7-gerenciar-chaves-ssh) ·
[Agentes](#8-agentes) ·
[GitHub CLI e API](#9-github-cli-e-api) ·
[Obsoleto](#10-o-que-está-obsoleto) ·
[Atalhos de quem usa há anos](#11-atalhos-de-quem-usa-isto-há-anos)

---

## 1. Configurar

| Chave de configuração | Valores | O que faz |
|---|---|---|
| `gpg.format` | `openpgp` (padrão) · `ssh` · `x509` | escolhe o formato de assinatura |
| `user.signingkey` | ID/impressão digital (GPG) · caminho do `.pub` (SSH) · `key::ssh-...` (SSH, Git ≥ 2.35) | qual chave usar |
| `commit.gpgsign` | `true` · `false` | assina todo commit automaticamente |
| `tag.gpgSign` | `true` · `false` | assina toda tag anotada |
| `gpg.program` | caminho | qual binário `gpg` chamar (essencial no Windows com dois GnuPG) |
| `gpg.ssh.allowedSignersFile` | caminho | lista de quem pode assinar, para verificação **local** |
| `gpg.ssh.revocationFile` | caminho | lista de chaves revogadas (KRL) — Git ≥ 2.35 |
| `gpg.ssh.defaultKeyCommand` | comando | descobre a chave dinamicamente (ex.: perguntar ao agente) |
| `merge.verifySignatures` | `true` · `false` | recusa mesclar ramo cuja **ponta** não esteja assinada |
| `log.showSignature` | `true` · `false` | faz todo `git log` já mostrar a verificação |

### Escopos, e quem vence quem

```bash
git config --system  ...   # /etc/gitconfig       — a máquina inteira
git config --global  ...   # ~/.gitconfig         — o seu usuário
git config --local   ...   # .git/config          — este repositório  ← vence
git -c chave=valor   ...   # só este comando      ← vence tudo
```

Ver de onde cada valor veio — o comando que resolve "funciona num repo e não em outro":

```bash
git config --list --show-origin | grep -E 'signingkey|gpgsign|gpg\.'
```

### Configuração condicional por pasta (trabalho × pessoal)

```ini
# ~/.gitconfig
[user]
    name = Seu Nome
    email = pessoal@exemplo.com
[includeIf "gitdir:~/trabalho/"]
    path = ~/.gitconfig-trabalho
```

```ini
# ~/.gitconfig-trabalho
[user]
    email = voce@empresa.com
    signingkey = ~/.ssh/id_empresa.pub
```

> A barra final em `gitdir:~/trabalho/` é obrigatória: sem ela, o padrão casa com o
> diretório e não com o que está dentro dele.

---

## 2. Assinar

| Comando | O que faz |
|---|---|
| `git commit -S -m "msg"` | assina este commit |
| `git commit --no-gpg-sign -m "msg"` | **não** assina, mesmo com `commit.gpgsign true` |
| `git commit -S<KEYID> -m "msg"` | assina com uma chave específica (sem espaço após o `-S`) |
| `git tag -s v1.0 -m "msg"` | tag anotada e assinada |
| `git tag -a v1.0 -m "msg"` | tag anotada **sem** assinar |
| `git rebase --exec 'git commit --amend --no-edit -S' -i <base>` | re-assina cada commit de um intervalo |
| `git rebase -S <base>` | rebase assinando os commits reescritos |
| `git cherry-pick -S <sha>` | cherry-pick assinando |
| `git merge -S --no-ff <ramo>` | assina o commit de merge |
| `git format-patch --signature-file ...` | **não** é isso — `--signature` de patch é texto de rodapé, não criptografia |

> `-S` é para **assinatura criptográfica**. `-s` minúsculo é `--signoff`, que só acrescenta
> uma linha `Signed-off-by:` de texto no fim da mensagem — é o DCO, uma declaração jurídica
> de autoria, **sem nenhuma criptografia**. Confundir os dois é o erro conceitual mais comum
> do assunto. Veja [17-automacao-e-ci.md § DCO](17-automacao-e-ci.md).

---

## 3. Ler o status de uma assinatura

### Os placeholders de `--format` / `--pretty`

| Placeholder | O que devolve | Exemplo real |
|---|---|---|
| `%G?` | o **código de status** (tabela abaixo) | `G` |
| `%GS` | o nome do assinante | `ana@exemplo.dev` |
| `%GK` | a chave usada | `SHA256:dOPYp66...` (SSH) · `1236820BC521B8EB...` (GPG) |
| `%GF` | impressão digital da chave | `SHA256:dOPYp66...` |
| `%GP` | impressão digital da **chave primária** (GPG, quando se assina com subchave) | — |
| `%GT` | nível de confiança | `ultimate` · `fully` · `marginal` · `never` · `undefined` |

### A tabela de códigos de `%G?` — **todos verificados na prática**

| Código | Significa | Quando aparece |
|---|---|---|
| `G` | **G**ood — assinatura boa e assinante conhecido | o caso normal |
| `B` | **B**ad — assinatura **ruim** | o conteúdo foi alterado depois de assinado |
| `U` | good, **U**nknown validity — boa, mas não sei de quem | falta o `allowed_signers`, ou a chave não está nele |
| `X` | e**X**pired signature — a assinatura tinha prazo e venceu | raro (exige assinatura com validade própria) |
| `Y` | signature made by expired ke**Y** | a chave era válida quando assinou e expirou depois |
| `R` | **R**evoked key | a chave foi revogada pelo dono |
| `E` | **E**rror — não foi possível verificar | falta a chave pública, ou o `gpg` falhou |
| `N` | **N**o signature | o commit não está assinado |

Saídas reais dos testes, para calibrar a leitura:

```
b0f4df6 G ana@exemplo.dev            ← normal
8b7f959 B                            ← objeto commit adulterado à mão
b0f4df6 U                            ← sem allowed_signers configurado
6dda04c N commit sem assinatura      ← nunca foi assinado
b293db1 Y assinado enquanto válida   ← a chave GPG expirou depois
fff55c4 R novo commit apos renovar   ← certificado de revogação importado
```

### Receitas de leitura

```bash
# uma linha por commit, com o status
git log --format='%h %G? %s' -20

# só os commits NÃO assinados
git log --format='%h %G? %s' | grep -v '^\S* G '

# com quem assinou e a chave
git log --format='%h [%G?] %GS (%GK)' -5

# a verificação completa, do jeito que a ferramenta a produz
git log --show-signature -1

# ligar a verificação em todo `git log` (cuidado: deixa o log mais lento)
git config --global log.showSignature true
```

---

## 4. Verificar

| Comando | O que faz | Código de saída |
|---|---|---|
| `git verify-commit <sha>` | verifica um commit | `0` se boa |
| `git verify-commit --raw <sha>` | saída legível por máquina (protocolo do GnuPG) | idem |
| `git verify-tag <tag>` / `git tag -v <tag>` | verifica uma tag | `0` se boa |
| `git log --show-signature <intervalo>` | verifica vários | sempre `0` — **não serve como teste** |
| `git merge --verify-signatures <ramo>` | recusa mesclar ponta não assinada | `0` ou aborta |
| `git pull --verify-signatures` | idem, no `pull` | — |

> **Pegadinha para automação:** `git log --show-signature` **sempre** sai com código 0, mesmo
> com assinatura ruim. Para porta de qualidade, use `git verify-commit` (por commit) ou leia
> `%G?` num laço — é o que faz o
> [`auditar-historico.sh`](07-projeto-modelo/bin/auditar-historico.sh).

Saída real de `--raw` (útil para script):

```
[GNUPG:] NEWSIG
[GNUPG:] KEY_CONSIDERED 409E6F2F50C861FAE4903F36A3D581D6D1412E44 0
[GNUPG:] SIG_ID IKldXxsGk8wIwLMxUvAg91J6PEU 2026-08-13 1786635566
[GNUPG:] GOODSIG A3D581D6D1412E44 Ana Souza <ana@exemplo.dev>
[GNUPG:] VALIDSIG 409E6F2F50C861FAE4903F36A3D581D6D1412E44 ...
```

### Verificar a assinatura SSH "na mão", com `ssh-keygen`

Útil para depurar quando o Git diz `U` e você quer saber por quê:

```bash
# 1. extrair a assinatura de dentro do objeto commit
git cat-file commit <sha> \
  | sed -n '/BEGIN SSH SIGNATURE/,/END SSH SIGNATURE/p' \
  | sed 's/^gpgsig //; s/^ //' > /tmp/sig.txt

# 2. perguntar qual principal do allowed_signers corresponde àquela chave
ssh-keygen -Y find-principals -f ~/.config/git/allowed_signers -s /tmp/sig.txt
# esperado: ana@exemplo.dev
# se vier "No principal matched", a chave não está na lista (ou a data não bate)
```

E as operações genéricas de assinatura de arquivos, que não têm nada a ver com Git mas usam o
mesmo mecanismo:

```bash
ssh-keygen -Y sign   -f ~/.ssh/id_assinatura -n file arquivo.txt     # gera arquivo.txt.sig
ssh-keygen -Y verify -f ~/.config/git/allowed_signers \
                     -I ana@exemplo.dev -n file -s arquivo.txt.sig < arquivo.txt
# esperado: Good "file" signature for ana@exemplo.dev with ED25519 key SHA256:...
```

> O `-n` é o **namespace**. Se o `allowed_signers` disser `namespaces="git"`, a verificação
> com `-n file` falha — de propósito, e isso é uma feature:
> `key is not permitted for use in signature namespace "file"`.

---

## 5. O arquivo `allowed_signers`

Formato de cada linha:

```
<principal> [opções,] <tipo-da-chave> <chave-base64> [comentário]
```

| Opção | O que faz |
|---|---|
| `namespaces="git"` | restringe a chave a assinar objetos do Git |
| `valid-after="AAAAMMDD"` | a chave só vale a partir desta data |
| `valid-before="AAAAMMDD"` | a chave deixa de valer nesta data |
| `cert-authority` | esta chave é uma **autoridade** que emite certificados para outras |

```bash
# uma linha, do jeito certo
printf '%s namespaces="git" %s\n' "$(git config --get user.email)" \
       "$(cat ~/.ssh/id_assinatura.pub)" >> ~/.config/git/allowed_signers
```

Comportamento real, medido:

| Situação | Resultado |
|---|---|
| chave presente, sem restrição de data | `G` |
| chave ausente do arquivo | `U` + `No principal matched.` |
| `valid-before` no passado | `U` + `key has expired: verify time ... > valid-before ...` |
| `valid-after` no futuro | `U` + `key is not yet valid: verify time ... < valid-after ...` |
| arquivo não configurado | `U` + `Unable to open allowed keys file` |
| **principal com nome de outra pessoa** | **`G`**, e `%GS` mostra o nome errado — o Git **não** compara com o autor |

Essa última linha merece releitura. Está demonstrada no ato 9 do
[projeto-modelo](07-projeto-modelo/) e explicada em
[60-teoria-avancada.md](60-teoria-avancada.md).

---

## 6. Gerenciar chaves GPG

| Tarefa | Comando |
|---|---|
| listar chaves privadas | `gpg --list-secret-keys --keyid-format=long` |
| listar chaves públicas | `gpg --list-keys --keyid-format=long` |
| pegar a impressão digital | `gpg --fingerprint <email>` |
| criar chave (assistente) | `gpg --full-generate-key` |
| criar chave (direto) | `gpg --quick-generate-key "Nome <email>" ed25519 sign 2y` |
| exportar pública (para o GitHub) | `gpg --armor --export <FPR>` |
| exportar privada (backup) | `gpg --armor --export-secret-keys <FPR>` |
| importar | `gpg --import arquivo.asc` |
| **renovar** a validade | `gpg --quick-set-expire <FPR> 2y` |
| renovar também as subchaves | `gpg --quick-set-expire <FPR> 2y '*'` |
| adicionar um e-mail à chave | `gpg --quick-add-uid <FPR> "Nome <outro@email>"` |
| criar subchave só de assinatura | `gpg --quick-add-key <FPR> ed25519 sign 2y` |
| revogar | `gpg --import revogacao.asc` e publicar |
| apagar chave privada | `gpg --delete-secret-keys <FPR>` |
| edição interativa (tudo o mais) | `gpg --edit-key <FPR>` |

Dentro do `--edit-key`, os subcomandos que se usa de verdade: `expire`, `addkey`, `adduid`,
`trust`, `passwd`, `revkey`, `save`.

> **O certificado de revogação.** O GnuPG cria um automaticamente em
> `~/.gnupg/openpgp-revocs.d/<FPR>.rev` quando a chave nasce. O arquivo vem com todas as
> linhas prefixadas por `:` para você não importá-lo por acidente — para usá-lo de verdade:
> ```bash
> sed 's/^://' ~/.gnupg/openpgp-revocs.d/<FPR>.rev > revogacao.asc
> gpg --import revogacao.asc
> ```
> Depois disso, `%G?` passa a devolver `R` para tudo que aquela chave assinou. **Testado.**

---

## 7. Gerenciar chaves SSH

| Tarefa | Comando |
|---|---|
| gerar Ed25519 | `ssh-keygen -t ed25519 -C "email" -f ~/.ssh/id_assinatura` |
| gerar em token FIDO2 (YubiKey) | `ssh-keygen -t ed25519-sk -C "email" -f ~/.ssh/id_yubikey` |
| gerar RSA (só se algo velho exigir) | `ssh-keygen -t rsa -b 4096 -C "email"` |
| ver a impressão digital | `ssh-keygen -lf ~/.ssh/id_assinatura.pub` |
| trocar a frase secreta | `ssh-keygen -p -f ~/.ssh/id_assinatura` |
| recuperar a pública a partir da privada | `ssh-keygen -y -f ~/.ssh/id_assinatura` |
| assinar arquivo | `ssh-keygen -Y sign -f <chave> -n <namespace> <arquivo>` |
| verificar arquivo | `ssh-keygen -Y verify -f <allowed_signers> -I <principal> -n <namespace> -s <sig>` |
| descobrir o principal de uma assinatura | `ssh-keygen -Y find-principals -f <allowed_signers> -s <sig>` |
| gerar lista de revogação | `ssh-keygen -k -f revogadas.krl chave-ruim.pub` |

---

## 8. Agentes

| Tarefa | GPG | SSH |
|---|---|---|
| ver o que está carregado | `gpg-connect-agent 'keyinfo --list' /bye` | `ssh-add -l` |
| adicionar chave | (automático no primeiro uso) | `ssh-add ~/.ssh/id_assinatura` |
| esquecer tudo | `gpgconf --reload gpg-agent` | `ssh-add -D` |
| matar o agente | `gpgconf --kill gpg-agent` | `pkill ssh-agent` |
| ver a configuração em vigor | `gpgconf --list-options gpg-agent` | `echo $SSH_AUTH_SOCK` |

Tempo de cache do `gpg-agent` (padrão: 600 s de inatividade, máximo 7200 s):

```ini
# ~/.gnupg/gpg-agent.conf
default-cache-ttl 3600
max-cache-ttl 28800
```

```bash
gpgconf --reload gpg-agent    # aplica sem reiniciar a máquina
```

---

## 9. GitHub CLI e API

```bash
# listar suas chaves cadastradas
gh ssh-key list
gh gpg-key list

# cadastrar
gh ssh-key add ~/.ssh/id_assinatura.pub --type signing --title "notebook"
gpg --armor --export <FPR> | gh gpg-key add -

# o VEREDITO DO GITHUB sobre um commit (o que vale de verdade)
gh api repos/<dono>/<repo>/commits/<sha> --jq '.commit.verification'
```

```json
{
  "verified": true,
  "reason": "valid",
  "signature": "-----BEGIN SSH SIGNATURE-----\n...",
  "payload": "tree ...\nauthor ...",
  "verified_at": "2026-08-13T15:28:07Z"
}
```

Os valores de `reason` que você vai encontrar na prática:

| `reason` | Significa |
|---|---|
| `valid` | tudo certo |
| `unsigned` | não tem assinatura |
| `unknown_key` | a chave não está cadastrada em nenhuma conta |
| `unverified_email` | o e-mail do commit não está verificado na conta dona da chave |
| `unknown_signature_type` | formato não suportado (é o caso do gitsign/Sigstore) |
| `expired_key` | a chave estava vencida quando assinou |
| `not_signing_key` | a chave está cadastrada, mas como *authentication*, não como *signing* |
| `bad_email` | o e-mail da assinatura não bate com o do commit |
| `gpgverify_error` | falha interna do lado do GitHub |

`not_signing_key` e `unverified_email` juntos respondem por quase todo `Unverified` que
aparece na vida real.

Auditar um PR inteiro:

```bash
gh api repos/<dono>/<repo>/pulls/<n>/commits --paginate \
   --jq '.[] | [.sha[0:9], .commit.verification.verified, .commit.verification.reason] | @tsv'
```

---

## 10. O que está obsoleto

| Obsoleto | Desde | Use no lugar |
|---|---|---|
| `gpg1` / GnuPG 1.4 | ~2015 | GnuPG 2.5.x |
| GnuPG **2.4.x** | **fim de suporte em 30/06/2026** | 2.5.x |
| chaves **DSA** e **RSA de 1024 bits** | há muito | Ed25519, ou RSA ≥ 3072 |
| SHA-1 em assinaturas OpenPGP | quebrado em 2017 (SHAttered) | SHA-256+ (o padrão hoje) |
| rede de confiança e assinatura mútua de chaves (*keysigning parties*) | na prática, ~2019 | o GitHub como autoridade de fato; ou CA SSH interna |
| servidor de chaves SKS | desligado em 2021 (ataque de envenenamento) | `keys.openpgp.org`, ou WKD, ou simplesmente não publicar |
| `git config --global gpg.program gpg2` | GnuPG 2 virou `gpg` | desnecessário na maioria das distros |
| `--verify-signatures` como única defesa | sempre foi | ruleset no servidor |

---

## 11. Atalhos de quem usa isto há anos

**Descobrir por que um commit específico está `Unverified`, em um comando:**

```bash
gh api repos/{owner}/{repo}/commits/$(git rev-parse HEAD) --jq '.commit.verification.reason'
```
Isso pergunta ao **GitHub**, não à sua máquina. É a única fonte que importa para o selo.

**Ver quem assinou o quê, agregado:**

```bash
git log --format='%GS' | sort | uniq -c | sort -rn
```

**Re-assinar tudo desde uma base** (destrói hashes — só em ramo seu, nunca no `main`):

```bash
git rebase --exec 'git commit --amend --no-edit -S' -i <base>
```

**Assinar sem alterar mais nada, no último commit:**

```bash
git commit --amend --no-edit -S
```

**Descobrir se o repositório está limpo antes de ligar um ruleset:**

```bash
git log --format='%G?' origin/main | sort | uniq -c
#   412 G
#    38 N     ← estes 38 vão ser um problema social, não técnico
```

**Um `alias` que vale a pena:**

```bash
git config --global alias.lg "log --format='%C(auto)%h %G? %d %s %C(dim)(%an)'"
git lg -15
```

**Verificar um repositório de terceiros que você acabou de clonar:**

```bash
git log --format='%h %G? %GS %s' -20
```
Se vier tudo `U`, é esperado: você não tem o `allowed_signers` dos mantenedores. Se vier
algum `B`, pare e investigue.

---

## Autoteste

1. Qual a diferença entre `git commit -s` e `git commit -S`?
2. Por que `git log --show-signature` não serve como teste de CI?
3. `%G?` devolveu `U`. Cite duas causas possíveis, no método SSH.
4. Qual comando responde, de forma autoritativa, por que o GitHub não verificou um commit?
5. Como renovar uma chave GPG vencida sem gerar uma nova?
6. Para que serve `namespaces="git"` no `allowed_signers`?
7. Você quer usar um e-mail no trabalho e outro nos projetos pessoais, automaticamente. Como?
8. Qual `reason` da API do GitHub indica que a chave foi cadastrada na lista errada?

*(Respostas: 1 — `-s` é `--signoff`, texto do DCO, sem criptografia; `-S` é assinatura
criptográfica. 2 — ele sempre sai com código 0, mesmo com assinatura ruim. 3 — a chave não
está no `allowed_signers`, ou `valid-before`/`valid-after` não cobre a data do commit (ou o
arquivo não está configurado). 4 — `gh api repos/.../commits/<sha> --jq
'.commit.verification.reason'`. 5 — `gpg --quick-set-expire <FPR> 2y`. 6 — restringe a chave a
assinar objetos do Git, impedindo o reaproveitamento de uma assinatura feita para outro fim.
7 — `includeIf "gitdir:~/trabalho/"` no `~/.gitconfig`. 8 — `not_signing_key`.)*
