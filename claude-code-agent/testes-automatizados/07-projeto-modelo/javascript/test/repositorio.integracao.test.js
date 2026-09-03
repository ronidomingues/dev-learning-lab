/**
 * Teste de **integração** com SQLite real — espelho de `test_repositorio_sqlite.py`.
 *
 * O `node:test` não tem marcadores como o `-m integracao` do pytest. As duas
 * saídas usadas na prática:
 *   1. convenção de nome de arquivo + `--test-name-pattern` / glob
 *      (`node --test test/*.integracao.test.js`), que é o que este projeto usa;
 *   2. `--test-skip-pattern` para excluir no laço rápido.
 * Desde o Node 22.9 existe também `test('nome', { skip: cond })` por teste.
 */

import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { after, before, beforeEach, describe, it } from 'node:test';

import { Assinatura, Estado } from '../src/assinatura.js';
import { GatewayFalso } from '../src/gateway.js';
import { CATALOGO } from '../src/plano.js';
import { RelogioFixo } from '../src/relogio.js';
import { RepositorioSQLite } from '../src/repositorio.js';
import { NotificadorEspiao, ServicoRenovacao } from '../src/servico.js';
import { somarDias } from '../src/data.js';

const HOJE = '2026-08-12';

function nova(id, { dias = 30, estado = Estado.ATIVA } = {}) {
  const a = Assinatura.criar(id, `${id}@ex.br`, CATALOGO.pro, HOJE);
  a.proximaCobranca = somarDias(HOJE, dias);
  a.estado = estado;
  return a;
}

describe('persistência em SQLite', () => {
  let repo;

  beforeEach(() => {
    // Banco novo a cada teste. Isolamento total: nenhum teste vê o lixo do outro.
    // Custo: microssegundos, porque `:memory:` não toca o disco.
    repo?.fechar?.();
    repo = new RepositorioSQLite(':memory:');
  });

  after(() => repo?.fechar?.());

  it('salva e recupera', () => {
    repo.salvar(nova('a1'));
    assert.equal(repo.buscar('a1').cliente, 'a1@ex.br');
  });

  it('id inexistente devolve null', () => {
    assert.equal(repo.buscar('nao-existe'), null);
  });

  it('salvar duas vezes atualiza em vez de duplicar (ON CONFLICT DO UPDATE)', () => {
    const a = nova('a1');
    repo.salvar(a);
    a.registrarPagamento(HOJE);
    repo.salvar(a);
    assert.equal(repo.buscar('a1').ciclosPagos, 1);
  });

  it('a data faz ida e volta sem perder o dia', () => {
    // SQLite não tem tipo DATE — guardamos TEXT ISO-8601.
    const a = nova('a1');
    a.proximaCobranca = '2026-02-28';
    repo.salvar(a);
    assert.equal(repo.buscar('a1').proximaCobranca, '2026-02-28');
  });

  it('inteiros voltam como number, não como string', () => {
    // `node:sqlite` devolve INTEGER como number (ou BigInt, se configurado).
    // Sem este teste, `tentativasFalhas + 1` poderia virar concatenação.
    const a = nova('a1');
    a.tentativasFalhas = 2;
    repo.salvar(a);
    const lida = repo.buscar('a1');
    assert.equal(typeof lida.tentativasFalhas, 'number');
    assert.equal(lida.tentativasFalhas + 1, 3);
  });
});

describe('persistência em arquivo', () => {
  let pasta;

  before(() => {
    pasta = mkdtempSync(join(tmpdir(), 'assinaturas-'));
  });

  after(() => {
    rmSync(pasta, { recursive: true, force: true });
  });

  it('dados sobrevivem a reconexão', () => {
    const caminho = join(pasta, 'sobrevive.db');
    const primeiro = new RepositorioSQLite(caminho);
    primeiro.salvar(nova('a1'));
    primeiro.fechar();

    const segundo = new RepositorioSQLite(caminho);
    try {
      assert.ok(segundo.buscar('a1'));
    } finally {
      segundo.fechar();
    }
  });

  it('o esquema é idempotente: abrir duas vezes não explode', () => {
    const caminho = join(pasta, 'idempotente.db');
    for (let i = 0; i < 3; i += 1) {
      const r = new RepositorioSQLite(caminho);
      r.fechar();
    }
  });

  it('`using` fecha o banco ao sair do bloco (Symbol.dispose)', () => {
    // `using` é o equivalente ao `with` do Python, disponível no Node 24.
    // Antes dele, esquecer o `fechar()` num teste vazava descritor de arquivo,
    // e a suíte quebrava com EMFILE lá pelo teste número 1.024.
    const caminho = join(pasta, 'using.db');
    {
      using repo = new RepositorioSQLite(caminho);
      repo.salvar(nova('a1'));
    } // ← fechado aqui, automaticamente

    // Prova de que fechou: reabrir e ler funciona, e o objeto anterior sumiu
    // do escopo sem deixar conexão pendurada.
    using outro = new RepositorioSQLite(caminho);
    assert.ok(outro.buscar('a1'));
  });
});

describe('consulta de vencidas', () => {
  let repo;

  beforeEach(() => {
    repo?.fechar?.();
    repo = new RepositorioSQLite(':memory:');
  });

  after(() => repo?.fechar?.());

  it('traz a que vence hoje e ignora a de amanhã', () => {
    repo.salvar(nova('hoje', { dias: 0 }));
    repo.salvar(nova('amanha', { dias: 1 }));
    assert.deepEqual(
      repo.listarVencidas(HOJE).map((a) => a.id),
      ['hoje'],
    );
  });

  it('traz as atrasadas', () => {
    repo.salvar(nova('atrasada', { dias: -30 }));
    assert.equal(repo.listarVencidas(HOJE).length, 1);
  });

  it('a comparação de data como TEXT funciona por ser ISO-8601', () => {
    // Cinco porquês, último nível: ordem lexicográfica == ordem cronológica
    // porque os campos têm largura fixa e vêm do mais significativo ao menos.
    // Com "DD/MM/AAAA" a consulta traria lixo. O teste trava o formato.
    repo.salvar(nova('ano_passado', { dias: -300 }));
    assert.deepEqual(
      repo.listarVencidas('2026-01-01').map((a) => a.id),
      ['ano_passado'],
    );
  });
});

describe('serviço integrado ao banco real', () => {
  it('ciclo completo de cobrança com SQLite', async () => {
    const repo = new RepositorioSQLite(':memory:');
    try {
      repo.salvar(nova('a1', { dias: 0 }));
      repo.salvar(nova('a2', { dias: 5 }));

      const servico = new ServicoRenovacao(
        repo,
        new GatewayFalso(),
        new RelogioFixo(HOJE),
        new NotificadorEspiao(),
      );
      const relatorio = await servico.renovarVencidas();

      assert.equal(relatorio.cobradas, 1);
      assert.equal(repo.buscar('a1').proximaCobranca, '2026-09-11');
      assert.equal(repo.buscar('a2').ciclosPagos, 0);
    } finally {
      repo.fechar();
    }
  });
});
