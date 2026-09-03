# 75 · Armadilhas, mitos e más práticas

> Nível: todos · Atualizado em 13/08/2026

Vinte e seis itens: o erro, por que ele persiste, e a correção. Divididos entre **erros de
configuração**, **erros de entendimento**, **más práticas** e **mitos**.

---

## A · Erros de configuração

### A1. Cadastrar a chave SSH como *Authentication* em vez de *Signing*

**Sintoma:** `push` funciona, verificação local diz `Good signature`, GitHub diz `Unverified`.
**Por que persiste:** são duas listas separadas na mesma tela, o campo *Key type* é um menu
discreto, e **não há mensagem de erro** — o commit simplesmente não ganha selo.
**Correção:** cadastre de novo com *Key type: Signing Key*. A mesma chave pode estar nas duas
listas. Confirme com `gh ssh-key list`, procurando o tipo `signing`.

### A2. E-mail do commit não verificado na conta

**Sintoma:** `Unverified`, `reason: unverified_email`.
**Por que persiste:** quem tem vários e-mails muda `user.email` por repositório e esquece de
verificar o novo.
**Correção:** <https://github.com/settings/emails>. E lembre: **mudar a configuração não
conserta commits já feitos** — o e-mail está gravado dentro deles.

### A3. Apontar `user.signingkey` para a chave privada (modo SSH)

**Sintoma:** `error: Load key ...: error in libcrypto`.
**Por que persiste:** é contraintuitivo. Em todo o resto do mundo você usa a privada para
assinar.
**Correção:** aponte para o `.pub`. O Git usa a pública como identificador para localizar a
privada, que pode nem estar em disco.

### A4. Configuração local sobrepondo a global

**Sintoma:** funciona num repositório e não em outro.
**Correção:** `git config --list --show-origin | grep -E 'signingkey|gpgsign|user.email'`.
`.git/config` sempre vence `~/.gitconfig`.

### A5. `GPG_TTY` ausente

**Sintoma:** `gpg: signing failed: Inappropriate ioctl for device`.
**Por que persiste:** a variável não é definida por padrão em quase nenhuma distribuição, e a
mensagem não sugere a causa.
**Correção:** `export GPG_TTY=$(tty)` no `~/.bashrc` ou `~/.zshrc`, e abra um terminal novo.

### A6. Gerar a chave com `sudo`

**Sintoma:** `secret key not available` para uma chave que "acabou de ser criada".
**Por que persiste:** o hábito de pôr `sudo` quando algo falha.
**Correção:** com `sudo`, `$HOME` é `/root`. Apague `/root/.gnupg` e refaça como você mesmo.

### A7. Esquecer `tag.gpgSign`

**Sintoma:** commits assinados, tags de release sem assinatura.
**Por que persiste:** todo tutorial mostra `commit.gpgsign` e para por aí.
**Correção:** `git config --global tag.gpgSign true`. A tag é o que as pessoas baixam.

### A8. `pinentry` errado no macOS

**Sintoma:** o `git commit` trava ou falha sem explicação.
**Correção:** `brew install pinentry-mac`, registre em `~/.gnupg/gpg-agent.conf`, e
`gpgconf --kill gpg-agent`.

### A9. Dois `gpg` no Windows

**Sintoma:** a chave existe no Kleopatra e o Git jura que não.
**Correção:** `where.exe gpg` e depois `git config --global gpg.program "<caminho certo>"`.
Ou, melhor, use WSL2.

### A10. `key::` numa versão de Git que não suporta

**Sintoma:** `error: Couldn't load public key key::ssh-ed25519 ...: No such file or directory?`
**Por que persiste:** a documentação do 1Password e vários blogs mostram a sintaxe sem dizer
que ela exige **Git ≥ 2.35**, e o Ubuntu 22.04 entrega 2.34.1.
**Correção:** atualize o Git, ou escreva a pública num arquivo e aponte para ele.

### A11. `fetch-depth` padrão no workflow de verificação

