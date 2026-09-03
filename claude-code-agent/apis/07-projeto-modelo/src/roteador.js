/**
 * Roteador mínimo: casa método + padrão de caminho e extrai parâmetros.
 *
 * Um framework faria isto por você. Está aqui para você ver que roteamento é,
 * essencialmente, uma tabela de expressões regulares — e para o projeto rodar
 * sem `npm install`.
 */
import { Problemas } from './problemas.js';

/**
 * Converte "/livros/:id" numa regex com grupo nomeado.
 *
 * Nota: `/` NÃO é metacaractere de regex, então o escape abaixo não o toca —
 * por isso o segundo replace procura "/:" e não "\/:".
 */
function compilar(padrao) {
  const fonte = padrao
    .replace(/\/+$/, '')
    .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')            // escapa metacaracteres
    .replace(/\/:([A-Za-z_][A-Za-z0-9_]*)/g, '/(?<$1>[^/]+)');
  return new RegExp(`^${fonte || '/'}$`);
}

export function criarRoteador() {
  const rotas = [];

  const adicionar = (metodo, padrao, manipulador, opcoes = {}) => {
    rotas.push({ metodo, padrao, regex: compilar(padrao), manipulador, ...opcoes });
  };

  return {
    get:    (p, h, o) => adicionar('GET', p, h, o),
    post:   (p, h, o) => adicionar('POST', p, h, o),
    patch:  (p, h, o) => adicionar('PATCH', p, h, o),
    put:    (p, h, o) => adicionar('PUT', p, h, o),
    delete: (p, h, o) => adicionar('DELETE', p, h, o),

    /**
     * @returns {{manipulador, params, opcoes}}
     * @throws {Problema} 405 se o caminho existe mas o método não; 404 se não existe
     */
    resolver(metodo, caminho) {
      const normalizado = caminho.replace(/\/+$/, '') || '/';
      const casaCaminho = [];

      // RFC 9110 §9.3.2: todo recurso que aceita GET DEVE aceitar HEAD.
      // HEAD é o mesmo GET, sem corpo — quem escreve o manipulador não precisa
      // saber disso; a supressão do corpo acontece em http.js/responder().
      const alvo = metodo === 'HEAD' ? 'GET' : metodo;

      for (const rota of rotas) {
        const casa = rota.regex.exec(normalizado);
        if (!casa) continue;

        casaCaminho.push(rota.metodo);
        if (rota.metodo === 'GET') casaCaminho.push('HEAD');

        if (rota.metodo === alvo) {
          return { manipulador: rota.manipulador, params: casa.groups ?? {}, rota };
        }
      }

      if (casaCaminho.length > 0) {
        // O caminho existe, o método não. 405 + Allow é o correto — 404 aqui
        // esconderia do cliente que ele está quase certo.
        const permitidos = [...new Set([...casaCaminho, 'OPTIONS'])];
        throw Problemas.metodoNaoPermitido(metodo, permitidos);
      }
      throw Problemas.rotaNaoEncontrada(metodo, caminho);
    },

    /** Métodos permitidos num caminho — usado para responder a OPTIONS. */
    metodosDe(caminho) {
      const normalizado = caminho.replace(/\/+$/, '') || '/';
      const metodos = rotas.filter(r => r.regex.test(normalizado))
                           .flatMap(r => (r.metodo === 'GET' ? ['GET', 'HEAD'] : [r.metodo]));
      return [...new Set(metodos)];
    },

    /** Lista os pares método+padrão — usada pelo teste de cobertura do contrato. */
    listar: () => rotas.map(r => ({ metodo: r.metodo, padrao: r.padrao }))
  };
}
