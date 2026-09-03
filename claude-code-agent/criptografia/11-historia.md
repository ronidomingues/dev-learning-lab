# 11 · História: como chegamos até aqui

**Nível:** iniciante · **Última atualização:** 19/08/2026

História de criptografia não é enfeite. Quase toda decisão estranha nos
sistemas de hoje — por que o TLS tem cinco versões, por que o RSA usa
preenchimento, por que existe um padrão chamado 3DES — só faz sentido quando
se sabe qual problema, em que ano, forçou aquela escolha.

---

## Linha do tempo em uma tela

```
-1900 ┤ hieróglifos não padronizados no Egito (primeiro registro de escrita alterada de propósito)
 -500 ┤ cítala espartana (transposição)
  -58 ┤ cifra de César
  850 ┤ al-Kindi descreve a ANÁLISE DE FREQUÊNCIA — a primeira criptanálise
 1467 ┤ Alberti: cifra polialfabética
 1553 ┤ Bellaso, depois atribuída a Vigenère: "le chiffre indéchiffrable"
 1863 ┤ Kasiski quebra Vigenère publicamente
 1883 ┤ Kerckhoffs publica os seis princípios
 1917 ┤ Vernam: one-time pad
 1919 ┤ patente da Enigma
 1932 ┤ Rejewski (Polônia) quebra a Enigma matematicamente
 1939 ┤ Bletchley Park, Turing, as "bombas"
 1945 ┤ Shannon escreve a teoria matemática da criptografia (publicada em 1949)
 1976 ┤ Diffie-Hellman: chave pública. O ponto de virada.
 1977 ┤ RSA · DES vira padrão federal americano
 1985 ┤ curvas elípticas (Koblitz e Miller, independentemente)
 1991 ┤ PGP (Zimmermann) · início das "crypto wars"
 1994 ┤ Shor: algoritmo quântico que quebra RSA e DH
 1995 ┤ SSL 3.0
 1997 ┤ concurso do AES
 1999 ┤ TLS 1.0
 2001 ┤ Rijndael vira AES
 2004 ┤ Wang quebra MD5 na prática
 2008 ┤ Bitcoin (aplicação em massa de hash e assinatura)
 2013 ┤ revelações de Snowden; suspeita sobre o Dual_EC_DRBG
 2014 ┤ Heartbleed · ChaCha20-Poly1305 no Chrome
 2016 ┤ NIST abre o concurso pós-quântico · Signal vira o padrão de E2EE
 2018 ┤ TLS 1.3 (RFC 8446)
 2022 ┤ SIKE, finalista pós-quântico, é quebrado num laptop em 1 hora
 2024 ┤ FIPS 203/204/205: ML-KEM, ML-DSA, SLH-DSA (13/08/2024)
 2025 ┤ HQC escolhido como reserva (11/03/2025) · OpenSSL 3.5 com PQC nativo (08/04/2025)
 2026 ┤ >50% do tráfego humano da Cloudflare com acordo pós-quântico (abr/2026)
```

---

## 1. Antes de 1900: esconder era um ofício, não uma ciência

**Cítala espartana (séc. V a.C.)** — uma tira de couro enrolada num bastão de
diâmetro específico; escrita ao longo do bastão, desenrolada vira letras
embaralhadas. É **transposição**: as letras são as mesmas, muda a ordem.

**Cifra de César (séc. I a.C.)** — deslocamento fixo do alfabeto. É
**substituição monoalfabética**: cada letra vira sempre a mesma outra.

**Al-Kindi (c. 850, Bagdá)** — o marco real. No *Manuscrito sobre a decifração
de mensagens criptográficas*, descreve a **análise de frequência**: em
português, o "a" e o "e" aparecem muito mais que o "z". Numa substituição
monoalfabética, a letra mais frequente do criptograma é, provavelmente, a
letra mais frequente do idioma. Isso quebrou, de uma vez, mil anos de cifras.

