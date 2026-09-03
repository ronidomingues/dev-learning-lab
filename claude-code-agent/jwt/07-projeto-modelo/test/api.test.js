/** Testes de ponta a ponta da API, com servidor HTTP de verdade. */

import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { montarAplicacao } from '../src/servidor.js';
import { Armazem } from '../src/armazem.js';
import { gerarChave, Chaveiro } from '../src/chaves.js';
import { agoraEmSegundos } from '../src/jwt.js';

const SENHA = 'senha-bem-comprida-1';

// Relogio controlavel: e o unico jeito honesto de testar expiracao sem
// deixar a suite lenta ou intermitente.
let deslocamento = 0;
const relogio = () => agoraEmSegundos() + deslocamento;

const configuracao = {
  emissor: 'https://teste.local',
  audiencia: 'cofre-de-notas-api',
  vidaAccessSegundos: 900,
  vidaRefreshSegundos: 1_209_600,
  toleranciaRelogioSegundos: 0,
  cookieSeguro: false,
};

let app;
let base;

before(async () => {
  const chave = gerarChave();
  app = montarAplicacao({
    armazem: new Armazem(),
    chaveiro: new Chaveiro([chave], chave.kid),
    configuracao,
    relogio,
  });
  await new Promise((ok) => app.servidor.listen(0, ok));
  base = `http://127.0.0.1:${app.servidor.address().port}`;
});

after(() => app.servidor.close());

// --- auxiliares -------------------------------------------------------------

async function pedir(caminho, { metodo = 'GET', corpo, token, cookie } = {}) {
  const cabecalhos = {};
  if (corpo !== undefined) cabecalhos['content-type'] = 'application/json';
  if (token) cabecalhos.authorization = `Bearer ${token}`;
  if (cookie) cabecalhos.cookie = cookie;
  const resposta = await fetch(base + caminho, {
    method: metodo,
    headers: cabecalhos,
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });
  const texto = await resposta.text();
  return {
    status: resposta.status,
    cabecalhos: resposta.headers,
    corpo: texto ? JSON.parse(texto) : null,
  };
}

let contador = 0;
async function novaConta(papeis) {
  const email = `pessoa${contador++}@teste.local`;
  await pedir('/auth/registrar', { metodo: 'POST', corpo: { email, senha: SENHA, papeis } });
  const login = await pedir('/auth/login', { metodo: 'POST', corpo: { email, senha: SENHA } });
  return { email, ...login.corpo };
}

// --- testes -----------------------------------------------------------------

describe('descoberta', () => {
  test('GET /.well-known/jwks.json publica a chave publica, e so ela', async () => {
    const r = await pedir('/.well-known/jwks.json');
    assert.equal(r.status, 200);
    assert.equal(r.corpo.keys.length, 1);
    const jwk = r.corpo.keys[0];
    assert.equal(jwk.kty, 'EC');
    assert.equal(jwk.crv, 'P-256');
    assert.equal(jwk.use, 'sig');
    assert.equal(jwk.alg, 'ES256');
    assert.ok(jwk.kid);
    // O componente privado (`d`) JAMAIS pode aparecer aqui.
    assert.equal(jwk.d, undefined);
  });
});

describe('registro e login', () => {
  test('registra e devolve o par de tokens no login', async () => {
    const conta = await novaConta();
    assert.ok(conta.access_token);
    assert.ok(conta.refresh_token);
    assert.equal(conta.token_type, 'Bearer');
    assert.equal(conta.expires_in, 900);
  });

  test('senha curta e recusada', async () => {
    const r = await pedir('/auth/registrar', {
      metodo: 'POST', corpo: { email: 'curta@teste.local', senha: '123' },
    });
    assert.equal(r.status, 400);
    assert.equal(r.corpo.erro, 'senha_curta');
  });

  test('e-mail duplicado e recusado', async () => {
    const corpo = { email: 'dup@teste.local', senha: SENHA };
    await pedir('/auth/registrar', { metodo: 'POST', corpo });
    const r = await pedir('/auth/registrar', { metodo: 'POST', corpo });
    assert.equal(r.status, 409);
  });

  test('senha errada e e-mail inexistente dao a MESMA resposta', async () => {
    const conta = await novaConta();
    const senhaErrada = await pedir('/auth/login', {
      metodo: 'POST', corpo: { email: conta.email, senha: 'senha-errada-mas-longa' },
    });
    const naoExiste = await pedir('/auth/login', {
      metodo: 'POST', corpo: { email: 'fantasma@teste.local', senha: SENHA },
    });
    assert.equal(senhaErrada.status, 401);
    assert.deepEqual(senhaErrada.corpo, naoExiste.corpo);
  });

  test('o refresh vem em cookie HttpOnly, SameSite=Strict, com Path restrito', async () => {
    const conta = await novaConta();
    const login = await pedir('/auth/login', {
      metodo: 'POST', corpo: { email: conta.email, senha: SENHA },
    });
    const cookie = login.cabecalhos.get('set-cookie');
    assert.match(cookie, /HttpOnly/);
    assert.match(cookie, /SameSite=Strict/);
    assert.match(cookie, /Path=\/auth\/refresh/);
  });
});

