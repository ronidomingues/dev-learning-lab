# 1 · O que é um commit assinado — para quem nunca ouviu falar

> Nível: iniciante · Sem nenhum jargão · Atualizado em 13/08/2026

---

## O problema, em uma frase

**Qualquer pessoa pode publicar código no seu nome, e ninguém percebe.**

Não é uma falha, não é uma brecha de segurança e não vai ser corrigido. É como o Git foi
projetado, de propósito, em 2005.

---

## A demonstração que convence

Vou pedir uma coisa incômoda: não acredite em mim, faça o teste. Numa pasta qualquer,
descartável:

```bash
mkdir /tmp/teste-identidade && cd /tmp/teste-identidade
git init
git config user.name "Linus Torvalds"
git config user.email "torvalds@linux-foundation.org"
echo "oi" > arquivo.txt
git add arquivo.txt
git commit -m "corrigindo o kernel"
git log
```

E aí está, no seu histórico:

```
commit 3f1a9c...
Author: Linus Torvalds <torvalds@linux-foundation.org>
Date:   Thu Aug 13 12:00:00 2026 -0300

    corrigindo o kernel
```

Você acabou de fazer um commit em nome do criador do Linux. O Git não reclamou, não pediu
senha, não conferiu nada. Se você tiver permissão de escrita em algum repositório e enviar
esse commit, o nome dele vai aparecer lá.

**Por que isso acontece?** Porque `user.name` e `user.email` no Git são apenas *texto que
você digita*. Não são login, não são senha, não são identidade. São o equivalente digital de
escrever um nome no remetente de um envelope: você escreve o que quiser.

Guarde essa frase, porque ela é a chave do assunto inteiro:

> No Git, o campo "autor" é uma etiqueta que o próprio autor escreve.

---

## "Mas eu preciso de senha para enviar para o GitHub..."

Precisa, e é exatamente aí que mora a confusão que quase todo mundo tem.

São duas coisas diferentes, e vale separá-las de uma vez:

| | O que é | O que prova |
|---|---|---|
| **Entrar (autenticação)** | a senha, o token ou a chave SSH que o GitHub te pede para *enviar* código | que **você** tem permissão de escrever naquele repositório |
| **Assinar** | um carimbo criptográfico dentro de cada commit | que **aquele commit específico** foi feito por quem diz ter sido |

A autenticação protege a **porta**. A assinatura protege o **conteúdo**.

E o buraco entre as duas é este: **quem entra pela porta pode carregar qualquer coisa para
dentro.** Se eu tenho acesso de escrita a um repositório de 30 pessoas, posso enviar commits
com o nome de qualquer uma das outras 29. O GitHub vai aceitar, porque a *minha* credencial é
válida — ele só verificou quem abriu a porta, não o nome escrito na caixa.

Pior: se alguém roubar o seu token de acesso (um vazamento, um notebook esquecido, um pacote
malicioso que leu seu `~/.gitconfig`), essa pessoa passa a poder commitar como você — e a
única coisa que a distingue de você é... nada.

---

## A analogia: o envelope e o lacre

Imagine que cada commit é uma carta que entra num arquivo público.

- **Sem assinatura**: você escreve o remetente no envelope. Como qualquer um escreve qualquer
  nome, o remetente é apenas uma sugestão. Se aparecer uma carta desagradável assinada com o
  seu nome, você não tem como provar que não foi você — e quem recebeu não tem como provar
  que foi.

- **Com assinatura**: junto da carta vai um lacre feito com um carimbo que **só você possui**.
  Qualquer pessoa consegue olhar o lacre e conferir que ele veio do seu carimbo. Ninguém
  consegue fabricar um lacre igual sem ter o carimbo na mão.

A analogia é boa em três pontos e é importante saber onde ela quebra:

| Na analogia | Na realidade |
|---|---|
| o carimbo é físico e único | é um arquivo, a **chave privada**, que fica na sua máquina |
| o lacre prova quem carimbou | a assinatura prova **posse da chave**, não quem digitou |
| o lacre quebra se abrirem a carta | qualquer alteração — um byte! — invalida a assinatura |

Esse último ponto é mais forte do que na analogia física: o lacre digital não é um selo por
cima da carta, ele é calculado **a partir do conteúdo inteiro**. Mude uma vírgula na mensagem
do commit, mude um caractere em qualquer arquivo, mude a data — e a conta não fecha mais. O
Git avisa na hora.

E o segundo ponto é a limitação honesta que carregamos pelo resto do curso: a assinatura
prova que **a chave** foi usada. Se alguém roubar a sua chave privada, essa pessoa assina
como você. A assinatura desloca o problema de "qualquer um pode fingir ser você" para
"só quem tiver a sua chave pode fingir ser você" — o que é uma melhora enorme, mas não é
mágica.

---

## O que aparece na prática

Quando funciona, o resultado no GitHub é um selo verde ao lado do commit:

```
✔ Verified      commit assinado, chave conhecida, e-mail confere
```

Quando não funciona:

```
✘ Unverified    tem assinatura, mas o GitHub não conseguiu confirmá-la
(nada)           não tem assinatura nenhuma — o padrão
```

Sim, é um selinho. Mas o selinho é a ponta visível de três coisas concretas:

1. **Você consegue provar autoria.** Em disputa, auditoria, incidente de segurança ou
   processo judicial, "foi ele que commitou" deixa de ser uma alegação e vira uma evidência.
