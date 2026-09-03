#!/usr/bin/env node
/**
 * Borda do sistema — espelho de `python/assinaturas/cli.py`.
 * Zero regra de negócio: só montagem (*composition root*) e impressão.
 */

import { parseArgs } from 'node:util';

import { Assinatura } from './assinatura.js';
import { GatewayFalso } from './gateway.js';
import { CATALOGO } from './plano.js';
import { RelogioDoSistema, RelogioFixo } from './relogio.js';
import { RepositorioMemoria, RepositorioSQLite } from './repositorio.js';
import { NotificadorEspiao, ServicoRenovacao } from './servico.js';

export async function demo({ imprimir = console.log } = {}) {
  const hoje = '2026-08-12';
  const relogio = new RelogioFixo(hoje);
  const repo = new RepositorioMemoria([
    Assinatura.criar('a1', 'ana@exemplo.br', CATALOGO.pro, '2026-07-13'),
    Assinatura.criar('a2', 'bruno@exemplo.br', CATALOGO.basico, '2026-07-13'),
    Assinatura.criar('a3', 'carla@exemplo.br', CATALOGO.anual, hoje),
  ]);
  const gateway = new GatewayFalso({ falharPara: ['bruno@exemplo.br'] });
  const notificador = new NotificadorEspiao();

  const servico = new ServicoRenovacao(repo, gateway, relogio, notificador);
  const relatorio = await servico.renovarVencidas();

  imprimir(`data simulada: 12/08/2026`);
  imprimir(`relatório: ${relatorio}`);
  imprimir('\nnotificações enviadas:');
  for (const { cliente, assunto, corpo } of notificador.mensagens) {
    imprimir(`  → ${cliente}: ${assunto} | ${corpo}`);
  }
  imprimir('\nestado final:');
  for (const id of ['a1', 'a2', 'a3']) {
    const a = repo.buscar(id);
    imprimir(
      `  ${a.id} ${a.cliente.padEnd(22)} ${a.estado.padEnd(12)} ` +
        `próx. ${a.proximaCobranca} ciclos ${a.ciclosPagos}`,
    );
  }
  return 0;
}

export async function renovar({ banco, data, imprimir = console.log }) {
  const relogio = data ? new RelogioFixo(data) : new RelogioDoSistema();
  const repo = new RepositorioSQLite(banco);
  try {
    const servico = new ServicoRenovacao(
      repo,
      new GatewayFalso(),
      relogio,
      new NotificadorEspiao(),
    );
    imprimir(String(await servico.renovarVencidas()));
  } finally {
    repo.fechar();
  }
  return 0;
}

export async function main(argv = process.argv.slice(2), { imprimir = console.log } = {}) {
  const [comando, ...resto] = argv;
  if (comando === 'demo') return demo({ imprimir });
  if (comando === 'renovar') {
    const { values } = parseArgs({
      args: resto,
      options: { banco: { type: 'string', default: 'assinaturas.db' }, data: { type: 'string' } },
    });
    return renovar({ banco: values.banco, data: values.data, imprimir });
  }
  imprimir('uso: node src/cli.js demo | renovar [--banco X.db] [--data AAAA-MM-DD]');
  return 2;
}

// `import.meta.main` existe desde o Node 24; é o equivalente ao
// `if __name__ == "__main__"` do Python. Antes disso a gambiarra era comparar
// `process.argv[1]` com `import.meta.url`.
if (import.meta.main) {
  process.exit(await main());
}
