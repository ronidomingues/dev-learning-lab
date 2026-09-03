# 85 · Cursos gratuitos e certificações

> Nível: todos · **Pesquisado na web em 13/08/2026** · Links podem expirar; a data de
> publicação de cada item está indicada quando conhecida

---

## Aviso honesto, antes da lista

**Não existe curso completo sobre assinatura de commits, em nenhum idioma.** O assunto é
tratado como uma seção de meia hora dentro de cursos de Git, ou como artigo de blog. Isso não
é acidente: o "como fazer" cabe em quinze minutos, e o "por que" — modelo de confiança,
limites, política de equipe — quase ninguém ensina.

Consequência prática: a melhor fonte sobre *como configurar* é a documentação oficial do
GitHub; a melhor sobre *como funciona* é o livro Pro Git; e a melhor sobre *o que isso resolve
de verdade* são os cursos de segurança de cadeia de suprimentos da Linux Foundation. Este
curso que você está lendo foi escrito porque esse material não existia reunido.

Segunda advertência: **não há certificação específica de assinatura de commits**, e não vai
haver. O assunto aparece como um item dentro de certificações maiores (§ 4).

---

## 1. Português 🇧🇷🇵🇹

### Vídeo, gratuito

| Título | Autor/canal | Plataforma | Duração | Nível | Ano | Vale? |
|---|---|---|---|---|---|---|
| **[Assinando Commits com Chave SSH — GitHub Mão na Massa](https://www.youtube.com/watch?v=WD92Tg3fobc)** | GitHub Mão na Massa | YouTube | curto | iniciante | ~2023 | **Sim.** É o material em português que trata do método **SSH**, que é o recomendado hoje. Direto ao ponto |
| **[Como assinar commits utilizando chaves GPG — Bitbucket e Github](https://www.youtube.com/watch?v=_oDXUonvCI0)** | canal independente | YouTube | curto | iniciante | ~2022 | Sim, para a trilha GPG. Cobre também Bitbucket, o que é raro |
| [Curso de Git e GitHub](https://www.youtube.com/@CursoemVideo) | Curso em Vídeo (Gustavo Guanabara) | YouTube | ~10 h (curso todo) | iniciante | 2019–2021 | Como base de **Git**, é o melhor material gratuito em português que existe. **Não cobre assinatura** — use para o pré-requisito |

### Texto, gratuito

| Recurso | Por que vale |
|---|---|
| **[Pro Git — 7.4 Assinando seu trabalho](https://git-scm.com/book/pt-br/v2/Ferramentas-do-Git-Assinando-seu-trabalho)** | o livro oficial do Git, **traduzido para português e legalmente gratuito**. A tradução é boa; alguns capítulos ficam atrás da edição em inglês |
| **[GitHub Docs em português](https://docs.github.com/pt/authentication/managing-commit-signature-verification)** | tradução oficial e mantida. É a fonte primária para o "como" |
| [Criando chaves SSH e GPG para o GitHub](https://vndmtrx.github.io/posts/ssh-gpg-github/) | artigo de blog em português cobrindo os dois métodos |

**Veredito para quem lê português:** assista ao vídeo de SSH, use a documentação oficial
traduzida como referência, e siga o Bloco B **deste curso** para a parte conceitual, que não
existe em português em lugar nenhum.

---

## 2. Inglês 🇬🇧

### Texto — as melhores fontes, e são melhores que os vídeos

| Recurso | Ano | Nível | Por que vale |
|---|---|---|---|
| **[GitHub Docs — Managing commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification)** | atualizado continuamente | iniciante | **a fonte primária.** É a única que reflete o comportamento real do selo |
| **[Pro Git — 7.4 Signing Your Work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)** | 2ª ed., atualizada | intermediário | explica o mecanismo, não só o comando. Gratuito |
| **[`PROTOCOL.sshsig`](https://github.com/openssh/openssh-portable/blob/master/PROTOCOL.sshsig)** | — | avançado | **a especificação do formato SSHSIG**, em duas páginas. Leitura obrigatória para quem quer entender por dentro |
| [Signing Git Commits with GPG and SSH — manuel laggner](https://www.laggner.info/posts/sign-git-commits-with-gpg-ssh/) | atualizado em abr/2026 | iniciante | um dos poucos que compara os dois métodos com prós e contras, e cobre os três sistemas operacionais |
| [Git: the complete guide to sign your commits with an SSH key — DEV](https://dev.to/ccoveille/git-the-complete-guide-to-sign-your-commits-with-an-ssh-key-35bg) | 2023+ | iniciante | bom passo a passo de SSH |
| [Ditching GPG by signing commits with SSH keys](https://tobywf.com/2026/01/ditch-gnupg-signing-commits-with-ssh/) | jan/2026 | intermediário | argumento atual e bem escrito a favor do SSH |

### Vídeo, gratuito

| Título | Plataforma | Nível | Observação |
|---|---|---|---|
| [Creating and Using GPG Keys for GitHub Signed Commits](https://www.youtube.com/watch?v=tXM77BpgeiA) | YouTube | iniciante | curto e funcional, para a trilha GPG |
| [Source Control Tip 19: Signing a commit via GPG](https://www.youtube.com/watch?v=2ISu2KTPzuQ) | YouTube | iniciante | dica curta, série de controle de versão |

**Opinião:** neste assunto específico, **os vídeos valem menos que o texto**. São todos do
mesmo formato — "digite estes seis comandos" — e nenhum trata do que importa: por que o selo
não aparece, o que ele prova, e como implantar numa equipe. Use vídeo se você prefere ver
alguém digitando; use os textos acima para tudo o mais.

### Onde o assunto é ensinado com profundidade (dentro de cursos maiores)

| Curso | Instituição | Custo | Onde o assunto aparece |
|---|---|---|---|
| **[Securing Your Software Supply Chain with Sigstore (LFS182)](https://training.linuxfoundation.org/training/securing-your-software-supply-chain-with-sigstore-lfs182/)** | Linux Foundation / OpenSSF | **gratuito** | assinatura sem chave, Fulcio, Rekor, Cosign, Policy Controller. **É o melhor curso gratuito relacionado ao tema** |
| **[Automating Supply Chain Security: SBOMs and Signatures (LFEL1007)](https://training.linuxfoundation.org/express-learning/automating-supply-chain-security-sboms-and-signatures-lfel1007/)** | Linux Foundation | gratuito (express) | atestações, verificação de integridade, assinatura de containers, SBOM |
| [Developing Secure Software (LFD121)](https://training.linuxfoundation.org/training/developing-secure-software-lfd121/) | Linux Foundation / OpenSSF | gratuito | segurança de desenvolvimento em geral; a cadeia de suprimentos entra num módulo |
| [GitHub Skills](https://skills.github.com/) | GitHub | gratuito | exercícios práticos de Git/GitHub; útil para o pré-requisito |

---

## 3. Francês 🇫🇷

| Recurso | Tipo | Nível | Por que vale |
|---|---|---|---|
| **[Pro Git — 7.4 Signer votre travail](https://git-scm.com/book/fr/v2/Utilitaires-Git-Signer-votre-travail)** | livro, gratuito | intermediário | a tradução francesa do Pro Git é **completa e bem cuidada** — a melhor tradução do livro depois da original |
| [Clés GPG et Git : sécurise tes commits en 5 minutes](https://formationgit.fr/blog/cles-gpg-et-git-securise-tes-commits-en-5-minutes-chrono) | artigo | iniciante | passo a passo para macOS, Linux e Windows |
| [Signer ses commits Git avec PGP — Garbage Collector](https://zedas.fr/posts/signer-ses-commits-avec-git-et-pgp/) | artigo | intermediário | cobre também Gitea, além do GitHub |
| [Signer ses commits Git et transférer son gpg-agent — Wiki Fiat Tux](https://wiki.fiat-tux.fr/books/développement/page/signer-ses-commits-git-et-transférer-son-gpg-agent-sur-un-serveur-distant) | artigo | avançado | **encaminhamento do `gpg-agent` para servidor remoto** — assunto que não achei tratado em português nem, com essa qualidade, em inglês |
| [Sécuriser son repo distant Git](https://gkemayo.developpez.com/tutoriels/git/securite-repo-git/) | tutorial | intermediário | developpez.com, referência francófona antiga e confiável |

**Nota:** não encontrei **vídeo** francófono dedicado ao assunto que valesse a indicação. O
material francês forte aqui é escrito — o que, para este tema, é uma vantagem.

---

## 4. Certificações

### A resposta curta

**Não existe certificação de assinatura de commits, e não deve existir.** O assunto é pequeno
demais para sustentar uma. Quem promete "certificado em commits assinados" está vendendo um
PDF.

### Onde o assunto aparece dentro de certificações reais

| Certificação | Emissor | Custo (13/08/2026) | O assunto aparece? | Valor de mercado |
|---|---|---|---|---|
| **GitHub Foundations** | GitHub | ~US$ 99 | sim, superficialmente (verificação de commits, chaves) | **baixo-médio.** Útil para o primeiro emprego; nenhuma empresa séria contrata por causa dele |
| **GitHub Advanced Security** | GitHub | ~US$ 99 | tangencialmente | médio, em quem já usa GHAS |
| **CompTIA Security+** | CompTIA | ~US$ 404 | sim: PKI, assinatura digital, cadeia de confiança | **alto** como porta de entrada em segurança; muito reconhecido em edital e RH |
| **CKS** (Kubernetes Security Specialist) | CNCF | ~US$ 445 | sim: assinatura de imagem, cadeia de suprimentos | alto, no nicho |
| **CISSP** | ISC² | ~US$ 749 | criptografia e PKI, em nível de gestão | alto, mas exige 5 anos de experiência |

### Certificados gratuitos, e o que eles valem

| Emissor | Certificado | Custo | Valor real |
|---|---|---|---|
| **Linux Foundation Training** (LFS182, LFEL1007, LFD121) | certificado de conclusão | **gratuito** | **simbólico**, e ainda assim o melhor da lista: o conteúdo é sério, e o nome Linux Foundation dá peso num currículo júnior |
| GitHub Skills | conclusão de exercícios | gratuito | simbólico |
| freeCodeCamp | certificações várias | gratuito | simbólico; nenhuma sobre este tema |
| Coursera/edX auditando | — | grátis para assistir, pago para certificar | o certificado paga o selo, não o conhecimento |

**Franqueza sobre certificados de conclusão gratuitos:** eles atestam que você assistiu, não
que você sabe. Valem como sinal de iniciativa num currículo de início de carreira e não valem
nada num de sênior. O que vale, e é o que eu recomendaria mostrar, é **um repositório público
seu com histórico inteiramente assinado, tags assinadas e um workflow de verificação
funcionando**. Isso é verificável por qualquer entrevistador em trinta segundos, e diz mais
que qualquer PDF.

---

## 5. Trilha de estudo sugerida

| Se você tem | Faça |
|---|---|
| **1 hora** | [04-como-comecar.md](04-como-comecar.md) + GitHub Docs |
| **1 dia** | Bloco A deste curso + o vídeo em português + o projeto-modelo |
| **1 semana** | Bloco A + B deste curso + Pro Git cap. 7.4 + `PROTOCOL.sshsig` |
| **1 mês** | tudo acima + LFS182 (Sigstore) + LFEL1007 (SBOM) + os 12 laboratórios do [70](70-pratica.md) |
| **quer certificação** | Security+ (o assunto entra em PKI), e não algo específico de assinatura |

---

## Autoteste

1. Por que não existe curso completo sobre este assunto?
2. Qual é a melhor fonte gratuita sobre o **mecanismo** (não sobre o comando)?
3. Qual curso gratuito trata do assunto com mais profundidade, ainda que indiretamente?
4. Existe certificação de assinatura de commits?
5. O que vale mais que um certificado de conclusão, numa entrevista?
6. Por que, neste tema, o material em texto é melhor que o em vídeo?

*(Respostas: 1 — o "como" cabe em 15 minutos, e o "por que" quase ninguém ensina. 2 — Pro Git
cap. 7.4 e a especificação `PROTOCOL.sshsig`. 3 — LFS182, da Linux Foundation/OpenSSF, sobre
Sigstore. 4 — não, e não deve existir; o assunto aparece dentro de Security+, GitHub
Foundations e CKS. 5 — um repositório público com histórico inteiramente assinado, tags
assinadas e verificação na CI. 6 — os vídeos existentes são todos do formato "digite estes
comandos" e não tratam do modelo de confiança nem dos limites.)*

---

**Fontes consultadas em 13/08/2026:** youtube.com (buscas em PT, EN e FR) · git-scm.com/book
(PT-BR, EN, FR) · docs.github.com/pt e /en · training.linuxfoundation.org (LFS182, LFEL1007,
LFD121) · openssf.org/training · skills.github.com · formationgit.fr · zedas.fr ·
wiki.fiat-tux.fr · gkemayo.developpez.com · laggner.info · tobywf.com.
Preços de certificação são de tabela e variam por região e promoção.

**Próximo:** [90-bibliografia.md](90-bibliografia.md).
