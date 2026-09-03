/**
 * config.mjs — a ÚNICA porta de entrada da configuração desta aplicação.
 *
 * Regra da casa: nenhum outro arquivo pode ler `process.env`.
 * Se você precisa de um valor novo, ele entra aqui, no `.env.example` e nos testes.
 *
 * O que este módulo demonstra (é o coração do curso):
 *   1. lê do AMBIENTE, nunca de um arquivo `.env` diretamente — quem carrega o `.env`
 *      é o runtime (`node --env-file-if-exists`), e só em desenvolvimento;
 *   2. aceita `NOME` ou `NOME_FILE` (padrão de fato do Docker/Kubernetes), o que
 *      permite rotação de segredo sem reiniciar e evita que o valor apareça em
 *      `docker inspect` e em `/proc/<pid>/environ`;
 *   3. valida TUDO na inicialização e reporta TODOS os erros de uma vez;
 *   4. encerra com código 78 (EX_CONFIG do sysexits.h), para o orquestrador
 *      distinguir "configuração errada" de "erro transitório";
 *   5. congela o resultado — configuração não muda em tempo de execução;
 *   6. oferece uma visão mascarada, para log e para a rota de diagnóstico.
 *
 * `criarConfig` é uma função PURA (recebe o ambiente, devolve o resultado):
 * é isso que torna a configuração testável sem subir processo a cada caso.
 */
import { readFileSync } from 'node:fs';

// ── validadores reutilizáveis ──────────────────────────────────────────────
export const v = {
  url: (esquemas) => (valor) => {
    let u;
    try {
      u = new URL(valor);
    } catch {
      return 'não é uma URL válida';
    }
    const esquema = u.protocol.replace(':', '');
    if (esquemas && !esquemas.includes(esquema)) {
      return `esquema deve ser um de ${esquemas.join(', ')} (veio "${esquema}")`;
    }
    return undefined;
  },
  inteiro: (min, max) => (valor) =>
    /^\d+$/.test(valor) && Number(valor) >= min && Number(valor) <= max
      ? undefined
      : `esperado inteiro entre ${min} e ${max}`,
  umDe: (...opcoes) => (valor) =>
    opcoes.includes(valor) ? undefined : `esperado um de ${opcoes.join(', ')}`,
  minimo: (n) => (valor) =>
    valor.length >= n ? undefined : `precisa ter ao menos ${n} caracteres (tem ${valor.length})`,
  booleano: (valor) =>
    ['true', 'false'].includes(valor) ? undefined : 'esperado "true" ou "false"',
};

/** Valor de exemplo do .env.example — recusado em produção. */
export const SEGREDO_DE_EXEMPLO = 'desenvolvimento-apenas-troque-isto-em-producao';

/** Chaves do resultado que são segredo: mascaradas em log e em /config. */
export const CHAVES_SECRETAS = Object.freeze(['sessionSecret', 'apiKey', 'databaseUrl']);

/**
 * Constrói e valida a configuração a partir de um objeto de ambiente.
 * @param {Record<string,string|undefined>} env  normalmente `process.env`
 * @param {(caminho:string)=>string} lerArquivo  injetável para teste
 * @returns {{config: object, problemas: string[]}}
 */
