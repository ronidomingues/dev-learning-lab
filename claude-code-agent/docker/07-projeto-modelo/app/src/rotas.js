// rotas.js — roteamento e tratamento de erro, sem framework.
//
// Sem Express de propósito: mantém o projeto com ZERO dependências de npm, o que faz o build
// da imagem ser reproduzível offline e o Dockerfile ficar legível sem ruído de lockfile.

import { ErroValidacao } from './repositorio.js';
import { log } from './log.js';

const PAGINA = (nome) => `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>${nome}</title>
  <style>
    :root { color-scheme: light dark; }
    body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1rem; line-height: 1.5; }
    form { display: grid; gap: .5rem; margin-bottom: 2rem; }
    input, textarea, button { font: inherit; padding: .5rem; }
    li { border-left: 3px solid currentColor; padding: .25rem .75rem; margin: .75rem 0; opacity: .9; }
    small { opacity: .6; }
    ul { list-style: none; padding: 0; }
  </style>
</head>
<body>
  <h1>${nome}</h1>
  <form id="f">
    <input name="autor" placeholder="Seu nome" required maxlength="60">
    <textarea name="texto" placeholder="Seu recado" required maxlength="280" rows="3"></textarea>
    <button>Publicar</button>
  </form>
  <ul id="lista"></ul>
  <script>
    const lista = document.getElementById('lista');
    async function carregar() {
      const r = await fetch('/api/recados');
      const { recados } = await r.json();
      lista.innerHTML = recados.map(x =>
        '<li><strong>' + escapar(x.autor) + '</strong><br>' + escapar(x.texto) +
        '<br><small>' + new Date(x.criadoEm).toLocaleString('pt-BR') + '</small></li>').join('');
    }
    function escapar(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
    document.getElementById('f').addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const dados = Object.fromEntries(new FormData(ev.target));
      const r = await fetch('/api/recados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados),
      });
      if (!r.ok) { const e = await r.json(); alert(e.erro); return; }
      ev.target.reset();
      carregar();
    });
    carregar();
  </script>
</body>
</html>`;

function responderJson(res, status, corpo) {
  const texto = JSON.stringify(corpo);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(texto),
  });
  res.end(texto);
}

async function lerCorpo(req, limiteBytes = 64 * 1024) {
  const pedacos = [];
  let total = 0;
  for await (const pedaco of req) {
    total += pedaco.length;
    // Sem este limite, um cliente malicioso derruba o processo por consumo de memória.
    if (total > limiteBytes) throw new ErroValidacao('corpo da requisição grande demais');
    pedacos.push(pedaco);
  }
  if (total === 0) return {};
  try {
    return JSON.parse(Buffer.concat(pedacos).toString('utf8'));
  } catch {
    throw new ErroValidacao('corpo não é um JSON válido');
  }
}

export function criarManipulador({ repositorio, config }) {
  return async function manipular(req, res) {
    const inicio = process.hrtime.bigint();
    const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const rota = `${req.method} ${url.pathname}`;

    try {
      // --- Healthcheck: usado pelo HEALTHCHECK do Dockerfile e pelo depends_on do Compose ---
      if (rota === 'GET /saude') {
        await repositorio.verificarSaude();
        return responderJson(res, 200, {
          status: 'ok',
          recados: repositorio.total(),
          ambiente: config.ambiente,
        });
      }

      // --- Liveness x readiness: sondas diferentes respondem perguntas diferentes ---
      // /vivo  = "o processo está de pé?"  (se falhar, reinicie)
      // /saude = "consigo atender?"        (se falhar, tire do balanceamento)
      if (rota === 'GET /vivo') {
        return responderJson(res, 200, { status: 'vivo', pid: process.pid });
      }

      if (rota === 'GET /api/recados') {
        const limite = Math.min(Number(url.searchParams.get('limite')) || 50, 200);
        return responderJson(res, 200, {
          total: repositorio.total(),
          recados: repositorio.listar({ limite }),
        });
      }

      if (rota === 'POST /api/recados') {
        const corpo = await lerCorpo(req);
        const recado = await repositorio.adicionar(corpo);
        log.info('recado publicado', { id: recado.id, autor: recado.autor });
        return responderJson(res, 201, recado);
      }

      if (req.method === 'DELETE' && url.pathname.startsWith('/api/recados/')) {
        const id = decodeURIComponent(url.pathname.slice('/api/recados/'.length));
        const removido = await repositorio.remover(id);
        if (!removido) return responderJson(res, 404, { erro: 'recado não encontrado' });
        return responderJson(res, 204, {});
      }

      if (rota === 'GET /') {
        const html = PAGINA(config.nomeDoMural);
        res.writeHead(200, {
          'Content-Type': 'text/html; charset=utf-8',
          'Content-Length': Buffer.byteLength(html),
        });
        return res.end(html);
      }

      return responderJson(res, 404, { erro: 'rota não encontrada', rota });
    } catch (e) {
      if (e instanceof ErroValidacao) {
        return responderJson(res, 400, { erro: e.message });
      }
      // Erro inesperado: registre COM contexto e devolva uma mensagem genérica.
      // Vazar a stack trace na resposta HTTP entrega detalhes internos a quem sondar a API.
      log.erro('falha ao processar requisição', { rota, erro: e });
      return responderJson(res, 500, { erro: 'erro interno' });
    } finally {
      const ms = Number(process.hrtime.bigint() - inicio) / 1e6;
      if (url.pathname !== '/saude' && url.pathname !== '/vivo') {
        log.info('requisição', { rota, status: res.statusCode, ms: Number(ms.toFixed(2)) });
      }
    }
  };
}
