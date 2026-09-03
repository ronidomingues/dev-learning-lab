/** Ponto de entrada: monta as pecas e sobe o servidor HTTP. */

import { createServer } from 'node:http';
import { Armazem } from './armazem.js';
import { carregarOuCriarChaveiro } from './chaves.js';
import { criarRoteador } from './roteador.js';
import { config } from './config.js';
import { agoraEmSegundos } from './jwt.js';

export function montarAplicacao({ armazem = new Armazem(), chaveiro, configuracao = config, relogio } = {}) {
  const chaveiroFinal = chaveiro ?? carregarOuCriarChaveiro(configuracao.caminhoChaveiro);
  const rotear = criarRoteador({ armazem, chaveiro: chaveiroFinal, config: configuracao, relogio });
  const servidor = createServer((req, res) => {
    rotear(req, res).catch((erro) => {
      console.error('[falha nao tratada]', erro);
      if (!res.headersSent) res.writeHead(500).end();
    });
  });
  return { servidor, armazem, chaveiro: chaveiroFinal, config: configuracao };
}

// So sobe o servidor se este arquivo for executado direto, nao quando importado
// pelos testes.
if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split('/').pop())) {
  const app = montarAplicacao();

  // Faxina periodica das listas: sem isso, a lista de negacao cresce para sempre.
  const faxina = setInterval(() => app.armazem.limpar(agoraEmSegundos()), 60_000);
  faxina.unref();

  app.servidor.listen(config.porta, () => {
    console.log(`cofre-de-notas ouvindo em http://localhost:${config.porta}`);
    console.log(`  emissor:   ${config.emissor}`);
    console.log(`  audiencia: ${config.audiencia}`);
    console.log(`  kid ativa: ${app.chaveiro.kidAtiva}`);
    console.log(`  JWKS:      http://localhost:${config.porta}/.well-known/jwks.json`);
  });
}
