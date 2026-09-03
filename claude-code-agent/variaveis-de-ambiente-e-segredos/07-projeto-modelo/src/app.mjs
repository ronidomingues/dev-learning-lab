/**
 * app.mjs — ponto de entrada.
 *
 * Ordem, e a razão de cada passo:
 *   1. carregar e VALIDAR a configuração (falha rápida, antes de abrir socket);
 *   2. logar a configuração MASCARADA (para o suporte saber o que subiu);
 *   3. subir o servidor;
 *   4. desligar com elegância em SIGTERM (é o sinal que o Docker/systemd/K8s manda).
 *
 * Repare no que NÃO existe aqui: nenhuma chamada a `dotenv`.
 * Em desenvolvimento use `npm run dev`, que roda
 * `node --env-file-if-exists=.env`. Em produção não há `.env`, e o programa
 * funciona igual — é o teste decisivo do curso.
 */
import { carregarConfig, configParaLog } from './config.mjs';
import { criarLog, redigirUrl } from './log.mjs';
import { criarServidor } from './servidor.mjs';

const config = carregarConfig(); // encerra com 78 se algo estiver errado
const log = criarLog(config.logLevel);

log.info('configuração carregada', {
  ...configParaLog(config),
  databaseUrl: redigirUrl(config.databaseUrl),
  fonte: process.env.DATABASE_URL_FILE ? 'arquivo (_FILE)' : 'variável de ambiente',
});

const { servidor } = criarServidor(config, { log });

servidor.listen(config.porta, () => {
  log.info('servidor no ar', { porta: config.porta, ambiente: config.ambiente });
});

for (const sinal of ['SIGTERM', 'SIGINT']) {
  process.on(sinal, () => {
    log.info('desligando', { sinal });
    servidor.close(() => process.exit(0));
    // rede de segurança: se conexões abertas travarem o close
    setTimeout(() => process.exit(0), 10_000).unref();
  });
}
