import test from 'node:test';
import assert from 'node:assert/strict';
import {
  RepositorioDeTarefas,
  ErroDeValidacao,
  NaoEncontrado,
} from '../src/tarefas.js';

// Relógio congelado: o teste não pode depender de "agora".
const RELOGIO = () => new Date('2026-08-13T12:00:00.000Z');

test('cria tarefa com valores padrão', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  const t = repo.criar({ titulo: 'estudar hooks' });
  assert.equal(t.id, 1);
  assert.equal(t.titulo, 'estudar hooks');
  assert.equal(t.prioridade, 'media');
  assert.equal(t.concluida, false);
  assert.equal(t.criadaEm, '2026-08-13T12:00:00.000Z');
  assert.equal(t.concluidaEm, null);
});

test('remove espaços em branco das bordas do título', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  assert.equal(repo.criar({ titulo: '  ler docs  ' }).titulo, 'ler docs');
});

test('rejeita título vazio', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  assert.throws(() => repo.criar({ titulo: '   ' }), ErroDeValidacao);
  assert.throws(() => repo.criar({}), ErroDeValidacao);
});

test('rejeita título longo demais na fronteira', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  assert.ok(repo.criar({ titulo: 'a'.repeat(120) })); // limite exato: passa
  assert.throws(() => repo.criar({ titulo: 'a'.repeat(121) }), ErroDeValidacao);
});

test('rejeita prioridade desconhecida', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  assert.throws(
    () => repo.criar({ titulo: 'x', prioridade: 'urgentíssima' }),
    ErroDeValidacao,
  );
});

test('lista ordenando por prioridade e depois por id', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  repo.criar({ titulo: 'b', prioridade: 'baixa' });
  repo.criar({ titulo: 'a', prioridade: 'alta' });
  repo.criar({ titulo: 'm', prioridade: 'media' });
  repo.criar({ titulo: 'a2', prioridade: 'alta' });
  assert.deepEqual(
    repo.listar().map((t) => t.titulo),
    ['a', 'a2', 'm', 'b'],
  );
});

test('filtra por concluída e por prioridade', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  const t = repo.criar({ titulo: 'feita', prioridade: 'alta' });
  repo.criar({ titulo: 'pendente', prioridade: 'baixa' });
  repo.concluir(t.id);
  assert.equal(repo.listar({ concluida: true }).length, 1);
  assert.equal(repo.listar({ concluida: false }).length, 1);
  assert.equal(repo.listar({ prioridade: 'alta' }).length, 1);
});

test('concluir é idempotente e carimba a data uma vez só', () => {
  let instante = new Date('2026-08-13T12:00:00.000Z');
  const repo = new RepositorioDeTarefas(() => instante);
  const t = repo.criar({ titulo: 'x' });
  const primeira = repo.concluir(t.id);
  instante = new Date('2026-08-13T18:00:00.000Z');
  const segunda = repo.concluir(t.id);
  assert.equal(primeira.concluidaEm, '2026-08-13T12:00:00.000Z');
  assert.equal(segunda.concluidaEm, primeira.concluidaEm);
});

test('obter, concluir e remover inexistente dão NaoEncontrado', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  assert.throws(() => repo.obter(99), NaoEncontrado);
  assert.throws(() => repo.concluir(99), NaoEncontrado);
  assert.throws(() => repo.remover(99), NaoEncontrado);
});

test('listar devolve cópias — mutar o resultado não corrompe o repositório', () => {
  const repo = new RepositorioDeTarefas(RELOGIO);
  repo.criar({ titulo: 'original' });
  const copia = repo.listar();
  copia[0].titulo = 'adulterado';
  assert.equal(repo.obter(1).titulo, 'original');
});
