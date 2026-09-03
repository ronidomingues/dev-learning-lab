/**
 * Testes das partes puras — rodam em milissegundos, sem subir servidor.
 * Toda lógica que puder ser testada assim, deve ser.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { validar } from '../src/validacao.js';
import { CriarLivro } from '../src/esquemas.js';
import { etagDe, etagCasa, cursor } from '../src/http.js';
import { criarRoteador } from '../src/roteador.js';
import { criarRepositorio } from '../src/repositorio.js';
import { _limparParaTeste } from '../src/log.js';
import { Problema } from '../src/problemas.js';

test('validação: aceita um livro correto', () => {
  assert.deepEqual(
    validar({ titulo: 'Iracema', autor: 'José de Alencar', ano: 1865 }, CriarLivro),
    []
  );
});

test('validação: acusa campo obrigatório, tipo errado, faixa e campo extra', () => {
  const erros = validar({ titulo: 123, ano: 3000, preco: 10 }, CriarLivro);
  const campos = erros.map(e => e.campo);
  assert.ok(campos.includes('autor'),  'deveria exigir autor');
  assert.ok(campos.includes('titulo'), 'deveria recusar titulo numérico');
  assert.ok(campos.includes('ano'),    'deveria recusar ano fora da faixa');
  assert.ok(campos.includes('preco'),  'deveria recusar campo não reconhecido');
});

test('ETag: é estável para o mesmo conteúdo e muda quando o conteúdo muda', () => {
  const a = { id: '1', titulo: 'X', versao: 1 };
  const b = { versao: 1, titulo: 'X', id: '1' };   // mesma coisa, ordem diferente
  assert.equal(etagDe(a), etagDe(b), 'a ordem das chaves não pode afetar o ETag');
  assert.notEqual(etagDe(a), etagDe({ ...a, titulo: 'Y' }));
});

test('ETag: If-None-Match aceita lista e curinga', () => {
  const etag = '"abc123"';
  assert.equal(etagCasa(etag, etag), true);
  assert.equal(etagCasa(`"outro", ${etag}`, etag), true);
  assert.equal(etagCasa('*', etag), true);
  assert.equal(etagCasa('"nao-bate"', etag), false);
  assert.equal(etagCasa(undefined, etag), false);
});

test('cursor: é opaco e reversível; valor inválido vira Problema 400', () => {
  const id = 'a1b2c3d4-0000-4000-8000-000000000000';
  const codificado = cursor.codificar(id);
  assert.notEqual(codificado, id, 'o cursor não pode ser o id cru');
  assert.equal(cursor.decodificar(codificado), id);
  assert.equal(cursor.decodificar(null), null);

  // base64url inválido: o Buffer é tolerante, então garantimos que o vazio falha.
  assert.throws(() => cursor.decodificar('!!!!'), Problema);
});

test('roteador: extrai parâmetro e distingue 405 de 404', () => {
  const r = criarRoteador();
  r.get('/livros/:id', () => {});
  r.post('/livros', () => {});

  const achado = r.resolver('GET', '/livros/42');
  assert.equal(achado.params.id, '42');

  // caminho existe, método não → 405
  assert.throws(() => r.resolver('DELETE', '/livros/42'), e => e.status === 405);
  // caminho não existe → 404
  assert.throws(() => r.resolver('GET', '/nada'), e => e.status === 404);
});

test('repositório: paginação por cursor não repete nem pula itens', () => {
  const repo = criarRepositorio();
  repo.semear();

  const p1 = repo.listarLivros({ limite: 2 });
  assert.equal(p1.dados.length, 2);
  assert.ok(p1.proximoId, 'deveria haver próxima página');

  const p2 = repo.listarLivros({ limite: 2, depoisDe: p1.proximoId });
  const ids1 = p1.dados.map(l => l.id);
  const ids2 = p2.dados.map(l => l.id);
  assert.equal(ids1.filter(id => ids2.includes(id)).length, 0, 'não pode repetir item');

  // Percorre tudo e confere que o total bate.
  const vistos = new Set();
  let cursorAtual = null;
  for (let i = 0; i < 20; i++) {
    const p = repo.listarLivros({ limite: 2, depoisDe: cursorAtual });
    p.dados.forEach(l => vistos.add(l.id));
    if (!p.proximoId) break;
    cursorAtual = p.proximoId;
  }
  assert.equal(vistos.size, repo.estatisticas().livros);
});

test('log: oculta campos sensíveis, inclusive aninhados', () => {
  const limpo = _limparParaTeste({
    usuario: 'ana',
    authorization: 'Bearer segredo',
    nested: { password: '123', ok: 'visivel' }
  });
  assert.equal(limpo.usuario, 'ana');
  assert.equal(limpo.authorization, '[oculto]');
  assert.equal(limpo.nested.password, '[oculto]');
  assert.equal(limpo.nested.ok, 'visivel');
});
