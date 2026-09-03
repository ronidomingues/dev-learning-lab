import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { criarConfig } from '../src/config.mjs';
import { criarServidor } from '../src/servidor.mjs';
import { criarLog, redigir, redigirUrl } from '../src/log.mjs';

const API_KEY = 'sk_test_chave_de_teste';
const { config } = criarConfig({
  DATABASE_URL: 'postgres://app:senha-secreta-do-banco@localhost:5432/recados',
  SESSION_SECRET: 'z'.repeat(40),
  API_KEY,
  // A porta do teste NÃO vem daqui: o servidor é aberto com listen(0), que pede
  // uma porta livre ao sistema. Assim os testes não brigam entre si nem com o CI.
  LOG_LEVEL: 'error',
  EXPOR_METRICAS: 'true',
});

let base;
let servidor;

before(async () => {
  ({ servidor } = criarServidor(config, { log: criarLog('error') }));
  await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
  base = `http://127.0.0.1:${servidor.address().port}`;
});

after(() => servidor.close());

const comChave = (extra = {}) => ({ authorization: `Bearer ${API_KEY}`, ...extra });

describe('rotas', () => {
  test('/health é público', async () => {
    const r = await fetch(`${base}/health`);
    assert.equal(r.status, 200);
    assert.deepEqual(await r.json(), { ok: true, ambiente: 'development' });
  });

  test('/recados exige a chave', async () => {
    const r = await fetch(`${base}/recados`);
    assert.equal(r.status, 401);
  });

  test('chave errada do mesmo tamanho é recusada', async () => {
    const r = await fetch(`${base}/recados`, {
      headers: { authorization: `Bearer ${'x'.repeat(API_KEY.length)}` },
    });
    assert.equal(r.status, 401);
  });

  test('cria e lista recado', async () => {
    const criado = await fetch(`${base}/recados`, {
      method: 'POST',
      headers: comChave({ 'content-type': 'application/json' }),
      body: JSON.stringify({ texto: 'comprar pão' }),
    });
    assert.equal(criado.status, 201);
    const corpo = await criado.json();
    assert.equal(corpo.texto, 'comprar pão');
    assert.match(corpo.assinatura, /^[A-Za-z0-9_-]{16}$/);

    const lista = await fetch(`${base}/recados`, { headers: comChave() });
    const { total } = await lista.json();
    assert.ok(total >= 1);
  });

  test('recusa recado sem texto', async () => {
    const r = await fetch(`${base}/recados`, {
      method: 'POST',
      headers: comChave({ 'content-type': 'application/json' }),
      body: JSON.stringify({ texto: '   ' }),
    });
    assert.equal(r.status, 400);
  });

  test('rota desconhecida devolve 404 em JSON', async () => {
    const r = await fetch(`${base}/nao-existe`);
    assert.equal(r.status, 404);
    assert.equal((await r.json()).erro, 'rota não encontrada');
  });

  test('/metrics só aparece com EXPOR_METRICAS=true', async () => {
    const r = await fetch(`${base}/metrics`);
    assert.equal(r.status, 200);

    const { config: semMetricas } = criarConfig({
      DATABASE_URL: 'memory://x',
      SESSION_SECRET: 'z'.repeat(40),
      API_KEY,
      EXPOR_METRICAS: 'false',
    });
    const { servidor: s2 } = criarServidor(semMetricas, { log: criarLog('error') });
    await new Promise((r2) => s2.listen(0, '127.0.0.1', r2));
    const r2 = await fetch(`http://127.0.0.1:${s2.address().port}/metrics`);
    assert.equal(r2.status, 404);
    s2.close();
  });
});

describe('a rota /config não pode vazar segredo — este é o teste que mais importa', () => {
  test('exige autenticação', async () => {
    assert.equal((await fetch(`${base}/config`)).status, 401);
  });

  test('nenhum segredo aparece inteiro na resposta', async () => {
    const r = await fetch(`${base}/config`, { headers: comChave() });
    assert.equal(r.status, 200);
    const texto = await r.text();
    assert.ok(!texto.includes(config.sessionSecret), 'SESSION_SECRET vazou');
    assert.ok(!texto.includes(config.apiKey), 'API_KEY vazou');
    assert.ok(!texto.includes('senha-secreta-do-banco'), 'senha do banco vazou');
    // e mesmo assim é útil para o suporte:
    assert.match(texto, /localhost:5432/);
  });
});

describe('log', () => {
  test('redige chaves sensíveis, inclusive aninhadas', () => {
    const saida = redigir({
      usuario: 'maria',
      senha: 'abc',
      headers: { authorization: 'Bearer x', 'user-agent': 'curl' },
      lista: [{ token: 't' }],
    });
    assert.equal(saida.senha, '[REDIGIDO]');
    assert.equal(saida.headers.authorization, '[REDIGIDO]');
    assert.equal(saida.headers['user-agent'], 'curl');
    assert.equal(saida.lista[0].token, '[REDIGIDO]');
    assert.equal(saida.usuario, 'maria');
  });

  test('aguenta referência circular', () => {
    const o = { a: 1 };
    o.self = o;
    assert.equal(redigir(o).self, '[circular]');
  });

  test('redigirUrl remove a senha embutida na URL — o que a redação por chave não pega', () => {
    assert.equal(
      redigirUrl('postgres://app:senha-secreta@db:5432/loja'),
      'postgres://app:***@db:5432/loja',
    );
  });

  test('o log real não deixa segredo escapar', () => {
    const linhas = [];
    const log = criarLog('info', (l) => linhas.push(l));
    log.info('conectando', { db: { host: 'x', password: 'p4ssw0rd' } });
    assert.ok(!linhas.join('').includes('p4ssw0rd'));
    assert.ok(linhas.join('').includes('[REDIGIDO]'));
  });

  test('respeita o nível mínimo', () => {
    const linhas = [];
    const log = criarLog('warn', (l) => linhas.push(l));
    log.info('não deve aparecer');
    log.error('deve aparecer');
    assert.equal(linhas.length, 1);
  });
});
