import Redis from "ioredis";

/**
 * Cache Redis/Valkey. Funciona com Upstash (rediss://), Render Key Value,
 * Redis Cloud e com o container local do compose.yaml.
 */
export function criarCacheRedis(url) {
  const cliente = new Redis(url, {
    maxRetriesPerRequest: 2,     // falhar rápido: cache fora não pode travar a requisição
    enableOfflineQueue: false,   // sem fila infinita de comandos quando o Redis some
    lazyConnect: false,
    // Upstash e Redis Cloud usam TLS; ioredis liga sozinho quando a URL é rediss://
  });

  cliente.on("error", (e) =>
    console.error(JSON.stringify({ nivel: "aviso", origem: "redis", msg: e.message })));

  return {
    tipo: "redis",

    async ping() { return (await cliente.ping()) === "PONG"; },

    async get(chave) { return cliente.get(chave); },

    async set(chave, valor, ttlSeg = null) {
      return ttlSeg ? cliente.set(chave, String(valor), "EX", ttlSeg) : cliente.set(chave, String(valor));
    },

    async del(chave) { return cliente.del(chave); },

    /**
     * Limitador de janela fixa em duas operações atômicas dentro de um pipeline:
     * INCR e, se for a primeira, PEXPIRE. O PEXPIRE é o que impede a chave de
     * viver para sempre e encher a memória do plano gratuito.
     */
    async consumir(chave, janelaMs) {
      const resultado = await cliente
        .multi()
        .incr(chave)
        .pttl(chave)
        .exec();

      const contagem = resultado[0][1];
      let ttlMs = resultado[1][1];

      if (ttlMs < 0) {                       // -1 = sem expiração definida ainda
        await cliente.pexpire(chave, janelaMs);
        ttlMs = janelaMs;
      }
      return { contagem, ttlMs };
    },

    async fechar() { await cliente.quit(); },
  };
}
