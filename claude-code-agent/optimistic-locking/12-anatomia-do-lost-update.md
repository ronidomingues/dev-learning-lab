# 12 · Anatomia do lost update

`Nível: intermediário` · `Atualizado em: 14/08/2026`

Este arquivo disseca o bug. Não para repetir a definição, mas para você conseguir
**reconhecê-lo em código que já existe** e **provar que ele acontece** — que é o que
convence uma equipe a consertar.

---

## 1. As quatro formas do mesmo bug

O *lost update* aparece disfarçado. Estas são as quatro formas em que eu já o encontrei em
código de produção, da mais óbvia para a mais traiçoeira.

### Forma 1 — LMW explícito na aplicação

```javascript
const conta = await db.buscar(42);           // saldo = 100
conta.saldo -= 10;
await db.salvar(conta);                      // UPDATE conta SET saldo = 90 WHERE id = 42
```

O clássico. Duas execuções simultâneas produzem `90` em vez de `80`.
**Como reconhecer:** um `SELECT` (ou `find`) seguido de um `UPDATE` que grava um valor
**absoluto** derivado do que foi lido.

### Forma 2 — o `PUT` de formulário

```
GET  /cliente/42/editar     → renderiza o formulário com todos os campos
                              (o usuário edita só o telefone)
POST /cliente/42            → envia TODOS os campos de volta
                              UPDATE cliente SET nome=?, telefone=?, endereco=?, ... WHERE id=42
```

Aqui o dano é maior que na forma 1: o usuário **nem tocou** nos campos que vai sobrescrever.
Ele editou o telefone; o navegador devolveu o endereço lido há vinte minutos, e esse endereço
apaga a correção que outra pessoa fez nesse meio-tempo.

**Como reconhecer:** um formulário que envia campos que o usuário não editou. Praticamente
todo CRUD gerado por scaffold faz isso.

### Forma 3 — o *upsert* ingênuo

```javascript
const existente = await db.buscar(chave);
if (existente) await db.atualizar(chave, dados);
else           await db.inserir(chave, dados);
```

Duas execuções concorrentes podem: (a) ambas verem `null` e inserirem duas vezes — a chave
única salva, se existir; (b) uma inserir e a outra atualizar por cima. A janela aqui é de
microssegundos, o que faz o bug ser **irreproduzível em desenvolvimento e frequente em
produção**.

**Correção:** `INSERT ... ON CONFLICT DO UPDATE` (PostgreSQL/SQLite), `MERGE` (SQL Server,
Oracle, PostgreSQL 15+), ou `INSERT ... ON DUPLICATE KEY UPDATE` (MySQL) — uma operação só.

### Forma 4 — o LMW escondido dentro de um `SELECT` agregado

```sql
-- calcular o novo total do pedido a partir dos itens
SELECT SUM(preco * qtd) FROM item WHERE pedido_id = 7;   -- 350
UPDATE pedido SET total = 350 WHERE id = 7;
```

Se alguém adicionar um item entre as duas linhas, o total fica errado — e **permanece** errado,
porque nada mais o recalcula. Este é o *lost update* mais difícil de encontrar, porque as duas
operações tocam **tabelas diferentes**: nenhuma coluna de versão em `item` protege `pedido`.

**Correção:** versão no **agregado** (a linha `pedido`), incrementada por qualquer escrita nos
filhos — é exatamente o que o `OPTIMISTIC_FORCE_INCREMENT` do JPA existe para fazer. Ou
`SERIALIZABLE`, ou recalcular com `UPDATE ... SET total = (SELECT SUM ...)` num comando só.

---

## 2. Provar que acontece

A conversa "isso não acontece na nossa escala" só termina com um número. Três maneiras de
produzir esse número, da mais barata para a mais convincente.

### 2.1 Reprodução determinística com duas sessões

Não depende de sorte. Abra dois terminais `psql` e execute na ordem indicada:

```sql
-- Sessão A                                  -- Sessão B
BEGIN;
SELECT saldo FROM conta WHERE id=1;          --
-- 100                                       BEGIN;
                                             SELECT saldo FROM conta WHERE id=1;
                                             -- 100
UPDATE conta SET saldo=90 WHERE id=1;
COMMIT;
                                             UPDATE conta SET saldo=90 WHERE id=1;
                                             COMMIT;

SELECT saldo FROM conta WHERE id=1;
-- 90   <<< deveria ser 80. Um débito de 10 desapareceu.
```

