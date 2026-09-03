# 90 · Bibliografia comentada

> Nível: todos · **Edições conferidas na web em 14/08/2026**
> Onde não tenho certeza da edição ou do ISBN, cito apenas autor e título. **Nada
> aqui foi inventado.**

---

## 90.1 · Se você for ler um livro só

> **Neil Madden. _API Security in Action_. Manning, 2020. ISBN 978-1-61729-602-4.**

É o melhor livro para quem trabalha com JWT. Não é um livro *sobre* JWT — é sobre
segurança de API, e trata JWT no contexto real em que ele existe: junto de sessão, de
OAuth, de macaroons, de mTLS e de capacidades.

O que ele faz melhor que os outros: **compara honestamente** e diz quando **não** usar
JWT. O autor é criptógrafo praticante (trabalhou na ForgeRock) e escreve com as
cicatrizes à mostra. Os capítulos sobre tokens autocontidos e sobre capacidades são os
melhores textos que li sobre o assunto.

Nível: intermediário a avançado. Envelheceu? Pouco — o núcleo é conceitual. Falta o
que veio depois de 2020: DPoP (RFC 9449, 2023), SD-JWT (RFC 9901, 2025), RFC 9700
(2025). Complemente com [65-estado-da-arte.md](65-estado-da-arte.md).

**Não há tradução para o português** que eu tenha confirmado.

---

## 90.2 · Gratuitos e legítimos

Liberados pelos autores ou editoras. Não são cópias piratas.

