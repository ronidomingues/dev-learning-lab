/** Planos, catálogo, cupons e calendário — espelho de `test_plano.py` + `test_cupom.py`. */

import assert from 'node:assert/strict';
import { beforeEach, describe, it } from 'node:test';

import { Dinheiro } from '../src/dinheiro.js';
import { CATALOGO, Cupom, CupomInvalido, Plano, proximaCobranca } from '../src/plano.js';

describe('Plano', () => {
  it('recusa ciclo zero', () => {
    assert.throws(() => new Plano('x', 'X', new Dinheiro(100), 0), /positivo/);
  });

  it('recusa ciclo negativo', () => {
    assert.throws(() => new Plano('x', 'X', new Dinheiro(100), -30), /positivo/);
  });

  it('recusa ciclo fracionário', () => {
    assert.throws(() => new Plano('x', 'X', new Dinheiro(100), 30.5), /inteiro/);
  });

  it('é imutável', () => {
    assert.throws(() => {
      CATALOGO.pro.preco = new Dinheiro(1);
    }, TypeError);
  });
});

describe('catálogo', () => {
  for (const codigo of ['basico', 'pro', 'anual']) {
    it(`a chave "${codigo}" bate com o código do objeto`, () => {
      assert.equal(CATALOGO[codigo].codigo, codigo);
    });
  }

  it('o plano anual compensa por mês', () => {
    assert.ok(CATALOGO.anual.preco.centavos / 12 < CATALOGO.pro.preco.centavos);
  });

  it('o catálogo em si é congelado', () => {
    assert.throws(() => {
      CATALOGO.novo = 1;
    }, TypeError);
  });
});

describe('proximaCobranca', () => {
  const casos = [
    [0, '2026-08-12'],
    [1, '2026-09-11'],
    [2, '2026-10-11'],
    [12, '2027-08-07'],
  ];

  for (const [ciclos, esperado] of casos) {
    it(`${ciclos} ciclos de 30 dias → ${esperado}`, () => {
      assert.equal(proximaCobranca('2026-08-12', 30, ciclos), esperado);
    });
  }

  it('recusa ciclos negativos', () => {
    assert.throws(() => proximaCobranca('2026-08-12', 30, -1), /não pode ser negativo/);
  });

  it('atravessa ano bissexto sem pular dia', () => {
    assert.equal(proximaCobranca('2028-02-01', 30), '2028-03-02');
  });

  it('em ano comum o mesmo cálculo cai um dia adiante no calendário', () => {
    // Consequência aceita da escolha "ciclo em dias": o dia do mês escorrega.
    assert.equal(proximaCobranca('2026-02-01', 30), '2026-03-03');
  });

  it('atravessa a virada do ano', () => {
    assert.equal(proximaCobranca('2026-12-20', 30), '2027-01-19');
  });
});

describe('Cupom', () => {
  const PRECO = Dinheiro.deReais('100,00');
  const VALIDADE = '2026-08-31';
  let cupom;

  beforeEach(() => {
    // `beforeEach` é o equivalente mais próximo de uma fixture do pytest.
    // Diferença importante: a fixture do pytest é PEDIDA pelo teste (injeção),
    // enquanto o beforeEach roda para todos os testes do bloco, queira ou não.
    // Por isso o pytest escala melhor em suítes grandes.
    cupom = new Cupom('PROMO20', 20, VALIDADE, 2);
  });

  describe('validade', () => {
    it('vale no dia anterior', () => {
      assert.equal(cupom.precoComDesconto(PRECO, '2026-08-30', 0).centavos, 8000);
    });

    it('vale NO último dia (fronteira inclusiva)', () => {
      assert.equal(cupom.precoComDesconto(PRECO, '2026-08-31', 0).centavos, 8000);
    });

    it('não vale no dia seguinte', () => {
      assert.throws(() => cupom.precoComDesconto(PRECO, '2026-09-01', 0), {
        name: 'CupomInvalido',
        message: /expirou/,
      });
    });

    it('a mensagem de expiração traz a data em formato brasileiro', () => {
      assert.throws(() => cupom.precoComDesconto(PRECO, '2026-09-01', 0), /31\/08\/2026/);
    });
  });

  describe('limite de usos', () => {
    const casos = [
      [0, true],
      [1, true],
      [2, false],
      [3, false],
    ];

    for (const [usos, vale] of casos) {
      it(`${usos} usos anteriores → ${vale ? 'vale' : 'esgotado'}`, () => {
        if (vale) {
          assert.equal(cupom.precoComDesconto(PRECO, VALIDADE, usos).centavos, 8000);
        } else {
          assert.throws(() => cupom.precoComDesconto(PRECO, VALIDADE, usos), /esgotado/);
        }
      });
    }
  });

  describe('percentuais', () => {
    it('cortesia de 100% zera a conta', () => {
      const cortesia = new Cupom('CORTESIA', 100, VALIDADE);
      assert.equal(cortesia.precoComDesconto(PRECO, VALIDADE, 0).centavos, 0);
    });

    it('cupom de 0% é válido e inócuo', () => {
      const inocuo = new Cupom('NADA', 0, VALIDADE);
      assert.ok(inocuo.precoComDesconto(PRECO, VALIDADE, 0).igual(PRECO));
    });
  });

  it('quando expirado E esgotado, reporta a expiração primeiro', () => {
    assert.throws(() => cupom.precoComDesconto(PRECO, '2026-12-01', 99), /expirou/);
  });

  it('CupomInvalido é uma subclasse de Error com nome próprio', () => {
    // Verificar `instanceof` e `name` importa: quem consome o serviço faz
    // `catch (e) { if (e.name === 'CupomInvalido') ... }`. Isso é contrato.
    const erro = (() => {
      try {
        cupom.precoComDesconto(PRECO, '2026-09-01', 0);
      } catch (e) {
        return e;
      }
    })();
    assert.ok(erro instanceof CupomInvalido);
    assert.ok(erro instanceof Error);
    assert.equal(erro.name, 'CupomInvalido');
  });
});
