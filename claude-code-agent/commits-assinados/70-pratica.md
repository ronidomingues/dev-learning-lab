# 70 · Prática — 12 laboratórios

> Nível: iniciante → avançado · Atualizado em 13/08/2026

Exercícios progressivos, com objetivo, roteiro e critério de conclusão. Os que exigem conta
no GitHub estão marcados com 🔑; os demais rodam offline, em pasta descartável.

**Regra de higiene para todos:** faça em `$(mktemp -d)`, com `GNUPGHOME` próprio. Nada aqui
deve tocar o seu `~/.gnupg`, `~/.ssh` ou `~/.gitconfig`. O
[projeto-modelo](07-projeto-modelo/) mostra o padrão de isolamento.

```bash
LAB=$(mktemp -d /tmp/lab.XXXX)
export GNUPGHOME="$LAB/gnupg"; mkdir -p "$GNUPGHOME"; chmod 700 "$GNUPGHOME"
cd "$LAB"
```

---

## Lab 1 · Forjar um commit no nome de outra pessoa

**Nível:** trivial · **Tempo:** 3 min · **Objetivo:** sentir o problema antes da solução.

1. Crie um repositório novo.
2. Configure `user.name` e `user.email` com o nome de alguém famoso.
3. Faça um commit e veja o `git log`.
4. Agora configure assinatura e repita.
5. Rode `git log --format='%h %G? %an'` e compare as duas linhas.

**Concluído quando:** você tiver, no mesmo histórico, um commit `[N]` no nome de outra pessoa
e um `[G]` no seu.

**A pergunta para levar:** o que exatamente mudou entre os dois commits — e o que **não**
mudou?

---

## Lab 2 · O ciclo completo, à mão

**Nível:** fácil · **Tempo:** 15 min · **Objetivo:** fazer sem copiar do `04`.

Sem consultar o [04-como-comecar.md](04-como-comecar.md), execute: gerar chave → configurar
`gpg.format`, `user.signingkey` e `commit.gpgsign` → montar `allowed_signers` → commitar →
verificar.

**Concluído quando:** `git log --format='%h %G? %GS' -1` devolver `G` e o seu e-mail.

**Se travar:** confira nesta ordem — `gpg.format`, o caminho apontar para o `.pub`,
`commit.gpgsign`, `gpg.ssh.allowedSignersFile`.

---

## Lab 3 · Provocar cada código de `%G?`

**Nível:** médio · **Tempo:** 30 min · **Objetivo:** conhecer os estados de falha.

Produza, num mesmo repositório, commits com os seguintes status:

| Status | Como provocar |
|---|---|
| `G` | o caso normal |
| `N` | `git commit --no-gpg-sign` |
| `U` | remova a chave do `allowed_signers`, ou desconfigure o arquivo |
| `B` | reescreva o objeto commit com `git cat-file` + `sed` + `git hash-object -w` |
| `Y` | crie uma chave GPG com `--quick-generate-key ... seconds=90`, assine, espere passar |
| `R` | importe o certificado de revogação (lembre-se do `sed 's/^://'`) |

**Concluído quando:** você tiver visto os seis com os próprios olhos e souber explicar a
diferença entre `B`, `U` e `Y`.

**Dica para o `Y`:** o teste deste curso usou uma chave com validade de 90 segundos. Assine
imediatamente, vá fazer outra coisa, volte e verifique.

---

## Lab 4 · A armadilha do `allowed_signers`

**Nível:** médio · **Tempo:** 10 min · **Objetivo:** internalizar o limite da verificação
local.

1. Assine um commit como você mesmo.
2. Edite o `allowed_signers` trocando o principal pelo e-mail de outra pessoa.
3. Rode `git log --format='%h [%G?] autor=%ae assinante=%GS' -1`.

**Concluído quando:** você conseguir explicar, para alguém que não leu o curso, por que o
status continua `G`.

**Extensão:** escreva um script que reprove commits em que `%ae` ≠ `%GS`
([14 § 2](14-ssh-signing-a-fundo.md) tem o esqueleto).

---

## Lab 5 · Validade por data

**Nível:** médio · **Tempo:** 15 min

1. Assine um commit hoje.
2. Ponha `valid-before="20250101"` na linha do `allowed_signers`. Verifique.
3. Troque para `valid-after="20990101"`. Verifique.
4. Leia com atenção as duas mensagens de erro.

**Concluído quando:** você souber responder: `valid-before` é comparado com a data do
**commit** ou com a data da **verificação**? E que consequência isso tem para auditoria
retroativa?

---

## Lab 6 · Ciclo de vida de uma chave GPG 🔑 (parcial)

**Nível:** médio · **Tempo:** 40 min

1. Gere uma chave com validade de 1 dia.
2. Faça o backup completo (privada, pública, ownertrust, certificado de revogação).
3. Adicione uma subchave só de assinatura.
4. Configure o Git para usar **a subchave** (com o `!` no fim do ID).
5. Renove a validade da primária e de todas as subchaves.
6. Exporte só as subchaves, apague tudo do chaveiro, reimporte, e confirme o `sec#`.
7. Revogue a subchave.

**Concluído quando:** `gpg --list-secret-keys` mostrar `sec#` (primária ausente) e o commit
continuar sendo assinado normalmente pela subchave.

---

## Lab 7 · Reconstruir o payload e verificar sem o Git

