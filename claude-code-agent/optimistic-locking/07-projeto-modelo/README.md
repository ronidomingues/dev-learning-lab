# Projeto-modelo — Catálogo Otimista

`Nível: iniciante → intermediário` · `Testado em: Node v24.18.0, Ubuntu 22.04.5, 14/08/2026`

Uma API de catálogo de produtos, pequena mas inteira, que implementa **optimistic locking
ponta a ponta**: coluna de versão no banco → guarda no `UPDATE` → `ETag`/`If-Match` no HTTP →
`412` → retentativa com recuo exponencial no cliente.

**Zero dependências.** Nada de `npm install`. Usa o SQLite embutido do Node (`node:sqlite`),
o servidor HTTP nativo e o runner de testes nativo (`node:test`).

---

## Por que este projeto e não um "hello world"

Optimistic locking só se entende vendo os **dois** comportamentos: o bug e a correção,
com a mesma carga de trabalho. Este projeto tem os dois caminhos ligados de propósito
(`PUT /produtos/:id` protegido, `PUT /inseguro/produtos/:id` não), e um script que roda
a mesma corrida nos dois e imprime quantas edições sobreviveram.

---

## Pré-requisitos

| Item | Versão mínima | Como conferir |
|---|---|---|
| Node.js | **22.5** (recomendado **24 LTS**) | `node --version` |

```bash
node --version
# esperado: v24.18.0 (ou superior). Se for < v22.5, `node:sqlite` não existe.
```

Se a saída for menor, veja [`../03-instalacao.md`](../03-instalacao.md).
Nenhuma outra ferramenta é necessária: sem banco externo, sem Docker, sem conta em serviço.

---

## Como rodar

```bash
cd 07-projeto-modelo
```

```bash
npm test
# esperado: "ℹ pass 21 / ℹ fail 0"
```

```bash
npm run demo:perde
# esperado: "edições PERDIDAS ...... 10" (o número varia; o que não varia é ser > 0)
```

```bash
npm run demo:protege
# esperado: "edições PERDIDAS ...... 0" e "escritas HTTP gastas .. ~67 (3.35x por edição)"
```

```bash
npm start
# esperado: "catálogo otimista em http://localhost:3000 (db: :memory:)"
```

Com o servidor no ar, o ciclo completo em três comandos:

```bash
curl -i http://localhost:3000/produtos/1
# esperado: HTTP/1.1 200 e um cabeçalho `ETag: "1"`
```

```bash
curl -i -X PUT http://localhost:3000/produtos/1 \
  -H 'content-type: application/json' -H 'if-match: "1"' \
  -d '{"nome":"Teclado editado"}'
# esperado: HTTP/1.1 200 e `ETag: "2"`
```

```bash
curl -i -X PUT http://localhost:3000/produtos/1 \
  -H 'content-type: application/json' -H 'if-match: "1"' \
  -d '{"nome":"Editado de novo com ETag velho"}'
# esperado: HTTP/1.1 412 Precondition Failed, com o estado atual no corpo
```

```bash
curl -i -X PUT http://localhost:3000/produtos/1 \
  -H 'content-type: application/json' -d '{"nome":"Sem precondição"}'
# esperado: HTTP/1.1 428 Precondition Required
```

Para persistir em arquivo em vez de memória:

```bash
DB=./catalogo.db PORTA=8080 npm start
```

---

## Estrutura

```
07-projeto-modelo/
├── package.json              # sem dependências; só scripts e `"type": "module"`
├── src/
│   ├── db.js                 # esquema (note a coluna `version`), seed idempotente
│   ├── repo.js               # ★ a guarda otimista vive aqui, e só aqui
│   ├── retry.js              # recuo exponencial com full jitter
│   ├── server.js             # HTTP: ETag, If-Match, 200/400/404/409/412/428
│   └── cliente.js            # o lado de fora: guardar o ETag e devolvê-lo
└── test/
    ├── run-tests.js          # 21 testes, incluindo uma corrida real de 20 clientes
    └── demo-corrida.js       # o bug e a correção, lado a lado, com números
```

---

## O que cada decisão de projeto ensina

### 1. A guarda inteira cabe em uma cláusula `WHERE` — `src/repo.js`

```sql
UPDATE produtos
   SET nome = ?, version = version + 1
 WHERE id = ? AND version = ?
```

Comparar e escrever no **mesmo comando** é o ponto. Um `SELECT version` seguido de `UPDATE`
recria exatamente o bug que se quer evitar, porque abre uma janela entre a verificação e a
escrita. É o banco que garante a atomicidade da linha; você só precisa não sabotá-lo.

### 2. Zero linhas afetadas **é** a detecção

`res.changes === 0` não gera exceção nenhuma no driver. Se o código não conferir esse número,
o sistema tem uma coluna de versão bonita e **nenhuma proteção**. Foi o erro mais comum que já
vi em revisão de código sobre este assunto.

A `demo:perde` prova isso de forma cruel: no modo inseguro a versão final também chega a 21
— a coluna incrementou 20 vezes — e ainda assim **10 edições sumiram**. Coluna de versão sem
`WHERE` é teatro.

### 3. Quem incrementa a versão é o banco, nunca o cliente

`version = version + 1` é calculado do lado do servidor. Se o cliente enviasse a versão nova,
dois clientes poderiam enviar o mesmo número e o conflito seguinte passaria despercebido.

