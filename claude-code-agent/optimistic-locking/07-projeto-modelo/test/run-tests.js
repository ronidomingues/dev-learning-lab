// Suíte com o runner nativo (`node:test`). Zero dependências.
// Rode com: npm test

import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';

import { abrirBanco, semear } from '../src/db.js';
import {
  buscar,
  atualizar,
  baixarEstoque,
  atualizarInseguro,
  ConflitoDeVersao,
  NaoEncontrado,
  EstoqueInsuficiente,
} from '../src/repo.js';
import { comRetentativa } from '../src/retry.js';
import { criarServidor, versaoDoIfMatch, etagDe } from '../src/server.js';
import { criarCliente } from '../src/cliente.js';

const bancoNovo = () => {
  const db = abrirBanco(':memory:');
  semear(db);
  return db;
};

// ---------------------------------------------------------------------------
describe('repositório · guarda de versão', () => {
  test('atualização com a versão certa incrementa a versão em 1', () => {
    const db = bancoNovo();
    const antes = buscar(db, 1);
    const depois = atualizar(db, 1, antes.version, { nome: 'Teclado novo' }, 'ana');
    assert.equal(depois.version, antes.version + 1);
    assert.equal(depois.nome, 'Teclado novo');
  });

  test('atualização com versão velha lança ConflitoDeVersao e não escreve nada', () => {
    const db = bancoNovo();
    atualizar(db, 1, 1, { nome: 'A' }, 'ana'); // versão vai a 2
    assert.throws(() => atualizar(db, 1, 1, { nome: 'B' }, 'bob'), ConflitoDeVersao);
    assert.equal(buscar(db, 1).nome, 'A', 'a escrita de bob não pode ter passado');
    assert.equal(buscar(db, 1).version, 2, 'versão não pode ter avançado no conflito');
  });

  test('o erro de conflito carrega o estado atual, para permitir merge', () => {
    const db = bancoNovo();
    atualizar(db, 1, 1, { nome: 'A' }, 'ana');
    try {
      atualizar(db, 1, 1, { nome: 'B' }, 'bob');
      assert.fail('deveria ter lançado');
    } catch (e) {
      assert.equal(e.versaoEsperada, 1);
      assert.equal(e.versaoAtual, 2);
      assert.equal(e.registroAtual.nome, 'A');
    }
  });

  test('a transação é atômica: conflito não deixa linha na auditoria', () => {
    const db = bancoNovo();
    atualizar(db, 1, 1, { nome: 'A' }, 'ana');
    assert.throws(() => atualizar(db, 1, 1, { nome: 'B' }, 'bob'));
    const trilha = db.prepare('SELECT COUNT(*) n FROM auditoria WHERE produto_id = 1').get();
    assert.equal(trilha.n, 1, 'só a escrita vencedora pode estar auditada');
  });

  test('registro inexistente lança NaoEncontrado, não ConflitoDeVersao', () => {
    const db = bancoNovo();
    assert.throws(() => atualizar(db, 999, 1, { nome: 'X' }), NaoEncontrado);
  });

  test('a atualização insegura demonstra o lost update', () => {
    const db = bancoNovo();
    // Dois leitores leem a versão 1.
    const ana = buscar(db, 1);
    const bob = buscar(db, 1);
    atualizarInseguro(db, 1, { descricao: ana.descricao + ' [ana]' });
    atualizarInseguro(db, 1, { descricao: bob.descricao + ' [bob]' });
    const fim = buscar(db, 1);
    assert.ok(fim.descricao.includes('[bob]'));
    assert.ok(!fim.descricao.includes('[ana]'), 'a edição de ana foi perdida — é esse o bug');
  });
});

// ---------------------------------------------------------------------------
describe('repositório · delta atômico (quando NÃO usar versão)', () => {
  test('baixas concorrentes somam corretamente sem gerar conflito', () => {
    const db = bancoNovo(); // produto 1 tem 10 unidades
    for (let i = 0; i < 7; i++) baixarEstoque(db, 1, 1);
    assert.equal(buscar(db, 1).estoque, 3);
  });

  test('a guarda de negócio impede estoque negativo', () => {
    const db = bancoNovo(); // produto 3 tem 2 unidades
    baixarEstoque(db, 3, 2);
    assert.throws(() => baixarEstoque(db, 3, 1), EstoqueInsuficiente);
    assert.equal(buscar(db, 3).estoque, 0);
  });
});

// ---------------------------------------------------------------------------
describe('retentativa', () => {
  test('converge quando a operação passa numa tentativa posterior', async () => {
    let n = 0;
    const r = await comRetentativa(
      () => {
        n++;
        if (n < 3) throw Object.assign(new Error('x'), { name: 'ConflitoDeVersao' });
        return 'ok';
      },
      { baseMs: 0, aleatorio: () => 0 }
    );
    assert.equal(r.valor, 'ok');
    assert.equal(r.tentativasGastas, 3);
  });

  test('não retenta erro que não é conflito', async () => {
    let n = 0;
    await assert.rejects(
      () =>
        comRetentativa(
          () => {
            n++;
            throw new TypeError('erro de programação');
          },
          { baseMs: 0, aleatorio: () => 0 }
        ),
      TypeError
    );
    assert.equal(n, 1, 'um TypeError não deve ser retentado — o bug não some sozinho');
  });

  test('desiste após o número máximo de tentativas', async () => {
    let n = 0;
    await assert.rejects(
      () =>
        comRetentativa(
          () => {
            n++;
            throw Object.assign(new Error('x'), { name: 'ConflitoDeVersao' });
          },
          { tentativas: 4, baseMs: 0, aleatorio: () => 0 }
        )
    );
    assert.equal(n, 4);
  });
});

