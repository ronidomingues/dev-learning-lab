/**
 * log.mjs — log em JSON com redação automática de segredo.
 *
 * Por que isto existe: a causa de vazamento mais comum depois do commit acidental
 * é alguém logar um objeto inteiro que contém credencial. A redação por nome de
 * chave não é perfeita (não pega senha embutida em URL — por isso `redigirUrl`),
 * mas elimina a classe mais frequente de acidente.
 */

const NIVEIS = { debug: 10, info: 20, warn: 30, error: 40 };

const CHAVES_SENSIVEIS =
  /^(pass|senha|secret|segredo|token|api_?key|auth|authorization|cookie|set-cookie|private|credential|senha_?hash)/i;

/** Substitui valores de chaves sensíveis por [REDIGIDO]. Trata ciclos e arrays. */
export function redigir(valor, vistos = new WeakSet()) {
  if (valor === null || typeof valor !== 'object') return valor;
  if (vistos.has(valor)) return '[circular]';
  vistos.add(valor);
  if (Array.isArray(valor)) return valor.map((item) => redigir(item, vistos));
  const saida = {};
  for (const [chave, val] of Object.entries(valor)) {
    saida[chave] = CHAVES_SENSIVEIS.test(chave) ? '[REDIGIDO]' : redigir(val, vistos);
  }
  return saida;
}

/**
 * Remove a senha de uma URL de conexão.
 * `postgres://app:senha@host/db` → `postgres://app:***@host/db`
 * Esta é a parte que a redação por nome de chave NÃO pega.
 */
export function redigirUrl(texto) {
  try {
    const u = new URL(texto);
    if (u.password) u.password = '***';
    return u.toString();
  } catch {
    return texto;
  }
}

export function criarLog(nivelMinimo = 'info', escrever = (linha) => process.stdout.write(linha)) {
  const minimo = NIVEIS[nivelMinimo] ?? NIVEIS.info;
  const emitir = (nivel) => (mensagem, dados = {}) => {
    if (NIVEIS[nivel] < minimo) return;
    escrever(
      JSON.stringify({
        ts: new Date().toISOString(),
        nivel,
        mensagem,
        ...redigir(dados),
      }) + '\n',
    );
  };
  return {
    debug: emitir('debug'),
    info: emitir('info'),
    warn: emitir('warn'),
    error: emitir('error'),
  };
}
