# 11 · História — como chegamos aqui

> Nível: intermediário · Atualizado em 13/08/2026

Quase toda esquisitice deste assunto tem explicação histórica. O campo se chama `gpgsig`
mesmo quando a assinatura é SSH; a chave GPG tem "subchaves" que ninguém entende; o modelo de
confiança do OpenPGP existe e não se usa. Nada disso é arbitrário — é sedimento.

---

## Linha do tempo

```
1976  Diffie & Hellman publicam a ideia de chave pública
1977  RSA
1991  Phil Zimmermann lança o PGP 1.0
1993  Governo dos EUA abre investigação criminal contra Zimmermann
1996  Investigação arquivada, sem denúncia
1997  Nasce o grupo OpenPGP no IETF · Werner Koch começa o GnuPG
1998  RFC 2440 — OpenPGP
1999  GnuPG 1.0
2005  Git (abril) · `git tag -s` desde os primeiros meses
2007  RFC 4880 — a versão do OpenPGP que valeu por 17 anos
2012  `git commit -S` (Git 1.7.9, janeiro)
2014  GitHub passa a exibir o selo de commits verificados por GPG
2017  SHAttered: primeira colisão prática de SHA-1 (fevereiro)
2019  SSHSIG: `ssh-keygen -Y sign` no OpenSSH 8.1 (outubro)
      Rede de servidores de chaves SKS colapsa por envenenamento
2020  SHA-1 is a Shambles: colisão de prefixo escolhido (janeiro)
      Git 2.29: formato de objeto SHA-256, experimental (outubro)
2021  Ordem executiva 14028 (EUA) sobre segurança da cadeia de software (maio)
      Sigstore/cosign (outubro) · Git 2.34: assinatura por SSH (novembro)
2022  GitHub passa a verificar assinaturas SSH (23 de agosto)
2024  RFC 9580 — OpenPGP renovado (julho) · backdoor no xz-utils (março)
2026  GnuPG 2.4 sai de suporte (30/06) · OpenSSH 10.4 traz ML-DSA experimental (julho)
```

---

## 1991–1996: o PGP e o processo criminal

Phil Zimmermann publicou o **PGP** (*Pretty Good Privacy*) em junho de 1991, e o distribuiu
de graça, pela internet incipiente. O contexto era político: tramitava no Senado americano
uma proposta que obrigaria fabricantes a inserir portas dos fundos em produtos de
comunicação.

O problema é que, na legislação americana da época, criptografia forte era classificada como
**munição**, na mesma categoria de armamento pesado, e exportá-la sem licença era crime. O
PGP saiu dos EUA em semanas, porque é o que a internet faz. Em 1993 o governo abriu
investigação criminal contra Zimmermann.

A resposta dele é um dos episódios mais elegantes da história da computação: publicou o
código-fonte completo do PGP **como livro impresso**, pela MIT Press. Livros são protegidos
pela Primeira Emenda; a exportação de um livro não podia ser proibida. Do outro lado do
Atlântico, voluntários escanearam as páginas e recompilaram o código.

A investigação foi arquivada em janeiro de 1996, sem denúncia.

**Por que isso importa para você, hoje.** Duas heranças diretas:

1. **O OpenPGP nasceu como ferramenta de resistência**, não como produto corporativo. Daí o
   modelo descentralizado de confiança, o cuidado obsessivo com metadados e uma interface
   pensada para ativistas — não para desenvolvedores com pressa. A fama de difícil não é
   acidente; é o preço de decisões tomadas para outro público.
2. **A distinção entre "cifrar" e "assinar" ficou embaralhada** na cabeça de todo mundo,
   porque o PGP fazia as duas coisas e foi vendido como ferramenta de privacidade. Até hoje se
   ouve "commit assinado" e se pensa em "commit secreto".

---

## 1997–2007: OpenPGP vira padrão, GnuPG vira a implementação

Para escapar do emaranhado de patentes e licenças do PGP comercial, o IETF padronizou o
formato: **RFC 2440** (1998), depois **RFC 4880** (2007), que reinou por dezessete anos.

Em paralelo, o alemão **Werner Koch** escreveu o **GnuPG**, implementação livre e limpa do
padrão. Vale saber, porque explica muita coisa sobre o estado da ferramenta: por quase duas
décadas o GnuPG foi mantido essencialmente por uma pessoa, com financiamento precário. Em
2015, uma reportagem da ProPublica sobre a situação financeira do projeto provocou uma onda
de doações e patrocínios (Facebook, Stripe, o governo alemão). Antes disso, o software que
cifra boa parte da comunicação sensível do planeta era sustentado por um desenvolvedor quase
falindo.

**Herança prática.** A interface do GnuPG é o que é — inconsistente, com opções que se
contradizem, mensagens de erro herméticas — porque foi acumulada por décadas sob restrição
severa de recursos, com compatibilidade retroativa como prioridade máxima. Não é desleixo. É
o resultado previsível daquelas condições.

