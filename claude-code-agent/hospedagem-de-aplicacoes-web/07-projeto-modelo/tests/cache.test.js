import { test } from "node:test";
import assert from "node:assert/strict";
import { criarCacheMemoria } from "../src/cache-memoria.js";

test("get devolve null para chave inexistente (não undefined)", async () => {
  const c = criarCacheMemoria();
  assert.equal(await c.get("nada"), null);
});

test("set e get, com valor guardado como texto", async () => {
  const c = criarCacheMemoria();
  await c.set("k", 42);
  assert.equal(await c.get("k"), "42");
});

test("TTL expira a chave — com relógio controlado, sem sleep", async () => {
  // Relógio injetado: teste de tempo NUNCA deve depender de esperar de verdade.
  let agora = 1_000_000;
  const c = criarCacheMemoria({ agora: () => agora });

  await c.set("k", "v", 10);              // 10 segundos
  assert.equal(await c.get("k"), "v");
  agora += 9_000;
  assert.equal(await c.get("k"), "v");    // ainda vivo
  agora += 2_000;
  assert.equal(await c.get("k"), null);   // expirou
});

test("consumir implementa janela fixa e devolve o ttl restante", async () => {
  let agora = 0;
  const c = criarCacheMemoria({ agora: () => agora });

  const a = await c.consumir("rl:ip", 60_000);
  assert.deepEqual([a.contagem, a.ttlMs], [1, 60_000]);

  agora += 10_000;
  const b = await c.consumir("rl:ip", 60_000);
  assert.equal(b.contagem, 2);
  assert.equal(b.ttlMs, 50_000);

  agora += 60_000;                        // janela virou
  const d = await c.consumir("rl:ip", 60_000);
  assert.equal(d.contagem, 1);
});

test("del remove a chave", async () => {
  const c = criarCacheMemoria();
  await c.set("k", "v");
  assert.equal(await c.del("k"), 1);
  assert.equal(await c.get("k"), null);
  assert.equal(await c.del("k"), 0);
});
