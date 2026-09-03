# 4 · Como começar — do ambiente pronto ao selo `Verified`

> Nível: iniciante · Atualizado em 13/08/2026 · Assume o ambiente do
> [03-instalacao.md](03-instalacao.md) pronto

Este arquivo tem as **duas trilhas lado a lado**: SSH e GPG. Você não precisa das duas —
escolha uma pela tabela abaixo, faça-a inteira, e volte à outra só se precisar.

Meta: **um commit seu com o selo `Verified` no GitHub**. Nada mais.

---

## Antes: escolha a trilha

| | **SSH** | **GPG** |
|---|---|---|
| Tempo até o `Verified` | **10 min** | 30 min (mais 20 se o `pinentry` brigar) |
| Peças envolvidas | Git + OpenSSH | Git + GnuPG + `gpg-agent` + `pinentry` |
| Reaproveita chave que você já tem | **sim**, a do `git push` | não |
| Expiração automática da chave | **não** — a validade vive no `allowed_signers`, um arquivo à parte | **sim**, embutida na chave |
| Revogação formal | por lista de revogação (KRL), pouco usada na prática | **sim**, certificado de revogação padronizado |
| Serve fora do Git (e-mail, pacotes, arquivos) | pouco | **sim**, é o padrão do mundo OpenPGP |
| Chave em token físico (YubiKey) | sim (FIDO/`sk-ssh-ed25519`) | sim (cartão OpenPGP), mais maduro |
| Curva de aprendizado | rasa | íngreme |
| Exigido por alguma empresa/distro? | raramente | às vezes — Debian, Fedora, muitas empresas reguladas |

**Escolha SSH se** você quer resolver isso hoje, trabalha sozinho ou numa equipe pequena, e o
objetivo é o `Verified` e a prova de autoria. É o caso de 90 % das pessoas, e é a minha
recomendação (opinião profissional, fundamentada em
[19-como-escolher.md](19-como-escolher.md)).

**Escolha GPG se** a sua empresa/projeto já padronizou OpenPGP, se você precisa que a chave
**expire sozinha**, se precisa de revogação formal auditável, ou se vai assinar outras coisas
além de commits (releases, pacotes, e-mail).

Dá para trocar depois sem perder o passado. A migração está em
[13-gpg-a-fundo.md § migração](13-gpg-a-fundo.md).

---

# TRILHA A · SSH

## A1. Você já tem uma chave?

```bash
ls -la ~/.ssh/*.pub
```

```
# se aparecer algo assim, você já tem — pule para A3:
-rw-r--r-- 1 voce voce  99 mar 12  2025 /home/voce/.ssh/id_ed25519.pub
```

> **Pode usar a mesma chave do `git push` para assinar?** Pode, tecnicamente, e o GitHub
> aceita: basta cadastrá-la **duas vezes**, uma como *Authentication key* e outra como
> *Signing key*. Se prefere separar — e há um bom argumento para separar, discutido em
> [14-ssh-signing-a-fundo.md](14-ssh-signing-a-fundo.md) —, gere uma nova em A2.

## A2. Gerar a chave

```bash
ssh-keygen -t ed25519 -C "seu-email@exemplo.com" -f ~/.ssh/id_assinatura
```

> Gera um par Ed25519 (o algoritmo padrão hoje: rápido, curto e seguro). `-C` é só um
> comentário que fica no fim da chave pública, para você se lembrar de que chave é essa.
> `-f` dá o nome do arquivo — sem ele, sobrescreveria a sua chave existente.

Ele pergunta uma frase secreta. **Ponha uma.** Ela é o que separa "roubaram meu notebook" de
"roubaram minha identidade". Você não vai digitá-la a cada commit — o `ssh-agent` cuida
disso (veja [16-hardware-e-agentes.md](16-hardware-e-agentes.md)).

**Verifique:**

```bash
ls -l ~/.ssh/id_assinatura ~/.ssh/id_assinatura.pub
```

```
# esperado — repare nas permissões:
-rw------- 1 voce voce 464 ago 13 12:00 /home/voce/.ssh/id_assinatura      ← 600, só você
-rw-r--r-- 1 voce voce 105 ago 13 12:00 /home/voce/.ssh/id_assinatura.pub  ← 644, pública
```

Se a privada não estiver `600`: `chmod 600 ~/.ssh/id_assinatura`.

## A3. Cadastrar a chave pública no GitHub — **como Signing key**

Copie a chave **pública**:

