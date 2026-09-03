# 06 · Exemplos — 14 receitas completas

`Nível: iniciante → avançado` · `Atualizado em: 14/08/2026`

Cada exemplo tem **problema → código completo → explicação**. Nada de `...` no meio.

**O que foi executado nesta máquina** (Node v24.18.0, Ubuntu 22.04.5, 14/08/2026):
exemplos **1, 5, 6, 7, 8** — as saídas mostradas são reais.
Os demais estão completos e na sintaxe correta da respectiva tecnologia, mas **não foram
executados aqui** por falta do runtime (PostgreSQL, JDK 21, .NET, Redis, AWS). Onde a saída
é ilustrativa, isso está dito.

| # | Exemplo | Nível | Tecnologia |
|---|---|---|---|
| 1 | [O padrão canônico](#1--o-padrão-canônico) | trivial | SQL / Node |
| 2 | [Distinguir 404 de 409](#2--distinguir-não-existe-de-conflito) | fácil | PostgreSQL |
| 3 | [Sem coluna de versão (dirty check)](#3--sem-coluna-de-versão-versionless) | fácil | SQL |
| 4 | [Delta atômico: quando NÃO usar versão](#4--delta-atômico-quando-não-usar-versão) | fácil | SQL |
| 5 | [Retentativa que converge](#5--retentativa-que-converge) | médio | Node |
| 6 | [Token por hash de conteúdo](#6--token-por-hash-de-conteúdo) | médio | Node |
| 7 | [Merge campo a campo](#7--merge-campo-a-campo-em-vez-de-recusar) | médio | Node |
| 8 | [ETag/If-Match ponta a ponta](#8--etagif-match-ponta-a-ponta) | médio | HTTP / curl |
| 9 | [JPA/Hibernate com `@Version`](#9--jpahibernate-com-version) | médio | Java 21 |
| 10 | [EF Core com `rowversion`](#10--ef-core-com-rowversion) | médio | .NET 10 |
| 11 | [Django e Rails](#11--django-e-rails) | médio | Python / Ruby |
| 12 | [DynamoDB `ConditionExpression`](#12--dynamodb-conditionexpression) | médio | Python / AWS |
| 13 | [**Produção:** reserva de assentos com lease](#13--produção-reserva-de-assentos-com-lease--occ) | avançado | PostgreSQL |
| 14 | [**Produção:** sincronizar catálogo com API de terceiro](#14--produção-sincronizar-com-uma-api-de-terceiro) | avançado | Node / HTTP |

---

## 1 · O padrão canônico

**Problema.** Duas pessoas leem o mesmo registro e gravam. A segunda não pode apagar a primeira.

```sql
-- esquema (PostgreSQL, MySQL, SQLite: idêntico salvo o tipo serial)
CREATE TABLE conta (
  id      INTEGER PRIMARY KEY,
  saldo   INTEGER NOT NULL,
  version INTEGER NOT NULL DEFAULT 1
);
INSERT INTO conta (id, saldo) VALUES (1, 100);
```

```sql
-- Ana lê
SELECT id, saldo, version FROM conta WHERE id = 1;   -- saldo=100, version=1

-- Bruno lê o mesmo
SELECT id, saldo, version FROM conta WHERE id = 1;   -- saldo=100, version=1

-- Ana grava dizendo que leu a versão 1
UPDATE conta SET saldo = 150, version = version + 1 WHERE id = 1 AND version = 1;
-- UPDATE 1   -> aceito, version vira 2

-- Bruno grava dizendo que leu a versão 1
UPDATE conta SET saldo = 200, version = version + 1 WHERE id = 1 AND version = 1;
-- UPDATE 0   -> RECUSADO. Nada foi escrito.

SELECT * FROM conta WHERE id = 1;                    -- saldo=150, version=2
```

O equivalente executável em Node está em [`04-como-comecar.md`](04-como-comecar.md#1-o-menor-programa-que-demonstra-a-ideia), com saída verificada.

**Por que funciona.** A comparação (`version = 1`) e a escrita acontecem no **mesmo comando**.
Não há janela entre conferir e gravar; o banco garante a atomicidade da linha.

---

## 2 · Distinguir "não existe" de "conflito"

**Problema.** `UPDATE 0` acontece por dois motivos completamente diferentes: o registro sumiu
(→ HTTP 404) ou a versão mudou (→ HTTP 412). Tratar os dois igual confunde o cliente.

**Solução ingênua (e correta na maioria dos casos):** um `SELECT` extra **só no caminho de
falha**.

```sql
-- caminho feliz: um comando só
UPDATE conta SET saldo = 150, version = version + 1 WHERE id = 1 AND version = 7;
-- se retornou 0, e SÓ nesse caso:
SELECT version FROM conta WHERE id = 1;
-- 0 linhas  -> 404
-- 1 linha   -> 412, e você já tem a versão atual para devolver
```

**Solução em um comando (PostgreSQL):** CTE modificadora de dados.

```sql
WITH existe AS (
  SELECT version AS v FROM conta WHERE id = 1
), aplicou AS (
  UPDATE conta
     SET saldo = 150, version = version + 1
   WHERE id = 1 AND version = 7
  RETURNING version AS nova
)
SELECT
  (SELECT count(*) FROM existe)  AS registro_existe,
  (SELECT v   FROM existe)       AS versao_atual,
  (SELECT nova FROM aplicou)     AS versao_nova;
```

Interpretação:

| `registro_existe` | `versao_nova` | Resposta |
|---|---|---|
| 0 | `NULL` | `404 Not Found` |
| 1 | `NULL` | `412 Precondition Failed`, devolva `versao_atual` |
| 1 | número | `200 OK`, devolva `versao_nova` |

> **Atenção.** Numa CTE, todas as subconsultas veem o **mesmo instantâneo**; `existe` não
> enxerga o efeito de `aplicou`. É exatamente o que queremos aqui, mas é uma fonte clássica
> de confusão em outras situações.
> Sintaxe específica do PostgreSQL — **não executado nesta máquina**.

---

## 3 · Sem coluna de versão (*versionless*)

**Problema.** A tabela é legada, você não pode alterar o esquema, mas precisa de proteção.

```sql
-- Grava só se TODOS os campos ainda estiverem como você leu.
UPDATE cliente
   SET telefone = '3333-2222',
       endereco = 'Rua B, 200'
 WHERE id = 42
   AND telefone IS NOT DISTINCT FROM '2222-1111'    -- valores lidos
   AND endereco IS NOT DISTINCT FROM 'Rua A, 100';
```

Ou, mais barato, comparando **só os campos que você está mudando** (o que o Hibernate chama
de `OptimisticLockType.DIRTY`):

```sql
UPDATE cliente
   SET telefone = '3333-2222'
 WHERE id = 42
   AND telefone IS NOT DISTINCT FROM '2222-1111';
```

**Trade-off honesto:**

| | Todos os campos (`ALL`) | Só os alterados (`DIRTY`) |
|---|---|---|
| Detecta | qualquer mudança concorrente | só mudança no mesmo campo |
| Falso conflito | muito | pouco |
| Perde escrita? | não | **pode**: se A muda o telefone e B muda o endereço a partir de leituras diferentes, os dois passam — o que costuma ser desejável, mas não é serializável |
| `UPDATE` gerado | enorme, ruim para índice e para log | enxuto |

`IS NOT DISTINCT FROM` em vez de `=` porque `NULL = NULL` é `NULL`, não verdadeiro — e a
comparação inteira falharia em silêncio. No MySQL, o operador é `<=>`. No SQL Server,
não há operador equivalente até 2022: use `EXISTS (SELECT a INTERSECT SELECT b)` ou
`(col = @v OR (col IS NULL AND @v IS NULL))`.

**Nunca** compare colunas de ponto flutuante desse jeito.

---

## 4 · Delta atômico: quando **não** usar versão

**Problema.** Contador de estoque com muita concorrência. Optimistic locking geraria conflito
a cada compra — e conflito **falso**, porque duas baixas de 1 unidade não se contradizem.

```sql
-- ERRADO: cria conflito onde não há
SELECT estoque, version FROM produto WHERE id = 7;         -- estoque=10, version=3
UPDATE produto SET estoque = 9, version = version + 1
 WHERE id = 7 AND version = 3;
```

```sql
-- CERTO: delta relativo, com a regra de negócio na guarda
UPDATE produto
   SET estoque = estoque - 1
 WHERE id = 7
   AND estoque >= 1;
-- 1 linha = vendeu; 0 linhas = acabou o estoque (regra de negócio, não conflito)
```

Com `RETURNING` você ainda descobre quanto sobrou, sem `SELECT` extra:

```sql
UPDATE produto SET estoque = estoque - 1
 WHERE id = 7 AND estoque >= 1
 RETURNING estoque;
```

**A regra.** Pergunte qual é a **intenção** do usuário:

| Intenção | Técnica |
|---|---|
| "o valor deve passar a ser X" (substituição) | **coluna de versão** |
| "aplique esta diferença ao que estiver lá" (delta) | **`UPDATE` relativo com guarda** |

Confundir as duas é o erro conceitual mais comum deste assunto. Ver
[`14-otimista-vs-pessimista.md`](14-otimista-vs-pessimista.md).

---

## 5 · Retentativa que converge

**Problema.** Sob concorrência, a primeira tentativa falha. Você quer transformar o conflito
em latência, não em erro para o usuário.

```javascript
// ex-retry.mjs — executável: node --no-warnings ex-retry.mjs
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
db.exec(`CREATE TABLE carteira (id INTEGER PRIMARY KEY, pontos INTEGER, version INTEGER)`);
db.prepare('INSERT INTO carteira VALUES (1, 0, 1)').run();

class Conflito extends Error { constructor() { super('conflito'); this.name = 'Conflito'; } }

const ler = (id) => db.prepare('SELECT * FROM carteira WHERE id = ?').get(id);

function gravar(id, pontos, versao) {
  const r = db.prepare(
    'UPDATE carteira SET pontos = ?, version = version + 1 WHERE id = ? AND version = ?'
  ).run(pontos, id, versao);
  if (r.changes === 0) throw new Conflito();
}

function comRetentativa(fn, max = 5) {
  for (let i = 0; i < max; i++) {
    try { return { valor: fn(), tentativas: i + 1 }; }
    catch (e) { if (e.name !== 'Conflito' || i === max - 1) throw e; }
  }
}

// Simula interferência: um "outro processo" escreve entre a leitura e a gravação,
// nas duas primeiras tentativas.
let interferir = 2;
const r = comRetentativa(() => {
  const c = ler(1);                                   // <<< RELER faz parte da retentativa
  if (interferir-- > 0) {
    db.prepare('UPDATE carteira SET pontos = pontos + 100, version = version + 1 WHERE id = 1').run();
  }
  gravar(1, c.pontos + 10, c.version);
  return ler(1);
});

console.log('tentativas gastas:', r.tentativas);
console.log('estado final     :', { ...r.valor });
```

**Saída real (14/08/2026):**

```
tentativas gastas: 3
estado final     : { id: 1, pontos: 210, version: 4 }
```

**Leia o resultado com atenção:** `210 = 100 + 100 + 10`. As duas interferências
sobreviveram **e** a sua soma de 10 também. Nada se perdeu. O bloco retentado precisa
**reler** e recalcular a partir do estado novo — se ele usasse `c` da primeira leitura,
o valor final seria 10 e as interferências teriam evaporado.

Versão de produção, com recuo exponencial e *jitter*:
[`07-projeto-modelo/src/retry.js`](07-projeto-modelo/src/retry.js).

---

## 6 · Token por hash de conteúdo

**Problema.** Você expõe um `ETag` público e não quer vazar quantas vezes o recurso foi
escrito. Além disso, quer que **regravar conteúdo idêntico não gere conflito** para os outros.

```javascript
// ex-hash.mjs — executável: node --no-warnings ex-hash.mjs
import { DatabaseSync } from 'node:sqlite';
import { createHash } from 'node:crypto';

const db = new DatabaseSync(':memory:');
db.exec(`CREATE TABLE artigo (id INTEGER PRIMARY KEY, titulo TEXT, corpo TEXT)`);
db.prepare('INSERT INTO artigo VALUES (1, ?, ?)').run('Título', 'Corpo original');

// Serialização CANÔNICA: ordem fixa dos campos, estrutura sem ambiguidade.
// Sem isso, o mesmo conteúdo pode gerar hashes diferentes e tudo vira conflito.
const canonico = (a) => JSON.stringify([a.id, a.titulo, a.corpo]);
const etag = (a) => `"${createHash('sha256').update(canonico(a)).digest('hex').slice(0, 16)}"`;

const ler = (id) => db.prepare('SELECT * FROM artigo WHERE id = ?').get(id);

function gravar(id, campos, etagLido) {
  const atual = ler(id);
  if (!atual) return { status: 404 };
  if (etag(atual) !== etagLido) return { status: 412, etag: etag(atual), atual: { ...atual } };
  db.prepare('UPDATE artigo SET titulo = ?, corpo = ? WHERE id = ?')
    .run(campos.titulo ?? atual.titulo, campos.corpo ?? atual.corpo, id);
  return { status: 200, etag: etag(ler(id)) };
}

const a = ler(1), b = ler(1);
console.log('ETag lido por A:', etag(a));
console.log('A grava:', gravar(1, { corpo: 'Corpo editado por A' }, etag(a)).status);
const rb = gravar(1, { corpo: 'Corpo editado por B' }, etag(b));
console.log('B grava:', rb.status, '-> etag atual', rb.etag);

const c = ler(1);
console.log('regravar conteúdo idêntico:', gravar(1, { corpo: c.corpo }, etag(c)).status,
            '| etag mudou?', gravar(1, { corpo: c.corpo }, etag(c)).etag !== etag(c));
```

**Saída real (14/08/2026):**

```
ETag lido por A: "e1f7fe7062a877cc"
A grava: 200
B grava: 412 -> etag atual "7801bedced92ba80"
regravar conteúdo idêntico: 200 | etag mudou? false
```

**A propriedade que só o hash tem:** gravar exatamente o mesmo conteúdo **não muda o token**,
então não invalida a leitura de mais ninguém. Com contador incremental, cada salvamento inócuo
vira conflito para os outros.

> **Defeito deste código, de propósito.** `ler` → comparar → `UPDATE` são três comandos
> separados: existe uma janela entre a checagem e a escrita. Aqui é seguro porque o Node é
> monothread e o `node:sqlite` é síncrono — nada roda no meio. **Em qualquer sistema real,
> isso é um bug**: coloque os três dentro de uma transação, ou (melhor) **guarde o hash numa
> coluna** e volte ao `WHERE hash = ?` do exemplo 1, que é atômico por construção.
> Reconhecer essa diferença é metade do aprendizado deste assunto.

---

## 7 · Merge campo a campo em vez de recusar

**Problema.** Ana editou o telefone, Bruno editou o endereço. Recusar o Bruno é tecnicamente
correto e **irritante**: as edições não se contradizem.

```javascript
// ex-merge.mjs — executável: node --no-warnings ex-merge.mjs
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
db.exec(`CREATE TABLE cliente (
  id INTEGER PRIMARY KEY, telefone TEXT, endereco TEXT, version INTEGER)`);
db.prepare('INSERT INTO cliente VALUES (1, ?, ?, 1)').run('2222-1111', 'Rua A, 100');

const ler = (id) => ({ ...db.prepare('SELECT * FROM cliente WHERE id = ?').get(id) });

function gravar(id, campos, versao) {
  const cols = Object.keys(campos);
  const r = db.prepare(
    `UPDATE cliente SET ${cols.map((c) => `${c} = ?`).join(', ')}, version = version + 1
      WHERE id = ? AND version = ?`
  ).run(...cols.map((c) => campos[c]), id, versao);
  return r.changes === 1;
}

/**
 * Grava com merge de três vias, o mesmo algoritmo do `git merge`:
 *   base   = o que eu li
 *   meu    = o que eu quero
 *   deles  = o que está no banco agora
 * Conflito REAL só existe quando o mesmo campo mudou dos dois lados para valores diferentes.
 */
function gravarComMerge(id, base, meu) {
  for (let i = 0; i < 5; i++) {
    const deles = ler(id);
    if (gravar(id, meu, base.version)) return { ok: true, tentativas: i + 1 };

    const conflitantes = [];
    const aplicar = {};
    for (const campo of Object.keys(meu)) {
      const mudouAqui  = meu[campo]   !== base[campo];
      const mudouLa    = deles[campo] !== base[campo];
      if (mudouAqui && mudouLa && meu[campo] !== deles[campo]) conflitantes.push(campo);
      else if (mudouAqui) aplicar[campo] = meu[campo];
    }
    if (conflitantes.length) return { ok: false, conflitantes, deles };
    if (Object.keys(aplicar).length === 0) return { ok: true, tentativas: i + 1, nada: true };
    base = deles;                       // rebase: minha nova base é o estado deles
    meu = aplicar;
  }
  return { ok: false, motivo: 'tentativas esgotadas' };
}

// --- cenário 1: campos diferentes -> merge automático
const baseAna = ler(1);
const baseBru = ler(1);
gravar(1, { telefone: '3333-2222' }, baseAna.version);          // Ana grava primeiro
console.log('Bruno (campo diferente):',
  gravarComMerge(1, baseBru, { endereco: 'Rua B, 200' }));
console.log('estado:', ler(1));

// --- cenário 2: mesmo campo, valores diferentes -> conflito real
const b1 = ler(1), b2 = ler(1);
gravar(1, { telefone: '4444-3333' }, b1.version);
console.log('Bruno (mesmo campo):',
  gravarComMerge(1, b2, { telefone: '5555-4444' }));
console.log('estado:', ler(1));
```

**Saída real (14/08/2026):**

```
Bruno (campo diferente): { ok: true, tentativas: 2 }
estado: { id: 1, telefone: '3333-2222', endereco: 'Rua B, 200', version: 3 }
Bruno (mesmo campo): {
  ok: false,
  conflitantes: [ 'telefone' ],
  deles: { id: 1, telefone: '4444-3333', endereco: 'Rua B, 200', version: 4 }
}
estado: { id: 1, telefone: '4444-3333', endereco: 'Rua B, 200', version: 4 }
```

Os dois resultados são o que se quer: **campos diferentes convivem**, **o mesmo campo com
valores diferentes sobe para o usuário decidir**. É o mesmo raciocínio do `git merge`,
e é a razão de o Hibernate ter `@OptimisticLock(excluded = true)` e o `OptimisticLockType.DIRTY`.

---

## 8 · ETag/If-Match ponta a ponta

**Problema.** Expor a proteção numa API HTTP, do jeito que a web padronizou.

Servidor completo em [`07-projeto-modelo/src/server.js`](07-projeto-modelo/src/server.js).
Suba-o (`npm start`) e execute a sequência abaixo — **verificada em 14/08/2026**:

```bash
curl -sD- -o/dev/null http://localhost:3000/produtos/1 | grep -i '^etag'
# etag: "1"
```

```bash
curl -s -o/dev/null -w '%{http_code}\n' -X PUT http://localhost:3000/produtos/1 \
  -H 'content-type: application/json' -H 'if-match: "1"' -d '{"nome":"A"}'
# 200
```

```bash
curl -s -X PUT http://localhost:3000/produtos/1 \
  -H 'content-type: application/json' -H 'if-match: "1"' -d '{"nome":"B"}'
# {
#   "erro": "conflito_de_versao",
#   "versao_enviada": 1,
#   "versao_atual": 2,
#   "atual": { "id": 1, "nome": "A", ... }
# }
```

```bash
curl -s -o/dev/null -w '%{http_code}\n' -X PUT http://localhost:3000/produtos/1 \
  -H 'content-type: application/json' -d '{"nome":"C"}'
# 428
```

```bash
curl -s -o/dev/null -w '%{http_code}\n' -X PUT http://localhost:3000/produtos/1 \
  -H 'content-type: application/json' -H 'if-match: W/"2"' -d '{"nome":"D"}'
# 400   <- ETag fraco: If-Match exige comparação forte (RFC 9110)
```

Cliente correto, em qualquer linguagem, é sempre a mesma dança:

```javascript
const r  = await fetch(url);
const et = r.headers.get('etag');           // guarde o ETag junto com os dados
const dados = await r.json();
// ... o usuário edita, o tempo que quiser ...
const p = await fetch(url, {
  method: 'PUT',
  headers: { 'content-type': 'application/json', 'if-match': et },   // devolva-o
  body: JSON.stringify(dados),
});
if (p.status === 412) { /* conflito: mesclar, perguntar ou retentar */ }
```

---

## 9 · JPA/Hibernate com `@Version`

**Problema.** O mesmo padrão, mas deixando o ORM gerar o SQL.
*Código completo; não executado nesta máquina (exige JDK 21 + Maven).*

```java
// Conta.java
package exemplo;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "conta")
public class Conta {
    @Id
    private Long id;

    private BigDecimal saldo;

    @Version                       // é só isto. O Hibernate faz o resto.
    private long version;          // NUNCA atribua este campo você mesmo

    protected Conta() {}           // exigido pelo JPA

    public Conta(Long id, BigDecimal saldo) { this.id = id; this.saldo = saldo; }

    public BigDecimal getSaldo() { return saldo; }
    public void setSaldo(BigDecimal s) { this.saldo = s; }
    public long getVersion() { return version; }
}
```

```java
// ServicoConta.java — a transação, a exceção e a retentativa
package exemplo;

import jakarta.persistence.*;
import java.math.BigDecimal;

public class ServicoConta {
    private final EntityManagerFactory emf;

    public ServicoConta(EntityManagerFactory emf) { this.emf = emf; }

    /** Debita com retentativa. `tentativas` limitado de propósito: ver 19-retentativa. */
    public void debitar(Long id, BigDecimal valor, int tentativas) {
        for (int i = 0; i < tentativas; i++) {
            EntityManager em = emf.createEntityManager();
            EntityTransaction tx = em.getTransaction();
            try {
                tx.begin();
                Conta c = em.find(Conta.class, id);          // relê a cada tentativa
                if (c == null) throw new IllegalArgumentException("conta inexistente");
                c.setSaldo(c.getSaldo().subtract(valor));
                tx.commit();                                  // aqui é que a versão é conferida
                return;
            } catch (OptimisticLockException e) {
                if (tx.isActive()) tx.rollback();
                if (i == tentativas - 1) throw e;
                try { Thread.sleep((long) (Math.random() * (5L << i))); }
                catch (InterruptedException ie) { Thread.currentThread().interrupt(); return; }
            } finally {
                em.close();
            }
        }
    }
}
```

O SQL que o Hibernate emite no `commit`:

```sql
update conta set saldo=?, version=? where id=? and version=?
-- se retornar 0 linhas, o Hibernate lança OptimisticLockException
```

**Três coisas que só se aprende apanhando:**

1. A verificação acontece no **flush/commit**, não no `setSaldo`. Um `try/catch` em volta do
   `set` não pega nada.
2. Em Spring Data JPA, `save()` numa entidade *detached* com `version == null` gera **INSERT**.
   É a origem de "duplicou em vez de atualizar".
3. Para proteger o **agregado** (editar um item invalida o total do pedido), use
   `em.lock(pedido, LockModeType.OPTIMISTIC_FORCE_INCREMENT)`. Sem isso, dois itens
   adicionados em paralelo passam os dois, e o total fica errado sem nenhum conflito detectado.

---

## 10 · EF Core com `rowversion`

*Código completo; não executado nesta máquina (exige .NET 10 SDK).*

```csharp
// Modelo
public class Conta {
    public int Id { get; set; }
    public decimal Saldo { get; set; }

    [Timestamp]                      // vira `rowversion` no SQL Server
    public byte[] RowVersion { get; set; } = default!;
}

// Alternativa portátil (PostgreSQL/SQLite), no OnModelCreating:
//   modelBuilder.Entity<Conta>().Property(c => c.Version).IsConcurrencyToken();
//   modelBuilder.Entity<Conta>().UseXminAsConcurrencyToken();   // só PostgreSQL
```

```csharp
// Serviço com resolução de conflito de três vias
public async Task DebitarAsync(int id, decimal valor, int tentativas = 5) {
    for (var i = 0; i < tentativas; i++) {
        using var db = new AppDbContext();
        var conta = await db.Contas.FindAsync(id)
                    ?? throw new InvalidOperationException("conta inexistente");
        conta.Saldo -= valor;
        try {
            await db.SaveChangesAsync();
            return;
        }
        catch (DbUpdateConcurrencyException ex) {
            var entry  = ex.Entries.Single();
            var doBanco = await entry.GetDatabaseValuesAsync();

            if (doBanco is null) throw new InvalidOperationException("registro foi apagado");

            // Os três conjuntos que tornam o merge possível:
            //   entry.OriginalValues -> o que eu li
            //   entry.CurrentValues  -> o que eu quero gravar
            //   doBanco              -> o que está lá agora
            // "Rebase": adoto o estado do banco como nova base e reaplico o delta.
            entry.OriginalValues.SetValues(doBanco);
            entry.CurrentValues[nameof(Conta.Saldo)] =
                (decimal)doBanco[nameof(Conta.Saldo)]! - valor;

            if (i == tentativas - 1) throw;
            await Task.Delay(Random.Shared.Next(1 << i) + 1);
        }
    }
}
```

O detalhe que faz esse código valer o espaço: `entry.OriginalValues.SetValues(doBanco)`.
Sem isso, o `SaveChanges` seguinte tentaria de novo com o token velho e falharia para sempre —
o [erro 2 do arquivo `04`](04-como-comecar.md#erro-2--retentar-sem-reler), na versão .NET.

---

## 11 · Django e Rails

*Código completo; não executado nesta máquina.*

### Django — sem mágica, e é melhor assim

```python
# models.py
from django.db import models

class Conta(models.Model):
    saldo = models.IntegerField()
    version = models.IntegerField(default=1)
```

```python
# servico.py
import random, time
from django.db.models import F
from django.db import transaction

class Conflito(Exception):
    pass

def debitar(conta_id: int, valor: int, tentativas: int = 5) -> None:
    for i in range(tentativas):
        conta = Conta.objects.get(pk=conta_id)          # relê a cada tentativa
        if conta.saldo < valor:
            raise ValueError("saldo insuficiente")

        # A guarda inteira: filtro por pk E por version, e conferir o retorno.
        n = (Conta.objects
             .filter(pk=conta_id, version=conta.version)
             .update(saldo=conta.saldo - valor, version=F('version') + 1))

        if n == 1:
            return
        if i == tentativas - 1:
            raise Conflito(f"conta {conta_id} sob contenção")
        time.sleep(random.random() * 0.005 * (2 ** i))
```

```python
# O CONTRAEXEMPLO — para um débito puro, isto é melhor: atômico, sem conflito, sem retentativa.
def debitar_atomico(conta_id: int, valor: int) -> bool:
    return Conta.objects.filter(pk=conta_id, saldo__gte=valor) \
                        .update(saldo=F('saldo') - valor) == 1
```

O Django **não tem** optimistic locking embutido — e a ausência é instrutiva: o
`filter(...).update(...)` já é exatamente a construção certa, e devolve o número de linhas.

### Rails — tem mágica, e ela é discreta

```ruby
# migration
class AddLockVersionToContas < ActiveRecord::Migration[8.0]
  def change
    add_column :contas, :lock_version, :integer, null: false, default: 0
  end
end
```

O nome da coluna, `lock_version`, é o gatilho: o ActiveRecord passa a proteger sozinho.

```ruby
# servico.rb
class Conflito < StandardError; end

def debitar(conta_id, valor, tentativas: 5)
  tentativas.times do |i|
    conta = Conta.find(conta_id)                 # relê a cada tentativa
    begin
      conta.update!(saldo: conta.saldo - valor)
      return
    rescue ActiveRecord::StaleObjectError => e
      raise Conflito, "conta #{conta_id} sob contenção" if i == tentativas - 1
      sleep(rand * 0.005 * (2**i))
    end
  end
end
```

Para desligar em um modelo específico: `self.locking_column = nil` não funciona —
use `ActiveRecord::Base.lock_optimistically = false` (global) ou não crie a coluna.

---

## 12 · DynamoDB `ConditionExpression`

*Código completo; não executado nesta máquina (exige credenciais AWS).*

```python
# dynamo_ocl.py
import random, time
import boto3
from botocore.exceptions import ClientError

tabela = boto3.resource('dynamodb').Table('contas')

class Conflito(Exception):
    pass

def debitar(conta_id: str, valor: int, tentativas: int = 5) -> dict:
    for i in range(tentativas):
        item = tabela.get_item(Key={'id': conta_id}, ConsistentRead=True).get('Item')
        if item is None:
            raise KeyError(conta_id)

        v = int(item['version'])
        try:
            resp = tabela.update_item(
                Key={'id': conta_id},
                UpdateExpression='SET saldo = :novo, version = :vnova',
                # A guarda. Sem ela, é sobrescrita cega.
                ConditionExpression='version = :vlida',
                ExpressionAttributeValues={
                    ':novo':  int(item['saldo']) - valor,
                    ':vnova': v + 1,
                    ':vlida': v,
                },
                ReturnValues='ALL_NEW',
                # Traz o item como estava na falha, SEM custo extra de leitura.
                ReturnValuesOnConditionCheckFailure='ALL_OLD',
            )
            return resp['Attributes']

        except ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
            if i == tentativas - 1:
                raise Conflito(conta_id) from e
            time.sleep(random.random() * 0.005 * (2 ** i))
```

**O que muda no DynamoDB em relação a um banco relacional:**

- A escrita condicional que **falha ainda consome capacidade de escrita (WCU)**. Numa chave
  quente, você paga pelas tentativas recusadas. Em SQL, um `UPDATE 0` também custa, mas o
  custo não aparece na fatura de forma tão direta.
- `ReturnValuesOnConditionCheckFailure` (2023) devolve o item da falha **sem custo adicional**,
  evitando um `get_item` extra — use sempre.
- `ConsistentRead=True` é necessário: com leitura eventual, você pode ler uma versão antiga e
  gerar conflito garantido.

---

## 13 · **Produção:** reserva de assentos com lease + OCC

**Problema real.** Venda de ingressos. O usuário escolhe a poltrona e tem 10 minutos para
pagar. Não dá para segurar uma transação de banco por 10 minutos, e não dá para vender duas
vezes o mesmo assento.

**A solução que funciona é híbrida:** um *lease* (reserva com prazo) protegido por
optimistic locking. *Código completo; sintaxe PostgreSQL; não executado nesta máquina.*

```sql
CREATE TABLE assento (
  id           BIGINT PRIMARY KEY,
  evento_id    BIGINT NOT NULL,
  fileira      TEXT   NOT NULL,
  numero       INT    NOT NULL,
  estado       TEXT   NOT NULL CHECK (estado IN ('livre','reservado','vendido')),
  reservado_por TEXT,                       -- id da sessão do comprador
  reserva_expira_em TIMESTAMPTZ,            -- o LEASE
  version      BIGINT NOT NULL DEFAULT 1,
  UNIQUE (evento_id, fileira, numero)
);

CREATE INDEX ON assento (evento_id, estado);
```

```sql
-- PASSO 1 — reservar (idempotente e seguro em corrida)
-- Um comando só. Aceita se: está livre, OU está reservado mas o lease venceu,
-- OU já é meu (reentrada do mesmo comprador).
UPDATE assento
   SET estado            = 'reservado',
       reservado_por     = :sessao,
       reserva_expira_em = now() + interval '10 minutes',
       version           = version + 1
 WHERE id = :assento
   AND (
         estado = 'livre'
      OR (estado = 'reservado' AND reserva_expira_em < now())
      OR (estado = 'reservado' AND reservado_por = :sessao)
   )
RETURNING id, version, reserva_expira_em;
-- 0 linhas -> alguém pegou antes (HTTP 409, e ofereça assentos vizinhos)
```

```sql
-- PASSO 2 — confirmar a venda, ao final do pagamento
UPDATE assento
   SET estado = 'vendido',
       reserva_expira_em = NULL,
       version = version + 1
 WHERE id = :assento
   AND version = :version_da_reserva     -- <<< o OCC entra aqui
   AND estado = 'reservado'
   AND reservado_por = :sessao
   AND reserva_expira_em > now()         -- o lease ainda vale?
RETURNING id;
-- 0 linhas -> o lease expirou e outro comprou. Estorne o pagamento.
```

**As decisões de projeto e o porquê de cada uma:**

| Decisão | Por quê |
|---|---|
| Lease com prazo, não lock de banco | 10 minutos segurando uma transação esgotaria as conexões e travaria o `VACUUM` |
| Prazo verificado **no `WHERE`**, com `now()` do banco | usar o relógio da aplicação abriria janela entre máquinas com relógios diferentes |
| Nenhum job de "liberar expirados" no caminho crítico | o `WHERE` já trata o expirado; o job é só higiene, e pode atrasar sem quebrar nada |
| `version` conferida no passo 2 | entre reservar e pagar, o assento pode ter sido reciclado; sem isso você vende duas vezes |
| Cláusula "ou já é meu" | o usuário que atualiza a página não perde a própria reserva |
| `UNIQUE (evento, fileira, numero)` | a última linha de defesa é o banco, não o código |

**O que quebra na vida real, e a correção:**

- **Relógio.** Se o passo 2 comparasse com a hora da aplicação, uma máquina adiantada
  aceitaria leases vencidos. Use sempre `now()` do banco.
- **Estorno.** O passo 2 pode falhar **depois** do pagamento aprovado. É obrigatório ter
  compensação; ver [`19-retentativa-e-idempotencia.md`](19-retentativa-e-idempotencia.md).
- **Fila de espera.** Quando a taxa de conflito passa de ~20% (show grande, venda às 10h),
  nenhum ajuste de OCC salva: aí o certo é uma **fila** que serializa a entrada.
  Ver [`14-otimista-vs-pessimista.md`](14-otimista-vs-pessimista.md).

---

## 14 · **Produção:** sincronizar com uma API de terceiro

**Problema real.** Você mantém um catálogo espelhado de um ERP que expõe `ETag`. Precisa
atualizar lá sem sobrescrever mudanças feitas por outros integradores, e sem baixar tudo toda
hora. *Código completo em Node 24; a API remota é fictícia, então não é executável como está.*

```javascript
// sync.mjs
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync('./espelho.db');
db.exec(`CREATE TABLE IF NOT EXISTS espelho (
  id TEXT PRIMARY KEY,
  etag_remoto TEXT,        -- o token DELES, guardado como opaco
  dados TEXT,
  version INTEGER NOT NULL DEFAULT 1,   -- o token NOSSO, independente
  sincronizado_em TEXT
)`);

const API = 'https://erp.exemplo.com/api/produtos';
const cabecalhosBase = { authorization: `Bearer ${process.env.TOKEN}` };

/** Puxa o remoto usando If-None-Match: 304 significa "nada mudou", e não custa banda. */
async function puxar(id) {
  const local = db.prepare('SELECT * FROM espelho WHERE id = ?').get(id);
  const cabecalhos = { ...cabecalhosBase };
  if (local?.etag_remoto) cabecalhos['if-none-match'] = local.etag_remoto;

  const r = await fetch(`${API}/${id}`, { headers: cabecalhos });

  if (r.status === 304) return { mudou: false, local };          // economia real de custo
  if (r.status === 404) return { mudou: true, apagado: true };
  if (!r.ok) throw new Error(`GET ${id}: ${r.status}`);

  const dados = await r.json();
  const etag = r.headers.get('etag');
  db.prepare(`INSERT INTO espelho (id, etag_remoto, dados, sincronizado_em)
              VALUES (?, ?, ?, datetime('now'))
              ON CONFLICT(id) DO UPDATE SET
                etag_remoto = excluded.etag_remoto,
                dados = excluded.dados,
                version = espelho.version + 1,
                sincronizado_em = excluded.sincronizado_em`)
    .run(id, etag, JSON.stringify(dados));
  return { mudou: true, dados, etag };
}

/** Empurra uma alteração nossa, respeitando o ETag deles. */
async function empurrar(id, alteracoes, tentativas = 4) {
  for (let i = 0; i < tentativas; i++) {
    const atual = await puxar(id);                    // sempre parta do estado remoto atual
    const etag = atual.etag ?? atual.local?.etag_remoto;
    if (!etag) throw new Error(`sem ETag para ${id}: o ERP não suporta If-Match?`);

    const corpo = { ...(atual.dados ?? JSON.parse(atual.local.dados)), ...alteracoes };

    const r = await fetch(`${API}/${id}`, {
      method: 'PUT',
      headers: { ...cabecalhosBase, 'content-type': 'application/json', 'if-match': etag },
      body: JSON.stringify(corpo),
    });

    if (r.ok) {
      db.prepare(`UPDATE espelho SET etag_remoto = ?, dados = ?, version = version + 1,
                  sincronizado_em = datetime('now') WHERE id = ?`)
        .run(r.headers.get('etag'), JSON.stringify(corpo), id);
      return { ok: true, tentativas: i + 1 };
    }

    if (r.status === 412) {                            // alguém escreveu antes de nós
      const espera = Math.random() * Math.min(2000, 100 * 2 ** i);
      await new Promise((res) => setTimeout(res, espera));
      continue;                                        // o próximo `puxar` traz o estado novo
    }

    if (r.status === 428) throw new Error('o ERP exige If-Match e não mandamos');
    if (r.status === 429) {                            // limite de taxa: respeite o Retry-After
      const espera = Number(r.headers.get('retry-after') ?? 5) * 1000;
      await new Promise((res) => setTimeout(res, espera));
      continue;
    }
    throw new Error(`PUT ${id}: ${r.status} ${await r.text()}`);
  }
  throw new Error(`${id}: não convergiu em ${tentativas} tentativas — investigue contenção`);
}
```

**O que este código ensina e um tutorial não mostraria:**

1. **Dois tokens, não um.** `etag_remoto` é deles (opaco, você nunca interpreta) e `version`
   é seu (para os seus próprios consumidores). Misturar os dois amarra você ao formato deles.
2. **`If-None-Match` no `GET` é dinheiro.** Um `304` não transfere corpo. Em catálogo grande e
   API tarifada por volume, é a diferença entre viável e caro.
3. **`412` é retentável; `428` não é.** `428` é bug seu — retentar não conserta e só queima
   cota. Distinguir erro retentável de erro permanente é o que separa uma integração que se
   recupera de uma que fica em laço.
4. **`429` tem regra própria.** Respeite `Retry-After` em vez de aplicar o seu backoff:
   ignorar isso é o caminho mais rápido para ser bloqueado pelo terceiro.
5. **Falhar depois de N tentativas é uma decisão**, não um acidente. Um laço infinito
   "para não perder dados" é como se perde o sistema inteiro.

---

## Autoteste

1. No exemplo 5, por que o resultado é 210 e não 10?
2. No exemplo 6, qual é o defeito deliberado do código, e qual é a correção estrutural?
3. Por que `IS NOT DISTINCT FROM` em vez de `=` no exemplo 3?
4. No exemplo 7, qual é a condição exata que caracteriza um conflito **real**?
5. No exemplo 9, por que um `try/catch` em volta do `setSaldo` não pega nada?
6. No exemplo 10, o que aconteceria sem `entry.OriginalValues.SetValues(doBanco)`?
7. No exemplo 13, por que o prazo do lease é conferido com `now()` do banco e não do servidor
   de aplicação?
8. No exemplo 14, por que `412` é retentável e `428` não é?
9. Escolha entre versão e delta atômico para: (a) "curtir" um post, (b) editar a biografia do
   perfil, (c) transferir R$ 50 entre contas. Justifique cada um.
