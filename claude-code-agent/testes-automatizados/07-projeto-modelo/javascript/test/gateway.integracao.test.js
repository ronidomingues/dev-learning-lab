/**
 * Teste de integração do cliente HTTP, contra um servidor **de verdade**.
 *
 * Por que subir um `http.createServer` em vez de mockar o `fetch`?
 *
 * Porque mockar `fetch` testa a sua crença sobre o protocolo, não o protocolo.
 * Um mock devolve o que você mandou devolver — inclusive um JSON que o servidor
 * real nunca produziria, um status que ele nunca retorna, ou um corpo já
 * desserializado. Com um servidor real em `localhost`, o que se exercita é a
 * pilha inteira: serialização, cabeçalhos, status, timeout, JSON malformado.
 *
 * Custo: ~2 ms por teste e uma porta efêmera (`listen(0)`). Barato o bastante
 * para não valer a pena mockar.
 */

import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { after, before, describe, it } from 'node:test';

import { Dinheiro } from '../src/dinheiro.js';
import { GatewayHttp } from '../src/gateway.js';

/** Sobe um servidor que responde conforme o handler passado. Devolve a URL. */
function servidorDeMentira(handler) {
  const servidor = createServer(handler);
  return new Promise((resolve) => {
    servidor.listen(0, '127.0.0.1', () => {
      const { port } = servidor.address();
      resolve({ url: `http://127.0.0.1:${port}`, servidor });
    });
  });
}

function lerCorpo(req) {
  return new Promise((resolve) => {
    let dados = '';
    req.on('data', (pedaco) => {
      dados += pedaco;
    });
    req.on('end', () => resolve(dados));
  });
}

describe('GatewayHttp contra servidor real', () => {
  let url;
  let servidor;
  let ultimaRequisicao;
  let proximaResposta;

  before(async () => {
    ({ url, servidor } = await servidorDeMentira(async (req, res) => {
      ultimaRequisicao = {
        metodo: req.method,
        caminho: req.url,
        cabecalhos: req.headers,
        corpo: await lerCorpo(req),
      };
      const { status, corpo, atrasoMs } = proximaResposta;
      if (atrasoMs) await new Promise((r) => setTimeout(r, atrasoMs));
      res.writeHead(status, { 'content-type': 'application/json' });
      res.end(corpo);
    }));
  });

  after(() => {
    servidor.close();
  });

  it('envia POST em /cobrancas com o corpo e o token corretos', async () => {
    proximaResposta = { status: 200, corpo: JSON.stringify({ aprovada: true, id: 'tx-9' }) };
    const gateway = new GatewayHttp(url, 'segredo-123');

    await gateway.cobrar('ana@ex.br', new Dinheiro(4990));

    assert.equal(ultimaRequisicao.metodo, 'POST');
    assert.equal(ultimaRequisicao.caminho, '/cobrancas');
    assert.equal(ultimaRequisicao.cabecalhos.authorization, 'Bearer segredo-123');
    assert.equal(ultimaRequisicao.cabecalhos['content-type'], 'application/json');
    assert.deepEqual(JSON.parse(ultimaRequisicao.corpo), {
      cliente: 'ana@ex.br',
      centavos: 4990,
    });
  });

  it('remove a barra final da URL base para não gerar //cobrancas', async () => {
    proximaResposta = { status: 200, corpo: JSON.stringify({ aprovada: true, id: 'tx-1' }) };
    await new GatewayHttp(`${url}/`, 'x').cobrar('a@ex.br', new Dinheiro(100));
    assert.equal(ultimaRequisicao.caminho, '/cobrancas');
  });

  it('traduz aprovação em Cobranca aprovada', async () => {
    proximaResposta = { status: 200, corpo: JSON.stringify({ aprovada: true, id: 'tx-42' }) };
    const cobranca = await new GatewayHttp(url, 'x').cobrar('a@ex.br', new Dinheiro(100));
    assert.equal(cobranca.aprovada, true);
    assert.equal(cobranca.idTransacao, 'tx-42');
    assert.equal(cobranca.motivo, null);
  });

  it('traduz recusa preservando o motivo', async () => {
    proximaResposta = {
      status: 200,
      corpo: JSON.stringify({ aprovada: false, id: 7, motivo: 'saldo insuficiente' }),
    };
    const cobranca = await new GatewayHttp(url, 'x').cobrar('a@ex.br', new Dinheiro(100));
    assert.equal(cobranca.aprovada, false);
    assert.equal(cobranca.idTransacao, '7', 'id numérico vira string, pelo contrato');
    assert.equal(cobranca.motivo, 'saldo insuficiente');
  });

  it('erro HTTP 500 vira exceção com o status na mensagem', async () => {
    proximaResposta = { status: 500, corpo: '{"erro":"boom"}' };
    await assert.rejects(() => new GatewayHttp(url, 'x').cobrar('a@ex.br', new Dinheiro(100)), {
      message: /gateway respondeu 500/,
    });
  });

  it('402 (pagamento requerido) também é erro, não recusa silenciosa', async () => {
    // Fronteira fácil de errar: 4xx não é "recusa de cartão", é erro de
    // protocolo. Recusa vem como 200 + aprovada:false. O teste fixa o contrato.
    proximaResposta = { status: 402, corpo: '{}' };
    await assert.rejects(() => new GatewayHttp(url, 'x').cobrar('a@ex.br', new Dinheiro(100)), {
      message: /gateway respondeu 402/,
    });
  });

  it('JSON malformado vira erro de parsing, não Cobranca inválida', async () => {
    proximaResposta = { status: 200, corpo: 'isto não é json' };
    await assert.rejects(() => new GatewayHttp(url, 'x').cobrar('a@ex.br', new Dinheiro(100)));
  });

  it('respeita o timeout e aborta', async () => {
    proximaResposta = {
      status: 200,
      corpo: JSON.stringify({ aprovada: true, id: 'tx-lento' }),
      atrasoMs: 200,
    };
    const gateway = new GatewayHttp(url, 'x', 30); // 30 ms de paciência

    await assert.rejects(() => gateway.cobrar('a@ex.br', new Dinheiro(100)), {
      name: 'TimeoutError',
    });
    // Sem este teste, um gateway lento travaria o lote inteiro de cobrança —
    // e o sintoma em produção seria "a rotina noturna não terminou".
  });
});