**Nível:** avançado · **Tempo:** 30 min · **Objetivo:** eliminar a última caixa-preta.

Reproduza o que está em [12 § 3](12-anatomia-do-commit.md): extraia a assinatura, reconstrua
o objeto sem o campo `gpgsig` e verifique com `ssh-keygen -Y verify` puro.

**Concluído quando:** aparecer `Good "git" signature ...` sem que o Git tenha participado da
verificação.

**Extensão (difícil):** faça o mesmo para uma **tag** assinada. O formato é diferente — a
assinatura vai no fim e não é recuada. Descubra qual é o payload exato.

---

## Lab 8 · Decodificar o blob SSHSIG

**Nível:** avançado · **Tempo:** 30 min

Escreva um script (Python, ou o que preferir) que leia um commit assinado por SSH, decodifique
o base64 e imprima cada campo da estrutura: magic, versão, chave pública, namespace,
reservado, algoritmo de hash, assinatura.

**Concluído quando:** a soma dos campos bater exatamente com o tamanho total do blob.

**Referência:** `PROTOCOL.sshsig`, no código-fonte do OpenSSH. A saída esperada está em
[14 § 1](14-ssh-signing-a-fundo.md).

---

## Lab 9 · Porta de qualidade

**Nível:** médio · **Tempo:** 30 min

Escreva do zero um script que:

- receba um intervalo (`base..head`);
- reprove com código 1 se houver commit sem assinatura válida;
- aceite `[U]` por variável de ambiente;
- ignore merges por variável de ambiente;
- imprima um relatório legível.

**Concluído quando:** ele reprovar corretamente no repositório do
[projeto-modelo](07-projeto-modelo/) (que tem um commit não assinado de propósito) e passar
num histórico limpo.

Depois compare com
[`auditar-historico.sh`](07-projeto-modelo/bin/auditar-historico.sh) e veja o que você deixou
passar.

---

## Lab 10 · Do zero ao `Verified` 🔑

**Nível:** fácil · **Tempo:** 20 min

Num repositório **público e descartável** da sua conta: configure, commite, envie e confirme o
selo. Depois:

1. Consulte o veredito pela API: `gh api repos/{owner}/{repo}/commits/{sha} --jq '.commit.verification'`.
2. **Quebre de propósito:** remova a chave da conta e crie outro commit. Qual `reason` aparece?
3. Recadastre a chave como *Authentication key* (não *Signing*). Qual `reason` agora?

**Concluído quando:** você tiver visto `valid`, `unknown_key` e `not_signing_key` na prática.

---

## Lab 11 · Implantação numa equipe (simulada) 🔑

**Nível:** avançado · **Tempo:** 1–2 h

Num repositório de teste com pelo menos duas contas (a sua e uma segunda, ou um colega):

1. Meça o estado atual pela API.
2. Crie um ruleset em modo `evaluate` exigindo assinatura.
3. Envie um commit **sem** assinatura e veja o registro em `rule-suites`.
4. Passe para `active` e repita — o push deve ser **rejeitado**.
5. Tente *Rebase and merge* num PR. O que acontece?
6. Configure um bot que commite pela API e confirme que ele passa.

**Concluído quando:** você conseguir descrever exatamente o que a equipe veria em cada passo.

---

## Lab 12 · Simulação de incidente

**Nível:** avançado · **Tempo:** 1 h · **Objetivo:** exercitar o raciocínio de investigação.

Cenário: um token com escopo de escrita vazou e ficou exposto por 40 horas. O repositório
exige assinatura.

Produza um relatório de uma página respondendo:

1. Quais commits entraram na janela, e qual o veredito de cada um?
2. O que a assinatura permite **concluir** com segurança?
3. O que ela **não** cobre? (mínimo: três itens)
4. Que evidência independente é necessária para sustentar a conclusão?
5. Qual seria o plano de resposta, em ordem?

**Concluído quando:** o seu relatório contiver ao menos um limite que o
[06 § 14](06-exemplos.md) menciona **e** um que ele não menciona.

---

## Roteiro sugerido

| Se você quer | Faça |
|---|---|
| só configurar e seguir a vida | 1, 2, 10 |
| entender os estados de falha | 1, 2, 3, 4, 5 |
| entender por dentro | 7, 8, mais o [12](12-anatomia-do-commit.md) |
| implantar numa equipe | 9, 10, 11, 12 |
| tudo | na ordem |

---

## Autoteste

1. Por que todo laboratório deve rodar com `GNUPGHOME` próprio?
2. Qual laboratório demonstra o limite mais importante da verificação local?
3. Como produzir um `[Y]` sem esperar dois anos?
4. Por que o Lab 7 é a última caixa-preta a abrir?
5. Qual é o erro que o Lab 9 provavelmente vai revelar no seu script?

*(Respostas: 1 — para não contaminar nem destruir o seu chaveiro real. 2 — o Lab 4: o Git não
compara assinante com autor. 3 — gerando a chave com validade em segundos, com
`--quick-generate-key ... seconds=90`. 4 — porque ele verifica a assinatura sem o Git,
mostrando exatamente qual byte foi assinado. 5 — usar `git log --show-signature` como teste,
que sai com código 0 mesmo com assinatura ruim; ou esquecer o caso de merge.)*

---

**Próximo:** [75-armadilhas.md](75-armadilhas.md).
