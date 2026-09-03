# 14 · A assinatura por dentro — HMAC, RSA, ECDSA, EdDSA

> Nível: intermediário a avançado · Atualizado em 14/08/2026
> Este arquivo ensina a criptografia necessária **do zero**. Não é pré-requisito
> saber criptografia para lê-lo.

---

## 14.1 · O problema que uma assinatura resolve

Você entrega um papel a alguém e essa pessoa devolve depois. Como saber se ela não
escreveu nada no meio do caminho?

Três respostas, em ordem crescente de poder:

| Mecanismo | Garante | Não garante |
|---|---|---|
| **Checksum / CRC32** | detecta erro **acidental** | nada contra quem quer alterar de propósito — é fácil ajustar o CRC |
| **Hash criptográfico** (SHA-256) | detecta alteração, se o hash chegar por canal confiável | nada, se o hash viaja junto — o atacante recalcula |
| **MAC / assinatura** | detecta alteração **mesmo com tudo junto** | confidencialidade |

A diferença decisiva: um MAC ou uma assinatura envolve uma **chave**. Sem ela, não dá
para recalcular. É por isso que a assinatura pode viajar dentro do próprio token.

---

## 14.2 · Hash criptográfico, em cinco minutos

Uma função de hash pega uma entrada de qualquer tamanho e devolve uma saída de
tamanho fixo.

```bash
echo -n "oi" | sha256sum
# 9be36ba6a3b31e1b4e4ce1e1eb0f5a1c8b1e35c6a1b8e0f7e2c... (32 bytes em hex)
echo -n "Oi" | sha256sum
# saída completamente diferente
```

Três propriedades a exigir de uma função de hash **criptográfica**:

1. **Resistência à pré-imagem** — dado o hash, é inviável achar uma entrada que o
   produza.
2. **Resistência à segunda pré-imagem** — dada uma entrada, é inviável achar outra
   com o mesmo hash.
3. **Resistência à colisão** — é inviável achar *qualquer* par de entradas com o
   mesmo hash.

"Inviável" tem número: para SHA-256, achar uma colisão exigiria cerca de 2^128
operações (ataque do aniversário). Para dimensionar: se cada átomo da Terra fosse um
computador fazendo um bilhão de tentativas por segundo desde o Big Bang, ainda
faltaria muito.

**SHA-1 já não tem a terceira propriedade.** Colisão real demonstrada em 2017
(SHAttered, Google + CWI). Por isso `alg` com SHA-1 não existe no JOSE — decisão
acertada de projeto.

---

## 14.3 · HMAC — a família HS***

**HMAC** = *Hash-based Message Authentication Code*. O caminho ingênuo seria
`hash(segredo || mensagem)`, e ele é **quebrado**: funções tipo Merkle–Damgård
(SHA-256 inclusive) permitem **extensão de comprimento** — quem tem o hash consegue
calcular o hash de `mensagem || extra` sem conhecer o segredo.

O HMAC (RFC 2104) resolve com dois passes e duas máscaras:

```
HMAC(K, M) = H( (K ⊕ opad) || H( (K ⊕ ipad) || M ) )

  ipad = 0x36 repetido até o tamanho do bloco
  opad = 0x5c repetido até o tamanho do bloco
```

O hash interno esconde a estrutura; o externo impede a extensão.

**Em JWS:**

```
assinatura = HMAC-SHA256( chave, ASCII(base64url(cab) || '.' || base64url(payload)) )
```

```bash
printf '%s' "$H.$P" | openssl dgst -sha256 -hmac "segredo-de-teste-com-32-bytes-ok" -binary \
  | openssl base64 -A | tr '+/' '-_' | tr -d '='
```

**A propriedade que define o HMAC:** é **simétrico**. A mesma chave assina e
verifica. Quem pode verificar, pode forjar.

**Tamanho da chave.** A RFC 7518 §3.2 exige chave de pelo menos o tamanho da saída:
32 bytes para HS256. **De aleatoriedade real**, não de senha digitada.

```bash
openssl rand -base64 32     # ✅
# "minha-empresa-2026"      # ❌ ~40 bits de entropia; quebrável offline em minutos
```

