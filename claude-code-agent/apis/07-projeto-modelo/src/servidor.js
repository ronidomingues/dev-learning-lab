/**
 * Composição: junta repositório, roteador, middlewares e o servidor HTTP.
 *
 * `criarApp()` devolve o servidor SEM escutar, para os testes subirem instâncias
 * isoladas em portas efêmeras. Só o bloco do fim, guardado por `import.meta.main`,
 * é que escuta de verdade.
 */
import { createServer } from 'node:http';
import { randomUUID } from 'node:crypto';

import { criarRoteador } from './roteador.js';
import { criarRepositorio } from './repositorio.js';
import { criarRegistroDeTokens } from './middlewares/autenticacao.js';
import { criarRateLimit } from './middlewares/rateLimit.js';
import { criarIdempotencia } from './middlewares/idempotencia.js';
import { validar } from './validacao.js';
import { CriarLivro, AtualizarLivro, CriarEmprestimo } from './esquemas.js';
import { Problema, Problemas } from './problemas.js';
import { log } from './log.js';
import {
  lerJSON, aceitaJSON, responder, tratarErro,
  etagDe, etagCasa, cursor, inteiroDaQuery
} from './http.js';

export function criarApp({
  producao = process.env.NODE_ENV === 'production',
  limiteRate = Number(process.env.RATE_LIMIT ?? 100),
  janelaRateMs = Number(process.env.RATE_LIMIT_JANELA_MS ?? 60_000),
  semear = true
} = {}) {

  const repo = criarRepositorio();
  if (semear) repo.semear();

  const tokens = criarRegistroDeTokens({ producao });
  const rate = criarRateLimit({ limite: limiteRate, janelaMs: janelaRateMs });
  const idem = criarIdempotencia();
  const rotas = criarRoteador();

  const iniciadoEm = Date.now();

  // ======================= rotas públicas =======================

  rotas.get('/health', async (ctx) => {
    // Vivo: o processo responde. Não consulta dependência nenhuma de propósito —
    // se esta sonda falhar por causa do banco, o orquestrador reinicia o processo
    // sem necessidade. Ver 18-operacao-e-ciclo-de-vida.md §2.
    responder(ctx.res, 200, {
      status: 'ok',
      uptime_s: Math.floor((Date.now() - iniciadoEm) / 1000),
      versao: '1.0.0'
    });
  }, { publica: true });

  rotas.get('/health/pronto', async (ctx) => {
    // Pronto: consegue atender. AQUI sim se checa dependência.
    const estat = repo.estatisticas();
    responder(ctx.res, 200, { status: 'pronto', ...estat });
  }, { publica: true });

  rotas.get('/openapi.json', async (ctx) => {
    // O contrato servido pela própria API. Cacheável: não depende de identidade.
    responder(ctx.res, 200, contratoResumido(rotas), {
      'Cache-Control': 'public, max-age=300'
    });
  }, { publica: true });

  // ========================= livros =========================

  rotas.get('/livros', async (ctx) => {
    tokens.exigirEscopo(ctx.principal, 'livros:ler');

    const limite = inteiroDaQuery(ctx.url, 'limite', { padrao: 20, minimo: 1, maximo: 100 });
    const depoisDe = cursor.decodificar(ctx.url.searchParams.get('cursor'));
    const autor = ctx.url.searchParams.get('autor');

    const cruDisponivel = ctx.url.searchParams.get('disponivel');
    let disponivel = null;
    if (cruDisponivel !== null) {
      if (cruDisponivel !== 'true' && cruDisponivel !== 'false') {
        throw Problemas.parametroInvalido('disponivel', 'use true ou false');
      }
      disponivel = cruDisponivel === 'true';
    }

    const { dados, proximoId, total } = repo.listarLivros({ limite, depoisDe, autor, disponivel });

    responder(ctx.res, 200, {
      dados,
      paginacao: {
        limite,
        total,
        proximo_cursor: proximoId ? cursor.codificar(proximoId) : null
      }
    });
  });

  rotas.get('/livros/:id', async (ctx) => {
    tokens.exigirEscopo(ctx.principal, 'livros:ler');

    const livro = repo.obterLivro(ctx.params.id);
    if (!livro) throw Problemas.naoEncontrado('Livro', ctx.params.id);

    const etag = etagDe(livro);
    if (etagCasa(ctx.req.headers['if-none-match'], etag)) {
      // 304 não tem corpo. Economiza banda e, em muitas APIs, cota do cliente.
      ctx.res.writeHead(304, { ETag: etag, 'Cache-Control': 'private, max-age=30' });
      return ctx.res.end();
    }

    responder(ctx.res, 200, livro, {
      ETag: etag,
      // "private": só o cliente guarda, nunca um cache compartilhado.
      'Cache-Control': 'private, max-age=30'
    });
  });

  rotas.post('/livros', async (ctx) => {
    tokens.exigirEscopo(ctx.principal, 'livros:escrever');

    const corpo = await lerJSON(ctx.req);
    if (corpo === null) throw Problemas.validacao([{ campo: '(raiz)', motivo: 'corpo obrigatório' }]);

    const guardada = idem.consultar(ctx.req, ctx.url.pathname, corpo);
    if (guardada) {
      return responder(ctx.res, guardada.status, guardada.corpo,
                       { ...guardada.cabecalhos, 'Idempotency-Replayed': 'true' });
    }

    const erros = validar(corpo, CriarLivro);
    if (erros.length) throw Problemas.validacao(erros);

    if (corpo.isbn && repo.livroPorIsbn(corpo.isbn)) {
      throw Problemas.isbnDuplicado(corpo.isbn);
    }

    idem.reservar(ctx.req, ctx.url.pathname, corpo);
    try {
      const livro = repo.criarLivro(corpo);
      const cabecalhos = { Location: `/livros/${livro.id}`, ETag: etagDe(livro) };
      idem.guardar(ctx.req, 201, livro, cabecalhos);
      responder(ctx.res, 201, livro, cabecalhos);
    } catch (e) {
      idem.liberar(ctx.req);   // falhou: o cliente pode retentar com a mesma chave
      throw e;
    }
  });

  rotas.patch('/livros/:id', async (ctx) => {
    tokens.exigirEscopo(ctx.principal, 'livros:escrever');

    const livro = repo.obterLivro(ctx.params.id);
    if (!livro) throw Problemas.naoEncontrado('Livro', ctx.params.id);

    // Concorrência otimista: exigimos que o cliente diga qual versão ele leu.
    const ifMatch = ctx.req.headers['if-match'];
    if (!ifMatch) throw Problemas.precondicaoObrigatoria();

    const etagAtual = etagDe(livro);
    if (!etagCasa(ifMatch, etagAtual)) throw Problemas.precondicaoFalhou(etagAtual);

    const corpo = await lerJSON(ctx.req);
    if (corpo === null || Object.keys(corpo).length === 0) {
      throw Problemas.validacao([{ campo: '(raiz)', motivo: 'informe ao menos um campo' }]);
    }
    const erros = validar(corpo, AtualizarLivro);
    if (erros.length) throw Problemas.validacao(erros);

    if (corpo.isbn) {
      const outro = repo.livroPorIsbn(corpo.isbn);
      if (outro && outro.id !== livro.id) throw Problemas.isbnDuplicado(corpo.isbn);
    }

    const atualizado = repo.atualizarLivro(livro.id, corpo);
    responder(ctx.res, 200, atualizado, { ETag: etagDe(atualizado) });
  });

  // ======================= empréstimos =======================

  rotas.get('/emprestimos', async (ctx) => {
    tokens.exigirEscopo(ctx.principal, 'emprestimos:ler');
    const abertos = ctx.url.searchParams.get('abertos') === 'true';
    const livroId = ctx.url.searchParams.get('livro_id');
    responder(ctx.res, 200, { dados: repo.listarEmprestimos({ livroId, apenasAbertos: abertos }) });
  });

  rotas.post('/emprestimos', async (ctx) => {
    tokens.exigirEscopo(ctx.principal, 'emprestimos:escrever');

    const corpo = await lerJSON(ctx.req);
    if (corpo === null) throw Problemas.validacao([{ campo: '(raiz)', motivo: 'corpo obrigatório' }]);

    const guardada = idem.consultar(ctx.req, ctx.url.pathname, corpo);
    if (guardada) {
      return responder(ctx.res, guardada.status, guardada.corpo,
                       { ...guardada.cabecalhos, 'Idempotency-Replayed': 'true' });
    }

    const erros = validar(corpo, CriarEmprestimo);
    if (erros.length) throw Problemas.validacao(erros);

    const livro = repo.obterLivro(corpo.livro_id);
    if (!livro) throw Problemas.naoEncontrado('Livro', corpo.livro_id);
    // 409 e não 422: a requisição está correta; é o ESTADO que não permite.
    if (!livro.disponivel) throw Problemas.livroIndisponivel(livro.id);

    idem.reservar(ctx.req, ctx.url.pathname, corpo);
    try {
      const emprestimo = repo.criarEmprestimo({ livroId: corpo.livro_id, pessoa: corpo.pessoa });
      if (!emprestimo) throw Problemas.livroIndisponivel(corpo.livro_id);

      const cabecalhos = { Location: `/emprestimos/${emprestimo.id}` };
      idem.guardar(ctx.req, 201, emprestimo, cabecalhos);
      responder(ctx.res, 201, emprestimo, cabecalhos);
    } catch (e) {
      idem.liberar(ctx.req);
      throw e;
    }
  });

  rotas.post('/emprestimos/:id/devolucao', async (ctx) => {
    tokens.exigirEscopo(ctx.principal, 'emprestimos:escrever');

    const emprestimo = repo.obterEmprestimo(ctx.params.id);
    if (!emprestimo) throw Problemas.naoEncontrado('Emprestimo', ctx.params.id);

    if (emprestimo.devolvido_em !== null) {
      // Devolver duas vezes: idempotente por natureza. Devolvemos 200 com o
      // estado atual em vez de 409 — repetir não é erro quando o efeito é o mesmo.
      return responder(ctx.res, 200, emprestimo, { 'Idempotency-Replayed': 'true' });
    }

    responder(ctx.res, 200, repo.devolver(emprestimo.id));
  }, { idempotenciaOpcional: true });

  // ==================== o servidor HTTP ====================

  const servidor = createServer(async (req, res) => {
    const inicio = process.hrtime.bigint();

    // Aceita o request-id do cliente (correlação entre serviços) ou cria um.
    const requestId = req.headers['x-request-id'] ?? randomUUID();
    const registrador = log.com({ request_id: requestId, metodo: req.method, caminho: req.url });

    res.setHeader('X-Request-Id', requestId);

    // Fecha o ciclo do log SEMPRE, inclusive quando o cliente desiste no meio.
    res.on('finish', () => {
      const duracaoMs = Number(process.hrtime.bigint() - inicio) / 1e6;
      registrador.info('requisicao', {
        status: res.statusCode,
        duracao_ms: Math.round(duracaoMs * 100) / 100
      });
    });

    let url;
    try {
      url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);
    } catch {
      return tratarErro(res, Problemas.parametroInvalido('url', 'URL malformada'), requestId, registrador);
    }

    try {
      if (!aceitaJSON(req)) throw Problemas.naoAceitavel(['application/json']);

      // OPTIONS é respondido pelo próprio roteador, sem autenticação.
      if (req.method === 'OPTIONS') {
        const metodos = rotas.metodosDe(url.pathname);
        if (metodos.length === 0) throw Problemas.rotaNaoEncontrada('OPTIONS', url.pathname);
        res.writeHead(204, { Allow: [...metodos, 'OPTIONS'].join(', ') });
        return res.end();
      }

      const { manipulador, params, rota } = rotas.resolver(req.method, url.pathname);

      let principal = null;
      if (!rota.publica) {
        principal = tokens.autenticar(req);

        // Rate limit por IDENTIDADE, não por IP: vários clientes atrás do mesmo
        // NAT corporativo compartilhariam a cota se fosse por IP.
        const estado = rate.verificar(principal.identidade);
        for (const [k, v] of Object.entries(rate.cabecalhos(estado))) res.setHeader(k, v);
      }

      await manipulador({ req, res, url, params, principal, repo,
                          registrador: registrador.com({ identidade: principal?.identidade }) });

    } catch (erro) {
      // Se o erro for 429, os cabeçalhos de rate limit já foram setados acima.
      tratarErro(res, erro, requestId, registrador);
    }
  });

  // Timeouts explícitos. Sem eles, uma conexão lenta (ou um Slowloris) segura
  // recursos indefinidamente.
  servidor.requestTimeout = 30_000;
  servidor.headersTimeout = 10_000;
  servidor.keepAliveTimeout = 5_000;

  servidor.parar = () => { rate.parar(); idem.parar(); };
  servidor.repo = repo;
  servidor.rotas = rotas;

  return servidor;
}

