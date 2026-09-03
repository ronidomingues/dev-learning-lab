/**
 * Dinheiro em centavos inteiros — espelho de `python/assinaturas/dinheiro.py`.
 *
 * Em JavaScript o problema é pior que em Python: **não existe tipo inteiro**.
 * Todo número é IEEE 754 de 64 bits, então `0.1 + 0.2 === 0.30000000000000004`
 * e `19.99 * 100 === 1998.9999999999998`. Guardar dinheiro em `number` de reais
 * é bug garantido; guardar em centavos inteiros é seguro até 2^53 centavos
 * (≈ 90 trilhões de reais), o que basta.
 *
 * A alternativa é `BigInt`, exata e sem teto. O custo é ergonomia: `1n + 1`
 * lança TypeError, e JSON não serializa BigInt. Escolha deste projeto: `number`
 * com validação estrita de inteiro, e um teste que trava a decisão.
 */

export class ValorInvalido extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'ValorInvalido';
  }
}

/** Arredondamento meio-para-cima em inteiros, sem passar por float. */
function metadeParaCima(numerador, denominador) {
  return Math.floor((numerador * 2 + denominador) / (denominador * 2));
}

export class Dinheiro {
  /** @param {number} centavos */
  constructor(centavos) {
    if (typeof centavos !== 'number' || !Number.isInteger(centavos)) {
      throw new ValorInvalido(`centavos deve ser inteiro, veio ${JSON.stringify(centavos)}`);
    }
    if (centavos < 0) {
      throw new ValorInvalido(`dinheiro não pode ser negativo: ${centavos}`);
    }
    this.centavos = centavos;
    Object.freeze(this); // imutabilidade: o equivalente ao frozen=True do Python
  }

  /**
   * Constrói a partir de reais. Aceita "19,90", "19.90", "R$ 1.234,56" ou 19.
   *
   * Repare que a conversão é feita **em texto**, com regex, e não com
   * `parseFloat(x) * 100`. Motivo: `parseFloat("19.99") * 100` dá
   * 1998.9999999999998. Fazer a conta em string elimina o float do caminho.
   */
  static deReais(entrada) {
    if (typeof entrada === 'number') {
      if (!Number.isFinite(entrada) || entrada < 0) {
        throw new ValorInvalido(`valor em reais inválido: ${entrada}`);
      }
      // toFixed(2) arredonda meio-para-cima para positivos na prática das
      // engines V8/SpiderMonkey; ainda assim validamos com teste.
      entrada = entrada.toFixed(2);
    }
    if (typeof entrada !== 'string') {
      throw new ValorInvalido(`esperava string ou number, veio ${typeof entrada}`);
    }

    let limpo = entrada.trim().replace(/R\$|\s/g, '');
    if (limpo.includes(',')) {
      limpo = limpo.replace(/\./g, '').replace(',', '.');
    }
    const casa = /^(\d+)(?:\.(\d+))?$/.exec(limpo);
    if (!casa) throw new ValorInvalido(`não reconheci como dinheiro: ${entrada}`);

    const inteiros = Number(casa[1]);
    const fracao = casa[2] ?? '';
    if (fracao.length <= 2) {
      const centavos = Number((fracao + '00').slice(0, 2));
      return new Dinheiro(inteiros * 100 + centavos);
    }
    // mais de 2 casas: arredonda meio-para-cima na terceira
    const centavosBrutos = Number(fracao.slice(0, 2));
    const resto = Number(fracao.slice(2));
    const escala = 10 ** (fracao.length - 2);
    const arredondado = metadeParaCima(resto, escala);
    return new Dinheiro(inteiros * 100 + centavosBrutos + arredondado);
  }

  mais(outro) {
    return new Dinheiro(this.centavos + outro.centavos);
  }

  menos(outro) {
    return new Dinheiro(this.centavos - outro.centavos);
  }

  vezes(quantidade) {
    if (!Number.isInteger(quantidade)) {
      throw new ValorInvalido('multiplique dinheiro só por inteiro (quantidade)');
    }
    return new Dinheiro(this.centavos * quantidade);
  }

  /** Desconta `percentual`%, arredondando meio-para-cima (favorece o cliente). */
  aplicarDesconto(percentual) {
    if (!Number.isInteger(percentual)) {
      throw new ValorInvalido('percentual deve ser inteiro');
    }
    if (percentual < 0 || percentual > 100) {
      throw new ValorInvalido(`percentual fora de 0..100: ${percentual}`);
    }
    const desconto = metadeParaCima(this.centavos * percentual, 100);
    return new Dinheiro(this.centavos - desconto);
  }

  /**
   * Igualdade **estrutural**. Existe porque em JavaScript
   * `new Dinheiro(100) === new Dinheiro(100)` é `false` — objetos comparam por
   * referência. Em Python, `@dataclass` gera `__eq__` de graça; aqui é manual.
   * É a diferença de linguagem que mais confunde quem migra: `assert.deepEqual`
   * salva no teste, mas o código de produção precisa de `igual()`.
   */
  igual(outro) {
    return outro instanceof Dinheiro && outro.centavos === this.centavos;
  }

  compararCom(outro) {
    return this.centavos - outro.centavos;
  }

  toString() {
    const inteiros = Math.floor(this.centavos / 100);
    const resto = this.centavos % 100;
    const comMilhar = String(inteiros).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `R$ ${comMilhar},${String(resto).padStart(2, '0')}`;
  }

  /** Serialização explícita: sem isto, `JSON.stringify` cospe `{"centavos":1990}`. */
  toJSON() {
    return { centavos: this.centavos, formatado: this.toString() };
  }
}

export const ZERO = new Dinheiro(0);
