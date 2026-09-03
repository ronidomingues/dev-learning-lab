/**
 * Caso de uso com dublês — espelho de `tests/test_servico.py`.
 *
 * Novidade em relação ao Python: aqui aparece `t.mock`, o mockador embutido do
 * `node:test`. Ele cobre o que `unittest.mock` cobre no Python:
 *   t.mock.fn()                → Mock()
 *   fn.mock.calls              → mock.call_args_list
 *   fn.mock.callCount()        → mock.call_count
 *   t.mock.method(obj, 'nome') → mock.patch.object
 *   t.mock.timers              → freezegun / vi.setSystemTime
 *
 * Vantagem do `t.mock` sobre variáveis globais de mock: ele é **restaurado
 * automaticamente** no fim do teste. Sem isso, um mock vazado entre testes vira
 * aquela falha que só acontece quando a suíte roda inteira.
 */

import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { Assinatura, Estado } from '../src/assinatura.js';
import { Dinheiro } from '../src/dinheiro.js';
import { Cobranca, GatewayFalso, GatewayQueExplode } from '../src/gateway.js';
import { CATALOGO, Cupom, CupomInvalido } from '../src/plano.js';
import { RelogioFixo } from '../src/relogio.js';
import { RepositorioMemoria } from '../src/repositorio.js';
import { NotificadorEspiao, ServicoRenovacao } from '../src/servico.js';

const HOJE = '2026-08-12';

function vencida(id, cliente, plano = 'pro', diasAtraso = 0) {
  const a = Assinatura.criar(id, cliente, CATALOGO[plano], HOJE);
  a.proximaCobranca = diasAtraso === 0 ? HOJE : `2026-08-${String(12 - diasAtraso).padStart(2, '0')}`;
  return a;
}

const CUPONS = {
  BEMVINDO10: new Cupom('BEMVINDO10', 10, '2026-12-31', 1),
  EXPIRADO: new Cupom('EXPIRADO', 50, '2026-08-11', 99),
};

function montar(assinaturas = [], { gateway = new GatewayFalso(), cupons = CUPONS } = {}) {
  const repo = new RepositorioMemoria(assinaturas);
  const notificador = new NotificadorEspiao();
  const servico = new ServicoRenovacao(repo, gateway, new RelogioFixo(HOJE), notificador, cupons);
  return { servico, repo, gateway, notificador };
}

describe('caminho feliz', () => {
  it('cobra apenas as vencidas', async () => {
    const futura = Assinatura.criar('a2', 'bruno@ex.br', CATALOGO.pro, HOJE);
    const { servico, gateway } = montar([vencida('a1', 'ana@ex.br'), futura]);

    const relatorio = await servico.renovarVencidas();

    assert.equal(relatorio.cobradas, 1);
    assert.deepEqual(
      gateway.cobrancas.map((c) => c.cliente),
      ['ana@ex.br'],
    );
  });

  it('soma o arrecadado', async () => {
    const { servico } = montar([vencida('a1', 'a@ex.br', 'pro'), vencida('a2', 'b@ex.br', 'basico')]);
    const relatorio = await servico.renovarVencidas();
    assert.equal(relatorio.totalArrecadado.centavos, 6980);
  });

  it('persiste o novo vencimento', async () => {
    const { servico, repo } = montar([vencida('a1', 'ana@ex.br')]);
    await servico.renovarVencidas();
    assert.equal(repo.buscar('a1').proximaCobranca, '2026-09-11');
  });

  it('notifica com o id da transação', async () => {
    const { servico, notificador } = montar([vencida('a1', 'ana@ex.br')]);
    await servico.renovarVencidas();
    assert.deepEqual(notificador.assuntosDe('ana@ex.br'), ['Pagamento confirmado']);
    assert.match(notificador.mensagens[0].corpo, /tx-1/);
  });

  it('lista vazia não chama o gateway', async () => {
    const { servico, gateway, notificador } = montar([]);
    const relatorio = await servico.renovarVencidas();
    assert.equal(relatorio.cobradas, 0);
    assert.deepEqual(gateway.cobrancas, []);
    assert.deepEqual(notificador.mensagens, []);
  });
});

