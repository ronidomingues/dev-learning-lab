/**
 * Testes da implementacao de JWS/JWT.
 *
 * Metade destes testes sao ATAQUES. Um teste que so confirma o caminho feliz
 * ("assino e verifico, funciona") nao prova nada sobre seguranca — o que
 * importa e que o token adulterado seja RECUSADO.
 */

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { createHmac, randomBytes, generateKeyPairSync } from 'node:crypto';
import { assinar, verificar, decodificarSemVerificar, thumbprintJwk, ErroJwt } from '../src/jwt.js';
import { gerarChave } from '../src/chaves.js';
import { paraBase64url, jsonParaBase64url, base64urlParaJson } from '../src/base64url.js';

const AGORA = 1_800_000_000; // 15/01/2027, fixo: teste com relogio real e teste intermitente
const BASE = { iss: 'https://emissor.teste', aud: 'api.teste', sub: 'u-1' };
const VERIFICACAO = { emissor: BASE.iss, audiencia: BASE.aud, agora: AGORA };

describe('base64url', () => {
  test('ida e volta preserva o conteudo', () => {
    const objeto = { a: 1, b: 'acentuacao: ção', c: [1, 2] };
    assert.deepEqual(base64urlParaJson(jsonParaBase64url(objeto)), objeto);
  });

  test('recusa caracteres do base64 comum (+ / =)', () => {
    assert.throws(() => base64urlParaJson('YQ=='), /base64url/);
    assert.throws(() => base64urlParaJson('a+b/c'), /base64url/);
  });

  test('recusa payload que nao e objeto JSON', () => {
    assert.throws(() => base64urlParaJson(paraBase64url(Buffer.from('null'))), /objeto JSON/);
    assert.throws(() => base64urlParaJson(paraBase64url(Buffer.from('[1,2]'))), /objeto JSON/);
  });
});

describe('assinar e verificar', () => {
  test('ES256: ida e volta', () => {
    const chave = gerarChave();
    const token = assinar({ ...BASE, exp: AGORA + 60 }, {
      alg: 'ES256', chave: chave.privada, kid: chave.kid, agora: AGORA,
    });
    const { payload, cabecalho } = verificar(token, {
      ...VERIFICACAO, algoritmos: ['ES256'], chave: chave.publica,
    });
    assert.equal(payload.sub, 'u-1');
    assert.equal(cabecalho.alg, 'ES256');
    assert.equal(cabecalho.kid, chave.kid);
    assert.equal(payload.iat, AGORA);
  });

  test('ES256 produz assinatura crua de 64 bytes (P1363), nao DER', () => {
    // Se sair DER, o token nao valida em nenhuma outra biblioteca JOSE.
    const chave = gerarChave();
    const token = assinar({ ...BASE, exp: AGORA + 60 }, { alg: 'ES256', chave: chave.privada, agora: AGORA });
    assert.equal(decodificarSemVerificar(token).assinatura.length, 64);
  });

  test('HS256: ida e volta', () => {
    const segredo = randomBytes(32);
    const token = assinar({ ...BASE, exp: AGORA + 60 }, { alg: 'HS256', chave: segredo, agora: AGORA });
    assert.equal(verificar(token, { ...VERIFICACAO, algoritmos: ['HS256'], chave: segredo }).payload.sub, 'u-1');
  });

  test('HS256 recusa segredo curto na assinatura', () => {
    assert.throws(
      () => assinar(BASE, { alg: 'HS256', chave: 'senha123', agora: AGORA }),
      (e) => e.codigo === 'segredo_fraco',
    );
  });

  test('o token tem exatamente tres segmentos separados por ponto', () => {
    const chave = gerarChave();
    const token = assinar({ ...BASE, exp: AGORA + 60 }, { alg: 'ES256', chave: chave.privada, agora: AGORA });
    assert.equal(token.split('.').length, 3);
  });
});

