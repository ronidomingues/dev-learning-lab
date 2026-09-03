import test from 'node:test';
import assert from 'node:assert/strict';
import { criarServidor } from '../src/servidor.js';
import { RepositorioDeTarefas } from '../src/tarefas.js';

/** Sobe o servidor numa porta livre e devolve a base da URL + um encerrador. */
async function subir() {
  const repositorio = new RepositorioDeTarefas(
    () => new Date('2026-08-13T12:00:00.000Z'),
  );
  const servidor = criarServidor({ repositorio });
  await new Promise((ok) => servidor.listen(0, '127.0.0.1', ok));
  const { port } = servidor.address();
  return {
    base: `http://127.0.0.1:${port}`,
    fechar: () => new Promise((ok) => servidor.close(ok)),
  };
}

test('GET /saude responde 200', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  const r = await fetch(`${base}/saude`);
  assert.equal(r.status, 200);
  assert.deepEqual(await r.json(), { status: 'ok', tarefas: 0 });
});

test('POST /tarefas cria e devolve 201 com Location', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  const r = await fetch(`${base}/tarefas`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ titulo: 'escrever hook', prioridade: 'alta' }),
  });
  assert.equal(r.status, 201);
  assert.equal(r.headers.get('location'), '/tarefas/1');
  const corpo = await r.json();
  assert.equal(corpo.titulo, 'escrever hook');
  assert.equal(corpo.prioridade, 'alta');
});

test('POST /tarefas com título vazio devolve 400', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  const r = await fetch(`${base}/tarefas`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ titulo: '' }),
  });
  assert.equal(r.status, 400);
  assert.deepEqual(await r.json(), { erro: 'titulo é obrigatório' });
});

test('POST /tarefas com JSON quebrado devolve 400, não 500', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  const r = await fetch(`${base}/tarefas`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: '{isto não é json',
  });
  assert.equal(r.status, 400);
  assert.equal((await r.json()).erro, 'corpo não é JSON válido');
});

test('GET /tarefas/:id inexistente devolve 404', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  const r = await fetch(`${base}/tarefas/42`);
  assert.equal(r.status, 404);
});

test('POST /tarefas/:id/concluir marca como concluída', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  await fetch(`${base}/tarefas`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ titulo: 'x' }),
  });
  const r = await fetch(`${base}/tarefas/1/concluir`, { method: 'POST' });
  assert.equal(r.status, 200);
  const corpo = await r.json();
  assert.equal(corpo.concluida, true);
  assert.equal(corpo.concluidaEm, '2026-08-13T12:00:00.000Z');
});

test('DELETE /tarefas/:id devolve 204 e some da listagem', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  await fetch(`${base}/tarefas`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ titulo: 'apagar' }),
  });
  const r = await fetch(`${base}/tarefas/1`, { method: 'DELETE' });
  assert.equal(r.status, 204);
  const lista = await (await fetch(`${base}/tarefas`)).json();
  assert.equal(lista.length, 0);
});

test('método não suportado devolve 405', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  const r = await fetch(`${base}/tarefas`, { method: 'PUT' });
  assert.equal(r.status, 405);
});

test('rota desconhecida devolve 404', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  const r = await fetch(`${base}/nada`);
  assert.equal(r.status, 404);
});

test('filtro ?concluida=true funciona pela query string', async (t) => {
  const { base, fechar } = await subir();
  t.after(fechar);
  for (const titulo of ['a', 'b']) {
    await fetch(`${base}/tarefas`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ titulo }),
    });
  }
  await fetch(`${base}/tarefas/1/concluir`, { method: 'POST' });
  const feitas = await (await fetch(`${base}/tarefas?concluida=true`)).json();
  const pendentes = await (await fetch(`${base}/tarefas?concluida=false`)).json();
  assert.equal(feitas.length, 1);
  assert.equal(pendentes.length, 1);
});
