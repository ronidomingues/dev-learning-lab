/**
 * A parte da CLI que toca o disco. Separada por convenção de nome de arquivo,
 * para o laço rápido (`npm run test:unit`) não pagar por ela.
 */

import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { after, before, describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

import { main } from '../src/cli.js';

const executar = promisify(execFile);
const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));

async function rodar(argv) {
  const linhas = [];
  const codigo = await main(argv, { imprimir: (t) => linhas.push(String(t)) });
  return { codigo, saida: linhas.join('\n') };
}

describe('comando renovar', () => {
  let pasta;

  before(() => {
    pasta = mkdtempSync(join(tmpdir(), 'assinaturas-cli-'));
  });

  after(() => {
    rmSync(pasta, { recursive: true, force: true });
  });

  it('cria o banco e não explode com base vazia', async () => {
    const banco = join(pasta, 'vazio.db');
    const { codigo, saida } = await rodar(['renovar', '--banco', banco, '--data', '2026-08-12']);
    assert.equal(codigo, 0);
    assert.match(saida, /0 cobradas/);
  });

  it('recusa data mal formada, em vez de cobrar o dia errado', async () => {
    const banco = join(pasta, 'outro.db');
    await assert.rejects(() => rodar(['renovar', '--banco', banco, '--data', '12/08/2026']), {
      name: 'DataInvalida',
    });
  });

  it('fecha o banco mesmo quando a renovação falha (finally)', async () => {
    // Sem o `finally` no cli.js, o arquivo ficaria aberto e no Windows nem
    // daria para apagar a pasta temporária. Este teste prova que o recurso
    // é liberado no caminho triste, não só no feliz.
    const banco = join(pasta, 'fecha.db');
    await assert.rejects(() => rodar(['renovar', '--banco', banco, '--data', 'ontem']));
    rmSync(banco, { force: true }); // se estivesse aberto, no Windows falharia
  });
});

describe('a CLI de verdade, como um usuário a executaria', () => {
  // Teste de ponta a ponta do binário: dispara `node src/cli.js demo` num
  // processo separado. É o único teste que verifica que o programa é
  // executável, que o shebang e o `import.meta.main` funcionam, e que nada
  // escreve em stderr. Lento (~80 ms) — por isso existe UM só.
  it('roda como processo e imprime o relatório em stdout', async () => {
    const { stdout, stderr } = await executar(process.execPath, [join(RAIZ, 'src/cli.js'), 'demo']);
    assert.equal(stderr, '');
    assert.match(stdout, /1 cobradas \(R\$ 49,90\), 1 recusadas/);
    assert.match(stdout, /a3 carla@exemplo\.br/);
  });

  it('sai com código 2 quando o comando é desconhecido', async () => {
    await assert.rejects(
      () => executar(process.execPath, [join(RAIZ, 'src/cli.js'), 'voar']),
      (erro) => {
        assert.equal(erro.code, 2);
        assert.match(erro.stdout, /^uso: /);
        return true;
      },
    );
  });
});
