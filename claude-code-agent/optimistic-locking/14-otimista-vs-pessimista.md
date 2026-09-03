# 14 · Otimista vs. pessimista — a escolha, com números

`Nível: intermediário → avançado` · `Atualizado em: 14/08/2026`

A pergunta "qual é melhor?" não tem resposta. A pergunta "qual é melhor **para esta carga**"
tem, e é calculável. Este arquivo dá o cálculo, os regimes onde cada um vence, e as opções
que não são nem uma coisa nem outra.

---

## 1. As duas estratégias, lado a lado

| | Pessimista | Otimista |
|---|---|---|
| Premissa | o conflito vai acontecer | o conflito é raro |
| Mecanismo | **impede** o acesso concorrente | **detecta** a interferência ao gravar |
| Custo no caso comum (sem conflito) | adquirir e liberar lock, sempre | ~zero |
| Custo no caso raro (com conflito) | esperar | refazer |
| Falha típica | deadlock, timeout, fila | *starvation* (a transação longa nunca passa) |
| Suporta janela longa? | **não** (segura recurso) | **sim** |
| Suporta cliente sem estado (HTTP)? | não | **sim** |
| Progresso garantido? | sim (com detecção de deadlock) | **não** — pode retentar para sempre |
| Comportamento sob sobrecarga | fila cresce, latência sobe | trabalho desperdiçado cresce, vazão **cai** |

A última linha é a mais importante e a menos conhecida. Sob contenção extrema:

- o pessimista **degrada** — fica lento, mas continua avançando;
- o otimista **colapsa** — cada transação gasta CPU e é descartada, e a vazão útil pode cair
  a quase zero enquanto a máquina fica 100% ocupada.

É o fenômeno de *thrashing* de OCC. Quem já viu um sistema com 100% de CPU e vazão despencando
sob pico provavelmente estava olhando para isso.

---

## 2. O cálculo

Definições:

- `p` = probabilidade de conflito por tentativa;
- `T` = custo de executar a operação uma vez (CPU, I/O, latência);
- `L` = custo de adquirir e liberar o lock;
- `E` = tempo médio de espera pelo lock, quando há disputa.

**Custo esperado, pessimista:**

```
C_pess = T + L + p·E
```

**Custo esperado, otimista** (número esperado de execuções = `1/(1−p)`):

```
C_otim = T / (1 − p)
```

Igualando, o ponto de virada é onde:

```
T/(1−p)  =  T + L + p·E
```

Com valores plausíveis de sistema web (`T` = 10 ms, `L` = 0,1 ms, `E` = 20 ms):

| `p` | `C_otim` | `C_pess` | Vencedor |
|---|---|---|---|
| 0,1% | 10,01 ms | 10,12 ms | otimista |
| 1% | 10,10 ms | 10,30 ms | otimista |
| 5% | 10,53 ms | 11,10 ms | otimista |
| 10% | 11,11 ms | 12,10 ms | otimista |
| 30% | 14,29 ms | 16,10 ms | otimista |
| 50% | 20,00 ms | 20,10 ms | empate |
| 70% | **33,33 ms** | 24,10 ms | pessimista |
| 90% | **100,00 ms** | 28,10 ms | pessimista |

**O que a tabela revela — e contraria a intuição de muita gente:** o ponto de virada é bem
mais alto do que se costuma supor. Com esses parâmetros, o otimista ganha até ~50% de
conflito. A regra de bolso "use pessimista se houver contenção" está errada na maioria dos
casos; a contenção precisa ser **muito** alta.

**Mas o modelo é otimista com o otimismo.** Ele assume que:

- o custo de refazer é igual ao da primeira execução (**falso** se houver efeitos externos —
  e-mail enviado, cobrança feita, arquivo escrito);
- as tentativas não interferem entre si (**falso**: retentativas aumentam a contenção, o que
  aumenta `p`, o que gera mais retentativas — é realimentação positiva);
