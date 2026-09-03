# 90 · Bibliografia comentada

**Nível:** todos · **Conferido na web em 31/08/2026**

Edições e datas foram verificadas. **Onde não tive certeza, cito só autor e título** —
inventar ISBN ou edição seria pior que omitir.

---

## 1. O livro do assunto

### ⭐ Ivan Ristić — *Bulletproof TLS and PKI*, **2ª edição**, Feisty Duck, **2022**. ISBN 978-1-907117-09-1. 512 p.

**É o único livro dedicado a TLS que vale a pena, e é excelente.** Escrito pelo criador
do **SSL Labs**, o que se nota: cada recomendação vem com a razão e com os dados de
quem mediu a internet inteira.

- **Nível:** intermediário a avançado. Um iniciante consegue ler os primeiros capítulos.
- **Cobre:** protocolo (incluindo TLS 1.3), PKI, o histórico completo de ataques,
  configuração prática de OpenSSL, nginx, Apache, Java e Windows, e desempenho.
- **O que faz melhor que qualquer outro:** o catálogo de ataques com contexto histórico,
  e a ponte entre teoria e configuração real.
- **Envelheceu?** **Parcialmente.** É de janeiro de 2022, portanto **anterior** aos
  certificados de 6 dias, à validade de 200 dias, ao ML-KEM em produção e ao ECH como
  RFC. Os fundamentos e a análise de ataques continuam integralmente válidos; o que é
  operacional em 2026 precisa ser complementado por [65](65-estado-da-arte.md) e
  [16](16-acme-e-automacao.md) deste curso.
