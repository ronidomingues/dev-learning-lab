# 16 · ORMs e frameworks — a mesma ideia, sete dialetos

`Nível: intermediário` · `Atualizado em: 14/08/2026`

Todo ORM implementa optimistic locking. Todos geram, no fundo, o mesmo `UPDATE ... WHERE
version = ?`. As diferenças estão em **quando** a verificação acontece, **o que** você recebe
para resolver o conflito, e **quais armadilhas** cada um esconde.

O código pronto de cada um está em [`06-exemplos.md`](06-exemplos.md). Aqui está o que os
exemplos não cabem: o comportamento e as pegadinhas.

---

## 1. Comparação de fundo

| | JPA/Hibernate | EF Core | ActiveRecord | Django | SQLAlchemy | TypeORM | Prisma |
|---|---|---|---|---|---|---|---|
| Como se ativa | `@Version` | `[Timestamp]` ou `IsConcurrencyToken()` | coluna `lock_version` | **manual** | `version_id_col` | `@VersionColumn()` | **manual** |
| Implícito? | sim | sim | sim (pelo nome) | não | sim | sim | não |
| Quando verifica | no flush/commit | no `SaveChanges()` | no `save`/`update` | quando você mandar | no flush | no `save` | quando você mandar |
| Exceção | `OptimisticLockException` | `DbUpdateConcurrencyException` | `StaleObjectError` | a sua | `StaleDataError` | `OptimisticLockVersionMismatchError` | a sua |
| Dá o estado do banco? | não (só a entidade sua) | **sim** (`GetDatabaseValuesAsync`) | não | você busca | não | não | você busca |
| Versão sem coluna | `@OptimisticLocking(ALL/DIRTY)` | `IsConcurrencyToken` em qualquer campo | não | não | não | não | não |
| Força versão no pai | `OPTIMISTIC_FORCE_INCREMENT` | manual | `touch` | manual | manual | manual | manual |

**A coluna do EF Core merece destaque:** ele é o único que entrega, de fábrica, os **três**
conjuntos de valores (o que você leu, o que quer gravar, o que está no banco) — o que torna o
merge de três vias direto. Nos outros, você precisa buscar o estado atual à mão.

---

## 2. JPA / Hibernate

### O que acontece de fato

`@Version` faz o Hibernate acrescentar a coluna ao `WHERE` de todo `UPDATE` e `DELETE` da
entidade, e comparar o número de linhas afetadas. Zero linhas → `OptimisticLockException`.

```sql
update conta set saldo=?, version=? where id=? and version=?
```

### As cinco armadilhas

**1. A verificação acontece no flush, não no `setter`.**

```java
tx.begin();
Conta c = em.find(Conta.class, 1L);
c.setSaldo(...);            // <- nada acontece aqui
tx.commit();                // <- É AQUI que pode lançar OptimisticLockException
```

Um `try/catch` em volta do `setSaldo` não pega nada. E, pior: com `@Transactional` do Spring,
o commit ocorre **depois** de o seu método retornar — o `catch` dentro do método também não
pega. Trate no chamador, ou use `TransactionTemplate` explicitamente.

**2. `save()` de entidade *detached* com `version == null` faz INSERT.**

O Spring Data usa a versão para decidir entre `persist` e `merge`. Se você reconstruiu a
entidade a partir de um DTO e esqueceu de copiar a versão, o resultado é um registro
**duplicado**, não uma exceção. É o bug mais caro desta lista, porque não parece um bug de
concorrência.

**3. Versão do pai não muda quando o filho muda.**

Adicionar um item a um pedido não incrementa a versão do pedido. Se a regra de negócio é
sobre o **agregado**, use:

```java
em.lock(pedido, LockModeType.OPTIMISTIC_FORCE_INCREMENT);
```

Isso força o incremento da versão do pai no commit, transformando "dois itens adicionados em
paralelo" num conflito detectável.