Por que "offline" é a palavra perigosa: quem tem **um** token seu tem um par
(mensagem, MAC). Pode testar bilhões de segredos por segundo na própria GPU, sem
tocar no seu servidor, sem gerar log, sem disparar limite de tentativas. Existem
ferramentas prontas para isso (`hashcat` modo 16500, `jwt_tool`). Se o segredo for
uma palavra de dicionário, ele cai em segundos.

**Verificação em tempo constante.** Comparar MACs com `===` vaza informação de tempo:
um laço que para no primeiro byte diferente demora mais quanto mais bytes acertar. Em
rede local, com muitas amostras, isso permite reconstruir o MAC byte a byte.

```js
crypto.timingSafeEqual(esperado, recebido)   // ✅
esperado === recebido                        // ❌
```

> **Ressalva honesta:** o ataque de temporização contra HMAC em rede pública é
> difícil na prática (o ruído de rede domina). Mas custa uma linha evitá-lo, e o
> mesmo padrão se aplica a comparações onde o ataque é fácil (tokens de API em
> processo local). Faça sempre.

---

## 14.4 · Criptografia assimétrica, em cinco minutos

O salto conceitual: **duas chaves matematicamente ligadas**, tais que o que uma faz,
só a outra desfaz — e conhecer uma não permite calcular a outra.

- **Chave privada** — assina. Nunca sai de casa.
- **Chave pública** — verifica. Pode ir num outdoor.

Isso muda a arquitetura inteira:

```
        HMAC (simétrico)                 Assimétrico
   ┌─────────────────────┐        ┌──────────────────────┐
   │ emissor: segredo S  │        │ emissor: privada     │
   │ serviço A: segredo S│◄─todos │ serviço A: PÚBLICA   │
   │ serviço B: segredo S│  podem │ serviço B: PÚBLICA   │
   │ serviço C: segredo S│  forjar│ serviço C: PÚBLICA   │
   └─────────────────────┘        └──────────────────────┘
                                   só o emissor pode emitir
```

**Ganha-se também o não repúdio.** Com HMAC, se um token indevido aparece, o emissor
pode alegar que qualquer um dos verificadores o fabricou — e estaria dizendo a
verdade. Com assinatura assimétrica, só quem tem a privada poderia. Em contexto
regulado (financeiro, saúde), isso pode ser exigência legal.

---

## 14.5 · RSA — a família RS*** e PS***

**Sobre o que a segurança repousa:** multiplicar dois primos grandes é fácil;
fatorar o produto de volta é inviável.

```
n = p × q          (p e q primos de ~1024 bits cada, para n de 2048 bits)
assinar:  s = m^d mod n     (d = expoente privado)
verificar: m = s^e mod n    (e = expoente público, quase sempre 65537)
```

**Nunca se assina a mensagem direta.** Assina-se o hash, depois de um
**preenchimento** (*padding*) que impede uma família de ataques algébricos:

| `alg` | Padding | Nota |
|---|---|---|
| `RS256` | PKCS#1 v1.5 | o mais usado; **sem prova de segurança formal**, mas sem ataque prático conhecido no uso de assinatura |
| `PS256` | RSA-PSS | probabilístico, **com prova de segurança**. Tecnicamente melhor |

**Opinião profissional:** PS256 é a escolha melhor e quase ninguém usa, porque RS256
já estava em todo lugar quando o PSS ficou disponível. Não vale brigar por isso numa
migração — vale escolher ES256, que resolve o problema de tamanho ao mesmo tempo.

**O preço do RSA:** a assinatura tem o tamanho da chave. Chave de 2048 bits → **256
bytes** → 342 caracteres no token. Uma chave de 4096 bits dobra isso.

**Por que quase todo provedor grande usa RS256 assim mesmo:** interoperabilidade.
Google, Microsoft e Auth0 precisam funcionar com bibliotecas de 2010 em servidores
corporativos que ninguém atualiza. RSA é o que todo mundo suporta.

---

## 14.6 · ECDSA — a família ES***

**Sobre o que repousa:** dado um ponto `G` numa curva elíptica e o ponto `Q = k·G`,
achar `k` é inviável (problema do logaritmo discreto em curva elíptica).

A vantagem é de **tamanho de chave**:

| Segurança equivalente | RSA | Curva elíptica |
|---|---|---|
| 112 bits | 2048 bits | 224 bits |
| **128 bits** | **3072 bits** | **256 bits (P-256)** |
| 192 bits | 7680 bits | 384 bits |

