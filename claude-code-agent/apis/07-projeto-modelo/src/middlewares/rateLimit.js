/**
 * Rate limiting por janela deslizante.
 *
 * Por que janela DESLIZANTE e não fixa: com janela fixa de 60 s, um cliente pode
 * fazer 100 chamadas no segundo 59 e mais 100 no segundo 61 — 200 em dois
 * segundos, dobrando o limite pretendido. A janela deslizante conta as chamadas
 * dos últimos 60 s a partir de agora, e não tem esse buraco.
 *
 * TODO(producao): este contador é por processo. Com N réplicas, o limite efetivo
 * vira N × limite. Em produção: Redis com script Lua atômico, ou o rate limit do
 * próprio gateway (que é onde ele idealmente deve ficar).
 */
import { Problemas } from '../problemas.js';

export function criarRateLimit({ limite = 100, janelaMs = 60_000 } = {}) {
  /** chave → array de timestamps (ms) */
  const registros = new Map();

  // Limpeza periódica: sem isto, o Map cresce para sempre com clientes que
  // apareceram uma vez. `unref` impede que este timer segure o processo vivo.
  const limpeza = setInterval(() => {
    const corte = Date.now() - janelaMs;
    for (const [chave, marcas] of registros) {
      const vivas = marcas.filter(t => t > corte);
      if (vivas.length === 0) registros.delete(chave);
      else registros.set(chave, vivas);
    }
  }, janelaMs).unref();

  return {
    /**
     * @param {string} chave  identidade do cliente (não use IP quando houver auth:
     *                        vários clientes atrás do mesmo NAT compartilhariam a cota)
     * @returns {{restante: number, resetEmS: number}}
     * @throws {Problema} 429
     */
    verificar(chave) {
      const agora = Date.now();
      const corte = agora - janelaMs;

      const marcas = (registros.get(chave) ?? []).filter(t => t > corte);

      if (marcas.length >= limite) {
        // Quando a requisição mais antiga sair da janela, abre uma vaga.
        const esperarS = Math.max(1, Math.ceil((marcas[0] + janelaMs - agora) / 1000));
        registros.set(chave, marcas);

        const problema = Problemas.limiteExcedido(limite, Math.round(janelaMs / 1000), esperarS);
        // O 429 PRECISA carregar os cabeçalhos de cota — é neles que o cliente
        // descobre quando pode voltar. Anexá-los aqui garante que eles saiam
        // mesmo quando a exceção corta o fluxo antes de o manipulador rodar.
        Object.assign(problema.cabecalhos,
          this.cabecalhos({ restante: 0, resetEmS: esperarS }));
        throw problema;
      }

      marcas.push(agora);
      registros.set(chave, marcas);

      return {
        restante: limite - marcas.length,
        resetEmS: Math.ceil((marcas[0] + janelaMs - agora) / 1000)
      };
    },

    /** Cabeçalhos informativos. O cliente educado os lê antes de estourar o limite. */
    cabecalhos({ restante, resetEmS }) {
      return {
        // Formato de facto, ainda o mais suportado por bibliotecas de cliente.
        'X-RateLimit-Limit': String(limite),
        'X-RateLimit-Remaining': String(restante),
        'X-RateLimit-Reset': String(Math.floor(Date.now() / 1000) + resetEmS),
        // Formato em padronização na IETF (draft-ietf-httpapi-ratelimit-headers).
        'RateLimit': `limit=${limite}, remaining=${restante}, reset=${resetEmS}`,
        'RateLimit-Policy': `${limite};w=${Math.round(janelaMs / 1000)}`
      };
    },

    parar: () => clearInterval(limpeza),
    _tamanho: () => registros.size
  };
}
