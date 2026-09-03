/**
 * O caso de uso — espelho de `python/assinaturas/servico.py`.
 *
 * Diferença de linguagem digna de nota: aqui `cobrar` é `async`, então
 * `renovarVencidas` é `async` e o laço usa `await`. Sequencial de propósito:
 * `Promise.all` sobre cobranças paralelas parece mais rápido e é um convite a
 * estourar o limite de requisições do gateway. Se algum dia virar paralelo,
 * será com concorrência limitada — e com um teste que prove o limite.
 */

import { Estado } from './assinatura.js';
import { Dinheiro, ZERO } from './dinheiro.js';
import { CupomInvalido } from './plano.js';

/** Spy: registra as chamadas para o teste inspecionar. */
export class NotificadorEspiao {
  constructor() {
    this.mensagens = [];
  }

  avisar(cliente, assunto, corpo) {
    this.mensagens.push({ cliente, assunto, corpo });
  }

  assuntosDe(cliente) {
    return this.mensagens.filter((m) => m.cliente === cliente).map((m) => m.assunto);
  }
}

export class Relatorio {
  constructor({ cobradas = 0, recusadas = 0, canceladas = 0, comErro = 0, totalArrecadado = ZERO } = {}) {
    Object.assign(this, { cobradas, recusadas, canceladas, comErro, totalArrecadado });
    Object.freeze(this);
  }

  toString() {
    return (
      `${this.cobradas} cobradas (${this.totalArrecadado}), ` +
      `${this.recusadas} recusadas, ${this.canceladas} canceladas, ` +
      `${this.comErro} com erro`
    );
  }
}

export class ServicoRenovacao {
  #repo;
  #gateway;
  #relogio;
  #notificador;
  #cupons;

  constructor(repositorio, gateway, relogio, notificador, cupons = {}) {
    this.#repo = repositorio;
    this.#gateway = gateway;
    this.#relogio = relogio;
    this.#notificador = notificador;
    this.#cupons = cupons;
  }

  precoACobrar(assinatura, codigoCupom = null) {
    const preco = assinatura.plano.preco;
    if (!codigoCupom) return preco;
    const cupom = this.#cupons[codigoCupom];
    if (!cupom) throw new CupomInvalido(`cupom ${codigoCupom} não existe`);
    return cupom.precoComDesconto(preco, this.#relogio.hoje(), assinatura.ciclosPagos);
  }

  async renovarVencidas() {
    const hoje = this.#relogio.hoje();
    let cobradas = 0;
    let recusadas = 0;
    let canceladas = 0;
    let comErro = 0;
    let arrecadado = ZERO;

    for (const assinatura of this.#repo.listarVencidas(hoje)) {
      let resultado;
      try {
        resultado = await this.#gateway.cobrar(assinatura.cliente, assinatura.plano.preco);
      } catch (erro) {
        // Falha de infraestrutura NÃO conta como falha do cliente.
        comErro += 1;
        this.#notificador.avisar(
          assinatura.cliente,
          'Não conseguimos processar sua cobrança hoje',
          `Erro técnico: ${erro.message}. Tentaremos novamente.`,
        );
        continue;
      }

      if (resultado.aprovada) {
        assinatura.registrarPagamento(hoje);
        cobradas += 1;
        arrecadado = arrecadado.mais(assinatura.plano.preco);
        this.#notificador.avisar(
          assinatura.cliente,
          'Pagamento confirmado',
          `${assinatura.plano.nome}: ${assinatura.plano.preco} ` +
            `(transação ${resultado.idTransacao})`,
        );
      } else {
        assinatura.registrarFalha();
        recusadas += 1;
        if (assinatura.estado === Estado.CANCELADA) {
          canceladas += 1;
          this.#notificador.avisar(
            assinatura.cliente,
            'Assinatura cancelada',
            `Após ${assinatura.tentativasFalhas} tentativas: ${resultado.motivo}`,
          );
        } else {
          this.#notificador.avisar(
            assinatura.cliente,
            'Pagamento recusado',
            `Tentativa ${assinatura.tentativasFalhas}: ${resultado.motivo}`,
          );
        }
      }

      this.#repo.salvar(assinatura);
    }

    return new Relatorio({
      cobradas,
      recusadas,
      canceladas,
      comErro,
      totalArrecadado: arrecadado instanceof Dinheiro ? arrecadado : ZERO,
    });
  }
}
