# 01 · O que é criptografia, para quem nunca ouviu falar

**Nível:** iniciante · **Pré-requisito:** nenhum · **Última atualização:** 19/08/2026

Este arquivo não tem uma única fórmula. Se em algum ponto você encontrar uma
palavra que não foi explicada antes, é um defeito meu — anote e cobre.

---

## 1. O problema, antes da solução

Imagine que você precisa mandar um bilhete para uma amiga do outro lado da
sala. O bilhete passa de mão em mão por seis colegas até chegar. Você não
confia em nenhum dos seis.

Três coisas podem dar errado, e é importante ver que **são três coisas
diferentes**:

1. **Alguém lê o bilhete.** Você queria que só ela lesse.
2. **Alguém altera o bilhete.** Você escreveu "te encontro às 15h" e chega
   "te encontro às 17h".
3. **Alguém escreve um bilhete falso** assinando com o seu nome.

A criptografia é o conjunto de técnicas que resolve esses três problemas —
e é útil separar desde já os nomes, porque o mundo profissional os usa o tempo
todo:

| Problema | Nome técnico | Tradução literal |
|---|---|---|
| Ninguém pode ler | **confidencialidade** (ou sigilo) | segredo |
| Ninguém pode alterar sem ser notado | **integridade** | inteireza |
| Você sabe quem escreveu | **autenticidade** | é mesmo quem diz ser |
| Quem escreveu não pode negar depois | **não repúdio** | não dá para dizer "não fui eu" |

Um erro que custa caro na prática: achar que resolver o primeiro resolve os
outros. Não resolve. Um bilhete embaralhado que ninguém lê ainda pode ser
alterado ao acaso, e o destinatário não tem como saber. Voltaremos a isso.

---

## 2. A primeira ideia que funciona: combinar um segredo antes

Você e sua amiga combinam, no recreio: **cada letra do bilhete anda três casas
no alfabeto**. "OI" vira "RL". Quem intercepta lê "RL" e não entende nada.

Isso é uma **cifra** (do grego *kryptós*, escondido, + *gráphein*, escrever).
Você acabou de reinventar a Cifra de César, usada pelo exército romano no
século I a.C.

Repare na estrutura, porque ela nunca mais muda em 2 000 anos de história:

```
  texto claro  →  [ ALGORITMO com uma CHAVE ]  →  texto cifrado
   "OI"                cifra de César, k=3          "RL"
```

- O **algoritmo** é o método: "ande k casas no alfabeto".
- A **chave** é o segredo: "k = 3".
- O **texto claro** (*plaintext*) é a mensagem original.
- O **texto cifrado** ou **criptograma** (*ciphertext*) é o resultado.

**Por que separar algoritmo de chave?** Porque o algoritmo vaza. Sempre.
Alguém conta, alguém desmonta o aparelho, alguém lê o código-fonte. Se o
segredo estiver no algoritmo, ele acabou. Se o segredo estiver só na chave,
basta trocar a chave.

Essa regra tem nome desde 1883: o **Princípio de Kerckhoffs** — *o sistema não
deve exigir segredo, e deve poder cair nas mãos do inimigo sem inconveniente*.
Ela é o motivo pelo qual os algoritmos que protegem sua conta bancária estão
publicados na internet, de graça, com o código-fonte aberto. Não é descuido.
É o contrário: um algoritmo que ninguém pôde atacar publicamente durante vinte
anos é a única evidência de segurança que existe.

O oposto — esconder o método — tem nome também, e é usado como xingamento:
**segurança por obscuridade**. Toda vez que uma empresa diz "nosso algoritmo
proprietário é secreto e por isso é seguro", a tradução é "ninguém competente
olhou para isto".

> **Por que a Cifra de César não serve hoje?** Porque só existem 25 chaves
> possíveis. Um humano testa todas em dois minutos. O tamanho do espaço de
> chaves é a primeira coisa que se olha numa cifra.

---

## 3. O problema que atormentou a humanidade por 2 000 anos