**Sintoma:** o teste passa sempre, inclusive quando deveria reprovar.
**Por que persiste:** é uma falha **silenciosa** — ninguém investiga um teste verde.
**Correção:** `fetch-depth: 0` no `actions/checkout`.

### A12. Chave GPG vencida

**Sintoma:** `error: gpg failed to sign the data` de um dia para o outro, sem nada ter mudado.
**Por que persiste:** ninguém agenda o vencimento de dois anos atrás.
**Correção:** `gpg --quick-set-expire <FPR> 2y '*'` e **reenvie a pública ao GitHub**.

---

## B · Erros de entendimento

### B1. Confundir `-s` com `-S`

`-s` é `--signoff`: uma linha de texto (DCO), sem nenhuma criptografia, forjável por qualquer
um. `-S` é assinatura. Tratar DCO como prova de autoria é o erro conceitual mais grave do
assunto.

### B2. Achar que `[G]` local prova autoria

Não prova. O Git busca a chave no seu `allowed_signers` e devolve **o rótulo que você mesmo
deu** àquela chave — inclusive se o rótulo for o nome de outra pessoa. Demonstrado no ato 9 do
[projeto-modelo](07-projeto-modelo/).

### B3. Achar que assinatura torna o commit secreto

Assinar não cifra. O conteúdo continua público. Assinatura acrescenta **procedência**.

### B4. Achar que `git log --show-signature` serve como teste

Ele sai com código 0 mesmo com assinatura ruim. Para automação, use `git verify-commit` ou
leia `%G?`.

### B5. Achar que rebase "apaga" assinaturas

Rebase **cria commits novos**. O original continua assinado e válido — apenas saiu do ramo.
Com `commit.gpgsign true`, os novos são assinados por você, agora, com a sua chave.

### B6. Esperar que revogar invalide o passado no GitHub

Não invalida. O veredito é gravado no momento da verificação e não retroage
([15 § 3](15-verificacao-no-github.md)). É, na minha opinião, a limitação mais séria do
modelo — e a menos divulgada.

### B7. Achar que `merge.verifySignatures` verifica o ramo inteiro

Verifica apenas a **ponta**. Um ramo de 10 commits com só o último assinado passa.

### B8. Achar que o e-mail no `allowed_signers` é validado

Não é. É um rótulo livre, e o Git nem o compara com o autor do commit.

### B9. Achar que chave SSH expira

Não expira. Chave SSH não tem validade embutida — a validade vive no `allowed_signers`, e vale
só para quem tem aquele arquivo.

---

## C · Más práticas

### C1. Chave sem frase secreta

"É só um notebook pessoal." Um arquivo sem frase secreta é copiável por qualquer processo seu,
por qualquer backup mal configurado e por qualquer pacote malicioso. Custo de pôr uma: cinco
segundos, uma vez.

### C2. A mesma chave em cinco máquinas

**Por que persiste:** parece mais simples que gerar cinco.
**Por que é ruim:** perder uma máquina obriga a rotacionar tudo, em todo lugar. Uma chave por
máquina isola o estrago. Todas cadastradas na mesma conta, todas no `allowed_signers`.

### C3. Chave sem backup, e sem certificado de revogação guardado

Chave GPG perdida sem certificado de revogação é uma chave que continua válida no mundo e que
você não pode desativar. O backup são quatro arquivos ([13 § 6](13-gpg-a-fundo.md)).

### C4. Apagar a linha do `allowed_signers` quando alguém sai

Isso transforma em `U` todo o histórico assinado por aquela pessoa. Use
`valid-before="<data de saída>"`.

### C5. Re-assinar o histórico antigo

Além de quebrar hashes, referências e clones, cria evidência criptográfica **falsa**: você
estaria afirmando ter assinado em 2019 algo que assinou hoje. Trace uma linha e assine uma tag
no marco.

### C6. Ligar o ruleset direto em `active`