export function criarConfig(env = process.env, lerArquivo = (p) => readFileSync(p, 'utf8')) {
  const problemas = [];

  /** Lê NOME do ambiente, ou o conteúdo do arquivo apontado por NOME_FILE. */
  const ler = (nome) => {
    const caminho = env[`${nome}_FILE`];
    if (caminho) {
      try {
        return lerArquivo(caminho).trim();
      } catch (e) {
        problemas.push(`${nome}_FILE aponta para "${caminho}", que não pôde ser lido (${e.code ?? e.message})`);
        return undefined;
      }
    }
    const valor = env[nome];
    // string vazia conta como ausente: é o caso comum de EnvironmentFile mal preenchido
    return valor === undefined || valor === '' ? undefined : valor;
  };

  const exigido = (nome, validar) => {
    const valor = ler(nome);
    if (valor === undefined) {
      problemas.push(`falta ${nome}`);
      return undefined;
    }
    const msg = validar?.(valor);
    if (msg) {
      problemas.push(`${nome}: ${msg}`);
      return undefined;
    }
    return valor;
  };

  const opcional = (nome, padrao, validar) => {
    const valor = ler(nome);
    if (valor === undefined) return padrao;
    const msg = validar?.(valor);
    if (msg) {
      problemas.push(`${nome}: ${msg}`);
      return padrao;
    }
    return valor;
  };

  // ── o CONTRATO da aplicação ──────────────────────────────────────────────
  // Espelhe qualquer alteração aqui no .env.example — há um teste que cobra isso.
  const bruta = {
    ambiente: opcional('NODE_ENV', 'development', v.umDe('development', 'test', 'production')),
    porta: opcional('PORT', '3000', v.inteiro(1, 65535)),
    logLevel: opcional('LOG_LEVEL', 'info', v.umDe('debug', 'info', 'warn', 'error')),
    databaseUrl: exigido('DATABASE_URL', v.url(['postgres', 'postgresql', 'memory'])),
    sessionSecret: exigido('SESSION_SECRET', v.minimo(32)),
    apiKey: exigido('API_KEY', v.minimo(8)),
    maxRecados: opcional('MAX_RECADOS', '100', v.inteiro(1, 100000)),
    exporMetricas: opcional('EXPOR_METRICAS', 'false', v.booleano),
  };

  // ── regras cruzadas: o que é aceitável em dev e inaceitável em produção ──
  if (bruta.ambiente === 'production') {
    if (bruta.sessionSecret === SEGREDO_DE_EXEMPLO) {
      problemas.push('SESSION_SECRET: o valor de exemplo não pode ser usado com NODE_ENV=production');
    }
    if (bruta.apiKey?.startsWith('sk_test_')) {
      problemas.push('API_KEY: chave de teste (sk_test_…) com NODE_ENV=production');
    }
    if (bruta.databaseUrl?.startsWith('memory:')) {
      problemas.push('DATABASE_URL: banco em memória com NODE_ENV=production perde tudo a cada reinício');
    }
  }

  const config = Object.freeze({
    ambiente: bruta.ambiente,
    porta: Number(bruta.porta),
    logLevel: bruta.logLevel,
    databaseUrl: bruta.databaseUrl,
    sessionSecret: bruta.sessionSecret,
    apiKey: bruta.apiKey,
    maxRecados: Number(bruta.maxRecados),
    exporMetricas: bruta.exporMetricas === 'true',
  });

  return { config, problemas: Object.freeze(problemas) };
}

export function mascarar(valor) {
  if (typeof valor !== 'string' || valor.length === 0) return valor;
  if (valor.length <= 8) return '********';
  return `${valor.slice(0, 3)}…${valor.slice(-2)} (${valor.length} chars)`;
}

/** Visão da configuração segura para log, para /config e para suporte técnico. */
export function configParaLog(config) {
  const saida = {};
  for (const [chave, valor] of Object.entries(config)) {
    saida[chave] = CHAVES_SECRETAS.includes(chave) ? mascarar(valor) : valor;
  }
  return saida;
}

export class ErroDeConfiguracao extends Error {
  constructor(lista) {
    super(`Configuração inválida:\n   • ${lista.join('\n   • ')}`);
    this.name = 'ErroDeConfiguracao';
    this.lista = lista;
  }
}

/**
 * Carrega a configuração do processo atual.
 * Com `sair: true` (padrão), imprime os problemas e encerra com 78.
 * Com `sair: false`, lança ErroDeConfiguracao — é o que os testes usam.
 */
export function carregarConfig({ env = process.env, sair = true } = {}) {
  const { config, problemas } = criarConfig(env);
  if (problemas.length === 0) return config;

  const erro = new ErroDeConfiguracao(problemas);
  if (!sair) throw erro;

  process.stderr.write(`\n❌ ${erro.message}\n\n`);
  process.stderr.write('Consulte .env.example para a lista completa de variáveis.\n');
  process.stderr.write('Em desenvolvimento:  cp .env.example .env   e preencha os valores.\n\n');
  process.exit(78); // EX_CONFIG — ver /usr/include/sysexits.h
}
