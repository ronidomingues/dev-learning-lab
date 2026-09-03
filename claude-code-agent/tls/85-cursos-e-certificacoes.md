# 85 · Cursos e certificações

**Nível:** todos · **Pesquisado na web em 31/08/2026.**
Links podem expirar; conteúdo em vídeo envelhece. **Confirme a data de publicação de
qualquer curso antes de investir tempo** — material sobre TLS anterior a 2019 ensina
TLS 1.2 como se fosse o estado da arte, e material anterior a 2015 ensina práticas
hoje perigosas.

---

## 0. Antes de qualquer curso: a verdade sobre este assunto

**Não existe um "curso de TLS" bom e completo.** Procurei em português, inglês e
francês. O que existe é:

- **documentação oficial e RFCs** (excelentes, gratuitas, e o material mais confiável);
- **um livro definitivo** (*Bulletproof TLS*, ver [90](90-bibliografia.md));
- **vídeos avulsos muito bons** sobre partes do assunto;
- **cursos de "segurança de redes"** que dedicam 1 ou 2 aulas ao TLS;
- **muito conteúdo raso** de plataforma de certificado gratuito.

**Opinião profissional:** o melhor caminho de aprendizado para TLS é **prática guiada**
— exatamente o que os arquivos [70-pratica.md](70-pratica.md) e
[07-projeto-modelo/](07-projeto-modelo/README.md) fazem — combinada com a leitura da
RFC 8446 e do *Bulletproof TLS*. Cursos em vídeo servem bem para a **intuição inicial**
e para a **criptografia de base**, não para dominar o assunto.

---

## 1. Português (Brasil e Portugal)

### 1.1 Gratuitos de verdade, em vídeo