describe('ataques', () => {
  test('alg: none e recusado', () => {
    const cabecalho = jsonParaBase64url({ alg: 'none', typ: 'JWT' });
    const corpo = jsonParaBase64url({ ...BASE, exp: AGORA + 60 });
    const token = `${cabecalho}.${corpo}.`;
    assert.throws(
      () => verificar(token, { ...VERIFICACAO, algoritmos: ['ES256'], chave: gerarChave().publica }),
      (e) => e.codigo === 'alg_nao_permitido',
    );
  });

  test('alg: nOnE (variacao de caixa) tambem e recusado', () => {
    // Bibliotecas que comparam string sem normalizar caiam exatamente aqui.
    for (const variante of ['nOnE', 'NONE', 'None', ' none']) {
      const token = `${jsonParaBase64url({ alg: variante })}.${jsonParaBase64url({ ...BASE, exp: AGORA + 60 })}.`;
      assert.throws(
        () => verificar(token, { ...VERIFICACAO, algoritmos: ['ES256'], chave: gerarChave().publica }),
        (e) => e.codigo === 'alg_nao_permitido',
        `variante "${variante}" deveria ser recusada`,
      );
    }
  });

  test('confusao de algoritmo: RS256 -> HS256 com a chave publica como segredo', () => {
    // O ataque classico. Quem verifica le `alg` do token e escolhe o modo;
    // quem ataca troca para HMAC e usa a chave PUBLICA (que e publica!) como
    // segredo. Nossa implementacao nao le `alg` para escolher nada.
    const { privateKey, publicKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
    const pemPublico = publicKey.export({ type: 'spki', format: 'pem' });

    const cabecalho = jsonParaBase64url({ alg: 'HS256', typ: 'JWT' });
    const corpo = jsonParaBase64url({ ...BASE, sub: 'admin', exp: AGORA + 60 });
    const entrada = `${cabecalho}.${corpo}`;
    const forjada = createHmac('sha256', pemPublico).update(entrada).digest();
    const tokenForjado = `${entrada}.${paraBase64url(forjada)}`;

    assert.throws(
      () => verificar(tokenForjado, { ...VERIFICACAO, algoritmos: ['RS256'], chave: publicKey }),
      (e) => e.codigo === 'alg_nao_permitido',
    );
    // E mesmo que HS256 estivesse na lista aceita, a chave resolvida seria a
    // publica RSA (um KeyObject), que normalizarSegredo recusa:
    assert.throws(() => verificar(tokenForjado, { ...VERIFICACAO, algoritmos: ['HS256'], chave: publicKey }));
    assert.ok(privateKey); // a privada nunca foi necessaria para o ataque
  });

  test('payload adulterado invalida a assinatura', () => {
    const chave = gerarChave();
    const token = assinar({ ...BASE, papeis: ['usuario'], exp: AGORA + 60 }, {
      alg: 'ES256', chave: chave.privada, agora: AGORA,
    });
    const [cab, , sig] = token.split('.');
    const adulterado = `${cab}.${jsonParaBase64url({ ...BASE, papeis: ['admin'], exp: AGORA + 60, iat: AGORA })}.${sig}`;
    assert.throws(
      () => verificar(adulterado, { ...VERIFICACAO, algoritmos: ['ES256'], chave: chave.publica }),
      (e) => e.codigo === 'assinatura_invalida',
    );
  });

  test('assinatura de outra chave e recusada', () => {
    const boa = gerarChave();
    const ma = gerarChave();
    const token = assinar({ ...BASE, exp: AGORA + 60 }, { alg: 'ES256', chave: ma.privada, agora: AGORA });
    assert.throws(
      () => verificar(token, { ...VERIFICACAO, algoritmos: ['ES256'], chave: boa.publica }),
      (e) => e.codigo === 'assinatura_invalida',
    );
  });

  test('kid desconhecido nao resolve chave nenhuma', () => {
    const chave = gerarChave();
    const token = assinar({ ...BASE, exp: AGORA + 60 }, {
      alg: 'ES256', chave: chave.privada, kid: '../../etc/passwd', agora: AGORA,
    });
    const resolver = (cab) => (cab.kid === chave.kid ? chave.publica : null);
    assert.throws(
      () => verificar(token, { ...VERIFICACAO, algoritmos: ['ES256'], chave: resolver }),
      (e) => e.codigo === 'chave_desconhecida',
    );
  });

  test('cabecalho crit desconhecido e recusado, nao ignorado', () => {
    const chave = gerarChave();
    const cabecalho = jsonParaBase64url({ alg: 'ES256', crit: ['exp-politica'], 'exp-politica': 'x' });
    const corpo = jsonParaBase64url({ ...BASE, exp: AGORA + 60 });
    const token = `${cabecalho}.${corpo}.AAAA`;
    assert.throws(
      () => verificar(token, { ...VERIFICACAO, algoritmos: ['ES256'], chave: chave.publica }),
      (e) => e.codigo === 'crit_nao_suportado',
    );
  });

  test('token com 2 ou 5 segmentos e recusado', () => {
    for (const ruim of ['a.b', 'a.b.c.d.e', '', 'nada']) {
      assert.throws(() => decodificarSemVerificar(ruim), ErroJwt);
    }
  });
});

describe('claims', () => {
  const chave = gerarChave();
  const emitir = (extra, agora = AGORA) =>
    assinar({ ...BASE, exp: agora + 60, ...extra }, { alg: 'ES256', chave: chave.privada, agora });
  const conferir = (token, extra = {}) =>
    verificar(token, { ...VERIFICACAO, algoritmos: ['ES256'], chave: chave.publica, ...extra });

  test('expirado e recusado', () => {
    const token = emitir({ exp: AGORA - 1 });
    assert.throws(() => conferir(token), (e) => e.codigo === 'expirado');
  });

  test('no instante exato de exp o token ja morreu', () => {
    const token = emitir({ exp: AGORA });
    assert.throws(() => conferir(token), (e) => e.codigo === 'expirado');
  });

  test('tolerancia de relogio aceita expiracao recente', () => {
    const token = emitir({ exp: AGORA - 30 });
    assert.throws(() => conferir(token));                       // sem tolerancia: recusa
    assert.ok(conferir(token, { tolerancia: 60 }).payload);     // com 60 s: aceita
  });

  test('token sem exp e recusado', () => {
    const semExp = assinar({ ...BASE }, { alg: 'ES256', chave: chave.privada, agora: AGORA });
    assert.throws(() => conferir(semExp), (e) => e.codigo === 'exp_ausente');
  });

  test('nbf no futuro e recusado', () => {
    const token = emitir({ nbf: AGORA + 100, exp: AGORA + 200 });
    assert.throws(() => conferir(token), (e) => e.codigo === 'ainda_nao_valido');
  });

  test('emissor errado e recusado', () => {
    const token = emitir({ iss: 'https://outro.emissor' });
    assert.throws(() => conferir(token), (e) => e.codigo === 'emissor_invalido');
  });

  test('audiencia errada e recusada — o token do servico vizinho nao vale aqui', () => {
    const token = emitir({ aud: 'api.do.vizinho' });
    assert.throws(() => conferir(token), (e) => e.codigo === 'audiencia_invalida');
  });

  test('aud como array e aceito quando contem a audiencia', () => {
    const token = emitir({ aud: ['api.teste', 'outra.api'] });
    assert.equal(conferir(token).payload.sub, 'u-1');
  });

  test('idadeMaxima recusa token antigo mesmo dentro da validade', () => {
    const token = emitir({ exp: AGORA + 86400 });
    assert.throws(
      () => conferir(token, { idadeMaxima: 300, agora: AGORA + 600 }),
      (e) => e.codigo === 'velho_demais',
    );
  });

  test('verificar sem lista de algoritmos e erro de programacao', () => {
    const token = emitir({});
    assert.throws(
      () => verificar(token, { ...VERIFICACAO, chave: chave.publica }),
      (e) => e.codigo === 'config_invalida',
    );
  });

  test('verificar sem emissor/audiencia e erro de programacao', () => {
    const token = emitir({});
    assert.throws(
      () => verificar(token, { algoritmos: ['ES256'], chave: chave.publica, agora: AGORA }),
      (e) => e.codigo === 'config_invalida',
    );
  });
});

describe('thumbprint de JWK (RFC 7638)', () => {
  test('reproduz o vetor de teste da RFC 7638 §3.1', () => {
    const jwk = {
      kty: 'RSA',
      n: '0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw',
      e: 'AQAB',
      alg: 'RS256',
      kid: '2011-04-29',
    };
    assert.equal(thumbprintJwk(jwk), 'NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs');
  });

  test('o mesmo par de chaves sempre gera o mesmo kid', () => {
    const chave = gerarChave();
    assert.equal(thumbprintJwk(chave.publica.export({ format: 'jwk' })), chave.kid);
  });

  test('chaves diferentes geram kids diferentes', () => {
    assert.notEqual(gerarChave().kid, gerarChave().kid);
  });
});
