/**
 * processo.test.mjs — testes que só fazem sentido em PROCESSO DE VERDADE.
 *
 * Os outros testes exercitam a função pura. Estes provam as afirmações do curso
 * sobre o comportamento do sistema operacional e do runtime:
 *   • a aplicação sobe SEM nenhum .env, recebendo tudo pelo ambiente;
 *   • variável de ambiente vence o .env;
 *   • configuração inválida encerra com o código 78;
 *   • a variável não persiste depois do processo.
 */
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const CHECK = join(RAIZ, 'src/check-config.mjs');

/** Roda o verificador de configuração num processo limpo. */
function rodar(env, args = []) {
  return spawnSync(process.execPath, [...args, CHECK], {
    env: { PATH: process.env.PATH, ...env }, // ambiente ENXUTO: nada da máquina vaza
    encoding: 'utf8',
    cwd: RAIZ,
  });
}

const valido = {
  DATABASE_URL: 'postgres://app:senha@localhost:5432/recados',
  SESSION_SECRET: 'q'.repeat(32),
  API_KEY: 'sk_test_abcdefghij',
};

describe('o processo real', () => {
  test('sobe SEM .env, só com o ambiente — o teste decisivo do curso', () => {
    const r = rodar(valido);
    assert.equal(r.status, 0, r.stderr);
    assert.match(r.stdout, /Configuração válida/);
  });

  test('configuração inválida encerra com 78 (EX_CONFIG), não com 1', () => {
    const r = rodar({});
    assert.equal(r.status, 78);
    assert.match(r.stderr, /falta DATABASE_URL/);
    assert.match(r.stderr, /falta SESSION_SECRET/);
  });

  test('a saída de diagnóstico nunca imprime segredo inteiro', () => {
    const r = rodar(valido);
    assert.ok(!r.stdout.includes(valido.SESSION_SECRET));
    assert.ok(!r.stdout.includes(valido.API_KEY));
    assert.ok(!r.stdout.includes('senha@'), 'a senha da DATABASE_URL apareceu');
    assert.match(r.stdout, /localhost:5432/); // e continua útil
  });

  test('variável de ambiente VENCE o .env — por isso o .env não vai para produção', () => {
    const dir = mkdtempSync(join(tmpdir(), 'cofre-env-'));
    const arquivo = join(dir, '.env');
    writeFileSync(
      arquivo,
      [
        'DATABASE_URL=postgres://vindo:do@arquivo:5432/env',
        `SESSION_SECRET=${'f'.repeat(32)}`,
        'API_KEY=sk_test_do_arquivo',
        'PORT=1111',
      ].join('\n') + '\n',
    );

    // (a) só o .env → os valores do arquivo valem
    const so = rodar({}, [`--env-file=${arquivo}`]);
    assert.equal(so.status, 0, so.stderr);
    assert.match(so.stdout, /porta\s+1111/);

    // (b) .env + ambiente → o AMBIENTE vence
    const ambos = rodar({ ...valido, PORT: '9999' }, [`--env-file=${arquivo}`]);
    assert.equal(ambos.status, 0, ambos.stderr);
    assert.match(ambos.stdout, /porta\s+9999/);
    assert.doesNotMatch(ambos.stdout, /1111/);
  });

  test('--env-file-if-exists não falha quando o arquivo não existe', () => {
    const r = rodar(valido, ['--env-file-if-exists=/nao/existe/.env']);
    assert.equal(r.status, 0, r.stderr);
  });

  test('a variável não sobrevive ao processo', () => {
    const a = spawnSync(process.execPath, ['-e', 'process.stdout.write(String(process.env.EFEMERA))'], {
      env: { ...process.env, EFEMERA: 'existo' },
      encoding: 'utf8',
    });
    assert.equal(a.stdout, 'existo');

    const b = spawnSync(process.execPath, ['-e', 'process.stdout.write(String(process.env.EFEMERA))'], {
      env: { ...process.env },
      encoding: 'utf8',
    });
    assert.equal(b.stdout, 'undefined');
  });

  test('o padrão _FILE funciona ponta a ponta, em processo real', () => {
    const dir = mkdtempSync(join(tmpdir(), 'cofre-file-'));
    const arquivo = join(dir, 'api_key');
    writeFileSync(arquivo, 'sk_test_montado_como_arquivo\n');
    const env = { ...valido };
    delete env.API_KEY;
    const r = rodar({ ...env, API_KEY_FILE: arquivo });
    assert.equal(r.status, 0, r.stderr);
    assert.ok(!r.stdout.includes('sk_test_montado_como_arquivo'));
    assert.match(r.stdout, /sk_…/);
  });
});
