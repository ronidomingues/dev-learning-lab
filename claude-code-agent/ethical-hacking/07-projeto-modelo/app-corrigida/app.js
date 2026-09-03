// app.js — VERSÃO CORRIGIDA da app de treino. Roda na porta 3001.
// As cinco vulnerabilidades da versão vulnerável foram corrigidas. Cada correção
// está marcada com "FIX #n" e explica o que mudou e por quê.
//
// Ainda sem dependências externas (o objetivo é ver a defesa no próprio código).
// Numa app real você usaria: framework (Express), ORM com prepared statements,
// bcrypt/argon2 para senha, JWT assinado, e um middleware de autorização.

const http   = require('http');
const fs     = require('fs');
const path   = require('path');
const url    = require('url');
const crypto = require('crypto');

const PORTA = parseInt(process.env.PORTA || '3001', 10);
const DB_PATH = path.join(__dirname, '..', 'app-vulneravel', 'usuarios.db.json');
const raw = JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));

// FIX #4 (A07/A02): nunca guardar senha em texto. Aqui derivamos um hash com sal
// (scrypt, nativo do Node) na carga. Numa app real o hash já estaria salvo no banco;
// simulamos a migração para não alterar o arquivo de dados compartilhado.
const db = {
  config: { versao: raw.config.versao }, // FIX #5: NÃO expomos segredo_jwt em lugar nenhum
  usuarios: raw.usuarios.map((u) => {
    const sal = crypto.randomBytes(16);
    const hash = crypto.scryptSync(u.senha, sal, 32);
    return { id: u.id, login: u.login, papel: u.papel, saldo: u.saldo, cpf: u.cpf,
             sal: sal.toString('hex'), hash: hash.toString('hex') };
  }),
};

function verificarSenha(usuario, senhaTentada) {
  const sal = Buffer.from(usuario.sal, 'hex');
  const hash = crypto.scryptSync(String(senhaTentada), sal, 32).toString('hex');
  // comparação de tempo constante evita timing attack
  const a = Buffer.from(hash, 'hex');
  const b = Buffer.from(usuario.hash, 'hex');
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const sessoes = new Map();
function novoToken(idUsuario) {
  const t = crypto.randomBytes(24).toString('hex'); // FIX: token imprevisível (256 bits)
  sessoes.set(t, idUsuario);
  return t;
}

// FIX #4 (parte 2): rate limit simples por login, para conter força bruta.
const tentativas = new Map(); // login -> { n, ate }
function bloqueado(login) {
  const t = tentativas.get(login);
  return t && t.n >= 5 && Date.now() < t.ate;
}
function registrarFalha(login) {
  const t = tentativas.get(login) || { n: 0, ate: 0 };
  t.n += 1;
  if (t.n >= 5) t.ate = Date.now() + 60_000; // 1 min de bloqueio após 5 falhas
  tentativas.set(login, t);
}

function enviarJson(res, status, obj) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(obj, null, 2));
}
function corpo(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', (c) => (data += c));
    req.on('end', () => { try { resolve(JSON.parse(data || '{}')); } catch { resolve({}); } });
  });
}

const servidor = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const rota = parsed.pathname;
  const q = parsed.query;

  try {
    if (rota === '/' && req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end('<h1>LojaExemplo (versao corrigida)</h1>');
    }

    // ---- Login (corrigido) --------------------------------------------------
    if (rota === '/api/login' && req.method === 'POST') {
      const b = await corpo(req);
      const login = String(b.login || '');
      const senha = String(b.senha || '');

      if (bloqueado(login)) return enviarJson(res, 429, { erro: 'muitas tentativas, tente depois' });

      // FIX #2 (A03): comparação direta de dados, SEM eval e SEM montar string.
      // A entrada nunca vira código nem query concatenada.
      const usuario = db.usuarios.find((u) => u.login === login);
      if (!usuario || !verificarSenha(usuario, senha)) {
        registrarFalha(login);
        return enviarJson(res, 401, { erro: 'credenciais invalidas' }); // mensagem genérica
      }

      tentativas.delete(login);
      const token = novoToken(usuario.id);
      return enviarJson(res, 200, { token, id: usuario.id, papel: usuario.papel });
    }

    // ---- Ver conta (corrigido) ---------------------------------------------
    if (rota === '/api/conta' && req.method === 'GET') {
      const token = (req.headers['authorization'] || '').replace('Bearer ', '');
      const idLogado = sessoes.get(token);
      if (idLogado === undefined) return enviarJson(res, 401, { erro: 'nao autenticado' });

      // FIX #1 (A01 - IDOR): a conta retornada é SEMPRE a do usuário logado.
      // O id vem da sessão do servidor, não de um parâmetro que o cliente controla.
      // (Se um admin precisar ver outras contas, cheque o papel explicitamente.)
      let idAlvo = idLogado;
      if (q.id !== undefined) {
        const pedido = parseInt(q.id, 10);
        const logado = db.usuarios.find((u) => u.id === idLogado);
        if (pedido !== idLogado && (!logado || logado.papel !== 'admin')) {
          return enviarJson(res, 403, { erro: 'acesso negado' }); // autorização, não só autenticação
        }
        idAlvo = pedido;
      }
      const conta = db.usuarios.find((u) => u.id === idAlvo);
      if (!conta) return enviarJson(res, 404, { erro: 'nao encontrada' });
      return enviarJson(res, 200, { id: conta.id, login: conta.login, saldo: conta.saldo, papel: conta.papel });
      // Nota: cpf removido da resposta padrão — minimização de dados.
    }

    // ---- Download (corrigido) ----------------------------------------------
    if (rota === '/download' && req.method === 'GET') {
      const arquivo = String(q.arquivo || '');

      // FIX #3 (A01/A05 - Path Traversal): resolvemos o caminho e EXIGIMOS que ele
      // continue dentro da pasta permitida. Qualquer "../" que escape é rejeitado.
      const base = path.join(__dirname, 'comprovantes');
      const alvo = path.resolve(base, arquivo);
      if (!alvo.startsWith(base + path.sep)) {
        return enviarJson(res, 400, { erro: 'nome de arquivo invalido' });
      }
      // (Ainda melhor: allowlist de nomes conhecidos.)
      if (!fs.existsSync(alvo)) return enviarJson(res, 404, { erro: 'nao encontrado' });
      res.writeHead(200, { 'Content-Type': 'application/octet-stream' });
      return res.end(fs.readFileSync(alvo));
    }

    return enviarJson(res, 404, { erro: 'rota inexistente' });

  } catch (err) {
    // FIX #5 (A05/A10): resposta de erro genérica. O detalhe vai para o LOG do servidor,
    // nunca para o cliente. Nenhum segredo, nenhum stack trace, nenhuma versão vazam.
    console.error('[erro interno]', err && err.stack ? err.stack : err);
    return enviarJson(res, 500, { erro: 'erro interno' });
  }
});

servidor.listen(PORTA, '127.0.0.1', () => {
  console.log(`App CORRIGIDA ouvindo em http://127.0.0.1:${PORTA}`);
});
