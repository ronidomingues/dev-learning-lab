// Configuração centralizada. Uma única função que lê o ambiente e valida.
//
// Por que um módulo só: em produção você quer falhar RÁPIDO e com mensagem clara
// se faltar configuração — e não descobrir isso na primeira requisição, às 3h da manhã.

export function carregarConfig(env = process.env) {
  const cfg = {
    porta: Number(env.PORT ?? 3000),
    baseUrl: (env.BASE_URL ?? `http://localhost:${env.PORT ?? 3000}`).replace(/\/+$/, ""),
    databaseUrl: env.DATABASE_URL ?? null,
    redisUrl: env.REDIS_URL ?? null,
    rateLimite: Number(env.RATE_LIMITE ?? 20),
    rateJanelaMs: Number(env.RATE_JANELA_MS ?? 60_000),
    // Modo memória: sem DATABASE_URL, a aplicação roda inteira em memória.
    // É o que permite `npm test` funcionar sem Docker, sem nuvem e sem rede.
    modoMemoria: !env.DATABASE_URL,
    ambiente: env.NODE_ENV ?? "development",
    // Origem permitida no CORS. null = não emite cabeçalho (mesma origem apenas).
    corsOrigem: env.CORS_ORIGEM ?? null,
  };

  if (!Number.isFinite(cfg.porta) || cfg.porta < 0 || cfg.porta > 65535) {
    throw new Error(`PORT inválida: ${env.PORT}`);
  }
  if (!Number.isFinite(cfg.rateLimite) || cfg.rateLimite < 1) {
    throw new Error(`RATE_LIMITE inválido: ${env.RATE_LIMITE}`);
  }
  return cfg;
}