---

## 2005: o Git nasce sem identidade, de propósito

Em abril de 2005, a licença do BitKeeper deixou de ser gratuita para o kernel Linux, e Linus
Torvalds escreveu o Git em poucas semanas. As decisões de projeto refletem o problema que ele
tinha: milhares de colaboradores, sem hierarquia de contas, sem servidor central.

Daí a decisão que gera este curso inteiro: **`user.name` e `user.email` são texto livre**.
Num sistema distribuído, não há autoridade que pudesse validá-los.

Mas a preocupação com integridade estava lá desde o início, em outro lugar: **todo objeto é
endereçado pelo seu próprio hash**. Isso não impede falsificação de autoria, mas torna
impossível alterar o passado sem mudar todos os hashes seguintes. É um mecanismo de
*integridade*, não de *autenticidade* — e essa distinção é o buraco que a assinatura preenche.

`git tag -s` (tag assinada) existe praticamente desde o começo, porque o caso de uso urgente
era outro: **provar que uma release é a release**. Assinar cada commit só veio em janeiro de
2012, no Git 1.7.9 (`git commit -S`) — sete anos depois.

---

## 2014–2017: o GitHub entra, e a rede de confiança sai

O GitHub passou a exibir o selo de verificação de commits GPG em 2014. Esse foi o momento em
que a **vinculação de identidade mudou de dono**, silenciosamente: em vez da rede de
confiança do OpenPGP, passou a valer "esta chave está cadastrada nesta conta, com este e-mail
verificado". Ninguém anunciou a mudança de modelo, mas foi ela que tornou assinar viável
para o desenvolvedor comum.

Enquanto isso, o modelo original ruía. A rede de servidores **SKS** — que sincronizava chaves
OpenPGP entre si — tinha uma propriedade fatal: aceitava qualquer assinatura de qualquer um
sobre qualquer chave, e **nunca apagava nada** (era projetada como registro imutável). Em
junho de 2019, alguém inundou as chaves de dois desenvolvedores conhecidos com dezenas de
milhares de assinaturas falsas. Baixar aquelas chaves passou a travar o GnuPG. Não havia
conserto possível dentro do desenho, e a rede foi efetivamente abandonada.

Foi o atestado de óbito da rede de confiança como prática viva.

---

## 2017–2020: o SHA-1 cai

Em fevereiro de 2017, Google e CWI Amsterdam publicaram o **SHAttered**: dois PDFs diferentes
com o mesmo hash SHA-1. Custo estimado, à época: cerca de 6.500 anos-CPU, ou algo em torno de
US$ 110 mil em nuvem.

Em janeiro de 2020, veio o golpe pior: **"SHA-1 is a Shambles"**, de Leurent e Peyrin,
demonstrou colisão de **prefixo escolhido** — o atacante escolhe os dois começos e ainda assim
consegue colidir. Custo estimado: por volta de US$ 45 mil. Isso é o que torna o ataque
*útil*, e não apenas *possível*.

**O que isso significa para o Git.** O Git usa SHA-1 para nomear objetos. Em teoria, uma
colisão permitiria trocar um objeto por outro mantendo o hash — e, portanto, mantendo a
assinatura válida. Três atenuantes reais, e uma ressalva:

- desde 2017 o Git aplica **detecção de colisão** (a biblioteca `sha1collisiondetection`, de
  Marc Stevens): ele reconhece os padrões dos ataques conhecidos e recusa o objeto;
- fabricar uma colisão que seja **também** código válido, plausível e malicioso é muito mais
  difícil do que colidir dois PDFs;
- o formato de objeto **SHA-256** existe no Git desde a versão 2.29 (outubro de 2020).

A ressalva: SHA-256 no Git segue **pouco adotado** em 2026, porque o GitHub e a maior parte
do ecossistema ainda não o suportam. Ou seja: o problema é conhecido há nove anos, a solução
existe há seis, e a migração praticamente não aconteceu. É um bom exemplo de que segurança
não avança por mérito técnico, mas por custo de coordenação.

---

## 2019–2022: assinar com SSH

Em outubro de 2019, o OpenSSH 8.1 trouxe o **SSHSIG**: `ssh-keygen -Y sign` e `-Y verify`,
um formato de assinatura genérica usando chaves SSH comuns, com **namespaces** para impedir
que uma assinatura feita para um fim seja aceita em outro.

Em novembro de 2021, o **Git 2.34** ganhou `gpg.format ssh` (trabalho de Fabian Stelzer), e
em **23 de agosto de 2022** o GitHub passou a verificar essas assinaturas.

