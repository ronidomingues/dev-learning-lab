import { test } from "node:test";
import assert from "node:assert/strict";
import { criarServico } from "../src/servico.js";
import { criarRepositorioMemoria } from "../src/repositorio-memoria.js";
import { criarCacheMemoria } from "../src/cache-memoria.js";
import { carregarConfig } from "../src/config.js";

const montar = (env = {}) => {
  const config = carregarConfig({ BASE_URL: "https://curto.br", ...env });
  const repo = criarRepositorioMemoria();
  const cache = criarCacheMemoria();
  return { config, repo, cache, servico: criarServico({ repo, cache, config }) };
};

test("criarLink monta a url_curta a partir da BASE_URL configurada", async () => {
  const { servico } = montar();
  const link = await servico.criarLink({ destino: "https://exemplo.com" });
  assert.equal(link.url_curta, `https://curto.br/${link.slug}`);
});

test("BASE_URL com barra no fim não gera url com barra dupla", async () => {
  const { servico } = montar({ BASE_URL: "https://curto.br///" });
  const link = await servico.criarLink({ destino: "https://exemplo.com" });
  assert.ok(!link.url_curta.includes("//" + "/"), link.url_curta);
  assert.equal(link.url_curta, `https://curto.br/${link.slug}`);
});

test("resolver lança nao_encontrado para slug inexistente", async () => {
  const { servico } = montar();
  await assert.rejects(() => servico.resolver("inexistente"), (e) => e.codigo === "nao_encontrado");
});

test("saude reporta 'ok: false' quando o banco está fora, mas 'ok: true' se só o cache caiu", async () => {
  const config = carregarConfig({});
  const repoQuebrado = { tipo: "falso", ping: async () => { throw new Error("banco fora"); } };
  const cacheOk = criarCacheMemoria();
  const s1 = criarServico({ repo: repoQuebrado, cache: cacheOk, config });
  const r1 = await s1.saude();
  assert.equal(r1.ok, false);
  assert.match(r1.banco, /down/);

  const repoOk = criarRepositorioMemoria();
  const cacheQuebrado = { tipo: "falso", ping: async () => { throw new Error("cache fora"); } };
  const s2 = criarServico({ repo: repoOk, cache: cacheQuebrado, config });
  const r2 = await s2.saude();
  assert.equal(r2.ok, true, "cache fora é degradação, não indisponibilidade");
  assert.match(r2.cache, /down/);
});

test("colisão de slug aleatório é reprocessada até haver sucesso", async () => {
  const config = carregarConfig({});
  const cache = criarCacheMemoria();
  let chamadas = 0;
  const repo = {
    tipo: "falso",
    ping: async () => true,
    async criar({ slug, destino }) {
      chamadas++;
      if (chamadas < 3) {                       // duas colisões seguidas
        const e = new Error("colidiu"); e.codigo = "slug_em_uso"; e.status = 409; throw e;
      }
      return { id: 1, slug, destino, cliques: 0, criado_em: new Date().toISOString() };
    },
  };
  const servico = criarServico({ repo, cache, config });
  const link = await servico.criarLink({ destino: "https://exemplo.com" });
  assert.equal(chamadas, 3);
  // Repare na barra final: validarDestino usa new URL(...).toString(), que NORMALIZA
  // a URL. "https://exemplo.com" vira "https://exemplo.com/". Isso é desejável
  // (evita duas entradas para o mesmo destino) e é o tipo de detalhe que só aparece
  // quando se escreve o teste.
  assert.equal(link.destino, "https://exemplo.com/");
});

test("estatísticas em cache não refletem clique imediato (é o trade-off documentado)", async () => {
  const { servico, repo } = montar();
  const link = await servico.criarLink({ destino: "https://exemplo.com" });
  const antes = await servico.estatisticas();
  assert.equal(antes.fonte, "banco");

  await repo.registrarClique(link.slug);
  const depois = await servico.estatisticas();
  assert.equal(depois.fonte, "cache");
  assert.equal(depois.links[0].cliques, 0, "o cache de 10 s ainda mostra o valor antigo — por projeto");
});

test("config rejeita PORT e RATE_LIMITE inválidos", () => {
  assert.throws(() => carregarConfig({ PORT: "abc" }), /PORT inválida/);
  assert.throws(() => carregarConfig({ PORT: "99999" }), /PORT inválida/);
  assert.throws(() => carregarConfig({ RATE_LIMITE: "0" }), /RATE_LIMITE inválido/);
});

test("modoMemoria é verdadeiro sem DATABASE_URL e falso com ela", () => {
  assert.equal(carregarConfig({}).modoMemoria, true);
  assert.equal(carregarConfig({ DATABASE_URL: "postgresql://x" }).modoMemoria, false);
});