Sempre passe por `evaluate` primeiro. Cada falha registrada é uma conversa que você não vai
ter com a equipe travada.

### C7. `--no-verify` como hábito

Um `--no-verify` ocasional é razoável. Um alias com `--no-verify` embutido significa que o
hook está atrapalhando e precisa ser corrigido ou removido — não contornado em silêncio.

### C8. Chave de bot num secret que nunca é rotacionado

E o e-mail do bot que ninguém verificou. É a origem de metade dos problemas de automação
neste assunto ([17](17-automacao-e-ci.md)).

### C9. Guardar backup da chave no mesmo lugar que tudo o resto

Backup no mesmo disco, no mesmo serviço de nuvem ou num repositório privado. Repositório
privado hoje é repositório público em algum incidente futuro.

---

## D · Mitos

### D1. "Assinar commits protege contra código malicioso"

**Não.** Os commits do backdoor do **xz-utils** estavam legitimamente assinados. Assinatura
resolve **atribuição**, não intenção nem qualidade. Contra código malicioso: revisão, análise
e diversidade de mantenedores.

### D2. "GPG é mais seguro que SSH"

A criptografia é a mesma (Ed25519 dos dois lados). O que difere é a **gestão** da chave:
subchaves, expiração e revogação formal. Se você não usa subchave com primária offline, "mais
seguro" aqui significa "mais complicado".

### D3. "O selo verde prova que a pessoa escreveu o código"

Prova que a chave foi usada. Se a máquina foi comprometida ou a chave roubada, o selo aparece
igual.

### D4. "Preciso publicar minha chave num servidor de chaves"

Não precisa. Para o GitHub, o que importa é a chave cadastrada na conta. No método SSH, não
existe servidor de chaves.

### D5. "Se eu perder a chave, perco meus commits"

Não. Os commits continuam lá e continuam `Verified` no GitHub. Você perde a capacidade de
assinar **novos** commits com aquela chave.

### D6. "Assinatura deixa o repositório pesado"

Uma assinatura SSH tem **173 bytes** (medido). Dez mil commits assinados somam ~1,7 MB.

---

## Referência rápida de diagnóstico

| Sintoma | Primeiro lugar a olhar |
|---|---|
| `Unverified` no GitHub, `G` local | tipo da chave (*signing*?) e e-mail verificado |
| `gpg failed to sign the data` | `echo teste \| gpg --clearsign` para ver o erro real |
| funciona no terminal, não no editor | variáveis de ambiente do aplicativo gráfico |
| `%G?` = `U` | `allowed_signers`: chave presente? datas cobrem? |
| `%G?` = `B` | **pare e investigue** — não acontece por acaso |
| parou de funcionar do nada | validade da chave GPG |
| funciona num repo e não em outro | `git config --list --show-origin` |
| o teste de CI nunca reprova | `fetch-depth` |

---

## Autoteste

1. Qual erro de configuração não produz mensagem de erro nenhuma?
2. Por que `git log --show-signature` não serve para CI?
3. Por que não se deve apagar a linha do `allowed_signers` de quem saiu?
4. Qual mito o caso xz-utils desmente?
5. Por que "GPG é mais seguro que SSH" é impreciso?
6. Você vê `%G?` = `B` num repositório. O que isso significa, e o que fazer?
7. Por que re-assinar o histórico antigo é eticamente problemático?

*(Respostas: 1 — cadastrar a chave SSH como *authentication* em vez de *signing*. 2 — sai com
código 0 mesmo com assinatura ruim. 3 — invalida o passado, transformando em `U` tudo que a
pessoa assinou. 4 — que assinar protege contra código malicioso. 5 — a criptografia é
equivalente; o que difere é a gestão de chave, e ela só rende vantagem com primária offline.
6 — o conteúdo não confere com a assinatura; investigue, porque não acontece por acidente.
7 — cria evidência criptográfica falsa de que você assinou no passado.)*

---

**Próximo:** [80-custos-e-licencas.md](80-custos-e-licencas.md).