```bash
cat ~/.ssh/id_assinatura.pub
```

```
# saída real do laboratório (a sua será diferente):
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINi2+bz2l8XnlynCFEuDzRyQkaC4VJmWOiCCFh4aa6Q0 ana@exemplo.dev
```

Agora, **pelo navegador**: <https://github.com/settings/ssh/new>

1. **Title**: um nome que você reconheça depois (`notebook-trabalho`).
2. **Key type**: mude para **Signing Key**. ← *este é o passo que quase todo mundo erra*
3. **Key**: cole a linha inteira.
4. **Add SSH key**.

Ou, se você tem o `gh` autenticado:

```bash
gh ssh-key add ~/.ssh/id_assinatura.pub --type signing --title "notebook-trabalho"
```

**Verifique:**

```bash
gh ssh-key list
# esperado: uma linha com "signing" na coluna de tipo
```

> **A pegadinha número um deste curso.** *Authentication key* e *Signing key* são listas
> separadas no GitHub. Cadastrar a chave só como *Authentication* faz o `push` funcionar e o
> selo **nunca** aparecer — e não há mensagem de erro nenhuma explicando isso. Se depois de
> tudo o commit ficar `Unverified`, volte aqui primeiro.

## A4. Confirmar o e-mail

O GitHub só marca `Verified` se o e-mail do commit estiver **verificado na conta dona da
chave**.

```bash
git config --get user.email
```

Compare com a lista em <https://github.com/settings/emails>. Precisa estar lá, com o selo de
verificado. Se você prefere não expor seu e-mail, use o e-mail privado que o GitHub fornece
(aparece na mesma página, no formato `12345678+usuario@users.noreply.github.com`):

```bash
git config --global user.email "12345678+usuario@users.noreply.github.com"
```

## A5. Configurar o Git — três linhas

```bash
git config --global gpg.format ssh
```
> Diz ao Git para assinar no formato SSH em vez de OpenPGP.

```bash
git config --global user.signingkey ~/.ssh/id_assinatura.pub
```
> **O caminho da chave PÚBLICA** (`.pub`), não da privada. Estranho, mas correto: o Git usa
> a pública para localizar a privada correspondente (no disco ou no agente).

```bash
git config --global commit.gpgsign true
git config --global tag.gpgSign true
```
> Assina todo commit e toda tag automaticamente, sem você precisar lembrar do `-S`.
> Assinar tag é tão importante quanto assinar commit, e é o que mais se esquece.

**Verifique:**

```bash
git config --global --get-regexp 'gpg|sign'
```

```
# esperado:
gpg.format ssh
user.signingkey /home/voce/.ssh/id_assinatura.pub
commit.gpgsign true
tag.gpgsign true
```

## A6. Montar o `allowed_signers` (para verificar na sua máquina)

Este passo é **opcional para o selo do GitHub** e **obrigatório para verificar localmente**.
Sem ele, `git log --show-signature` diz "assinatura boa, dono desconhecido".

```bash
mkdir -p ~/.config/git
printf '%s namespaces="git" %s\n' \
  "$(git config --get user.email)" "$(cat ~/.ssh/id_assinatura.pub)" \
  >> ~/.config/git/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers
```

> Cria o arquivo que liga chaves a pessoas e diz ao Git onde ele está.
> `namespaces="git"` restringe a chave a assinar objetos do Git — sem isso, uma assinatura
> feita para outra finalidade poderia ser aceita aqui.

**Verifique:**

```bash
cat ~/.config/git/allowed_signers
# esperado: seu-email namespaces="git" ssh-ed25519 AAAA... comentário
```

## A7. O primeiro commit assinado

```bash
cd ~/algum-repositorio-seu
echo "teste de assinatura" >> LEIAME.md
git add LEIAME.md
git commit -m "primeiro commit assinado"
```

**Verifique, localmente:**

```bash
git log --show-signature -1
```

```
# saída real do laboratório:
commit b0f4df651ca75ad8fd95cd9d8a551a0c6ca2c2ff
Good "git" signature for ana@exemplo.dev with ED25519 key SHA256:dOPYp66kQRpqWjjSA3F995N6QFG77icC5HYiw9E2Be8
Author: Ana Souza <ana@exemplo.dev>
Date:   Thu Aug 13 12:28:07 2026 -0300

    primeiro commit assinado
```

Ou, mais curto, o código de status:

```bash
git log --format='%h %G? %GS' -1
# esperado: b0f4df6 G ana@exemplo.dev
#           └ o G é o que importa
```

