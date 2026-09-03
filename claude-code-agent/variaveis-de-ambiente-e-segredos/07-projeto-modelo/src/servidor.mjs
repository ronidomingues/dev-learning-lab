/**
 * servidor.mjs — a aplicação em si: uma API de recados.
 *
 * O que ela faz é o de menos. O que importa é COMO ela recebe configuração:
 * o servidor recebe `config` por parâmetro e NUNCA lê `process.env`.
 * Isso é injeção de dependência aplicada à configuração, e é o que torna
 * possível testar seis cenários de configuração sem subir seis processos.
 */
import { createServer } from 'node:http';
import { createHmac, timingSafeEqual, randomUUID } from 'node:crypto';
import { criarLog, redigirUrl } from './log.mjs';
import { configParaLog } from './config.mjs';

/** Comparação em tempo constante — evita vazar o segredo por análise de tempo. */
function iguaisSeguro(a, b) {
  const ba = Buffer.from(a ?? '', 'utf8');
  const bb = Buffer.from(b ?? '', 'utf8');
  if (ba.length !== bb.length) return false;
  return timingSafeEqual(ba, bb);
}

export function criarServidor(config, { log = criarLog(config.logLevel) } = {}) {
  /** "Banco de dados": em memória, porque o assunto do projeto é configuração. */
  const recados = [];

  const json = (res, status, corpo) => {
    const texto = JSON.stringify(corpo);
    res.writeHead(status, {
      'content-type': 'application/json; charset=utf-8',
      'content-length': Buffer.byteLength(texto),
      // cabeçalhos de higiene: nunca guardar resposta de API em cache compartilhado
      'cache-control': 'no-store',
    });
    res.end(texto);
  };

  const autorizado = (req) => {
    const cabecalho = req.headers.authorization ?? '';
    const token = cabecalho.startsWith('Bearer ') ? cabecalho.slice(7) : '';
    return iguaisSeguro(token, config.apiKey);
  };

  /** Assina o id do recado com o SESSION_SECRET — prova de que o servidor o emitiu. */
  const assinar = (valor) =>
    createHmac('sha256', config.sessionSecret).update(valor).digest('base64url').slice(0, 16);

  const servidor = createServer(async (req, res) => {
    const inicio = process.hrtime.bigint();
    const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);

    try {
      // ── rota pública: só diz se está de pé ─────────────────────────────
      if (req.method === 'GET' && url.pathname === '/health') {
        return json(res, 200, { ok: true, ambiente: config.ambiente });
      }

      // ── diagnóstico: configuração MASCARADA, e só para quem tem a chave ──
      // Existe porque é a primeira pergunta do suporte: "que configuração
      // esse servidor está usando?". Sem esta rota, alguém vai dar um
      // `console.log(config)` às pressas e vazar tudo no log.
      if (req.method === 'GET' && url.pathname === '/config') {
        if (!autorizado(req)) return json(res, 401, { erro: 'não autorizado' });
        return json(res, 200, {
          ...configParaLog(config),
          databaseUrl: redigirUrl(config.databaseUrl),
        });
      }

      if (req.method === 'GET' && url.pathname === '/recados') {
        if (!autorizado(req)) return json(res, 401, { erro: 'não autorizado' });
        return json(res, 200, { total: recados.length, recados });
      }

      if (req.method === 'POST' && url.pathname === '/recados') {
        if (!autorizado(req)) return json(res, 401, { erro: 'não autorizado' });
        if (recados.length >= config.maxRecados) {
          return json(res, 429, { erro: `limite de ${config.maxRecados} recados atingido` });
        }
        const corpo = await lerJson(req);
        const texto = String(corpo?.texto ?? '').trim();
        if (!texto) return json(res, 400, { erro: 'campo "texto" é obrigatório' });
        if (texto.length > 500) return json(res, 400, { erro: 'texto acima de 500 caracteres' });

        const id = randomUUID();
        const recado = { id, texto, assinatura: assinar(id), criadoEm: new Date().toISOString() };
        recados.push(recado);
        log.info('recado criado', { id, tamanho: texto.length });
        return json(res, 201, recado);
      }

      if (config.exporMetricas && req.method === 'GET' && url.pathname === '/metrics') {
        return json(res, 200, { recados: recados.length, memoriaMB: Math.round(process.memoryUsage().rss / 1e6) });
      }

      return json(res, 404, { erro: 'rota não encontrada' });
    } catch (e) {
      // Nunca devolver a mensagem de erro crua ao cliente: ela costuma conter
      // a string de conexão do banco, com senha.
      log.error('erro não tratado', { rota: url.pathname, tipo: e.name, mensagem: e.message });
      return json(res, 500, { erro: 'erro interno' });
    } finally {
      const ms = Number(process.hrtime.bigint() - inicio) / 1e6;
      log.debug('requisição', { metodo: req.method, rota: url.pathname, status: res.statusCode, ms: +ms.toFixed(2) });
    }
  });

  return { servidor, recados };
}

function lerJson(req, limiteBytes = 64 * 1024) {
  return new Promise((resolve, reject) => {
    let bruto = '';
    req.on('data', (pedaco) => {
      bruto += pedaco;
      if (bruto.length > limiteBytes) {
        req.destroy();
        reject(new Error('corpo grande demais'));
      }
    });
    req.on('end', () => {
      if (!bruto) return resolve({});
      try {
        resolve(JSON.parse(bruto));
      } catch {
        resolve(null);
      }
    });
    req.on('error', reject);
  });
}