// ---------------------------------------------------------------------------
describe('If-Match · interpretação', () => {
  test('ETag emitido é forte (sem W/), como o If-Match exige', () => {
    assert.equal(etagDe({ version: 7 }), '"7"');
  });
  test('formas aceitas e recusadas', () => {
    assert.deepEqual(versaoDoIfMatch('"3"'), { tipo: 'ok', versoes: [3] });
    assert.deepEqual(versaoDoIfMatch('"3", "4"'), { tipo: 'ok', versoes: [3, 4] });
    assert.equal(versaoDoIfMatch('*').tipo, 'curinga');
    assert.equal(versaoDoIfMatch('W/"3"').tipo, 'fraco');
    assert.equal(versaoDoIfMatch(undefined).tipo, 'ausente');
    assert.equal(versaoDoIfMatch('lixo').tipo, 'malformado');
  });
});

// ---------------------------------------------------------------------------
describe('HTTP ponta a ponta', () => {
  let servidor, base, cliente, db;

  before(async () => {
    db = bancoNovo();
    servidor = criarServidor(db);
    await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
    base = `http://127.0.0.1:${servidor.address().port}`;
    cliente = criarCliente(base);
  });

  after(() => servidor.close());

  test('GET devolve ETag igual à versão', async () => {
    const { produto, etag } = await cliente.obter(2);
    assert.equal(etag, `"${produto.version}"`);
  });

  test('PUT sem If-Match é recusado com 428', async () => {
    const r = await fetch(`${base}/produtos/2`, {
      method: 'PUT',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ nome: 'sem precondição' }),
    });
    assert.equal(r.status, 428);
  });

  test('PUT com ETag correto retorna 200 e ETag novo', async () => {
    const { etag } = await cliente.obter(2);
    const r = await cliente.salvar(2, etag, { nome: 'Monitor bom' }, 'ana');
    assert.equal(r.produto.nome, 'Monitor bom');
    assert.notEqual(r.etag, etag);
  });

  test('PUT com ETag velho retorna 412 com o estado atual', async () => {
    const { etag: velho } = await cliente.obter(2);
    await cliente.salvar(2, velho, { nome: 'primeiro' }, 'ana');
    const r = await fetch(`${base}/produtos/2`, {
      method: 'PUT',
      headers: { 'content-type': 'application/json', 'if-match': velho },
      body: JSON.stringify({ nome: 'segundo' }),
    });
    assert.equal(r.status, 412);
    const corpo = await r.json();
    assert.equal(corpo.erro, 'conflito_de_versao');
    assert.equal(corpo.atual.nome, 'primeiro');
    assert.equal(r.headers.get('etag'), `"${corpo.versao_atual}"`);
  });

  test('ETag fraco é recusado com 400', async () => {
    const r = await fetch(`${base}/produtos/2`, {
      method: 'PUT',
      headers: { 'content-type': 'application/json', 'if-match': 'W/"1"' },
      body: JSON.stringify({ nome: 'x' }),
    });
    assert.equal(r.status, 400);
  });

  test('CORRIDA REAL: 20 clientes concorrentes, nenhuma escrita perdida', async () => {
    const N = 20;
    const inicial = (await cliente.obter(3)).produto.descricao;

    const resultados = await Promise.all(
      Array.from({ length: N }, (_, i) =>
        cliente.editar(
          3,
          (p) => ({ descricao: `${p.descricao}|${i}` }),
          { autor: `cli${i}`, tentativas: 60, baseMs: 1, aleatorio: () => Math.random() }
        )
      )
    );

    const fim = (await cliente.obter(3)).produto;
    const marcas = fim.descricao.slice(inicial.length).split('|').filter(Boolean).map(Number).sort((a, b) => a - b);

    assert.deepEqual(marcas, Array.from({ length: N }, (_, i) => i),
      'todas as 20 edições precisam estar presentes');
    assert.equal(fim.version, 1 + N, 'a versão avança exatamente uma vez por escrita aceita');

    const trilha = await cliente.auditoria(3);
    assert.equal(trilha.length, N);

    const gastas = resultados.reduce((s, r) => s + r.tentativasGastas, 0);
    assert.ok(gastas > N, `houve conflito de verdade (tentativas: ${gastas} para ${N} escritas)`);
  });

  test('CORRIDA SEM PROTEÇÃO: quase tudo se perde', async () => {
    const N = 20;
    const inicial = (await cliente.obter(1)).produto.descricao;
    await Promise.all(
      Array.from({ length: N }, (_, i) =>
        cliente.editarSemProtecao(1, (p) => ({ descricao: `${p.descricao}|${i}` }))
      )
    );
    const fim = (await cliente.obter(1)).produto;
    const marcas = fim.descricao.slice(inicial.length).split('|').filter(Boolean);
    assert.ok(marcas.length < N, `sobraram ${marcas.length} de ${N} edições — as outras evaporaram`);
  });

  test('baixa de estoque concorrente não fica negativa', async () => {
    const antes = (await cliente.obter(2)).produto.estoque;
    const rs = await Promise.all(
      Array.from({ length: antes + 3 }, () => cliente.baixarEstoque(2, 1))
    );
    const ok = rs.filter((r) => r.status === 200).length;
    const recusadas = rs.filter((r) => r.status === 409).length;
    assert.equal(ok, antes);
    assert.equal(recusadas, 3);
    assert.equal((await cliente.obter(2)).produto.estoque, 0);
  });
});
