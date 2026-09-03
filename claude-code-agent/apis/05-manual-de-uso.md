# 05 · Manual de uso — referência consultável

`Nível: intermediário` · `Atualizado: 11/08/2026`

Organizado **por tarefa**, não por ordem alfabética. Use `Ctrl+F`.

---

## Índice

1. [Métodos HTTP](#1-métodos-http)
2. [Códigos de status](#2-códigos-de-status)
3. [Cabeçalhos de requisição](#3-cabeçalhos-de-requisição)
4. [Cabeçalhos de resposta](#4-cabeçalhos-de-resposta)
5. [curl — receituário](#5-curl--receituário)
6. [HTTPie — equivalências](#6-httpie--equivalências)
7. [jq — receituário](#7-jq--receituário)
8. [JSON — o formato em meia página](#8-json--o-formato-em-meia-página)
9. [Formatos de data, número e identificador](#9-formatos-de-data-número-e-identificador)
10. [URL: anatomia e codificação](#10-url-anatomia-e-codificação)
11. [Atalhos que só quem usa há anos conhece](#11-atalhos-que-só-quem-usa-há-anos-conhece)
12. [O que está obsoleto](#12-o-que-está-obsoleto)

---

## 1. Métodos HTTP

| Método | Faz | Seguro? | Idempotente? | Tem corpo? | Cacheável? |
|---|---|---|---|---|---|
| **GET** | lê um recurso | ✅ | ✅ | não (por convenção) | ✅ |
| **HEAD** | igual ao GET, sem corpo | ✅ | ✅ | não | ✅ |
| **POST** | cria, ou executa uma ação | ❌ | ❌ | sim | raramente |
| **PUT** | substitui o recurso inteiro | ❌ | ✅ | sim | ❌ |
| **PATCH** | altera parte do recurso | ❌ | ❌* | sim | ❌ |
| **DELETE** | remove o recurso | ❌ | ✅ | opcional | ❌ |
| **OPTIONS** | pergunta o que é permitido | ✅ | ✅ | não | ❌ |

\* PATCH **pode** ser idempotente, dependendo de como você define a operação.
`{"nome": "Maria"}` é idempotente; `{"op": "incrementar", "campo": "saldo"}` não é.

**Os dois adjetivos que confundem todo mundo:**

- **Seguro** (*safe*) = **não altera nada** no servidor. Um `GET` pode ser repetido por um
  crawler, um pré-carregador do navegador ou um proxy, sem consequência.
- **Idempotente** = **repetir tem o mesmo efeito que fazer uma vez**. Apagar duas vezes
  deixa o recurso apagado, não "duas vezes apagado".

**Por que isso importa na prática, e não é teoria:** se um método é idempotente, o cliente
**pode retentar automaticamente** quando a rede falhar. Se não é, retentar pode duplicar —
um pedido, uma cobrança, um e-mail. É a razão de existir a chave de idempotência
([14-design-de-api-rest.md](14-design-de-api-rest.md) §7).

> **Nunca use GET para alterar estado.** Parece óbvio, e ainda assim `GET /usuarios/42/apagar`
> existe em produção mundo afora. O pré-carregador do navegador, o antivírus corporativo e o
> bot de indexação vão apagar seus dados sem que ninguém clique em nada. Já aconteceu com
> empresas grandes.

---

## 2. Códigos de status

### 2.1 As cinco famílias

| Faixa | Significa | Quem errou |
|---|---|---|
| **1xx** | informativo, continue | ninguém |
| **2xx** | deu certo | ninguém |
| **3xx** | redirecionamento / cache | ninguém |
| **4xx** | **o cliente errou** | você, que chamou |
| **5xx** | **o servidor errou** | eles |

**A divisão 4xx/5xx é a informação mais útil de todo o HTTP.** Ela diz de quem é a culpa,
e portanto quem tem que agir. `4xx` = corrija sua requisição. `5xx` = retente, e se
persistir, abra um chamado.

### 2.2 Os que você realmente vai usar

| Código | Nome | Quando usar |
|---|---|---|
| **200** | OK | leitura ou atualização bem-sucedida, com corpo |
| **201** | Created | criou um recurso. **Envie `Location`** apontando para ele |
| **202** | Accepted | aceitei, vou processar depois. Envie como acompanhar |
| **204** | No Content | deu certo e não há corpo (típico de `DELETE` e `PUT`) |
| **206** | Partial Content | resposta parcial (`Range`) |
| **301** | Moved Permanently | mudou de endereço para sempre. Cacheado agressivamente |
| **302 / 307** | Found / Temporary Redirect | mudou temporariamente. **307 preserva o método**; 302 não necessariamente |
| **304** | Not Modified | nada mudou; use seu cache |
| **400** | Bad Request | requisição malformada (JSON inválido, parâmetro ausente) |
| **401** | Unauthorized | **não autenticado** — você não disse quem é |
| **403** | Forbidden | **autenticado, mas sem permissão** |
| **404** | Not Found | não existe |
| **405** | Method Not Allowed | o caminho existe, o método não. **Envie `Allow`** |
| **406** | Not Acceptable | não consigo produzir o formato que você pediu no `Accept` |
| **409** | Conflict | conflito de estado (duplicata, edição concorrente) |
| **410** | Gone | existiu e foi removido de propósito, permanentemente |
| **412** | Precondition Failed | a condição do `If-Match` não bateu |
| **413** | Content Too Large | corpo grande demais |
| **415** | Unsupported Media Type | não aceito esse `Content-Type` |
| **422** | Unprocessable Content | sintaxe válida, **semântica inválida** (falhou validação) |
| **428** | Precondition Required | exijo `If-Match` para evitar sobrescrita cega |
| **429** | Too Many Requests | estourou o limite. **Envie `Retry-After`** |
| **500** | Internal Server Error | eu quebrei e não sei explicar |
| **501** | Not Implemented | não implementei esse método |
| **502** | Bad Gateway | eu sou um proxy e quem está atrás de mim falhou |
| **503** | Service Unavailable | indisponível, temporariamente. **Envie `Retry-After`** |
| **504** | Gateway Timeout | eu sou um proxy e quem está atrás demorou demais |

### 2.3 Os pares que todo mundo confunde

| Confusão | A diferença |
|---|---|
| **401 vs. 403** | 401 = "não sei quem você é" (falta ou falhou a credencial). 403 = "sei quem você é e você não pode". Mnemônico: 401 → faça login; 403 → peça permissão |
| **400 vs. 422** | 400 = não consegui **entender** (JSON quebrado, tipo errado). 422 = entendi e **discordo** (CPF inválido, data no passado) |
| **404 vs. 403** | Se revelar a existência do recurso já é um vazamento, devolva **404** mesmo sem permissão. É a escolha certa para IDs sequenciais |
| **404 vs. 410** | 404 = não achei (pode nunca ter existido). 410 = existiu e foi removido de propósito. 410 diz ao cliente para parar de tentar |
| **409 vs. 412** | 409 = conflito de negócio (e-mail já cadastrado). 412 = a **pré-condição** que você enviou não bate (o `ETag` mudou) |
| **502 vs. 503 vs. 504** | 502 = o de trás respondeu errado. 503 = eu estou fora. 504 = o de trás demorou |

> **A regra que resolve 90% das dúvidas:** devolva `4xx` quando repetir a mesma requisição
> vai falhar de novo, e `5xx` quando repetir pode funcionar. Isso é literalmente o que o
> cliente precisa saber para decidir se retenta.

---

## 3. Cabeçalhos de requisição

| Cabeçalho | Para quê | Exemplo |
|---|---|---|
| `Accept` | que formato eu quero de volta | `application/json` |
| `Accept-Language` | em que idioma | `pt-BR, pt;q=0.9, en;q=0.8` |
| `Accept-Encoding` | que compressão eu aceito | `gzip, br, zstd` |
| `Content-Type` | o formato do que **estou enviando** | `application/json; charset=utf-8` |
| `Content-Length` | tamanho do corpo em bytes | `348` |
| `Authorization` | credencial | `Bearer eyJhbGci...` |
| `User-Agent` | quem sou eu | `meu-app/1.2.0 (contato@empresa.com)` |
| `If-None-Match` | só me responda se o ETag mudou | `W/"abc123"` |
| `If-Match` | só altere se o ETag ainda for este | `"abc123"` |
| `If-Modified-Since` | só me responda se mudou depois de… | `Tue, 11 Aug 2026 12:00:00 GMT` |
| `Idempotency-Key` | chave para não duplicar em retentativa | `9f2a-...` |
| `Prefer` | preferência de comportamento | `return=minimal`, `respond-async` |
| `Range` | quero só um pedaço | `bytes=0-1023` |
| `Origin` | de que site o navegador está chamando | `https://app.exemplo.com` |
| `X-Request-Id` / `Traceparent` | correlação entre serviços | `00-4bf92f...-01` |

**Sobre o `User-Agent`:** parece formalidade e não é. Quando sua integração começar a se
comportar mal, o time da API vai procurar quem está causando. Um `User-Agent` com o nome do
seu sistema e um e-mail de contato faz a diferença entre "vamos avisar essa equipe" e
"vamos bloquear esse IP". Várias APIs públicas **exigem** um `User-Agent` identificável.

---

## 4. Cabeçalhos de resposta

| Cabeçalho | Para quê |
|---|---|
| `Content-Type` | formato do corpo |
| `Content-Length` | tamanho |
| `Cache-Control` | política de cache (§4.1) |
| `ETag` | impressão digital da representação |
| `Last-Modified` | quando mudou pela última vez |
| `Location` | onde está o recurso criado (`201`) ou para onde ir (`3xx`) |
| `Allow` | métodos permitidos (obrigatório em `405`) |
| `Retry-After` | quantos segundos esperar (`429`, `503`) — ou uma data |
| `Link` | links de navegação, RFC 8288 (paginação!) |
| `Vary` | quais cabeçalhos da requisição afetam a resposta |
| `WWW-Authenticate` | como se autenticar (obrigatório em `401`) |
| `RateLimit` / `RateLimit-Policy` | cota restante (formato em padronização na IETF) |
| `X-RateLimit-*` | a versão de facto, ainda dominante |
| `Strict-Transport-Security` | force HTTPS daqui em diante |
| `Content-Security-Policy` | política de conteúdo (relevante se a API serve HTML) |
| `Access-Control-Allow-*` | CORS ([12](12-http-por-dentro.md) §9) |
| `Deprecation` / `Sunset` | esta API vai morrer; quando |

### 4.1 `Cache-Control` — as diretivas que importam

| Diretiva | Efeito |
|---|---|
| `public` | qualquer cache pode guardar (CDN, proxy) |
| `private` | só o navegador do usuário |
| `no-cache` | **pode guardar, mas revalide antes de usar** |
| `no-store` | **não guarde em lugar nenhum** — para dado sensível |
| `max-age=600` | válido por 600 segundos |
| `s-maxage=3600` | validade para caches compartilhados (sobrepõe `max-age`) |
| `must-revalidate` | ao expirar, é obrigatório revalidar (não sirva vencido) |
| `stale-while-revalidate=60` | sirva o vencido por 60 s enquanto busca o novo |
| `immutable` | nunca muda; nem revalide |

> **`no-cache` não significa "não use cache".** Significa "guarde, mas pergunte antes de
> servir". Quem quer proibir o armazenamento precisa de **`no-store`**. Essa confusão de
> nomenclatura é histórica e já vazou dado sensível para cache de proxy corporativo em
> incidentes reais.

### 4.2 `Vary` — o cabeçalho que evita servir a resposta errada

```http
Vary: Accept, Accept-Language, Authorization
```

Diz ao cache: "esta resposta depende desses cabeçalhos; não sirva a versão em português
para quem pediu inglês". **Esquecer `Vary: Authorization` numa resposta cacheável faz uma
CDN servir os dados de um usuário para outro.** É uma das piores falhas possíveis, e é
fácil de cometer.

---

## 5. curl — receituário

### 5.1 O básico

| Quero | Comando |
|---|---|
| GET simples | `curl https://api.exemplo.com/livros` |
| Sem barra de progresso | `curl -s ...` |
| Ver cabeçalhos + corpo | `curl -i ...` |
| Ver **só** cabeçalhos (faz HEAD) | `curl -I ...` |
| Ver tudo, inclusive o que foi enviado | `curl -v ...` |
| Ver ainda mais (TLS, DNS) | `curl --trace-ascii - ...` |
| Seguir redirecionamento | `curl -L ...` |
| Salvar em arquivo | `curl -o saida.json ...` |
| Salvar com o nome remoto | `curl -O https://.../arquivo.zip` |

### 5.2 Enviar dados

```bash
# JSON (forma longa, universal)
curl -X POST https://api.exemplo.com/livros \
  -H 'Content-Type: application/json' \
  -d '{"titulo":"Iracema","autor":"José de Alencar"}'

# JSON (atalho do curl 7.82+: define Content-Type e Accept sozinho)
curl --json '{"titulo":"Iracema"}' https://api.exemplo.com/livros

# JSON de um arquivo
curl -X POST https://api.exemplo.com/livros \
  -H 'Content-Type: application/json' \
  -d @corpo.json

# Formulário
curl -X POST https://api.exemplo.com/login \
  -d 'usuario=maria' -d 'senha=segredo'

# Upload de arquivo (multipart)
curl -X POST https://api.exemplo.com/anexos \
  -F 'arquivo=@contrato.pdf' -F 'descricao=Contrato assinado'

# Corpo vindo do stdin
echo '{"a":1}' | curl -X POST --json @- https://api.exemplo.com/x
```

### 5.3 Autenticação

```bash
curl -H "Authorization: Bearer $TOKEN" ...              # token / OAuth / JWT
curl -u usuario:senha ...                                # Basic (peça a senha!)
curl -u usuario ...                                      # Basic, pedindo a senha sem eco
curl -H "X-API-Key: $CHAVE" ...                          # chave de API em cabeçalho
curl --cert cliente.pem --key cliente.key ...            # mTLS
curl --netrc                                             # lê ~/.netrc (chmod 600)
```

> `-u usuario:senha` coloca a senha no histórico do shell e na lista de processos
> (`ps aux` mostra). Use `-u usuario` (sem senha) e deixe o curl perguntar, ou `--netrc`.

### 5.4 Medir e diagnosticar

```bash
# Status, tempo e protocolo em uma linha
curl -s -o /dev/null -w '%{http_code} %{time_total}s http/%{http_version}\n' https://api.exemplo.com/

# Onde o tempo foi gasto
curl -s -o /dev/null -w '
  dns:      %{time_namelookup}s
  tcp:      %{time_connect}s
  tls:      %{time_appconnect}s
  1º byte:  %{time_starttransfer}s
  total:    %{time_total}s
  tamanho:  %{size_download} bytes
  redirect: %{num_redirects}
' https://api.exemplo.com/
```
*Se `dns` for alto, o problema é resolução de nome. Se `tls` for alto, é handshake. Se o
salto for entre `tls` e `1º byte`, o servidor é que está lento. **Esse comando substitui
meia hora de suposição.***

```bash
curl --http1.1 ...     # força HTTP/1.1
curl --http2 ...       # força HTTP/2
curl --http3 ...       # força HTTP/3 (se o curl tiver suporte compilado)
curl --resolve api.exemplo.com:443:203.0.113.10 https://api.exemplo.com/  # testa um IP específico
curl --max-time 10 --connect-timeout 3 ...    # timeouts explícitos
curl --retry 3 --retry-delay 2 --retry-all-errors ...   # retentativa
```

### 5.5 Cache e condicionais

```bash
curl -H 'If-None-Match: "abc123"' ...        # espera 304
curl -H 'If-Match: "abc123"' -X PUT ...      # falha com 412 se mudou
curl -H 'Cache-Control: no-cache' ...        # força revalidação
```

### 5.6 Sessões e cookies

```bash
curl -c cookies.txt -d 'usuario=maria&senha=x' https://exemplo.com/login   # grava
curl -b cookies.txt https://exemplo.com/perfil                              # usa
```

---

## 6. HTTPie — equivalências

| curl | HTTPie |
|---|---|
| `curl https://api.x.com/a` | `http api.x.com/a` |
| `curl -X POST ... -d '{"n":"M"}'` | `http POST api.x.com/a n=M` |
| `-d '{"idade":30}'` (número) | `idade:=30` |
| `-d '{"tags":["a","b"]}'` | `tags:='["a","b"]'` |
| `-H 'Accept: application/json'` | `Accept:application/json` |
| `?q=machado` | `q==machado` |
| `-H "Authorization: Bearer $T"` | `-A bearer -a $T` |
| `-u user:pass` | `-a user:pass` |
| `-F 'arq=@a.pdf'` | `-f arq@a.pdf` |
| `-i` | `--print=Hh` |
| `-v` | `-v` |

**A regra de sintaxe do HTTPie, em quatro símbolos:**
`=` string · `:=` JSON cru · `==` parâmetro de URL · `:` cabeçalho

---

## 7. jq — receituário

```bash
jq .                              # formata e colore
jq -r .campo                      # extrai um campo, sem aspas (raw)
jq '.a.b.c'                       # aninhado
jq '.itens[0]'                    # primeiro elemento
jq '.itens[]'                     # cada elemento, um por linha
jq '.itens | length'              # quantidade
jq -r '.itens[].nome'             # um campo de cada elemento
jq '.itens[] | select(.ativo)'    # filtra
jq '.itens | map(.preco) | add'   # soma
jq '{nome: .titulo, quem: .autor}'          # remodela
jq '.itens | sort_by(.preco) | reverse'     # ordena
jq '.itens | group_by(.tipo) | map({tipo: .[0].tipo, n: length})'   # agrupa
jq -r '.itens[] | [.id, .nome] | @csv'      # exporta CSV
jq '.. | .erro? // empty'                   # procura "erro" em qualquer profundidade
jq -s 'add'                                 # junta várias entradas em um array
jq --arg n "Maria" '.itens[] | select(.nome == $n)'   # variável externa (seguro)
jq -e '.ok'                       # define o código de saída — útil em scripts
```

**Combinações que você vai usar toda semana:**
```bash
# Extrair um token de uma resposta de login
TOKEN=$(curl -s -X POST https://api.x.com/login --json '{"u":"a","p":"b"}' | jq -r .access_token)

# Percorrer todas as páginas
url='https://api.github.com/repos/nodejs/node/tags?per_page=100'
while [ -n "$url" ]; do
  curl -s -D /tmp/h "$url" | jq -r '.[].name'
  url=$(grep -i '^link:' /tmp/h | tr ',' '\n' | grep 'rel="next"' | sed -E 's/.*<(.*)>.*/\1/')
done

# Falhar o script se a API devolver erro
curl -s https://api.x.com/a | jq -e '.status == "ok"' > /dev/null || { echo "falhou"; exit 1; }
```

---

## 8. JSON — o formato em meia página

```json
{
  "texto":    "aspas duplas, sempre",
  "numero":   42,
  "decimal":  3.14,
  "booleano": true,
  "nulo":     null,
  "lista":    [1, "dois", null],
  "objeto":   { "aninhado": true }
}
```

**As regras que pegam as pessoas:**

| Regra | Consequência |
|---|---|
| Só **aspas duplas**. Nunca simples | `{'a':1}` não é JSON |
| **Sem vírgula final** | `{"a":1,}` é inválido |
| **Sem comentários** | `// isto` quebra o parser |
| Chaves são sempre **strings** | `{1: "x"}` é inválido |
| Não há tipo **data** | datas são strings; ver §9 |
| Não há **inteiro vs. decimal** | tudo é `number` (IEEE 754 duplo) |
| Números grandes **perdem precisão** | acima de 2⁵³ (~9×10¹⁵), use string |
| A ordem das chaves **não é garantida** | nunca dependa dela |
| Codificação é **UTF-8** | RFC 8259 |

> **O erro de dinheiro:** `0.1 + 0.2 !== 0.3` em ponto flutuante binário. Nunca transmita
> valores monetários como `number`. Use **centavos em inteiro** (`"valor_centavos": 4790`)
> ou **string decimal** (`"valor": "47.90"`). Toda API de pagamento séria faz isso, e é
> por esse motivo.

**Alternativas ao JSON, e quando aparecem:**

| Formato | Onde |
|---|---|
| **JSON** | padrão de APIs web |
| **JSON Lines** (`.jsonl`) | streaming, logs, exportação grande — um objeto por linha |
| **XML** | SOAP, sistemas legados, governo |
| **Protobuf** | gRPC — binário, compacto, exige o `.proto` |
| **MessagePack / CBOR** | binário compacto, IoT |
| **YAML** | configuração e OpenAPI. **Nunca** como formato de resposta de API |
| **CSV** | exportação tabular |
| **Avro / Parquet** | dados analíticos |

---

## 9. Formatos de data, número e identificador

| Coisa | Use | Não use |
|---|---|---|
| Data e hora | **ISO 8601 / RFC 3339 em UTC**: `2026-08-11T14:30:00Z` | `11/08/2026 14:30`, timestamp Unix cru |
| Data sem hora | `2026-08-11` | `11-08-2026` |
| Duração | ISO 8601: `PT30M`, ou segundos: `1800` | `"30 min"` |
| Fuso | inclua o offset: `2026-08-11T11:30:00-03:00` | hora local sem offset |
| Dinheiro | inteiro em centavos + código ISO 4217: `{"valor_centavos": 4790, "moeda": "BRL"}` | float |
| Percentual | decimal explícito: `{"taxa": 0.075}` com o nome claro | `7.5` sem dizer se é % |
| Identificador | **string**, sempre | número (perde zeros à esquerda, e o tipo muda no futuro) |
| ID gerado | **UUIDv7** (ordenável no tempo) ou ULID | sequencial exposto (vaza volume de negócio) |
| Enumeração | string em maiúsculas: `"CANCELADO"` | número mágico: `3` |
| País, moeda, idioma | ISO 3166, ISO 4217, BCP 47 | invenção própria |

> **Por que UUIDv7 e não v4:** o v7 embute um timestamp no início, então ele é **ordenável**
> e agrupa bem em índice de banco de dados. O v4 é aleatório puro e causa fragmentação de
> índice em tabelas grandes. Ambos são globalmente únicos. UUIDv7 foi padronizado no
> **RFC 9562** (maio/2024), que substituiu o RFC 4122.

> **Por que não expor ID sequencial:** `/pedidos/1043` diz ao concorrente que você teve
> 1.043 pedidos. Pior: permite enumerar tudo (`/pedidos/1`, `/pedidos/2`…), que é a
> vulnerabilidade **BOLA**, a nº 1 do OWASP API Top 10 — ver [16-seguranca.md](16-seguranca.md) §7.

---

## 10. URL: anatomia e codificação

```text
https://api.exemplo.com:443/v1/livros/42?campos=titulo,autor&limite=10#secao
└─┬─┘   └──────┬──────┘└┬┘└─────┬──────┘└──────────┬──────────────────┘└─┬─┘
esquema     host      porta   caminho          query string          fragmento
                                                                    (NÃO vai ao servidor)
```

**Regras de codificação que causam bug silencioso:**

| Caractere | Em caminho | Em query | Percent-encoding |
|---|---|---|---|
| espaço | `%20` | `%20` ou `+` | `%20` |
| `/` | separador | `%2F` | `%2F` |
| `?` | `%3F` | separador | `%3F` |
| `&` | `%26` | separador | `%26` |
| `=` | ok | separador | `%3D` |
| `#` | `%23` | `%23` | `%23` |
| `+` | ok | **significa espaço!** | `%2B` |
| `ã`, `ç` | UTF-8 percent-encoded | idem | `%C3%A3` |

```bash
# Codificar com curl (não monte URL na mão com dados do usuário)
curl --get --data-urlencode 'q=máquina & ferramenta' https://api.exemplo.com/busca
```
```bash
# Codificar com jq
jq -rn --arg v 'máquina & ferramenta' '$v|@uri'
# esperado: m%C3%A1quina%20%26%20ferramenta
```

> **O `+` é a armadilha clássica.** Em query string, `+` historicamente significa espaço
> (herança de formulários HTML). Então `?email=maria+trabalho@x.com` chega ao servidor como
> `maria trabalho@x.com`, e o e-mail quebra. Sempre codifique `+` como `%2B`.

---

## 11. Atalhos que só quem usa há anos conhece

1. **DevTools → botão direito na requisição → "Copy as cURL"**. Você reproduz qualquer
   chamada de qualquer site no terminal, com cookies e cabeçalhos. É a forma mais rápida de
   entender uma API não documentada — e de reportar um bug com o comando exato.
2. **`curl -w` com o bloco de tempos** (§5.4) diagnostica lentidão em 5 segundos. Guarde-o
   num alias: `alias curltime='curl -s -o /dev/null -w "dns:%{time_namelookup} tls:%{time_appconnect} ttfb:%{time_starttransfer} total:%{time_total}\n"'`.
3. **`HEAD` antes de `GET`** quando você só quer saber se existe ou se mudou. É de graça.
4. **`OPTIONS <url>`** às vezes revela os métodos suportados numa API não documentada.
5. **Arquivos `.http`** (extensão REST Client do VS Code) versionam no Git e viram
   documentação executável do time. Melhor que uma coleção presa numa conta de SaaS.
6. **`jq -e`** define o código de saída do processo — é o que permite usar jq em `if` de
   script e falhar o pipeline de CI corretamente.
7. **Leia `Retry-After` antes de retentar.** Retentar imediatamente após `429` é a forma
   mais rápida de ser bloqueado.
8. **`Prefer: return=minimal`** faz algumas APIs devolverem `204` em vez do recurso inteiro.
   Em operações em massa, corta tráfego pela metade.
9. **`Vary: Authorization`** em toda resposta cacheável e autenticada. Sem ele, a CDN
   entrega os dados de um usuário a outro.
10. **`Idempotency-Key` em todo `POST` que movimenta dinheiro.** Se a API que você consome
    suportar, use. Se você está construindo, implemente.
11. **Paginação por cursor, não por offset**, em qualquer coisa que cresça. `?offset=100000`
    faz o banco varrer 100.000 linhas para descartá-las — e itens novos deslocam a janela,
    fazendo você pular ou repetir registros.
12. **Versione desde o dia 1** (`/v1/`), mesmo sozinho. Adicionar versão depois é
    retrocompatibilidade forçada para sempre.
13. **Um `User-Agent` com contato** transforma "vamos bloquear esse IP" em "vamos avisar essa
    equipe".
14. **Loga o `X-Request-Id`/`traceparent`** que a API devolve. Quando você abrir um chamado,
    é o único dado que permite ao suporte achar sua requisição entre bilhões.

---

## 12. O que está obsoleto

| Obsoleto | Substituto | Desde |
|---|---|---|
| **RFC 7807** (Problem Details) | **RFC 9457** | jul/2023 |
| RFCs 7230–7235 (HTTP) | **RFC 9110–9114** | jun/2022 |
| **RFC 4122** (UUID) | **RFC 9562** (inclui UUIDv7) | mai/2024 |
| **OAuth 2.0 Implicit Grant** | Authorization Code + **PKCE** | ~2019 |
| **OAuth 2.0 Password Grant** | Authorization Code + PKCE, ou Client Credentials | ~2019 |
| **Basic Auth** em API pública | Bearer token, OAuth, mTLS | há anos |
| **SOAP** para API nova | REST, gRPC, GraphQL | ~2010 |
| **WSDL** | OpenAPI, Protobuf | ~2012 |
| **XML** como formato padrão de API web | JSON | ~2010 |
| **JSONP** | CORS | ~2014 |
| **Swagger 2.0** | **OpenAPI 3.1 / 3.2** | 2017 |
| **HAL, JSON-API** como padrão universal | não houve vencedor; use o que o time entende | — |
| Cabeçalhos `X-*` como convenção | nomes sem `X-` (RFC 6648 desaconselha o prefixo) | 2012 |
| **Long polling** | SSE ou WebSocket | ~2015 |
| **Comet** | SSE / WebSocket | ~2012 |
| `application/x-www-form-urlencoded` em API JSON | `application/json` | — |
| **HTTP sem TLS** em qualquer contexto | HTTPS sempre | — |

---

## Autoteste

1. Quais métodos são seguros? Quais são idempotentes? Por que a distinção importa para retentativa?
2. Explique a diferença entre 401 e 403, e entre 400 e 422. Dê um exemplo de cada.
3. Qual regra decide entre devolver 4xx e 5xx?
4. Qual a diferença entre `no-cache` e `no-store`? Qual você usa para dado sensível?
5. O que acontece se você esquecer `Vary: Authorization` numa resposta cacheável?
6. Escreva o comando curl que mostra onde o tempo de uma requisição foi gasto.
7. Por que não se deve transmitir dinheiro como `number` em JSON? O que usar?
8. Por que UUIDv7 em vez de UUIDv4? Por que não expor ID sequencial?
9. Por que `?email=maria+trabalho@x.com` quebra, e como corrigir?
10. Cite três coisas obsoletas desta lista e o que as substituiu.