describe('recusa', () => {
  it('deixa inadimplente e não arrecada', async () => {
    const { servico, repo } = montar([vencida('a1', 'ana@ex.br')], {
      gateway: new GatewayFalso({ aprovar: false }),
    });
    const relatorio = await servico.renovarVencidas();
    assert.equal(relatorio.recusadas, 1);
    assert.equal(relatorio.totalArrecadado.centavos, 0);
    assert.equal(repo.buscar('a1').estado, Estado.INADIMPLENTE);
  });

  it('terceira recusa cancela e avisa', async () => {
    const a = vencida('a1', 'ana@ex.br');
    a.tentativasFalhas = 2;
    a.estado = Estado.INADIMPLENTE;
    const { servico, repo, notificador } = montar([a], {
      gateway: new GatewayFalso({ aprovar: false }),
    });

    const relatorio = await servico.renovarVencidas();

    assert.equal(relatorio.canceladas, 1);
    assert.equal(repo.buscar('a1').estado, Estado.CANCELADA);
    assert.deepEqual(notificador.assuntosDe('ana@ex.br'), ['Assinatura cancelada']);
  });

  it('a recusa de um cliente não impede a cobrança do outro', async () => {
    const { servico, repo } = montar([vencida('a1', 'ruim@ex.br'), vencida('a2', 'boa@ex.br')], {
      gateway: new GatewayFalso({ falharPara: ['ruim@ex.br'] }),
    });
    const relatorio = await servico.renovarVencidas();
    assert.equal(relatorio.cobradas, 1);
    assert.equal(relatorio.recusadas, 1);
    assert.equal(repo.buscar('a2').ciclosPagos, 1);
  });
});

describe('falha de infraestrutura', () => {
  it('gateway fora do ar não pune o cliente', async () => {
    const { servico, repo, notificador } = montar([vencida('a1', 'ana@ex.br')], {
      gateway: new GatewayQueExplode(),
    });

    const relatorio = await servico.renovarVencidas();

    assert.equal(relatorio.comErro, 1);
    assert.equal(relatorio.recusadas, 0);
    const salva = repo.buscar('a1');
    assert.equal(salva.tentativasFalhas, 0);
    assert.equal(salva.estado, Estado.ATIVA);
    assert.deepEqual(notificador.assuntosDe('ana@ex.br'), [
      'Não conseguimos processar sua cobrança hoje',
    ]);
  });

  it('erro em um cliente não interrompe o lote', async () => {
    let chamadas = 0;
    const instavel = {
      async cobrar() {
        chamadas += 1;
        if (chamadas === 1) throw new Error('conexão caiu');
        return new Cobranca(true, `tx-${chamadas}`);
      },
    };
    const { servico } = montar([vencida('a1', 'ana@ex.br'), vencida('a2', 'bruno@ex.br')], {
      gateway: instavel,
    });
    const relatorio = await servico.renovarVencidas();
    assert.equal(relatorio.comErro, 1);
    assert.equal(relatorio.cobradas, 1);
  });

  it('rejeição de Promise é tratada igual a throw síncrono', async () => {
    // Armadilha só de JavaScript: se o serviço não tivesse `await` dentro do
    // `try`, a rejeição escaparia do catch e viraria unhandledRejection, que
    // em Node 15+ DERRUBA o processo. Este teste protege o `await`.
    const rejeitador = { cobrar: () => Promise.reject(new Error('recusa assíncrona')) };
    const { servico } = montar([vencida('a1', 'ana@ex.br')], { gateway: rejeitador });
    const relatorio = await servico.renovarVencidas();
    assert.equal(relatorio.comErro, 1);
  });
});

