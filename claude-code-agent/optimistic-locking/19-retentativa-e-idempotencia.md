# 19 · Retentativa e idempotência

`Nível: avançado` · `Atualizado em: 14/08/2026`

Detectar o conflito é a parte fácil. **Retentar sem causar dano é a parte que separa um
sistema robusto de um sistema que cobra duas vezes do cliente.**

---

## 1. Quando retentar é correto

Não é sempre. A pergunta a fazer é:

> **A operação continua sendo a decisão certa depois de reler o estado novo?**

| Situação | Retentar automaticamente? | Por quê |
|---|---|---|
| `saldo = saldo − 10` | **sim** | a intenção é o delta; recalcular sobre o novo estado é fiel |
| "aplicar 10% de desconto" | **sim** | a regra é reaplicável |
| "definir o preço para R$ 99" | **talvez** | depende: o usuário decidiu 99 vendo qual preço anterior? |
| "aprovo este texto" | **não** | ele aprovou o texto que leu; o texto mudou |
| "confirmar transferência de R$ 500" | **não sem revisão** | o saldo pode ter mudado; a decisão dele pressupunha o saldo antigo |
| Job de sincronização automática | **sim** | não há decisão humana envolvida |

**A regra:** retentativa automática é segura quando a operação é uma **função do estado**.
É insegura quando é uma **decisão sobre o estado**, porque a decisão foi tomada com base numa
informação que deixou de valer.

Confundir as duas é como aplicar `git rebase` automaticamente numa revisão de código: o
resultado compila e não é o que a pessoa revisou.

---

## 2. A política de retentativa

### 2.1 Recuo exponencial com jitter

```javascript
// atraso_i = aleatório(0, min(teto, base × 2^i))   — "full jitter"
const atraso = Math.floor(Math.random() * Math.min(tetoMs, baseMs * 2 ** tentativa));
```

Por que cada peça existe:

| Peça | Sem ela |
|---|---|
| **exponencial** | atraso constante mantém a pressão sobre a linha quente |
| **jitter** | todos os clientes em conflito voltam no mesmo instante e colidem de novo — *thundering herd* |
| **teto** | a latência de cauda cresce sem limite; o `p99` fica inaceitável |
| **limite de tentativas** | uma linha permanentemente quente produz laço infinito e derruba o serviço |

O efeito do jitter é mensurável. Na demonstração do projeto-modelo, com 20 clientes
disputando a mesma linha, o custo com *full jitter* ficou em **3,35 escritas por edição
bem-sucedida** e todas as 20 edições convergiram. Sem jitter, o mesmo cenário faz os clientes
sincronizarem-se em rodadas e a convergência piora.

### 2.2 Escolher os números

| Contexto | Tentativas | Base | Teto |
|---|---|---|---|
| Requisição interativa (usuário esperando) | 2 a 3 | 10 ms | 200 ms |
| API interna, serviço a serviço | 3 a 5 | 20 ms | 1 s |
| Job em lote, sem ninguém esperando | 10 a 50 | 50 ms | 10 s |
| Sincronização com terceiro | 3 a 5 | 200 ms | 30 s (e respeite `Retry-After`) |

**Orçamento de tempo, não contagem de tentativas.** Uma política melhor que "5 tentativas" é
"até 800 ms no total". Ela protege o `p99` diretamente, que é o que o usuário sente:

```javascript
const prazo = Date.now() + 800;
while (Date.now() < prazo) {
  try { return await operacao(); }
  catch (e) {
    if (!ehConflito(e)) throw e;
    await dormir(Math.random() * Math.min(200, 10 * 2 ** i++));
  }
}
throw new Error('orçamento de retentativa esgotado');
```

### 2.3 O que **não** retentar

```javascript
const retentavel = (e) =>
  e.name === 'ConflitoDeVersao' ||
  e.status === 412 ||
  e.code === '40001' ||          // serialization_failure
  e.code === '40P01';            // deadlock_detected

// TypeError, ValidationError, 400, 403, 404, 428 -> NUNCA.
// Retentar um bug de programação só multiplica o bug e queima cota.
```

`428` merece destaque: significa "você esqueceu o `If-Match`". Retentar não conserta nada;
é bug do seu cliente. Um laço de retentativa que engole `428` transforma um erro óbvio em
um problema de desempenho misterioso.

---

## 3. Idempotência: o pré-requisito

Retentar só é seguro se executar duas vezes tiver o mesmo efeito de executar uma.

