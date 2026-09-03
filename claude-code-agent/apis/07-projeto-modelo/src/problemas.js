/**
 * Catálogo de erros no formato RFC 9457 (Problem Details for HTTP APIs).
 *
 * Regra do contrato: o cliente programa contra `type` (URI estável e documentada).
 * `title` e `detail` são para humanos e PODEM mudar — inclusive por tradução.
 */

const BASE = 'https://exemplo.com/problemas';

export class Problema extends Error {
  /**
   * @param {number} status  código HTTP
   * @param {string} tipo    sufixo da URI de tipo
   * @param {string} titulo  resumo estável
   * @param {string} detalhe explicação desta ocorrência
   * @param {object} extras  campos adicionais do tipo
   * @param {object} cabecalhos cabeçalhos HTTP que este erro exige
   */
  constructor(status, tipo, titulo, detalhe, extras = {}, cabecalhos = {}) {
    super(detalhe ?? titulo);
    this.name = 'Problema';
    this.status = status;
    this.type = `${BASE}/${tipo}`;
    this.title = titulo;
    this.detail = detalhe;
    this.extras = extras;
    this.cabecalhos = cabecalhos;
  }

  paraCorpo(requestId) {
    return {
      type: this.type,
      title: this.title,
      status: this.status,
      detail: this.detail,
      instance: `/requisicoes/${requestId}`,
      ...this.extras
    };
  }
}

export const Problemas = {
  // ---- 400 ----
  jsonInvalido: motivo => new Problema(
    400, 'json-invalido', 'JSON invalido',
    `O corpo não é JSON válido: ${motivo}`),

  parametroInvalido: (nome, motivo) => new Problema(
    400, 'parametro-invalido', 'Parametro invalido',
    `O parâmetro "${nome}" é inválido: ${motivo}`, { parametro: nome }),

  cursorInvalido: () => new Problema(
    400, 'cursor-invalido', 'Cursor invalido',
    'O cursor enviado não é válido. Use o valor de "proximo_cursor" da resposta anterior.'),

  // ---- 401 / 403 ----
  naoAutenticado: motivo => new Problema(
    401, 'nao-autenticado', 'Nao autenticado',
    motivo ?? 'Envie o cabeçalho Authorization: Bearer <token>.',
    {}, { 'WWW-Authenticate': 'Bearer realm="api"' }),

  tokenInvalido: () => new Problema(
    401, 'token-invalido', 'Token invalido',
    'O token enviado não é reconhecido ou expirou.',
    {}, { 'WWW-Authenticate': 'Bearer realm="api", error="invalid_token"' }),

  escopoInsuficiente: necessario => new Problema(
    403, 'escopo-insuficiente', 'Escopo insuficiente',
    `Esta operação exige o escopo "${necessario}".`,
    { escopo_necessario: necessario },
    { 'WWW-Authenticate': `Bearer realm="api", error="insufficient_scope", scope="${necessario}"` }),

  // ---- 404 / 405 / 406 ----
  naoEncontrado: (tipo, id) => new Problema(
    404, 'nao-encontrado', 'Recurso nao encontrado',
    `${tipo} com identificador "${id}" não existe.`),

  rotaNaoEncontrada: (metodo, caminho) => new Problema(
    404, 'rota-nao-encontrada', 'Rota nao encontrada',
    `Nada responde a ${metodo} ${caminho}.`),

  metodoNaoPermitido: (metodo, permitidos) => new Problema(
    405, 'metodo-nao-permitido', 'Metodo nao permitido',
    `${metodo} não é permitido aqui. Permitidos: ${permitidos.join(', ')}.`,
    { permitidos }, { Allow: permitidos.join(', ') }),

  naoAceitavel: aceitos => new Problema(
    406, 'nao-aceitavel', 'Formato nao suportado',
    `Não consigo produzir o formato pedido. Aceito: ${aceitos.join(', ')}.`),

  // ---- 409 / 412 / 413 / 415 / 422 / 428 ----
  conflito: (motivo, extras = {}) => new Problema(
    409, 'conflito', 'Conflito de estado', motivo, extras),

  livroIndisponivel: (id) => new Problema(
    409, 'livro-indisponivel', 'Livro indisponivel',
    `O livro "${id}" já está emprestado.`, { livro_id: id }),

  isbnDuplicado: isbn => new Problema(
    409, 'isbn-duplicado', 'ISBN ja cadastrado',
    `Já existe um livro com o ISBN ${isbn}.`, { isbn }),

  precondicaoFalhou: etagAtual => new Problema(
    412, 'precondicao-falhou', 'Precondicao falhou',
    'O recurso foi alterado por outra pessoa desde a sua leitura. Releia e tente de novo.',
    { etag_atual: etagAtual }, { ETag: etagAtual }),

  corpoGrandeDemais: limite => new Problema(
    413, 'corpo-grande-demais', 'Corpo grande demais',
    `O corpo excede o limite de ${limite} bytes.`, { limite_bytes: limite }),

  tipoNaoSuportado: esperado => new Problema(
    415, 'tipo-nao-suportado', 'Tipo de midia nao suportado',
    `Envie Content-Type: ${esperado}.`, {},
    { 'Accept-Post': esperado }),

  validacao: erros => new Problema(
    422, 'validacao', 'Dados invalidos',
    'Um ou mais campos não passaram na validação.', { erros }),

  precondicaoObrigatoria: () => new Problema(
    428, 'precondicao-obrigatoria', 'Precondicao obrigatoria',
    'Esta operação exige If-Match. Faça um GET, pegue o ETag e envie-o.'),

  chaveIdempotenciaAusente: () => new Problema(
    400, 'chave-idempotencia-ausente', 'Idempotency-Key obrigatorio',
    'Envie o cabeçalho Idempotency-Key com um identificador único desta operação.'),

  chaveIdempotenciaReusada: () => new Problema(
    422, 'chave-idempotencia-reusada', 'Chave de idempotencia reutilizada',
    'Esta Idempotency-Key já foi usada com um corpo diferente.'),

  // ---- 429 ----
  limiteExcedido: (limite, janelaS, esperarS) => new Problema(
    429, 'limite-excedido', 'Limite de requisicoes excedido',
    `Você excedeu ${limite} requisições em ${janelaS} segundos.`,
    { limite, janela_segundos: janelaS, tentar_em_segundos: esperarS },
    { 'Retry-After': String(esperarS) }),

  // ---- 500 ----
  erroInterno: () => new Problema(
    500, 'erro-interno', 'Erro interno',
    'Ocorreu um erro inesperado. Informe o identificador da requisição ao suporte.')
};