## A8. O selo no GitHub

```bash
git push
```

Abra o commit no GitHub. Ao lado do hash deve estar:

```
✔ Verified
```

Clicando nele, o GitHub mostra a chave usada e a frase *"This commit was signed with the
committer's verified signature."*

**Pronto.** Se apareceu, você terminou. Vá para [06-exemplos.md](06-exemplos.md).
Se apareceu `Unverified`, vá para a seção **"Os cinco erros"**, no fim deste arquivo.

---

# TRILHA B · GPG

## B1. Gerar a chave

```bash
gpg --full-generate-key
```

> Abre o assistente interativo. As respostas que você deve dar:

| Pergunta | Responda | Por quê |
|---|---|---|
| *Please select what kind of key you want* | **`9` (ECC sign and encrypt)**, ou `1` (RSA and RSA) | ECC (Ed25519) é menor e mais rápido. RSA 4096 é a escolha conservadora, aceita em todo lugar |
| *Please select which elliptic curve* | **`1` (Curve 25519)** | o padrão moderno |
| *Key is valid for?* | **`2y`** | ver a nota abaixo |
| *Real name* | seu nome | aparece no commit |
| *Email address* | **o e-mail verificado no GitHub** | é o que amarra a chave à conta |
| *Comment* | vazio | comentário em UID dá mais problema do que ajuda |
| frase secreta | **ponha uma** | é a única coisa entre um notebook roubado e a sua identidade |

> **Por que `2y` e não "nunca expira"?** Porque expiração é um *interruptor morto*: se você
> perder o acesso à chave e não puder revogá-la, ela para sozinha em dois anos. Uma chave
> "para sempre" que você perdeu fica válida para sempre. E renovar é um comando de 5
> segundos, que você pode dar **depois** do vencimento — o vencimento não destrói nada.
>
> Contrapartida honesta, e verificada no teste: **com a chave vencida, o `git commit -S`
> falha e o commit não é criado** (`error: gpg failed to sign the data`). É um susto anual.
> Anote a data na agenda.

Alternativa não interativa, se você prefere:

```bash
gpg --quick-generate-key "Seu Nome <seu-email@exemplo.com>" ed25519 sign 2y
```

**Verifique:**

```bash
gpg --list-secret-keys --keyid-format=long
```

```
# saída real do laboratório:
sec   ed25519/69D87EAC1C026253 2026-08-13 [SC] [expira: 2028-08-12]
      1236820BC521B8EB9D3DF2C469D87EAC1C026253
uid               [final] Ana Souza <ana@exemplo.dev>
#            └─ ID longo: é isto que vai em user.signingkey
```

O `[SC]` quer dizer que a chave pode **S**ign (assinar) e **C**ertify (certificar). Se não
houver `S`, ela não serve para assinar commits.

## B2. Fazer o backup **agora**, antes de qualquer outra coisa

Este passo não é opcional. Perder a chave privada significa perder a capacidade de assinar
como você — e o certificado de revogação é o que permite dizer ao mundo "essa chave não é
mais minha" caso ela vaze.

```bash
FPR=$(gpg --list-secret-keys --with-colons | awk -F: '/^fpr:/ {print $10; exit}')

gpg --armor --export-secret-keys "$FPR" > ~/chave-privada-BACKUP.asc
gpg --armor --export "$FPR"             > ~/chave-publica.asc
ls ~/.gnupg/openpgp-revocs.d/            # o certificado de revogação já existe aqui
```

> O GnuPG **gera o certificado de revogação sozinho**, na criação da chave, e o guarda em
> `~/.gnupg/openpgp-revocs.d/<FPR>.rev`. Guarde uma cópia dele **fora desta máquina**.
>
> Detalhe que só se descobre na hora do desespero, e que confirmei no teste: esse arquivo
> vem com todas as linhas prefixadas por `:` (para você não o importar por acidente). Para
> usá-lo de verdade, é preciso remover esses dois-pontos antes:
> `sed 's/^://' arquivo.rev > revogacao.asc`.

Leve `~/chave-privada-BACKUP.asc` e o `.rev` para um lugar seguro **e offline** (pendrive num
cofre, gerenciador de senhas). Depois apague o `.asc` do disco:

```bash
shred -u ~/chave-privada-BACKUP.asc   # depois de copiar para o lugar seguro
```

## B3. Exportar a chave pública para o GitHub