> **Idempotente:** `f(f(x)) = f(x)`.

| Operação | Idempotente? |
|---|---|
| `UPDATE ... SET saldo = 90 WHERE id=1 AND version=7` | **sim** — a segunda vez afeta 0 linhas |
| `UPDATE ... SET saldo = saldo - 10 WHERE id=1` | **não** — debita duas vezes |
| `INSERT ... ON CONFLICT DO NOTHING` | sim |
| `INSERT` puro | não (a chave única transforma em erro, o que é melhor que duplicar) |
| enviar e-mail | **não** |
| cobrar cartão | **não** — e é a mais cara da lista |
| publicar em fila | não (a menos que o consumidor deduplique) |

Repare no detalhe elegante da primeira linha: **a própria guarda de versão torna o `UPDATE`
idempotente**. A segunda execução com o mesmo token não faz nada. É uma propriedade que se
ganha de graça e quase nunca é notada.

### 3.1 Chave de idempotência

Para operações com efeito externo, a solução padrão:

```sql
CREATE TABLE operacao_idempotente (
  chave        TEXT PRIMARY KEY,          -- gerada pelo CLIENTE, única por intenção
  requisicao_hash TEXT NOT NULL,          -- para detectar reuso da chave com corpo diferente
  resposta     JSONB,                     -- a resposta original, para repetir
  estado       TEXT NOT NULL CHECK (estado IN ('em_curso','concluida')),
  criada_em    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```
1. Cliente gera uma chave (UUID) por INTENÇÃO — não por tentativa.
2. Servidor tenta INSERT ... ON CONFLICT DO NOTHING.
   - inseriu   -> é a primeira vez: execute, grave a resposta, marque 'concluida'
   - não inseriu, estado='concluida'  -> devolva a resposta guardada, sem reexecutar
   - não inseriu, estado='em_curso'   -> 409 "em processamento, tente de novo"
3. Se o hash do corpo diferir do guardado -> 422: a mesma chave com pedido diferente
```

Detalhes que fazem diferença na prática:

- **A chave vem do cliente**, e é a mesma em todas as tentativas do mesmo pedido. Se o cliente
  gerar uma chave nova a cada retentativa, a proteção não existe.
- **Guarde a resposta**, não só a marca de "já feito": a retentativa precisa receber a mesma
  resposta da primeira vez, ou o cliente conclui que falhou.
- **Confira o hash do corpo.** Chave repetida com corpo diferente é bug do cliente e precisa
  ser denunciado, não silenciosamente ignorado.
- **Expire as chaves** (24 h a 7 dias, conforme o negócio) ou a tabela cresce para sempre.
- O estado `em_curso` cobre o caso de a retentativa chegar **enquanto** a primeira ainda
  executa. Sem ele, duas execuções simultâneas passam.

### 3.2 Idempotência e OCC são ortogonais

| Protege contra | Mecanismo |
|---|---|
| sobrescrever o trabalho **de outro** | `If-Match` / coluna de versão |
| executar **o seu próprio** pedido duas vezes | chave de idempotência |

Rotas de escrita com efeito externo costumam precisar dos dois. Confundi-los é comum:
`Idempotency-Key` não impede lost update, e `If-Match` não impede cobrança dupla.

---

## 4. Efeitos externos dentro de um bloco retentado

O erro mais caro deste assunto:

```javascript
// ERRADO: o e-mail é enviado a cada tentativa
await comRetentativa(async () => {
  const p = await ler(id);
  await enviarEmail(p.cliente, 'Pedido confirmado');   // <<< efeito externo!
  await gravar(id, { status: 'confirmado' }, p.version);
});
```

Três conflitos, três e-mails. Correções, em ordem de preferência:

```javascript
// CERTO 1 — o efeito externo sai do bloco retentado
const r = await comRetentativa(async () => {
  const p = await ler(id);
  return gravar(id, { status: 'confirmado' }, p.version);
});
await enviarEmail(r.valor.cliente, 'Pedido confirmado');   // uma vez só, após o sucesso
```

```javascript
// CERTO 2 — outbox transacional: grave a intenção na MESMA transação,
// e deixe um worker separado entregar. Sobrevive a queda do processo.
db.exec('BEGIN');
  // UPDATE ... WHERE version = ?
  db.prepare('INSERT INTO outbox (tipo, payload) VALUES (?, ?)')
    .run('email_confirmacao', JSON.stringify({ pedido: id }));