- não há limite de tentativas (**falso**: na prática você desiste, e a operação vira erro);
- `p` é constante (**falso**: com N clientes disputando a mesma linha, `p` cresce com N).

Com realimentação, o comportamento real não é a curva suave da tabela: há um **joelho**,
depois do qual a vazão despenca. Por isso a recomendação prática é conservadora:

> **Acima de ~10% de taxa de conflito medida, pare de ajustar a retentativa e mude o
> projeto.** Não é que o OCC deixe de funcionar; é que 10% é o sinal de que o dado está
> modelado errado.

---

## 3. Os regimes, e a decisão

```
taxa de conflito medida
│
│  > 30%   ▓▓▓▓▓  reprojete: delta atômico, partição, fila, CRDT
│                 (nem OCC nem lock resolvem bem)
│
│ 10–30%   ▓▓▓    lock pessimista curto, ou serialização por chave
│
│  1–10%   ▓▓     OCC + retentativa com jitter  ← a maioria dos sistemas
│
│  < 1%    ▓      OCC simples, sem nem precisar de retentativa automática
│
└──────────────────────────────────────────────────
```

E, cruzando com a duração da janela:

| | Janela curta (< 100 ms) | Janela longa (segundos a horas) |
|---|---|---|
| **Conflito raro** | qualquer um serve; **OCC** por simplicidade | **OCC** — é o único que funciona |
| **Conflito frequente** | **lock pessimista** curto, ou fila | **lease** (reserva com prazo) + OCC |