> **Lição que atravessa o curso:** al-Kindi mostrou que a cifra vaza
> **estatística** do texto claro. Toda a criptografia moderna é construída para
> que o criptograma pareça ruído — indistinguível de bytes aleatórios. É a
> mesma lição do ECB no
> [exemplo 2](06-exemplos.md#2--por-que-o-modo-ecb-é-proibido).

**Vigenère (1553/1586)** — usa uma palavra-chave que muda o deslocamento a
cada letra. Ficou 300 anos com fama de indecifrável, até **Kasiski** (1863)
notar que repetições no criptograma revelam o comprimento da chave — e que
então basta resolver *n* cifras de César.

**Kerckhoffs (1883)** — ver [10-fundamentos.md](10-fundamentos.md#7-o-princípio-de-kerckhoffs-e-a-segurança-por-obscuridade).

---

## 2. 1917–1945: a criptografia vira máquina, e depois matemática

**One-time pad (Vernam, 1917; Mauborgne acrescenta a aleatoriedade)** — chave
aleatória, do mesmo tamanho da mensagem, usada **uma única vez**. É o único
esquema com **segurança perfeita provada** (Shannon, 1949). E é quase inútil:
a chave é tão grande quanto a mensagem, o que só transfere o problema. Quando
a regra do "uma única vez" foi violada pelos soviéticos, o projeto **VENONA**
americano decifrou milhares de mensagens — a prova prática de que reutilizar
keystream é fatal (a mesma matemática do
[exemplo 5](06-exemplos.md#5--reuso-de-nonce-explorado-na-prática)).

**Enigma (1919–1945)** — rotores que mudam a substituição a cada tecla.
Espaço de configuração enorme (~10²³), mas com duas fraquezas fatais: o
refletor garantia que **nenhuma letra jamais virava ela mesma**, e havia
padrões previsíveis no tráfego militar (*cribs*, como a saudação e o boletim
meteorológico diário). Rejewski, na Polônia, atacou matematicamente já em 1932;
Bletchley Park industrializou o ataque a partir de 1939.

Três lições ainda vivas:

- **Texto claro previsível é munição.** Hoje isso reaparece como ataque de
  texto claro escolhido — e é por isso que a segurança moderna exige
  resistência a IND-CPA.
- **Erro de operador quebra sistema bom.** Chaves repetidas, mensagens
  padronizadas, saudações fixas.
- **A restrição "nenhuma letra vira ela mesma" parecia uma qualidade** e era
  um vazamento. Qualquer estrutura que o criptograma revele é exploração
  potencial.

**Shannon (1945/1949)** — *Communication Theory of Secrecy Systems* funda o
campo como ciência: define sigilo perfeito, prova que o one-time pad o atinge
e que exige chave do tamanho da mensagem, e formula **confusão** (relação
complexa entre chave e criptograma) e **difusão** (um bit do claro afeta muitos
bits do cifrado). AES e ChaCha20 são, literalmente, engenharia dessas duas
ideias.

---

## 3. 1976–1978: os três anos que criaram o mundo atual

**Diffie & Hellman, "New Directions in Cryptography" (1976).** Duas ideias
novas: acordo de chaves em canal público e a *noção* de assinatura digital.
Resolveram o problema de distribuição de chaves que travava a criptografia
havia dois mil anos.

Nota histórica que corrige o crédito: **James Ellis, Clifford Cocks e Malcolm
Williamson**, do GCHQ britânico, chegaram às mesmas ideias entre 1969 e 1974
— Cocks descreveu o equivalente ao RSA em 1973. Estava tudo classificado até
**1997**. É o argumento mais forte contra pesquisa secreta: 20 anos de
descoberta desperdiçados socialmente.

**RSA (Rivest, Shamir e Adleman, 1977).** A primeira realização prática de
cifragem e assinatura de chave pública. Baseado em fatoração de inteiros
grandes. Detalhes matemáticos em [17-chave-publica-rsa.md](17-chave-publica-rsa.md).

**DES (1977).** Padrão federal americano, derivado do Lucifer da IBM, com
intervenção da NSA em dois pontos: as S-boxes foram alteradas (motivo não
explicado à época) e a chave foi **reduzida de 128 para 56 bits**.

Décadas depois, a história se inverteu de forma instrutiva: em 1990, Biham e
Shamir publicaram a **criptanálise diferencial**, e descobriu-se que as S-boxes
alteradas pela NSA eram **mais resistentes** a ela — a agência conhecia a
técnica desde os anos 1970 e a manteve secreta. Ou seja: a NSA fortaleceu o
algoritmo contra um ataque desconhecido do público **e** enfraqueceu a chave
para conseguir quebrá-lo por força bruta. Em 1998, a EFF construiu o *Deep
Crack* por US$ 250 mil e quebrou uma chave DES em 56 horas.

> Essa ambiguidade — a mesma agência fortalecendo e enfraquecendo — é o motivo
> pelo qual a comunidade criptográfica trata recomendações governamentais com
> ceticismo estruturado, e o motivo pelo qual **curvas de origem transparente**
> (Curve25519) ganharam preferência sobre as curvas do NIST, cujos parâmetros
> vêm de sementes nunca explicadas.

---

## 4. 1985–2001: curvas, concursos e o padrão que ficou

**Curvas elípticas (1985)** — Koblitz e Miller, independentemente, propõem
usar o grupo de pontos de uma curva elíptica. A vantagem é dramática: 256 bits
de curva ≈ 3072 bits de RSA. Levaram ~20 anos para virar padrão, por patentes
(a Certicom detinha várias) e conservadorismo.

**Crypto wars (1991–2000)** — o governo americano tratava criptografia forte
como munição, restringindo exportação a 40 bits. Zimmermann publicou o PGP em
1991 e foi investigado criminalmente por três anos. O código-fonte foi
exportado impresso em livro, protegido pela Primeira Emenda. Em 1993 veio a
proposta do **Clipper Chip**, com chave depositada com o governo; morreu
quando Matt Blaze mostrou, em 1994, que seu mecanismo de custódia podia ser
burlado.

O legado técnico das crypto wars durou décadas: as cifras "de exportação"
ficaram no código do OpenSSL e do TLS, e ressurgiram como as vulnerabilidades
**FREAK** e **Logjam** — em **2015**, vinte anos depois.

> **Isto é história repetindo-se agora.** O debate sobre acesso legal ao
> conteúdo cifrado voltou em 2020–2026, na União Europeia (regulamento de
> "chat control"), no Reino Unido (Online Safety Act) e na Austrália. O
> argumento técnico não mudou: não existe porta dos fundos que só o "lado
> bom" atravesse; ver [75-armadilhas.md](75-armadilhas.md).

**Concurso do AES (1997–2001)** — o NIST fez o oposto do processo do DES:
chamada pública, 15 candidatos, análise aberta por três anos, conferências,
critérios publicados. Venceu o **Rijndael**, de dois belgas, Joan Daemen e
Vincent Rijmen. O processo virou o modelo de tudo depois: SHA-3 (2007–2012),
CAESAR (AEAD, 2013–2019), Password Hashing Competition (2013–2015) e o
concurso pós-quântico (2016–2024).

---

## 5. 2004–2017: a queda dos hashes

| Ano | Evento |
|---|---|
| 2004 | Xiaoyun Wang apresenta colisões em MD5 na CRYPTO; a plateia aplaudiu de pé |
| 2005 | Wang publica ataque a SHA-1 em 2⁶⁹ (abaixo dos 2⁸⁰ teóricos) |
| 2008 | Sotirov *et al.* forjam um **certificado de CA válido** explorando MD5 |
| 2012 | o malware **Flame** usa uma colisão MD5 inédita para se passar por atualização da Microsoft |
| 2017 | **SHAttered**: Google e CWI produzem duas PDFs diferentes com o mesmo SHA-1 |
| 2020 | colisão de prefixo escolhido em SHA-1 por ~US$ 45 mil de computação |

A lição operacional: entre "ataque teórico publicado" e "ataque prático
barato" passaram-se **13 anos para o MD5** e **15 para o SHA-1**. Esse é o
prazo real de migração — e é por isso que, quando surge um ataque teórico, a
resposta certa não é "ainda não é prático", é "comece a migrar".

---

## 6. 2013–2018: Snowden, a reação e o TLS 1.3

As revelações de 2013 tiveram três efeitos técnicos duradouros:

1. **Suspeita concreta de sabotagem.** O gerador **Dual_EC_DRBG**, padronizado
   pelo NIST, tinha uma estrutura que permitia porta dos fundos se quem
   escolheu as constantes conhecesse um valor secreto. Havia suspeita desde
   2007 (Shumow e Ferguson); em 2013 vieram indícios de pagamento da NSA à RSA
   Security para torná-lo o padrão do BSAFE. Foi retirado em 2014.
2. **Cifragem por padrão.** HTTPS deixou de ser exceção. Let's Encrypt (2015)
   tornou o certificado gratuito e automatizado; a fração de tráfego cifrado
   saltou de ~30% para mais de 95%.
3. **TLS 1.3 (2018)** — projetado com desconfiança: só cinco suítes, todas
   AEAD; sigilo futuro obrigatório; RSA para troca de chaves removido;
   renegociação removida; compressão removida; handshake em 1-RTT.
   **Retirar coisas foi a maior contribuição de segurança do protocolo.**

Nesse período consolidou-se também o **ChaCha20-Poly1305**: o Google levou-o
ao Chrome em 2014 porque celulares Android sem instrução de AES sofriam com
AES-GCM. Ganho técnico de um lado, diversidade de outro — deixar de depender
de uma única cifra.

---

## 7. 1994–2026: a ameaça quântica sai do papel

**1994** — Peter Shor mostra que um computador quântico fatoraria inteiros e
resolveria logaritmos discretos em tempo polinomial. Em uma tacada: RSA, DH,
DSA e curvas elípticas caem. AES e SHA-2 sobrevivem, com margem reduzida pelo
algoritmo de Grover.

**2016** — o NIST abre a chamada pós-quântica. 82 submissões.

**2022** — o **SIKE**, finalista baseado em isogenias, é quebrado por Castryck
e Decru: **uma hora, num laptop de núcleo único**. Foi um choque saudável — o
lembrete de que "sobreviveu à primeira rodada" não é sinônimo de "seguro". É a
razão principal de a recomendação atual ser **híbrida**.

**13/08/2024** — publicados FIPS 203 (ML-KEM), 204 (ML-DSA) e 205 (SLH-DSA).

**11/03/2025** — HQC escolhido como KEM de reserva, com base matemática
distinta (códigos corretores em vez de reticulados).

**08/04/2025** — OpenSSL 3.5 LTS traz PQC nativo e prefere `X25519MLKEM768`.

**Abril de 2026** — a Cloudflare informa que mais da metade do tráfego humano
que atende já usa acordo de chaves pós-quântico. De ~2% em 2024 a >50% em dois
anos: uma das curvas de adoção mais rápidas da história da criptografia.

Estado detalhado em [65-estado-da-arte.md](65-estado-da-arte.md).

---

## 8. O que a história ensina, em cinco frases

1. **Todo algoritmo tem prazo de validade.** DES durou 21 anos como padrão;
   MD5, ~13 anos até a colisão prática. Projete para trocar.
2. **Processo aberto vence processo secreto.** AES e SHA-3 sobreviveram; A5/1,
   Crypto-1 e CSS caíram assim que foram examinados.
3. **A migração leva de 10 a 20 anos.** Comece quando o ataque é teórico, não
   quando é prático.
4. **O elo fraco é operacional.** Enigma caiu por procedimento; VENONA, por
   reuso de chave; a maior parte dos incidentes de hoje, por gestão de chaves.
5. **Restrições políticas viram vulnerabilidades técnicas décadas depois.**
   FREAK e Logjam, em 2015, são filhos diretos da política de exportação de
   1992.

---

## Autoteste

1. O que al-Kindi descobriu, e qual princípio moderno descende disso?
2. Por que o one-time pad é perfeitamente seguro e ainda assim quase inútil?
   O que foi o VENONA?
3. Cite as duas intervenções da NSA no DES e explique por que elas apontam em
   direções opostas.
4. Quem inventou a criptografia de chave pública, e por que a resposta tem
   duas versões?
5. Quanto tempo se passou entre o primeiro ataque teórico ao SHA-1 e a
   primeira colisão prática? O que isso implica para decisões de migração?
6. Cite três coisas que o TLS 1.3 **removeu**, e por quê.
7. O que aconteceu com o SIKE em 2022, e como isso justifica a criptografia
   híbrida de hoje?
8. Como as restrições de exportação dos anos 1990 produziram vulnerabilidades
   em 2015?

---

**Anterior:** [10-fundamentos.md](10-fundamentos.md) ·
**Próximo:** [12-criptografia-simetrica.md](12-criptografia-simetrica.md)
