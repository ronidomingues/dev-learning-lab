/**
 * Cache em memória com TTL. Mesmo contrato do cache Redis.
 *
 * IMPORTANTE, e é a lição do arquivo: isto NÃO substitui o Redis em produção.
 * Ele é local ao processo — com duas instâncias da aplicação, cada uma tem o seu,
 * e elas divergem. É exatamente por isso que existe um cache externo.
 */
export function criarCacheMemoria({ agora = () => Date.now() } = {}) {
  const dados = new Map();  // chave -> { valor, expiraEm }

  const vivo = (e) => e && (e.expiraEm === null || e.expiraEm > agora());

  return {
    tipo: "memoria",

    async ping() { return true; },

    async get(chave) {
      const e = dados.get(chave);
      if (!vivo(e)) { dados.delete(chave); return null; }
      return e.valor;
    },

    async set(chave, valor, ttlSeg = null) {
      dados.set(chave, { valor: String(valor), expiraEm: ttlSeg ? agora() + ttlSeg * 1000 : null });
      return "OK";
    },

    async del(chave) { return dados.delete(chave) ? 1 : 0; },

    /** Janela fixa: incrementa e devolve {contagem, ttlMs}. */
    async consumir(chave, janelaMs) {
      const e = dados.get(chave);
      if (!vivo(e)) {
        dados.set(chave, { valor: "1", expiraEm: agora() + janelaMs });
        return { contagem: 1, ttlMs: janelaMs };
      }
      e.valor = String(Number(e.valor) + 1);
      return { contagem: Number(e.valor), ttlMs: Math.max(0, e.expiraEm - agora()) };
    },

    async fechar() { dados.clear(); },
  };
}
