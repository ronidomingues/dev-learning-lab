# 17 · HTTP e APIs — o optimistic locking que já estava no protocolo

`Nível: intermediário → avançado` · `Atualizado em: 14/08/2026`
`Referência normativa: RFC 9110 (HTTP Semantics, junho de 2022), §8.8 e §13`

A web resolveu este problema em 1997 e a maioria das APIs de 2026 ignora a solução. Este
arquivo mostra o mecanismo padrão, os detalhes que derrubam integrações reais, e como projetar
uma API que não perde escritas.

---

## 1. Por que a janela do HTTP é a pior de todas

```
GET /pedido/42          ──► [servidor lê, responde]  ◄── transação nº 1, dura 3 ms
      ⋮
      ⋮   o usuário lê a tela, atende o telefone, almoça, volta   ← 5 s a 5 horas
      ⋮
PUT /pedido/42          ──► [servidor grava]         ◄── transação nº 2, dura 4 ms
```

Nenhum nível de isolamento cobre esse intervalo, porque **não existe transação ali**. O
servidor sequer sabe que o usuário está com um formulário aberto. E não pode saber: o HTTP é
sem estado por projeto, e essa foi a decisão que permitiu a web escalar.

Consequência: **a única proteção possível é o cliente devolver o que leu.** É exatamente o que
`If-Match` faz.

---

## 2. O mecanismo padrão

```http
GET /pedido/42 HTTP/1.1

HTTP/1.1 200 OK
ETag: "7"
Content-Type: application/json

{ "id": 42, "status": "aberto", "total": 1500 }
```

```http
PUT /pedido/42 HTTP/1.1
If-Match: "7"
Content-Type: application/json

{ "status": "pago", "total": 1500 }

HTTP/1.1 200 OK
ETag: "8"
```

```http
PUT /pedido/42 HTTP/1.1
If-Match: "7"

HTTP/1.1 412 Precondition Failed
ETag: "9"
Content-Type: application/json

{ "erro": "conflito", "versao_enviada": "7", "versao_atual": "9",
  "atual": { "id": 42, "status": "cancelado", "total": 1500 } }
```

Três regras que fazem a diferença entre uma API correta e uma API que só parece correta:

1. **Toda resposta de leitura de um recurso mutável leva `ETag`.** Sem isso o cliente não tem
   o que devolver.
2. **Toda resposta de escrita bem-sucedida leva o `ETag` novo.** Sem isso o cliente precisa de
   um `GET` extra para poder editar de novo — e essa ida e volta é uma janela nova de conflito.
3. **O corpo do `412` carrega o estado atual.** Idem.

---

## 3. Os detalhes que quebram integrações

### 3.1 ETag fraco não serve para `If-Match`

A RFC 9110 define duas formas de comparação:

| Comparação | Usada em | ETag fraco (`W/"7"`) casa? |
|---|---|---|
| **forte** | `If-Match` | **não** |
| fraca | `If-None-Match` | sim |

Um ETag fraco significa "semanticamente equivalente, mas talvez não byte a byte" — útil para
cache, inútil para decidir se você pode sobrescrever.

**A pegadinha prática:** o Express (Node) gera **ETags fracos por padrão** para respostas JSON.
Uma API construída em Express que emite `W/"..."` e espera `If-Match` de volta vai recusar
todas as escritas, para sempre, com `412`. E o sintoma não sugere a causa.

```javascript
app.set('etag', 'strong');   // ou gere o ETag você mesmo, a partir da versão
```

### 3.2 `If-Match: *` não protege nada

`If-Match: *` significa apenas *"o recurso precisa existir"*. Não compara versão nenhuma.
Clientes que mandam `*` para "satisfazer o servidor" desativam a proteção mantendo a aparência
dela. Se o seu servidor aceita `*` em `PUT`, no mínimo registre o fato — o projeto-modelo
devolve um cabeçalho `X-Aviso` justamente por isso.

O uso legítimo do curinga é o **inverso**, para criação:

```http
PUT /pedido/42
If-None-Match: *          → crie apenas se ainda não existir
                          → 201 se criou, 412 se já existia
```

### 3.3 Proxies, CDNs e compressão

Um intermediário que recomprima ou transforme a resposta **pode alterar o `ETag`** — a RFC
permite. Se a sua CDN mexe no corpo (minificação, `Content-Encoding` diferente) e reescreve o
validador, o `If-Match` do cliente deixa de casar.

Mitigação: emita o ETag a partir da **versão do recurso**, não do corpo serializado, e
configure a CDN para não gerar validadores próprios em rotas de escrita.

### 3.4 `Last-Modified` tem resolução de um segundo

