/**
 * O arquivo que justifica `src/data.js` existir.
 *
 * Cada teste aqui corresponde a um bug real que aparece em todo sistema
 * JavaScript que trata data de calendário com `Date` ingenuamente.
 */

import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { DataInvalida, comparar, data, diferencaEmDias, formatarBr, somarDias } from '../src/data.js';

describe('validação', () => {
  it('aceita ISO bem formada', () => {
    assert.equal(data('2026-08-12'), '2026-08-12');
  });

  const invalidas = [
    '12/08/2026',
    '2026-8-12',
    '2026/08/12',
    '20260812',
    '',
    'hoje',
    '2026-08-12T00:00:00Z',
  ];
  for (const ruim of invalidas) {
    it(`recusa formato: ${JSON.stringify(ruim)}`, () => {
      assert.throws(() => data(ruim), DataInvalida);
    });
  }

  it('recusa data inexistente no calendário', () => {
    // `new Date(Date.UTC(2026, 1, 30))` NÃO explode: vira 2 de março em
    // silêncio. Esse "conserto automático" é a razão de a validação existir.
    assert.throws(() => data('2026-02-30'), /inexistente no calendário/);
    assert.throws(() => data('2026-13-01'), DataInvalida);
    assert.throws(() => data('2026-00-10'), DataInvalida);
  });

  it('aceita 29 de fevereiro em ano bissexto e recusa em ano comum', () => {
    assert.equal(data('2028-02-29'), '2028-02-29');
    assert.throws(() => data('2026-02-29'), /inexistente no calendário/);
  });
});

describe('a armadilha do fuso horário', () => {
  it('demonstra por que não usamos new Date(iso).getDate()', () => {
    // Em fuso negativo (Brasil, UTC-3), `new Date('2026-08-12')` é meia-noite
    // UTC = 21h do dia 11 em São Paulo, e `getDate()` devolve 11.
    // Este teste roda em QUALQUER fuso: só afirma que a leitura em UTC está
    // correta, que é a única leitura estável.
    const d = new Date('2026-08-12');
    assert.equal(d.getUTCDate(), 12);

    // E a nossa função devolve o dia certo independentemente do TZ da máquina:
    assert.equal(somarDias('2026-08-12', 0), '2026-08-12');
  });

  it('não escorrega ao atravessar horário de verão', () => {
    // O Brasil não tem mais horário de verão desde 2019, mas o teste protege
    // contra rodar a suíte em CI configurado em America/New_York, onde
    // 2026-03-08 tem 23 horas. Somar 86.400.000 ms em horário LOCAL pularia
    // ou repetiria um dia; em UTC, não.
    assert.equal(somarDias('2026-03-07', 1), '2026-03-08');
    assert.equal(somarDias('2026-03-08', 1), '2026-03-09');
    assert.equal(somarDias('2026-11-01', 1), '2026-11-02');
  });
});

describe('somarDias', () => {
  const casos = [
    ['2026-08-12', 0, '2026-08-12'],
    ['2026-08-12', 1, '2026-08-13'],
    ['2026-08-12', 30, '2026-09-11'],
    ['2026-08-12', 365, '2027-08-12'],
    ['2026-08-12', -1, '2026-08-11'],
    ['2026-12-31', 1, '2027-01-01'],
    ['2026-01-01', -1, '2025-12-31'],
    ['2028-02-28', 1, '2028-02-29'],
    ['2026-02-28', 1, '2026-03-01'],
  ];

  for (const [base, dias, esperado] of casos) {
    it(`${base} + ${dias} = ${esperado}`, () => {
      assert.equal(somarDias(base, dias), esperado);
    });
  }

  it('recusa dias fracionários', () => {
    assert.throws(() => somarDias('2026-08-12', 1.5), DataInvalida);
  });

  it('preenche mês e dia com zero à esquerda', () => {
    // Sem o padStart, sairia "2027-1-1" e a comparação lexicográfica quebraria.
    assert.equal(somarDias('2026-12-31', 1), '2027-01-01');
  });
});

describe('diferencaEmDias e comparar', () => {
  it('conta a diferença nos dois sentidos', () => {
    assert.equal(diferencaEmDias('2026-09-11', '2026-08-12'), 30);
    assert.equal(diferencaEmDias('2026-08-12', '2026-09-11'), -30);
    assert.equal(diferencaEmDias('2026-08-12', '2026-08-12'), 0);
  });

  it('atravessa ano bissexto contando 366 dias', () => {
    assert.equal(diferencaEmDias('2029-01-01', '2028-01-01'), 366);
    assert.equal(diferencaEmDias('2027-01-01', '2026-01-01'), 365);
  });

  it('compara na ordem cronológica', () => {
    assert.equal(comparar('2026-08-11', '2026-08-12'), -1);
    assert.equal(comparar('2026-08-12', '2026-08-12'), 0);
    assert.equal(comparar('2026-08-13', '2026-08-12'), 1);
  });

  it('a ordem lexicográfica coincide com a cronológica (propriedade do ISO-8601)', () => {
    const desordenado = ['2026-12-01', '2025-01-31', '2026-01-02', '2026-01-10'];
    assert.deepEqual(
      [...desordenado].sort(),
      ['2025-01-31', '2026-01-02', '2026-01-10', '2026-12-01'],
    );
  });
});

describe('formatarBr', () => {
  it('inverte a ordem dos campos', () => {
    assert.equal(formatarBr('2026-08-12'), '12/08/2026');
  });

  it('preserva zeros à esquerda', () => {
    assert.equal(formatarBr('2026-01-05'), '05/01/2026');
  });
});
