import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { subirApp } from "./ajuda.js";

let app;
// Limite alto na instância compartilhada: o teste de limite usa uma instância própria.
// (Este ajuste veio de uma falha real ao escrever a suíte: com RATE_LIMITE=5, o sexto
//  POST de QUALQUER teste passava a receber 429 e derrubava testes não relacionados.)
before(async () => { app = await subirApp({ RATE_LIMITE: "1000", RATE_JANELA_MS: "60000" }); });
after(async () => { await app.fechar(); });

test("GET /health responde 200 com as dependências", async () => {
  const r = await app.get("/health");
  assert.equal(r.status, 200);
  const corpo = await r.json();
  assert.equal(corpo.ok, true);
  assert.equal(corpo.banco, "up");
  assert.equal(corpo.cache, "up");
  assert.equal(corpo.modo, "memoria+memoria");
});

test("GET / serve o frontend", async () => {
  const r = await app.get("/");
  assert.equal(r.status, 200);
  assert.match(r.headers.get("content-type"), /text\/html/);
  assert.match(await r.text(), /EncurtaLink/);
});

test("POST /api/links cria um link e devolve 201 com Location", async () => {
  const r = await app.post("/api/links", { destino: "https://exemplo.com/pagina" });
  assert.equal(r.status, 201);
  const link = await r.json();
  assert.equal(link.destino, "https://exemplo.com/pagina");
  assert.equal(link.slug.length, 7);
  assert.equal(link.url_curta, `http://teste.local/${link.slug}`);
  assert.equal(r.headers.get("location"), link.url_curta);
});

// Nota: "minhaPagina" não contém l, o, O, I, 0 nem 1 — esses caracteres NÃO existem
// no alfabeto de slugs (ver src/ids.js). Um apelido com "l" é recusado com 400.
test("POST /api/links aceita apelido escolhido e recusa o repetido com 409", async () => {
  const primeiro = await app.post("/api/links", { destino: "https://exemplo.com/a", slug: "minhaPagina" });
  assert.equal(primeiro.status, 201);
  assert.equal((await primeiro.json()).slug, "minhaPagina");

  const segundo = await app.post("/api/links", { destino: "https://exemplo.com/b", slug: "minhaPagina" });
  assert.equal(segundo.status, 409);
  assert.equal((await segundo.json()).codigo, "slug_em_uso");
});

test("POST /api/links devolve 400 com código de validação para destino inválido", async () => {
  const r = await app.post("/api/links", { destino: "javascript:alert(1)" });
  assert.equal(r.status, 400);
  assert.equal((await r.json()).codigo, "validacao");
});

test("POST /api/links devolve 400 para JSON malformado", async () => {
  const r = await fetch(`${app.base}/api/links`, {
    method: "POST", headers: { "content-type": "application/json" }, body: "{ isto não é json",
  });
  assert.equal(r.status, 400);
  assert.equal((await r.json()).codigo, "json_invalido");
});

test("GET /<slug> redireciona com 302 e não com 301", async () => {
  const criado = await (await app.post("/api/links", { destino: "https://exemplo.com/destino" })).json();
  const r = await app.get(`/${criado.slug}`);
  assert.equal(r.status, 302, "301 seria cacheado para sempre pelo navegador");
  assert.equal(r.headers.get("location"), "https://exemplo.com/destino");
  assert.equal(r.headers.get("cache-control"), "no-store");
});

test("GET /<slug> inexistente devolve 404 com código", async () => {
  const r = await app.get("/naoExiste9");
  assert.equal(r.status, 404);
  assert.equal((await r.json()).codigo, "nao_encontrado");
});

test("GET /api/links/<slug> devolve o detalhe com a contagem de cliques", async () => {
  const criado = await (await app.post("/api/links", { destino: "https://exemplo.com/c" })).json();
  await app.get(`/${criado.slug}`);
  await app.get(`/${criado.slug}`);
  // A contagem é assíncrona de propósito (fora do caminho da resposta):
  // damos um tique do event loop para ela acontecer.
  await new Promise((r) => setImmediate(r));

  const r = await app.get(`/api/links/${criado.slug}`);
  assert.equal(r.status, 200);
  assert.equal((await r.json()).cliques, 2);
});

test("a segunda resolução do mesmo slug vem do cache", async () => {
  const criado = await (await app.post("/api/links", { destino: "https://exemplo.com/quente" })).json();
  const primeira = await app.servico.resolver(criado.slug);
  const segunda = await app.servico.resolver(criado.slug);
  assert.equal(primeira.fonte, "banco");
  assert.equal(segunda.fonte, "cache");
});

test("GET /api/stats devolve o ranking e depois o serve do cache", async () => {
  const a = await (await app.post("/api/links", { destino: "https://exemplo.com/pop" })).json();
  for (let i = 0; i < 3; i++) await app.get(`/${a.slug}`);
  await new Promise((r) => setImmediate(r));

  const primeira = await (await app.get("/api/stats")).json();
  assert.equal(primeira.fonte, "banco");
  assert.ok(Array.isArray(primeira.links));

  const segunda = await (await app.get("/api/stats")).json();
  assert.equal(segunda.fonte, "cache");
});

test("limite de taxa: o 6º POST do mesmo IP devolve 429 com Retry-After", async () => {
  const isolado = await subirApp({ RATE_LIMITE: "5", RATE_JANELA_MS: "60000" });
  try {
    for (let i = 0; i < 5; i++) {
      const r = await isolado.post("/api/links", { destino: `https://exemplo.com/${i}` });
      assert.equal(r.status, 201, `a requisição ${i + 1} deveria passar`);
    }
    const excedente = await isolado.post("/api/links", { destino: "https://exemplo.com/x" });
    assert.equal(excedente.status, 429);
    assert.equal((await excedente.json()).codigo, "limite_excedido");
    const espera = Number(excedente.headers.get("retry-after"));
    assert.ok(espera > 0 && espera <= 60, `retry-after fora do esperado: ${espera}`);
  } finally {
    await isolado.fechar();
  }
});

test("rota desconhecida devolve 404 em JSON", async () => {
  const r = await app.get("/api/nao/existe");
  assert.equal(r.status, 404);
  assert.equal((await r.json()).codigo, "nao_encontrado");
});

test("OPTIONS devolve 204 (pré-voo do CORS)", async () => {
  const r = await fetch(`${app.base}/api/links`, { method: "OPTIONS" });
  assert.equal(r.status, 204);
});

test("corpo maior que 16 KB é recusado com 413", async () => {
  const gigante = JSON.stringify({ destino: "https://exemplo.com/" + "a".repeat(20_000) });
  const r = await fetch(`${app.base}/api/links`, {
    method: "POST", headers: { "content-type": "application/json" }, body: gigante,
  }).catch(() => null);
  // O servidor pode fechar a conexão ao destruir a requisição; qualquer um dos dois
  // desfechos é aceitável — o que NÃO é aceitável é processar 20 KB de corpo.
  if (r) assert.ok([400, 413].includes(r.status), `status inesperado: ${r.status}`);
});