`If-Unmodified-Since` é a alternativa por data e é **estruturalmente insuficiente**: o formato
de data do HTTP tem resolução de segundos. Duas escritas no mesmo segundo passam sem detecção.
Use-o apenas como reserva para clientes antigos, nunca como proteção principal.

### 3.5 O corpo do `412` e o cache

Alguns clientes e bibliotecas descartam o corpo de respostas 4xx. Se o seu cliente faz isso,
o estado atual que você devolveu se perde. Documente que o corpo do `412` é significativo —
ou repita a informação essencial em cabeçalhos (`ETag` no mínimo).

---

## 4. `409` ou `412`? O debate, resolvido

Encontro esta dúvida em toda revisão de API. A distinção correta:

| | `412 Precondition Failed` | `409 Conflict` |
|---|---|---|
| Significa | **a pré-condição que você enviou não é verdadeira** | **o pedido conflita com o estado atual do recurso** |
| Depende de | um cabeçalho condicional (`If-Match`) | a semântica do recurso |
| Exemplo | `If-Match: "7"`, mas o recurso está em `"9"` | "não dá para pagar um pedido cancelado" |
| O cliente resolve como | reler, mesclar, retentar | mudar o pedido; retentar não adianta |

**Regra:** se a recusa veio da avaliação de um cabeçalho condicional, é `412`. Se veio de uma
regra de negócio, é `409`. As duas podem coexistir na mesma API — e devem.

Casos reais que confundem:

- **Versão no corpo do JSON, não em `If-Match`.** Aí, tecnicamente, não houve pré-condição
  HTTP: `409` é mais defensável. Mas prefira mover a versão para `If-Match` e usar `412` —
  você ganha interoperabilidade com caches, clientes HTTP genéricos e ferramentas.
- **`428 Precondition Required`.** Use quando o cliente **omitiu** `If-Match` e o servidor
  exige. É a diferença entre um servidor que protege e um servidor cúmplice. Foi definido na
  RFC 6585 e incorporado à prática comum.
- **`423 Locked`** (WebDAV) é para lock pessimista de verdade. Não use para conflito otimista.

---

## 5. Projetando a API inteira

### 5.1 Onde colocar a versão

| Lugar | Prós | Contras |
|---|---|---|
| `If-Match` / `ETag` | padrão, funciona com caches e ferramentas, semântica clara | precisa de cabeçalho; alguns clientes de baixo nível dificultam |
| Campo no corpo (`"version": 7`) | fácil em formulários e GraphQL | não é padrão HTTP; caches ignoram; `PATCH` fica estranho |
| Parâmetro de query (`?version=7`) | fácil de testar | **evite**: polui a URL e mistura identidade com estado |

Recomendação: **`If-Match` como contrato principal**, e aceitar a versão no corpo como
compatibilidade para clientes que não conseguem enviar cabeçalhos.

### 5.2 `PUT` vs. `PATCH`

`PATCH` reduz naturalmente o escopo do conflito: se o cliente envia só o campo que mudou, duas
edições de campos diferentes não se contradizem. Mas `PATCH` **não dispensa** `If-Match` —
sem ele, dois `PATCH` no mesmo campo ainda perdem um.

Combinação que funciona bem:

```http
PATCH /pedido/42
If-Match: "7"
Content-Type: application/merge-patch+json

{ "status": "pago" }
```

Com `PATCH` + `If-Match`, você tem detecção **e** escopo reduzido — o melhor dos dois.

### 5.3 Operações em lote

Aqui não há padrão e há muita API ruim. As opções:

| Estratégia | Semântica | Quando |
|---|---|---|
| Tudo ou nada | um conflito aborta o lote inteiro | quando os itens são interdependentes |
| Melhor esforço | aplica o que dá, relata os conflitos | importações, sincronização |
| Por item | cada item traz sua própria versão | sempre que possível |

Recomendo **por item + melhor esforço**, com `207 Multi-Status` (ou `200` com um corpo de
resultados por item):

```json
{
  "resultados": [
    { "id": 1, "status": 200, "etag": "\"8\"" },
    { "id": 2, "status": 412, "versao_atual": "\"5\"", "atual": { } },
    { "id": 3, "status": 200, "etag": "\"3\"" }
  ]
}
```

O que **não** fazer: aceitar um lote sem versão nenhuma "porque é interno". Jobs de lote são
justamente os que sobrescrevem mais dados de uma vez quando dão errado.

### 5.4 Idempotência é outro problema

`If-Match` protege contra **sobrescrever trabalho alheio**. Não protege contra **executar duas
vezes o seu próprio pedido** (o cliente reenviou por timeout de rede). Para isso existe a
chave de idempotência:

