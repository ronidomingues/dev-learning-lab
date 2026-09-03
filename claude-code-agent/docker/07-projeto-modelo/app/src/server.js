// server.js — ponto de entrada. PID 1 dentro do container.
//
// As três responsabilidades deste arquivo, na ordem em que importam num container:
//   1. Falhar rápido e alto se a configuração estiver errada.
//   2. Subir o servidor.
//   3. Encerrar com elegância quando chegar SIGTERM — porque `docker stop` manda SIGTERM,
//      espera 10 segundos e então manda SIGKILL. Quem não trata SIGTERM perde requisições
//      em curso a cada deploy.

import http from 'node:http';
import { config } from './config.js';
import { log } from './log.js';
import { Repositorio } from './repositorio.js';
import { criarManipulador } from './rotas.js';

async function principal() {
  const repositorio = new Repositorio({
    caminho: config.arquivoDados,
    limite: config.maxRecados,
    tamanhoMaxTexto: config.tamanhoMaxTexto,
  });

  const carregados = await repositorio.iniciar();
  log.info('repositório pronto', { arquivo: config.arquivoDados, recados: carregados });

  const servidor = http.createServer(criarManipulador({ repositorio, config }));

  // Conexões ociosas seguram o encerramento. Este limite garante que o processo consiga sair.
  servidor.keepAliveTimeout = 5000;
  servidor.headersTimeout = 6000;

  await new Promise((resolve, reject) => {
    servidor.once('error', reject);
    servidor.listen(config.porta, config.host, resolve);
  });

  log.info('servidor ouvindo', {
    host: config.host,
    porta: config.porta,
    ambiente: config.ambiente,
    pid: process.pid,
    node: process.version,
  });

  // ---------- Encerramento gracioso ----------
  let encerrando = false;
  async function encerrar(sinal) {
    if (encerrando) return; // um segundo Ctrl+C não deve reentrar aqui
    encerrando = true;
    log.info('sinal recebido, encerrando', { sinal });

    // Rede de segurança: se as conexões não fecharem no prazo, saia mesmo assim.
    // Sem isto, um cliente com keep-alive impediria a saída até o SIGKILL do Docker.
    const prazo = setTimeout(() => {
      log.aviso('prazo de encerramento estourado, saindo à força');
      process.exit(1);
    }, config.prazoEncerramentoMs);
    prazo.unref();

    servidor.close((erro) => {
      if (erro) {
        log.erro('falha ao fechar o servidor', { erro });
        process.exit(1);
      }
      log.info('encerrado com elegância');
      process.exit(0);
    });
    servidor.closeIdleConnections?.();
  }

  process.on('SIGTERM', () => encerrar('SIGTERM')); // docker stop / orquestrador
  process.on('SIGINT', () => encerrar('SIGINT')); //  Ctrl+C

  // Um erro não tratado deixa o processo em estado desconhecido. Registrar e sair é mais
  // correto que seguir servindo: o supervisor (restart policy) sobe uma instância limpa.
  process.on('uncaughtException', (erro) => {
    log.erro('exceção não tratada', { erro });
    process.exit(1);
  });
  process.on('unhandledRejection', (motivo) => {
    log.erro('promessa rejeitada sem tratamento', { erro: motivo });
    process.exit(1);
  });
}

principal().catch((erro) => {
  // Configuração inválida cai aqui. Sair com código != 0 faz o Docker/Compose acusar a falha.
  log.erro('falha na inicialização', { erro });
  process.exit(1);
});
