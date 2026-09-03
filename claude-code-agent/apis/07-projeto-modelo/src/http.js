/**
 * Utilidades de HTTP: ler o corpo com segurança, negociar formato, responder.
 */
import { createHash } from 'node:crypto';
import { Problema, Problemas } from './problemas.js';
import { log } from './log.js';

export const LIMITE_CORPO_BYTES = Number(process.env.LIMITE_CORPO_BYTES ?? 256 * 1024);

/**
 * Lê o corpo da requisição com limite de tamanho.
 *
 * O limite não é zelo excessivo: sem ele, um cliente que envie um corpo de 2 GB
 * faz o processo consumir 2 GB de memória e morrer. É negação de serviço trivial.
 */
export async function lerCorpo(req, limite = LIMITE_CORPO_BYTES) {
  const partes = [];
  let total = 0;

  for await (const parte of req) {
    total += parte.length;
    if (total > limite) {
      // Paramos de acumular e deixamos o socket vivo: destruí-lo aqui faria o
      // cliente receber ECONNRESET em vez do 413, e ele nunca saberia o motivo.
      // O custo é continuar drenando bytes que serão descartados — aceitável,
      // porque o servidor à frente (proxy/gateway) normalmente já corta antes.
      partes.length = 0;
      throw Problemas.corpoGrandeDemais(limite);
    }
    partes.push(parte);
  }
  return total === 0 ? null : Buffer.concat(partes);
}

/** Lê e desserializa o corpo como JSON, exigindo o Content-Type correto. */
export async function lerJSON(req) {
  const tipo = (req.headers['content-type'] ?? '').split(';')[0].trim().toLowerCase();
  if (tipo && tipo !== 'application/json') {
    throw Problemas.tipoNaoSuportado('application/json');
  }
  const bruto = await lerCorpo(req);
  if (bruto === null) return null;
  try {
    return JSON.parse(bruto.toString('utf8'));
  } catch (e) {
    throw Problemas.jsonInvalido(e.message);
  }
}

/**
 * Negociação de conteúdo simplificada.
 * Aceita "application/json", "application/*", "*∕*" e ausência do cabeçalho.
 */
export function aceitaJSON(req) {
  const accept = req.headers.accept;
  if (!accept) return true;
  return accept.split(',').some(parte => {
    const tipo = parte.split(';')[0].trim().toLowerCase();
    return tipo === 'application/json' || tipo === 'application/*' || tipo === '*/*';
  });
}

/** ETag forte derivado do CONTEÚDO — estável entre réplicas e entre reinícios. */
export function etagDe(objeto) {
  const canonico = JSON.stringify(objeto, Object.keys(objeto).sort());
  return `"${createHash('sha256').update(canonico).digest('base64url').slice(0, 22)}"`;
}

/** Compara um If-None-Match / If-Match com o ETag atual (aceita lista e `*`). */
export function etagCasa(cabecalho, etagAtual) {
  if (!cabecalho) return false;
  if (cabecalho.trim() === '*') return true;
  return cabecalho.split(',')
    .map(e => e.trim().replace(/^W\//, ''))
    .includes(etagAtual.replace(/^W\//, ''));
}

/**
 * Envia uma resposta JSON.
 *
 * Padrão seguro: `Cache-Control: no-store`. Rotas que PODEM ser cacheadas dizem
 * isso explicitamente. O contrário — cachear por padrão — já vazou dado de um
 * usuário para outro em incidentes reais.
 */
export function responder(res, status, corpo, cabecalhos = {}) {
  const texto = corpo === null || status === 204 ? '' : JSON.stringify(corpo);

  const finais = {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    // Defesa contra content sniffing: o navegador não deve adivinhar o tipo.
    'X-Content-Type-Options': 'nosniff',
    ...cabecalhos
  };
  if (texto) finais['Content-Length'] = Buffer.byteLength(texto);
  else delete finais['Content-Type'];

  // Toda resposta que varia por identidade PRECISA disto, senão um cache
  // compartilhado entrega os dados de um cliente para outro.
  if (finais['Cache-Control'] !== 'no-store') {
    finais.Vary = finais.Vary ? `${finais.Vary}, Authorization` : 'Authorization';
  }

  res.writeHead(status, finais);
  // HEAD devolve os MESMOS cabeçalhos do GET (incluindo Content-Length), mas sem
  // corpo — RFC 9110 §9.3.2. É o que permite ao cliente checar tamanho, ETag ou
  // existência de um recurso sem baixá-lo.
  res.end(res.req?.method === 'HEAD' ? undefined : texto);
}

/** Envia um erro RFC 9457, com os cabeçalhos que aquele status exige. */
export function responderProblema(res, problema, requestId) {
  const corpo = JSON.stringify(problema.paraCorpo(requestId));
  res.writeHead(problema.status, {
    'Content-Type': 'application/problem+json; charset=utf-8',
    'Content-Length': Buffer.byteLength(corpo),
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'X-Request-Id': requestId,
    ...problema.cabecalhos
  });
  res.end(corpo);
}

/**
 * Converte qualquer erro numa resposta.
 * Erros de domínio (Problema) viram a resposta correspondente; o resto vira 500
 * com mensagem genérica — a stack trace fica no log, nunca na resposta.
 */
export function tratarErro(res, erro, requestId, registrador = log) {
  if (erro instanceof Problema) {
    if (erro.status >= 500) {
      registrador.error('problema de servidor', { status: erro.status, type: erro.type });
    } else {
      registrador.info('problema de cliente', { status: erro.status, type: erro.type });
    }
    return responderProblema(res, erro, requestId);
  }

  registrador.error('erro nao tratado', {
    erro: erro?.message,
    stack: erro?.stack?.split('\n').slice(0, 5).join(' | ')
  });
  responderProblema(res, Problemas.erroInterno(), requestId);
}

/** Cursor opaco: o cliente não deve depender do formato interno. */
export const cursor = {
  codificar: id => Buffer.from(String(id), 'utf8').toString('base64url'),
  decodificar(valor) {
    if (!valor) return null;
    try {
      const bruto = Buffer.from(valor, 'base64url').toString('utf8');
      if (!bruto) throw new Error('vazio');
      return bruto;
    } catch {
      throw Problemas.cursorInvalido();
    }
  }
};

/** Lê e valida um parâmetro inteiro da query string. */
export function inteiroDaQuery(url, nome, { padrao, minimo, maximo }) {
  const cru = url.searchParams.get(nome);
  if (cru === null || cru === '') return padrao;

  const n = Number(cru);
  if (!Number.isInteger(n)) {
    throw Problemas.parametroInvalido(nome, 'deve ser um número inteiro');
  }
  if (n < minimo || n > maximo) {
    throw Problemas.parametroInvalido(nome, `deve estar entre ${minimo} e ${maximo}`);
  }
  return n;
}
