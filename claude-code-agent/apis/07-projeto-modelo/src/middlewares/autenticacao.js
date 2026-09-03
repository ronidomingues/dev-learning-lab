/**
 * Autenticação por Bearer token opaco + autorização por escopo.
 *
 * Token OPACO (uma string sem significado) em vez de JWT, de propósito:
 *  - revogação é imediata (basta apagar do registro);
 *  - não vaza informação se for lido;
 *  - o custo é uma consulta por requisição — aceitável, e cacheável.
 * JWT vale a pena quando a verificação precisa ser possível SEM consultar o
 * emissor. Ver 16-seguranca.md §4.
 */
import { createHash, timingSafeEqual } from 'node:crypto';
import { Problemas } from '../problemas.js';

/** Guardamos o HASH do token, nunca o token. Igual a senha. */
const hash = t => createHash('sha256').update(t, 'utf8').digest();

/**
 * Em produção, isto vem de um banco e os tokens são criados por um endpoint
 * de administração. Os de demonstração só existem fora de produção.
 */
export function criarRegistroDeTokens({ producao = false } = {}) {
  const porHash = new Map();

  function registrar(token, identidade, escopos) {
    porHash.set(hash(token).toString('base64'), {
      identidade, escopos: new Set(escopos), token_hash: hash(token)
    });
  }

  if (!producao) {
    registrar('tok_leitor_demo', 'leitor',
              ['livros:ler', 'emprestimos:ler']);
    registrar('tok_biblio_demo', 'bibliotecario',
              ['livros:ler', 'livros:escrever', 'emprestimos:ler', 'emprestimos:escrever']);
  }

  const extras = (process.env.API_TOKENS ?? '').trim();
  if (extras) {
    // Formato: "token:identidade:escopo1|escopo2,token2:..."
    for (const linha of extras.split(',')) {
      const [tok, ident, escopos] = linha.split(':');
      if (tok && ident) registrar(tok, ident, (escopos ?? '').split('|').filter(Boolean));
    }
  }

  return {
    /**
     * @returns {{identidade: string, escopos: Set<string>}}
     * @throws {Problema} 401 se ausente ou inválido
     */
    autenticar(req) {
      const cabecalho = req.headers.authorization;
      if (!cabecalho) throw Problemas.naoAutenticado();

      const [esquema, valor] = cabecalho.split(' ');
      if (esquema?.toLowerCase() !== 'bearer' || !valor) {
        throw Problemas.naoAutenticado('O esquema deve ser Bearer.');
      }

      const candidato = hash(valor);
      // Percorremos TODOS os registros comparando em tempo constante.
      // Um `Map.get` puro seria mais rápido, mas o tempo de resposta passaria a
      // depender do token enviado — canal lateral clássico. Com dezenas de
      // clientes o custo é irrelevante; com milhares, use um índice + comparação
      // constante só do candidato encontrado.
      let achado = null;
      for (const registro of porHash.values()) {
        if (registro.token_hash.length === candidato.length &&
            timingSafeEqual(registro.token_hash, candidato)) {
          achado = registro;
        }
      }
      if (!achado) throw Problemas.tokenInvalido();

      return { identidade: achado.identidade, escopos: achado.escopos };
    },

    /** @throws {Problema} 403 se o escopo não estiver presente */
    exigirEscopo(principal, escopo) {
      if (!principal.escopos.has(escopo)) {
        throw Problemas.escopoInsuficiente(escopo);
      }
    },

    _quantidade: () => porHash.size
  };
}
