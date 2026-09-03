/**
 * JWS Compact Serialization (RFC 7515) + validacao de claims de JWT (RFC 7519),
 * escrito do zero sobre `node:crypto`.
 *
 * OBJETIVO DIDATICO: nao existe caixa-preta aqui. Cada byte do token e montado
 * e conferido neste arquivo. EM PRODUCAO, use uma biblioteca auditada
 * (`jose`, no ecossistema JavaScript) — o codigo abaixo e correto, mas nao
 * passou por anos de fuzzing e revisao adversarial como ela passou.
 *
 * Decisoes de seguranca deliberadas, todas explicadas em 20-ataques-e-defesas.md:
 *
 *  1. `verificar()` EXIGE a lista de algoritmos aceitos. O `alg` do cabecalho
 *     do token nunca escolhe o algoritmo — ele so e conferido contra a lista.
 *     Essa e a defesa contra `alg: none` e contra confusao de algoritmo.
 *  2. O `kid` seleciona a chave dentro de um conjunto local. Nunca vira caminho
 *     de arquivo, nunca vira URL.
 *  3. `iss` e `aud` sao obrigatorios na verificacao. Sem eles, um token valido
 *     emitido para outro servico e aceito aqui.
 *  4. Comparacao de HMAC em tempo constante (`timingSafeEqual`).
 */

import { createHmac, createHash, sign as assinarCripto, verify as verificarCripto, timingSafeEqual } from 'node:crypto';
import { jsonParaBase64url, base64urlParaJson, paraBase64url, deBase64url } from './base64url.js';

export class ErroJwt extends Error {
  constructor(codigo, mensagem) {
    super(mensagem);
    this.name = 'ErroJwt';
    this.codigo = codigo; // ex.: 'expirado', 'assinatura_invalida', 'alg_nao_permitido'
  }
}

/**
 * Algoritmos suportados por este projeto.
 *
 * `familia` diz o que a chave precisa ser. `hash` e a funcao de digest.
 * `dsaEncoding: 'ieee-p1363'` e essencial para ES256: o JWS exige a assinatura
 * como R||S cru (64 bytes), e nao no formato DER que o OpenSSL usa por padrao.
 * Errar isso e o motivo numero um de "minha assinatura ES256 nao valida em Java".
 */
const ALGORITMOS = {
  HS256: { familia: 'oct', hash: 'sha256' },
  HS384: { familia: 'oct', hash: 'sha384' },
  HS512: { familia: 'oct', hash: 'sha512' },
  RS256: { familia: 'RSA', hash: 'sha256', opcoes: {} },
  ES256: { familia: 'EC', hash: 'sha256', curva: 'P-256', opcoes: { dsaEncoding: 'ieee-p1363' } },
  ES384: { familia: 'EC', hash: 'sha384', curva: 'P-384', opcoes: { dsaEncoding: 'ieee-p1363' } },
  EdDSA: { familia: 'OKP', hash: null, opcoes: {} },
};

export const ALGORITMOS_SUPORTADOS = Object.keys(ALGORITMOS);

// ---------------------------------------------------------------------------
// Assinar
// ---------------------------------------------------------------------------

/**
 * Monta um JWS compacto: base64url(cabecalho).base64url(payload).base64url(assinatura)
 *
 * @param {object} payload      claims. `iat` e preenchido se ausente.
 * @param {object} opcoes
 * @param {string} opcoes.alg   algoritmo (ex.: 'ES256')
 * @param {KeyObject|Buffer} opcoes.chave  chave privada (assimetrico) ou segredo (HMAC)
 * @param {string} [opcoes.kid] identificador da chave, vai no cabecalho
 * @param {string} [opcoes.typ] padrao 'JWT'. Use 'at+jwt' em access token (RFC 9068).
 * @param {number} [opcoes.agora] epoch em segundos, para testes deterministicos
 * @returns {string} o token compacto
 */
export function assinar(payload, { alg, chave, kid, typ = 'JWT', agora = agoraEmSegundos() }) {
  const spec = ALGORITMOS[alg];
  if (!spec) throw new ErroJwt('alg_desconhecido', `algoritmo nao suportado: ${alg}`);
  if (payload === null || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new ErroJwt('payload_invalido', 'o payload precisa ser um objeto');
  }

  const cabecalho = { alg, typ };
  if (kid) cabecalho.kid = kid;

  const corpo = { iat: agora, ...payload };

  const cabecalhoB64 = jsonParaBase64url(cabecalho);
  const corpoB64 = jsonParaBase64url(corpo);
  const entradaAssinatura = Buffer.from(`${cabecalhoB64}.${corpoB64}`, 'ascii');

  const assinatura = calcularAssinatura(alg, spec, entradaAssinatura, chave);

  return `${cabecalhoB64}.${corpoB64}.${paraBase64url(assinatura)}`;
}

