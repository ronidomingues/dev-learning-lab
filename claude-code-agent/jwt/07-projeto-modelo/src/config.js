/**
 * Configuracao. Tudo que muda entre ambientes mora aqui, nunca espalhado
 * pelo codigo.
 *
 * Os tempos de vida sao a decisao de projeto mais importante do arquivo, e
 * estao explicados em 17-ciclo-de-vida-sessao.md:
 *
 *  - access token curto (15 min) porque ele NAO e consultado no banco a cada
 *    uso; a janela de estrago de um token roubado e o seu tempo de vida;
 *  - refresh token longo (14 dias) porque ele SEMPRE bate no banco, entao pode
 *    ser revogado no ato.
 */

export const config = {
  emissor: process.env.JWT_ISS ?? 'http://localhost:3000',
  audiencia: process.env.JWT_AUD ?? 'cofre-de-notas-api',

  vidaAccessSegundos: Number(process.env.JWT_ACCESS_TTL ?? 15 * 60),      // 15 minutos
  vidaRefreshSegundos: Number(process.env.JWT_REFRESH_TTL ?? 14 * 86400), // 14 dias

  /**
   * Tolerancia de relogio. 60 s e o valor de consenso. Zero e defensavel se
   * todas as maquinas usam NTP e voce mede a deriva; acima de 300 s voce
   * esta, na pratica, estendendo a vida do token.
   */
  toleranciaRelogioSegundos: Number(process.env.JWT_LEEWAY ?? 60),

  porta: Number(process.env.PORT ?? 3000),
  caminhoChaveiro: process.env.JWT_KEYS ?? new URL('../dados/chaveiro.json', import.meta.url).pathname,

  /** `secure: true` obriga HTTPS no cookie. Desligado so em desenvolvimento local. */
  cookieSeguro: process.env.COOKIE_SECURE === 'true',
};
