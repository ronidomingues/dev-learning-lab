/**
 * Chaveiro: geracao, persistencia, publicacao em JWKS e rotacao.
 *
 * Por que assimetrico (ES256) e nao HMAC (HS256): com HMAC, quem verifica o
 * token tambem consegue emitir token. Se amanha um segundo servico precisar
 * validar, voce tera de entregar a ele o poder de forjar. Com ES256, o servico
 * de autenticacao guarda a chave privada e o mundo inteiro pode verificar com a
 * publica. Ver 14-assinatura-jws.md.
 *
 * Por que P-256 e nao RSA: assinatura de 64 bytes contra 256 bytes. Num token
 * que viaja em todo cabecalho HTTP, isso e o triplo do tamanho por requisicao.
 */

import { generateKeyPairSync, createPrivateKey, createPublicKey } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { thumbprintJwk } from './jwt.js';

export const ALG_DE_ASSINATURA = 'ES256';

/**
 * Um chaveiro tem:
 *  - `ativa`: a chave com que se ASSINA agora;
 *  - `todas`: todas as chaves com que ainda se VERIFICA.
 *
 * Essa separacao e o que torna a rotacao possivel sem derrubar ninguem:
 * troca-se a ativa e mantem-se a antiga em `todas` por, no minimo, o tempo de
 * vida do token mais longo que ela assinou.
 */
export class Chaveiro {
  constructor(chaves, kidAtiva) {
    this.chaves = new Map(chaves.map((c) => [c.kid, c]));
    this.kidAtiva = kidAtiva;
  }

  get ativa() {
    return this.chaves.get(this.kidAtiva);
  }

  /**
   * Resolve a chave publica de verificacao a partir do cabecalho do token.
   *
   * Repare no que NAO acontece aqui: o `kid` nao vira nome de arquivo, nao vira
   * consulta SQL, nao vira URL. Ele e so uma busca num Map de chaves que este
   * servico ja conhece. Um `kid` desconhecido devolve `null`, e a verificacao
   * falha. Ver 20-ataques-e-defesas.md, secao "injecao por kid".
   */
  publicaPara(cabecalho) {
    const registro = cabecalho.kid ? this.chaves.get(cabecalho.kid) : this.ativa;
    return registro ? registro.publica : null;
  }

  /** Documento JWKS (RFC 7517) para publicar em /.well-known/jwks.json */
  jwks() {
    return {
      keys: [...this.chaves.values()].map((registro) => ({
        ...registro.jwkPublico,
        kid: registro.kid,
        use: 'sig',
        alg: ALG_DE_ASSINATURA,
      })),
    };
  }
}

/** Gera um par EC P-256 e devolve o registro completo do chaveiro. */
export function gerarChave() {
  const { privateKey, publicKey } = generateKeyPairSync('ec', { namedCurve: 'P-256' });
  const jwkPublico = publicKey.export({ format: 'jwk' });
  return {
    kid: thumbprintJwk(jwkPublico),
    privada: privateKey,
    publica: publicKey,
    jwkPublico,
  };
}

/**
 * Carrega o chaveiro do disco; se nao existir, gera e salva.
 *
 * A chave privada e gravada em PKCS#8 PEM sem senha, com permissao 0600.
 * Em producao isso vira um segredo do orquestrador (Kubernetes Secret, AWS
 * Secrets Manager, Vault) ou, melhor, uma chave que nunca sai de um HSM/KMS
 * — o servico manda o dado para assinar e recebe a assinatura de volta.
 * Ver 22-operacao-em-producao.md.
 */
export function carregarOuCriarChaveiro(caminhoArquivo) {
  if (existsSync(caminhoArquivo)) {
    const bruto = JSON.parse(readFileSync(caminhoArquivo, 'utf8'));
    const chaves = bruto.chaves.map((c) => {
      const privada = createPrivateKey(c.pem);
      const publica = createPublicKey(privada);
      return { kid: c.kid, privada, publica, jwkPublico: publica.export({ format: 'jwk' }) };
    });
    return new Chaveiro(chaves, bruto.kidAtiva);
  }

  const chave = gerarChave();
  mkdirSync(dirname(caminhoArquivo), { recursive: true });
  salvar(caminhoArquivo, [chave], chave.kid);
  return new Chaveiro([chave], chave.kid);
}

/**
 * Rotaciona: gera uma chave nova, torna-a ativa, e MANTEM a antiga para
 * verificacao. O erro classico de rotacao e apagar a antiga no mesmo instante
 * — todo token vivo emitido por ela vira invalido e o suporte recebe uma onda
 * de "fui deslogado do nada".
 */
export function rotacionar(chaveiro, caminhoArquivo) {
  const nova = gerarChave();
  chaveiro.chaves.set(nova.kid, nova);
  chaveiro.kidAtiva = nova.kid;
  salvar(caminhoArquivo, [...chaveiro.chaves.values()], nova.kid);
  return nova.kid;
}

/** Aposenta uma chave: so faca isso depois de expirar o ultimo token dela. */
export function aposentar(chaveiro, kid, caminhoArquivo) {
  if (kid === chaveiro.kidAtiva) throw new Error('nao se aposenta a chave ativa; rotacione antes');
  chaveiro.chaves.delete(kid);
  salvar(caminhoArquivo, [...chaveiro.chaves.values()], chaveiro.kidAtiva);
}

function salvar(caminhoArquivo, chaves, kidAtiva) {
  const conteudo = {
    kidAtiva,
    chaves: chaves.map((c) => ({
      kid: c.kid,
      pem: c.privada.export({ type: 'pkcs8', format: 'pem' }),
    })),
  };
  writeFileSync(caminhoArquivo, JSON.stringify(conteudo, null, 2), { mode: 0o600 });
}

export const CAMINHO_PADRAO = join(process.cwd(), 'dados', 'chaveiro.json');