function calcularAssinatura(alg, spec, entrada, chave) {
  if (spec.familia === 'oct') {
    const segredo = normalizarSegredo(chave, alg);
    return createHmac(spec.hash, segredo).update(entrada).digest();
  }
  // Para EdDSA o Node exige algoritmo de hash `null` — a curva ja define o hash.
  return assinarCripto(spec.hash, entrada, { key: chave, ...(spec.opcoes ?? {}) });
}

/**
 * Um segredo HMAC precisa ter, no minimo, o tamanho da saida do hash
 * (RFC 7518 §3.2). Com 32 bytes para HS256 a busca por forca bruta e inviavel;
 * com "senha123" ela roda no notebook de quem atacou, offline, em segundos.
 */
function normalizarSegredo(chave, alg) {
  const buffer = Buffer.isBuffer(chave) ? chave : Buffer.from(String(chave), 'utf8');
  const minimo = { HS256: 32, HS384: 48, HS512: 64 }[alg];
  if (buffer.length < minimo) {
    throw new ErroJwt('segredo_fraco', `${alg} exige segredo de pelo menos ${minimo} bytes (recebido: ${buffer.length})`);
  }
  return buffer;
}

// ---------------------------------------------------------------------------
// Decodificar sem verificar
// ---------------------------------------------------------------------------

/**
 * Le o conteudo do token SEM conferir a assinatura.
 *
 * Serve para depurar e para descobrir o `kid` antes de escolher a chave.
 * NUNCA tome decisao de autorizacao com o resultado disto. O nome longo e
 * de proposito: se aparecer numa revisao de codigo, tem que doer.
 */
export function decodificarSemVerificar(token) {
  const partes = String(token).split('.');
  if (partes.length !== 3) {
    throw new ErroJwt('formato_invalido', `um JWS compacto tem 3 segmentos, recebido ${partes.length}`);
  }
  return {
    cabecalho: base64urlParaJson(partes[0]),
    payload: base64urlParaJson(partes[1]),
    assinatura: deBase64url(partes[2]),
    entradaAssinatura: Buffer.from(`${partes[0]}.${partes[1]}`, 'ascii'),
  };
}

// ---------------------------------------------------------------------------
// Verificar
// ---------------------------------------------------------------------------

/**
 * Verifica assinatura e claims. Lanca ErroJwt na primeira falha.
 *
 * @param {string} token
 * @param {object} opcoes
 * @param {string[]} opcoes.algoritmos   OBRIGATORIO. Lista fechada de `alg` aceitos.
 * @param {function|KeyObject|Buffer} opcoes.chave
 *        Chave publica/segredo, ou uma funcao `(cabecalho) => chave` para
 *        resolver por `kid`.
 * @param {string} opcoes.emissor        valor exigido em `iss`
 * @param {string} opcoes.audiencia      valor exigido em `aud`
 * @param {number} [opcoes.tolerancia=0] folga de relogio, em segundos
 * @param {number} [opcoes.agora]        epoch em segundos (testes)
 * @param {string[]} [opcoes.typAceitos] valores aceitos em `typ`
 * @param {number} [opcoes.idadeMaxima]  segundos desde `iat`
 * @returns {{payload: object, cabecalho: object}}
 */
export function verificar(token, {
  algoritmos,
  chave,
  emissor,
  audiencia,
  tolerancia = 0,
  agora = agoraEmSegundos(),
  typAceitos = null,
  idadeMaxima = null,
}) {
  if (!Array.isArray(algoritmos) || algoritmos.length === 0) {
    throw new ErroJwt('config_invalida', 'a lista de algoritmos aceitos e obrigatoria');
  }
  if (!emissor || !audiencia) {
    throw new ErroJwt('config_invalida', 'emissor e audiencia sao obrigatorios na verificacao');
  }

  const { cabecalho, payload, assinatura, entradaAssinatura } = decodificarSemVerificar(token);

  // --- 1. algoritmo: conferido contra a lista, NUNCA usado para escolher ------
  if (typeof cabecalho.alg !== 'string' || !algoritmos.includes(cabecalho.alg)) {
    throw new ErroJwt('alg_nao_permitido', `alg "${cabecalho.alg}" nao esta na lista aceita [${algoritmos.join(', ')}]`);
  }
  const spec = ALGORITMOS[cabecalho.alg];
  if (!spec) throw new ErroJwt('alg_desconhecido', `algoritmo nao suportado: ${cabecalho.alg}`);

  // --- 2. `crit`: se o emissor marcou uma extensao como critica e nao a --------
  //        entendemos, o certo e recusar, nao ignorar (RFC 7515 §4.1.11).
  if ('crit' in cabecalho) {
    throw new ErroJwt('crit_nao_suportado', 'cabecalho `crit` presente e nao suportado por este verificador');
  }

  if (typAceitos && !typAceitos.includes(cabecalho.typ)) {
    throw new ErroJwt('typ_invalido', `typ "${cabecalho.typ}" nao aceito`);
  }

  // --- 3. resolucao da chave -------------------------------------------------
  const chaveResolvida = typeof chave === 'function' ? chave(cabecalho) : chave;
  if (!chaveResolvida) {
    throw new ErroJwt('chave_desconhecida', `nenhuma chave para kid "${cabecalho.kid ?? '(ausente)'}"`);
  }

  // --- 4. assinatura --------------------------------------------------------
  if (!assinaturaConfere(cabecalho.alg, spec, entradaAssinatura, assinatura, chaveResolvida)) {
    throw new ErroJwt('assinatura_invalida', 'assinatura nao confere');
  }

  // --- 5. claims ------------------------------------------------------------
  validarClaims(payload, { emissor, audiencia, tolerancia, agora, idadeMaxima });

  return { payload, cabecalho };
}

