/**
 * Teste de contrato — espelho de `tests/test_contrato_repositorio.py`.
 *
 * A mesma bateria roda contra o fake em memória e contra o SQLite real. É o que
 * impede o fake de mentir. No pytest isso sai de graça com
 * `@pytest.fixture(params=[...])`; aqui a "parametrização" é um laço sobre as
 * implementações, e cada uma vira um `describe`.
 */

import assert from 'node:assert/strict';
import { afterEach, beforeEach, describe, it } from 'node:test';

import { Assinatura, Estado } from '../src/assinatura.js';
import { CATALOGO } from '../src/plano.js';
import { RepositorioMemoria, RepositorioSQLite } from '../src/repositorio.js';

const HOJE = '2026-08-12';

const IMPLEMENTACOES = [
  { nome: 'RepositorioMemoria', criar: () => new RepositorioMemoria(), fechar: () => {} },
  {
    nome: 'RepositorioSQLite',
    criar: () => new RepositorioSQLite(':memory:'),
    fechar: (r) => r.fechar(),
  },
];

function nova(id, { dias = 0, estado = Estado.ATIVA } = {}) {
  const a = Assinatura.criar(id, `${id}@ex.br`, CATALOGO.pro, HOJE);
  a.proximaCobranca = dias === 0 ? HOJE : new Date(Date.UTC(2026, 7, 12 + dias)).toISOString().slice(0, 10);
  a.estado = estado;
  return a;
}

for (const impl of IMPLEMENTACOES) {
  describe(`contrato: ${impl.nome}`, () => {
    let repo;

    beforeEach(() => {
      repo = impl.criar();
    });

    afterEach(() => {
      impl.fechar(repo);
    });

    it('buscar devolve null para id desconhecido', () => {
      assert.equal(repo.buscar('fantasma'), null);
    });

    it('salvar e buscar preserva os campos', () => {
      const original = nova('a1');
      original.tentativasFalhas = 2;
      original.ciclosPagos = 7;
      repo.salvar(original);

      const lida = repo.buscar('a1');

      assert.equal(lida.id, 'a1');
      assert.equal(lida.cliente, 'a1@ex.br');
      assert.equal(lida.plano.codigo, 'pro');
      assert.equal(lida.estado, Estado.ATIVA);
      assert.equal(lida.tentativasFalhas, 2);
      assert.equal(lida.ciclosPagos, 7);
      assert.equal(lida.inicio, original.inicio);
      assert.equal(lida.proximaCobranca, original.proximaCobranca);
    });

    it('salvar duas vezes o mesmo id não duplica', () => {
      repo.salvar(nova('a1'));
      repo.salvar(nova('a1'));
      assert.equal(repo.listarVencidas(HOJE).length, 1);
    });

    it('vencidas incluem o próprio dia', () => {
      repo.salvar(nova('a1', { dias: 0 }));
      assert.deepEqual(
        repo.listarVencidas(HOJE).map((a) => a.id),
        ['a1'],
      );
    });

    it('vencidas excluem o futuro', () => {
      repo.salvar(nova('a1', { dias: 1 }));
      assert.deepEqual(repo.listarVencidas(HOJE), []);
    });

    for (const estado of [Estado.PAUSADA, Estado.CANCELADA]) {
      it(`vencidas excluem ${estado}`, () => {
        repo.salvar(nova('a1', { dias: -10, estado }));
        assert.deepEqual(repo.listarVencidas(HOJE), []);
      });
    }

    it('vencidas incluem inadimplente', () => {
      repo.salvar(nova('a1', { dias: -10, estado: Estado.INADIMPLENTE }));
      assert.equal(repo.listarVencidas(HOJE).length, 1);
    });

    it('vencidas vêm ordenadas por id', () => {
      for (const id of ['c', 'a', 'b']) repo.salvar(nova(id));
      assert.deepEqual(
        repo.listarVencidas(HOJE).map((a) => a.id),
        ['a', 'b', 'c'],
      );
    });

    it('repositório vazio devolve array vazio, não null', () => {
      assert.deepEqual(repo.listarVencidas(HOJE), []);
    });

    it('a assinatura lida é uma instância de Assinatura, com métodos', () => {
      // Sem este teste, `RepositorioSQLite` poderia devolver um objeto literal
      // e todo `.estaVencida()` do serviço quebraria só em produção.
      repo.salvar(nova('a1'));
      const lida = repo.buscar('a1');
      assert.ok(lida instanceof Assinatura);
      assert.equal(typeof lida.estaVencida, 'function');
      assert.equal(lida.estaVencida(HOJE), true);
    });
  });
}

describe('divergência conhecida entre as implementações', () => {
  it('o fake guarda referências; o SQLite guarda cópias', () => {
    // Esta é a diferença que o contrato NÃO cobre, e ela é real. Documentar
    // com um teste é melhor do que documentar com um comentário: se um dia o
    // fake passar a copiar, o teste falha e alguém decide conscientemente.
    const memoria = new RepositorioMemoria();
    const a = nova('a1');
    memoria.salvar(a);
    a.ciclosPagos = 99; // mutação FORA do repositório
    assert.equal(memoria.buscar('a1').ciclosPagos, 99, 'fake enxerga a mutação');

    const sqlite = new RepositorioSQLite(':memory:');
    try {
      const b = nova('a1');
      sqlite.salvar(b);
      b.ciclosPagos = 99;
      assert.equal(sqlite.buscar('a1').ciclosPagos, 0, 'SQLite não enxerga: precisa de salvar()');
    } finally {
      sqlite.fechar();
    }
  });
});