Você e sua amiga combinaram "k=3" no recreio, cara a cara. Ótimo.

Agora imagine que ela está em Lisboa, você em Belo Horizonte, vocês nunca se
viram, e **tudo o que vocês trocam passa pelo mesmo canal que o adversário
escuta**. Como combinar a chave?

Se você manda a chave pelo canal, o adversário lê a chave. Se você cifra a
chave, precisa de outra chave para isso, e o problema recomeça. Isso é o
**problema da distribuição de chaves**, e ele foi considerado insolúvel por
literalmente dois milênios. Bancos mandavam malotes lacrados. Embaixadas
mandavam diplomatas com maletas algemadas ao pulso. A Marinha americana
distribuía livros de códigos por navio, e um único submarino capturado
comprometia uma frota inteira.

Em 1976, Whitfield Diffie e Martin Hellman publicaram a solução — e ela é tão
contraintuitiva que vale a analogia com calma.

### A analogia das tintas

Você e ela querem chegar a uma mesma cor secreta, conversando aos gritos numa
praça cheia.

1. Aos gritos, vocês combinam uma **cor pública**: amarelo. Todos ouvem.
2. Você escolhe, sem contar a ninguém, uma **cor secreta sua**: vermelho.
   Ela escolhe a dela: azul.
3. Você mistura amarelo + vermelho = laranja. Ela mistura amarelo + azul =
   verde. Vocês gritam essas misturas um para o outro. Todos ouvem
   "laranja" e "verde".
4. Você pega o verde dela e acrescenta seu vermelho. Ela pega seu laranja e
   acrescenta o azul dela. **Os dois chegam ao mesmo marrom.**
5. Quem estava na praça ouviu amarelo, laranja e verde — e não consegue chegar
   ao marrom, porque **separar tintas misturadas é muito mais difícil do que
   misturá-las**.

Esse é o **acordo de chaves Diffie-Hellman**. Não há tintas, há números, e a
operação difícil de desfazer é uma exponenciação em aritmética de relógio (a
mesma aritmética do "são 22h + 5h = 3h"). Mas a estrutura é exatamente essa: um
segredo compartilhado surge do nada, na frente de todo mundo.

Guarde a expressão-chave: **função de mão única** (*one-way function*). Fácil
de calcular, difícil de inverter. Misturar tinta. Quebrar um copo. Multiplicar
dois primos gigantes. Toda a criptografia moderna se apoia nisso.

---

## 4. A segunda grande ideia: o cadeado aberto

Diffie-Hellman resolve "combinar um segredo". Mas há um segundo truque, ainda
mais estranho, chamado **criptografia de chave pública** ou **assimétrica**.

A analogia clássica é o cadeado:

- Você compra um cadeado e uma chave. Você fica com a chave.
- Você espalha **cópias do cadeado aberto** pelo mundo: deixa na portaria,
  publica na internet, manda para desconhecidos.
- Qualquer pessoa pode pegar um cadeado seu, trancar uma caixa e mandar para
  você. **Nem essa pessoa consegue reabrir depois de trancar.**
- Só você, que tem a chave, abre.

O cadeado é a **chave pública**. A chave é a **chave privada**. Elas nascem
juntas, matematicamente ligadas, e a graça é que **conhecer o cadeado não
revela a chave**.

Agora inverta a operação e você ganha a **assinatura digital**:

- Você faz algo na caixa que só quem tem a chave privada consegue fazer.
- Qualquer pessoa com seu cadeado (a chave pública) verifica que foi você.
- Você não pode negar depois: só sua chave privada produziria aquilo.

É assim que seu navegador sabe que está falando com o banco e não com um
impostor, que o Windows sabe que uma atualização veio da Microsoft, e que um
`git commit` pode ser provadamente seu.

