/** Planos e cupons — espelho de `python/assinaturas/plano.py`. */

import { comparar, formatarBr, somarDias } from './data.js';
import { Dinheiro } from './dinheiro.js';

export class Plano {
  constructor(codigo, nome, preco, diasCiclo) {
    if (!Number.isInteger(diasCiclo) || diasCiclo <= 0) {
      throw new Error('diasCiclo deve ser inteiro positivo');
    }
    Object.assign(this, { codigo, nome, preco, diasCiclo });
    Object.freeze(this);
  }
}

export const CATALOGO = Object.freeze({
  basico: new Plano('basico', 'Básico', Dinheiro.deReais('19,90'), 30),
  pro: new Plano('pro', 'Pro', Dinheiro.deReais('49,90'), 30),
  anual: new Plano('anual', 'Pro Anual', Dinheiro.deReais('499,00'), 365),
});

export class CupomInvalido extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'CupomInvalido';
  }
}

export class Cupom {
  constructor(codigo, percentual, validade, usosMaximos = 1) {
    Object.assign(this, { codigo, percentual, validade, usosMaximos });
    Object.freeze(this);
  }

  /** Vale **no** dia da validade (inclusive). Ver test/cupom.test.js. */
  precoComDesconto(preco, hoje, usosAtuais) {
    if (comparar(hoje, this.validade) > 0) {
      throw new CupomInvalido(`cupom ${this.codigo} expirou em ${formatarBr(this.validade)}`);
    }
    if (usosAtuais >= this.usosMaximos) {
      throw new CupomInvalido(
        `cupom ${this.codigo} esgotado (${usosAtuais}/${this.usosMaximos})`,
      );
    }
    return preco.aplicarDesconto(this.percentual);
  }
}

export function proximaCobranca(base, diasCiclo, ciclos = 1) {
  if (!Number.isInteger(ciclos) || ciclos < 0) {
    throw new Error('ciclos não pode ser negativo');
  }
  return somarDias(base, diasCiclo * ciclos);
}
