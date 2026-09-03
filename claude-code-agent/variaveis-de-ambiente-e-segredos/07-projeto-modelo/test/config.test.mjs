import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { criarConfig, configParaLog, mascarar, SEGREDO_DE_EXEMPLO } from '../src/config.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');

/** Ambiente mínimo válido, usado como base nos testes. */
const base = () => ({
  DATABASE_URL: 'postgres://app:senha@localhost:5432/recados',
  SESSION_SECRET: 'a'.repeat(32),
  API_KEY: 'sk_test_abcdefghij',
});

describe('criarConfig — obrigatórias', () => {
  test('ambiente vazio reporta TODAS as faltas de uma vez, não só a primeira', () => {
    const { problemas } = criarConfig({});
    assert.ok(problemas.includes('falta DATABASE_URL'));
    assert.ok(problemas.includes('falta SESSION_SECRET'));
    assert.ok(problemas.includes('falta API_KEY'));
    assert.equal(problemas.length, 3);
  });

  test('string vazia conta como ausente', () => {
    const { problemas } = criarConfig({ ...base(), API_KEY: '' });
    assert.ok(problemas.includes('falta API_KEY'));
  });

  test('ambiente mínimo válido não gera problema', () => {
    const { problemas } = criarConfig(base());
    assert.deepEqual([...problemas], []);
  });
});

describe('criarConfig — tipos e padrões', () => {
  test('PORT vira número, não string', () => {
    const { config } = criarConfig({ ...base(), PORT: '8080' });
    assert.equal(config.porta, 8080);
    assert.equal(typeof config.porta, 'number');
  });

  test('padrões são aplicados quando a variável não existe', () => {
    const { config } = criarConfig(base());
    assert.equal(config.porta, 3000);
    assert.equal(config.logLevel, 'info');
    assert.equal(config.ambiente, 'development');
    assert.equal(config.maxRecados, 100);
    assert.equal(config.exporMetricas, false);
  });

  test('booleano: a string "false" vira false (e não true, como faria Boolean())', () => {
    const { config } = criarConfig({ ...base(), EXPOR_METRICAS: 'false' });
    assert.equal(config.exporMetricas, false);
    assert.equal(Boolean('false'), true); // o erro clássico que estamos evitando
  });

  test('valor inválido é reportado e o padrão é mantido', () => {
    const { config, problemas } = criarConfig({ ...base(), PORT: '99999' });
    assert.ok(problemas.some((p) => p.startsWith('PORT:')));
    assert.equal(config.porta, 3000);
  });

  test('LOG_LEVEL fora da lista é recusado', () => {
    const { problemas } = criarConfig({ ...base(), LOG_LEVEL: 'verboso' });
    assert.ok(problemas.some((p) => p.includes('esperado um de debug, info, warn, error')));
  });

  test('DATABASE_URL com esquema errado é recusada', () => {
    const { problemas } = criarConfig({ ...base(), DATABASE_URL: 'mysql://a:b@c/d' });
    assert.ok(problemas.some((p) => p.includes('esquema deve ser um de')));
  });

  test('SESSION_SECRET curto é recusado', () => {
    const { problemas } = criarConfig({ ...base(), SESSION_SECRET: 'curto' });
    assert.ok(problemas.some((p) => p.includes('ao menos 32 caracteres')));
  });
});

describe('criarConfig — padrão _FILE (Docker/Kubernetes)', () => {
  const dir = mkdtempSync(join(tmpdir(), 'cofre-'));

  test('lê o valor do arquivo apontado por NOME_FILE', () => {
    const arquivo = join(dir, 'api_key');
    writeFileSync(arquivo, 'sk_live_do_arquivo\n'); // com quebra de linha de propósito
    const env = { ...base() };
    delete env.API_KEY;
    const { config, problemas } = criarConfig({ ...env, API_KEY_FILE: arquivo });
    assert.deepEqual([...problemas], []);
    assert.equal(config.apiKey, 'sk_live_do_arquivo'); // trim aplicado
  });

  test('NOME_FILE tem precedência sobre NOME', () => {
    const arquivo = join(dir, 'api_key2');
    writeFileSync(arquivo, 'do-arquivo-abcdefgh');
    const { config } = criarConfig({ ...base(), API_KEY: 'da-variavel', API_KEY_FILE: arquivo });
    assert.equal(config.apiKey, 'do-arquivo-abcdefgh');
  });

  test('arquivo inexistente vira problema legível, não exceção', () => {
    const { problemas } = criarConfig({ ...base(), API_KEY_FILE: '/nao/existe/mesmo' });
    assert.ok(problemas.some((p) => p.includes('não pôde ser lido') && p.includes('ENOENT')));
  });
});

