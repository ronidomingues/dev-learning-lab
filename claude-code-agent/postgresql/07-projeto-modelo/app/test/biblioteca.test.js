// Testes de integração contra um PostgreSQL DE VERDADE.
//
// Estes testes EXIGEM um banco acessível via DATABASE_URL, com o schema aplicado.
// A forma mais fácil de rodá-los é com o compose deste projeto:
//   docker compose --profile testes run --rm testes
// ou, com um Postgres local:
//   psql "$DATABASE_URL" -f schema/001_schema.sql -f schema/002_functions.sql -f schema/003_seed.sql
//   DATABASE_URL=... node --test
//
// Se DATABASE_URL não estiver definida, os testes são PULADOS com um aviso — em vez de
// falharem com erro de conexão confuso. Isso é honesto: o teste diz o que precisa.

import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';

const TEM_BANCO = Boolean(process.env.DATABASE_URL);

let repo, db;
before(async () => {
  if (!TEM_BANCO) return;
  repo = await import('../src/repositorio.js');
  db = await import('../src/db.js');
});
after(async () => {
  if (TEM_BANCO && db) await db.fechar();
});

// Helper: pega um exemplar disponível de qualquer livro.
async function umExemplarLivre() {
  const livros = await repo.listarLivros();
  for (const l of livros) {
    const ex = await repo.exemplaresDisponiveis(l.id);
    if (ex.length) return ex[0].exemplar_id;
  }
  throw new Error('nenhum exemplar livre no seed');
}

test('lista livros do seed com autores', { skip: !TEM_BANCO && 'defina DATABASE_URL' }, async () => {
  const livros = await repo.listarLivros();
  assert.ok(livros.length >= 4, 'esperava ao menos 4 livros do seed');
  const dom = livros.find((l) => l.titulo === 'Dom Casmurro');
  assert.ok(dom, 'Dom Casmurro deveria existir');
  assert.ok(dom.autores.includes('Machado de Assis'));
});

test('busca por título filtra', { skip: !TEM_BANCO && 'defina DATABASE_URL' }, async () => {
  const r = await repo.listarLivros({ busca: 'vidas' });
  assert.equal(r.length, 1);
  assert.equal(r[0].titulo, 'Vidas Secas');
});

test('emprestar e devolver um exemplar', { skip: !TEM_BANCO && 'defina DATABASE_URL' }, async () => {
  const exemplar = await umExemplarLivre();
  const livros = await repo.listarLivros();
  const membroId = 1;

  const emprestimoId = await repo.emprestar(exemplar, membroId, 7);
  assert.ok(emprestimoId, 'deveria retornar um id de empréstimo');

  // Agora o exemplar NÃO deve estar mais em nenhuma lista de disponíveis.
  const listaTodos = [];
  for (const l of livros) listaTodos.push(...(await repo.exemplaresDisponiveis(l.id)));
  assert.ok(!listaTodos.some((e) => e.exemplar_id === exemplar), 'exemplar não deveria estar livre');

  const devolvido = await repo.devolver(exemplar);
  assert.equal(devolvido, true);

  // Devolver de novo é idempotente: retorna false, não quebra.
  const devolvidoDeNovo = await repo.devolver(exemplar);
  assert.equal(devolvidoDeNovo, false);
});

test('não empresta o mesmo exemplar duas vezes', { skip: !TEM_BANCO && 'defina DATABASE_URL' }, async () => {
  const exemplar = await umExemplarLivre();
  await repo.emprestar(exemplar, 1, 7);
  await assert.rejects(
    () => repo.emprestar(exemplar, 2, 7),
    (e) => e.name === 'ErroNegocio' && e.codigo === 'indisponivel',
    'o segundo empréstimo do mesmo exemplar deve falhar',
  );
  await repo.devolver(exemplar); // limpa
});

test('cadastra livro com autores numa transação', { skip: !TEM_BANCO && 'defina DATABASE_URL' }, async () => {
  const id = await repo.cadastrarLivro({
    titulo: 'Livro de Teste',
    ano: 2026,
    genero: 'técnico',
    autores: ['Autor Teste', 'Coautor Teste'],
  });
  assert.ok(id);
  const livros = await repo.listarLivros({ busca: 'Livro de Teste' });
  assert.equal(livros[0].autores.length, 2);
});
