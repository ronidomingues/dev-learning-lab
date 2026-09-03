// Camada HTTP: só traduz requisição <-> domínio. Zero regra de negócio aqui.
// Zero dependências externas — usa apenas node:http.

import { createServer } from 'node:http';
import { RepositorioDeTarefas, ErroDeValidacao, NaoEncontrado } from './tarefas.js';

/** Lê o corpo da requisição com limite, para não deixar o processo sem memória. */
async function lerCorpo(req, limiteBytes = 64 * 1024) {
  const pedacos = [];
  let tamanho = 0;
  for await (const pedaco of req) {
    tamanho += pedaco.length;
    if (tamanho > limiteBytes) {
      throw new ErroDeValidacao('corpo da requisição maior que 64 KiB');
    }
    pedacos.push(pedaco);
  }
  if (pedacos.length === 0) return {};
  try {
    return JSON.parse(Buffer.concat(pedacos).toString('utf8'));
  } catch {
    throw new ErroDeValidacao('corpo não é JSON válido');
  }
}

function responder(res, status, corpo) {
  const texto = corpo === undefined ? '' : JSON.stringify(corpo);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(texto),
  });
  res.end(texto);
}

/**
 * Cria o servidor. O repositório é injetado para o teste poder controlá-lo.
 * @param {{ repositorio?: RepositorioDeTarefas }} opcoes
 */
export function criarServidor({ repositorio = new RepositorioDeTarefas() } = {}) {
  const servidor = createServer(async (req, res) => {
    const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);
    const partes = url.pathname.split('/').filter(Boolean);

    try {
      // GET /saude — verificação de vida, usada pelo teste e pelo hook.
      if (req.method === 'GET' && url.pathname === '/saude') {
        return responder(res, 200, { status: 'ok', tarefas: repositorio.total });
      }

      if (partes[0] !== 'tarefas') {
        return responder(res, 404, { erro: 'rota não encontrada' });
      }

      // /tarefas
      if (partes.length === 1) {
        if (req.method === 'GET') {
          const concluida = url.searchParams.has('concluida')
            ? url.searchParams.get('concluida') === 'true'
            : null;
          const prioridade = url.searchParams.get('prioridade');
          return responder(res, 200, repositorio.listar({ concluida, prioridade }));
        }
        if (req.method === 'POST') {
          const corpo = await lerCorpo(req);
          const tarefa = repositorio.criar(corpo);
          res.setHeader('location', `/tarefas/${tarefa.id}`);
          return responder(res, 201, tarefa);
        }
        return responder(res, 405, { erro: 'método não permitido' });
      }

      // /tarefas/:id
      const id = partes[1];
      if (partes.length === 2) {
        if (req.method === 'GET') return responder(res, 200, repositorio.obter(id));
        if (req.method === 'DELETE') {
          repositorio.remover(id);
          return responder(res, 204);
        }
        return responder(res, 405, { erro: 'método não permitido' });
      }

      // /tarefas/:id/concluir
      if (partes.length === 3 && partes[2] === 'concluir' && req.method === 'POST') {
        return responder(res, 200, repositorio.concluir(id));
      }

      return responder(res, 404, { erro: 'rota não encontrada' });
    } catch (erro) {
      if (erro instanceof ErroDeValidacao || erro instanceof NaoEncontrado) {
        return responder(res, erro.status, { erro: erro.message });
      }
      // Erro não previsto: registra e devolve 500 sem vazar detalhe interno.
      console.error('[erro-interno]', erro);
      return responder(res, 500, { erro: 'erro interno' });
    }
  });

  return servidor;
}
