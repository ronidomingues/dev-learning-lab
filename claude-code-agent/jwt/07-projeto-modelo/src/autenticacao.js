/**
 * Regras de autenticacao: emissao do par de tokens, rotacao do refresh com
 * deteccao de reuso, e o guarda que protege as rotas.
 */

import { randomUUID } from 'node:crypto';
import { assinar, verificar, agoraEmSegundos, ErroJwt } from './jwt.js';
import { ALG_DE_ASSINATURA } from './chaves.js';

/**
 * Emite o access token.
 *
 * Repare no que NAO vai no payload: nome, e-mail, telefone, endereco. O payload
 * de um JWT e assinado, nao cifrado — qualquer pessoa com o token le tudo, e o
 * token passa por logs de proxy, historico de navegador e ferramentas de
 * observabilidade. Vai so o que o servico precisa para autorizar.
 *
 * `typ: 'at+jwt'` segue a RFC 9068 e existe por um motivo pratico: impede que
 * um id_token do OIDC seja aceito como access token, e vice-versa.
 */
export function emitirAccessToken({ usuario, chaveiro, config, agora = agoraEmSegundos() }) {
  const jti = randomUUID();
  const token = assinar(
    {
      iss: config.emissor,
      sub: usuario.id,
      aud: config.audiencia,
      exp: agora + config.vidaAccessSegundos,
      jti,
      papeis: usuario.papeis,
    },
    { alg: ALG_DE_ASSINATURA, chave: chaveiro.ativa.privada, kid: chaveiro.kidAtiva, typ: 'at+jwt', agora },
  );
  return { token, jti, expiraEm: agora + config.vidaAccessSegundos };
}

/** Login: valida credencial (feito pelo chamador) e devolve o par de tokens. */
export function abrirSessao({ usuario, chaveiro, armazem, config, agora = agoraEmSegundos() }) {
  const acesso = emitirAccessToken({ usuario, chaveiro, config, agora });
  const { segredo, registro } = armazem.emitirRefresh({
    usuarioId: usuario.id,
    vidaSegundos: config.vidaRefreshSegundos,
    agora,
  });
  return {
    accessToken: acesso.token,
    expiraEm: config.vidaAccessSegundos,
    refreshToken: segredo,
    familiaId: registro.familiaId,
  };
}

export class ErroSessao extends Error {
  constructor(codigo, mensagem, status = 401) {
    super(mensagem);
    this.name = 'ErroSessao';
    this.codigo = codigo;
    this.status = status;
  }
}

/**
 * Rotacao de refresh token com deteccao de reuso (o padrao recomendado pela
 * RFC 9700 para clientes publicos).
 *
 * Cada uso queima o token antigo e emite um novo da MESMA familia. Se um token
 * ja queimado reaparecer, uma copia esta circulando: derruba-se a familia
 * inteira e a pessoa precisa fazer login de novo. E incomodo de proposito —
 * o incomodo e o preco de detectar roubo de token sem hardware extra.
 */
export function renovarSessao({ refreshToken, chaveiro, armazem, config, agora = agoraEmSegundos() }) {
  const registro = armazem.buscarRefresh(refreshToken);

  if (!registro) throw new ErroSessao('refresh_desconhecido', 'refresh token invalido');
  if (armazem.familiaEstaQueimada(registro.familiaId)) {
    throw new ErroSessao('familia_queimada', 'sessao invalidada por suspeita de reuso; faca login novamente');
  }
  if (registro.expEm <= agora) throw new ErroSessao('refresh_expirado', 'refresh token expirado');

  if (registro.usado) {
    const queimados = armazem.queimarFamilia(registro.familiaId);
    const erro = new ErroSessao('reuso_detectado', 'refresh token reutilizado; todas as sessoes desta familia foram encerradas');
    erro.queimados = queimados;
    throw erro;
  }

  const usuario = armazem.usuarioPorId(registro.usuarioId);
  if (!usuario) throw new ErroSessao('usuario_removido', 'usuario nao existe mais');

  const novo = armazem.emitirRefresh({
    usuarioId: usuario.id,
    familiaId: registro.familiaId, // mesma familia: e a mesma sessao continuando
    vidaSegundos: config.vidaRefreshSegundos,
    agora,
  });
  armazem.marcarRefreshUsado(refreshToken, novo.registro.id);

  const acesso = emitirAccessToken({ usuario, chaveiro, config, agora });
  return {
    accessToken: acesso.token,
    expiraEm: config.vidaAccessSegundos,
    refreshToken: novo.segredo,
  };
}

/**
 * Guarda de rota. Devolve o payload verificado ou lanca ErroSessao.
 *
 * Ordem deliberada: primeiro a assinatura e as claims (barato, sem I/O),
 * depois a lista de negacao (uma consulta). Fazer o contrario significaria
 * consultar o banco com dados que nem sabemos se sao autenticos.
 */
export function exigirAutenticacao(req, { chaveiro, armazem, config, agora = agoraEmSegundos() }) {
  const cabecalho = req.headers.authorization ?? '';
  // O esquema e "Bearer", case-insensitive por RFC 7235; exatamente um espaco.
  const casou = /^Bearer (\S+)$/i.exec(cabecalho);
  if (!casou) throw new ErroSessao('sem_credencial', 'cabecalho Authorization: Bearer <token> ausente ou malformado');

  let payload;
  try {
    ({ payload } = verificar(casou[1], {
      algoritmos: [ALG_DE_ASSINATURA],       // lista fechada: a defesa contra confusao de algoritmo
      chave: (cab) => chaveiro.publicaPara(cab),
      emissor: config.emissor,
      audiencia: config.audiencia,
      tolerancia: config.toleranciaRelogioSegundos,
      typAceitos: ['at+jwt'],
      agora,
    }));
  } catch (erro) {
    if (erro instanceof ErroJwt) throw new ErroSessao(erro.codigo, erro.message);
    throw erro;
  }

  if (payload.jti && armazem.jtiEstaRevogado(payload.jti)) {
    throw new ErroSessao('token_revogado', 'este token foi revogado');
  }

  const usuario = armazem.usuarioPorId(payload.sub);
  if (!usuario) throw new ErroSessao('usuario_removido', 'usuario nao existe mais');

  return { payload, usuario };
}

/** Autorizacao por papel. Autenticacao diz quem e; autorizacao diz o que pode. */
export function exigirPapel(payload, papel) {
  if (!Array.isArray(payload.papeis) || !payload.papeis.includes(papel)) {
    throw new ErroSessao('sem_permissao', `esta operacao exige o papel "${papel}"`, 403);
  }
}
