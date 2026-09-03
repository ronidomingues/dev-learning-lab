/**
 * base64url — RFC 4648 §5, com o preenchimento ("=") removido.
 *
 * Por que base64url e nao base64 comum: um JWT viaja em URL, em cabecalho HTTP
 * e em cookie. O base64 comum usa "+", "/" e "=", que sao caracteres com
 * significado especial nesses tres lugares. O base64url troca "+" por "-",
 * "/" por "_" e joga o "=" fora.
 */

/** Bytes (Buffer) -> string base64url. */
export function paraBase64url(buffer) {
  return Buffer.from(buffer).toString('base64url');
}

/** String base64url -> Buffer. */
export function deBase64url(texto) {
  if (typeof texto !== 'string' || !/^[A-Za-z0-9_-]*$/.test(texto)) {
    throw new ErroBase64url('segmento nao e base64url valido');
  }
  return Buffer.from(texto, 'base64url');
}

/** Objeto JS -> string base64url do seu JSON UTF-8. */
export function jsonParaBase64url(objeto) {
  return paraBase64url(Buffer.from(JSON.stringify(objeto), 'utf8'));
}

/** String base64url -> objeto JS. */
export function base64urlParaJson(texto) {
  const bruto = deBase64url(texto).toString('utf8');
  let objeto;
  try {
    objeto = JSON.parse(bruto);
  } catch {
    throw new ErroBase64url('segmento nao contem JSON valido');
  }
  // Um JWT so aceita objeto JSON no topo. Array, numero ou string sao invalidos:
  // sem isso, um token com payload `null` passaria e viraria `undefined` adiante.
  if (objeto === null || typeof objeto !== 'object' || Array.isArray(objeto)) {
    throw new ErroBase64url('segmento nao e um objeto JSON');
  }
  return objeto;
}

export class ErroBase64url extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'ErroBase64url';
  }
}
