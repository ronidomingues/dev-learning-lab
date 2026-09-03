/**
 * O tempo como dependência injetada — espelho de `python/assinaturas/relogio.py`.
 *
 * Em JavaScript existe a alternativa de falsear o tempo globalmente: o
 * `node:test` traz `t.mock.timers.enable({ apis: ['Date'] })`, e o Vitest tem
 * `vi.setSystemTime()`. Funciona, e às vezes é a única saída (código legado que
 * chama `Date.now()` no meio de tudo).
 *
 * Ainda assim, este projeto injeta o relógio. Motivo prático, com cicatriz:
 * falsear o tempo global vaza entre testes quando alguém esquece o
 * `mock.timers.reset()`, e o sintoma é um teste que só falha quando roda
 * **depois** de outro. Injeção não tem esse modo de falha.
 * (`test/relogio.test.js` mostra as duas técnicas lado a lado.)
 */

import { data, somarDias } from './data.js';

/** Implementação de produção: a única linha que fala com o mundo real. */
export class RelogioDoSistema {
  hoje() {
    // toISOString() é sempre UTC — coerente com src/data.js. Em produção real
    // você provavelmente quer o fuso do cliente; isso seria um parâmetro.
    return new Date().toISOString().slice(0, 10);
  }
}

/** Stub: devolve sempre a mesma data. */
export class RelogioFixo {
  #data;

  constructor(iso) {
    this.#data = data(iso);
  }

  hoje() {
    return this.#data;
  }

  avancar(dias) {
    this.#data = somarDias(this.#data, dias);
  }
}