**Por que isso mudou tudo.** Não por ser mais seguro — a criptografia é essencialmente a
mesma. Mudou porque **eliminou a barreira de adoção**: a chave já existe, não há agente
adicional, não há `pinentry`, não há servidor de chaves, não há subchave, não há validade
para renovar. O que era um tutorial de 40 passos virou três linhas de `git config`.

É a lição de sempre em segurança: **o controle que se adota vence o controle que é melhor no
papel**. GPG era tecnicamente mais completo em 2019 e continua sendo em 2026. E perdeu.

---

## 2021–2026: cadeia de suprimentos, regulação e o que vem

Três forças empurraram o assunto do "capricho de quem gosta de criptografia" para "requisito
de contrato":

1. **Ataques reais e de grande alcance.** SolarWinds (dezembro de 2020), `event-stream`,
   Codecov, e sobretudo o **xz-utils** (março de 2024) — um backdoor plantado ao longo de
   **dois anos** por um colaborador que ganhou a confiança do mantenedor por engenharia
   social, e que só foi descoberto porque um engenheiro da Microsoft achou estranho meio
   segundo de lentidão no SSH.
2. **Regulação.** A ordem executiva 14028 (EUA, maio de 2021) exigiu SBOM e proveniência de
   software para fornecedores do governo. O *Cyber Resilience Act* europeu segue a mesma
   direção, com prazos ao longo de 2026–2027.
3. **Ferramentas sem chave.** O **Sigstore** (outubro de 2021) propôs eliminar a chave de
   longa duração: você se autentica com sua identidade OIDC (Google, GitHub), recebe um
   certificado válido por 10 minutos, assina, e o registro vai para um log público de
   transparência (Rekor). O `gitsign` aplica isso a commits.

**Sobre o xz-utils, a nota que dói:** todos os commits do backdoor **estavam assinados**, e
por uma chave legítima do próprio mantenedor. A assinatura funcionou perfeitamente e provou
exatamente o que promete provar — e não impediu nada. É o melhor argumento disponível contra
tratar assinatura como solução de segurança de cadeia de suprimentos, em vez de como o que
ela é: um mecanismo de **atribuição**.

---

## O que ficou como cicatriz no código de hoje

| Esquisitice | Explicação histórica |
|---|---|
| o campo se chama `gpgsig` mesmo para SSH | foi criado em 2012, quando só havia GPG; renomear quebraria repositórios existentes |
| `-S` assina e `-s` faz "signoff" | `--signoff` veio antes (2004, para o DCO do kernel após o processo da SCO) e ficou com a letra minúscula |
| chave GPG tem subchaves | herança do desenho do OpenPGP para separar papéis (assinar, cifrar, autenticar) e permitir rotação sem trocar a identidade |
| `user.signingkey` aponta para a chave **pública** no modo SSH | o SSH sempre identificou chaves pela pública; a privada pode estar num agente ou num token |
| o certificado de revogação vem comentado com `:` | proteção do GnuPG contra você revogar a própria chave por acidente |
| o Git ainda usa SHA-1 por padrão | migrar exige coordenação de todo o ecossistema, e ninguém quer pagar essa conta |
| não existe "expiração" nativa em chave SSH | o SSH nunca teve o conceito; a validade foi enxertada no `allowed_signers` em 2021 |

---

## Autoteste

1. Por que o PGP foi objeto de investigação criminal nos EUA?
2. Como Zimmermann contornou a proibição de exportação?
3. Por que o Git nasceu sem qualquer verificação de identidade?
4. Que evento derrubou a rede de servidores de chaves SKS, e por que não havia conserto?
5. O SHA-1 está quebrado. Por que o Git ainda funciona, e por que a migração para SHA-256 não
   aconteceu?
6. Por que a assinatura por SSH mudou a adoção, se a criptografia é equivalente?
7. O que o caso xz-utils prova sobre os limites da assinatura de commits?
8. Por que o campo se chama `gpgsig` mesmo em assinaturas SSH?

*(Respostas: 1 — criptografia forte era classificada como munição, e exportá-la sem licença
era crime. 2 — publicou o código-fonte como livro impresso, protegido pela Primeira Emenda.
3 — foi projetado como sistema distribuído, sem servidor central que pudesse validar
identidade. 4 — envenenamento por assinaturas falsas; o desenho era de registro imutável que
nunca apagava nada. 5 — o Git aplica detecção de colisão desde 2017 e forjar código malicioso
que colida é muito mais difícil que colidir PDFs; a migração exige coordenação de todo o
ecossistema, que ninguém financiou. 6 — porque eliminou a barreira de adoção: nenhuma peça
nova a instalar ou manter. 7 — que ela prova posse de chave, não boa-fé: os commits maliciosos
estavam legitimamente assinados. 8 — compatibilidade retroativa: o campo é de 2012, quando só
existia GPG.)*

---

**Próximo:** [12-anatomia-do-commit.md](12-anatomia-do-commit.md).