describe('com t.mock (verificação de interação)', () => {
  it('gateway recebe cliente e valor do plano', async (t) => {
    const cobrar = t.mock.fn(async () => new Cobranca(true, 'tx-abc'));
    const { servico } = montar([vencida('a1', 'ana@ex.br', 'basico')], {
      gateway: { cobrar },
    });

    await servico.renovarVencidas();

    assert.equal(cobrar.mock.callCount(), 1);
    const [cliente, valor] = cobrar.mock.calls[0].arguments;
    assert.equal(cliente, 'ana@ex.br');
    assert.equal(valor.centavos, 1990);
  });

  it('a ordem das cobranças segue a ordem do repositório', async (t) => {
    const cobrar = t.mock.fn(async () => new Cobranca(true, 'tx'));
    const { servico } = montar([vencida('a2', 'b@ex.br'), vencida('a1', 'a@ex.br')], {
      gateway: { cobrar },
    });

    await servico.renovarVencidas();

    assert.deepEqual(
      cobrar.mock.calls.map((c) => c.arguments[0]),
      ['a@ex.br', 'b@ex.br'],
    );
  });

  it('mock frouxo aceita método que não existe — a armadilha', async (t) => {
    // Demonstração de problema, não de boa prática. `t.mock.fn()` não checa
    // assinatura; se o contrato virar `criarCobranca`, o mock continua
    // "funcionando" e o teste passa enquanto a produção quebra.
    // JavaScript não tem `autospec`. Mitigação: o teste de contrato
    // (test/contratoRepositorio.test.js) e tipos via JSDoc/TypeScript.
    const frouxo = t.mock.fn();
    assert.doesNotThrow(() => frouxo(1, 2, 3, 'qualquer coisa'));
    assert.equal(frouxo.mock.callCount(), 1);
  });

  it('t.mock.method troca um método de um objeto real e restaura sozinho', async (t) => {
    const gateway = new GatewayFalso();
    const espiao = t.mock.method(gateway, 'cobrar');

    const { servico } = montar([vencida('a1', 'ana@ex.br')], { gateway });
    await servico.renovarVencidas();

    assert.equal(espiao.mock.callCount(), 1);
    // O método original ainda rodou: `mock.method` espiona sem substituir,
    // a menos que se passe uma implementação. Por isso a cobrança de fato
    // entrou na lista do fake:
    assert.equal(gateway.cobrancas.length, 1);
  });
});

describe('cupons', () => {
  it('aplica desconto do cupom', () => {
    const { servico } = montar([]);
    assert.equal(servico.precoACobrar(vencida('a1', 'a@ex.br'), 'BEMVINDO10').centavos, 4491);
  });

  it('sem cupom cobra o preço cheio', () => {
    const { servico } = montar([]);
    assert.equal(servico.precoACobrar(vencida('a1', 'a@ex.br')).centavos, 4990);
  });

  it('cupom inexistente explode', () => {
    const { servico } = montar([]);
    assert.throws(() => servico.precoACobrar(vencida('a1', 'a@ex.br'), 'INVENTADO'), {
      name: 'CupomInvalido',
      message: /não existe/,
    });
  });

  it('cupom expirado explode usando o relógio injetado', () => {
    const { servico } = montar([]);
    assert.throws(() => servico.precoACobrar(vencida('a1', 'a@ex.br'), 'EXPIRADO'), CupomInvalido);
  });

  it('cupom de uso único não vale no segundo ciclo', () => {
    const { servico } = montar([]);
    const a = vencida('a1', 'a@ex.br');
    a.ciclosPagos = 1;
    assert.throws(() => servico.precoACobrar(a, 'BEMVINDO10'), /esgotado/);
  });
});

describe('relatório', () => {
  it('formata em uma linha legível', async () => {
    const { servico } = montar([vencida('a1', 'a@ex.br', 'basico')]);
    assert.equal(
      String(await servico.renovarVencidas()),
      '1 cobradas (R$ 19,90), 0 recusadas, 0 canceladas, 0 com erro',
    );
  });

  it('é imutável', async () => {
    const { servico } = montar([]);
    const relatorio = await servico.renovarVencidas();
    assert.throws(() => {
      relatorio.cobradas = 99;
    }, TypeError);
  });

  it('o total arrecadado é um Dinheiro, não um número solto', () => {
    assert.ok(new Dinheiro(0) instanceof Dinheiro);
  });
});
