# Projeto-modelo — laboratório de commits assinados

> Nível: iniciante → intermediário · Testado em 13/08/2026

Uma aplicação pequena, mas inteira, do assunto: um **laboratório executável** que monta do
zero um repositório com commits assinados por **SSH e por GPG**, verifica as assinaturas,
e então **quebra a verificação de cinco maneiras diferentes** para você ver cada código de
status com os próprios olhos, em vez de decorar uma tabela.

Não é um trecho de código. É o roteiro inteiro, do par de chaves à porta de qualidade na CI.

---

## Garantia de isolamento — leia antes de rodar

O script **não toca em nada seu**:

| O que você poderia temer | O que o script faz |
|---|---|
| mexer no seu `~/.gnupg` | usa um `GNUPGHOME` próprio, dentro da pasta de trabalho |
| criar chave em `~/.ssh` | grava as chaves na pasta de trabalho |
| alterar seu `~/.gitconfig` | só usa `git config` **local**, dentro do repositório de teste |
| subir algo para o GitHub | não usa rede, em momento algum |
| pedir sua senha | as chaves de brinquedo são geradas sem frase secreta |
| deixar sujeira | apaga a pasta ao sair (a menos que você peça `--manter`) |

As chaves geradas são **descartáveis e sem frase secreta**. Isso é aceitável exatamente
porque elas vivem alguns segundos e nunca vão para lugar nenhum. Em uma chave de verdade,
frase secreta é obrigatória — veja [16-hardware-e-agentes.md](../16-hardware-e-agentes.md).

---

## Pré-requisitos

| Ferramenta | Versão mínima | Por quê |
|---|---|---|
| `git` | **2.34** | é a versão que introduziu `gpg.format ssh` |
| `gpg` | 2.2 | assinatura OpenPGP; qualquer 2.x serve para o laboratório |
| `ssh-keygen` (OpenSSH) | **8.1** | `ssh-keygen -Y sign/verify` (formato SSHSIG) |
| `bash` | 4.x | o script usa arranjos e substituição de processo |

Confira tudo de uma vez:

```bash
git --version && gpg --version | head -1 && ssh -V
```

Se faltar alguma coisa, ou se o seu `git` for anterior a 2.34, siga
[03-instalacao.md](../03-instalacao.md) antes.

---

## Como rodar

```bash
cd 07-projeto-modelo
chmod +x bin/*.sh hooks/pre-commit
./bin/sandbox.sh
```

O laboratório inteiro leva **menos de 5 segundos** e apaga a pasta ao terminar.

Para explorar o repositório depois, mantenha a pasta:

```bash
./bin/sandbox.sh --manter
# ... ele imprime o caminho no fim; entre nele e brinque à vontade:
#   cd /tmp/commits-assinados.XXXXXX/repo
#   GNUPGHOME=/tmp/commits-assinados.XXXXXX/gnupg git log --show-signature
```

Ou escolha onde montar:

```bash
./bin/sandbox.sh --dir ~/lab-assinatura
```

---

## Estrutura de pastas

```
07-projeto-modelo/
├── README.md                       este arquivo
├── bin/
│   ├── sandbox.sh                  o laboratório completo, em 15 atos
│   └── auditar-historico.sh        porta de qualidade: reprova histórico não assinado
├── hooks/
│   └── pre-commit                  impede commit sem assinatura, por esquecimento
├── ci/
│   └── verificar-assinaturas.yml   o mesmo teste, rodando no GitHub Actions
└── allowed_signers.exemplo         o arquivo que liga chaves SSH a pessoas
```

Só `auditar-historico.sh`, `hooks/pre-commit`, `ci/` e `allowed_signers.exemplo` são feitos
para você **levar para os seus projetos de verdade**. O `sandbox.sh` é didático: ele existe
para ser lido e rodado, não para ser copiado para produção.

---

## Os 15 atos, e o que cada um ensina

| Ato | O que acontece | A lição |
|---|---|---|
| 0 | imprime as versões | quase todo problema de assinatura é versão velha |
| 1 | gera chave SSH e chave GPG | os dois caminhos, lado a lado, desde o início |
| 2 | cria o repositório | `user.email` é **texto livre** — daí a necessidade de assinar |
| 3 | primeiro commit assinado por SSH | sem `allowed_signers`, o status é `[U]`, não `[G]` |
| 4 | monta o `allowed_signers` | é ele que transforma `[U]` em `[G]` |
| 5 | commit assinado por GPG no mesmo repo | os dois métodos convivem; muda só `gpg.format` |
| 6 | mostra o objeto commit cru | a assinatura é um campo `gpgsig` dentro do objeto |
| 7 | commit sem assinatura | `[N]` é o padrão do Git, não um erro |
| 8 | **adultera** um commit assinado | `[B]` — um byte muda e a conta não fecha |
| 9 | põe o nome errado no `allowed_signers` | **o Git não confere assinante × autor** |
| 10 | `valid-before` no passado | como aposentar uma chave sem invalidar o passado |
| 11 | tag assinada | quase todo mundo esquece a tag, que é o que mais importa |
| 12 | hook `pre-commit` | conveniência local, não segurança |
| 13 | auditoria do histórico | o teste que você roda na CI |
| 14 | `merge.verifySignatures` | ele só olha a **ponta** do ramo |
| — | resumo com o histórico inteiro | os códigos de `%G?` lado a lado |

