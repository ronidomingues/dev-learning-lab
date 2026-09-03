# 16 · Agentes, frases secretas e hardware

> Nível: intermediário · Atualizado em 13/08/2026

Este é o arquivo do "funciona, mas me pede senha o tempo todo" e do "no terminal vai, no VS
Code não". A criptografia leva microssegundos; o que consome a sua tarde é o agente.

---

## 1. O problema

Sua chave privada em disco está **cifrada** com uma chave derivada da sua frase secreta. Para
assinar, ela precisa ser decifrada. Se isso acontecesse a cada commit, você digitaria a frase
30 vezes por dia — e, previsivelmente, tiraria a frase secreta.

O **agente** resolve: decifra uma vez, guarda em memória, e responde às requisições seguintes.

```
frase secreta ──KDF──▶ chave que decifra ──▶ chave privada em memória
                                                     │
                            git commit ──requisita──▶ agente ──▶ assinatura
```

Dois agentes, um para cada mundo:

| | `ssh-agent` | `gpg-agent` |
|---|---|---|
| guarda | chaves SSH | chaves OpenPGP (e SSH, se você quiser) |
| como pede a senha | pelo terminal, ou `ssh-askpass` | pelo `pinentry` |
| onde se configura | `~/.ssh/config` | `~/.gnupg/gpg-agent.conf` |
| cache padrão | até o agente morrer | 600 s de inatividade, máx. 7200 s |

---

## 2. `ssh-agent`

```bash
eval "$(ssh-agent -s)"                    # inicia (a maioria das distros já faz)
ssh-add ~/.ssh/id_assinatura              # carrega, pedindo a frase uma vez
ssh-add -l                                # lista o que está carregado
ssh-add -D                                # esquece tudo
```

Carregar automaticamente no primeiro uso, com validade:

```
# ~/.ssh/config
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_assinatura
```

```bash
ssh-add -t 8h ~/.ssh/id_assinatura        # esquece depois de 8 horas
```

> `-t` é subestimado. Um agente que guarda a chave "até reiniciar" guarda também durante as
> três semanas em que você nunca desliga o notebook. Oito horas cobre o dia de trabalho e
> força uma reautenticação diária, que é barata.

**macOS.** O `ssh-agent` do sistema integra com o Keychain:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_assinatura
```

```
# ~/.ssh/config
Host *
    UseKeychain yes
    AddKeysToAgent yes
```

**Windows.** O `ssh-agent` é um serviço:

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_assinatura
```

---

## 3. `gpg-agent` e `pinentry`

O `gpg-agent` sobe sozinho no primeiro uso do `gpg`. Quem pede a senha é o **`pinentry`**, um
programa separado — e é aí que mora a maior parte das dores.

```ini
# ~/.gnupg/gpg-agent.conf
default-cache-ttl 3600      # 1 h de inatividade
max-cache-ttl 28800         # 8 h no máximo, mesmo em uso contínuo
pinentry-program /usr/bin/pinentry-gnome3
```

```bash
gpgconf --reload gpg-agent    # aplica sem reiniciar a máquina
```

### Qual `pinentry` usar

| Ambiente | Programa | Onde costuma estar |
|---|---|---|
| Linux + GNOME | `pinentry-gnome3` | `/usr/bin/` |
| Linux + KDE | `pinentry-qt` | `/usr/bin/` |
| Linux sem gráfico / SSH remoto | `pinentry-curses` | `/usr/bin/` |
| **macOS** | **`pinentry-mac`** | `$(brew --prefix)/bin/` |
| Windows | vem com o Gpg4win | — |

**No macOS o `pinentry-mac` é obrigatório na prática.** Sem ele, o `pinentry` padrão tenta
pedir a senha no terminal, não consegue, e o commit falha com uma mensagem que não explica
nada.

### `GPG_TTY`

```bash
export GPG_TTY=$(tty)
```

Diz ao GnuPG em qual terminal desenhar o prompt. Sem ela, o erro clássico:

```
gpg: signing failed: Inappropriate ioctl for device
error: gpg failed to sign the data
```

Ponha no `~/.bashrc` ou `~/.zshrc`. E lembre-se de que a mudança só vale em terminal novo.

### Diagnóstico

```bash
gpg-connect-agent 'keyinfo --list' /bye   # o que está em cache
gpgconf --list-options gpg-agent          # configuração efetiva
gpgconf --kill gpg-agent                  # derruba (sobe de novo no próximo uso)
echo teste | gpg --clearsign              # testa a assinatura FORA do Git
```

> Esse último comando é o mais útil de todos. `error: gpg failed to sign the data` é uma
> mensagem genérica do Git; `gpg --clearsign` mostra o erro **real** do GnuPG.

---

## 4. O caso "no terminal funciona, no editor não"

Sintoma clássico: `git commit` no terminal assina; o botão de commit do VS Code, do
IntelliJ ou do SourceTree falha.

Três causas, nesta ordem de probabilidade:

1. **O editor não herdou as variáveis de ambiente.** Aplicativos gráficos abertos pelo menu
   do sistema não leem `~/.bashrc`, e portanto não têm `GPG_TTY` nem `SSH_AUTH_SOCK`.
   *Correção:* abra o editor a partir do terminal (`code .`), ou defina as variáveis no
   ambiente de sessão do sistema (`~/.profile`, `launchctl setenv` no macOS,
   variáveis de usuário no Windows).
2. **O `pinentry` não tem onde aparecer.** Com `pinentry-curses` e um editor gráfico, o
   prompt é desenhado num terminal que não existe. *Correção:* use um `pinentry` gráfico.