A célula inferior direita é a que gera os projetos mais interessantes: reserva de assento,
edição de documento com "alguém está editando", carrinho com estoque reservado. A resposta
sempre envolve **lease** — ver [`06-exemplos.md` § 13](06-exemplos.md#13--produção-reserva-de-assentos-com-lease--occ).

---

## 4. O terceiro caminho: não ter conflito

A maior parte dos problemas rotulados como "precisamos escolher entre otimista e pessimista"
some quando se reformula o dado. Em ordem de preferência:

### 4.1 Delta atômico

```sql
UPDATE produto SET estoque = estoque - 1 WHERE id = ? AND estoque >= 1;
```

Não há janela. Não há versão. Não há retentativa. Funciona em qualquer taxa de conflito, e é
a resposta certa para **contadores, saldos e estoques**.

Limite: só funciona quando a operação é expressável como delta e a regra de negócio cabe no
`WHERE`. "Debite 10 se o saldo for suficiente" cabe. "Debite 10 se o cliente não estiver
inadimplente há mais de 30 dias e o limite do plano permitir" não cabe — e aí você volta ao OCC.

### 4.2 Partição: um escritor por chave

Se todas as escritas de uma chave passam pela mesma fila/partição/ator, elas são
**serializadas por construção**. É o modelo do Kafka particionado por chave, do modelo de
atores (Akka, Orleans), e do *sharding* por `user_id`.

Ganho: zero conflito, latência previsível.
Custo: a fila vira o gargalo daquela chave, e você precisa lidar com a fila estar cheia,
lenta ou fora do ar. Trocou um problema por outro — às vezes vale muito a pena.

### 4.3 Operações comutativas / CRDT

Se as operações comutam, a ordem não importa e não há conflito a resolver. Contador
incremento-decremento, conjunto com adição, texto com CRDT de sequência (Yjs, Automerge).

Ganho: funciona **offline** e em multi-mestre, coisa que nenhum OCC faz.
Custo: nem toda semântica é expressável ("o saldo não pode ficar negativo" **não** é
comutativa — é uma invariante global, e CRDTs não a garantem sem coordenação adicional).

### 4.4 Reduzir a janela

Trivial e subestimado. Se a janela cai de 300 s para 5 s, a probabilidade de conflito cai
quase 60 vezes (ver [`12`](12-anatomia-do-lost-update.md#4-quanto-custa-a-matemática-da-janela)).
Formas de reduzir:

- salvar campo a campo em vez de formulário inteiro;
- não abrir o formulário de edição até o usuário clicar em "editar";
- carregar dados no cliente e enviar só o *diff*;
- mover a leitura para o mais perto possível da escrita.

---

## 5. Quando o pessimista é claramente a escolha certa

Para não sair deste material achando que otimista é sempre a resposta — não é. Casos em que
o lock pessimista é o certo, sem discussão:

1. **Exclusão mútua real.** "Só uma instância pode rodar este job." Não há como detectar depois
   que dois rodaram; é preciso impedir. Use lock consultivo (`pg_advisory_lock`), lease em
   Redis/etcd, ou eleição de líder.
2. **Contenção alta com transação curta e inteiramente no servidor.** Sequenciador,
   alocação de número de nota fiscal, geração de identificador legalmente sequencial.
   `SELECT ... FOR UPDATE` é mais barato que retentar.
3. **Operações não idempotentes com efeito externo.** Se refazer significa cobrar duas vezes
   e você não tem chave de idempotência, prefira impedir a refazer.
4. **Regras sobre conjuntos** (o *write skew* de [`10`](10-fundamentos.md#21-write-skew-o-buraco-que-ninguém-vê)),
   quando `SERIALIZABLE` não é opção. `SELECT ... FOR UPDATE` sobre a faixa lida resolve.
5. **Quando o usuário precisa saber, antes de começar, que vai conseguir.** "Este documento
   está sendo editado por Ana" é uma informação de produto que o OCC não consegue dar —
   ele só descobre no fim. Aí o certo é um lease visível na interface.

---

## 6. Um erro de leitura que custa caro

Confundir **contenção** com **carga**.

- Um sistema com 50.000 escritas por segundo espalhadas por 10 milhões de linhas tem
  contenção praticamente nula. OCC é perfeito.
- Um sistema com 50 escritas por segundo, **todas na mesma linha**, tem contenção altíssima.
  OCC vai sofrer.

A métrica que importa não é *requests por segundo*; é **escritas por segundo por chave
disputada**. Meça a distribuição, não a média: quase sempre existem poucas linhas quentes
e um oceano de linhas frias, e a política certa pode ser **diferente para cada grupo**.

Um sistema maduro faz exatamente isso: OCC para o caso geral, e um caminho especial (fila,
delta atômico, lease) para as poucas chaves quentes conhecidas.

---

## 7. Tabela de decisão

Para colar na parede.

| Sua situação | Faça isto |
|---|---|
| Formulário web, CRUD comum | OCC com `version` + `If-Match` no HTTP |
| Contador, saldo, estoque | `UPDATE x = x ± n WHERE guarda` — sem versão |
| "Só um pode executar" | lock consultivo / lease / eleição de líder |
| Regra sobre um conjunto de linhas | `SERIALIZABLE` + retentativa em `40001`, ou `FOR UPDATE` no conjunto |
| Reserva com prazo (assento, carrinho) | lease com expiração no `WHERE` + OCC na confirmação |
| Edição colaborativa em tempo real | CRDT ou OT — não OCC |
| Sincronização offline | vector clock ou CRDT |
| Linha quente conhecida (> 30% de conflito) | fila por chave, ou reformule para delta |
| Integração com API de terceiro | `ETag` + `If-Match`, com retentativa e respeito a `Retry-After` |

---

## Autoteste

1. Escreva as duas fórmulas de custo e explique cada termo.
2. Com `T`=10 ms, `L`=0,1 ms, `E`=20 ms, em que `p` aproximado ocorre o empate?
3. Cite três premissas do modelo que são falsas na prática, e o efeito de cada uma.
4. O que é *thrashing* de OCC, e por que ele produz "CPU a 100% com vazão caindo"?
5. Diferencie contenção de carga com um exemplo numérico próprio.
6. Dê dois casos em que o pessimista é claramente melhor, e diga por quê.
7. Por que um CRDT não garante "o saldo não pode ficar negativo"?
8. Sua métrica mostra 25% de conflito numa tabela. Quais são as três primeiras coisas que
   você investiga — e por que "aumentar as tentativas" não está entre elas?
