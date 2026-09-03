# 01 · O que é optimistic locking, para quem nunca ouviu falar

`Nível: iniciante` · `Sem jargão` · `Atualizado em: 14/08/2026`

---

## A cena

Duas pessoas trabalham no mesmo escritório: Ana e Bruno.

Na gaveta existe **uma única ficha de papel** com os dados de um cliente. Nela está escrito,
entre outras coisas, o telefone: `2222-1111`.

- **09h00** — Ana tira a ficha da gaveta, **fotocopia**, devolve o original e leva a cópia
  para a mesa dela. Vai corrigir o telefone.
- **09h01** — Bruno faz exatamente a mesma coisa. Também leva uma cópia. Vai corrigir o
  endereço.
- **09h20** — Ana volta, escreve na ficha original o telefone novo: `3333-2222`. Guarda.
- **09h35** — Bruno volta. Na cópia **dele**, o telefone ainda é `2222-1111` — era o que
  estava lá quando ele copiou. Ele escreve o endereço novo e, junto, sem perceber,
  copia de volta o telefone velho. Guarda.

**Resultado:** o trabalho da Ana desapareceu. Ninguém errou, ninguém foi avisado, ninguém
recebeu mensagem de erro. O telefone voltou a `2222-1111` e vai continuar assim até alguém
reclamar — provavelmente o cliente, meses depois.

Esse desaparecimento tem nome. Chama-se **atualização perdida** (em inglês, *lost update*).
É o problema mais silencioso e mais caro da computação com dados compartilhados, e é
exatamente ele que o optimistic locking existe para resolver.

---

## As duas maneiras de resolver

### Jeito 1 — trancar a gaveta (pessimista)

Quando Ana pega a ficha, ela **leva o original** e tranca a gaveta. Bruno chega, não consegue
abrir, e espera. Quando Ana devolve, Bruno pega.

Funciona. Mas repare no preço:

- Bruno ficou **parado** 20 minutos sem produzir nada.
- Se Ana sair para almoçar com a ficha na mesa, Bruno para o dia inteiro.
- Se Ana e Bruno pegarem, cada um, uma ficha de que o outro precisa, **os dois travam para
  sempre** esperando um ao outro. Isso tem nome também: *deadlock*, abraço mortal.

Esse é o **bloqueio pessimista** (*pessimistic locking*). Ele parte da suposição de que
o choque **vai** acontecer, e por isso previne antes, sempre, mesmo quando não haveria choque
nenhum.

### Jeito 2 — carimbar a ficha (otimista)

Ninguém tranca nada. Mas a ficha ganha, num canto, um **número de versão**:

```
FICHA DO CLIENTE 42                    versão: 7
telefone: 2222-1111
endereço: Rua A, 100
```

Ana copia a ficha e anota: *"eu li a versão 7"*.
Bruno copia a ficha e anota: *"eu li a versão 7"*.

- **09h20** — Ana volta e diz ao arquivista: *"quero gravar isto, **eu li a versão 7**"*.
  O arquivista confere: a ficha está na versão 7. Bate. Ele grava e **passa para a versão 8**.
- **09h35** — Bruno volta e diz: *"quero gravar isto, **eu li a versão 7**"*.
  O arquivista confere: a ficha está na versão **8**. Não bate. Ele **recusa**:
  *"alguém mexeu depois de você. Pegue a ficha nova e refaça."*

Ninguém esperou. Ninguém travou. E **nada se perdeu**, porque a única escrita que poderia
apagar trabalho alheio foi barrada na hora.

Esse é o **bloqueio otimista** (*optimistic locking*). Ele parte da suposição de que o choque
**raramente** acontece, e por isso não previne nada — só **detecta na hora de gravar** e
manda refazer.

---

## O nome é ruim, e vale saber por quê

"Optimistic locking" é um nome enganoso: **não existe lock nenhum**. Nada é trancado, nada é
reservado, ninguém espera. O nome pegou por oposição a "pessimistic locking", que usa locks
de verdade.

Nomes mais honestos, que você vai encontrar na literatura:

- **controle de concorrência otimista** (*optimistic concurrency control*, OCC) — o termo
  acadêmico, de 1981;
- **detecção de conflito por versão**;
- **compare-and-swap** (comparar e trocar) — o mesmo raciocínio no nível do processador.

Se você guardar uma frase deste arquivo, guarde esta:
**otimista não impede o conflito; otimista impede o dano do conflito.**

---

## Onde você já usou isso sem saber

Você já viu optimistic locking funcionando, provavelmente hoje:

| Situação | O que acontece |
|---|---|
| Google Docs / Notion | Duas pessoas editam; o sistema detecta a divergência e mescla, ou avisa. |
| `git push` recusado | *"Updates were rejected because the remote contains work that you do not have."* É exatamente isto: você leu o commit X, o remoto está em Y, refaça com `git pull`. |
| Wikipédia | *"Conflito de edição: alguém salvou enquanto você escrevia."* |
| Reserva de assento em site de show | Você escolhe a poltrona, alguém confirma antes, e você recebe *"assento indisponível"*. |
| Carrinho de compras de estoque baixo | *"A quantidade mudou desde que você adicionou ao carrinho."* |

Em todos, a mesma estrutura: **ler → trabalhar longe → tentar gravar dizendo o que se leu →
o sistema confere → aceita ou recusa.**

---

## Quando cada jeito é melhor

A escolha não é ideológica, é aritmética. Depende de uma pergunta só:

> **Com que frequência duas pessoas mexem no mesmo dado ao mesmo tempo?**

```
   raro                                                            frequente
   ├───────────────────────────────────────────────────────────────────┤
   OTIMISTA                                                    PESSIMISTA
   (quase nunca refaz;                             (refazer o tempo todo
    não paga espera nenhuma)                        sairia mais caro que esperar)
```

- Cadastro de clientes de uma empresa com 30 funcionários? **Otimista**. A chance de dois
  editarem o mesmo cliente no mesmo minuto é minúscula; travar seria pagar caro por nada.
- Contador de estoque de um produto em promoção de Black Friday, com 5.000 pedidos por
  segundo na mesma linha? **Nem otimista nem pessimista** — aí a resposta certa é outra
  (uma operação atômica de subtração, ou uma fila). Veja [`14`](14-otimista-vs-pessimista.md).

O erro mais comum não é escolher errado: é **não escolher nada** e deixar o *lost update*
acontecendo em silêncio.

---

## Como isso aparece no código, em três linhas

Não precisa entender ainda; é só para você ver que a ideia inteira cabe numa linha de SQL.

```sql
-- Ana leu a versão 7 e quer gravar. O banco só grava se ainda estiver na 7.
UPDATE clientes
   SET telefone = '3333-2222',
       version  = version + 1
 WHERE id = 42
   AND version = 7;          --  <<< esta linha é o optimistic locking inteiro
```

Se a versão já tiver virado 8, o banco atualiza **zero linhas**. Zero linhas é a maneira de
o banco dizer *"alguém chegou antes de você"*. O programa confere esse número e avisa o usuário.

Repare: o banco **não dá erro**. Ele obedece — só que não encontra nada para atualizar.
Quem precisa reparar nas zero linhas é o seu código. Metade dos bugs deste assunto nasce aí.

---

## O preço que se paga

Nada é de graça. O que o otimismo cobra:

1. **Alguém precisa refazer o trabalho.** Se o conflito for comum, a mesma tarefa é feita
   três, quatro vezes. Isso gasta CPU, banda e paciência.
2. **O usuário pode ser interrompido.** *"Alguém editou antes de você"* é uma frase que só
   se pode dizer poucas vezes por dia sem irritar.
3. **Precisa haver um plano para o conflito.** Refazer sozinho? Mesclar automaticamente?
   Mostrar as duas versões lado a lado e deixar a pessoa decidir? Ignorar isso é o que
   transforma uma boa técnica numa má experiência.

---

## O que você deve levar deste arquivo

1. **Lost update** é uma escrita que apaga outra sem avisar ninguém.
2. **Pessimista** previne travando; paga com espera e risco de deadlock.
3. **Otimista** não previne — **detecta na hora de gravar** e manda refazer; paga com retrabalho.
4. A detecção funciona porque você **grava dizendo qual versão leu**, e o sistema confere.
5. Otimista vence quando conflitos são raros — que é o caso da maioria esmagadora dos sistemas.
6. **Zero linhas afetadas é a detecção.** Quem não confere isso não tem proteção nenhuma.

---

## Autoteste

1. Explique *lost update* para alguém sem usar as palavras "banco", "transação" ou "versão".
2. Por que o nome "optimistic locking" é tecnicamente incorreto?
3. Ana leu a versão 7, Bruno leu a versão 7. Bruno grava primeiro. O que acontece com Ana?
4. Cite dois sistemas que você usou esta semana que aplicam a ideia.
5. Dê um exemplo de sistema onde a estratégia otimista seria uma escolha ruim, e diga por quê.
6. Se o banco não dá erro quando a versão não bate, quem detecta o conflito?
7. Qual é o custo pago pela estratégia otimista, e quem paga esse custo?

---

**Próximo:** [`02-pre-requisitos.md`](02-pre-requisitos.md) — o que você precisa saber e ter
antes de continuar. Se quiser ver funcionando primeiro, pule para
[`04-como-comecar.md`](04-como-comecar.md).