| Obra | Autor | Onde | Nota |
|---|---|---|---|
| **_The JWT Handbook_** | Sebastián Peyrott | [auth0.com/resources/ebooks/jwt-handbook](https://auth0.com/resources/ebooks/jwt-handbook) | ~90 páginas, o material dedicado mais completo que existe de graça. Pede e-mail. Excelente na parte criptográfica. Publicado pela Auth0 |
| **_OAuth 2.0 Simplified_** | Aaron Parecki | [oauth.com](https://www.oauth.com/) | **Livro inteiro, gratuito online.** Do coeditor do OAuth 2.1. A melhor introdução a OAuth que existe, em qualquer preço |
| **_A Graduate Course in Applied Cryptography_** | Dan Boneh, Victor Shoup | [toc.cryptobook.us](http://toc.cryptobook.us/) | **PDF gratuito**, liberado pelos autores. Nível pós-graduação. Para quem foi ao [60-teoria-avancada.md](60-teoria-avancada.md) e quis mais |
| **_The Handbook of Applied Cryptography_** | Menezes, van Oorschot, Vanstone | [cacr.uwaterloo.ca/hac/](https://cacr.uwaterloo.ca/hac/) | **PDF gratuito** por autorização da CRC Press. Clássico de 1996: envelheceu em recomendações, continua excelente em fundamentos |
| **OWASP Cheat Sheet Series** | OWASP | [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/) | não é livro, mas é a referência prática mais consultada da área |

---

## 90.3 · Criptografia — dos fundamentos à teoria

| Livro | Autor / Editora / Ano | Nível | Comentário |
|---|---|---|---|
| **_Serious Cryptography_, 2ª ed.** | Jean-Philippe Aumasson · No Starch Press · ISBN 978-1-71850-384-7 | intermediário | **A melhor ponte entre "usa" e "entende".** Escrito por criptógrafo praticante, sem álgebra pesada, sem simplificação enganosa. A 2ª edição atualiza e acrescenta um capítulo novo. Se você quer entender HMAC, ECDSA e Ed25519 de verdade, é este |
| **_Real-World Cryptography_** | David Wong · Manning · 2021 | intermediário | Foco em **o que se usa hoje**, não no histórico. Ótimo sobre curvas elípticas e pós-quântico. Complementa bem o Aumasson |
| **_Cryptography Engineering_** | Ferguson, Schneier, Kohno · Wiley · 2010 | intermediário | O melhor sobre **como sistemas criptográficos falham na prática**. Datado em recomendações específicas (é de 2010), atemporal em mentalidade de projeto |
| **_Introduction to Modern Cryptography_, 3ª ed.** | Katz & Lindell · CRC Press · 2020 | avançado | **O livro-texto padrão** de criptografia com prova. É aqui que EUF-CMA, reduções e o modelo do oráculo aleatório são tratados com rigor. Exige matemática |

**Sobre traduções para o português:** Stallings, _Criptografia e Segurança de Redes_
(Pearson), tem edições em português brasileiro e é usado em muitos cursos de
graduação. É mais amplo e menos profundo que os acima; serve como primeiro contato em
português. Não confirmei qual é a edição brasileira mais recente — verifique antes de
comprar.

---

## 90.4 · Identidade, OAuth e OIDC

| Livro | Autor / Editora / Ano | Nível | Comentário |
|---|---|---|---|
| **_OAuth 2 in Action_** | Justin Richer, Antonio Sanso · Manning · 2017 | intermediário | O tratamento mais completo de OAuth em livro. Richer é autor de várias RFCs do grupo. **Envelheceu** no que a RFC 9700 (2025) mudou — leia junto com a BCP |
| **_Solving Identity Management in Modern Applications_, 2ª ed.** | Yvonne Wilson, Abhishek Hingnikar · Apress · 2023 | iniciante a intermediário | Panorama de identidade: OAuth, OIDC, SAML, gestão de usuários. Menos técnico, mais arquitetural. Bom para quem decide, não só para quem implementa |
| **_Microservices Security in Action_** | Prabath Siriwardena, Nuwan Dias · Manning · 2020 | intermediário | JWT em arquitetura distribuída: propagação de identidade, mTLS, service mesh. Cobre o que o [22-operacao-em-producao.md](22-operacao-em-producao.md) trata |
| **_Identity and Data Security for Web Development_** | Jonathan LeBlanc, Tim Messerschmidt · O'Reilly · 2016 | iniciante | Introdutório e datado. Só se você achar de graça |

---

## 90.5 · Segurança de aplicação web

| Livro | Autor / Editora / Ano | Nível | Comentário |
|---|---|---|---|
| **_The Web Application Hacker's Handbook_, 2ª ed.** | Dafydd Stuttard, Marcus Pinto · Wiley · 2011 | intermediário | **Datado** (é de 2011, anterior ao JWT ser RFC), e ainda assim o melhor livro de metodologia de teste de aplicação web. Leia pela mentalidade, não pelas tecnologias. Para a parte atual de JWT, use a PortSwigger Academy — dos mesmos autores, gratuita e atualizada |
| **_The Tangled Web_** | Michał Zalewski · No Starch Press · 2011 | intermediário | Sobre o modelo de segurança do navegador. Datado nas APIs, insuperável na explicação de **por que** a web é como é. Relevante para [18-onde-guardar-no-cliente.md](18-onde-guardar-no-cliente.md) |
| **_Alice and Bob Learn Application Security_** | Tanya Janca · Wiley · 2020 | iniciante | Acessível e atual. Bom primeiro livro de segurança para quem programa |

---

## 90.6 · Clássicos que continuam valendo × livros datados

**Continuam valendo integralmente:**

- Katz & Lindell — a teoria não envelhece;
- _Cryptography Engineering_ — a mentalidade de projeto não envelhece;
- _The Tangled Web_ — a arqueologia do navegador explica o presente;
- _API Security in Action_ — o núcleo é conceitual.

**Datados, leia com ressalva:**

- _The Web Application Hacker's Handbook_ (2011) — metodologia ✅, tecnologias ❌;
- _OAuth 2 in Action_ (2017) — anterior à RFC 9700; o fluxo *implicit* que ele
  descreve como legítimo hoje é **proibido**;
- _Identity and Data Security for Web Development_ (2016) — superado;
- qualquer livro de JWT anterior a 2020 — anterior à RFC 8725, a BCP que define a
  prática correta.

**Regra prática para este assunto:** livro anterior a 2020 sobre **prática** de JWT
deve ser lido com a RFC 8725 aberta ao lado. Livro sobre **criptografia** ou sobre
**mentalidade** envelhece muito mais devagar.

---

## 90.7 · Papers e artigos seminais

| Trabalho | Autores / Ano | Por que ler |
|---|---|---|
| *Keying Hash Functions for Message Authentication* | Bellare, Canetti, Krawczyk · 1996 | o paper original do HMAC |
| *New Proofs for NMAC and HMAC* | Bellare · 2006 | a prova sob hipótese mais fraca; explica por que HMAC-SHA1 sobreviveu à queda do SHA-1 |
| *The Random Oracle Methodology, Revisited* | Canetti, Goldreich, Halevi · 1998 | por que provas no ROM não são provas — e por que as aceitamos mesmo assim |
| *Generic Groups, Collision Resistance, and ECDSA* | Brown · 2001 | a prova do ECDSA no modelo de grupo genérico |
| *High-speed high-security signatures* (Ed25519) | Bernstein, Duif, Lange, Schwabe, Yang · 2011 | o paper do Ed25519; a seção de motivação é uma aula de projeto seguro |
| *Chosen Ciphertext Attacks Against Protocols Based on RSA Encryption Standard PKCS #1* | Bleichenbacher · 1998 | por que `RSA1_5` é proibido no JWE |
| *Critical vulnerabilities in JSON Web Token libraries* | Tim McLean · março de 2015 | **o artigo que definiu o assunto**. Curto. Leia hoje |
| *ROBOT Attack* | Böck, Somorovsky, Young · 2018 | Bleichenbacher renascendo 19 anos depois |
| Literatura de *XML Signature Wrapping* | vários · 2005–2012 | o problema que o JOSE decidiu eliminar por projeto |

O artigo de Tim McLean é o único desta lista que eu chamaria de **leitura
obrigatória** para qualquer pessoa que use JWT. São poucas páginas e explicam por que
a lista de algoritmos existe.

---

## 90.8 · Trilhas de leitura

### "Quero usar bem" (≈ 2 semanas)

```
Este material (blocos A e B)
  → RFC 7519 + RFC 8725
  → OAuth 2.0 Simplified (Parecki)
  → API Security in Action, capítulos de tokens
```

### "Quero entender a criptografia" (≈ 2 meses)

```
Serious Cryptography, 2ª ed. (Aumasson)
  → Real-World Cryptography (Wong)
  → paper do HMAC (Bellare et al.)
  → paper do Ed25519
  → Katz & Lindell, se quiser rigor
```

### "Quero atacar e defender" (≈ 1 mês)

```
Artigo do Tim McLean (2015)
  → PortSwigger Academy, laboratórios de JWT
  → The Web Application Hacker's Handbook (metodologia)
  → OWASP Cheat Sheets
  → 20-ataques-e-defesas.md deste material
```

### "Quero decidir arquitetura" (≈ 3 semanas)

```
21-quando-nao-usar.md deste material
  → API Security in Action (o livro inteiro)
  → Microservices Security in Action
  → Solving Identity Management in Modern Applications
```

### "Quero pesquisar" (≈ 6 meses)

```
Katz & Lindell
  → Boneh & Shoup (gratuito)
  → as RFCs de JOSE, integrais
  → RFC 9901 (SD-JWT) e RFC 9964 (ML-DSA)
  → os rascunhos ativos do grupo OAuth do IETF
```

---

## 90.9 · O que não recomendo

Sem citar títulos, porque não é sobre atacar autores específicos:

- **"JWT em 24 horas"** e similares — o assunto não dá 24 horas de conteúdo honesto;
- **livros de uma tecnologia com um capítulo de JWT** — costumam ensinar
  `jwt.verify(token, segredo)` sem lista de algoritmos, e propagam o erro;
- **cursos e livros anteriores a 2020 apresentados como atuais** — anteriores à
  RFC 8725;
- **qualquer material que diga "JWT é criptografado"** — se erra isso, erra o resto.

**Um teste rápido de qualquer material sobre JWT:** procure se ele fala de
`algorithms` na verificação, de validação de `aud`, e de revogação. Se os três
estiverem ausentes, o material é superficial ou perigoso.

---

## Autoteste

1. Se você fosse ler um livro só, qual seria e por quê?
2. Cite três obras **legalmente gratuitas** e o que cada uma faz melhor.
3. Qual livro está datado em recomendações mas continua valendo em mentalidade?
4. Por que _OAuth 2 in Action_ (2017) precisa ser lido junto com a RFC 9700?
5. Qual é o único paper desta lista que é leitura obrigatória, e por quê?
6. Qual a diferença entre a prova de HMAC de 1996 e a de 2006, e qual consequência
   prática ela teve?
7. Qual é o teste rápido para avaliar a qualidade de um material sobre JWT?
8. Existe tradução para o português do livro recomendado na 90.1?

---

### Nota de método

Edições e ISBNs conferidos na web em **14/08/2026** para: _API Security in Action_
(Manning, 2020, ISBN 978-1-61729-602-4) e _Serious Cryptography_, 2ª edição
(No Starch, ISBN 978-1-71850-384-7). Para as demais obras, cito autor, editora e ano
quando tenho confiança, e omito o ISBN quando não confirmei. Os papers são citados
por autor e ano, sem número de página. **Se algum dado estiver errado, é erro de
memória, não invenção deliberada — confirme antes de comprar.**
