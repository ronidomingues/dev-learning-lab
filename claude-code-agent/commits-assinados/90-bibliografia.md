# 90 · Bibliografia comentada

> Nível: todos · **Edições e disponibilidade conferidas na web em 13/08/2026**
> 🆓 = **legalmente gratuito** (liberado pelo autor ou pela editora)

Nenhum livro é sobre "assinatura de commits" — o assunto é pequeno demais para um. O que
existe são três prateleiras que o cercam: **Git**, **criptografia aplicada** e **segurança de
cadeia de suprimentos**. Abaixo, o que vale de cada uma, com o nível e a advertência sobre
envelhecimento.

---

## 1. Git — onde o assunto realmente aparece

### 🆓 Pro Git — Scott Chacon e Ben Straub · Apress · 2ª edição, 2014, revisada
continuamente online

**Nível:** iniciante → intermediário.
**A leitura obrigatória deste curso.** O capítulo **7.4 — "Assinando seu trabalho"** é a
melhor explicação gratuita do mecanismo, e o capítulo **10 — "Git Internals"** é o que explica
por que a assinatura muda o hash.

- Gratuito e legal, sob licença Creative Commons: <https://git-scm.com/book>
- **Tem tradução para português (PT-BR), e é boa.** Alguns capítulos ficam atrás da versão em
  inglês; se algo parecer estranho, confira o original.
- Também há tradução **francesa completa e bem cuidada**.
- **Envelheceu?** Em parte: a edição impressa é de 2014 e antecede a assinatura por SSH. A
  versão **online** é atualizada e cobre. Prefira a online, sempre.

### Version Control with Git — Prem Kumar Ponuthorai e Jon Loeliger · O'Reilly · 3ª ed., 2022

**Nível:** intermediário → avançado.
Mais denso e mais mecânico que o Pro Git: entra fundo em objetos, referências e no modelo de
dados. É o complemento certo se o capítulo 10 do Pro Git deixou você com vontade de mais.
Pago. Sem tradução para o português que eu conheça.

---

## 2. Criptografia — para entender o que a assinatura prova

### Serious Cryptography — Jean-Philippe Aumasson · No Starch Press · 2ª ed., outubro de 2024

**Nível:** intermediário.
**A minha primeira recomendação de criptografia para quem programa.** Explica hash,
assinatura, curvas elípticas e aleatoriedade com rigor e sem exigir matemática pesada. A 2ª
edição atualiza o livro e inclui criptografia pós-quântica — o que importa para
[60 § 6](60-teoria-avancada.md).
Pago. Existe tradução para o português da 1ª edição; prefira o original em inglês, que é a
edição atual.

### 🆓 Security Engineering — Ross Anderson · Wiley · 3ª ed., 2020

**Nível:** intermediário → avançado.
Não é um livro de criptografia: é um livro sobre **por que sistemas seguros falham**, e é o
melhor que existe nessa categoria. Os capítulos sobre distribuição de chaves e economia da
segurança são a base do argumento de [60 § 4](60-teoria-avancada.md) e de boa parte da minha
opinião em [65](65-estado-da-arte.md).

- **Todos os capítulos da 3ª edição estão livres para download** no site do autor, por acordo
  com a editora: <https://www.cl.cam.ac.uk/archive/rja14/book.html>
- Ross Anderson faleceu em 2024; a 3ª edição é definitiva.

### Introduction to Modern Cryptography — Jonathan Katz e Yehuda Lindell · CRC Press · 3ª ed., 2020

**Nível:** pesquisa.
O livro-texto padrão. É aqui que EUF-CMA ([60 § 1](60-teoria-avancada.md)) é definido com
rigor e provado. Exige conforto com prova matemática. Pago.

### 🆓 A Graduate Course in Applied Cryptography — Dan Boneh e Victor Shoup

**Nível:** pesquisa.
Rascunho publicado gratuitamente pelos autores em <https://toc.cryptobook.us/> (versão 0.6,
janeiro de 2023). Cobre assinaturas digitais com profundidade e é a referência aberta mais
completa que existe. Por ser rascunho, tem lacunas — e ainda assim é excelente.

### Cryptography Engineering — Niels Ferguson, Bruce Schneier e Tadayoshi Kohno · Wiley · 2010

**Nível:** intermediário.
O foco é **como não errar ao implementar**. Envelheceu em algoritmos (é anterior à
popularização das curvas Edwards e ao pós-quântico), mas o raciocínio sobre modos de falha
continua válido. Pago.

### ⚠️ Applied Cryptography — Bruce Schneier · Wiley · 2ª ed., 1996 (reedição de 2015)

**Nível:** histórico.
**Está datado, e o próprio autor diz isso.** Cite-o para entender a história do campo, não
para tomar decisão técnica. Se você viu esse livro recomendado em algum lugar como leitura
atual, desconfie do lugar.

---

## 3. SSH e OpenPGP

### SSH Mastery: OpenSSH, PuTTY, Tunnels and Keys — Michael W. Lucas · Tilted Windmill Press · 2ª ed.