> **Onde a analogia do cadeado quebra** (toda analogia quebra, e é importante
> saber onde): um cadeado físico pode ser arrombado com uma marreta, e o
> esforço não depende do tamanho. Na criptografia, cada bit a mais na chave
> **dobra** o esforço do atacante. Uma chave de 256 bits tem mais combinações
> do que átomos existem na Via Láctea, e nenhuma marreta muda isso.

---

## 5. A terceira ideia: a impressão digital de um arquivo

Existe uma operação que não esconde nada e ainda assim é uma das mais usadas:
a **função de hash criptográfico** (às vezes traduzida como "função de
resumo").

Ela pega qualquer coisa — um caractere, um filme de 40 GB — e devolve sempre
um número de tamanho fixo, tipicamente 32 bytes escritos como 64 caracteres
hexadecimais. Esse número é o **hash**, ou **resumo**, ou "impressão digital".

Três propriedades, que valem memorizar:

1. **Determinística**: o mesmo arquivo dá sempre o mesmo hash.
2. **Efeito avalanche**: mudar um único bit muda metade do hash, de modo
   imprevisível.
3. **Mão única**: dado o hash, é inviável descobrir o arquivo.

Para que serve? Para responder "este arquivo é exatamente o mesmo?" sem
precisar do arquivo. É como um download é verificado, como uma senha é
guardada sem ser guardada, como o Git identifica cada versão do seu código, e
como um blockchain amarra blocos uns aos outros.

Você pode ver isso funcionando agora mesmo, sem instalar nada, se estiver no
Linux ou no macOS:

```bash
echo -n "ola" | sha256sum
# 55a9f4f8994b1bbf2058ea38c8efb6c459000814d5f39c087002571639e6230e  -
echo -n "Ola" | sha256sum
# f21d8a4f1f93e8abd047bc92fc4f36be7a1a17da212c3833480466db2f192e6e  -
```

(Saídas reais, executadas em 19/08/2026. Repare: uma única letra maiúscula
muda o resultado inteiro, sem nenhuma semelhança residual.)

---

## 6. Como as três ideias se juntam num cadeado só

Quase todo sistema real usa as três, e nesta ordem:

```
┌─ 1. ACORDO DE CHAVES (assimétrico, lento) ─────────────────┐
│  Diffie-Hellman em curva elíptica: as duas pontas chegam   │
│  a um segredo comum sem nunca transmiti-lo.                │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌─ 2. AUTENTICAÇÃO (assinatura + certificado) ───────────────┐
│  O servidor prova que é o banco, com um certificado        │
│  assinado por uma autoridade em que seu navegador confia.  │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌─ 3. CIFRAGEM DOS DADOS (simétrico, rápido) ────────────────┐
│  Com o segredo comum, cifra-se o tráfego com AES-GCM ou    │
│  ChaCha20-Poly1305, que autentica ao mesmo tempo.          │
└────────────────────────────────────────────────────────────┘
```

Isso tem nome: **criptografia híbrida**. Usa-se o assimétrico (caro, mas
resolve o problema da distribuição) apenas para combinar a chave, e o
simétrico (barato) para o volume de dados. Na sua máquina, medido para este
curso em 19/08/2026: o AES-256-GCM do OpenSSL processa **3,6 GB por segundo**;
uma assinatura RSA-2048 leva **0,6 milissegundo**. Cifrar 1 GB com RSA seria
absurdo — e, tecnicamente, nem é possível: RSA cifra no máximo alguns bytes por
operação.

Cada vez que você abre um site com cadeado no navegador, essa dança acontece
em cerca de 50 milissegundos. Você já usou criptografia dezenas de vezes hoje.

---

## 7. Para que isso serve na sua vida, concretamente

| Você faz isso | Isto está acontecendo |
|---|---|
| Abre um site `https://` | TLS 1.3: acordo X25519, certificado assinado, tráfego em AES-GCM |
| Manda mensagem no WhatsApp ou Signal | Criptografia de ponta a ponta com o Protocolo Signal; o servidor não lê |
| Desbloqueia o celular | A chave que decifra o armazenamento é liberada por um chip seguro |
| Faz `git commit` | SHA-1/SHA-256 identificando cada objeto (e, opcionalmente, assinatura) |
| Paga com o cartão por aproximação | O chip assina uma transação única; o número não basta para clonar |
| Conecta por Wi-Fi WPA3 | Acordo de chaves resistente a dicionário (SAE) |
| Atualiza o sistema operacional | Assinatura do pacote conferida antes de instalar |
| Recebe um PIX | TLS entre bancos, assinatura na mensagem, HSM guardando as chaves |

E, do outro lado da moeda, é criptografia (mal usada, ou usada contra você) o
que faz um *ransomware* tornar seus arquivos irrecuperáveis.

---

## 8. Cinco mal-entendidos que vale desmontar já

**"Criptografia é matemática impossível de entender."**
A ideia central de cada peça cabe em um parágrafo, como você acabou de ver.
O que é difícil é a **análise de segurança** — provar que ninguém consegue
quebrar. Usar corretamente é uma habilidade de engenharia, acessível.

**"Chave maior é sempre mais segura."**
Não. Uma chave RSA de 4096 bits com um gerador de números aleatórios defeituoso
é pior que uma de 2048 bits bem gerada. E 256 bits de curva elíptica equivalem
a ~3072 bits de RSA. Comparar números sem comparar famílias não faz sentido.

**"Eu não tenho nada a esconder."**
Confidencialidade é só um dos quatro objetivos. Você quer **integridade** no
boleto que vai pagar e **autenticidade** na atualização do seu sistema, mesmo
que o conteúdo seja público.

**"Isso é seguro, usa criptografia de nível militar."**
Frase de marketing sem conteúdo. "AES-256" está em qualquer celular desde 2010.
O que decide a segurança é *como* foi usado — modo de operação, gestão de
chaves, aleatoriedade, atualização. É onde 95% das falhas reais acontecem.

**"Computadores quânticos já quebraram tudo."**
Não. Em agosto de 2026, o maior número fatorado por um computador quântico com
o algoritmo de Shor, sem trapaça, ainda é minúsculo. Mas a ameaça é séria e
tem prazo: a estimativa mais recente (Gidney, Google, maio de 2025) fala em
menos de um milhão de qubits ruidosos para quebrar RSA-2048 em menos de uma
semana, e a migração mundial já começou. Detalhes em
[65-estado-da-arte.md](65-estado-da-arte.md).

---

## 9. O que você vai saber fazer ao fim deste curso

- Explicar, sem jargão, o que cada peça faz e por que ela existe.
- Escolher o algoritmo certo para cada problema, e justificar.
- Cifrar arquivos, gerar chaves, assinar e verificar, na linha de comando.
- Ler e escrever código que usa criptografia sem cometer os erros clássicos.
- Entender um handshake TLS 1.3 pacote a pacote.
- Discutir a migração pós-quântica com números e prazos reais.
- Provar por que RSA funciona, e conhecer os limites teóricos do que é
  demonstrável.

---

## Autoteste

1. Quais são os quatro objetivos da criptografia? Dê um exemplo em que você
   quer integridade mas **não** quer confidencialidade.
2. Por que os algoritmos usados pelos bancos são publicados abertamente?
   Como se chama esse princípio e de que ano ele é?
3. Explique, com a analogia das tintas, como duas pessoas combinam um segredo
   gritando numa praça. Que operação faz o papel de "misturar"?
4. Qual a diferença entre a chave pública e a chave privada, e por que
   publicar uma não compromete a outra?
5. Cite três usos de função de hash que não envolvem esconder nada.
6. O que é criptografia híbrida e por que ela existe? Dê o argumento em
   números.
7. Alguém lhe apresenta um produto com "algoritmo proprietário secreto de
   nível militar". Escreva as duas perguntas que você faria.

---

**Próximo:** [02-pre-requisitos.md](02-pre-requisitos.md) —
o que você precisa saber e ter antes de começar a praticar.
