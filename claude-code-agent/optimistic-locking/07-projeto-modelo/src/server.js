// Servidor HTTP sem framework. Expõe o optimistic locking do repositório
// na forma que a web padronizou: ETag + If-Match + 412/428.

import http from 'node:http';
import { abrirBanco, semear } from './db.js';
import {
  buscar,
  atualizar,
  atualizarInseguro,
  baixarEstoque,
  ConflitoDeVersao,
  NaoEncontrado,
  EstoqueInsuficiente,
} from './repo.js';

// ---------------------------------------------------------------------------
// ETag
//
// O ETag é o token de versão viajando pelo protocolo. Aqui ele é literalmente a
// coluna `version`, mas poderia ser um hash do corpo — veja 13-tokens-de-versao.md.
//
// ATENÇÃO a um detalhe que derruba integrações reais: a RFC 9110 manda comparar
// `If-Match` com comparação FORTE. Um ETag fraco (`W/"3"`) NUNCA casa com If-Match.
// Por isso emitimos ETag forte: `"3"`, sem o prefixo `W/`.
// ---------------------------------------------------------------------------
export const etagDe = (produto) => `"${produto.version}"`;

/** Interpreta um cabeçalho If-Match. Aceita `"3"`, lista `"1", "2"`, `*`; recusa `W/"3"`. */
export function versaoDoIfMatch(cabecalho) {
  if (cabecalho === undefined || cabecalho === null || cabecalho === '') return { tipo: 'ausente' };
  const bruto = String(cabecalho).trim();
  if (bruto === '*') return { tipo: 'curinga' };
  if (bruto.startsWith('W/')) return { tipo: 'fraco' };
  const versoes = bruto
    .split(',')
    .map((s) => s.trim())
    .filter((s) => /^"\d+"$/.test(s))
    .map((s) => Number(s.slice(1, -1)));
  if (versoes.length === 0) return { tipo: 'malformado' };
  return { tipo: 'ok', versoes };
}

const json = (res, status, corpo, cabecalhos = {}) => {
  const texto = JSON.stringify(corpo, null, 2);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(texto),
    ...cabecalhos,
  });
  res.end(texto);
};

async function lerCorpo(req) {
  const partes = [];
  for await (const p of req) partes.push(p);
  if (partes.length === 0) return {};
  try {
    return JSON.parse(Buffer.concat(partes).toString('utf8'));
  } catch {
    const e = new Error('JSON inválido');
    e.name = 'CorpoInvalido';
    throw e;
  }
}

/** Cria o servidor sobre um banco já aberto. Fábrica separada para o teste poder injetar. */
export function criarServidor(db) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://${req.headers.host ?? 'localhost'}`);
    const partes = url.pathname.split('/').filter(Boolean);

    try {
      // GET /produtos/:id
      if (req.method === 'GET' && partes[0] === 'produtos' && partes.length === 2) {
        const p = buscar(db, Number(partes[1]));
        return json(res, 200, p, { etag: etagDe(p) });
      }

      // GET /auditoria/:id  — prova de que nenhuma escrita se perdeu
      if (req.method === 'GET' && partes[0] === 'auditoria' && partes.length === 2) {
        const linhas = db
          .prepare('SELECT * FROM auditoria WHERE produto_id = ? ORDER BY id')
          .all(Number(partes[1]));
        return json(res, 200, linhas.map((l) => ({ ...l })));
      }

      // PUT /produtos/:id  — o caminho protegido
      if (req.method === 'PUT' && partes[0] === 'produtos' && partes.length === 2) {
        const id = Number(partes[1]);
        const cond = versaoDoIfMatch(req.headers['if-match']);

        // 428: o servidor EXIGE a pré-condição. Sem isso, um cliente distraído
        // sobrescreve tudo em silêncio — e o servidor teria sido cúmplice.
        if (cond.tipo === 'ausente') {
          return json(res, 428, {
            erro: 'precondicao_obrigatoria',
            detalhe: 'envie If-Match com o ETag obtido no GET',
          });
        }
        if (cond.tipo === 'fraco') {
          return json(res, 400, {
            erro: 'etag_fraco',
            detalhe: 'If-Match exige comparação forte (RFC 9110); não use W/',
          });
        }
        if (cond.tipo === 'malformado') {
          return json(res, 400, { erro: 'if_match_malformado' });
        }

        const corpo = await lerCorpo(req);
        const autor = String(req.headers['x-autor'] ?? 'anon');

        if (cond.tipo === 'curinga') {
          // `If-Match: *` significa apenas "o recurso precisa existir".
          // Não protege contra lost update; aceitamos, mas avisamos.
          const atual = buscar(db, id);
          const p = atualizar(db, id, atual.version, corpo, autor);
          return json(res, 200, p, { etag: etagDe(p), 'x-aviso': 'if-match-curinga-nao-protege' });
        }

        let ultimo;
        for (const v of cond.versoes) {
          try {
            const p = atualizar(db, id, v, corpo, autor);
            return json(res, 200, p, { etag: etagDe(p) });
          } catch (e) {
            if (e.name !== 'ConflitoDeVersao') throw e;
            ultimo = e;
          }
        }
        throw ultimo;
      }

      // PUT /inseguro/produtos/:id — só para a demonstração do bug
      if (req.method === 'PUT' && partes[0] === 'inseguro' && partes[1] === 'produtos') {
        const corpo = await lerCorpo(req);
        const p = atualizarInseguro(db, Number(partes[2]), corpo);
        return json(res, 200, p, { etag: etagDe(p) });
      }

      // POST /produtos/:id/baixa — delta atômico, sem versão (de propósito)
      if (req.method === 'POST' && partes[0] === 'produtos' && partes[2] === 'baixa') {
        const corpo = await lerCorpo(req);
        const p = baixarEstoque(db, Number(partes[1]), Number(corpo.qtd));
        return json(res, 200, p, { etag: etagDe(p) });
      }

      return json(res, 404, { erro: 'rota_inexistente' });
    } catch (e) {
      if (e instanceof ConflitoDeVersao) {
        // 412 Precondition Failed é a resposta certa. Devolvemos o estado atual e o
        // ETag novo para o cliente conseguir fazer merge sem um GET adicional.
        return json(
          res,
          412,
          {
            erro: 'conflito_de_versao',
            versao_enviada: e.versaoEsperada,
            versao_atual: e.versaoAtual,
            atual: e.registroAtual,
          },
          { etag: `"${e.versaoAtual}"` }
        );
      }
      if (e instanceof NaoEncontrado) return json(res, 404, { erro: 'nao_encontrado' });
      if (e instanceof EstoqueInsuficiente) {
        return json(res, 409, { erro: 'estoque_insuficiente', detalhe: e.message });
      }
      if (e.name === 'CorpoInvalido' || e instanceof TypeError) {
        return json(res, 400, { erro: 'requisicao_invalida', detalhe: e.message });
      }
      return json(res, 500, { erro: 'erro_interno', detalhe: e.message });
    }
  });
}

// Só sobe a porta quando executado diretamente (`node src/server.js`),
// nunca quando importado por um teste.
if (import.meta.url === `file://${process.argv[1]}`) {
  const PORTA = Number(process.env.PORTA ?? 3000);
  const CAMINHO_DB = process.env.DB ?? ':memory:';
  const db = abrirBanco(CAMINHO_DB);
  semear(db);
  criarServidor(db).listen(PORTA, () => {
    console.log(`catálogo otimista em http://localhost:${PORTA} (db: ${CAMINHO_DB})`);
  });
}