Uma chave P-256 dá a mesma segurança de uma RSA de 3072 bits com **12× menos bits**.

**Formato da assinatura — a pegadinha nº 1 de interoperabilidade.** ECDSA produz dois
números, `r` e `s`. Há duas formas de os representar:

| Formato | Como é | Onde aparece |
|---|---|---|
| **DER** | sequência ASN.1, tamanho variável (~70–72 bytes) | padrão do OpenSSL, de Java, de Go |
| **P1363** (`r‖s` cru) | 64 bytes fixos para P-256 | **o que o JWS exige** |

Se você assinar com uma API que devolve DER e colocar no token, **nenhuma outra
biblioteca valida**. Em Node:

```js
crypto.sign('sha256', dados, { key, dsaEncoding: 'ieee-p1363' })   // ✅ 64 bytes
crypto.sign('sha256', dados, key)                                   // ❌ DER
```

O [projeto-modelo](07-projeto-modelo/src/jwt.js) usa `ieee-p1363` e tem um teste que
falha se a assinatura não tiver exatamente 64 bytes.

**O perigo do ECDSA — o nonce `k`.** Cada assinatura usa um número aleatório `k`. Se
`k` se repetir para duas mensagens diferentes com a mesma chave, **a chave privada é
recuperável por álgebra elementar**. Não é teórico:

- **PlayStation 3, 2010** — a Sony usava `k` fixo. O grupo fail0verflow extraiu a
  chave privada de assinatura de código do console.
- **Carteiras Bitcoin em Android, 2013** — gerador de aleatoriedade defeituoso
  repetiu `k`; chaves privadas foram extraídas e fundos roubados.

A mitigação é o **RFC 6979** (ECDSA determinístico), que deriva `k` do hash da
mensagem e da chave privada, eliminando a dependência do gerador aleatório.
Bibliotecas modernas (OpenSSL 3, Web Crypto) fazem isso ou usam geradores robustos —
mas **implementar ECDSA à mão é uma péssima ideia** por causa disto.

---

## 14.7 · EdDSA — Ed25519

Projetado por Daniel J. Bernstein e outros (2011), padronizado no JOSE pela RFC 8037
(jan/2017). É o estado da arte em assinatura clássica.

**O que resolve, ponto a ponto:**

| Problema | Como o Ed25519 resolve |
|---|---|
| `k` repetido derruba a chave | é **determinístico por projeto** — não há aleatoriedade na assinatura |
| ataque de canal lateral por tempo | operações em **tempo constante** por construção |
| curva com parâmetros suspeitos | curva com **origem justificada publicamente** (*nothing-up-my-sleeve*) |
| validação de ponto esquecida | o formato torna pontos inválidos irrelevantes |
| assinatura grande | 64 bytes, igual ao ES256 |

**Por que não é o padrão, então?** Suporte. Chegou depois; bibliotecas antigas,
HSMs e serviços de KMS podem não oferecer. Em 2026 o suporte é bom em software
moderno (Node ≥ 12, `jose`, Python `cryptography`, Go) e irregular em hardware.

**Recomendação prática:** use `EdDSA` se todos os consumidores o suportam;
`ES256` como padrão seguro; `RS256` quando a interoperabilidade máxima for exigida.

---

## 14.8 · Tabela de decisão

| Situação | Escolha | Por quê |
|---|---|---|
| Monolito: quem assina é quem verifica | `HS256` | mais simples; sem gestão de chave pública |
| Vários serviços verificam | **`ES256`** | separa emissão de verificação; assinatura curta |
| Consumidores fora do seu controle | `RS256` | interoperabilidade máxima |
| Tudo moderno e sob seu controle | `EdDSA` | melhor projeto criptográfico |
| Exigência regulatória de curva grande | `ES384` | — |
| Preparação pós-quântica | ver [65](65-estado-da-arte.md) | ML-DSA (RFC 9964, mai/2026) |
| Qualquer situação | **nunca `none`** | — |

**A pergunta única que decide:** *quem precisa verificar este token?* Se a resposta
não é "somente eu, para sempre", use assimétrico.

**Recomendação profissional, declarada como opinião:** comece com ES256 mesmo quando
HS256 bastaria. Migrar de HMAC para assimétrico depois de 15 serviços compartilharem
o segredo é um projeto de trimestre. Começar assimétrico custa uma tarde.