describe('rota protegida', () => {
  test('sem token: 401 com WWW-Authenticate', async () => {
    const r = await pedir('/notas');
    assert.equal(r.status, 401);
    assert.match(r.cabecalhos.get('www-authenticate'), /^Bearer error="invalid_token"/);
  });

  test('com token: acessa e isola por usuario', async () => {
    const ana = await novaConta();
    const beto = await novaConta();

    await pedir('/notas', { metodo: 'POST', corpo: { texto: 'segredo da Ana' }, token: ana.access_token });

    const daAna = await pedir('/notas', { token: ana.access_token });
    const doBeto = await pedir('/notas', { token: beto.access_token });
    assert.equal(daAna.corpo.notas.length, 1);
    assert.equal(doBeto.corpo.notas.length, 0);
  });

  test('token com assinatura mexida e recusado', async () => {
    const conta = await novaConta();
    const [cab, corpo, sig] = conta.access_token.split('.');
    const trocado = sig[0] === 'A' ? `B${sig.slice(1)}` : `A${sig.slice(1)}`;
    const r = await pedir('/notas', { token: `${cab}.${corpo}.${trocado}` });
    assert.equal(r.status, 401);
    assert.equal(r.corpo.erro, 'assinatura_invalida');
  });

  test('esquema errado (Basic) e recusado', async () => {
    const r = await fetch(`${base}/notas`, { headers: { authorization: 'Basic YWJjOjEyMw==' } });
    assert.equal(r.status, 401);
  });

  test('access token expirado e recusado quando o relogio avanca', async () => {
    const conta = await novaConta();
    assert.equal((await pedir('/notas', { token: conta.access_token })).status, 200);
    deslocamento += 901; // passa de exp
    assert.equal((await pedir('/notas', { token: conta.access_token })).corpo.erro, 'expirado');
    deslocamento -= 901;
  });

  test('DELETE remove a propria nota', async () => {
    const conta = await novaConta();
    const criada = await pedir('/notas', { metodo: 'POST', corpo: { texto: 'apagar' }, token: conta.access_token });
    const r = await pedir(`/notas/${criada.corpo.id}`, { metodo: 'DELETE', token: conta.access_token });
    assert.equal(r.status, 204);
    assert.equal((await pedir('/notas', { token: conta.access_token })).corpo.notas.length, 0);
  });
});

describe('autorizacao por papel', () => {
  test('usuario comum recebe 403 na rota de admin', async () => {
    const conta = await novaConta();
    const r = await pedir('/admin/sessoes', { token: conta.access_token });
    assert.equal(r.status, 403);
    assert.equal(r.corpo.erro, 'sem_permissao');
    assert.match(r.cabecalhos.get('www-authenticate'), /insufficient_scope/);
  });

  test('admin acessa', async () => {
    const admin = await novaConta('admin');
    const r = await pedir('/admin/sessoes', { token: admin.access_token });
    assert.equal(r.status, 200);
    assert.ok(r.corpo.refreshAtivos >= 1);
  });
});