| Curso | Autor / instituição | Onde | Duração | Nível | Vale? |
|---|---|---|---|---|---|
| **Curso de CA com OpenSSL, TLS/SSL e HTTPS** | comunidade (playlist) | [YouTube](https://www.youtube.com/playlist?list=PLozhsZB1lLUO1w0nfntfvR7VPtpa1SkeM) | algumas horas | iniciante–intermediário | **Sim.** É o material em PT mais próximo de um curso prático de CA e certificados. Confira a data de cada vídeo |
| **Tudo sobre HTTPS, SSL/TLS, certificados e chaves pública/privada** | live técnica em PT-BR | [YouTube](https://www.youtube.com/watch?v=FmfE1qN1_aE) | ~1–2 h | iniciante | **Sim, como introdução.** Formato de live: bom para intuição, fraco como referência |
| **Segurança e Criptografia** | **Bóson Treinamentos** (Fábio dos Reis) | [YouTube / bosontreinamentos.com.br](https://www.youtube.com/@bosontreinamentos) | série | iniciante–intermediário | **Sim.** Um dos canais técnicos mais consistentes em PT-BR; ótimo para os fundamentos de rede e criptografia que sustentam o TLS |
| **Redes de Computadores** | Bóson Treinamentos | YouTube | série longa | iniciante | Sim, para o pré-requisito de redes |
| **Segurança de TI (Google, legendado)** | Google via Coursera | [Coursera](https://www.coursera.org/learn/seguranca-de-it) | ~30 h | iniciante | **Parcial.** Bom panorama; **TLS é uma fração pequena**. Gratuito para assistir; certificado é pago |
| **Segurança da Informação** | Cisco Networking Academy | [netacad.com (PT-BR)](https://www.netacad.com/pt/career-paths/cybersecurity?courseLang=pt-BR) | 15–30 h | iniciante | Sim, para base ampla. Emite **certificado gratuito** de conclusão |

### 1.2 Onde ter cuidado

Há dezenas de sites brasileiros oferecendo "Curso de Segurança de Redes grátis com
certificado" (Cursa, Elevo, Anglo, WR Educacional, Cursou, EducaWeb e semelhantes).

**Seja franco consigo mesmo sobre o que eles são:** o conteúdo costuma ser texto
genérico, sem prática, e o "certificado" tem valor de mercado **próximo de zero** —
serve para horas complementares de graduação e para currículo de concurso, não para
convencer um entrevistador técnico. Não são fraude; são outra coisa. Se o seu objetivo
é aprender TLS, o tempo rende muito mais nos laboratórios do
[70-pratica.md](70-pratica.md).

### 1.3 Pagos que valem menção

| Curso | Onde | Preço aprox. (31/08/2026) | Comentário |
|---|---|---|---|
| **Certificação Digital SSL/TLS — Fundamentos e Prática** | [Udemy](https://www.udemy.com/course/ssltls-fundamentosepratica/) | R$ 30–90 em promoção | O curso **em português dedicado a TLS** mais completo que encontrei. Confira a data de atualização antes de comprar |
| **Segurança da Informação com Criptografia e Certificados Digitais** | [Senac SP](https://www.sp.senac.br/cursos-livres/curso-de-seguranca-da-informacao-com-criptografia-de-dados-e-certificados-digitais) | consultar | presencial/online; útil para quem quer certificado institucional reconhecido no Brasil |

---

## 2. Inglês

### 2.1 O melhor material gratuito do assunto, em qualquer idioma

| Curso | Autor | Onde | Duração | Nível | Comentário |
|---|---|---|---|---|---|
| **TLS (playlist completa)** | **Hussein Nasser** | [YouTube](https://www.youtube.com/playlist?list=PLQnljOFTspQW4yHuqp_Opv853-G_wAiH-) | **~8 h** | intermediário | ⭐ **A melhor coisa gratuita sobre TLS que existe.** Cobre TLS 1.2 e 1.3, certificados, mTLS, kTLS, handshake por exemplo. Explicação de engenheiro, não de professor — direto ao ponto |
| **TLS Handshake / TLS 1.3 explained** | **Practical Networking** (Ed Harmoush) | [YouTube](https://www.youtube.com/@PracticalNetworking) | ~1–2 h | iniciante–intermediário | ⭐ Didática visual excelente. A melhor explicação animada do handshake que existe |
| **Cryptography I** | **Dan Boneh, Stanford** | [Coursera](https://www.coursera.org/learn/crypto) · [material aberto](https://crypto.stanford.edu/~dabo/courses/OnlineCrypto/) | ~6 semanas | avançado | ⭐ O curso de criptografia de referência. **Gratuito para assistir**; certificado ~€67. Não é sobre TLS, é sobre o que o TLS usa. Exigente e vale cada hora |
| **CS 255: Introduction to Cryptography** | Stanford | [cs255.stanford.edu](https://cs255.stanford.edu/) | semestre | avançado | Notas, slides e trabalhos abertos |
| **Computerphile — TLS/HTTPS/Diffie-Hellman** | University of Nottingham | YouTube | vídeos de 10–20 min | iniciante | Melhor formato curto para intuição |
| **Cloudflare Learning Center — SSL/TLS** | Cloudflare | [cloudflare.com/learning/ssl/](https://www.cloudflare.com/learning/ssl/) | leitura | iniciante–intermediário | Excelente, atualizado, gratuito, sem cadastro |
| **Mozilla Server Side TLS** | Mozilla | [wiki.mozilla.org/Security/Server_Side_TLS](https://wiki.mozilla.org/Security/Server_Side_TLS) | referência | intermediário | A fonte por trás do gerador de configuração |
| **Illustrated TLS 1.3 Connection** | Michael Driscoll | [tls13.xargs.org](https://tls13.xargs.org/) | 1–2 h | avançado | ⭐⭐ **Byte a byte, com cada campo anotado e as chaves derivadas na tela.** Se você quer *ver* o TLS 1.3, é isto. Único no mundo |
| **Let's Encrypt — How It Works** | ISRG | [letsencrypt.org/how-it-works/](https://letsencrypt.org/how-it-works/) | 30 min | iniciante | Base para o [16](16-acme-e-automacao.md) |

### 2.2 Trilhas mais amplas, com TLS dentro

| Curso | Onde | Comentário |
|---|---|---|
| **Fortinet Training Institute** — trilhas gratuitas | [fortinet.com/training](https://www.fortinet.com/training/cybersecurity-professionals) | Gratuito e com **certificação gratuita** (programa NSE). Enviesado para os produtos Fortinet — saiba disso ao estudar |
| **Cisco Networking Academy** — *Introduction to Cybersecurity*, *Network Defense* | [netacad.com](https://www.netacad.com/) | Gratuito, com certificado de conclusão. Boa base de redes |
| **TryHackMe / HackTheBox** — trilhas de rede e web | tryhackme.com · hackthebox.com | Prático, gamificado; camada gratuita útil, boa parte é paga |
| **OWASP Cheat Sheets — Transport Layer Security** | [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/) | Referência prática, gratuita, atualizada |

---

## 3. Francês

O material francófono sobre TLS especificamente é escasso. O que vale:

| Curso | Autor / instituição | Onde | Duração | Nível | Comentário |
|---|---|---|---|---|---|
| **Sécurisez vos connexions avec TLS** (dentro de *Sécurisez vos données avec la cryptographie*) | **OpenClassrooms** | [openclassrooms.com](https://openclassrooms.com/fr/courses/1757741-securisez-vos-donnees-avec-la-cryptographie/6031695-securisez-vos-connexions-avec-tls) | 1 capítulo (~1 h); curso completo ~10 h | iniciante | ⭐ **O melhor material em francês sobre TLS.** Gratuito para ler; certificado exige assinatura |
| **MOOC SecNumacadémie** | **ANSSI** (agência nacional de cibersegurança da França) | [secnumacademie.gouv.fr](https://secnumacademie.gouv.fr/) · [cyber.gouv.fr](https://cyber.gouv.fr/offre-de-service/formations-entrainement-et-decouverte-des-metiers/formations/formations-delivrees-par-lanssi/mooc-secnumacademie/) | 4 módulos, 20 unidades | iniciante | ⚠️ **A plataforma estava fechada para reformulação em 2026**, com nova versão prevista para o mesmo ano. Vale checar — quando ativo, é gratuito, de qualidade estatal e emite **atestado gratuito**. TLS aparece dentro do módulo de segurança na internet |
| **Guides de l'ANSSI** — *Recommandations de sécurité relatives à TLS* | ANSSI | [cyber.gouv.fr](https://cyber.gouv.fr/publications) | documento | intermediário–avançado | ⭐ **Recomendo mesmo a quem não lê francês fluente.** É o equivalente francês do Mozilla Server Side TLS, com recomendações concretas de configuração e justificativas. Documento sério, atualizado |
| **Cursos de cibersegurança** | My Mooc / France Num | [my-mooc.com](https://www.my-mooc.com/fr/mooc/securite-numerique-academie) · [francenum.gouv.fr](https://www.francenum.gouv.fr/formations/formez-vous-sur-internet-gratuitement-la-securite-du-numerique) | variado | iniciante | Agregadores; qualidade irregular |

---

## 4. Certificações

### 4.1 Não existe certificação de TLS

Vale dizer com todas as letras: **não há uma certificação profissional dedicada a TLS**,
como há para nuvem ou para redes. TLS aparece como **tópico** dentro de certificações
mais amplas.

### 4.2 Gratuitas (emissor e exame sem custo)

| Certificação | Emissor | Custo | Vale no mercado? |
|---|---|---|---|
| **Fortinet NSE 1–3** (e trilhas do programa 2026) | Fortinet | **grátis** | Reconhecimento limitado, mas **real** — aparece em vagas de segurança de rede. Enviesada para produtos Fortinet |
| **Cisco Networking Academy** — certificados de conclusão | Cisco | **grátis** | Simbólico; vale como base e como linha no currículo de quem está começando |
| **Google Cybersecurity** (Coursera) | Google | assistir grátis; certificado pago | O conteúdo gratuito vale; o certificado é opcional |
| Certificados de plataformas brasileiras "grátis com certificado" | vários | grátis | **Valor de mercado próximo de zero.** Servem para horas complementares |

### 4.3 Pagas em que TLS aparece de verdade

| Certificação | Emissor | Custo aprox. (31/08/2026) | TLS aparece? |
|---|---|---|---|
| **CompTIA Security+** | CompTIA | ~US$ 400 (~R$ 2.070) | Sim, criptografia e PKI são domínio inteiro. Boa porta de entrada |
| **CCNA** | Cisco | ~US$ 300 (~R$ 1.550) | Sim, na parte de segurança |
| **CISSP** | ISC² | ~US$ 750 (~R$ 3.880) | Sim, em *Communication and Network Security*. Exige 5 anos de experiência |
| **OSCP** | OffSec | ~US$ 1.750 (~R$ 9.050) | Indiretamente; foco em exploração |
| **AWS/Azure/GCP Security Specialty** | provedores | ~US$ 300 (~R$ 1.550) | Sim, na parte de certificados gerenciados |

> **Opinião profissional, marcada como opinião:** para TLS especificamente, **nenhuma
> certificação substitui um repositório público com uma PKI que você montou, um serviço
> com mTLS funcionando e testes que provam que ele recusa o que deve recusar.** Numa
> entrevista técnica, "eu implementei uma CA com revogação por CRL e escrevi testes que
> tentam entrar com certificado revogado" pesa mais que uma linha de certificado.
> O [projeto-modelo](07-projeto-modelo/README.md) é exatamente isso — leve-o adiante.

---

## 5. Trilha recomendada, do zero à competência

| Fase | O que fazer | Tempo |
|---|---|---|
| **1. Intuição** | Practical Networking (TLS Handshake) + [01](01-introducao-leigo.md) deste curso | 3 h |
| **2. Mãos** | [03](03-instalacao.md) → [04](04-como-comecar.md) → labs 1, 2, 3 e 6 do [70](70-pratica.md) | 8 h |
| **3. Profundidade** | Playlist de TLS do Hussein Nasser + [12](12-handshake.md) e [13](13-certificados-e-pki.md) | 15 h |
| **4. Ver os bytes** | [tls13.xargs.org](https://tls13.xargs.org/) + lab 4 do [70](70-pratica.md) | 4 h |
| **5. Construir** | [07-projeto-modelo/](07-projeto-modelo/README.md), inteiro, com os desafios | 10 h |
| **6. Operar** | [16](16-acme-e-automacao.md), [17](17-configuracao-de-servidores.md), labs 8–11 | 12 h |
| **7. Base teórica** | *Cryptography I* (Dan Boneh) + [14](14-criptografia-do-tls.md) | 40 h |
| **8. Referência** | *Bulletproof TLS* + RFC 8446 ([90](90-bibliografia.md), [95](95-referencias.md)) | contínuo |

---

## Fontes consultadas (31/08/2026)

- Class Central — catálogos de TLS e criptografia: <https://www.classcentral.com/subject/tls> · <https://www.classcentral.com/subject/cryptography>
- Hussein Nasser — playlist TLS: <https://www.youtube.com/playlist?list=PLQnljOFTspQW4yHuqp_Opv853-G_wAiH->
- Coursera — *Cryptography I* (Stanford): <https://www.coursera.org/learn/crypto>
- Stanford — material aberto: <https://crypto.stanford.edu/~dabo/courses/OnlineCrypto/> · <https://cs255.stanford.edu/>
- OpenClassrooms — *Sécurisez vos connexions avec TLS*: <https://openclassrooms.com/fr/courses/1757741-securisez-vos-donnees-avec-la-cryptographie/6031695-securisez-vos-connexions-avec-tls>
- ANSSI — SecNumacadémie: <https://cyber.gouv.fr/offre-de-service/formations-entrainement-et-decouverte-des-metiers/formations/formations-delivrees-par-lanssi/mooc-secnumacademie/> (plataforma em reformulação em 2026)
- Fortinet Training Institute: <https://www.fortinet.com/training/cybersecurity-professionals>
- Cisco Networking Academy (PT-BR): <https://www.netacad.com/pt/career-paths/cybersecurity?courseLang=pt-BR>
- Bóson Treinamentos: <https://www.bosontreinamentos.com.br/>
- Playlist PT sobre CA/OpenSSL/HTTPS: <https://www.youtube.com/playlist?list=PLozhsZB1lLUO1w0nfntfvR7VPtpa1SkeM>
- Udemy — SSL/TLS em português: <https://www.udemy.com/course/ssltls-fundamentosepratica/>
- Senac SP: <https://www.sp.senac.br/cursos-livres/curso-de-seguranca-da-informacao-com-criptografia-de-dados-e-certificados-digitais>

> Preços de certificação em USD foram convertidos a R$ 5,17 e são **aproximados**.
> Preços de Udemy variam absurdamente com promoções — nunca pague o preço cheio.

---

## Autoteste

1. Por que não existe um "curso de TLS" bom e completo, e qual é o caminho recomendado?
2. Qual é o melhor material gratuito sobre TLS em qualquer idioma, e por quê?
3. O que é o `tls13.xargs.org` e para que serve?
4. O que os certificados "grátis" de plataformas brasileiras valem de verdade?
5. Qual é o melhor material em francês, e qual documento da ANSSI vale mesmo sem francês fluente?
6. Existe certificação profissional de TLS? O que existe?
7. Qual é a alternativa a uma certificação, para provar competência em TLS numa entrevista?
8. Descreva a trilha de 8 fases e o tempo total aproximado.

*Respostas: §0, §2.1, §2.1, §1.2, §3, §4.1, §4.3, §5.*

---

**Próximo:** [90-bibliografia.md](90-bibliografia.md).