Repare que **nenhum erro apareceu em nenhuma das sessões**, e que isso acontece no nível de
isolamento padrão (`READ COMMITTED`). O padrão do seu banco não protege contra isto.

> Em `REPEATABLE READ`, o PostgreSQL aborta a sessão B com
> `ERROR: could not serialize access due to concurrent update`. Já o MySQL/InnoDB, no mesmo
> nível nominal, **não** aborta: ele reexecuta o `UPDATE` sobre a versão nova. Mesmo nome,
> comportamentos diferentes — ver [`15`](15-isolamento-e-mvcc.md).

### 2.2 Corrida real, com contagem

O que convence uma equipe é a tabela de sobreviventes. É o que faz
[`demo-corrida.js`](07-projeto-modelo/test/demo-corrida.js), com saída verificada:

```
modo .................. inseguro
clientes .............. 20
edições sobreviventes . 10 de 20
edições PERDIDAS ...... 10
versão final .......... 21
```

O detalhe decisivo desse resultado: **a versão final é 21 nos dois modos**. Ter uma coluna
`version` que incrementa não prova nada. Só o `WHERE` protege.

### 2.3 Detecção em produção, sem mudar o comportamento

Quando você suspeita mas não pode arriscar mudar nada, instrumente antes de corrigir:

```sql
-- Trilha de auditoria com o valor anterior. Sem alterar o caminho de escrita.
CREATE TABLE conta_audit (
  id BIGSERIAL PRIMARY KEY,
  conta_id BIGINT NOT NULL,
  saldo_antes INTEGER,
  saldo_depois INTEGER,
  version_antes INTEGER,
  quando TIMESTAMPTZ NOT NULL DEFAULT now(),
  sessao TEXT NOT NULL DEFAULT current_setting('application_name', true)
);

CREATE OR REPLACE FUNCTION audita_conta() RETURNS trigger AS $$
BEGIN
  INSERT INTO conta_audit (conta_id, saldo_antes, saldo_depois, version_antes)
  VALUES (OLD.id, OLD.saldo, NEW.saldo, OLD.version);
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audita_conta AFTER UPDATE ON conta
  FOR EACH ROW EXECUTE FUNCTION audita_conta();
```

Depois, procure pelo padrão: **duas escritas próximas no tempo partindo do mesmo valor
anterior**.

```sql
SELECT a.conta_id, a.quando, b.quando, a.saldo_antes
  FROM conta_audit a
  JOIN conta_audit b
    ON a.conta_id = b.conta_id
   AND a.id < b.id
   AND a.saldo_antes = b.saldo_antes        -- as duas partiram do MESMO valor
   AND b.quando - a.quando < interval '30 seconds'
 ORDER BY a.quando DESC
 LIMIT 50;
```

Cada linha desse resultado é um lost update quase certo. Leve essa consulta para a reunião.

---

## 3. Por que o bug não aparece em desenvolvimento

Cinco razões, todas estruturais — não é falta de cuidado:

| Motivo | Efeito |
|---|---|
| **Um usuário só** | não há concorrência; a janela nunca é disputada |
| **Latência local ~0** | a janela entre `SELECT` e `UPDATE` fica em microssegundos |
| **Dados de teste esparsos** | ninguém edita a mesma linha |
| **Testes sequenciais** | chamar a função duas vezes em sequência **nunca** reproduz o bug |
| **Sem métrica** | mesmo que aconteça, ninguém vê |

Corolário importante para quem escreve testes:

> Um teste que chama `debitar()` duas vezes seguidas **não testa concorrência**. Ele testa
> sequência. Para testar concorrência é preciso concorrência de verdade: N clientes, N
> processos ou N threads, disputando a mesma linha.

É por isso que o projeto-modelo usa 20 clientes HTTP reais em vez de um mock — ver
[`test/run-tests.js`](07-projeto-modelo/test/run-tests.js).

---

## 4. Quanto custa: a matemática da janela

Uma estimativa grosseira e útil da probabilidade de conflito. Suponha:

