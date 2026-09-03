/** Roteamento e regras de cada endpoint. */

import { lerJson, responderJson, responderErroAuth, cookieRefresh, cookieRefreshApagado, lerCookie } from './http.js';
import { gerarHash, conferir } from './senha.js';
import { abrirSessao, renovarSessao, exigirAutenticacao, exigirPapel, ErroSessao } from './autenticacao.js';
import { agoraEmSegundos, decodificarSemVerificar } from './jwt.js';

export function criarRoteador({ armazem, chaveiro, config, relogio = agoraEmSegundos }) {
  return async function rotear(req, res) {
    const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);
    const rota = `${req.method} ${url.pathname}`;
    const agora = relogio();

    try {
      switch (true) {
        // --- descoberta ----------------------------------------------------
        case rota === 'GET /.well-known/jwks.json':
          // Publico de proposito: e assim que outros servicos verificam nossos
          // tokens sem que precisemos entregar segredo nenhum a eles.
          return responderJson(res, 200, chaveiro.jwks(), { 'cache-control': 'public, max-age=300' });

        case rota === 'GET /saude':
          return responderJson(res, 200, { ok: true, kidAtiva: chaveiro.kidAtiva, agora });

        // --- autenticacao ---------------------------------------------------
        case rota === 'POST /auth/registrar':
          return await registrar(req, res, { armazem });

        case rota === 'POST /auth/login':
          return await login(req, res, { armazem, chaveiro, config, agora });

        case rota === 'POST /auth/refresh':
          return await refresh(req, res, { armazem, chaveiro, config, agora });

        case rota === 'POST /auth/logout':
          return await logout(req, res, { armazem, chaveiro, config, agora });

        // --- recurso protegido ----------------------------------------------
        case rota === 'GET /notas': {
          const { usuario } = exigirAutenticacao(req, { armazem, chaveiro, config, agora });
          return responderJson(res, 200, { notas: armazem.listarNotas(usuario.id) });
        }

        case rota === 'POST /notas': {
          const { usuario } = exigirAutenticacao(req, { armazem, chaveiro, config, agora });
          const corpo = await lerJson(req);
          if (typeof corpo.texto !== 'string' || corpo.texto.trim() === '') {
            return responderJson(res, 400, { erro: 'texto_obrigatorio' });
          }
          return responderJson(res, 201, armazem.criarNota(usuario.id, corpo.texto.trim()));
        }

        case req.method === 'DELETE' && /^\/notas\/[\w-]+$/.test(url.pathname): {
          const { usuario } = exigirAutenticacao(req, { armazem, chaveiro, config, agora });
          const id = url.pathname.split('/')[2];
          if (!armazem.apagarNota(usuario.id, id)) {
            return responderJson(res, 404, { erro: 'nota_nao_encontrada' });
          }
          res.writeHead(204).end();
          return;
        }

        // --- rota administrativa: mostra autorizacao por papel ---------------
        case rota === 'GET /admin/sessoes': {
          const { payload } = exigirAutenticacao(req, { armazem, chaveiro, config, agora });
          exigirPapel(payload, 'admin');
          return responderJson(res, 200, {
            refreshAtivos: armazem.refresh.size,
            jtiRevogados: armazem.jtiRevogados.size,
            familiasQueimadas: armazem.familiasQueimadas.size,
          });
        }

        // --- utilitario didatico ---------------------------------------------
        case rota === 'POST /debug/decodificar': {
          // Existe so para o material de estudo: mostra o conteudo de um token
          // SEM verificar. Nao coloque um endpoint destes em producao.
          const corpo = await lerJson(req);
          const { cabecalho, payload } = decodificarSemVerificar(String(corpo.token ?? ''));
          return responderJson(res, 200, { cabecalho, payload, aviso: 'assinatura NAO verificada' });
        }

        default:
          return responderJson(res, 404, { erro: 'rota_nao_encontrada', rota });
      }
    } catch (erro) {
      if (erro instanceof ErroSessao) {
        return responderErroAuth(res, erro.status, erro.codigo, erro.message);
      }
      if (erro.status) return responderJson(res, erro.status, { erro: erro.message });
      // Erro nao previsto: log completo no servidor, mensagem generica ao cliente.
      console.error('[erro]', erro);
      return responderJson(res, 500, { erro: 'erro_interno' });
    }
  };
}

// ---------------------------------------------------------------------------

