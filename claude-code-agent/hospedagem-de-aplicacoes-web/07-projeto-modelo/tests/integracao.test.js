// Testes de integração REAIS, contra PostgreSQL e Redis de verdade.
//
// São pulados por padrão: `npm test` precisa rodar em qualquer máquina, sem Docker
// e sem rede. Para rodá-los:
//
//   docker compose up -d db cache
//   DATABASE_URL=postgresql://app:dev_senha_local@localhost:5432/app \
//   REDIS_URL=redis://localhost:6379 npm run test:integracao
//
import { test, describe } from "node:test";
import assert from "node:assert/strict";

const ligado = process.env.INTEGRACAO === "1" && !!process.env.DATABASE_URL && !!process.env.REDIS_URL;

describe("integração com PostgreSQL e Redis", { skip: ligado ? false : "defina INTEGRACAO=1, DATABASE_URL e REDIS_URL" }, () => {
  test("o repositório PostgreSQL cria, busca, conta clique e ranqueia", async () => {
    const { criarRepositorioPg } = await import("../src/repositorio-pg.js");
    const repo = criarRepositorioPg(process.env.DATABASE_URL);
    try {
      assert.equal(await repo.ping(), true);

      const slug = "t" + Math.random().toString(36).slice(2, 8);
      const criado = await repo.criar({ slug, destino: "https://exemplo.com/integra" });
      assert.equal(criado.slug, slug);
      assert.equal(Number(criado.cliques), 0);

      const achado = await repo.buscarPorSlug(slug);
      assert.equal(achado.destino, "https://exemplo.com/integra");

      await repo.registrarClique(slug);
      assert.equal(Number((await repo.buscarPorSlug(slug)).cliques), 1);

      // O UNIQUE do banco é a fonte da verdade sobre colisão.
      await assert.rejects(
        () => repo.criar({ slug, destino: "https://exemplo.com/outro" }),
        (e) => e.codigo === "slug_em_uso"
      );

      assert.ok((await repo.top(5)).length > 0);
    } finally {
      await repo.fechar();
    }
  });

  test("o cache Redis respeita TTL e o limitador de janela fixa", async () => {
    const { criarCacheRedis } = await import("../src/cache-redis.js");
    const cache = criarCacheRedis(process.env.REDIS_URL);
    try {
      assert.equal(await cache.ping(), true);

      const k = "teste:" + Math.random().toString(36).slice(2, 8);
      await cache.set(k, "valor", 2);
      assert.equal(await cache.get(k), "valor");
      await new Promise((r) => setTimeout(r, 2500));
      assert.equal(await cache.get(k), null, "a chave deveria ter expirado");

      const rl = "rl:teste:" + Math.random().toString(36).slice(2, 8);
      const a = await cache.consumir(rl, 5_000);
      const b = await cache.consumir(rl, 5_000);
      assert.equal(a.contagem, 1);
      assert.equal(b.contagem, 2);
      assert.ok(b.ttlMs > 0 && b.ttlMs <= 5_000);
      await cache.del(rl);
    } finally {
      await cache.fechar();
    }
  });
});