```bash
gpg --armor --export "$FPR"
```

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEZ...
-----END PGP PUBLIC KEY BLOCK-----
```

Copie **tudo**, inclusive as linhas `BEGIN` e `END`.

Pelo navegador: <https://github.com/settings/gpg/new> → cole → **Add GPG key**.

Ou pelo `gh`:

```bash
gpg --armor --export "$FPR" | gh gpg-key add -
```

**Verifique:**

```bash
gh gpg-key list
```

## B4. Configurar o Git

```bash
git config --global gpg.format openpgp
```
> Explícito de propósito: se você já experimentou o modo SSH antes, `gpg.format` pode estar
> como `ssh` e o erro resultante é confuso. Alternativa: `git config --global --unset gpg.format`.

```bash
git config --global user.signingkey 69D87EAC1C026253
```
> O ID longo (16 caracteres hexadecimais) que você viu em B1. A impressão digital de 40
> caracteres também funciona.

```bash
git config --global commit.gpgsign true
git config --global tag.gpgSign true
```

**Se você usa uma subchave** para assinar (o arranjo mais seguro, explicado em
[13-gpg-a-fundo.md](13-gpg-a-fundo.md)), acrescente `!` ao final do ID para forçar aquela
subchave específica:

```bash
git config --global user.signingkey 4BB6D45482678BE3!
```

## B5. `GPG_TTY` — o passo que evita o erro mais comum do GPG

```bash
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc     # bash
echo 'export GPG_TTY=$(tty)' >> ~/.zshrc      # zsh (macOS)
source ~/.bashrc
```

**Verifique:**

```bash
echo $GPG_TTY
# esperado: /dev/pts/3 (algo assim). Vazio = a linha não foi lida; abra um terminal novo.
```

No **macOS**, além disso, o `pinentry-mac` precisa estar configurado — veja
[03-instalacao.md § 3.2](03-instalacao.md).

## B6. O primeiro commit assinado

```bash
cd ~/algum-repositorio-seu
echo "teste" >> LEIAME.md
git add LEIAME.md
git commit -m "primeiro commit assinado com GPG"
```

Vai aparecer o `pinentry` pedindo sua frase secreta. Depois disso, o `gpg-agent` guarda a
chave destravada por um tempo (padrão: 10 minutos de inatividade, até 2 horas).

**Verifique:**

```bash
git log --show-signature -1
```

```
# saída real do laboratório:
commit 613fdd8cf...
gpg: Assinatura feita qui 13 ago 2026 12:28:07 -03
gpg:                usando EDDSA chave 1236820BC521B8EB9D3DF2C469D87EAC1C026253
gpg: Assinatura correta de "Ana Souza <ana@exemplo.dev>" [final]
Author: Ana Souza <ana@exemplo.dev>
```

```bash
git log --format='%h %G? %GK' -1
# esperado: 613fdd8 G 1236820BC521B8EB9D3DF2C469D87EAC1C026253
```

## B7. O selo no GitHub

```bash
git push
```

Mesmo resultado da trilha SSH: `✔ Verified` ao lado do commit.

---

# O ciclo de trabalho, depois de configurado

Isto é o que muda no seu dia a dia: **nada**.

```
editar → git add → git commit → (assina sozinho) → git push
```

Com `commit.gpgsign true`, você não digita `-S` nunca mais. As únicas diferenças perceptíveis:

| Quando | O que acontece |
|---|---|
| primeiro commit do dia (GPG, com frase secreta) | o `pinentry` pede a senha uma vez |
| primeiro commit do dia (SSH, com frase secreta) | o `ssh-agent` pede a senha uma vez |
| commit num repositório onde você não quer assinar | `git commit --no-gpg-sign -m "..."` |
| a chave GPG expirou | o commit **falha**; renove com `gpg --quick-set-expire <FPR> 2y` |

Para conferir o estado de um histórico rapidamente:

```bash
git log --format='%h %G? %s' -10
```

```
# saída real:
6dda04c N commit sem assinatura
613fdd8 G commit assinado com GPG
b0f4df6 G commit assinado com SSH
```

Os códigos: `G` boa · `B` **ruim** · `U` boa, assinante desconhecido · `N` sem assinatura ·
`Y` feita por chave que depois expirou · `R` chave revogada · `E` não deu para checar. A
tabela completa está no
[05-manual-de-uso.md](05-manual-de-uso.md).

---

# Os cinco erros que todo iniciante comete (no uso, não na instalação)

### 1. Cadastrou a chave SSH como *Authentication* e não como *Signing*

**Sintoma:** o `push` funciona, `git log --show-signature` diz `Good signature`, e o GitHub
insiste em `Unverified`.
**Correção:** <https://github.com/settings/keys> — a chave precisa aparecer na seção
**"SSH signing keys"**. Se estiver só em "Authentication keys", cadastre-a de novo, agora
com *Key type: Signing Key*. A mesma chave pode estar nas duas listas.

### 2. O e-mail do commit não está verificado na conta

**Sintoma:** `Unverified`, e ao clicar o GitHub diz que não conseguiu associar a assinatura à
conta.
**Correção:**

```bash
git config --get user.email                     # o que o Git usa
git log --format='%ae' -1                       # o que foi gravado no commit
```

Os dois têm de estar em <https://github.com/settings/emails>, verificados. Note que **mudar a
configuração não conserta commits já feitos** — o e-mail está gravado dentro deles.

### 3. Configurou `--global` mas o repositório tem configuração local que sobrepõe

**Sintoma:** funciona num repositório e não em outro.
**Correção:**

```bash
git config --list --show-origin | grep -E 'signingkey|gpgsign|gpg.format'
```

A configuração local (`.git/config`) vence a global sempre. É comum ter um `user.email`
antigo dentro de um repositório específico.

### 4. Apontou `user.signingkey` para a chave **privada** no modo SSH

**Sintoma:** `error: Load key ...: error in libcrypto` ou "not a public key".
**Correção:** aponte para o arquivo **`.pub`**:

```bash
git config --global user.signingkey ~/.ssh/id_assinatura.pub
```

Contraintuitivo, mas é assim: o Git usa a pública como identificador para achar a privada.

### 5. Rebase/squash "apagou" as assinaturas

**Sintoma:** você assinou tudo, fez `rebase` ou usou *Squash and merge* no GitHub, e os
commits resultantes estão sem assinatura.
**Por quê:** rebase e squash **criam commits novos**. O commit assinado original não foi
alterado — ele foi substituído por outro, com outro hash. E o servidor do GitHub não tem a
sua chave privada para assinar o resultado.
**Correção:**
- localmente, garanta `commit.gpgsign true` (confirmado no teste: com ele ligado, o `rebase`
  **re-assina** os commits reescritos);
- no GitHub, prefira *Merge commit* (que ele assina com a chave dele) a *Rebase and merge*
  (que ele não consegue assinar);
- detalhes em [12-anatomia-do-commit.md](12-anatomia-do-commit.md) e
  [18-politica-de-equipe.md](18-politica-de-equipe.md).

---

## Onde ir depois

| Se você quer | Vá para |
|---|---|
| receitas prontas (dois e-mails, bot, YubiKey, auditoria) | [06-exemplos.md](06-exemplos.md) |
| ver tudo isso rodando de ponta a ponta, com as falhas | [07-projeto-modelo/](07-projeto-modelo/) |
| a referência de comandos | [05-manual-de-uso.md](05-manual-de-uso.md) |
| entender **por que** funciona | [10-fundamentos.md](10-fundamentos.md) |
| decidir SSH × GPG com argumento | [19-como-escolher.md](19-como-escolher.md) |
| implantar na equipe | [18-politica-de-equipe.md](18-politica-de-equipe.md) |

---

## Autoteste

1. Por que `user.signingkey` aponta para a chave **pública** no modo SSH?
2. O que acontece se você cadastrar a chave SSH no GitHub só como *Authentication key*?
3. Por que pôr validade de 2 anos numa chave GPG, se isso vai me dar trabalho depois?
4. Você trocou de e-mail e verificou o novo no GitHub. Os commits antigos passam a ficar
   `Verified`?
5. Qual comando mostra, em uma linha por commit, se cada um está assinado?
6. Por que o *Squash and merge* do GitHub produz um commit sem a sua assinatura?
7. Você quer, num repositório específico, **não** assinar. Como faz sem mexer no global?

*(Respostas: 1 — a pública é o identificador com que o Git localiza a privada, no disco ou no
agente. 2 — o `push` funciona e o selo nunca aparece, sem mensagem de erro. 3 — expiração é
interruptor morto: uma chave perdida para sozinha; renovar é um comando. 4 — não; o e-mail
está gravado dentro de cada commit. 5 — `git log --format='%h %G? %s'`. 6 — squash cria um
commit novo no servidor, e o GitHub não tem sua chave privada. 7 — `git config --local
commit.gpgsign false` dentro dele.)*