async function registrar(req, res, { armazem }) {
  const corpo = await lerJson(req);
  const email = String(corpo.email ?? '').trim().toLowerCase();
  const senha = String(corpo.senha ?? '');

  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return responderJson(res, 400, { erro: 'email_invalido' });
  }
  if (senha.length < 12) {
    // Comprimento minimo em vez de "1 maiuscula, 1 simbolo": e o que a NIST
    // SP 800-63B recomenda desde 2017, e da mais entropia de verdade.
    return responderJson(res, 400, { erro: 'senha_curta', mensagem: 'minimo de 12 caracteres' });
  }

  try {
    const papeis = corpo.papeis === 'admin' ? ['usuario', 'admin'] : ['usuario'];
    const usuario = armazem.criarUsuario({ email, hashDaSenha: await gerarHash(senha), papeis });
    return responderJson(res, 201, { id: usuario.id, email: usuario.email, papeis: usuario.papeis });
  } catch (erro) {
    if (erro.codigo === 'email_duplicado') return responderJson(res, 409, { erro: 'email_duplicado' });
    throw erro;
  }
}

async function login(req, res, { armazem, chaveiro, config, agora }) {
  const corpo = await lerJson(req);
  const email = String(corpo.email ?? '').trim().toLowerCase();
  const senha = String(corpo.senha ?? '');

  const usuario = armazem.usuarioPorEmail(email);
  // Mesma resposta para "e-mail nao existe" e "senha errada": responder coisas
  // diferentes entrega ao atacante uma lista de e-mails validos de graca.
  const senhaOk = usuario ? await conferir(senha, usuario.hashDaSenha) : false;
  if (!usuario || !senhaOk) {
    return responderJson(res, 401, { erro: 'credenciais_invalidas' });
  }

  const sessao = abrirSessao({ usuario, chaveiro, armazem, config, agora });
  return responderJson(
    res,
    200,
    {
      token_type: 'Bearer',
      access_token: sessao.accessToken,
      expires_in: sessao.expiraEm,
      // O refresh vai TAMBEM no corpo para facilitar o estudo com curl.
      // Numa aplicacao de navegador, entregue-o so pelo cookie HttpOnly.
      refresh_token: sessao.refreshToken,
    },
    { 'set-cookie': cookieRefresh(sessao.refreshToken, { maxIdade: config.vidaRefreshSegundos, seguro: config.cookieSeguro }) },
  );
}

async function refresh(req, res, { armazem, chaveiro, config, agora }) {
  const corpo = await lerJson(req).catch(() => ({}));
  const enviado = corpo.refresh_token ?? lerCookie(req, 'refresh_token');
  if (!enviado) return responderJson(res, 400, { erro: 'refresh_ausente' });

  try {
    const sessao = renovarSessao({ refreshToken: String(enviado), chaveiro, armazem, config, agora });
    return responderJson(
      res,
      200,
      {
        token_type: 'Bearer',
        access_token: sessao.accessToken,
        expires_in: sessao.expiraEm,
        refresh_token: sessao.refreshToken,
      },
      { 'set-cookie': cookieRefresh(sessao.refreshToken, { maxIdade: config.vidaRefreshSegundos, seguro: config.cookieSeguro }) },
    );
  } catch (erro) {
    if (erro instanceof ErroSessao) {
      // Sessao morta: limpe o cookie, senao o cliente reenvia lixo para sempre.
      return responderJson(res, erro.status, { erro: erro.codigo, mensagem: erro.message }, {
        'set-cookie': cookieRefreshApagado({ seguro: config.cookieSeguro }),
      });
    }
    throw erro;
  }
}

async function logout(req, res, { armazem, chaveiro, config, agora }) {
  // Logout de verdade precisa matar OS DOIS tokens:
  //   1. o refresh, apagando-o do armazem;
  //   2. o access, pondo o `jti` na lista de negacao ate o `exp`.
  // Sem o passo 2, o access token continua valendo pelos minutos que faltam —
  // esse e o "JWT nao desloga" que tanto se ouve por ai.
  let revogado = false;
  try {
    const { payload } = exigirAutenticacao(req, { armazem, chaveiro, config, agora });
    armazem.revogarJti(payload.jti, payload.exp);
    revogado = true;
  } catch {
    // Logout sem access token valido ainda deve limpar o refresh.
  }

  const corpo = await lerJson(req).catch(() => ({}));
  const enviado = corpo.refresh_token ?? lerCookie(req, 'refresh_token');
  let familiaEncerrada = false;
  if (enviado) {
    const registro = armazem.buscarRefresh(String(enviado));
    if (registro) { armazem.queimarFamilia(registro.familiaId); familiaEncerrada = true; }
  }

  return responderJson(res, 200, { ok: true, accessRevogado: revogado, familiaEncerrada }, {
    'set-cookie': cookieRefreshApagado({ seguro: config.cookieSeguro }),
  });
}
