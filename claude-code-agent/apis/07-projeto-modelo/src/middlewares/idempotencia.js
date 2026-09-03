/**
 * Idempotência para POST, via cabeçalho `Idempotency-Key`.
 *
 * O problema que isto resolve: a rede cai DEPOIS de o servidor processar e ANTES
 * de a resposta chegar. O cliente não sabe se deu certo, retenta, e o efeito
 * acontece duas vezes. Sem idempotência, é questão de tempo até duplicar.
 *
 * TODO(producao): este registro vive em memória. Com N réplicas, cada uma tem o
 * seu e a garantia some. Em produção: Redis com TTL, ou uma tabela com
 * constraint UNIQUE na chave — a garantia precisa estar no ARMAZENAMENTO, não
 * no código, porque entre um "select" e um "insert" existe uma janela que a
 * concorrência encontra. Ver 60-teoria-avancada.md §4.
 */
import { createHash } from 'node:crypto';
import { Problemas } from '../problemas.js';

export function criarIdempotencia({ janelaMs = 24 * 60 * 60 * 1000 } = {}) {
  /** chave → { impressao, status, corpo, cabecalhos, expiraEm, emAndamento } */
  const registros = new Map();

  const limpeza = setInterval(() => {
    const agora = Date.now();
    for (const [chave, r] of registros) {
      if (r.expiraEm <= agora) registros.delete(chave);
    }
  }, 60 * 60 * 1000).unref();

  const impressaoDe = (metodo, caminho, corpo) =>
    createHash('sha256')
      .update(`${metodo} ${caminho} ${JSON.stringify(corpo ?? null)}`)
      .digest('base64url');

  return {
    /**
     * Consulta antes de processar.
     * @returns {null | {status, corpo, cabecalhos}} resposta guardada, se houver
     * @throws {Problema} 400 se a chave faltar; 422 se for reusada com outro corpo;
     *                    409 se houver uma requisição igual em andamento
     */
    consultar(req, caminho, corpo, { obrigatoria = true } = {}) {
      const chave = req.headers['idempotency-key'];

      if (!chave) {
        if (obrigatoria) throw Problemas.chaveIdempotenciaAusente();
        return null;
      }
      if (typeof chave !== 'string' || chave.length < 8 || chave.length > 200) {
        throw Problemas.parametroInvalido('Idempotency-Key',
          'deve ter entre 8 e 200 caracteres (use um UUID)');
      }

      const registro = registros.get(chave);
      if (!registro || registro.expiraEm <= Date.now()) return null;

      const impressao = impressaoDe(req.method, caminho, corpo);
      if (registro.impressao !== impressao) {
        // O cliente reusou a chave para outra operação. É bug dele, e é grave:
        // sem esta checagem, devolveríamos a resposta da operação ERRADA.
        throw Problemas.chaveIdempotenciaReusada();
      }

      if (registro.emAndamento) {
        // Duas retentativas chegaram juntas. A segunda espera, não duplica.
        throw Problemas.conflito(
          'Uma requisição com esta Idempotency-Key ainda está em processamento. Tente em instantes.',
          { idempotency_key: chave });
      }

      return { status: registro.status, corpo: registro.corpo, cabecalhos: registro.cabecalhos };
    },

    /** Marca a chave como "sendo processada agora". */
    reservar(req, caminho, corpo) {
      const chave = req.headers['idempotency-key'];
      if (!chave) return;
      registros.set(chave, {
        impressao: impressaoDe(req.method, caminho, corpo),
        emAndamento: true,
        expiraEm: Date.now() + janelaMs
      });
    },

    /** Guarda a resposta para as retentativas futuras. */
    guardar(req, status, corpo, cabecalhos = {}) {
      const chave = req.headers['idempotency-key'];
      if (!chave) return;
      const registro = registros.get(chave);
      if (!registro) return;
      registros.set(chave, { ...registro, emAndamento: false, status, corpo, cabecalhos });
    },

    /** Libera a chave quando o processamento falhou — para o cliente poder retentar. */
    liberar(req) {
      const chave = req.headers['idempotency-key'];
      if (chave) registros.delete(chave);
    },

    parar: () => clearInterval(limpeza),
    _tamanho: () => registros.size
  };
}