describe('criarConfig — regras cruzadas de produção', () => {
  test('segredo de exemplo é recusado em produção', () => {
    const { problemas } = criarConfig({
      ...base(),
      NODE_ENV: 'production',
      SESSION_SECRET: SEGREDO_DE_EXEMPLO,
    });
    assert.ok(problemas.some((p) => p.includes('valor de exemplo')));
  });

  test('chave de teste é recusada em produção', () => {
    const { problemas } = criarConfig({ ...base(), NODE_ENV: 'production' });
    assert.ok(problemas.some((p) => p.includes('chave de teste')));
  });

  test('o mesmo ambiente passa em development', () => {
    const { problemas } = criarConfig({ ...base(), NODE_ENV: 'development' });
    assert.deepEqual([...problemas], []);
  });

  test('banco em memória é recusado em produção', () => {
    const { problemas } = criarConfig({
      ...base(),
      NODE_ENV: 'production',
      API_KEY: 'sk_live_abcdefghij',
      DATABASE_URL: 'memory://local',
      SESSION_SECRET: 'b'.repeat(40),
    });
    assert.ok(problemas.some((p) => p.includes('memória')));
  });
});

describe('mascaramento', () => {
  test('segredo curto vira asteriscos, sem revelar o tamanho exato', () => {
    assert.equal(mascarar('12345678'), '********');
  });

  test('segredo longo mostra pontas e tamanho — suficiente para conferir, insuficiente para usar', () => {
    assert.equal(mascarar('sk_live_abcdefghij'), 'sk_…ij (18 chars)');
  });

  test('configParaLog não deixa nenhum segredo passar inteiro', () => {
    const { config } = criarConfig(base());
    const visao = configParaLog(config);
    const texto = JSON.stringify(visao);
    assert.ok(!texto.includes(config.sessionSecret));
    assert.ok(!texto.includes(config.apiKey));
    assert.ok(!texto.includes('senha')); // a senha dentro da DATABASE_URL
  });
});

describe('o contrato com o .env.example', () => {
  // Este teste é o antídoto para o erro nº 1 de equipe: alguém adiciona uma
  // variável no código e esquece de documentá-la, e o deploy no cliente quebra.
  test('toda variável exigida pelo código aparece no .env.example', () => {
    const exemplo = readFileSync(join(RAIZ, '.env.example'), 'utf8');
    const nomesNoExemplo = new Set(
      exemplo
        .split('\n')
        .map((l) => l.match(/^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=/)?.[1])
        .filter(Boolean),
    );
    const fonte = readFileSync(join(RAIZ, 'src/config.mjs'), 'utf8');
    const nomesNoCodigo = new Set(
      [...fonte.matchAll(/(?:exigido|opcional)\('([A-Z][A-Z0-9_]*)'/g)].map((m) => m[1]),
    );
    const faltando = [...nomesNoCodigo].filter((n) => !nomesNoExemplo.has(n));
    assert.deepEqual(faltando, [], `variáveis ausentes do .env.example: ${faltando.join(', ')}`);
  });

  test('o .env.example não contém nenhum valor que pareça segredo de verdade', () => {
    const exemplo = readFileSync(join(RAIZ, '.env.example'), 'utf8');
    const suspeitos = [/sk_live_/, /AKIA[0-9A-Z]{16}/, /-----BEGIN [A-Z ]*PRIVATE KEY-----/];
    for (const padrao of suspeitos) {
      assert.ok(!padrao.test(exemplo), `.env.example casa com ${padrao}`);
    }
  });
});