/** Contrato mínimo servido em /openapi.json. O completo está em openapi.yaml. */
function contratoResumido(rotas) {
  const paths = {};
  for (const { metodo, padrao } of rotas.listar()) {
    const caminho = padrao.replace(/:([A-Za-z_][A-Za-z0-9_]*)/g, '{$1}');
    paths[caminho] ??= {};
    paths[caminho][metodo.toLowerCase()] = { operationId: `${metodo.toLowerCase()}${caminho}` };
  }
  return {
    openapi: '3.1.0',
    info: {
      title: 'API de Biblioteca',
      version: '1.0.0',
      description: 'Projeto-modelo do curso de APIs. O contrato completo está em openapi.yaml.'
    },
    paths
  };
}

// ------------------------- ponto de entrada -------------------------
// import.meta.main é true só quando este arquivo é executado diretamente,
// nunca quando é importado por um teste. (Node 24+; em versões anteriores,
// compare process.argv[1] com fileURLToPath(import.meta.url).)
if (import.meta.main) {
  const PORTA = Number(process.env.PORT ?? 3000);
  const app = criarApp();

  app.listen(PORTA, () => {
    log.info('servidor iniciado', {
      porta: PORTA,
      ambiente: process.env.NODE_ENV ?? 'development',
      pid: process.pid
    });
    console.log(`API      → http://localhost:${PORTA}`);
    console.log(`Contrato → http://localhost:${PORTA}/openapi.json`);
    console.log(`Saúde    → http://localhost:${PORTA}/health`);
    if (process.env.NODE_ENV !== 'production') {
      console.log('Tokens de exemplo:');
      console.log('  leitor        (livros:ler emprestimos:ler)  → tok_leitor_demo');
      console.log('  bibliotecario (livros:* emprestimos:*)      → tok_biblio_demo');
    }
  });

  /**
   * Desligamento gracioso.
   * Sem isto, um deploy mata o processo no meio de requisições em andamento e o
   * cliente recebe uma conexão fechada — que ele não sabe se é seguro retentar.
   */
  let desligando = false;
  for (const sinal of ['SIGTERM', 'SIGINT']) {
    process.on(sinal, () => {
      if (desligando) return process.exit(1);   // segundo Ctrl+C força
      desligando = true;
      log.info('desligando', { sinal });

      app.parar();
      app.close(() => { log.info('conexoes drenadas'); process.exit(0); });

      // Rede de segurança: se alguma conexão não drenar, não fique pendurado.
      setTimeout(() => { log.warn('desligamento forcado'); process.exit(1); }, 10_000).unref();
    });
  }

  process.on('unhandledRejection', (motivo) => {
    log.error('promise rejeitada sem tratamento', { motivo: String(motivo) });
  });
}
