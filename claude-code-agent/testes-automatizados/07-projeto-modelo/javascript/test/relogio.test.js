/**
 * Duas técnicas para domar o tempo, lado a lado.
 *
 * A) **Injeção** (o que o projeto usa): passe o relógio como dependência.
 * B) **Falsear o tempo global** com `t.mock.timers`: útil quando o código
 *    legado chama `Date.now()` no meio da regra e você não pode refatorar hoje.
 *
 * Opinião profissional, declarada como opinião: prefira (A). (B) funciona, mas
 * cria acoplamento invisível — o teste passa a depender de um estado global que
 * outro teste pode ter deixado sujo, e o sintoma é falha por ordem de execução.
 * Use (B) como ponte para chegar em (A), não como destino.
 */

import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { RelogioDoSistema, RelogioFixo } from '../src/relogio.js';

describe('RelogioDoSistema', () => {
  it('devolve uma data ISO', () => {
    assert.match(new RelogioDoSistema().hoje(), /^\d{4}-\d{2}-\d{2}$/);
  });

  it('está dentro de uma faixa plausível', () => {
    // Faixa larga de propósito: comparar com a data exata de hoje tornaria o
    // teste *flaky* — ele quebraria sozinho à meia-noite UTC.
    const hoje = new RelogioDoSistema().hoje();
    assert.ok(hoje > '2024-01-01' && hoje < '2100-01-01');
  });

  it('duas leituras dão o mesmo dia, ou um a mais se cruzar a meia-noite', () => {
    const a = new RelogioDoSistema().hoje();
    const b = new RelogioDoSistema().hoje();
    assert.ok(b >= a);
  });
});

describe('RelogioFixo', () => {
  it('devolve sempre a mesma data', () => {
    const r = new RelogioFixo('2026-08-12');
    assert.equal(r.hoje(), '2026-08-12');
    assert.equal(r.hoje(), '2026-08-12');
  });

  it('avançar simula a passagem do tempo', () => {
    const r = new RelogioFixo('2026-08-12');
    r.avancar(30);
    assert.equal(r.hoje(), '2026-09-11');
  });

  it('avançar aceita negativo e volta no tempo', () => {
    const r = new RelogioFixo('2026-08-12');
    r.avancar(-1);
    assert.equal(r.hoje(), '2026-08-11');
  });

  it('avanços sucessivos acumulam', () => {
    const r = new RelogioFixo('2026-01-01');
    for (let i = 0; i < 12; i += 1) r.avancar(30);
    assert.equal(r.hoje(), '2026-12-27');
  });

  it('recusa data mal formada na construção', () => {
    assert.throws(() => new RelogioFixo('12/08/2026'), { name: 'DataInvalida' });
  });

  it('o campo interno é privado de verdade (#data)', () => {
    // Campos `#privados` do JavaScript não são convenção como o `_` do Python:
    // são inacessíveis de fora, e o acesso é erro de sintaxe/TypeError.
    const r = new RelogioFixo('2026-08-12');
    assert.equal(Object.keys(r).length, 0);
    assert.equal(JSON.stringify(r), '{}');
  });
});

describe('técnica B: falsear o tempo global com t.mock.timers', () => {
  it('congela Date e faz RelogioDoSistema virar determinístico', (t) => {
    // `now` em milissegundos desde 1970 UTC. 1786492800000 = 2026-08-12T00:00:00Z.
    t.mock.timers.enable({ apis: ['Date'], now: Date.UTC(2026, 7, 12) });

    assert.equal(new RelogioDoSistema().hoje(), '2026-08-12');
    assert.equal(new Date().toISOString(), '2026-08-12T00:00:00.000Z');
    // A restauração é automática no fim do teste — é a vantagem sobre
    // mexer em `globalThis.Date` na mão, que exige um try/finally.
  });

  it('permite adiantar o relógio dentro do mesmo teste', (t) => {
    t.mock.timers.enable({ apis: ['Date'], now: Date.UTC(2026, 7, 12) });
    t.mock.timers.tick(86_400_000 * 30);
    assert.equal(new RelogioDoSistema().hoje(), '2026-09-11');
  });

  it('o teste seguinte NÃO vê o tempo falso (prova do isolamento)', () => {
    const hoje = new RelogioDoSistema().hoje();
    assert.ok(hoje > '2026-01-01');
    assert.notEqual(new Date().getTime(), Date.UTC(2026, 7, 12));
  });
});

describe('contrato do relógio', () => {
  it('as duas implementações respondem hoje() com ISO', () => {
    for (const impl of [new RelogioDoSistema(), new RelogioFixo('2026-08-12')]) {
      assert.equal(typeof impl.hoje, 'function');
      assert.match(impl.hoje(), /^\d{4}-\d{2}-\d{2}$/);
    }
  });
});
