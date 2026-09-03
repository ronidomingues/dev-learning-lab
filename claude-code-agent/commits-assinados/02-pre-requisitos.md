# 2 · Pré-requisitos

> Nível: iniciante · Atualizado em 13/08/2026

O que você precisa **saber**, o que precisa **ter**, quanto tempo isso realmente leva, e o
que fazer se faltar alguma coisa.

---

## 1. Conhecimento

### Indispensável

Sem isto, o material não vai fazer sentido — e, pior, você vai conseguir seguir os comandos
e não vai entender o que quebrou quando quebrar.

| Você precisa saber | Como conferir se sabe | Onde aprender |
|---|---|---|
| **Usar o terminal**: navegar entre pastas, editar um arquivo, ler uma mensagem de erro | você consegue explicar o que `cd ~/projetos && ls -la` faz | [Linux Journey](https://linuxjourney.com/) · [Curso em Vídeo — Linux](https://www.cursoemvideo.com/curso/curso-de-linux/) (PT) |
| **Git no dia a dia**: `clone`, `add`, `commit`, `push`, `log` | você fez pelo menos uns 20 commits na vida | [Pro Git, cap. 1–2](https://git-scm.com/book/pt-br/v2) (grátis, em português) |
| **Ter uma conta no GitHub** e já ter enviado código para ela | você tem pelo menos um repositório seu | — |

### Ajuda muito (mas dá para começar sem)

| Assunto | Por que ajuda | Onde aprender |
|---|---|---|
| **O que é um par de chaves** (pública e privada) | é o modelo mental inteiro | [10-fundamentos.md](10-fundamentos.md) deste curso ensina do zero |
| **Já ter configurado chave SSH** para `git push` | metade do caminho do método SSH já estará andada | [GitHub Docs — chaves SSH](https://docs.github.com/pt/authentication/connecting-to-github-with-ssh) |
| **O que é função de hash** | explica por que um byte alterado quebra a assinatura | [10-fundamentos.md](10-fundamentos.md) |
| **Como o Git guarda objetos** internamente | explica por que rebase destrói assinatura | [12-anatomia-do-commit.md](12-anatomia-do-commit.md) |
| **CI/CD (GitHub Actions)** | necessário só para o [17](17-automacao-e-ci.md) e o [18](18-politica-de-equipe.md) | [docker/85-cursos](../docker/85-cursos-e-certificacoes.md) tem trilhas |

**Não** é pré-requisito: saber criptografia, matemática, teoria dos números, nem ter lido
qualquer coisa sobre PGP antes. O curso constrói isso a partir do zero em
[10-fundamentos.md](10-fundamentos.md).

---

## 2. Ambiente

### Sistema operacional

Qualquer um dos três serve. A ordem de facilidade, por experiência:

| SO | Situação | Observação |
|---|---|---|
| **Linux** | mais simples | tudo vem do gerenciador de pacotes; cuidado com a versão do Git em distros antigas |
| **macOS** | simples, com uma pedra | o `pinentry` padrão não fala com o terminal; precisa do `pinentry-mac` |
| **Windows** | mais peças | **recomendação: use WSL2**. Windows nativo funciona, mas você vai manter dois mundos de chaves |

### Versões mínimas — este é o ponto que mais causa dor

| Ferramenta | Mínimo absoluto | Recomendado (13/08/2026) | Por que o mínimo é esse |
|---|---|---|---|
| **Git** | **2.34** | 2.55.0 | 2.34 (nov/2021) introduziu `gpg.format ssh`. Antes disso, só GPG. |
| **Git**, para `user.signingkey "key::..."` | **2.35** | 2.55.0 | a sintaxe de chave literal só existe a partir da 2.35 |
| **OpenSSH** | **8.1** | 10.5 | 8.1 (out/2019) trouxe `ssh-keygen -Y sign` / `-Y verify` (formato SSHSIG); 8.2 acrescentou `-Y find-principals` |
| **OpenSSH**, para `valid-after`/`valid-before` no `allowed_signers` | **8.5** | 10.5 | opções de validade por data |
| **GnuPG** | 2.2 | **2.5.x** | a série 2.4 saiu de suporte em **30/06/2026** |

Confira tudo de uma vez:

```bash
git --version && ssh -V && gpg --version | head -1
```

```
# esperado (algo assim ou superior):
git version 2.34.1
OpenSSH_8.9p1 Ubuntu-3ubuntu0.16, OpenSSL 3.0.2 15 Mar 2022
gpg (GnuPG) 2.2.27
```

> **Armadilha muito comum.** Ubuntu 22.04 LTS entrega `git 2.34.1` — exatamente o mínimo.
> Debian 12, `2.39`. RHEL 9, `2.43`. Se o seu Git for **anterior a 2.34**, o método SSH
> simplesmente não existe para você, e a mensagem de erro não diz isso com clareza:
> `error: unsupported value for gpg.format: ssh`. O
> [03-instalacao.md](03-instalacao.md) mostra como instalar uma versão nova sem quebrar o
> sistema.

### Hardware

Nenhum requisito relevante. Assinatura Ed25519 é da ordem de microssegundos, e as chaves
ocupam menos de 1 KB. Um Raspberry Pi assina commit sem esforço.

O único item de hardware **opcional** é um token físico (YubiKey ou similar), que guarda a
chave privada de forma que ela não possa ser copiada. Custo e modelos estão em
[80-custos-e-licencas.md](80-custos-e-licencas.md); vale a pena? A discussão honesta está em
[16-hardware-e-agentes.md](16-hardware-e-agentes.md).

### Contas e acessos

| O que | Obrigatório? | Custo | Observação |
|---|---|---|---|
| Conta no GitHub | **sim** | grátis | não pede cartão |
| **E-mail verificado** na conta | **sim** | — | é o requisito que mais gente esquece; sem ele, nada fica `Verified` |
| Plano pago do GitHub | não | — | rulesets exigindo assinatura funcionam em repositório **público** no plano Free |
| Permissão de administrador no repositório | só para o [18](18-politica-de-equipe.md) | — | para configurar o ruleset |

> Confira agora, leva 15 segundos: <https://github.com/settings/emails>. O e-mail que você
> usa em `git config user.email` precisa estar nessa lista **e** com o selo de verificado.
> Se você usa o e-mail privado do GitHub (`12345+usuario@users.noreply.github.com`), ele já
> conta como verificado.

---

## 3. Tempo realista

Números honestos, medidos em gente de verdade — não o "5 minutos!" dos tutoriais.

| Objetivo | Tempo | O que você consegue fazer no fim |
|---|---|---|
| **Primeiro commit `Verified`, via SSH** | **10–20 min** | assinar seus próprios commits, num repositório |
| **Primeiro commit `Verified`, via GPG** | **30–60 min** | idem, e mais 20 min se o `pinentry` brigar |
| **Configuração completa e permanente** (global, tags, expiração anotada, backup da chave) | **2–3 h** | não pensar mais nisso por um ano |
| **Entender de verdade** o Bloco B (o que a assinatura prova, como o GitHub decide) | **8–12 h** | discutir o assunto com propriedade; escolher entre SSH e GPG com argumento |
| **Implantar numa equipe** (ruleset, onboarding, migração do histórico, plano de rotação) | **1–3 semanas** de calendário, ~10 h de trabalho | a equipe inteira assinando sem revolta |
| **Nível pesquisa** (Blocos B final + C + teoria) | **30–50 h** | avaliar criticamente propostas como Sigstore; entender os limites |

Duas observações sobre esses números, das cicatrizes:

- **O que consome tempo não é a criptografia, é o agente.** Gerar chave leva 3 segundos.
  Fazer o `pinentry` aparecer no lugar certo, o `gpg-agent` não morrer, e a senha não ser
  pedida a cada commit — isso é que come a tarde. Está tratado em
  [16-hardware-e-agentes.md](16-hardware-e-agentes.md).
- **A implantação em equipe é um problema social, não técnico.** A parte técnica são 20
  minutos. As três semanas são para lidar com "meus commits pararam de funcionar", com quem
  usa GUI que não assina, e com o bot que quebrou.

---

## 4. Rota de resgate — o que fazer se faltar um pré-requisito

| Falta | Solução rápida (hoje) | Solução certa (esta semana) |
|---|---|---|
| **Git anterior a 2.34** | use o método **GPG**, que funciona em qualquer versão | atualize o Git — [03-instalacao.md § por SO](03-instalacao.md) |
| **Sem terminal / só uso GUI** | commits feitos **pela interface web do GitHub** já vêm assinados por ele | aprenda o mínimo de terminal; ou use um cliente que assine ([05](05-manual-de-uso.md) lista quais) |
| **Não sei o que é chave pública** | siga o [04](04-como-comecar.md) mecanicamente e volte depois | leia [10-fundamentos.md](10-fundamentos.md) — 40 min, resolve de vez |
| **Não posso instalar nada** (máquina corporativa travada) | GitHub **Codespaces** já vem com Git novo; ou assine pela web | peça ao TI; o argumento pronto está em [80](80-custos-e-licencas.md) |
| **Rede corporativa bloqueia servidor de chaves** | irrelevante para o método **SSH** (não usa servidor de chaves) | [03-instalacao.md § rede corporativa](03-instalacao.md) |
| **Nunca usei GitHub** | crie a conta, faça um repositório de teste, envie um arquivo | volte para cá depois; sem isso não há o que verificar |
| **Sem e-mail verificado** | verifique agora em <https://github.com/settings/emails> | — |

---

## 5. Checklist antes de seguir

Marque tudo antes de abrir o [03-instalacao.md](03-instalacao.md):

- [ ] `git --version` responde **2.34 ou maior**
- [ ] `ssh -V` responde **8.1 ou maior** (ideal: 8.5+, pelas opções de validade por data)
- [ ] Tenho conta no GitHub e já enviei código para ela
- [ ] O e-mail de `git config user.email` está verificado na minha conta
- [ ] Sei em que sistema operacional estou e tenho permissão para instalar programas
      (ou li a rota de resgate acima)
- [ ] Entendi que assinar **não** substitui revisão de código

---

## Autoteste

1. Qual a versão mínima do Git para assinar com SSH, e por que exatamente essa?
2. Por que ter o e-mail verificado no GitHub é pré-requisito e não detalhe?
3. Você está num Ubuntu 22.04 com Git 2.34.1. Qual método funciona sem atualizar nada?
4. Qual parte da configuração costuma consumir mais tempo, e por quê?
5. Sua empresa proíbe instalar programas. Cite duas formas de ainda assim ter commits
   assinados.
6. Por que a implantação numa equipe leva semanas se a parte técnica leva 20 minutos?

*(Respostas: 1 — 2.34, porque foi ela que introduziu `gpg.format ssh`. 2 — o GitHub só marca
`Verified` se o e-mail do commit estiver verificado na conta dona da chave. 3 — os dois, mas
sem a sintaxe `key::`, que exige 2.35. 4 — o agente e o `pinentry`: fazer a senha ser pedida
do jeito certo, e não a cada commit. 5 — commits pela interface web do GitHub, que ele assina;
ou GitHub Codespaces. 6 — porque o gargalo é social: gente com fluxo quebrado, clientes
gráficos que não assinam, bots que param.)*

---

**Próximo:** [03-instalacao.md](03-instalacao.md) — instalar tudo, por sistema operacional.