O ato mais importante é o **9**, e ele costuma surpreender até quem já assina há anos.

---

## O ato 9, por extenso: o Git não valida quem você diz que é

Depois de assinar um commit como **Ana**, o script reescreve o `allowed_signers` dizendo que
aquela mesma chave pertence a um tal de **Roberto**, de outra empresa. O resultado real:

```
ff2ebb4  [G]  autor=Ana Souza <ana@exemplo.dev>  assinante=roberto@outraempresa.com
```

O Git deu `[G]` — assinatura boa. E apontou como assinante uma pessoa que **não é o autor do
commit**. Isso não é um defeito: é o modelo. A verificação local do Git responde a uma
pergunta só, *"esta assinatura foi feita por uma chave que consta no meu arquivo?"*, e
devolve o rótulo que o **seu próprio arquivo** dá àquela chave. Ela não responde
*"o autor deste commit é quem diz ser?"*.

Quem responde à segunda pergunta é o **GitHub**, porque só ele tem as três peças ao mesmo
tempo: a chave, a conta a que ela pertence, e a lista de e-mails verificados daquela conta.
Detalhe em [15-verificacao-no-github.md](../15-verificacao-no-github.md).

Consequência prática: **um `[G]` na sua máquina não prova autoria.** Prova posse de uma chave
que você mesmo cadastrou como confiável.

---

## As peças que dá para levar para o seu projeto

### `bin/auditar-historico.sh`

Reprova o histórico se houver commit sem assinatura válida. Sai com código 1 — logo, serve
como porta de qualidade em qualquer CI.

```bash
# todo o histórico do repositório atual
./bin/auditar-historico.sh

# só o que veio no PR (o uso normal em CI)
./bin/auditar-historico.sh . origin/main..HEAD

# aceitando [U] — na CI você quase nunca tem o allowed_signers montado
ACEITAR_U=1 IGNORAR_MERGE=1 ./bin/auditar-historico.sh . origin/main..HEAD
```

Saída real do laboratório:

```
  FALHA 6dda04cf3  [N]  commit sem assinatura  (autor: Ana Souza)
  ok    613fdd8cf  [G]  commit assinado com GPG
  ok    b0f4df651  [G]  commit assinado com SSH

  1 de 3 commit(s) sem assinatura válida.
```

**A decisão de projeto que isso ensina:** aceitar `[U]` na CI é um trade-off consciente.
`[U]` significa *"assinatura matematicamente boa, dono desconhecido"*. Na CI, montar um
`allowed_signers` com a chave de todo mundo dá trabalho e envelhece mal; a alternativa
honesta é deixar a verificação de **identidade** com o GitHub (que já a faz no `push`, se
você ligar o ruleset) e usar a CI só para pegar commit **sem assinatura nenhuma**.
Se você aceitar `[U]` sem o ruleset ligado, você não está verificando quase nada — está
apenas exigindo que exista *alguma* assinatura.

### `hooks/pre-commit`

Impede que você commite sem assinar **por esquecimento**. Instale com:

```bash
install -m 755 hooks/pre-commit .git/hooks/pre-commit
```

Ele confere três coisas: `commit.gpgsign` ligado, `user.signingkey` preenchido e — no modo
SSH — que a chave pública existe mesmo no caminho configurado. A checagem da chave privada é
só **aviso**, não erro, porque com 1Password, `ssh-agent` ou YubiKey a privada legitimamente
não está em disco.

Limite honesto, e ele está escrito dentro do próprio hook: `git commit --no-verify` passa por
cima, e `.git/hooks/` não é versionado nem distribuído. **Hook local é ergonomia. Trava é
ruleset no servidor.**

### `ci/verificar-assinaturas.yml`

O mesmo teste no GitHub Actions, com o detalhe que derruba a maioria das tentativas:
`actions/checkout` faz um clone **raso** (`fetch-depth: 1`) por padrão, e aí não existe
histórico para auditar. O arquivo resolve isso.

### `allowed_signers.exemplo`

