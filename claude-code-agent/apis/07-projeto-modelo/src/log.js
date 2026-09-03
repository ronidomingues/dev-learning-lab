/**
 * Log estruturado em JSON.
 *
 * Por que JSON e não texto: log de produção é lido por máquina antes de ser lido por
 * gente. Com JSON você filtra por campo (`nivel="error" AND request_id="abc"`) em vez
 * de escrever expressão regular sobre texto livre.
 *
 * Por que uma linha por evento: agregadores (Loki, CloudWatch, Datadog) quebram por
 * linha. Log multilinha vira N eventos sem relação entre si.
 */

const NIVEIS = { debug: 10, info: 20, warn: 30, error: 40 };
const NIVEL_MINIMO = NIVEIS[process.env.LOG_LEVEL ?? 'info'] ?? NIVEIS.info;

/** Chaves cujo valor nunca deve aparecer no log. */
const SENSIVEIS = new Set([
  'authorization', 'password', 'senha', 'token', 'access_token',
  'refresh_token', 'secret', 'segredo', 'cookie', 'set-cookie', 'api_key'
]);

/** Substitui recursivamente valores sensíveis por "[oculto]". */
function limpar(valor, profundidade = 0) {
  if (profundidade > 4 || valor === null || typeof valor !== 'object') return valor;
  if (Array.isArray(valor)) return valor.map(v => limpar(v, profundidade + 1));

  const saida = {};
  for (const [chave, v] of Object.entries(valor)) {
    saida[chave] = SENSIVEIS.has(chave.toLowerCase()) ? '[oculto]' : limpar(v, profundidade + 1);
  }
  return saida;
}

function emitir(nivel, msg, campos = {}) {
  if (NIVEIS[nivel] < NIVEL_MINIMO) return;

  const linha = {
    ts: new Date().toISOString(),
    nivel,
    msg,
    ...limpar(campos)
  };
  // stderr para warn/error, stdout para o resto: é a convenção que permite
  // separar os fluxos no orquestrador.
  const fluxo = NIVEIS[nivel] >= NIVEIS.warn ? process.stderr : process.stdout;
  fluxo.write(JSON.stringify(linha) + '\n');
}

export const log = {
  debug: (msg, campos) => emitir('debug', msg, campos),
  info:  (msg, campos) => emitir('info',  msg, campos),
  warn:  (msg, campos) => emitir('warn',  msg, campos),
  error: (msg, campos) => emitir('error', msg, campos),

  /** Devolve um logger que carrega campos fixos — tipicamente o request_id. */
  com(camposFixos) {
    return {
      debug: (m, c) => emitir('debug', m, { ...camposFixos, ...c }),
      info:  (m, c) => emitir('info',  m, { ...camposFixos, ...c }),
      warn:  (m, c) => emitir('warn',  m, { ...camposFixos, ...c }),
      error: (m, c) => emitir('error', m, { ...camposFixos, ...c }),
      com(mais) { return log.com({ ...camposFixos, ...mais }); }
    };
  }
};

export { limpar as _limparParaTeste };