function assinaturaConfere(alg, spec, entrada, assinatura, chave) {
  if (spec.familia === 'oct') {
    const esperada = createHmac(spec.hash, normalizarSegredo(chave, alg)).update(entrada).digest();
    // timingSafeEqual exige o mesmo comprimento; conferir antes evita a excecao
    // e nao vaza nada (o tamanho do HMAC nao e segredo).
    if (esperada.length !== assinatura.length) return false;
    return timingSafeEqual(esperada, assinatura);
  }
  try {
    return verificarCripto(spec.hash, entrada, { key: chave, ...(spec.opcoes ?? {}) }, assinatura);
  } catch {
    // Chave do tipo errado para o alg declarado (ex.: chave EC com RS256).
    // Isso e exatamente o que a confusao de algoritmo tenta provocar.
    return false;
  }
}

function validarClaims(payload, { emissor, audiencia, tolerancia, agora, idadeMaxima }) {
  if (payload.iss !== emissor) {
    throw new ErroJwt('emissor_invalido', `iss "${payload.iss}" != "${emissor}"`);
  }

  // `aud` pode ser string ou array de strings (RFC 7519 §4.1.3).
  const aud = payload.aud;
  const audOk = typeof aud === 'string' ? aud === audiencia : Array.isArray(aud) && aud.includes(audiencia);
  if (!audOk) {
    throw new ErroJwt('audiencia_invalida', `aud nao contem "${audiencia}"`);
  }

  if (payload.exp === undefined) {
    throw new ErroJwt('exp_ausente', 'token sem exp: este servico nao aceita token eterno');
  }
  if (!Number.isFinite(payload.exp)) {
    throw new ErroJwt('exp_invalido', 'exp precisa ser numerico (segundos desde a epoca)');
  }
  // A comparacao e `>=`: no instante exato de exp o token JA expirou (RFC 7519 §4.1.4).
  if (agora >= payload.exp + tolerancia) {
    throw new ErroJwt('expirado', `token expirou em ${new Date(payload.exp * 1000).toISOString()}`);
  }

  if (payload.nbf !== undefined) {
    if (!Number.isFinite(payload.nbf)) throw new ErroJwt('nbf_invalido', 'nbf precisa ser numerico');
    if (agora + tolerancia < payload.nbf) {
      throw new ErroJwt('ainda_nao_valido', `token so vale a partir de ${new Date(payload.nbf * 1000).toISOString()}`);
    }
  }

  if (payload.iat !== undefined && !Number.isFinite(payload.iat)) {
    throw new ErroJwt('iat_invalido', 'iat precisa ser numerico');
  }
  if (idadeMaxima !== null) {
    if (payload.iat === undefined) throw new ErroJwt('iat_ausente', 'idadeMaxima exige iat');
    if (agora - payload.iat > idadeMaxima + tolerancia) {
      throw new ErroJwt('velho_demais', `token emitido ha mais de ${idadeMaxima}s`);
    }
  }
}

// ---------------------------------------------------------------------------
// Utilitarios
// ---------------------------------------------------------------------------

/** Epoch em SEGUNDOS. O erro classico e usar Date.now(), que da milissegundos. */
export function agoraEmSegundos() {
  return Math.floor(Date.now() / 1000);
}

/**
 * Thumbprint de JWK (RFC 7638): identificador estavel de chave, derivado da
 * propria chave publica. Usado como `kid`.
 *
 * Regra: SHA-256 do JSON canonico com SOMENTE os membros obrigatorios da
 * familia, em ordem lexicografica, sem espaco nenhum. Qualquer desvio muda o
 * thumbprint e quebra a interoperabilidade.
 */
export function thumbprintJwk(jwk) {
  const membros = {
    EC: ['crv', 'kty', 'x', 'y'],
    RSA: ['e', 'kty', 'n'],
    oct: ['k', 'kty'],
    OKP: ['crv', 'kty', 'x'],
  }[jwk.kty];
  if (!membros) throw new ErroJwt('kty_desconhecido', `kty nao suportado: ${jwk.kty}`);

  const canonico = {};
  for (const membro of membros) canonico[membro] = jwk[membro];
  return createHash('sha256').update(JSON.stringify(canonico), 'utf8').digest('base64url');
}
