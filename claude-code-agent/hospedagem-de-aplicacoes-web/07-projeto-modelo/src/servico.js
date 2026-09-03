import { gerarSlug } from "./ids.js";
import { validarDestino, validarSlug } from "./validate.js";
import { erroNaoEncontrado, erroLimite, erroSlugEmUso } from "./erros.js";

const TTL_RESOLUCAO = 300;   // 5 min — link mudou? o pior caso é redirecionar para o destino antigo
const TTL_ESTATISTICAS = 10; // 10 s — números de painel podem estar 10 s atrasados sem prejuízo

/**
 * Camada de serviço: TODA a regra de negócio mora aqui.
 * Não conhece HTTP, não conhece SQL, não conhece Redis — só os contratos
 * `repo` e `cache`. É isso que torna o sistema testável sem infraestrutura.
 */
export function criarServico({ repo, cache, config }) {
  const chaveLink = (slug) => `link:${slug}`;

  return {
    async criarLink({ destino, slug, ip }) {
      // 1) Limite por IP — protege a cota gratuita do banco e do cache.
      if (ip) {
        const { contagem, ttlMs } = await cache.consumir(`rl:criar:${ip}`, config.rateJanelaMs);
        if (contagem > config.rateLimite) {
          throw erroLimite(Math.ceil(ttlMs / 1000));
        }
      }

      // 2) Validação. Falhar cedo, com mensagem específica.
      const destinoValido = validarDestino(destino);

      // 3) Apelido escolhido pelo usuário: uma tentativa, conflito é erro.
      if (slug != null && slug !== "") {
        const escolhido = validarSlug(slug);
        const link = await repo.criar({ slug: escolhido, destino: destinoValido });
        return this.formatar(link);
      }

      // 4) Apelido aleatório: até 5 tentativas em caso de colisão.
      //    A colisão é improvável (1,7 trilhão de combinações), mas o UNIQUE do banco
      //    é a fonte da verdade — nunca "verifique antes e insira depois", isso é
      //    uma condição de corrida clássica.
      for (let tentativa = 0; tentativa < 5; tentativa++) {
        try {
          const link = await repo.criar({ slug: gerarSlug(7), destino: destinoValido });
          return this.formatar(link);
        } catch (e) {
          if (e.codigo !== "slug_em_uso") throw e;
        }
      }
      throw erroSlugEmUso("(aleatório)");
    },

    /** Resolve um slug para o destino. É o caminho quente: cache-aside. */
    async resolver(slug) {
      const emCache = await cache.get(chaveLink(slug));
      if (emCache !== null) {
        this.contarClique(slug);
        return { destino: emCache, fonte: "cache" };
      }

      const link = await repo.buscarPorSlug(slug);
      if (!link) throw erroNaoEncontrado();

      await cache.set(chaveLink(slug), link.destino, TTL_RESOLUCAO);
      this.contarClique(slug);
      return { destino: link.destino, fonte: "banco" };
    },

    /**
     * Contagem de clique fora do caminho da resposta.
     * O usuário não deve esperar por um UPDATE para ser redirecionado.
     * Se falhar, perde-se um clique — trade-off consciente: latência > precisão de métrica.
     */
    contarClique(slug) {
      Promise.resolve(repo.registrarClique(slug)).catch((e) =>
        console.error(JSON.stringify({ nivel: "aviso", origem: "clique", slug, msg: e.message })));
    },

    async detalhe(slug) {
      const link = await repo.buscarPorSlug(slug);
      if (!link) throw erroNaoEncontrado();
      return this.formatar(link);
    },

    async estatisticas() {
      const emCache = await cache.get("stats:top");
      if (emCache !== null) return { fonte: "cache", links: JSON.parse(emCache) };

      const links = await repo.top(10);
      await cache.set("stats:top", JSON.stringify(links), TTL_ESTATISTICAS);
      return { fonte: "banco", links };
    },

    async saude() {
      const [banco, memoria] = await Promise.allSettled([repo.ping(), cache.ping()]);
      return {
        ok: banco.status === "fulfilled",             // banco fora = não saudável
        banco: banco.status === "fulfilled" ? "up" : `down: ${banco.reason?.message}`,
        cache: memoria.status === "fulfilled" ? "up" : `down: ${memoria.reason?.message}`,
        modo: `${repo.tipo}+${cache.tipo}`,
      };
    },

    formatar(link) {
      return {
        slug: link.slug,
        destino: link.destino,
        cliques: Number(link.cliques ?? 0),
        url_curta: `${config.baseUrl}/${link.slug}`,
        criado_em: link.criado_em,
      };
    },
  };
}