**Nível:** intermediário.
O melhor livro prático sobre OpenSSH, escrito com humor e sem enrolação. **Ressalva
importante:** a 2ª edição é anterior ao SSHSIG virar assunto corriqueiro, então
`ssh-keygen -Y sign` não é o foco. Vale pelo resto — agente, chaves, encaminhamento. Pago e
barato.

### ⚠️ PGP & GPG: Email for the Practical Paranoid — Michael W. Lucas · No Starch Press · 2006

**Nível:** iniciante.
**Datado.** É de 2006, anterior ao GnuPG 2, aos servidores de chaves modernos e ao colapso da
rede de confiança. Interessante como documento histórico do modelo que não vingou
([11](11-historia.md)). Não use como manual.

**Para OpenPGP atual, não há livro — há a RFC 9580 e o manual do GnuPG.** Os dois estão em
[95-referencias.md](95-referencias.md).

---

## 4. Cadeia de suprimentos e segurança de desenvolvimento

### 🆓 Building Secure and Reliable Systems — Google · O'Reilly · 2020

**Nível:** intermediário → avançado.
Liberado gratuitamente pelo Google em <https://sre.google/books/building-secure-reliable-systems/>.
Os capítulos sobre proveniência de build e cadeia de suprimentos são o contexto em que a
assinatura de commits faz sentido — e mostram por que ela sozinha não basta.

### Software Supply Chain Security — Cassie Crossley · O'Reilly · 2024

**Nível:** intermediário.
Tratamento abrangente e atual: SBOM, proveniência, assinatura, requisitos regulatórios. É a
ponte entre este curso e as exigências do [65 § 4](65-estado-da-arte.md). Pago.

### Securing DevOps — Julien Vehent · Manning · 2018

**Nível:** intermediário.
Bom em pipeline e automação; envelheceu no ferramental. Pago.

---

## 5. Roteiro de leitura

| Objetivo | Leia, nesta ordem |
|---|---|
| **entender o mecanismo** | Pro Git 7.4 → Pro Git cap. 10 → `PROTOCOL.sshsig` ([95](95-referencias.md)) |
| **entender a criptografia** | Serious Cryptography (cap. de hash e assinatura) → Katz & Lindell, se quiser rigor |
| **entender por que sistemas falham** | Security Engineering 🆓, caps. de distribuição de chaves e economia |
| **implantar numa organização** | Building Secure and Reliable Systems 🆓 → Software Supply Chain Security |
| **nível pesquisa** | Boneh & Shoup 🆓 → os papers em [95](95-referencias.md) |

**Se você só puder ler duas coisas:** Pro Git 7.4 (uma hora) e os capítulos de distribuição de
chaves do Security Engineering (uma tarde). Os dois são gratuitos e cobrem, juntos, o "como" e
o "por que" melhor que qualquer outra combinação.

---

## 6. Nota sobre traduções para o português

| Obra | Tradução PT? | Qualidade |
|---|---|---|
| Pro Git | **sim, online e gratuita** | boa; alguns capítulos atrasados em relação ao inglês |
| GitHub Docs | **sim, oficial** | boa e mantida |
| Serious Cryptography | 1ª edição | aceitável, mas a edição atual é a 2ª, só em inglês |
| Security Engineering | não | — |
| Katz & Lindell | não | — |
| Software Supply Chain Security | não | — |

O material técnico deste assunto em português é escasso e concentrado em blog. É a razão pela
qual o Bloco B deste curso foi escrito em vez de apenas referenciado.

---

## Autoteste

1. Qual capítulo do Pro Git trata diretamente de assinatura, e qual explica por que a
   assinatura muda o hash?
2. Qual livro de criptografia é o mais indicado para quem programa, e por quê?
3. Por que o *Applied Cryptography* de Schneier não deve guiar decisão técnica hoje?
4. Quais obras desta lista são legalmente gratuitas?
5. Se você só puder ler duas coisas, quais são?
6. Por que não existe livro atual sobre OpenPGP?

*(Respostas: 1 — 7.4 e o capítulo 10 (Git Internals). 2 — *Serious Cryptography*, 2ª ed., por
tratar hash, assinatura e curvas com rigor sem exigir matemática pesada. 3 — é de 1996 e o
próprio autor o considera datado. 4 — Pro Git, Security Engineering 3ª ed., Boneh & Shoup,
Building Secure and Reliable Systems. 5 — Pro Git 7.4 e os capítulos de distribuição de chaves
do Security Engineering. 6 — o campo se moveu para as RFCs e para a documentação do GnuPG; o
modelo que os livros descreviam, a rede de confiança, não vingou.)*

---

**Verificado na web em 13/08/2026:** edição e ano de *Serious Cryptography* 2ª ed. (No Starch,
out/2024) · disponibilidade gratuita de *Security Engineering* 3ª ed. no site de Ross Anderson
· *A Graduate Course in Applied Cryptography* (Boneh & Shoup, versão 0.6, jan/2023) em
toc.cryptobook.us · Pro Git em git-scm.com/book (PT-BR, EN, FR) · *SSH Mastery* 2ª ed.
**Nenhum ISBN é citado neste arquivo por opção**, para não arriscar erro de dígito.

**Próximo:** [95-referencias.md](95-referencias.md).
