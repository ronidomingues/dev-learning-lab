# 1 · O que é um JWT — para quem nunca ouviu falar

> Nível: iniciante · Sem nenhum jargão · Atualizado em 14/08/2026

---

## O problema, em uma frase

**A internet esquece você a cada clique.**

Não é defeito, não é bug e não vai ser corrigido. É como a web foi projetada, de
propósito, em 1991.

---

## Por que a web esquece

Quando você abre uma página, seu navegador manda um pedido ao servidor, o servidor
responde e — aqui está o ponto — **a conversa acaba ali**. Não fica uma linha
telefônica aberta. O próximo clique é um pedido novo, de um estranho.

Isso tem um nome: o HTTP é *sem estado* (*stateless*). O servidor não guarda memória
de quem falou com ele um segundo atrás.

Faz sentido? Faz muito. Imagine o contrário: um servidor que atende 10 milhões de
pessoas teria de manter 10 milhões de conversas abertas simultaneamente. A web nunca
teria escalado. O esquecimento é a razão de ela funcionar.

Mas cria um problema óbvio:

> Se o servidor esquece você a cada clique, como ele sabe que você já fez login?

---

## A analogia da pulseira do parque

Você chega num parque aquático. Na entrada, mostra o documento, paga, e recebe uma
**pulseira**.

Daí em diante, ninguém no parque pede mais seu documento. Você chega no
tobogã, o funcionário olha a pulseira e libera. Chega na piscina de ondas, mesma
coisa. O funcionário do tobogã não te conhece, não sabe quem você é, não faz ideia
se você pagou — ele só sabe ler a pulseira.

Um JWT é essa pulseira.

Agora repare em três detalhes da pulseira, porque eles são o assunto inteiro:

**1. A pulseira diz coisas.** Está escrito nela: "adulto", "passe VIP", "válida até
18h". O funcionário não precisa ligar para a bilheteria perguntando; a resposta está
no pulso.

**2. A pulseira é difícil de falsificar.** Tem um holograma, uma solda que não dá
para abrir sem rasgar. Qualquer funcionário sabe reconhecer uma falsa, mas nenhum
deles consegue *fabricar* uma verdadeira — só a bilheteria consegue.

**3. Qualquer um pode ler a pulseira.** Inclusive a pessoa ao seu lado na fila. Ela
não é segredo. Ela é **prova**, e prova é uma coisa diferente de segredo.

Guarde esses três pontos:

| Pulseira | JWT |
|---|---|
| diz coisas ("adulto", "VIP", "até 18h") | carrega dados ("usuário 42", "admin", "expira 15h30") |
| tem holograma que só a bilheteria faz | tem assinatura digital que só o servidor de login faz |
| qualquer um lê o que está escrito | **qualquer um lê o conteúdo — ele não é secreto** |

Esse terceiro ponto é o mal-entendido número um sobre JWT, e voltaremos a ele mais
de uma vez.

---

## Como era antes: a alternativa da lista na portaria

Existe outro jeito de resolver o problema, e é mais antigo. Em vez de escrever na
pulseira, o parque te dá uma **ficha com um número**: `48291`. Não diz nada além do
número.

Quando você chega no tobogã, o funcionário liga para a portaria: "chegou aqui a ficha
48291, quem é?". A portaria consulta a lista e responde: "é a Ana, adulta, passe VIP,
válida até 18h".

Isso é a **sessão com cookie**, o jeito que a web usa desde 1994. Funciona muito bem.
E tem duas propriedades que a pulseira não tem:

- **Dá para cancelar na hora.** Se a Ana for expulsa do parque, a portaria risca o
  48291 da lista. No tobogã seguinte, a ficha não vale mais. Instantâneo.
- **Ninguém lê nada na ficha**, porque não há nada escrito nela.

E uma desvantagem: **toda porta precisa de uma linha para a portaria**. Se o parque
tem 300 atrações e um milhão de visitantes, a portaria vira gargalo. E se o parque
tem filiais em outras cidades, cada uma teria de ligar para a matriz.

Aí está a escolha inteira, e ela é honesta dos dois lados:

|  | Ficha com número (sessão) | Pulseira escrita (JWT) |
|---|---|---|
| Verificar custa | uma consulta à portaria | ler e conferir o holograma, ali mesmo |
| Cancelar na hora | trivial | difícil — a pulseira já está no pulso |
| Serve para vários prédios | mal | muito bem |
| O conteúdo é secreto | sim (não tem conteúdo) | **não** |

Quem te disser que JWT é "melhor" que sessão está vendendo alguma coisa. São
ferramentas com formatos de custo diferentes. O arquivo
[21-quando-nao-usar.md](21-quando-nao-usar.md) trata disso inteiro, e a resposta vai
te surpreender: para a maioria dos sistemas, a sessão comum é a escolha certa.

---

## Como um JWT se parece de verdade

Ele é uma tira de texto feia, mais ou menos assim:

```
eyJhbGciOiJFUzI1NiIsInR5cCI6ImF0K2p3dCJ9.eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjE3ODY3MjY5NzZ9.QaTjSAXBDdNnh0v3GHsHt4UUhKUj4R65WZQWNUaz_gqlSgwcQx3N
```

Parece embaralhado. Não está. Repare que existem **dois pontos** dividindo a tira em
três pedaços:

