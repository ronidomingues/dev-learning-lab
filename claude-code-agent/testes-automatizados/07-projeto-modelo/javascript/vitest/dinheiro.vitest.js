/**
 * O MESMO conjunto de testes, escrito em Vitest.
 *
 * Objetivo deste arquivo: mostrar que o que muda entre `node:test` e
 * Vitest/Jest é **a sintaxe da asserção e do mock**, não o raciocínio de teste.
 * Quem entendeu `test/dinheiro.test.js` lê este aqui sem esforço.
 *
 * Tabela de tradução (vale igual para Jest 30):
 *
 *   node:test                              | Vitest 4 / Jest 30
 *   ---------------------------------------|-----------------------------------
 *   import { describe, it } from 'node:test'| globais (com `globals: true`) ou
 *                                          |   import { describe, it } from 'vitest'
 *   import assert from 'node:assert/strict'| expect (embutido)
 *   assert.equal(a, b)                     | expect(a).toBe(b)
 *   assert.deepStrictEqual(a, b)           | expect(a).toEqual(b)
 *   assert.ok(x)                           | expect(x).toBeTruthy()
 *   assert.throws(fn, /re/)                | expect(fn).toThrow(/re/)
 *   assert.rejects(fn)                     | await expect(fn()).rejects.toThrow()
 *   assert.match(s, /re/)                  | expect(s).toMatch(/re/)
 *   t.mock.fn()                            | vi.fn()
 *   t.mock.method(obj, 'm')                | vi.spyOn(obj, 'm')
 *   t.mock.timers.enable({apis:['Date']})  | vi.useFakeTimers()
 *   (laço gerando it())                    | it.each([...])('...', ...)
 *
 * Rode com: npx vitest run
 */

import { describe, expect, it } from 'vitest';

import { Dinheiro, ValorInvalido } from '../src/dinheiro.js';

describe('construção', () => {
  it('aceita centavos inteiros', () => {
    expect(new Dinheiro(1990).centavos).toBe(1990);
  });

  it('recusa negativo', () => {
    expect(() => new Dinheiro(-1)).toThrow(ValorInvalido);
    expect(() => new Dinheiro(-1)).toThrow(/não pode ser negativo/);
  });

  it.each([19.9, '100', NaN, Infinity, null, undefined, true])(
    'recusa %p',
    (entrada) => {
      expect(() => new Dinheiro(entrada)).toThrow(ValorInvalido);
    },
  );
});

describe('deReais', () => {
  // `it.each` é o `parametrize` do Vitest. Repare que ele produz um nome de
  // teste por caso, como o pytest — vantagem sobre o laço manual do node:test.
  it.each([
    ['19,90', 1990],
    ['19.90', 1990],
    ['R$ 19,90', 1990],
    ['1.234,56', 123456],
    ['0,01', 1],
    ['0', 0],
    ['100', 10000],
    [49, 4900],
    [19.9, 1990],
  ])('converte %s em %i centavos', (entrada, esperado) => {
    expect(Dinheiro.deReais(entrada).centavos).toBe(esperado);
  });

  it.each([
    ['0,005', 1],
    ['0,004', 0],
    ['0,015', 2],
    ['0,999', 100],
  ])('arredonda %s para %i', (entrada, esperado) => {
    expect(Dinheiro.deReais(entrada).centavos).toBe(esperado);
  });

  it('não sofre do erro de 19.99 * 100', () => {
    expect(19.99 * 100).not.toBe(1999);
    expect(Dinheiro.deReais('19,99').centavos).toBe(1999);
  });
});

describe('aritmética', () => {
  it('soma', () => {
    // `toEqual` compara estrutura — é o análogo do assert.deepStrictEqual.
    expect(new Dinheiro(1990).mais(new Dinheiro(10))).toEqual(new Dinheiro(2000));
  });

  it('recusa subtração que ficaria negativa', () => {
    expect(() => new Dinheiro(100).menos(new Dinheiro(101))).toThrow(ValorInvalido);
  });

  it('é imutável', () => {
    const d = new Dinheiro(100);
    expect(() => {
      d.centavos = 200;
    }).toThrow(TypeError);
    expect(d.centavos).toBe(100);
  });

  it('toBe usa Object.is: dois Dinheiro iguais NÃO são o mesmo objeto', () => {
    // A pegadinha número 1 de quem vem do pytest: `toBe` é identidade,
    // `toEqual` é estrutura. No pytest, `==` de dataclass já é estrutural.
    expect(new Dinheiro(100)).not.toBe(new Dinheiro(100));
    expect(new Dinheiro(100)).toEqual(new Dinheiro(100));
  });
});

describe('desconto', () => {
  it.each([
    [1000, 10, 900],
    [1000, 0, 1000],
    [1000, 100, 0],
    [1999, 10, 1799],
    [1, 50, 0],
    [3, 50, 1],
    [4990, 10, 4491],
  ])('%i centavos com %i%% vira %i', (centavos, percentual, esperado) => {
    expect(new Dinheiro(centavos).aplicarDesconto(percentual).centavos).toBe(esperado);
  });

  it.each([-1, 101, 1000])('recusa percentual %i', (p) => {
    expect(() => new Dinheiro(1000).aplicarDesconto(p)).toThrow(/fora de 0\.\.100/);
  });
});

describe('formatação', () => {
  it.each([
    [0, 'R$ 0,00'],
    [1, 'R$ 0,01'],
    [1990, 'R$ 19,90'],
    [123456, 'R$ 1.234,56'],
    [100000000, 'R$ 1.000.000,00'],
  ])('%i vira %s', (centavos, texto) => {
    expect(String(new Dinheiro(centavos))).toBe(texto);
  });

  it('ida e volta preserva o valor', () => {
    for (const c of [0, 1, 99, 100, 1990, 123456, 100000000]) {
      expect(Dinheiro.deReais(String(new Dinheiro(c))).centavos).toBe(c);
    }
  });

  it('snapshot inline: o Vitest sabe escrever o valor esperado sozinho', () => {
    // `toMatchInlineSnapshot` grava o valor no próprio arquivo na primeira
    // execução. É poderoso e perigoso: ver 75-armadilhas.md, "snapshot podre".
    // Use para saída estável e pequena, nunca para objeto grande de domínio.
    expect(new Dinheiro(1990).toJSON()).toMatchInlineSnapshot(`
      {
        "centavos": 1990,
        "formatado": "R$ 19,90",
      }
    `);
  });
});