O formato do arquivo, comentado, com os casos que importam: uma pessoa com duas chaves,
uma chave aposentada com `valid-before`, e o porquê de `namespaces="git"`.

---

## O que este projeto deliberadamente **não** faz

- **Não cadastra nada no GitHub.** Isso exige a sua conta e o seu navegador. O passo a passo
  está em [04-como-comecar.md](../04-como-comecar.md).
- **Não usa frase secreta nem agente.** Seria a única forma realista de deixar o laboratório
  rodando sozinho. O mundo real — `gpg-agent`, `pinentry`, YubiKey, Touch ID — está em
  [16-hardware-e-agentes.md](../16-hardware-e-agentes.md).
- **Não demonstra `[X]` nem `[E]`.** `[X]` (assinatura com prazo próprio) é raríssimo na
  prática e `[E]` é falha de ferramenta. Os outros seis códigos aparecem todos.

---

## Tratamento de erro, configuração e teste

Coisas que projetos reais têm e tutoriais omitem, e que estão aqui de propósito:

- **`trap limpar EXIT`** — a pasta é removida mesmo se o script morrer no meio. E antes de
  remover, `gpgconf --kill all` derruba o `gpg-agent`; sem isso sobra processo apontando para
  uma pasta que não existe mais (uma das causas do erro
  `gpg: can't connect to the agent` em sessões seguintes).
- **Configuração por argumento** — `--manter` e `--dir` mudam o comportamento sem editar o
  script.
- **Um teste de verdade** — o ato 13 não imprime um relatório bonito: ele **falha**, com
  código de saída 1, porque o histórico do laboratório tem um commit sem assinatura de
  propósito. Teste que nunca reprova não é teste.
- **`set -uo pipefail`** — variável não definida vira erro; código de saída de um cano é o do
  comando que falhou. Note que **não** há `-e`: o laboratório precisa continuar rodando
  depois dos comandos que falham de propósito (atos 8, 12 e 14).

---

## Saída completa e verificada

O laboratório foi **executado de ponta a ponta** em 13/08/2026, nesta base:

```
git version 2.34.1
gpg (GnuPG) 2.2.27
OpenSSH_8.9p1 Ubuntu-3ubuntu0.16, OpenSSL 3.0.2 15 Mar 2022
Ubuntu 22.04.5 LTS
```

Todas as saídas citadas neste README e nos demais arquivos do assunto são **reais**, copiadas
dessa execução — inclusive as falhas.

Um aviso de honestidade: `git 2.34.1` é exatamente a **versão mínima** que suporta assinatura
por SSH, e é a que o Ubuntu 22.04 entrega. Duas coisas se comportam diferente em versões
novas, e estão anotadas onde aparecem:

- a sintaxe `user.signingkey "key::ssh-ed25519 AAAA..."` (chave literal, sem arquivo) **só
  existe a partir do Git 2.35** — no 2.34.1 ela falha com
  `error: Couldn't load public key key::ssh-ed25519 ...: No such file or directory?`;
- `gpg.ssh.revocationFile` também é posterior.

A versão atual do Git em 13/08/2026 é a **2.55.0**. Se você puder, use ela.

---

## Autoteste

1. Por que o ato 3 mostra `[U]` e o ato 4, com o mesmo commit, mostra `[G]`?
2. No ato 9, o autor é a Ana e o Git aponta o Roberto como assinante — e mesmo assim o status
   é `[G]`. Isso é um defeito do Git? Justifique.
3. Qual a diferença prática entre apagar uma linha do `allowed_signers` e pôr um
   `valid-before` nela?
4. Por que `hooks/pre-commit` trata a ausência da chave **privada** como aviso e não como erro?
5. Em `auditar-historico.sh`, o que você perde ao ligar `ACEITAR_U=1`?
6. O ato 14 mescla com `merge.verifySignatures=true` e falha. Se o ramo tivesse 10 commits e
   só a ponta estivesse assinada, o merge passaria?
7. Por que o script usa `set -uo pipefail` e **não** `set -e`?

*(Respostas: 1 — o `allowed_signers` é o que liga a chave a uma pessoa; sem ele o Git valida a
matemática mas não sabe de quem é. 2 — não é defeito: o Git responde "esta chave está na minha
lista?", não "o autor é quem diz ser"; o casamento com a identidade é papel do GitHub.
3 — apagar invalida também o passado; `valid-before` mantém válido o que foi assinado antes da
data. 4 — com agente ou hardware a privada legitimamente não está em disco. 5 — você deixa de
exigir que a assinatura seja de alguém conhecido; passa a exigir apenas que exista assinatura.
6 — sim, passaria: `merge.verifySignatures` só olha a ponta. 7 — porque três atos falham de
propósito e o laboratório precisa continuar.)*