```http
POST /pagamento
Idempotency-Key: 8f3c-…-a91
If-Match: "7"
```

São mecanismos ortogonais e você costuma precisar dos dois em rotas de escrita com efeito
externo. Ver [`19-retentativa-e-idempotencia.md`](19-retentativa-e-idempotencia.md).

---

## 6. Do lado do cliente

O erro mais comum não é deixar de enviar `If-Match`: é **enviar um `ETag` velho por causa de
cache local**.

```javascript
// Guarde o ETag JUNTO com os dados, e atualize os dois na mesma operação.
const cache = new Map();   // id -> { dados, etag }

async function carregar(id) {
  const r = await fetch(`/pedido/${id}`);
  const dados = await r.json();
  cache.set(id, { dados, etag: r.headers.get('etag') });   // sempre juntos
  return dados;
}

async function salvar(id, dados) {
  const { etag } = cache.get(id) ?? {};
  if (!etag) throw new Error('sem ETag: carregue antes de salvar');

  const r = await fetch(`/pedido/${id}`, {
    method: 'PUT',
    headers: { 'content-type': 'application/json', 'if-match': etag },
    body: JSON.stringify(dados),
  });

  if (r.status === 412) {
    const conflito = await r.json();
    cache.set(id, { dados: conflito.atual, etag: r.headers.get('etag') });  // atualize os dois
    throw new ConflitoDeVersao(conflito);                                    // deixe a UI decidir
  }
  if (!r.ok) throw new Error(`HTTP ${r.status}`);

  cache.set(id, { dados, etag: r.headers.get('etag') });
  return dados;
}
```

Regras do lado do cliente:

1. **Dados e ETag vivem juntos.** Guardá-los em lugares diferentes garante que um dia vão
   divergir.
2. **Atualize o ETag também no `412`.** É o principal ganho de o servidor devolver o estado.
3. **Não retente automaticamente uma edição feita por humano.** Retentar significa aplicar a
   decisão dele sobre um estado que ele não viu. Suba o conflito para a interface.
4. **`If-None-Match` nos `GET`** economiza banda de verdade: um `304` não transfere corpo.

---

## 7. Lista de verificação da sua API

- [ ] Todo `GET` de recurso mutável devolve `ETag`.
- [ ] O `ETag` é **forte** (sem `W/`).
- [ ] Todo `PUT`/`PATCH`/`DELETE` exige `If-Match` e responde `428` sem ele.
- [ ] `412` devolve o `ETag` novo **e** o estado atual no corpo.
- [ ] `409` é usado só para conflito de regra de negócio, e está documentado.
- [ ] `DELETE` também aceita `If-Match` (apagar a versão errada é um lost update também).
- [ ] Rotas em lote levam versão **por item** e devolvem resultado por item.
- [ ] A CDN/proxy não reescreve validadores nas rotas de escrita.
- [ ] Rotas com efeito externo aceitam `Idempotency-Key`.
- [ ] A documentação (OpenAPI) descreve `ETag`, `If-Match`, `412` e `428` como parte do
      contrato, não como detalhe.
- [ ] Existe métrica de `412` por rota, no painel.

O último item é o que transforma tudo isso em engenharia: sem medir, você não sabe se a
proteção está sendo usada nem se está cara demais.

---

## Autoteste

1. Por que nenhum nível de isolamento pode proteger a janela entre `GET` e `PUT`?
2. Por que `W/"7"` nunca casa com `If-Match`? Qual framework popular cai nessa por padrão?
3. O que `If-Match: *` realmente garante? E `If-None-Match: *`?
4. Enuncie a regra que distingue `409` de `412`, e dê um exemplo de cada.
5. Quando usar `428`, e o que ele diz sobre a postura do servidor?
6. Por que `PATCH` reduz o conflito mas não dispensa `If-Match`?
7. Qual é o erro de cache mais comum no cliente, e como evitá-lo?
8. Por que `If-Match` e `Idempotency-Key` resolvem problemas diferentes?

---

## Fontes consultadas (14/08/2026)

- [RFC 9110 — HTTP Semantics (junho de 2022)](https://datatracker.ietf.org/doc/html/rfc9110) — §8.8 validadores, §13 requisições condicionais, §15.5.13 (412)
- [RFC 7232 — Conditional Requests (obsoleta pela 9110)](https://httpwg.org/specs/rfc7232.html)
- [MDN — cabeçalho `If-Match`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match)
- [MDN — cabeçalho `If-None-Match`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-None-Match)
- [http.dev — guia de requisições condicionais](https://http.dev/conditional-requests)
