/**
 * Gateway de pagamento: contrato e dublês.
 *
 * JavaScript não tem `Protocol` nem interface. O "contrato" é convenção +
 * teste de contrato. Isso é uma desvantagem real em relação ao Python tipado:
 * nada impede alguém de passar um objeto sem `cobrar`. O que compensa a falta
 * é `test/contratoGateway.test.js`, que roda a mesma bateria em toda
 * implementação registrada — inclusive nas falsas.
 */

export class Cobranca {
  constructor(aprovada, idTransacao, motivo = null) {
    Object.assign(this, { aprovada, idTransacao, motivo });
    Object.freeze(this);
  }
}

/** Implementação real. Só é exercitada em teste de integração. */
export class GatewayHttp {
  constructor(baseUrl, token, timeoutMs = 5000) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.token = token;
    this.timeoutMs = timeoutMs;
  }

  async cobrar(cliente, valor) {
    const resposta = await fetch(`${this.baseUrl}/cobrancas`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify({ cliente, centavos: valor.centavos }),
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    if (!resposta.ok) {
      throw new Error(`gateway respondeu ${resposta.status}`);
    }
    const dados = await resposta.json();
    return new Cobranca(Boolean(dados.aprovada), String(dados.id), dados.motivo ?? null);
  }
}

/** Fake: implementação funcional em memória do contrato inteiro. */
export class GatewayFalso {
  constructor({ aprovar = true, motivoRecusa = 'cartão sem limite', falharPara = [] } = {}) {
    this.aprovar = aprovar;
    this.motivoRecusa = motivoRecusa;
    this.falharPara = new Set(falharPara);
    this.cobrancas = [];
  }

  async cobrar(cliente, valor) {
    this.cobrancas.push({ cliente, valor });
    const n = this.cobrancas.length;
    if (!this.aprovar || this.falharPara.has(cliente)) {
      return new Cobranca(false, `tx-${n}`, this.motivoRecusa);
    }
    return new Cobranca(true, `tx-${n}`);
  }
}

/** Dublê de sabotagem: simula o provedor fora do ar. */
export class GatewayQueExplode {
  constructor(erro = new Error('gateway indisponível')) {
    this.erro = erro;
  }

  async cobrar() {
    throw this.erro;
  }
}