### 4. Nem todo campo quer optimistic locking — `baixarEstoque()`

Baixa de estoque é um **delta comutativo**: se dois pedidos tiram 1 cada, o certo é −2 e não
há conflito real para relatar a ninguém. Usar versão ali produziria conflitos falsos e
retentativas inúteis. A guarda certa é a regra de negócio no `WHERE`:

```sql
WHERE id = ? AND estoque >= ?
```

Regra prática: **versão** quando a intenção é *"substituir o valor que eu li"*;
**delta atômico** quando a intenção é *"aplicar esta diferença ao que estiver lá"*.

### 5. Retentar exige **reler** — `src/cliente.js`, função `editar`

`comRetentativa` reexecuta o bloco inteiro: `GET` → transformar → `PUT`. Retentar com o mesmo
ETag falharia para sempre. E a transformação precisa ser reaplicável sobre o estado novo —
por isso ela recebe `p` e devolve campos derivados de `p`, em vez de valores fixos.

### 6. Jitter não é enfeite — `src/retry.js`

Sem sorteio no atraso, os 20 clientes em conflito voltam todos no mesmo instante e colidem
outra vez: a taxa de conflito não cai, só muda de horário. Com *full jitter*, a `demo:protege`
converge em ~3,3 escritas por edição.

### 7. `412` devolve o estado atual junto

O cliente que levou 412 precisa do estado novo para decidir (mesclar? avisar o usuário?
retentar?). Mandá-lo fazer um `GET` extra é uma ida e volta desperdiçada — e uma janela nova
para outro conflito.

### 8. `428 Precondition Required` é obrigação do servidor

Se o servidor aceitasse `PUT` sem `If-Match`, o cliente distraído sobrescreveria tudo em
silêncio e o servidor teria sido cúmplice. A pré-condição precisa ser **exigida**, não sugerida.

### 9. ETag **forte**, sem `W/`

A RFC 9110 manda comparar `If-Match` com comparação forte. Um `W/"3"` nunca casa — a
requisição falha sempre, e o sintoma (412 eterno) não parece ter nada a ver com a causa.
O servidor recusa `W/` com `400` e diz o motivo, em vez de deixar o integrador adivinhar.

### 10. Erros distintos para causas distintas

`ConflitoDeVersao` (412) e `NaoEncontrado` (404) chegam ambos como "zero linhas afetadas".
O repositório faz um `SELECT` a mais **só no caminho de falha** para separar os dois. Custo
zero no caminho feliz, diagnóstico correto no caminho ruim.

### 11. Transação envolvendo a auditoria

O `UPDATE` e o `INSERT` na trilha de auditoria acontecem na mesma transação: um conflito não
pode deixar rastro de uma escrita que não ocorreu. O teste *"conflito não deixa linha na
auditoria"* trava esse comportamento.

### 12. O que tutoriais omitem e está aqui

Tratamento de erro por categoria, configuração por variável de ambiente (`DB`, `PORTA`),
seed idempotente, servidor exportado como fábrica (para o teste subir na porta 0 em vez de
depender da 3000), e uma suíte que inclui uma **corrida de verdade**, não um mock de corrida.

---

## Resultado observado (14/08/2026, Node v24.18.0)

```
modo .................. inseguro          modo .................. seguro
clientes .............. 20                clientes .............. 20
edições sobreviventes . 10 de 20          edições sobreviventes . 20 de 20
edições PERDIDAS ...... 10                edições PERDIDAS ...... 0
versão final .......... 21                versão final .......... 21
escritas HTTP gastas .. 20 (1.00x)        escritas HTTP gastas .. 67 (3.35x)
tempo ................. 64.0 ms           tempo ................. 239.7 ms
```

Leia a tabela como um trade-off, porque é isso que ela é: a correção custou **3,3× mais
escritas** e **3,7× mais tempo** sob contenção máxima (20 clientes na mesma linha). Em carga
real, com conflitos raros, o custo tende a zero — e é justamente por isso que a estratégia
se chama *otimista*. Veja [`14-otimista-vs-pessimista.md`](../14-otimista-vs-pessimista.md)
para quando o cálculo se inverte.

---

## Exercícios sobre este código

1. Troque a coluna `version` por um `hash` do conteúdo (SHA-256 dos campos) e faça a suíte
   passar de novo. O que quebra? (Dica: `atualizado_em` muda em toda escrita.)
2. Implemente merge campo a campo no `412`: se dois clientes editaram campos **diferentes**,
   aceite os dois em vez de recusar. Compare com `@OptimisticLock(excluded=true)` do Hibernate.
3. Faça o servidor devolver `409 Conflict` em vez de `412` e argumente qual é o certo.
   (Veja [`17-http-e-apis.md`](../17-http-e-apis.md).)
4. Meça a taxa de conflito com 5, 20, 100 clientes. Ela cresce linearmente? Por quê?
5. Aponte `DB=./catalogo.db` e rode duas instâncias do servidor na mesma porta... que não vai
   dar. Rode em portas diferentes contra o **mesmo arquivo** e veja o que acontece com
   `SQLITE_BUSY`. Qual camada passou a ser o gargalo?

---

[← voltar ao mapa](../00-MAPA.md) · [exemplos](../06-exemplos.md) · [armadilhas](../75-armadilhas.md)