**4. `@Version` em `Timestamp` herda todos os problemas de relógio** de
[`13`](13-tokens-de-versao.md#32-timestamp-a-armadilha-mais-popular). Use `long`.

**5. Versão fora do banco.** Se a entidade viaja para o cliente em JSON, a versão precisa
viajar junto e voltar. Muitos DTOs omitem o campo "porque é interno" — e a proteção morre na
fronteira da API. Ver [`17-http-e-apis.md`](17-http-e-apis.md).

### `OptimisticLockType`: ALL vs. DIRTY

Para tabelas legadas sem coluna de versão:

```java
@Entity
@OptimisticLocking(type = OptimisticLockType.DIRTY)
@DynamicUpdate                       // obrigatório junto com DIRTY
public class Cliente { ... }
```

| | `ALL` | `DIRTY` |
|---|---|---|
| `WHERE` gerado | todos os campos | só os que mudaram |
| Falso conflito | muito | pouco |
| Detecta escrita concorrente em outro campo | sim | **não** |
| Tamanho do SQL | grande | pequeno |

`DIRTY` é, na prática, um merge campo a campo implícito: duas pessoas editando campos
diferentes passam as duas. Isso é bom para usabilidade e **não** é serializável — decida com
consciência, não por acidente.

---

## 3. EF Core

O ponto forte é a resolução de conflito. Os três conjuntos:

```csharp
catch (DbUpdateConcurrencyException ex) {
    var entry = ex.Entries.Single();
    var doBanco = await entry.GetDatabaseValuesAsync();   // estado atual
    // entry.OriginalValues -> o que eu li
    // entry.CurrentValues  -> o que eu quero gravar
}
```

Três estratégias, e quando cada uma:

| Estratégia | Código | Quando |
|---|---|---|
| **Última escrita vence** | `entry.OriginalValues.SetValues(doBanco)` e salvar de novo | quando a intenção do usuário não depende do que ele leu |
| **Recusar e informar** | propagar a exceção com os dois estados | edição de conteúdo, formulários |
| **Merge campo a campo** | comparar os três conjuntos propriedade a propriedade | quando campos são independentes |

O detalhe que quase todo mundo erra: **sem `entry.OriginalValues.SetValues(doBanco)`, a
retentativa usa o token velho e falha para sempre.** É a versão .NET do "retentar sem reler".

Sobre tokens no EF Core:

- `[Timestamp]` → `rowversion` do SQL Server. Automático e confiável, mas amarra ao SQL Server.
- `IsConcurrencyToken()` em uma coluna sua → portátil, mas **você** precisa incrementá-la.
- `UseXminAsConcurrencyToken()` (Npgsql) → zero manutenção, com as ressalvas do `xmin`.
- Qualquer propriedade pode ser token: `Property(p => p.Preco).IsConcurrencyToken()` cria uma
  proteção **só sobre o preço**, permitindo edições concorrentes de outros campos.

---

## 4. ActiveRecord (Rails)

Ativação por convenção: crie a coluna `lock_version` e a proteção liga. Nada mais.

```ruby
add_column :contas, :lock_version, :integer, null: false, default: 0
```

Pontos de atenção:

- `update_column` e `update_all` **contornam** a proteção — não passam pelas validações nem
  pelo mecanismo de versão. Isso é útil e perigoso; use conscientemente.
- `touch` incrementa `lock_version`, o que faz `belongs_to ..., touch: true` funcionar como
  um `FORCE_INCREMENT` do JPA para agregados. Efeito colateral útil e pouco documentado.
- A exceção `StaleObjectError` traz `record` e `attempted_action`, mas **não** o estado do
  banco. Para mesclar, faça `record.reload` você mesmo.
- `lock_version` começa em `0`, não em `1`. Numa migração de tabela existente, use
  `default: 0, null: false` e faça o backfill antes de adicionar `null: false`, ou a migração
  trava a tabela.

---

## 5. Django e a virtude do explícito

O Django não tem optimistic locking embutido — e depois de anos usando os dois modelos, acho
que a ausência é uma **vantagem pedagógica**, embora seja um incômodo prático.

```python
n = (Conta.objects
     .filter(pk=conta_id, version=versao_lida)
     .update(saldo=novo, version=F('version') + 1))
if n == 0:
    raise Conflito()
```

Está tudo visível: a guarda, o incremento no banco (`F()` evita a corrida de calcular em
Python) e a checagem do retorno. Ninguém é protegido por acidente e ninguém é surpreendido.

O que **não** fazer no Django:

```python
# ERRADO: lê em Python, soma em Python, grava. Corrida garantida.
conta = Conta.objects.get(pk=1)
conta.saldo -= 10
conta.save()          # UPDATE ... SET saldo = 90  (valor absoluto)
```

```python
# ERRADO por outro motivo: save(update_fields=...) não protege, só reduz o SQL
conta.save(update_fields=['saldo'])
```

`select_for_update()` existe e funciona, mas exige transação e é pessimista — leia
[`14`](14-otimista-vs-pessimista.md) antes de usá-lo por reflexo.

Pacote de terceiro: `django-concurrency` adiciona `IntegerVersionField` e integra com o admin.
Antes de adotar, verifique a data do último lançamento e a compatibilidade com a sua versão
do Django — é um pacote pequeno e a manutenção já oscilou.

---

## 6. Node: TypeORM, Sequelize, Prisma, Drizzle

| Biblioteca | Suporte | Como |
|---|---|---|
| **TypeORM** | nativo | `@VersionColumn()`; a exceção é `OptimisticLockVersionMismatchError`; exige `save()` com `{ version }` explícito em algumas rotas |
| **Sequelize** | nativo | `version: true` nas opções do modelo; lança `SequelizeOptimisticLockError` |
| **Prisma** | **não tem** | `updateMany({ where: { id, version }, data: { ..., version: { increment: 1 } } })` e cheque `count` |
| **Drizzle** | **não tem** | `.update().where(and(eq(t.id, id), eq(t.version, v))).returning()` e cheque o array vazio |
| **Knex / SQL puro** | — | `.where({id, version}).update(...)` devolve o número de linhas |

A ausência no Prisma é frequentemente reclamada. A construção acima é correta e completa;
o incômodo é que `update()` (singular) lança se não encontrar, enquanto `updateMany()` devolve
`count` — então o padrão certo usa a variante "many" mesmo para uma linha, o que confunde
quem lê o código depois. Vale um comentário no código explicando.

---

## 7. GraphQL, gRPC e a fronteira que todo mundo esquece

O padrão se perde ao sair do ORM. Três lugares onde eu já vi a proteção morrer:

**DTO que omite a versão.** O `mapper` de entidade para DTO lista os campos "de negócio" e
deixa `version` de fora porque "é detalhe técnico". A partir daí o cliente não tem o que
devolver, e a camada de aplicação passa a ler-e-gravar sem guarda.

**GraphQL sem contrato de versão.** Uma mutation `updateProduto(id, nome, preco)` não tem onde
pôr a pré-condição. Solução: incluir a versão como argumento **obrigatório** e devolver um
union type de resultado:

```graphql
type Produto { id: ID!, nome: String!, preco: Int!, version: Int! }

union ResultadoAtualizacao = Produto | ConflitoDeVersao

type ConflitoDeVersao {
  versaoEnviada: Int!
  versaoAtual: Int!
  atual: Produto!          # o estado atual, para o cliente mesclar
}

type Mutation {
  atualizarProduto(id: ID!, version: Int!, nome: String, preco: Int): ResultadoAtualizacao!
}
```

Conflito **não é erro** aqui: é um resultado esperado, e modelá-lo no tipo de retorno (em vez
de no array `errors`) obriga o cliente a tratá-lo. Essa é a razão de usar union type.

**gRPC.** Inclua o token no request e devolva `FAILED_PRECONDITION` (código 9) no conflito —
não `ABORTED` (10), que a documentação do gRPC reserva para conflitos de concorrência
resolvíveis por retentativa em nível mais alto. Na prática, muitos serviços usam `ABORTED`
para conflito otimista, o que também é defensável; o importante é **escolher um e documentar**.

---

## 8. Como auditar o seu ORM em 15 minutos

1. **Ligue o log de SQL** (`spring.jpa.show-sql`, `logging.level.Microsoft.EntityFrameworkCore
   .Database.Command=Information`, `DEBUG=knex:query`, `django.db.backends` em DEBUG).
2. Faça uma edição comum e **leia o `UPDATE` gerado**. Existe `AND version = ?` no `WHERE`?
3. Force um conflito: abra dois clientes, edite nos dois, salve nos dois. O segundo dá erro?
4. Veja o que o usuário recebe nesse erro. É uma mensagem útil ou um stack trace?
5. Procure no código as rotas de escrita que **não** passam pelo ORM (SQL cru, `update_all`,
   `updateMany`, jobs em lote, scripts de migração). Essas normalmente não têm guarda nenhuma.

O passo 5 é o que mais rende. A proteção quase sempre existe no caminho principal e some nos
caminhos laterais — importações, correções manuais, jobs noturnos —, que são justamente os que
escrevem em lote e podem apagar muita coisa de uma vez.

---

## Autoteste

1. Em JPA, por que um `try/catch` em volta do setter não pega `OptimisticLockException`?
2. Que bug acontece quando uma entidade *detached* com `version == null` é passada a `save()`?
3. O que `OPTIMISTIC_FORCE_INCREMENT` resolve? Dê um caso concreto.
4. Qual a diferença prática entre `OptimisticLockType.ALL` e `DIRTY`, e qual é serializável?
5. No EF Core, o que acontece se você omitir `entry.OriginalValues.SetValues(doBanco)`?
6. Por que `update_all` do Rails e `updateMany` do Prisma exigem cuidado especial?
7. Como você modela conflito otimista em GraphQL, e por que não como erro?
8. Quais são os cinco passos da auditoria, e qual deles costuma render mais achados?
