# 13 · GPG a fundo

> Nível: intermediário → avançado · Atualizado em 13/08/2026 · Testado com GnuPG 2.2.27

Tudo que existe no OpenPGP além do "gere uma chave e cole no GitHub": estrutura de chave
mestra e subchaves, expiração, revogação, modelo de confiança, distribuição, backup e
migração. Se você escolheu a trilha SSH e não pretende mudar, este arquivo é opcional —
mas a seção sobre **subchaves** vale a leitura de qualquer jeito, porque é o único mecanismo
por aí que separa *identidade* de *material criptográfico*.

---

## 1. A estrutura real de uma chave OpenPGP

Uma "chave GPG" não é uma chave. É uma **árvore**:

```
chave primária (mestra)   [C] certify — só serve para assinar as próprias subchaves e UIDs
│
├── UID: Ana Souza <ana@exemplo.dev>
├── UID: Ana Souza <ana@empresa.com>
│
├── subchave [S] sign        ← esta é a que assina seus commits
├── subchave [E] encrypt     ← cifra mensagens para você
└── subchave [A] authenticate ← login SSH, se você quiser
```

```bash
gpg --list-secret-keys --keyid-format=long
```

```
sec   ed25519/69D87EAC1C026253 2026-08-13 [SC] [expira: 2028-08-12]
      1236820BC521B8EB9D3DF2C469D87EAC1C026253
uid               [final] Ana Souza <ana@exemplo.dev>
```

Leitura da saída:

| Símbolo | Significa |
|---|---|
| `sec` | chave **sec**reta primária (`pub` = só a pública) |
| `ssb` | **s**u**b**chave secreta |
| `[C]` | pode **C**ertificar (assinar outras chaves) — é o poder de definir sua identidade |
| `[S]` | pode a**S**sinar dados |
| `[E]` | pode cifrar (**E**ncrypt) |
| `[A]` | pode autenticar |
| `[SC]` | neste exemplo, a primária faz as duas coisas — o padrão do `--quick-generate-key` |

### Por que separar em subchaves

O poder está concentrado na primária: quem a tem pode **criar novas subchaves, adicionar
e-mails à sua identidade e revogar o que quiser**. A subchave de assinatura só pode assinar.

O arranjo que os projetos sérios usam:

1. a chave **primária** fica offline (pendrive num cofre, ou máquina desconectada);
2. no notebook do dia a dia fica só a **subchave de assinatura**;
3. se o notebook for comprometido, você usa a primária (offline) para revogar aquela
   subchave e emitir outra — **sem perder a identidade**, sem precisar avisar ninguém para
   trocar a chave que confia em você.

Isso é o que o SSH não tem. Chave SSH comprometida é chave trocada, e todo mundo que confiava
nela precisa atualizar o `allowed_signers`. É o argumento técnico mais forte a favor do GPG,
e vale exatamente na medida em que você realmente for manter a primária offline — se ela
estiver no mesmo notebook, o arranjo não vale nada.

```bash
# criar uma subchave só de assinatura, válida por 1 ano
gpg --quick-add-key <FPR> ed25519 sign 1y

# usar aquela subchave específica no Git (o "!" força; sem ele o gpg escolhe)
git config --global user.signingkey 4BB6D45482678BE3!
```

### Tirar a primária de circulação

```bash
# 1. exportar TUDO para o backup offline (guarde bem)
gpg --armor --export-secret-keys <FPR> > primaria-completa.asc

# 2. exportar só as subchaves
gpg --armor --export-secret-subkeys <FPR> > subchaves.asc

# 3. apagar tudo do chaveiro local e reimportar só as subchaves
gpg --delete-secret-keys <FPR>
gpg --import subchaves.asc
```

Confirme que deu certo — o `sec#` com cerquilha é o sinal de que a primária **não** está mais
aqui:

```bash
gpg --list-secret-keys
# sec#  ed25519/...    ← a cerquilha diz: "chave primária ausente"
# ssb   ed25519/...    ← subchave presente
```

---

## 2. Expiração

Chave OpenPGP tem validade embutida, e a validade é **assinada pela primária** — ou seja,
prorrogá-la é uma operação criptográfica, não uma edição de metadado.

```bash
gpg --quick-set-expire <FPR> 2y        # a primária
gpg --quick-set-expire <FPR> 2y '*'    # e todas as subchaves
```

**O que acontece quando vence** — três comportamentos, todos verificados no teste:

| Situação | Resultado real |
|---|---|
| assinar **com** chave vencida | **falha**: `error: gpg failed to sign the data`, e o commit não é criado |
| verificar hoje um commit assinado **antes** de vencer | `%G?` = **`Y`**, com `gpg: Assinatura correta ... [expirado]` |
| no GitHub, commit assinado antes de vencer | continua **`Verified`** — ele grava o veredito no momento da verificação |

Ou seja: **o vencimento não invalida o passado, só impede o futuro.** É por isso que pôr
validade é bom negócio. O custo é um susto anual e um comando.

