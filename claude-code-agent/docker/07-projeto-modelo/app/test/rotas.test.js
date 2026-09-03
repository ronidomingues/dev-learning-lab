// Teste de integração HTTP: sobe o servidor de verdade numa porta efêmera e faz requisições.
// Sem mock — é o comportamento observável que interessa.

import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { Repositorio } from '../src/repositorio.js';
import { criarManipulador } from '../src/rotas.js';

let servidor;
let base;
let pastaTemp;

async function pedir(caminho, opcoes = {}) {
  const resposta = await fetch(base + caminho, opcoes);
  const texto = await resposta.text();
  return {
    status: resposta.status,
    corpo: texto ? JSON.parse(texto) : null,
    tipo: resposta.headers.get('content-type'),
    texto,
  };
}

describe('rotas HTTP', () => {
  before(async () => {
    pastaTemp = await mkdtemp(join(tmpdir(), 'mural-http-'));
    const repositorio = new Repositorio({ caminho: join(pastaTemp, 'r.json') });
    await repositorio.iniciar();

    const config = { nomeDoMural: 'Mural de Teste', ambiente: 'test' };
    servidor = http.createServer(criarManipulador({ repositorio, config }));

    await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
    base = `http://127.0.0.1:${servidor.address().port}`;
  });

  after(async () => {
    await new Promise((r) => servidor.close(r));
    await rm(pastaTemp, { recursive: true, force: true });
  });

  test('GET /saude responde 200 com status ok', async () => {
    const r = await pedir('/saude');
    assert.equal(r.status, 200);
    assert.equal(r.corpo.status, 'ok');
  });

  test('GET /vivo responde 200', async () => {
    const r = await pedir('/vivo');
    assert.equal(r.status, 200);
    assert.equal(r.corpo.status, 'vivo');
  });

  test('GET / devolve HTML com o nome configurado', async () => {
    const resposta = await fetch(base + '/');
    const html = await resposta.text();
    assert.equal(resposta.status, 200);
    assert.match(resposta.headers.get('content-type'), /text\/html/);
    assert.match(html, /Mural de Teste/);
  });

  test('POST /api/recados cria e devolve 201', async () => {
    const r = await pedir('/api/recados', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ autor: 'Ana', texto: 'Olá container' }),
    });
    assert.equal(r.status, 201);
    assert.equal(r.corpo.autor, 'Ana');
    assert.ok(r.corpo.id);
  });

  test('GET /api/recados lista o que foi criado', async () => {
    const r = await pedir('/api/recados');
    assert.equal(r.status, 200);
    assert.ok(r.corpo.total >= 1);
    assert.equal(r.corpo.recados[0].texto, 'Olá container');
  });

  test('POST com corpo inválido devolve 400 e mensagem legível', async () => {
    const r = await pedir('/api/recados', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ autor: '', texto: '' }),
    });
    assert.equal(r.status, 400);
    assert.match(r.corpo.erro, /autor/);
  });

  test('POST com JSON malformado devolve 400, não 500', async () => {
    const r = await pedir('/api/recados', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{ quebrado',
    });
    assert.equal(r.status, 400);
  });

  test('DELETE de id inexistente devolve 404', async () => {
    const r = await pedir('/api/recados/nao-existe', { method: 'DELETE' });
    assert.equal(r.status, 404);
  });

  test('rota desconhecida devolve 404 em JSON', async () => {
    const r = await pedir('/nada/aqui');
    assert.equal(r.status, 404);
    assert.match(r.tipo, /application\/json/);
  });

  test('a resposta de erro não vaza stack trace', async () => {
    const r = await pedir('/api/recados', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ autor: 'A' }),
    });
    assert.equal(r.status, 400);
    assert.ok(!r.texto.includes('at '), 'a resposta não deve conter stack trace');
  });
});