```
eyJhbGciOiJFUzI1NiIsInR5cCI6ImF0K2p3dCJ9  .  eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjE3ODY3MjY5NzZ9  .  QaTjSAXBDd...
└────────── pedaço 1 ──────────┘            └──────────────── pedaço 2 ─────────────────┘              └── pedaço 3 ──┘
      que tipo de pulseira é                          o que está escrito nela                              o holograma
```

Os dois primeiros pedaços são texto comum, apenas reescrito num alfabeto que
sobrevive a viajar dentro de um endereço da web. Qualquer pessoa desembrulha em
segundos. Não acredite em mim — faça:

```bash
# cole o segundo pedaço (entre os dois pontos) no lugar indicado
echo 'eyJzdWIiOiI0MiIsIm5vbWUiOiJBbmEiLCJleHAiOjE3ODY3MjY5NzZ9' | base64 -d
```

Saída:

```json
{"sub":"42","nome":"Ana","exp":1786726976}
```

Está tudo lá, em texto limpo. Nenhuma senha foi pedida, nenhuma chave foi usada.

> **A frase mais importante deste arquivo:**
> **um JWT não esconde nada. Ele só impede que alguém mude o que está escrito.**

Se você colocar o CPF de alguém dentro de um JWT, você publicou o CPF dessa pessoa.
Ele vai aparecer no log do proxy, no histórico do navegador, na ferramenta de
monitoramento. Isso não é uma falha do JWT — é o que ele é.

E o terceiro pedaço, o holograma? Esse sim é matemática. Ele é calculado a partir dos
dois primeiros usando uma chave que só o servidor tem. Mude uma vírgula no pedaço 2 e
o holograma deixa de bater. É isso que faz alguém não conseguir trocar
`"nome":"Ana"` por `"nome":"admin"` e sair mandando no sistema.

---

## Para que serve, na prática

Você usa JWT sem saber, várias vezes por dia:

- **"Entrar com Google"** em qualquer site. O Google te devolve um JWT dizendo "esta
  pessoa é fulano@gmail.com, e eu, Google, garanto". O site confere o holograma do
  Google e te deixa entrar sem nunca ter visto sua senha.
- **Aplicativo de celular falando com o servidor.** O app guarda o token e o manda em
  cada pedido.
- **Microsserviços.** A empresa tem 40 serviços internos; o token emitido no login
  vale nos 40, e nenhum deles precisa consultar o serviço de login.
- **Link de "redefinir senha" que expira em 15 minutos.** O link carrega um token com
  prazo embutido.

---

## Os três mal-entendidos que você já pode evitar

**"JWT é criptografado."** Não. É *assinado*. Assinado significa "à prova de
adulteração"; criptografado significa "ilegível". São coisas diferentes, e o JWT
comum faz só a primeira. (Existe uma variante que cifra, o JWE — ver
[15-criptografia-jwe.md](15-criptografia-jwe.md) —, e você quase nunca vai precisar
dela.)

**"JWT é mais seguro que sessão."** Não. É diferente. Em vários cenários é *menos*
seguro, porque revogar é difícil. Ver [21-quando-nao-usar.md](21-quando-nao-usar.md).

**"JWT elimina o banco de dados."** Quase nunca. Assim que você precisar deslogar
alguém, ou renovar a sessão sem pedir a senha de novo, o estado volta. O
[projeto-modelo](07-projeto-modelo/) mostra exatamente onde ele volta e por quê.

---

## De onde veio o nome

**J**SON **W**eb **T**oken. Pronuncia-se "jóti" em inglês (*jot*), por sugestão da
própria especificação — que diz, em nota de rodapé, que a pronúncia é a mesma da
palavra inglesa *jot*, "anotação breve". Em português, a maioria fala "jota-vê-tê".

Ele foi padronizado em maio de 2015, na RFC 7519. A história de por que ele surgiu
naquele momento específico — e do que ele veio substituir — está em
[11-historia.md](11-historia.md), e vale a leitura: explica várias decisões que hoje
parecem estranhas.

---

## O que vem a seguir

| Se você quer… | Vá para |
|---|---|
| conferir se tem a base necessária | [02-pre-requisitos.md](02-pre-requisitos.md) |
| montar o ambiente | [03-instalacao.md](03-instalacao.md) |
| ver um token nascer na sua tela em 10 minutos | [04-como-comecar.md](04-como-comecar.md) |
| entender os conceitos com precisão | [10-fundamentos.md](10-fundamentos.md) |
| saber se deve mesmo usar JWT | [21-quando-nao-usar.md](21-quando-nao-usar.md) |

---

## Autoteste

1. Por que o HTTP "esquece" quem você é entre um clique e outro, e por que isso é
   uma escolha de projeto e não um defeito?
2. Na analogia do parque, o que corresponde à assinatura digital? E o que
   corresponde à sessão com cookie?
3. Um colega quer guardar o CPF do cliente dentro do JWT "porque está criptografado".
   O que você responde, em uma frase?
4. Cite uma vantagem concreta da sessão com cookie sobre o JWT, e uma do JWT sobre a
   sessão.
5. Um JWT tem três pedaços. Quais são, e qual deles exige uma chave secreta para ser
   produzido?
6. Se alguém trocar `"papel":"usuario"` por `"papel":"admin"` dentro de um JWT, o que
   acontece quando o servidor recebe esse token?
7. Você consegue, com um comando de terminal, ler o conteúdo de um JWT que
   interceptou? Precisa de alguma chave para isso?
