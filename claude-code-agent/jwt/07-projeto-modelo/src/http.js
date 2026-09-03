/** Utilitarios de HTTP: leitura de corpo, resposta JSON, cookies. */

export async function lerJson(req, limiteBytes = 64 * 1024) {
  const pedacos = [];
  let total = 0;
  for await (const pedaco of req) {
    total += pedaco.length;
    if (total > limiteBytes) {
      const erro = new Error('corpo grande demais');
      erro.status = 413;
      throw erro;
    }
    pedacos.push(pedaco);
  }
  if (total === 0) return {};
  try {
    const objeto = JSON.parse(Buffer.concat(pedacos).toString('utf8'));
    if (objeto === null || typeof objeto !== 'object' || Array.isArray(objeto)) {
      throw new Error('nao e objeto');
    }
    return objeto;
  } catch {
    const erro = new Error('corpo nao e um objeto JSON valido');
    erro.status = 400;
    throw erro;
  }
}

export function responderJson(res, status, corpo, cabecalhos = {}) {
  const texto = JSON.stringify(corpo);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(texto),
    'cache-control': 'no-store',   // token em cache de proxy e vazamento
    ...cabecalhos,
  });
  res.end(texto);
}

/**
 * Erro 401 no formato do RFC 6750 §3: o `WWW-Authenticate` diz ao cliente
 * POR QUE falhou. Sem ele, um SPA nao sabe distinguir "token expirou, renove"
 * de "voce nao tem permissao, nao adianta renovar" — e entra em laco de
 * renovacao infinito.
 */
export function responderErroAuth(res, status, codigo, descricao) {
  const desafio = status === 401
    ? `Bearer error="invalid_token", error_description="${descricao.replace(/"/g, "'")}"`
    : `Bearer error="insufficient_scope", error_description="${descricao.replace(/"/g, "'")}"`;
  responderJson(res, status, { erro: codigo, mensagem: descricao }, { 'www-authenticate': desafio });
}

/**
 * Cookie do refresh token.
 *
 *   HttpOnly  — JavaScript nao le. Um XSS nao consegue roubar o refresh.
 *   Secure    — so viaja em HTTPS.
 *   SameSite=Strict — o navegador nao envia em requisicao vinda de outro site;
 *                     e a defesa contra CSRF nesta rota.
 *   Path=/auth/refresh — o cookie nem e enviado nas outras rotas. Menos
 *                     superficie, menos byte por requisicao.
 *
 * Ver 18-onde-guardar-no-cliente.md para o porque desta combinacao.
 */
export function cookieRefresh(valor, { maxIdade, seguro }) {
  const partes = [
    `refresh_token=${valor}`,
    'HttpOnly',
    'SameSite=Strict',
    'Path=/auth/refresh',
    `Max-Age=${maxIdade}`,
  ];
  if (seguro) partes.push('Secure');
  return partes.join('; ');
}

export function cookieRefreshApagado({ seguro }) {
  return cookieRefresh('', { maxIdade: 0, seguro });
}

export function lerCookie(req, nome) {
  const bruto = req.headers.cookie;
  if (!bruto) return null;
  for (const par of bruto.split(';')) {
    const igual = par.indexOf('=');
    if (igual === -1) continue;
    if (par.slice(0, igual).trim() === nome) return par.slice(igual + 1).trim();
  }
  return null;
}