- `N` = escritas por segundo sobre um mesmo registro;
- `W` = duração da janela de vulnerabilidade, em segundos.

O número esperado de escritas que caem dentro da sua janela é `N × W`. Assumindo chegadas
aproximadamente independentes, a chance de **pelo menos uma** interferir é

```
P(conflito) ≈ 1 − e^(−N·W)
```

| Cenário | `N` | `W` | `P(conflito)` |
|---|---|---|---|
| Cadastro interno, edição por formulário | 0,001/s | 300 s (5 min) | ~0,03% |
| Cadastro interno, mesma linha em época de auditoria | 0,05/s | 300 s | ~1,5% |
| Carrinho, LMW dentro do servidor | 5/s | 0,005 s | ~2,5% |
| Estoque de item em promoção | 200/s | 0,005 s | **~63%** |
| Contador global de acessos | 5.000/s | 0,001 s | **~99,3%** |

O que a tabela ensina, e é o ponto do arquivo inteiro:

1. **A janela importa tanto quanto o volume.** Reduzir `W` de 300 s para 5 s tem o mesmo
   efeito que reduzir o tráfego em 60 vezes. Frequentemente é mais fácil.
2. **Acima de ~10% de conflito, OCC deixa de ser a resposta certa.** Não porque falhe — ele
   continua correto —, mas porque o custo de retentar domina. Ver [`14`](14-otimista-vs-pessimista.md).
3. **Os dois últimos casos não devem usar versão nenhuma.** São deltas comutativos: a
   resposta é `UPDATE ... SET x = x + 1`, que não tem janela.

> A fórmula assume chegadas independentes (processo de Poisson). Tráfego real é **em rajadas**
> e correlacionado — promoções, robôs, retentativas em cascata. Trate os números como ordem de
> grandeza, não como previsão. Se precisar de precisão, meça: a taxa de conflito observada é o
> único número honesto.

---

## 5. Onde procurar no seu código hoje

Uma lista de buscas concretas para rodar no repositório. Cada acerto é um candidato.

```bash
# 1. LMW explícito: leitura seguida de gravação do objeto inteiro
grep -rn "findById\|findOne\|\.get(" --include='*.java' --include='*.ts' -A6 . \
  | grep -B4 "save(\|update("
```

```bash
# 2. Rotas de escrita que não mencionam versão nem ETag
grep -rn "app.put\|app.patch\|@PutMapping\|@PatchMapping" . \
  | xargs -I{} echo {}   # e revise uma a uma: quantas checam If-Match?
```

```bash
# 3. UPDATE com valor absoluto onde deveria haver delta
grep -rn "SET .*= ?" --include='*.sql' . | grep -v "= .* [+-]"
```

```bash
# 4. Retorno de UPDATE descartado
grep -rn "\.run(\|executeUpdate()\|ExecuteNonQuery()\|\.update(" . \
  | grep -v "changes\|rowcount\|rowCount\|RowsAffected\|== 1\|n =\|var n"
```

O item 4 costuma ser o mais produtivo: encontra os lugares onde a guarda **existe** e ninguém
olha o resultado — proteção zero com aparência de proteção.

Checklist de revisão de código, para colar no seu template de PR:

- [ ] Este `UPDATE` grava um valor **absoluto** derivado de uma leitura anterior?
- [ ] Se sim, o `WHERE` contém a versão lida?
- [ ] O número de linhas afetadas é conferido?
- [ ] O caminho de conflito faz algo além de lançar 500?
- [ ] O formulário/`PUT` envia campos que o usuário não editou?
- [ ] Existe métrica de taxa de conflito para esta tabela?

---

## Autoteste

1. Descreva as quatro formas do lost update e dê um exemplo próprio de cada.
2. Por que a forma 4 (agregado) não é resolvida por versão nas linhas filhas?
3. Escreva a sequência de duas sessões `psql` que reproduz o bug de forma determinística.
4. Por que um teste que chama a função duas vezes em sequência não testa concorrência?
5. Estime a probabilidade de conflito com 10 escritas/s e janela de 50 ms.
6. Reduzir a janela de 300 s para 5 s equivale a que redução de tráfego?
7. Qual das buscas da seção 5 você rodaria primeiro no seu repositório, e por quê?
