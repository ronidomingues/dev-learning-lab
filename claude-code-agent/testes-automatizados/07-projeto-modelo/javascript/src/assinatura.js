/** Máquina de estados da assinatura — espelho de `python/assinaturas/assinatura.py`. */

import { comparar } from './data.js';
import { proximaCobranca } from './plano.js';

export const Estado = Object.freeze({
  ATIVA: 'ativa',
  PAUSADA: 'pausada',
  INADIMPLENTE: 'inadimplente',
  CANCELADA: 'cancelada',
});

export const MAX_TENTATIVAS = 3;

export class TransicaoInvalida extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'TransicaoInvalida';
  }
}

export class Assinatura {
  constructor({
    id,
    cliente,
    plano,
    inicio,
    proximaCobranca: proxima,
    estado = Estado.ATIVA,
    tentativasFalhas = 0,
    ciclosPagos = 0,
    historico = [],
  }) {
    Object.assign(this, {
      id,
      cliente,
      plano,
      inicio,
      proximaCobranca: proxima,
      estado,
      tentativasFalhas,
      ciclosPagos,
      historico: [...historico],
    });
  }

  static criar(id, cliente, plano, hoje) {
    return new Assinatura({
      id,
      cliente,
      plano,
      inicio: hoje,
      proximaCobranca: proximaCobranca(hoje, plano.diasCiclo),
    });
  }

  estaVencida(hoje) {
    const cobravel = this.estado === Estado.ATIVA || this.estado === Estado.INADIMPLENTE;
    return cobravel && comparar(hoje, this.proximaCobranca) >= 0;
  }

  pausar() {
    if (this.estado !== Estado.ATIVA) {
      throw new TransicaoInvalida(`só dá para pausar assinatura ativa, está ${this.estado}`);
    }
    this.estado = Estado.PAUSADA;
    this.historico.push('pausada');
  }

  retomar(hoje) {
    if (this.estado !== Estado.PAUSADA) {
      throw new TransicaoInvalida(`só dá para retomar assinatura pausada, está ${this.estado}`);
    }
    this.estado = Estado.ATIVA;
    this.proximaCobranca = proximaCobranca(hoje, this.plano.diasCiclo);
    this.historico.push('retomada');
  }

  cancelar() {
    if (this.estado === Estado.CANCELADA) {
      throw new TransicaoInvalida('assinatura já está cancelada');
    }
    this.estado = Estado.CANCELADA;
    this.historico.push('cancelada');
  }

  registrarPagamento(hoje) {
    if (this.estado !== Estado.ATIVA && this.estado !== Estado.INADIMPLENTE) {
      throw new TransicaoInvalida(`não se cobra assinatura ${this.estado}`);
    }
    this.estado = Estado.ATIVA;
    this.tentativasFalhas = 0;
    this.ciclosPagos += 1;
    this.proximaCobranca = proximaCobranca(hoje, this.plano.diasCiclo);
    this.historico.push(`pago em ${hoje}`);
  }

  registrarFalha() {
    if (this.estado !== Estado.ATIVA && this.estado !== Estado.INADIMPLENTE) {
      throw new TransicaoInvalida(`não se cobra assinatura ${this.estado}`);
    }
    this.tentativasFalhas += 1;
    this.historico.push(`falha ${this.tentativasFalhas}`);
    if (this.tentativasFalhas >= MAX_TENTATIVAS) {
      this.estado = Estado.CANCELADA;
      this.historico.push('cancelada por inadimplência');
    } else {
      this.estado = Estado.INADIMPLENTE;
    }
  }
}
