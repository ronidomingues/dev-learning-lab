import { test } from "node:test";
import assert from "node:assert/strict";
import { gerarSlug, ALFABETO, ESPACO_DE_CHAVES } from "../src/ids.js";

test("gerarSlug devolve o tamanho pedido", () => {
  assert.equal(gerarSlug(7).length, 7);
  assert.equal(gerarSlug(12).length, 12);
});

test("gerarSlug usa apenas o alfabeto sem caracteres ambíguos", () => {
  const permitido = new Set(ALFABETO);
  for (let i = 0; i < 200; i++) {
    for (const c of gerarSlug()) assert.ok(permitido.has(c), `caractere inesperado: ${c}`);
  }
  // O alfabeto não pode conter os pares que se confundem ao ler em voz alta.
  for (const proibido of ["0", "O", "1", "l", "I"]) {
    assert.ok(!permitido.has(proibido), `${proibido} não deveria estar no alfabeto`);
  }
});

test("gerarSlug rejeita tamanhos fora da faixa", () => {
  assert.throws(() => gerarSlug(3), /faixa/);
  assert.throws(() => gerarSlug(64), /faixa/);
});

test("mil slugs gerados não colidem (na prática)", () => {
  const vistos = new Set();
  for (let i = 0; i < 1000; i++) vistos.add(gerarSlug());
  assert.equal(vistos.size, 1000);
});

test("o espaço de chaves é da ordem de trilhões", () => {
  assert.ok(ESPACO_DE_CHAVES > 1e12, `espaço pequeno demais: ${ESPACO_DE_CHAVES}`);
});
