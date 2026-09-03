/**
 * Testes unitários puros com `node:test` — espelho de `tests/test_dinheiro.py`.
 *
 * Tradução de vocabulário Python → JavaScript:
 *
 *   pytest                          | node:test
 *   --------------------------------|-------------------------------------
 *   class TestX:                    | describe('X', () => { ... })
 *   def test_y():                   | it('y', () => { ... })
 *   assert a == b                   | assert.deepStrictEqual(a, b)
 *   pytest.raises(E, match=...)     | assert.throws(fn, { name, message })
 *   @pytest.mark.parametrize        | for (const caso of casos) it(...)
 *   fixture                         | beforeEach / função de fábrica
 */

import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { Dinheiro, ValorInvalido } from '../src/dinheiro.js';

describe('construção', () => {
  it('aceita centavos inteiros', () => {
    assert.equal(new Dinheiro(1990).centavos, 1990);
  });

  it('aceita zero', () => {
    assert.equal(new Dinheiro(0).centavos, 0);
  });

  it('recusa negativo', () => {
    assert.throws(() => new Dinheiro(-1), {
      name: 'ValorInvalido',
      message: /não pode ser negativo/,
    });
  });

  it('recusa fracionário para não perder centavo', () => {
    assert.throws(() => new Dinheiro(19.9), ValorInvalido);
  });

  it('recusa string, mesmo string numérica', () => {
    // Em JavaScript `'100' * 1 === 100`: a coerção implícita é o inimigo.
    // Sem esta validação, `new Dinheiro('100')` criaria um objeto cujo
    // `centavos` é string, e a soma daria '100100' em vez de 200.
    assert.throws(() => new Dinheiro('100'), ValorInvalido);
  });

  it('recusa NaN e Infinity', () => {
    assert.throws(() => new Dinheiro(NaN), ValorInvalido);
    assert.throws(() => new Dinheiro(Infinity), ValorInvalido);
  });

  it('recusa null e undefined', () => {
    assert.throws(() => new Dinheiro(null), ValorInvalido);
    assert.throws(() => new Dinheiro(undefined), ValorInvalido);
  });

  it('recusa true, ao contrário do que a coerção sugeriria', () => {
    // `true * 1 === 1`. Em Python o problema é `isinstance(True, int)`.
    // Linguagens diferentes, armadilha idêntica, mesmo teste nas duas.
    assert.throws(() => new Dinheiro(true), ValorInvalido);
  });
});

describe('deReais', () => {
  const casos = [
    ['19,90', 1990, 'vírgula pt-BR'],
    ['19.90', 1990, 'ponto en-US'],
    ['R$ 19,90', 1990, 'com símbolo'],
    ['  19,90  ', 1990, 'com espaços'],
    ['1.234,56', 123456, 'milhar pt-BR'],
    ['0,01', 1, 'um centavo'],
    ['0', 0, 'zero'],
    ['100', 10000, 'string inteira'],
    [49, 4900, 'number inteiro'],
    [19.9, 1990, 'number fracionário'],
  ];

  for (const [entrada, esperado, rotulo] of casos) {
    it(`converte ${rotulo}`, () => {
      assert.equal(Dinheiro.deReais(entrada).centavos, esperado);
    });
  }

  const arredondamentos = [
    ['0,005', 1, 'meio arredonda pra cima'],
    ['0,004', 0, 'abaixo de meio desce'],
    ['0,015', 2, 'um e meio sobe'],
    ['0,999', 100, 'carrega para o real inteiro'],
  ];

  for (const [entrada, esperado, rotulo] of arredondamentos) {
    it(`arredonda: ${rotulo}`, () => {
      assert.equal(Dinheiro.deReais(entrada).centavos, esperado);
    });
  }

  it('não sofre do erro de ponto flutuante de 19.99 * 100', () => {
    // `19.99 * 100` em JavaScript dá 1998.9999999999998. Este teste é a razão
    // de existir da conversão por texto, e o comentário está aqui para que
    // ninguém "simplifique" o código depois.
    assert.notEqual(19.99 * 100, 1999);
    assert.equal(Dinheiro.deReais('19,99').centavos, 1999);
  });

  it('recusa lixo', () => {
    for (const lixo of ['abc', '', '1,2,3', 'R$', '-5']) {
      assert.throws(() => Dinheiro.deReais(lixo), ValorInvalido, `deveria recusar: ${lixo}`);
    }
  });

  it('recusa tipos que não são string nem number', () => {
    for (const tipoErrado of [null, undefined, {}, [], true, Symbol('x'), 10n]) {
      assert.throws(() => Dinheiro.deReais(tipoErrado), ValorInvalido);
    }
  });

  it('recusa number negativo, NaN e Infinity', () => {
    for (const ruim of [-1, -0.01, NaN, Infinity, -Infinity]) {
      assert.throws(() => Dinheiro.deReais(ruim), /valor em reais inválido/);
    }
  });
});