3. **O editor usa o Git dele, não o seu.** Alguns trazem um Git embutido, mais antigo.
   *Correção:* aponte o editor para o Git do sistema (no VS Code,
   `"git.path": "/usr/bin/git"`).

---

## 5. Hardware: token físico

### O que muda

A chave privada **nasce e vive dentro do token** e não pode ser extraída. Assinar exige o
dispositivo presente e, tipicamente, um toque físico.

O que isso protege: um malware que leia `~/.ssh/` e `~/.gnupg/` não consegue assinar no seu
nome. Esse é justamente o vetor que mais cresceu em ataques a desenvolvedores — pacote
malicioso instalado por engano, que varre a casa atrás de credenciais.

O que **não** protege: malware ativo enquanto você trabalha pode pedir uma assinatura no
instante em que você toca o token achando que é para outra coisa.

### SSH em FIDO2 (o caminho mais simples)

```bash
ssh-keygen -t ed25519-sk -O resident -O verify-required -f ~/.ssh/id_yubikey
git config --global user.signingkey ~/.ssh/id_yubikey.pub
```

O arquivo em disco não é a chave privada — é um *handle* que aponta para dentro do token.
Recuperar as chaves residentes numa máquina nova:

```bash
ssh-keygen -K            # extrai os handles das chaves residentes do token
```

Exige OpenSSH ≥ 8.2; no Linux, `libfido2`.

### GPG em cartão OpenPGP

```bash
gpg --card-status                # o token é reconhecido?
gpg --edit-key <FPR>
> key 1                          # seleciona a subchave de assinatura
> keytocard                      # MOVE para o cartão (a cópia local é destruída)
> save
```

> **`keytocard` move, não copia.** Faça o backup antes
> (`gpg --armor --export-secret-keys`), guardado offline. Sem backup, perder o token é perder
> a chave.

### Comprar dois

O conselho operacional que mais se repete entre quem usa: **compre dois tokens e configure os
dois**. Guarde o segundo em outro lugar físico. Token único é ponto único de falha, e a falha
aqui não é "fico sem acessar" — é "perdi a identidade".

Preços em [80-custos-e-licencas.md](80-custos-e-licencas.md).

---

## 6. Alternativas em software

| Ferramenta | Plataforma | Como funciona | Ressalvas |
|---|---|---|---|
| **1Password** | todas | agente SSH próprio, desbloqueio por biometria | pago; exige `key::` no config (Git ≥ 2.35) |
| **Secretive** | macOS | chave no Secure Enclave, nunca em disco | gratuito, código aberto; só macOS |
| **Keeper / Bitwarden** | todas | agente SSH próprio | pago; maturidade menor |
| **`gitsign` (Sigstore)** | todas | **sem chave**: identidade OIDC + certificado de 10 min | o GitHub ainda **não** marca `Verified` ([65](65-estado-da-arte.md)) |
| **`ssh-agent` + `-t`** | todas | o caminho padrão, sem instalar nada | é o suficiente para a maioria |

**Recomendação, e é opinião:** comece com `ssh-agent` e `-t 8h`. Vá para 1Password ou
Secretive se você já usa a ferramenta por outros motivos. Vá para token físico se você
publica software que outras pessoas instalam, ou se a empresa exige. Não comece pelo token:
é fácil comprar um, configurar mal, e ficar com uma chave inutilizável e uma frustração.

---

## 7. Higiene da frase secreta

- **Ponha uma.** Uma chave sem frase secreta é um arquivo que qualquer processo seu — e
  qualquer backup mal configurado — carrega consigo.
- **Frase, não senha.** Quatro ou cinco palavras aleatórias vencem `Tr0ub4dor&3` em entropia
  e em digitabilidade.
- **Guarde-a no gerenciador de senhas.** Frase que só existe na sua cabeça é frase que você
  perde.
- **Não a reutilize.** Ela protege exatamente uma coisa; se vazar por outro caminho, você
  perdeu esta também.
- **Trocar é barato:**
  ```bash
  ssh-keygen -p -f ~/.ssh/id_assinatura     # SSH
  gpg --passwd <FPR>                        # GPG
  ```
  Trocar a frase **não** muda a chave: nada precisa ser recadastrado.

---

## Autoteste

1. Para que serve um agente, e o que aconteceria sem ele?
2. Por que `GPG_TTY` é necessária, e qual erro literal aparece sem ela?
3. Seu editor gráfico não assina, mas o terminal sim. Quais são as três causas prováveis?
4. Qual comando isola se o problema é do Git ou do GnuPG?
5. Por que `keytocard` exige backup prévio?
6. O que um token físico protege, e o que não protege?
7. Por que comprar dois tokens?
8. Trocar a frase secreta obriga a recadastrar a chave no GitHub?

*(Respostas: 1 — guarda a chave destravada em memória; sem ele você digitaria a frase a cada
commit e acabaria removendo a frase. 2 — diz ao GnuPG em qual terminal pedir a senha; sem ela,
`gpg: signing failed: Inappropriate ioctl for device`. 3 — o editor não herdou as variáveis de
ambiente; o `pinentry` não tem onde aparecer; o editor usa um Git embutido. 4 —
`echo teste | gpg --clearsign`. 5 — ele move a chave para o cartão e destrói a cópia local.
6 — protege contra roubo da chave por malware que lê o disco; não protege contra malware ativo
que peça uma assinatura no momento do toque. 7 — token único é ponto único de falha, e perdê-lo
significa perder a identidade. 8 — não; a chave não muda.)*

---

**Próximo:** [17-automacao-e-ci.md](17-automacao-e-ci.md).
