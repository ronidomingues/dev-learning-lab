# 6 · Exemplos

> Nível: iniciante → avançado · Atualizado em 13/08/2026
> Todo código aqui é **completo e executável**. Os exemplos marcados com ✅ foram
> **executados** nesta redação (Git 2.34.1, GnuPG 2.2.27, OpenSSH 8.9p1, Ubuntu 22.04.5);
> os marcados com ⚠️ dependem de hardware ou conta que não havia no ambiente de escrita e
> seguem a documentação oficial.

| # | Exemplo | Nível |
|---|---|---|
| [1](#1-) | Assinar só neste repositório ✅ | trivial |
| [2](#2-) | Dois e-mails e duas chaves, por pasta ✅ | fácil |
| [3](#3-) | Auditar o histórico de um repositório clonado ✅ | fácil |
| [4](#4-) | Descobrir por que um commit está `Unverified` | fácil |
| [5](#5-) | Assinar e verificar uma tag de release ✅ | fácil |
| [6](#6-) | Re-assinar os commits do seu ramo antes do PR ✅ | médio |
| [7](#7-) | Montar o `allowed_signers` de uma equipe pela API do GitHub ✅ | médio |
| [8](#8-) | Aposentar uma chave sem invalidar o passado ✅ | médio |
| [9](#9-) | Renovar uma chave GPG vencida ✅ | médio |
| [10](#10-) | Porta de qualidade na CI ✅ | médio |
| [11](#11-) | Chave de assinatura numa YubiKey ⚠️ | avançado |
| [12](#12-) | 1Password como agente de assinatura ⚠️ | avançado |
| [13](#13--caso-real-migrar-uma-equipe-de-gpg-para-ssh) | **Caso real:** migrar uma equipe de GPG para SSH | avançado |
| [14](#14--caso-real-token-vazado-o-que-a-assinatura-permitiu-concluir) | **Caso real:** token vazado — o que a assinatura permitiu concluir | avançado |

---

## 1 · ✅ Assinar só neste repositório

**Problema.** Você quer assinar em um projeto específico — o do trabalho, digamos — sem
ligar assinatura em tudo que existe na máquina.

**Solução.**

```bash
cd ~/trabalho/projeto-x

git config --local gpg.format ssh
git config --local user.signingkey ~/.ssh/id_empresa.pub
git config --local user.email "voce@empresa.com"
git config --local commit.gpgsign true

git commit --allow-empty -m "teste"
git log --format='%h %G? %GS' -1
```

```
# saída real:
b0f4df6 G ana@exemplo.dev
```

**Explicação.** `--local` grava em `.git/config`, que vence a configuração global. É o
mecanismo por trás de quase todo "funciona num repositório e não em outro" — inclusive quando
você não queria que funcionasse assim. Para ver quem está vencendo:

```bash
git config --list --show-origin | grep -E 'signingkey|gpgsign|user.email'
```

---

## 2 · ✅ Dois e-mails e duas chaves, por pasta

**Problema.** Projetos pessoais em `~/pessoal`, do trabalho em `~/trabalho`. Cada um exige
e-mail e chave diferentes, e você **vai** esquecer de trocar.

**Solução.** Configuração condicional, que o Git aplica sozinho conforme a pasta.

```bash
# ~/.gitconfig — o padrão, pessoal
cat >> ~/.gitconfig <<'EOF'

[user]
    name = Ana Souza
    email = ana@pessoal.dev
    signingkey = /home/ana/.ssh/id_pessoal.pub
[gpg]
    format = ssh
[commit]
    gpgsign = true
[tag]
    gpgSign = true

[includeIf "gitdir:~/trabalho/"]
    path = ~/.gitconfig-trabalho
EOF

# ~/.gitconfig-trabalho — só vale dentro de ~/trabalho
cat > ~/.gitconfig-trabalho <<'EOF'
[user]
    email = ana.souza@empresa.com
    signingkey = /home/ana/.ssh/id_empresa.pub
EOF
```

**Verifique — de dentro de cada pasta:**

```bash
cd ~/pessoal/algo   && git config --get user.email
# ana@pessoal.dev
cd ~/trabalho/algo  && git config --get user.email
# ana.souza@empresa.com
```

**Explicação e pegadinhas.**
- A **barra final** em `gitdir:~/trabalho/` é obrigatória. Sem ela, o padrão casa com o
  diretório, não com o conteúdo dele.
- `includeIf` só funciona em repositórios **dentro** do caminho. Um repositório em
  `~/outro/lugar` com *remote* da empresa não é pego — para isso existe
  `includeIf "hasconfig:remote.*.url:git@github.com:empresa/**"` (Git ≥ 2.36).
- Registre **as duas** chaves no GitHub como *Signing key*, e ponha **as duas** no seu
  `allowed_signers`.

---

## 3 · ✅ Auditar o histórico de um repositório clonado

**Problema.** Você clonou um projeto e quer saber o estado real das assinaturas antes de
confiar nele — ou antes de propor um ruleset para a equipe.

**Solução.**

```bash
# panorama
git log --format='%G?' | sort | uniq -c | sort -rn

# quem assina, e quanto
git log --format='%GS' | sort | uniq -c | sort -rn | head

# os não assinados, com autor
git log --format='%h %G? %an — %s' | awk '$2 != "G"' | head -20
```

**Saída real, rodada neste repositório de estudos:**

```
  ok    bb2d29c1c  [G]  Merge remote-tracking branch 'origin/xcard'
  FALHA f4e24fda1  [N]  update files  (autor: Ronivaldo D. Andrade)
  ok    9af0cfee9  [G]  Add bibliografia, referências e glossário sobre testes automatizados
  ok    57fa48eaa  [G]  Add comprehensive guides on testing types and unit testing principles

  1 de 4 commit(s) sem assinatura válida.
```

**Explicação.** Esse padrão — quase tudo assinado, um ou outro `N` no meio — é o mais comum
do mundo real, e tem três causas típicas: um commit feito de outra máquina ainda não
configurada, um `--no-verify` apressado, ou um commit criado por ferramenta (IDE, script,
bot) que não passa pela configuração normal. Achar **qual** é o motivo importa mais do que o
número.

Se vier tudo `U`, é esperado num repositório de terceiros: você não tem o `allowed_signers`
dos mantenedores. Se vier algum `B`, **pare e investigue** — `B` não acontece por acidente.

---

## 4 · Descobrir por que um commit está `Unverified`

**Problema.** Localmente está tudo `G`; o GitHub mostra `Unverified`. As duas coisas não se
contradizem: são verificações diferentes, com informações diferentes.

**Solução — pergunte ao GitHub, que é quem decide:**

```bash
gh api repos/{owner}/{repo}/commits/$(git rev-parse HEAD) \
   --jq '.commit.verification | {verified, reason}'
```

```json
{ "verified": false, "reason": "not_signing_key" }
```

**Roteiro de diagnóstico, por `reason`:**

| `reason` | O que fazer |
|---|---|
| `not_signing_key` | a chave está cadastrada como *Authentication*. Recadastre como **Signing Key** em <https://github.com/settings/ssh/new> |
| `unverified_email` | verifique o e-mail em <https://github.com/settings/emails> |
| `unknown_key` | a chave não está em conta nenhuma. Cadastre-a |
| `unsigned` | o commit realmente não foi assinado. Confira `git config --get commit.gpgsign` **no repositório** |
| `expired_key` | a chave estava vencida ao assinar. Renove e re-assine |
| `bad_email` | o e-mail da chave GPG não bate com o do commit. Acrescente o UID: `gpg --quick-add-uid` |
| `unknown_signature_type` | você usou gitsign/Sigstore, que o GitHub ainda não reconhece ([65](65-estado-da-arte.md)) |

**Explicação.** É comum inverter a ordem e passar uma hora depurando a máquina local quando a
resposta estava a um comando de distância. A verificação local responde
*"esta chave está na minha lista?"*; a do GitHub responde *"esta chave pertence a uma conta,
e o e-mail do commit é dela?"*.

---

## 5 · ✅ Assinar e verificar uma tag de release

**Problema.** A tag é o que as pessoas baixam. Assinar commit e esquecer a tag é o padrão da
casa — e é justamente a tag que um atacante moveria.

**Solução.**

```bash
git tag -s v1.0.0 -m "release 1.0.0"
git tag -v v1.0.0
```

```
# saída real:
Good "git" signature for ana@exemplo.dev with ED25519 key SHA256:dOPYp66kQRpqWjjSA3F995N6QFG77icC5HYiw9E2Be8
object 6dda04cf337b91b9660a32e3fb736026a0cf08d2
type commit
tag v1.0.0
```

Para nunca mais esquecer:

```bash
git config --global tag.gpgSign true
```

**Verificar a tag de outra pessoa** (o caso real: você vai empacotar a versão 3.2.1 de uma
dependência):

```bash
git clone https://github.com/projeto/dependencia && cd dependencia
git tag -v v3.2.1
```

Sem a chave pública do mantenedor no seu chaveiro, isso falha com
`gpg: Can't check signature: No public key` — e é aí que se descobre que "usar só versões
assinadas" exige, antes, decidir **de quem** você aceita assinatura.

---

## 6 · ✅ Re-assinar os commits do seu ramo antes do PR

**Problema.** Você fez 8 commits e só depois percebeu que a assinatura estava desligada.

**Solução.**

```bash
git config --local commit.gpgsign true
git rebase --exec 'git commit --amend --no-edit -S' -i origin/main
```

> Reescreve cada commit desde `origin/main`, re-assinando. `--no-edit` mantém as mensagens.

**Verifique:**

```bash
git log --format='%h %G? %s' origin/main..HEAD
```

**Explicação e o aviso obrigatório.** Isso **reescreve o histórico**: todos os commits ganham
hash novo. Use apenas no **seu** ramo, antes do PR, e nunca em `main` compartilhada.

Detalhe verificado no teste: com `commit.gpgsign true` configurado, um `git rebase` comum já
re-assina os commits reescritos, sem precisar do `--exec`. Mas o hash muda de qualquer jeito
— rebase sempre cria commits novos:

```
antes:  aee16c5 [G] commit assinado que sera rebaseado
depois: 6615316 [G] commit assinado que sera rebaseado
```

Se os commits já estiverem no remoto, você vai precisar de `git push --force-with-lease` —
e `--force-with-lease`, não `--force`, porque ele recusa sobrescrever trabalho que apareceu
lá enquanto você não olhava.

---

## 7 · ✅ Montar o `allowed_signers` de uma equipe pela API do GitHub

**Problema.** Você quer que todo mundo consiga verificar localmente o histórico, sem pedir a
chave pública de cada pessoa por mensagem.

**Solução.** O GitHub publica as chaves de assinatura de qualquer usuário, sem autenticação:

```bash
#!/usr/bin/env bash
# montar-allowed-signers.sh — gera o arquivo a partir dos usuários do GitHub
set -uo pipefail

DEST="$1"; shift
: > "$DEST"

for usuario in "$@"; do
  chaves=$(curl -sS -m 15 "https://api.github.com/users/$usuario/ssh_signing_keys" \
           | grep -o '"key": *"[^"]*"' | sed 's/"key": *"//; s/"$//') || true
  if [ -z "$chaves" ]; then
    echo "aviso: $usuario não publicou chave de assinatura SSH" >&2
    continue
  fi
  while IFS= read -r k; do
    printf '%s@users.noreply.github.com namespaces="git" %s\n' "$usuario" "$k" >> "$DEST"
  done <<< "$chaves"
done

echo "$(wc -l < "$DEST") linha(s) em $DEST"
```

```bash
bash montar-allowed-signers.sh ~/.config/git/allowed_signers sethvargo mislav torvalds
```

```
# saída real (13/08/2026):
aviso: torvalds não publicou chave de assinatura SSH
4 linha(s) em /home/ana/.config/git/allowed_signers
```

**Explicação e as três armadilhas.**

1. **`|| true` depois do `curl`**. Sem ele, com `set -e`, o script morre calado no primeiro
   usuário sem chave. Foi exatamente o que aconteceu na primeira versão deste exemplo
   enquanto eu o escrevia: ele processou dois usuários e saiu sem dizer nada.
2. **O principal que o script usa é `<usuario>@users.noreply.github.com`**, que só bate se a
   pessoa commitar com o e-mail privado do GitHub. Se a equipe usa e-mail corporativo, troque
   a linha do `printf` por um mapeamento explícito usuário → e-mail.
3. **Isto é confiança-no-primeiro-uso.** Você está confiando no GitHub para dizer de quem é
   cada chave. Se essa premissa não serve para o seu modelo de ameaça, o `allowed_signers`
   tem de ser montado por outro canal — e aí a pergunta interessante é por que você confia no
   GitHub para hospedar o código, mas não para dizer de quem é a chave.
   ([60-teoria-avancada.md](60-teoria-avancada.md) trata disso.)

Endpoints relacionados, todos públicos:

```bash
curl -s https://github.com/<usuario>.keys     # chaves de AUTENTICAÇÃO
curl -s https://github.com/<usuario>.gpg      # chaves GPG
curl -s https://api.github.com/users/<usuario>/ssh_signing_keys   # chaves de ASSINATURA
```

---

## 8 · ✅ Aposentar uma chave sem invalidar o passado

**Problema.** Você trocou de notebook e gerou uma chave nova. Se apagar a linha antiga do
`allowed_signers`, três anos de commits viram `U`.

**Solução.** Delimite as duas por data, em vez de apagar:

```
carla@exemplo.dev namespaces="git",valid-before="20260301" ssh-ed25519 AAAA...ANTIGA carla@antigo
carla@exemplo.dev namespaces="git",valid-after="20260301"  ssh-ed25519 AAAA...NOVA   carla@novo
```

**Verifique o comportamento — saída real:**

```
# com valid-before no passado, para um commit de hoje:
Good "git" signature with ED25519 key SHA256:dOPYp66...
allowed_signers:1: key has expired: verify time 2026-08-13T12:28:08 > valid-before 2025-01-01T00:00:00
No principal matched.
→ status [U]
```

```
# com valid-after no futuro:
allowed_signers:1: key is not yet valid: verify time 2026-08-13T12:28:08 < valid-after 2099-01-01T00:00:00
→ status [U]
```

**Explicação.** O OpenSSH compara a data do intervalo com a **data de verificação**, não com
a data do commit — o que é uma sutileza importante e um limite honesto do mecanismo. Na
prática funciona bem para o caso "chave saiu de uso em tal data", que é o que se quer 95 % das
vezes. Exige OpenSSH ≥ 8.5.

Note que `[U]` não é `[B]`: a assinatura continua matematicamente boa. O que mudou foi você
ter deixado de reconhecer aquela chave como daquela pessoa naquela data.

---

## 9 · ✅ Renovar uma chave GPG vencida

**Problema.** Um dia os commits param, com uma mensagem que não explica nada:

```
error: gpg failed to sign the data
fatal: failed to write commit object
```

E o commit **não é criado**. Isso é o vencimento da chave, e acontece com todo mundo que
seguiu o bom conselho de pôr validade.

**Solução.**

```bash
gpg --list-secret-keys --keyid-format=long
# procure "[expirado: AAAA-MM-DD]" ou "[expired: ...]"

FPR=$(gpg --list-secret-keys --with-colons | awk -F: '/^fpr:/ {print $10; exit}')
gpg --quick-set-expire "$FPR" 2y          # a chave primária
gpg --quick-set-expire "$FPR" 2y '*'      # e todas as subchaves
```

**Verifique:**

```bash
gpg --list-keys --keyid-format=long | grep -E 'expira|expires'
git commit --allow-empty -S -m "voltou a funcionar"
git log --format='%h %G? %s' -1
# saída real: fff55c4 G voltou a funcionar
```

**E o passado?** Continua válido. Testado: um commit assinado enquanto a chave era válida,
verificado depois do vencimento, devolve **`Y`** ("assinatura boa, feita por chave que
expirou") — não `B`. E no GitHub ele **continua `Verified`**, porque o GitHub grava o
resultado da verificação no momento em que ela foi feita.

```
# saída real, verificando hoje um commit assinado antes do vencimento:
b293db1 [Y] assinado enquanto a chave era valida
gpg: Assinatura correta de "Curta <curta@exemplo.dev>" [expirado]
gpg: Nota: Esta chave expirou!
```

**Depois de renovar, reenvie a chave pública para o GitHub** — a validade nova faz parte da
chave, e o GitHub precisa da versão atualizada:

```bash
gpg --armor --export "$FPR" | gh gpg-key add -
```

---

## 10 · ✅ Porta de qualidade na CI

**Problema.** Você quer que o PR reprove se alguém enviar commit sem assinatura, e o
`git log --show-signature` não serve (ele sai com código 0 sempre).

**Solução.** O script está em
[`07-projeto-modelo/bin/auditar-historico.sh`](07-projeto-modelo/bin/auditar-historico.sh).
O núcleo dele:

```bash
falhas=0
while IFS='|' read -r hash st assunto; do
  case "$st" in
    G) ;;                                       # ok
    U) [ "${ACEITAR_U:-0}" = "1" ] || falhas=$((falhas+1)) ;;
    *) falhas=$((falhas+1)); echo "FALHA $hash [$st] $assunto" ;;
  esac
done < <(git log --format='%H|%G?|%s' "$1")
[ "$falhas" -eq 0 ]
```

No GitHub Actions, o detalhe que derruba a maioria das tentativas:

```yaml
- uses: actions/checkout@v5
  with:
    fetch-depth: 0     # sem isto, o clone é RASO e não há histórico para auditar
```

**Explicação.** Com `fetch-depth: 1` (o padrão), `git log origin/main..HEAD` não tem o que
percorrer: o teste passa sempre e ninguém percebe que ele nunca testou nada. É a categoria
mais perigosa de teste — o que dá verde por não fazer nada.

Alternativa que evita o script inteiro, e é mais confiável, porque pergunta ao GitHub:

```bash
gh api "repos/${GITHUB_REPOSITORY}/pulls/${PR}/commits" --paginate \
   --jq '.[] | select(.commit.verification.verified == false) | .sha' \
| tee nao_verificados.txt
[ ! -s nao_verificados.txt ]
```

---

## 11 · ⚠️ Chave de assinatura numa YubiKey

**Problema.** Chave privada em disco é chave que pode ser copiada por qualquer processo que
rode como você — inclusive um pacote npm malicioso.

**Solução (SSH, mais simples).**

```bash
ssh-keygen -t ed25519-sk -O resident -O verify-required \
           -C "ana@exemplo.dev" -f ~/.ssh/id_yubikey
```

> `-sk` = *security key*: a chave privada nasce **dentro** do token e não sai de lá.
> `-O resident` guarda-a no token (dá para recuperá-la em outra máquina com
> `ssh-keygen -K`). `-O verify-required` exige o PIN, além do toque.

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_yubikey.pub
git config --global commit.gpgsign true
```

A partir daí, **cada commit pisca o token e espera um toque**. Exige OpenSSH ≥ 8.2 dos dois
lados.

**Solução (GPG, mais poderosa).** Mover a subchave de assinatura para o cartão OpenPGP:

```bash
gpg --edit-key <FPR>
> key 1          # seleciona a subchave de assinatura
> keytocard      # move para o cartão — a cópia local é DESTRUÍDA
> save
```

**Explicação e o aviso que salva chave.** `keytocard` **move**, não copia: a chave privada
sai do disco. Faça o backup **antes** (`gpg --armor --export-secret-keys`), guardado offline.
Sem backup, perder o token é perder a chave.

Trade-off honesto, na minha opinião profissional: o token vale muito a pena para quem publica
software que outros instalam, e é exagero para o desenvolvedor médio de aplicação interna.
O ganho concreto é contra roubo de chave por malware — e esse é justamente o vetor que mais
cresceu na cadeia de suprimentos.

---

## 12 · ⚠️ 1Password como agente de assinatura

**Problema.** Você quer a chave protegida por biometria, sincronizada entre máquinas, sem
token físico.

**Solução.**

```bash
# 1. no app: Developer → "Use the SSH agent"; crie uma chave SSH no cofre
# 2. no Git:
git config --global gpg.format ssh
git config --global user.signingkey "key::ssh-ed25519 AAAAC3Nza...ana@exemplo.dev"
git config --global commit.gpgsign true
git config --global gpg.ssh.program "/opt/1Password/op-ssh-sign"
```

**Explicação e a pegadinha de versão.** Aqui a chave vai **literal** dentro do config, com o
prefixo `key::`, porque não existe arquivo `.pub` em disco. Verificado no teste: **essa
sintaxe exige Git ≥ 2.35**. No Git 2.34.1 ela falha assim:

```
error: Couldn't load public key key::ssh-ed25519 AAAAC3Nza...: No such file or directory?
fatal: failed to write commit object
```

Se você está preso ao Git 2.34, escreva a chave pública num arquivo e aponte para ele — o
1Password continua guardando a **privada**.

Ferramentas equivalentes: `gitsign` (sem chave, veja [17](17-automacao-e-ci.md)), Secretive
(macOS, chave no Secure Enclave), Keeper, e o `ssh-agent` do sistema com `AddKeysToAgent`.

---

## 13 · Caso real: migrar uma equipe de GPG para SSH

**Contexto.** Equipe de 25 pessoas, GPG desde 2019, exigido por um ruleset. Sintomas
acumulados: quatro pessoas com a chave vencida (e commits falhando), duas que perderam a
chave e commitavam com `--no-verify`, e um novato que levou dois dias para entrar em produção
por causa do `pinentry` no macOS.

**A decisão.** Migrar para SSH, mantendo o GPG aceito por 6 meses.

**O plano que funcionou:**

```bash
# Fase 1 (semana 1) — permitir os dois, não exigir nada ainda.
#   O ruleset já aceita qualquer assinatura válida: nada a mudar do lado do servidor.
#   Documentação interna publicada, com o passo a passo do 04-como-comecar.md.

# Fase 2 (semanas 2-3) — mutirão. Cada pessoa, na sua máquina:
ssh-keygen -t ed25519 -C "$(git config --get user.email)" -f ~/.ssh/id_assinatura
gh ssh-key add ~/.ssh/id_assinatura.pub --type signing --title "$(hostname)"
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_assinatura.pub

# Fase 3 (semana 4) — medir, antes de exigir.
gh api "repos/$ORG/$REPO/commits?since=2026-03-01" --paginate \
  --jq '.[] | [.commit.verification.verified, .commit.author.name] | @tsv' \
| sort | uniq -c | sort -rn
# → mostrou 3 pessoas ainda em 0%. Conversar com 3 pessoas é barato;
#   descobrir isso depois de ligar a trava e travar a equipe inteira, não.

# Fase 4 (semana 6) — o allowed_signers da equipe, versionado no repositório:
git config --local gpg.ssh.allowedSignersFile .github/allowed_signers
```

**O que deu errado, e é o que vale registrar:**

1. **O bot de release parou.** Ele usava uma chave GPG num *secret*, e ninguém lembrava.
   Resolvido em [17-automacao-e-ci.md](17-automacao-e-ci.md).
2. **Duas pessoas cadastraram a chave como *Authentication*.** O `push` funcionava, o selo
   não aparecia, e a suspeita inicial foi de bug do GitHub. Custou meio dia.
3. **O `allowed_signers` versionado gerou um debate legítimo**: quem tem escrita no
   repositório pode se acrescentar a ele. A conclusão a que chegaram — e que eu subscrevo —
   é que o arquivo serve para **conveniência de verificação local**, e a trava de verdade
   continua sendo o ruleset do GitHub, que consulta as chaves das contas, não o arquivo.

**Resultado.** Tempo de configuração para novato caiu de ~2 h para ~10 min. Nenhuma chave
vencida desde então, pela razão simples de que chave SSH não vence — o que, dependendo do seu
modelo de ameaça, é uma vitória ou uma dívida ([19-como-escolher.md](19-como-escolher.md)).

---

## 14 · Caso real: token vazado — o que a assinatura permitiu concluir

**Contexto.** Um token de acesso pessoal com escopo de escrita vazou num log público de CI e
ficou exposto por cerca de 40 horas. O repositório tinha ruleset exigindo commits assinados.

**A pergunta do incidente**, que é sempre a mesma: *entrou alguma coisa?*

**O que se fez, na ordem:**

```bash
# 1. revogar o token — primeiro, antes de investigar qualquer coisa
#    https://github.com/settings/tokens

# 2. listar tudo que entrou na janela de exposição
gh api "repos/$ORG/$REPO/commits?since=2026-04-02T08:00:00Z&until=2026-04-03T23:59:59Z" \
   --paginate --jq '.[] | [.sha[0:9], .commit.author.name,
                           .commit.verification.verified,
                           .commit.verification.reason] | @tsv'

# 3. e os eventos do repositório, que pegam force-push e criação/remoção de ramo
gh api "repos/$ORG/$REPO/events" --paginate --jq '.[] | [.type, .created_at, .actor.login] | @tsv'
```

**O que a assinatura permitiu concluir — e o que não permitiu.**

**Permitiu:** todos os 14 commits da janela vieram `verified: true`, com chaves de contas
conhecidas da equipe. Como o atacante teria o token mas **não** a chave privada de ninguém,
qualquer commit que ele empurrasse sairia sem assinatura válida — e o ruleset o teria
**recusado no push**. Isso reduziu o incidente de "auditar tudo" para "confirmar que o
ruleset estava mesmo ligado na janela".

**Não permitiu** (e este é o ponto que costuma ser esquecido em pós-morte):

- o token dava acesso de **leitura** a repositórios privados; assinatura não protege contra
  cópia, só contra escrita forjada;
- o token podia **abrir e aprovar PR**, alterar rulesets se tivesse escopo de administração,
  e publicar releases — e nada disso passa pela assinatura de commit;
- e a conclusão inteira depende de o ruleset estar ligado **naquele momento**, o que teve de
  ser confirmado pelo log de auditoria da organização, não pela assinatura.

**A lição operacional.** Assinatura de commit transformou uma investigação de dias numa de
horas, para **um** dos vetores. Quem apresentar isso como "o incidente foi contido porque
assinamos os commits" está exagerando — e é assim que se constrói confiança indevida no
controle. A formulação honesta é: *o vetor de escrita forjada de código estava fechado; os
demais precisaram ser investigados um a um*.

---

## Autoteste

1. Por que `--local` vence `--global`, e como descobrir quem está vencendo?
2. Na configuração por pasta, o que acontece se você esquecer a barra final em `gitdir:`?
3. Por que o script do exemplo 7 precisa de `|| true` depois do `curl`?
4. Qual a diferença entre `[U]` e `[B]` para quem está auditando um repositório?
5. Sua chave GPG venceu. Os commits antigos ficam inválidos? Qual código `%G?` eles passam a
   ter?
6. Por que `fetch-depth: 0` é obrigatório no workflow de verificação?
7. No exemplo 11, por que `keytocard` exige backup prévio?
8. No caso 14, cite dois riscos que a assinatura de commits **não** cobriu.

*(Respostas: 1 — `.git/config` é mais específico; use `git config --list --show-origin`.
2 — o padrão casa com o próprio diretório e não com os repositórios dentro dele. 3 — sem ele,
com `set -e`, o script morre calado no primeiro usuário sem chave. 4 — `U` é assinatura boa de
alguém que você não reconhece; `B` é assinatura que não confere com o conteúdo — só `B` indica
adulteração. 5 — continuam válidos, com código `Y`, e permanecem `Verified` no GitHub.
6 — porque o clone padrão é raso e não há histórico para auditar; o teste passaria sempre.
7 — `keytocard` move a chave para o cartão e apaga a cópia local. 8 — leitura de repositórios
privados; abertura/aprovação de PR, alteração de rulesets e publicação de releases.)*
