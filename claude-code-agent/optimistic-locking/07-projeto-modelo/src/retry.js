// Retentativa com recuo exponencial e jitter.
//
// Optimistic locking sem política de retentativa transfere o problema para o usuário:
// ele vê "alguém editou antes de você" e desiste. Com retentativa, o conflito vira
// latência em vez de erro — MAS só quando a operação é reexecutável a partir do estado
// novo. Se a decisão do usuário depende do que ele leu ("aprovo este texto"),
// retentar automaticamente é errado: aí o conflito precisa subir até ele.

/**
 * @param {() => Promise<T>|T} fn operação a executar; deve reler o estado a cada tentativa
 * @param {object} opts
 * @param {number} opts.tentativas número máximo de execuções (não de retentativas)
 * @param {number} opts.baseMs atraso base
 * @param {number} opts.tetoMs teto do atraso
 * @param {(e:Error) => boolean} opts.retentavel decide se o erro merece nova tentativa
 * @param {() => number} opts.aleatorio injetável para tornar o teste determinístico
 */
export async function comRetentativa(fn, opts = {}) {
  const {
    tentativas = 5,
    baseMs = 5,
    tetoMs = 500,
    retentavel = (e) => e.name === 'ConflitoDeVersao',
    aleatorio = Math.random,
    dormir = (ms) => new Promise((r) => setTimeout(r, ms)),
  } = opts;

  let ultimoErro;
  for (let i = 0; i < tentativas; i++) {
    try {
      return { valor: await fn(i), tentativasGastas: i + 1 };
    } catch (e) {
      if (!retentavel(e) || i === tentativas - 1) throw e;
      ultimoErro = e;
      // Recuo exponencial com "full jitter": atraso sorteado em [0, teto_i].
      // Sem jitter, todos os clientes em conflito voltam ao mesmo tempo e colidem de novo
      // — é o efeito manada (thundering herd) que faz a taxa de conflito não cair.
      const teto = Math.min(tetoMs, baseMs * 2 ** i);
      await dormir(Math.floor(aleatorio() * teto));
    }
  }
  throw ultimoErro;
}
