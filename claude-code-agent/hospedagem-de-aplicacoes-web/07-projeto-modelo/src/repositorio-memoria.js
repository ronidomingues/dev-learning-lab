import { erroSlugEmUso } from "./erros.js";

/**
 * Repositório em memória. Mesmo contrato do repositório PostgreSQL.
 *
 * Por que existe: permite rodar os testes e a demonstração sem banco nenhum.
 * O padrão é "porta e adaptador" — o resto da aplicação nunca sabe qual dos dois está em uso.
 */
export function criarRepositorioMemoria() {
  const porSlug = new Map();
  let proximoId = 1;

  return {
    tipo: "memoria",

    async ping() { return true; },

    async criar({ slug, destino }) {
      if (porSlug.has(slug)) throw erroSlugEmUso(slug);
      const link = { id: proximoId++, slug, destino, cliques: 0, criado_em: new Date().toISOString() };
      porSlug.set(slug, link);
      return { ...link };
    },

    async buscarPorSlug(slug) {
      const l = porSlug.get(slug);
      return l ? { ...l } : null;
    },

    async registrarClique(slug) {
      const l = porSlug.get(slug);
      if (l) l.cliques += 1;
    },

    async top(limite = 10) {
      return [...porSlug.values()]
        .sort((a, b) => b.cliques - a.cliques || b.id - a.id)
        .slice(0, limite)
        .map(({ slug, destino, cliques }) => ({ slug, destino, cliques }));
    },

    async fechar() {},
  };
}