> **Opinião profissional:** ponha 2 anos, não "nunca". O argumento de quem prefere "nunca" é
> evitar o susto; o argumento do outro lado é que uma chave que você perdeu o controle e não
> consegue revogar fica válida para sempre. Expiração é um interruptor morto que funciona
> mesmo quando você não está lá para acioná-lo — e é o único mecanismo do OpenPGP que não
> depende de você conseguir agir.

---

## 3. Revogação

Revogar é dizer publicamente: *esta chave não deve mais ser aceita*. Diferente de expirar,
revogação é **imediata e definitiva**, e costuma implicar que houve comprometimento.

O GnuPG cria o certificado de revogação **na hora em que a chave nasce**:

```bash
ls ~/.gnupg/openpgp-revocs.d/
# 1236820BC521B8EB9D3DF2C469D87EAC1C026253.rev
```

Esse arquivo é o seu seguro: com ele você revoga a chave **mesmo tendo perdido a chave
privada**. Guarde uma cópia offline, hoje.

**A pegadinha que só se descobre no dia do desespero**, e que confirmei no teste: o arquivo
vem com todas as linhas prefixadas por `:`, para você não o importar sem querer. Importá-lo
assim falha com `gpg: nenhum dado OpenPGP válido encontrado`:

```bash
sed 's/^://' ~/.gnupg/openpgp-revocs.d/<FPR>.rev > revogacao.asc
gpg --import revogacao.asc
```

Efeito imediato, medido:

```
# antes:  fff55c4 [G] novo commit apos renovar expiracao
# depois: fff55c4 [R] novo commit apos renovar expiracao
gpg: Assinatura correta de "Nova Chave <nova@exemplo.dev>" [final]
gpg: AVISO: Esta chave foi revogada pelo seu dono!
gpg:          Isto poderia significar que a assinatura está forjada.
```

Note que `R` é mais severo que `Y`: revogação vale para **tudo**, inclusive o passado, porque
o pressuposto é que a chave pode ter estado em mãos erradas por tempo indeterminado.

Para revogar só uma subchave (o caso do notebook roubado, com a primária a salvo):

```bash
gpg --edit-key <FPR>
> key 1        # seleciona a subchave
> revkey       # revoga só ela
> save
```

E depois **publique**: exporte a chave atualizada e envie-a para onde ela estiver cadastrada
(GitHub inclusive — `gpg --armor --export <FPR> | gh gpg-key add -`). Revogação que ninguém
recebe não revoga nada.

---

## 4. Modelo de confiança — e por que ele não se usa mais

O GnuPG mantém um banco de confiança (`trustdb`) com níveis por chave:

| Nível | `%GT` | Significa |
|---|---|---|
| `ultimate` | `ultimate` | é sua própria chave |
| `full` | `fully` | você confia plenamente em quem certificou |
| `marginal` | `marginal` | confia parcialmente; três marginais somam uma completa |
| `never` / `undefined` | — | não decidiu, ou decidiu que não |

Valores reais, medidos:

```
83c225c G ultimate    ← chave GPG própria
877fffe G fully       ← assinatura SSH via allowed_signers
9c60d56 N undefined   ← commit sem assinatura
```

Esse mecanismo — a **rede de confiança** — foi projetado para funcionar sem autoridade
central, e não vingou: exigia encontros presenciais, a métrica não era compreensível para
não-especialistas, e a rede de servidores que a sustentava foi derrubada por envenenamento em
2019 ([11-historia.md](11-historia.md)).

**Na prática, hoje**, `%GT` diz pouco. O que decide se o seu commit fica `Verified` é o
GitHub, com o modelo dele: chave cadastrada + e-mail verificado. O `trustdb` só afeta o que
você vê na sua própria máquina.

Definir confiança manualmente, se você precisar:

```bash
gpg --edit-key <FPR>
> trust
> 5            # ultimate (só para as suas próprias chaves)
> save
```

---

## 5. Distribuição da chave pública

Quatro caminhos, em ordem decrescente de utilidade em 2026:

| Caminho | Como | Vale a pena? |
|---|---|---|
| **cadastrar no GitHub** | `gh gpg-key add` | **sim** — é o único que produz o selo |
| **WKD** (*Web Key Directory*) | publicar em `https://seudominio/.well-known/openpgpkey/...` | sim, se você tem domínio próprio e quer ser encontrável |
| `keys.openpgp.org` | `gpg --keyserver keys.openpgp.org --send-keys <FPR>` | talvez — só publica o e-mail após confirmação, e não aceita assinaturas de terceiros (foi a resposta ao envenenamento) |
| rede SKS | — | **não**: efetivamente morta desde 2019 |

Buscar a chave de alguém para verificar uma tag de release:

```bash
gpg --auto-key-locate wkd,keyserver --locate-keys mantenedor@projeto.org
gpg --keyserver keys.openpgp.org --recv-keys <FPR>
```

> Nunca busque por **e-mail** e confie no primeiro resultado: qualquer um pode criar uma
> chave com o e-mail de qualquer um. Busque pela **impressão digital**, obtida por um canal
> independente (o site do projeto, um anúncio assinado por chave que você já tem).

---

## 6. Backup e recuperação

O que precisa estar no seu backup offline:

```bash
FPR=<sua impressão digital>

gpg --armor --export-secret-keys "$FPR"     > 1-privada-completa.asc
gpg --armor --export "$FPR"                 > 2-publica.asc
gpg --export-ownertrust                     > 3-confianca.txt
cp ~/.gnupg/openpgp-revocs.d/"$FPR".rev       4-revogacao.rev
```

| Arquivo | Sem ele, você perde |
|---|---|
| privada completa | tudo: a capacidade de assinar como você |
| pública | nada (é recuperável da privada), mas é conveniente |
| ownertrust | as relações de confiança que você configurou |
| certificado de revogação | a capacidade de dizer ao mundo que a chave morreu |

Restaurar numa máquina nova:

```bash
gpg --import 1-privada-completa.asc
gpg --import-ownertrust < 3-confianca.txt
gpg --list-secret-keys
```

> **Onde guardar.** Não no mesmo disco, não no mesmo serviço de nuvem onde está o seu
> gerenciador de senhas, não num repositório privado (privado hoje, público em algum
> incidente futuro). Pendrive cifrado em local físico distinto é o padrão razoável.
> Duas cópias, dois lugares.

---

## 7. Migrar de GPG para SSH sem perder o passado

O caminho, e o ponto importante: **não apague nem revogue a chave GPG**.

```bash
# 1. chave SSH nova e cadastrada como Signing key
ssh-keygen -t ed25519 -C "$(git config --get user.email)" -f ~/.ssh/id_assinatura
gh ssh-key add ~/.ssh/id_assinatura.pub --type signing --title "$(hostname)"

# 2. trocar o método
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_assinatura.pub

# 3. NÃO revogue a chave GPG, e NÃO a remova do GitHub
```

Por quê: o GitHub grava o resultado da verificação de cada commit no momento em que ela
ocorre, então commits antigos permanecem `Verified` mesmo depois. Mas quem **clonar** o
repositório e verificar localmente precisa da chave pública GPG — se você a apagar do seu
chaveiro e do GitHub, esses commits passam a `E` (não foi possível verificar) para todo
mundo. Deixe a chave GPG cadastrada, com a validade correndo. Ela não atrapalha nada.

A migração inversa (SSH → GPG) é simétrica e mais simples: mantenha a chave SSH no
`allowed_signers` com `valid-before` na data da troca.

---

## 8. Referência rápida

| Tarefa | Comando |
|---|---|
| criar chave completa | `gpg --full-generate-key` |
| criar rápido | `gpg --quick-generate-key "Nome <email>" ed25519 sign 2y` |
| adicionar subchave de assinatura | `gpg --quick-add-key <FPR> ed25519 sign 1y` |
| adicionar e-mail | `gpg --quick-add-uid <FPR> "Nome <novo@email>"` |
| renovar validade | `gpg --quick-set-expire <FPR> 2y '*'` |
| trocar frase secreta | `gpg --passwd <FPR>` |
| exportar pública | `gpg --armor --export <FPR>` |
| exportar privada | `gpg --armor --export-secret-keys <FPR>` |
| exportar só subchaves | `gpg --armor --export-secret-subkeys <FPR>` |
| mover chave para cartão | `gpg --edit-key <FPR>` → `key N` → `keytocard` |
| revogar subchave | `gpg --edit-key <FPR>` → `key N` → `revkey` |
| revogar tudo | importar o `.rev` (removendo os `:`) |
| ver o que o agente tem em cache | `gpg-connect-agent 'keyinfo --list' /bye` |

---

## Autoteste

1. O que a chave primária pode fazer que a subchave de assinatura não pode?
2. Qual o ganho concreto de manter a primária offline? E quando esse ganho é zero?
3. Sua chave GPG venceu ontem. Você consegue assinar hoje? E os commits antigos, mudam de
   status?
4. Qual a diferença de efeito entre `%G?` = `Y` e `%G?` = `R`?
5. Por que o certificado de revogação vem com `:` no começo das linhas?
6. Por que buscar chave por e-mail num servidor é perigoso?
7. Você vai migrar para SSH. Por que **não** revogar a chave GPG?
8. O que precisa estar no backup, além da chave privada?

*(Respostas: 1 — certificar: criar subchaves, adicionar UIDs e revogar. 2 — permite revogar a
subchave comprometida e emitir outra sem perder a identidade; é zero se a primária estiver na
mesma máquina. 3 — não consegue assinar (o commit falha); os antigos passam a `Y` localmente
e continuam `Verified` no GitHub. 4 — `Y` afeta só o futuro; `R` invalida também o passado,
porque supõe comprometimento. 5 — para você não revogar a própria chave por acidente ao
importar o arquivo. 6 — qualquer um pode criar uma chave com o e-mail de qualquer um; é
preciso conferir a impressão digital por canal independente. 7 — quem clonar e verificar
localmente precisa da pública para os commits antigos; sem ela, viram `E`. 8 — a chave pública,
o ownertrust e o certificado de revogação.)*

---

**Próximo:** [14-ssh-signing-a-fundo.md](14-ssh-signing-a-fundo.md).