db.exec('COMMIT');
```

O padrão **outbox** é a resposta madura: ele resolve, de uma vez, a retentativa e a queda do
processo entre gravar e notificar. Custa um worker e uma tabela.

---

## 5. Quando a retentativa é o problema

Retentativa mal calibrada **causa** indisponibilidade. Três modos de falha, todos reais:

### 5.1 Amplificação em cascata

Três camadas com 3 tentativas cada produzem **27** chamadas ao serviço do fim. Sob degradação,
a carga sobe 27 vezes exatamente quando ele menos aguenta.

**Correção:** retente numa camada só — a mais próxima do problema. As demais propagam.
Se precisar de retentativa em mais de uma, use **orçamento de retentativa** (um percentual do
tráfego, tipo 10%) em vez de contagem por requisição — é o que o Envoy e o Finagle chamam de
*retry budget*.

### 5.2 Efeito manada

Todos os clientes falham juntos e voltam juntos. Sem jitter, a segunda rodada é idêntica à
primeira. **Correção:** jitter, sempre.

### 5.3 Retentativa mascarando problema estrutural

Uma taxa de conflito de 40% "resolvida" com 50 tentativas: os erros somem do painel e a
latência p99 vai para 3 segundos. Ninguém investiga porque não há erro.

**Correção:** alerte sobre **tentativas por operação bem-sucedida**, não só sobre erros.
Se a média passar de ~1,5, há um problema de modelagem esperando para piorar.

---

## 6. O que medir

| Métrica | Como | Alerta quando |
|---|---|---|
| Taxa de conflito | `conflitos / escritas_tentadas`, por tabela e por rota | > 5% |
| Tentativas por sucesso | histograma | média > 1,5 ou p99 > 5 |
| Falhas após esgotar | contador | qualquer valor não trivial |
| Latência com e sem conflito | dois histogramas separados | a diferença revela o custo real |
| Distância de versão | `versao_atual − versao_enviada` | mediana > 1 indica linha quente |
| Chaves de idempotência reusadas | contador | > 0 com corpo diferente = bug de cliente |

A **distância de versão** é a métrica mais subestimada da lista. Se ela é sempre 1, você tem
corridas ocasionais entre dois atores — normal. Se é 5, há uma multidão escrevendo na mesma
linha e nenhuma retentativa vai consertar isso: é hora de reprojetar.

---

## 7. Modelo de implementação

```javascript
/**
 * Retentativa com orçamento de tempo, jitter e classificação de erro.
 * Ponto crucial: `fn` recebe o número da tentativa e DEVE reler o estado.
 */
export async function comRetentativa(fn, {
  orcamentoMs = 800,
  baseMs = 10,
  tetoMs = 200,
  maxTentativas = 6,
  retentavel = (e) => e.name === 'ConflitoDeVersao' || e.status === 412 || e.code === '40001',
  aoRetentar = () => {},          // gancho de métrica
} = {}) {
  const prazo = Date.now() + orcamentoMs;
  let ultimo;

  for (let i = 0; i < maxTentativas; i++) {
    try {
      return { valor: await fn(i), tentativas: i + 1 };
    } catch (e) {
      if (!retentavel(e)) throw e;                    // bug ou erro permanente: suba já
      ultimo = e;
      aoRetentar(i, e);
      const atraso = Math.floor(Math.random() * Math.min(tetoMs, baseMs * 2 ** i));
      if (Date.now() + atraso >= prazo) break;        // não estoure o orçamento
      await new Promise((r) => setTimeout(r, atraso));
    }
  }
  throw Object.assign(
    new Error('conflito persistente: orçamento de retentativa esgotado'),
    { causa: ultimo, permanente: true }
  );
}
```

Versão em uso e testada: [`07-projeto-modelo/src/retry.js`](07-projeto-modelo/src/retry.js).

---

## Autoteste

1. Qual é a pergunta que decide se uma operação pode ser retentada automaticamente?
2. Dê um exemplo de operação que **não** deve ser retentada sem intervenção humana.
3. O que cada peça da fórmula de backoff resolve? O que acontece sem jitter?
4. Por que orçamento de tempo é melhor que contagem de tentativas?
5. Por que `428` nunca deve ser retentado?
6. Em que sentido a guarda de versão já torna o `UPDATE` idempotente?
7. Descreva o fluxo completo de uma chave de idempotência, incluindo o estado `em_curso`.
8. Três camadas com 3 tentativas cada geram quantas chamadas no pior caso? Qual a correção?
9. O que a "distância de versão" revela que a taxa de conflito não revela?