2. **Ninguém consegue plantar código no seu nome.** Se o repositório exigir assinatura, um
   invasor com o token roubado ainda não consegue se passar por você.
3. **O histórico vira detectavelmente imutável.** Se alguém reescrever o passado — e o Git
   permite reescrever o passado —, as assinaturas quebram e a reescrita fica visível.

---

## Por que isso virou assunto agora

Assinar commit é possível desde 2005 e quase ninguém fazia. Três coisas mudaram:

1. **Ataques à cadeia de suprimentos ficaram comuns.** Já não se ataca a empresa: ataca-se a
   biblioteca que a empresa usa. Casos como o backdoor plantado no `xz-utils` (março de 2024),
   descoberto por acaso por causa de meio segundo de lentidão no SSH, mostraram que o elo
   fraco é o commit que entra sem ninguém olhar.
2. **Regulação chegou.** Ordem executiva americana sobre segurança de software (2021),
   o *Cyber Resilience Act* europeu, exigências de SBOM em contrato público. Origem
   verificável de código deixou de ser capricho e virou requisito de compra.
3. **Ficou fácil.** Até 2021, assinar exigia GPG, uma ferramenta com fama merecida de
   hostil. Desde o Git 2.34 (novembro de 2021), dá para assinar com a **mesma chave SSH que
   você já usa** para enviar código. São três linhas de configuração.

Esse terceiro ponto é o que muda o cálculo. A resposta honesta para "vale a pena?" em 2015 era
"depende, dá muito trabalho". Em 2026, é **sim**, e o argumento contrário virou preguiça.

---

## Os dois caminhos, em uma tabela

Você vai escolher entre dois métodos. O curso ensina os dois, e o
[04-como-comecar.md](04-como-comecar.md) mostra os dois lado a lado.

| | **SSH** | **GPG** |
|---|---|---|
| Você já tem a chave? | provavelmente **sim** (a que usa para `git push`) | não |
| Peças para instalar | nenhuma, além do Git | GnuPG + agente + pinentry |
| Tempo até o primeiro commit assinado | ~10 minutos | ~30 minutos |
| A chave expira sozinha? | não (a validade fica num arquivo à parte) | sim, nativamente |
| Dá para revogar? | por lista de revogação, manual | sim, com certificado de revogação |
| Funciona fora do Git (e-mail, arquivos) | pouco | sim, é o padrão do mundo OpenPGP |
| Reputação | simples, moderno | poderoso, e famoso por ser difícil |

**Recomendação profissional** (é opinião, e está fundamentada em
[19-como-escolher.md](19-como-escolher.md)): comece por **SSH**. Se depois você precisar de
expiração automática, revogação formal ou chave em cartão inteligente por exigência da
empresa, migre para GPG — e o curso ensina a migrar sem invalidar o passado.

---

## O que assinar **não** resolve

Prometi honestidade, então aqui está a parte que os tutoriais omitem. Uma assinatura prova
**uma** coisa: que a chave X foi usada para assinar aquele conteúdo. Só isso.

Ela **não** prova que:

- o código é bom, seguro ou foi revisado;
- a pessoa entendeu o que estava enviando;
- a pessoa não estava sendo coagida, ou com a máquina invadida;
- a chave não foi roubada;
- a pessoa é mesmo quem diz ser — isso depende de quem cadastrou a chave e como.

Existe uma expressão para o exagero que se faz aqui: **teatro de segurança**. Uma equipe que
exige assinatura em todo commit e aprova PR sem ler está mais protegida contra falsificação de
autoria e igualmente desprotegida contra código ruim. As duas coisas são necessárias e
resolvem problemas diferentes.

O tratamento formal disso — o que a assinatura prova, e o que é só sensação — está em
[60-teoria-avancada.md](60-teoria-avancada.md). Vale a leitura antes de vender a ideia para a
sua liderança.

---

## Autoteste

1. Por que o Git aceita qualquer nome em `user.name` sem reclamar?
2. Qual a diferença entre a chave SSH que você usa para `git push` e uma chave de assinatura?
3. Se um atacante roubar o seu token do GitHub, ele consegue commitar no seu nome? E se você
   assinar todos os seus commits, o que muda?
4. Uma assinatura válida prova que o código foi revisado? Justifique.
5. Por que a mudança de um único byte no commit invalida a assinatura?
6. Cite duas razões, além do selinho verde, para assinar.
7. Em que situação o GPG ainda é a escolha certa, apesar de mais trabalhoso?

*(Respostas: 1 — são metadados de texto livre; o Git foi feito para funcionar sem servidor
central e sem autenticação. 2 — pode ser fisicamente a mesma chave; muda o uso: uma abre a
porta, a outra carimba o conteúdo. 3 — sim, consegue; assinando, o commit dele sai sem
assinatura válida e um repositório que exija assinatura o rejeita. 4 — não prova nada sobre
qualidade; prova posse da chave. 5 — a assinatura é calculada sobre o conteúdo inteiro do
objeto commit. 6 — provar autoria em auditoria/incidente; tornar detectável a reescrita do
histórico. 7 — quando se precisa de expiração automática, revogação formal, ou quando a
empresa já padronizou OpenPGP / cartão inteligente.)*

---

**Próximo:** [02-pre-requisitos.md](02-pre-requisitos.md) — o que você precisa saber e ter
antes de começar.