describe('aritmética', () => {
  it('soma', () => {
    assert.ok(new Dinheiro(1990).mais(new Dinheiro(10)).igual(new Dinheiro(2000)));
  });

  it('subtrai', () => {
    assert.ok(new Dinheiro(2000).menos(new Dinheiro(10)).igual(new Dinheiro(1990)));
  });

  it('recusa subtração que ficaria negativa', () => {
    assert.throws(() => new Dinheiro(100).menos(new Dinheiro(101)), ValorInvalido);
  });

  it('multiplica por quantidade', () => {
    assert.equal(new Dinheiro(1990).vezes(3).centavos, 5970);
  });

  it('recusa multiplicação por fração', () => {
    assert.throws(() => new Dinheiro(1990).vezes(0.9), {
      message: /só por inteiro/,
    });
  });

  it('é imutável', () => {
    const d = new Dinheiro(100);
    // Em módulo ESM o código é strict mode por padrão, então atribuir a um
    // objeto congelado LANÇA. Em script não-strict, falharia em silêncio —
    // motivo de fundo para preferir ESM.
    assert.throws(() => {
      d.centavos = 200;
    }, TypeError);
    assert.equal(d.centavos, 100);
  });

  it('deepStrictEqual funciona porque a forma do objeto é a mesma', () => {
    // Atenção: `assert.deepStrictEqual` compara estrutura E protótipo. Serve
    // para Dinheiro, mas NÃO substitui `igual()` no código de produção.
    assert.deepStrictEqual(new Dinheiro(100), new Dinheiro(100));
  });

  it('=== NÃO funciona: comparação por referência', () => {
    // Este teste documenta a semântica da linguagem. É a diferença mais
    // importante entre o Dinheiro de Python (dataclass, __eq__ de graça) e
    // este daqui. Um teste que "prova o óbvio" às vezes é documentação viva.
    assert.notEqual(new Dinheiro(100) === new Dinheiro(100), true);
  });

  it('ordena com compararCom', () => {
    const ordenado = [new Dinheiro(300), new Dinheiro(100), new Dinheiro(200)]
      .sort((a, b) => a.compararCom(b))
      .map((d) => d.centavos);
    assert.deepEqual(ordenado, [100, 200, 300]);
  });
});

describe('desconto', () => {
  const casos = [
    [1000, 10, 900],
    [1000, 0, 1000],
    [1000, 100, 0],
    [1999, 10, 1799],
    [1, 50, 0],
    [3, 50, 1],
    [4990, 10, 4491],
  ];

  for (const [centavos, percentual, esperado] of casos) {
    it(`${centavos} com ${percentual}% → ${esperado}`, () => {
      assert.equal(new Dinheiro(centavos).aplicarDesconto(percentual).centavos, esperado);
    });
  }

  it('recusa percentual fora de 0..100', () => {
    for (const p of [-1, 101, 1000]) {
      assert.throws(() => new Dinheiro(1000).aplicarDesconto(p), /fora de 0\.\.100/);
    }
  });

  it('recusa percentual fracionário', () => {
    assert.throws(() => new Dinheiro(1000).aplicarDesconto(10.5), /deve ser inteiro/);
  });

  it('bate centavo a centavo com a implementação Python', () => {
    // Valores extraídos de tests/test_dinheiro.py::TestDesconto. Se um dia as
    // duas implementações divergirem no arredondamento, é aqui que aparece.
    assert.equal(new Dinheiro(1999).aplicarDesconto(10).centavos, 1799);
    assert.equal(new Dinheiro(4990).aplicarDesconto(10).centavos, 4491);
  });
});

describe('formatação', () => {
  const casos = [
    [0, 'R$ 0,00'],
    [1, 'R$ 0,01'],
    [1990, 'R$ 19,90'],
    [123456, 'R$ 1.234,56'],
    [100000000, 'R$ 1.000.000,00'],
  ];

  for (const [centavos, texto] of casos) {
    it(`${centavos} → ${texto}`, () => {
      assert.equal(String(new Dinheiro(centavos)), texto);
    });
  }

  it('formatar e reler preserva o valor (ida e volta)', () => {
    for (const c of [0, 1, 99, 100, 1990, 123456, 100000000]) {
      const d = new Dinheiro(c);
      assert.equal(Dinheiro.deReais(String(d)).centavos, c);
    }
  });

  it('serializa em JSON de forma explícita', () => {
    assert.equal(
      JSON.stringify(new Dinheiro(1990)),
      '{"centavos":1990,"formatado":"R$ 19,90"}',
    );
  });
});