- **Gratuito?** Não. Editora Feisty Duck (<https://www.feistyduck.com/>), com versão
  digital que **recebe atualizações** — vale mais que o papel por isso.
- **Em português?** Não há tradução.

**Se você só puder ler um livro sobre TLS, é este.** Não há segundo lugar.

### Ivan Ristić — *OpenSSL Cookbook*, Feisty Duck.

**Gratuito** em <https://www.feistyduck.com/books/openssl-cookbook/>. É um extrato dos
capítulos de OpenSSL do *Bulletproof*, atualizado periodicamente. Referência prática
excelente e sem custo — **comece por aqui** se estiver em dúvida sobre comprar o outro.

---

## 2. Criptografia — o que sustenta o TLS

### ⭐ Jean-Philippe Aumasson — *Serious Cryptography*, **2ª edição**, No Starch Press, **2024**. ISBN 978-1-7185-0384-7.

**A melhor introdução moderna à criptografia para quem programa.** Sem provas pesadas,
com foco no que se usa e no que dá errado. A 2ª edição atualizou o material e
acrescentou um capítulo sobre criptografia em criptomoedas.

- **Nível:** intermediário. Exige matemática de ensino médio, não mais.
- **Por que ler para TLS:** os capítulos de AEAD, curvas elípticas, troca de chaves e
  aleatoriedade explicam exatamente o que o [14](14-criptografia-do-tls.md) resume.
- **Envelheceu?** Não — é o mais atual dos livros gerais.
- **Em português?** A 1ª edição saiu como *Criptografia Moderna* (Novatec). Confirme a
  edição antes de comprar; a 2ª é substancialmente melhor.

### David Wong — *Real-World Cryptography*, Manning, **2021**. ISBN 978-1-61729-671-0.

Orientado a protocolos reais (TLS, Noise, Signal, criptomoedas) em vez de primitivas
isoladas. **Tem um capítulo dedicado ao TLS** que é uma boa ponte entre criptografia e
protocolo.

- **Nível:** intermediário.
- **Gratuito?** Não, mas a Manning disponibiliza capítulos no liveBook
  (<https://livebook.manning.com/book/real-world-cryptography/>).
- **Envelheceu?** Pouco. É pré-padronização do NIST para PQC (2024), então a parte
  pós-quântica está desatualizada.

### Niels Ferguson, Bruce Schneier, Tadayoshi Kohno — *Cryptography Engineering*, Wiley, **2010**. ISBN 978-0-470-47424-2.

O clássico sobre **como não errar ao usar criptografia**. É a 2ª edição do
*Practical Cryptography* (2003), renomeada.

- **Nível:** intermediário.
- **Continua valendo?** **Sim, para princípios de engenharia** — modelo de ameaça,
  complexidade como inimiga, gestão de chaves, por que não implementar você mesmo.
- **Envelheceu?** **Sim, nos detalhes.** É de 2010: anterior ao TLS 1.3, ao ChaCha20,
  ao AEAD onipresente, às curvas modernas. Leia pelos princípios, não pelas recomendações.

### Dan Boneh, Victor Shoup — *A Graduate Course in Applied Cryptography*.

- **Gratuito e legal:** <https://toc.cryptobook.us/> — os autores publicam abertamente.
- **Nível:** pesquisa. É o livro-texto para quem quer ler as provas do
  [60](60-teoria-avancada.md).
- **Estado:** em desenvolvimento contínuo; confira a versão mais recente no site.

### Katz & Lindell — *Introduction to Modern Cryptography*, CRC Press, 3ª edição, 2020.

O livro-texto padrão de criptografia com rigor de prova, em cursos de pós-graduação.
Se *Serious Cryptography* é a versão para engenheiros, este é a versão para teóricos.
Não gratuito.

---

## 3. Redes — o contexto

### ⭐ Kurose & Ross — *Redes de Computadores e a Internet: uma abordagem top-down*, 8ª edição, Pearson.

O livro de redes mais usado no mundo, **com tradução brasileira boa** (a Pearson
mantém a edição em português). Tem um capítulo de segurança com uma introdução sólida
ao TLS.

- **Nível:** iniciante a intermediário. É livro de graduação, e funciona.
- **Por que ele:** a abordagem *top-down* (da aplicação para o físico) é a melhor para
  quem vem de software.

### Ilya Grigorik — *High Performance Browser Networking*, O'Reilly, 2013.

- **⭐ Gratuito e legal, na íntegra:** <https://hpbn.co/> (o autor liberou).
- **Por que ler:** os capítulos sobre TLS e latência são a melhor explicação existente
  do **custo real** do TLS e de como reduzi-lo.
- **Envelheceu?** É de 2013 — anterior ao TLS 1.3, ao HTTP/2 maduro e ao QUIC.
  Os **princípios de latência não envelheceram nada**; os números e as versões, sim.

### W. Richard Stevens — *TCP/IP Illustrated, Volume 1*, 2ª edição (Fall, Stevens), Addison-Wesley, 2011.

O clássico de TCP/IP. Relevante aqui porque entender TCP é entender por que o handshake
custa RTTs, por que a janela de congestionamento importa para o tamanho do certificado,
e o que o QUIC resolve.

---

## 4. Segurança de aplicações web

### Michal Zalewski — *The Tangled Web*, No Starch Press, 2011.

Sobre o modelo de segurança do navegador: origem, cookies, conteúdo misto, e por que
HTTPS sozinho não protege uma aplicação web. Datado nos detalhes, **insubstituível nos
conceitos**.

### OWASP — *Cheat Sheet Series*.

- **Gratuito:** <https://cheatsheetseries.owasp.org/>
- Não é livro, mas é a referência prática mais atualizada. A folha de *Transport Layer
  Security* é curta, direta e revisada com frequência.

---

## 5. Em português — o que existe

Sendo honesto: **não há livro em português dedicado a TLS.** O que existe:

| Obra | Comentário |
|---|---|
| **Kurose & Ross** (Pearson, 8ª ed.) | ✅ tradução boa; o capítulo de segurança é a melhor introdução ao TLS em português impresso |
| **Criptografia Moderna** — Aumasson (Novatec) | tradução da **1ª** edição de *Serious Cryptography*; boa, mas confira se saiu a 2ª |
| **Segurança de Redes** — Stallings (Pearson) | acadêmico, abrangente, denso; tradução aceitável |
| Livros de "segurança da informação" genéricos | ⚠️ costumam ter 3 páginas sobre TLS, frequentemente desatualizadas. Não compre por causa disso |

**Recomendação franca:** para TLS, o material em inglês é incomparavelmente melhor, e
os melhores itens são gratuitos (*OpenSSL Cookbook*, *hpbn.co*, RFCs, `tls13.xargs.org`).
Se a barreira do idioma for um problema, comece pelos vídeos em português listados em
[85](85-cursos-e-certificacoes.md) e use este curso como texto de apoio.

---

## 6. O que é legalmente gratuito

| Obra | Onde | Por que é grátis |
|---|---|---|
| *OpenSSL Cookbook* — Ristić | <https://www.feistyduck.com/books/openssl-cookbook/> | a editora libera |
| *High Performance Browser Networking* — Grigorik | <https://hpbn.co/> | o autor liberou |
| *A Graduate Course in Applied Cryptography* — Boneh & Shoup | <https://toc.cryptobook.us/> | os autores publicam abertamente |
| *Illustrated TLS 1.3 Connection* — Driscoll | <https://tls13.xargs.org/> | projeto aberto |
| Todas as **RFCs** | <https://www.rfc-editor.org/> | a IETF publica abertamente |
| OWASP Cheat Sheets | <https://cheatsheetseries.owasp.org/> | licença aberta |
| Mozilla Server Side TLS | <https://wiki.mozilla.org/Security/Server_Side_TLS> | wiki aberta |
| Cloudflare Learning Center | <https://www.cloudflare.com/learning/ssl/> | conteúdo de marketing, mas bom e correto |

---

## 7. Roteiro de leitura sugerido

| Se você quer… | Leia, nesta ordem |
|---|---|
| **começar do zero** | Kurose (cap. de segurança) → *OpenSSL Cookbook* → *Bulletproof TLS* |
| **usar TLS direito no trabalho** | *OpenSSL Cookbook* → Mozilla Server Side TLS → *Bulletproof TLS* |
| **entender a criptografia** | *Serious Cryptography* 2ª ed. → *Real-World Cryptography* (cap. TLS) |
| **otimizar desempenho** | *hpbn.co* (caps. de TLS) → *Bulletproof TLS* (cap. de desempenho) |
| **chegar à pesquisa** | Boneh & Shoup → RFC 8446 → papers do [95](95-referencias.md) |
| **só uma coisa** | *Bulletproof TLS and PKI*, 2ª ed. (2022), complementado por [65](65-estado-da-arte.md) |

---

## Autoteste

1. Qual é **o** livro sobre TLS, quem escreveu e por que a autoria importa?
2. Em que aspecto o *Bulletproof TLS* (2022) envelheceu, e com o que complementá-lo?
3. Qual livro de Ristić é gratuito, e o que ele contém?
4. Qual é a melhor introdução moderna à criptografia para quem programa, e em que edição?
5. *Cryptography Engineering* (2010) continua valendo? Para quê, e para o quê não?
6. Cite três obras legalmente gratuitas e por que cada uma é gratuita.
7. Existe livro em português sobre TLS? Qual é a recomendação honesta?
8. Que livro ler para entender o custo de latência do TLS, e onde ele envelheceu?

*Respostas: §1, §1, §1, §2, §2, §6, §5, §3.*

---

**Próximo:** [95-referencias.md](95-referencias.md).