---

## 14.9 · Como uma assinatura é quebrada — o modelo formal

O padrão de segurança para assinatura é **EUF-CMA**: *Existential Unforgeability
under Chosen Message Attack*.

O jogo:

1. Um desafiante gera um par de chaves e entrega a **pública** ao adversário.
2. O adversário pede assinaturas de quantas mensagens quiser, à escolha dele.
3. O adversário vence se produzir um par (mensagem, assinatura) válido para uma
   mensagem **que nunca pediu**.

Um esquema é EUF-CMA-seguro se nenhum adversário eficiente vence com probabilidade
não desprezível.

Repare no que o modelo **não** cobre — e é aí que moram os ataques reais a JWT:

| O modelo assume | Na prática |
|---|---|
| a chave pública é conhecida e correta | o atacante tenta **trocar a chave** (`jku`, `jwk`, `kid`) |
| o algoritmo é fixo | o atacante tenta **trocar o algoritmo** (`alg: none`, confusão) |
| a mensagem verificada é a mensagem usada | o código pode ler o payload **antes** de verificar |
| a chave privada é secreta | ela vaza em repositório Git, em log, em variável de ambiente |

**Conclusão que vale para todo o assunto:** a criptografia do JWT não é o elo fraco.
Nenhum incidente conhecido com JWT quebrou HMAC-SHA256 ou ECDSA. Todos exploraram o
**contorno** da criptografia — o que está fora do modelo formal. Ver
[20-ataques-e-defesas.md](20-ataques-e-defesas.md) e
[60-teoria-avancada.md](60-teoria-avancada.md).

---

## 14.10 · Os cinco porquês: por que o `alg` fica dentro do token?

**1. Por que o token declara o próprio algoritmo?**
Para que o verificador saiba como verificar sem combinação prévia.

**2. Por que essa autodescrição parecia necessária?**
Porque o JOSE foi projetado para **federação**: um verificador aceita tokens de
emissores que ele não configurou um a um. Sem `alg`, seria preciso um registro
externo de "qual emissor usa qual algoritmo".

**3. Por que isso é um problema de segurança?**
Porque `alg` é **entrada controlada pelo atacante** — quem manda o token escreve o
campo. Deixar a entrada hostil escolher o caminho de verificação é a definição de
confusão de tipo.

**4. Por que não removeram o campo depois de 2015?**
Porque as RFCs 7515–7519 já estavam publicadas e implantadas; o OIDC dependia delas
desde 2014. Remover `alg` quebraria todo token e toda biblioteca existentes. E há um
argumento técnico legítimo: sem `alg`, rotacionar de RS256 para ES256 exigiria
coordenação global simultânea.

**5. Por que a solução é do lado do verificador?**
Porque é o único ponto onde o defensor tem controle total. O verificador sabe quais
algoritmos ele aceita; o token, não. A RFC 8725 §3.1 formaliza:
*"Use Appropriate Algorithms"* — o verificador declara a lista, o `alg` do token é
apenas conferido contra ela.

**Parada legítima:** decisão histórica documentada, com trade-off explícito. A
flexibilidade de federação foi comprada ao preço de uma superfície de ataque
permanente. É defensável, e é a origem de CVEs de bypass de autenticação de 2015 até
2026.

---

## Autoteste

1. Por que um CRC32 não serve como assinatura, mesmo detectando alteração?
2. Por que HMAC não é simplesmente `SHA256(segredo || mensagem)`?
3. Qual é o tamanho mínimo do segredo HS256, e por que uma senha digitada não serve?
4. O que significa "ataque offline" contra um segredo HMAC, e por que ele é grave?
5. Compare o tamanho da assinatura em HS256, ES256, EdDSA e RS256. Qual o impacto no
   tráfego de uma SPA?
6. O que é o formato P1363 e por que ele importa em ES256?
7. O que acontece se o `k` de um ECDSA se repetir? Cite um caso real.
8. Cite três problemas do ECDSA que o Ed25519 resolve por projeto.
9. Enuncie o jogo EUF-CMA. Cite duas coisas que ele **não** cobre e que são a origem
   dos ataques reais a JWT.
10. Por que a solução para a confusão de algoritmo está no verificador, e não no
    formato?