describe('rotacao de refresh e deteccao de reuso', () => {
  test('refresh devolve tokens novos e invalida o antigo', async () => {
    const conta = await novaConta();
    const r1 = await pedir('/auth/refresh', { metodo: 'POST', corpo: { refresh_token: conta.refresh_token } });
    assert.equal(r1.status, 200);
    assert.notEqual(r1.corpo.refresh_token, conta.refresh_token);
    assert.ok(r1.corpo.access_token);
    // o token novo funciona
    assert.equal((await pedir('/notas', { token: r1.corpo.access_token })).status, 200);
  });

  test('reusar um refresh ja gasto derruba a familia inteira', async () => {
    const conta = await novaConta();
    const r1 = await pedir('/auth/refresh', { metodo: 'POST', corpo: { refresh_token: conta.refresh_token } });

    // Alguem (ou um bug) usa de novo o refresh original:
    const reuso = await pedir('/auth/refresh', { metodo: 'POST', corpo: { refresh_token: conta.refresh_token } });
    assert.equal(reuso.status, 401);
    assert.equal(reuso.corpo.erro, 'reuso_detectado');

    // E o refresh legitimo, que estava valido, tambem morre. E o preco:
    // nao da para saber qual dos dois lados era o ladrao.
    const depois = await pedir('/auth/refresh', { metodo: 'POST', corpo: { refresh_token: r1.corpo.refresh_token } });
    assert.equal(depois.status, 401);
  });

  test('refresh desconhecido nao vaza informacao e limpa o cookie', async () => {
    const r = await pedir('/auth/refresh', { metodo: 'POST', corpo: { refresh_token: 'inventado' } });
    assert.equal(r.status, 401);
    assert.match(r.cabecalhos.get('set-cookie'), /Max-Age=0/);
  });

  test('o refresh tambem e lido do cookie', async () => {
    const conta = await novaConta();
    const r = await pedir('/auth/refresh', {
      metodo: 'POST', cookie: `refresh_token=${conta.refresh_token}`,
    });
    assert.equal(r.status, 200);
  });
});

describe('logout', () => {
  test('mata o access token na hora (lista de negacao por jti)', async () => {
    const conta = await novaConta();
    assert.equal((await pedir('/notas', { token: conta.access_token })).status, 200);

    const saida = await pedir('/auth/logout', {
      metodo: 'POST', token: conta.access_token, corpo: { refresh_token: conta.refresh_token },
    });
    assert.equal(saida.corpo.accessRevogado, true);
    assert.equal(saida.corpo.familiaEncerrada, true);

    // Sem a lista de negacao, este token ainda valeria por ~15 minutos.
    const depois = await pedir('/notas', { token: conta.access_token });
    assert.equal(depois.status, 401);
    assert.equal(depois.corpo.erro, 'token_revogado');
  });

  test('mata o refresh: nao da mais para renovar', async () => {
    const conta = await novaConta();
    await pedir('/auth/logout', {
      metodo: 'POST', token: conta.access_token, corpo: { refresh_token: conta.refresh_token },
    });
    const r = await pedir('/auth/refresh', { metodo: 'POST', corpo: { refresh_token: conta.refresh_token } });
    assert.equal(r.status, 401);
  });
});

describe('higiene', () => {
  test('respostas com token trazem cache-control: no-store', async () => {
    const conta = await novaConta();
    const r = await pedir('/auth/login', { metodo: 'POST', corpo: { email: conta.email, senha: SENHA } });
    assert.equal(r.cabecalhos.get('cache-control'), 'no-store');
  });

  test('o payload do access token nao carrega e-mail nem hash de senha', async () => {
    const conta = await novaConta();
    const r = await pedir('/debug/decodificar', { metodo: 'POST', corpo: { token: conta.access_token } });
    const claims = Object.keys(r.corpo.payload).sort();
    assert.deepEqual(claims, ['aud', 'exp', 'iat', 'iss', 'jti', 'papeis', 'sub']);
    assert.equal(r.corpo.cabecalho.typ, 'at+jwt');
  });

  test('a lista de negacao e limpa quando os tokens expiram', async () => {
    const conta = await novaConta();
    await pedir('/auth/logout', { metodo: 'POST', token: conta.access_token });
    const antes = app.armazem.jtiRevogados.size;
    assert.ok(antes >= 1);
    app.armazem.limpar(relogio() + 100_000);
    assert.equal(app.armazem.jtiRevogados.size, 0);
  });

  test('rota inexistente devolve 404', async () => {
    assert.equal((await pedir('/nao-existe')).status, 404);
  });
});
