// Testes do repositório, com o test runner embutido do Node (node:test) — sem jest, sem vitest.
// Rode com:  npm test     (ou)  docker compose --profile testes run --rm testes

import { test, describe, beforeEach, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { Repositorio, ErroValidacao } from '../src/repositorio.js';

let pastaTemp;
let repo;

async function novoRepo(opcoes = {}) {
  pastaTemp = await mkdtemp(join(tmpdir(), 'mural-'));
  const r = new Repositorio({ caminho: join(pastaTemp, 'recados.json'), ...opcoes });
  await r.iniciar();
  return r;
}

describe('Repositorio', () => {
  beforeEach(async () => {
    repo = await novoRepo();
  });

  after(async () => {
    if (pastaTemp) await rm(pastaTemp, { recursive: true, force: true });
  });

  test('começa vazio quando o arquivo não existe', () => {
    assert.equal(repo.total(), 0);
    assert.deepEqual(repo.listar(), []);
  });

  test('adiciona um recado e devolve id e timestamp', async () => {
    const r = await repo.adicionar({ autor: 'Ana', texto: 'Olá' });
    assert.match(r.id, /^[0-9a-f-]{36}$/);
    assert.equal(r.autor, 'Ana');
    assert.ok(Date.parse(r.criadoEm));
    assert.equal(repo.total(), 1);
  });

  test('remove espaços em branco nas pontas', async () => {
    const r = await repo.adicionar({ autor: '  Ana  ', texto: '  Olá  ' });
    assert.equal(r.autor, 'Ana');
    assert.equal(r.texto, 'Olá');
  });

  test('rejeita autor vazio', async () => {
    await assert.rejects(() => repo.adicionar({ autor: '   ', texto: 'x' }), ErroValidacao);
  });

  test('rejeita texto acima do limite', async () => {
    const curto = await novoRepo({ tamanhoMaxTexto: 5 });
    await assert.rejects(() => curto.adicionar({ autor: 'A', texto: '123456' }), ErroValidacao);
  });

  test('rejeita corpo sem os campos esperados', async () => {
    await assert.rejects(() => repo.adicionar({}), ErroValidacao);
    await assert.rejects(() => repo.adicionar({ autor: 'A' }), ErroValidacao);
  });

  test('lista do mais novo para o mais antigo', async () => {
    await repo.adicionar({ autor: 'A', texto: 'primeiro' });
    await repo.adicionar({ autor: 'B', texto: 'segundo' });
    const lista = repo.listar();
    assert.equal(lista[0].texto, 'segundo');
    assert.equal(lista[1].texto, 'primeiro');
  });

  test('respeita o limite máximo, descartando os mais antigos', async () => {
    const limitado = await novoRepo({ limite: 3 });
    for (const t of ['1', '2', '3', '4', '5']) {
      await limitado.adicionar({ autor: 'A', texto: t });
    }
    assert.equal(limitado.total(), 3);
    assert.deepEqual(
      limitado.listar().map((r) => r.texto),
      ['5', '4', '3'],
    );
  });

  test('remove por id e devolve false para id inexistente', async () => {
    const r = await repo.adicionar({ autor: 'A', texto: 'x' });
    assert.equal(await repo.remover(r.id), true);
    assert.equal(repo.total(), 0);
    assert.equal(await repo.remover('nao-existe'), false);
  });

  test('persiste no disco e é relido por uma instância nova', async () => {
    await repo.adicionar({ autor: 'Ana', texto: 'persistido' });

    const outro = new Repositorio({ caminho: join(pastaTemp, 'recados.json') });
    await outro.iniciar();

    assert.equal(outro.total(), 1);
    assert.equal(outro.listar()[0].texto, 'persistido');
  });

  test('escritas concorrentes não se perdem (a fila serializa)', async () => {
    // Sem a fila em Repositorio#enfileirar, este teste falha: as gravações se sobrescrevem.
    await Promise.all(
      Array.from({ length: 20 }, (_, i) => repo.adicionar({ autor: 'A', texto: `n${i}` })),
    );
    assert.equal(repo.total(), 20);

    const noDisco = JSON.parse(await readFile(join(pastaTemp, 'recados.json'), 'utf8'));
    assert.equal(noDisco.length, 20);
  });

  test('arquivo corrompido falha alto em vez de fingir estar vazio', async () => {
    const { writeFile } = await import('node:fs/promises');
    const caminho = join(pastaTemp, 'quebrado.json');
    await writeFile(caminho, '{ isto não é json', 'utf8');

    const quebrado = new Repositorio({ caminho });
    await assert.rejects(() => quebrado.iniciar(), /ilegível/);
  });
});
