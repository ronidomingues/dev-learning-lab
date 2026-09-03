/**
 * O serviço em Vitest — a metade do arquivo que mais muda em relação ao node:test:
 * mocks (`vi.fn`, `vi.spyOn`) e tempo falso (`vi.useFakeTimers`).
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { Assinatura, Estado } from '../src/assinatura.js';
import { Cobranca, GatewayFalso, GatewayQueExplode } from '../src/gateway.js';
import { CATALOGO } from '../src/plano.js';
import { RelogioDoSistema, RelogioFixo } from '../src/relogio.js';
import { RepositorioMemoria } from '../src/repositorio.js';
import { NotificadorEspiao, ServicoRenovacao } from '../src/servico.js';

const HOJE = '2026-08-12';

function vencida(id, cliente, plano = 'pro') {
  const a = Assinatura.criar(id, cliente, CATALOGO[plano], HOJE);
  a.proximaCobranca = HOJE;
  return a;
}

function montar(assinaturas = [], gateway = new GatewayFalso()) {
  const repo = new RepositorioMemoria(assinaturas);
  const notificador = new NotificadorEspiao();
  const servico = new ServicoRenovacao(repo, gateway, new RelogioFixo(HOJE), notificador);
  return { servico, repo, gateway, notificador };
}

describe('renovação', () => {
  it('cobra apenas as vencidas', async () => {
    const futura = Assinatura.criar('a2', 'bruno@ex.br', CATALOGO.pro, HOJE);
    const { servico, gateway } = montar([vencida('a1', 'ana@ex.br'), futura]);

    const relatorio = await servico.renovarVencidas();

    expect(relatorio.cobradas).toBe(1);
    expect(gateway.cobrancas.map((c) => c.cliente)).toEqual(['ana@ex.br']);
  });

  it('gateway fora do ar não pune o cliente', async () => {
    const { servico, repo } = montar([vencida('a1', 'ana@ex.br')], new GatewayQueExplode());

    const relatorio = await servico.renovarVencidas();

    expect(relatorio).toMatchObject({ comErro: 1, recusadas: 0 });
    expect(repo.buscar('a1')).toMatchObject({ estado: Estado.ATIVA, tentativasFalhas: 0 });
  });

  it('relata o resultado em uma linha', async () => {
    const { servico } = montar([vencida('a1', 'a@ex.br', 'basico')]);
    await expect(servico.renovarVencidas().then(String)).resolves.toBe(
      '1 cobradas (R$ 19,90), 0 recusadas, 0 canceladas, 0 com erro',
    );
  });
});

describe('mocks com vi', () => {
  it('vi.fn registra as chamadas', async () => {
    const cobrar = vi.fn(async () => new Cobranca(true, 'tx-abc'));
    const { servico } = montar([vencida('a1', 'ana@ex.br', 'basico')], { cobrar });

    await servico.renovarVencidas();

    expect(cobrar).toHaveBeenCalledTimes(1);
    expect(cobrar).toHaveBeenCalledWith('ana@ex.br', expect.objectContaining({ centavos: 1990 }));
  });

  it('vi.spyOn espiona sem substituir', async () => {
    const gateway = new GatewayFalso();
    const espiao = vi.spyOn(gateway, 'cobrar');

    const { servico } = montar([vencida('a1', 'ana@ex.br')], gateway);
    await servico.renovarVencidas();

    expect(espiao).toHaveBeenCalledOnce();
    expect(gateway.cobrancas).toHaveLength(1); // o original rodou
  });

  it('mockResolvedValueOnce encadeia respostas diferentes', async () => {
    const cobrar = vi
      .fn()
      .mockRejectedValueOnce(new Error('conexão caiu'))
      .mockResolvedValue(new Cobranca(true, 'tx-2'));

    const { servico } = montar(
      [vencida('a1', 'ana@ex.br'), vencida('a2', 'bruno@ex.br')],
      { cobrar },
    );

    const relatorio = await servico.renovarVencidas();

    expect(relatorio).toMatchObject({ comErro: 1, cobradas: 1 });
  });
});

describe('tempo falso com vi.useFakeTimers', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-08-12T12:00:00Z'));
  });

  afterEach(() => {
    // Sem este `useRealTimers`, o tempo falso VAZA para os arquivos seguintes
    // e o sintoma é um teste que só falha quando a suíte roda inteira.
    // Esta é a razão pela qual o projeto prefere injetar o relógio.
    vi.useRealTimers();
  });

  it('congela o relógio do sistema', () => {
    expect(new RelogioDoSistema().hoje()).toBe('2026-08-12');
  });

  it('avança o tempo em 30 dias', () => {
    vi.advanceTimersByTime(30 * 86_400_000);
    expect(new RelogioDoSistema().hoje()).toBe('2026-09-11');
  });
});
