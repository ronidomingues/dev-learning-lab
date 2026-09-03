// server.js — uma API HTTP mínima sobre a biblioteca, sem framework.
// Demonstra a aplicação conversando com o Postgres de forma correta.

import http from 'node:http';
import * as repo from './repositorio.js';
import { ErroNegocio } from './repositorio.js';
import { pool, fechar } from './db.js';

const PORTA = Number(process.env.PORT || 3000);

function json(res, status, corpo) {
  const texto = JSON.stringify(corpo);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(texto);
}

async function lerCorpo(req) {
  const pedacos = [];
  for await (const p of req) pedacos.push(p);
  if (!pedacos.length) return {};
  return JSON.parse(Buffer.concat(pedacos).toString('utf8'));
}

const servidor = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const rota = `${req.method} ${url.pathname}`;
  try {
    // Verifica se o banco responde. Usado como healthcheck.
    if (rota === 'GET /saude') {
      await pool.query('SELECT 1');
      return json(res, 200, { status: 'ok' });
    }

    if (rota === 'GET /livros') {
      const busca = url.searchParams.get('busca');
      return json(res, 200, await repo.listarLivros({ busca }));
    }

    if (rota === 'POST /livros') {
      const corpo = await lerCorpo(req);
      if (!corpo.titulo) throw new ErroNegocio('titulo é obrigatório', 'validacao');
      const id = await repo.cadastrarLivro(corpo);
      return json(res, 201, { id });
    }

    if (rota === 'GET /atrasados') {
      return json(res, 200, await repo.atrasados());
    }

    if (rota === 'POST /emprestimos') {
      const { exemplar_id, membro_id, dias } = await lerCorpo(req);
      const id = await repo.emprestar(exemplar_id, membro_id, dias);
      return json(res, 201, { emprestimo_id: id });
    }

    if (rota === 'POST /devolucoes') {
      const { exemplar_id } = await lerCorpo(req);
      const estava = await repo.devolver(exemplar_id);
      return json(res, 200, { devolvido: estava });
    }

    return json(res, 404, { erro: 'rota não encontrada' });
  } catch (e) {
    if (e instanceof ErroNegocio) {
      const status = e.codigo === 'nao_encontrado' ? 404 : e.codigo === 'validacao' ? 400 : 409;
      return json(res, status, { erro: e.message, codigo: e.codigo });
    }
    console.error(JSON.stringify({ nivel: 'erro', rota, erro: e.message }));
    return json(res, 500, { erro: 'erro interno' });
  }
});

servidor.listen(PORTA, '0.0.0.0', () =>
  console.log(JSON.stringify({ nivel: 'info', msg: 'ouvindo', porta: PORTA })),
);

// Encerramento gracioso: fecha o pool antes de sair, senão conexões ficam penduradas no Postgres.
async function encerrar() {
  console.log(JSON.stringify({ nivel: 'info', msg: 'encerrando' }));
  servidor.close();
  await fechar();
  process.exit(0);
}
process.on('SIGTERM', encerrar);
process.on('SIGINT', encerrar);
