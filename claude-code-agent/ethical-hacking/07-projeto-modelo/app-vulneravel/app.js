// app.js — Aplicação web DELIBERADAMENTE VULNERÁVEL para treino de pentest.
// SOMENTE laboratório, SOMENTE localhost. Não exponha à rede.
//
// Cinco vulnerabilidades foram plantadas de propósito. Cada uma está marcada com
// "VULN #n" e um comentário explicando a causa-raiz. A versão corrigida está em
// ../app-corrigida/app.js — compare os dois.
//
// Sem dependências externas: usa só módulos nativos do Node, para você conseguir
// ler o servidor inteiro e ver a causa de cada falha no código.

const http = require('http');
const fs   = require('fs');
const path = require('path');
const url  = require('url');

const PORTA = 3000;
const DB_PATH = path.join(__dirname, 'usuarios.db.json');
const db = JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));

// "Sessões" simplificadas: token -> id do usuário. (Um sistema real usaria JWT/cookie assinado.)
const sessoes = new Map();
let contador = 0;
function novoToken(idUsuario) {
  const t = 'tok_' + (++contador) + '_' + idUsuario; // token previsível — parte do exercício
  sessoes.set(t, idUsuario);
  return t;
}

function enviarJson(res, status, obj) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(obj, null, 2));
}

function corpo(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', (c) => (data += c));
    req.on('end', () => {
      try { resolve(JSON.parse(data || '{}')); }
      catch { resolve({}); }
    });
  });
}

const servidor = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const rota = parsed.pathname;
  const q = parsed.query;

  try {
    // ---- Página inicial -----------------------------------------------------
    if (rota === '/' && req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end(
        '<h1>LojaExemplo (app vulneravel de treino)</h1>' +
        '<p>Rotas: POST /api/login, GET /api/conta?id=, GET /download?arquivo=</p>' +
        '<p>Servidor v' + db.config.versao + '</p>'
      );
    }

    // ---- Login --------------------------------------------------------------
    if (rota === '/api/login' && req.method === 'POST') {
      const b = await corpo(req);
      const login = String(b.login || '');
      const senha = String(b.senha || '');

      // VULN #2 (A03 Injection) e VULN #4 (A07 Auth / A02 Crypto):
      // A "busca" imita SQL montado por concatenação: um filtro construído como string
      // e avaliado. Um valor como senha = '" || "1"=="1' faz o filtro sempre passar.
      // Além disso NÃO há rate limit (força bruta livre) e a senha é comparada em TEXTO PURO.
      const filtro = `u.login === "${login}" && u.senha === "${senha}"`;
      let usuario = null;
      try {
        // eslint-disable-next-line no-eval
        usuario = db.usuarios.find((u) => eval(filtro)); // eval de entrada do usuário = RCE-lite
      } catch (e) {
        // cai no tratador global (VULN #5)
        throw e;
      }

      if (!usuario) return enviarJson(res, 401, { erro: 'credenciais invalidas' });
      const token = novoToken(usuario.id);
      return enviarJson(res, 200, { token, id: usuario.id, papel: usuario.papel });
    }

    // ---- Ver conta ----------------------------------------------------------
    if (rota === '/api/conta' && req.method === 'GET') {
      const token = (req.headers['authorization'] || '').replace('Bearer ', '');
      if (!sessoes.has(token)) return enviarJson(res, 401, { erro: 'nao autenticado' });

      // VULN #1 (A01 Broken Access Control - IDOR):
      // A app autentica (checa o token) mas NÃO autoriza: ela devolve a conta do "id"
      // pedido na query, sem checar se esse id pertence a quem está logado.
      const idPedido = parseInt(q.id, 10);
      const conta = db.usuarios.find((u) => u.id === idPedido);
      if (!conta) return enviarJson(res, 404, { erro: 'nao encontrada' });
      return enviarJson(res, 200, {
        id: conta.id, login: conta.login, saldo: conta.saldo, cpf: conta.cpf, papel: conta.papel
      });
    }

    // ---- Download de comprovante -------------------------------------------
    if (rota === '/download' && req.method === 'GET') {
      const arquivo = String(q.arquivo || '');

      // VULN #3 (A01/A05 Path Traversal):
      // O caminho é montado juntando uma pasta com o nome que o usuário mandou, sem
      // normalizar nem checar. "../../../../etc/passwd" escapa da pasta e lê o sistema.
      const caminho = path.join(__dirname, 'comprovantes', arquivo);
      const conteudo = fs.readFileSync(caminho); // sem allowlist, sem verificação de prefixo
      res.writeHead(200, { 'Content-Type': 'application/octet-stream' });
      return res.end(conteudo);
    }

    return enviarJson(res, 404, { erro: 'rota inexistente' });

  } catch (err) {
    // VULN #5 (A05 Misconfiguration / A10):
    // Tratador global que vaza o stack trace E o segredo de configuração no corpo do erro.
    // Em produção, isso entrega ao atacante caminhos internos, versões e até chaves.
    return enviarJson(res, 500, {
      erro: 'erro interno',
      detalhe: String(err && err.stack ? err.stack : err),
      dica_config: db.config // vaza segredo_jwt — nunca faça isto
    });
  }
});

servidor.listen(PORTA, '127.0.0.1', () => {
  console.log(`App vulneravel ouvindo em http://127.0.0.1:${PORTA}  (SOMENTE laboratorio)`);
});
