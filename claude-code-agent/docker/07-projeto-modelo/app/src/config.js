// config.js — configuração vem do ambiente, e o processo FALHA RÁPIDO se algo faltar.
//
// Por que assim: um container que sobe com configuração inválida e só quebra na primeira
// requisição é muito pior que um container que se recusa a subir. O orquestrador sabe lidar
// com "não subiu"; ele não sabe lidar com "subiu errado".

function obrigatoria(nome) {
  const valor = process.env[nome];
  if (valor === undefined || valor === '') {
    throw new Error(`Variável de ambiente obrigatória ausente: ${nome}`);
  }
  return valor;
}

function inteiro(nome, padrao) {
  const bruto = process.env[nome];
  if (bruto === undefined || bruto === '') return padrao;
  const n = Number.parseInt(bruto, 10);
  if (!Number.isInteger(n) || n <= 0) {
    throw new Error(`Variável ${nome} deve ser um inteiro positivo, recebi: "${bruto}"`);
  }
  return n;
}

export const config = {
  porta: inteiro('PORT', 3000),

  // 0.0.0.0, nunca 127.0.0.1: dentro do container, o loopback não é alcançável pelo -p do host.
  host: process.env.HOST || '0.0.0.0',

  // Caminho do arquivo de dados. Em produção ele aponta para dentro de um VOLUME.
  arquivoDados: process.env.ARQUIVO_DADOS || '/dados/recados.json',

  // Só para demonstrar uma variável obrigatória de verdade: sem ela, o container não sobe.
  nomeDoMural: obrigatoria('NOME_DO_MURAL'),

  maxRecados: inteiro('MAX_RECADOS', 500),
  tamanhoMaxTexto: inteiro('TAMANHO_MAX_TEXTO', 280),

  // Prazo para o encerramento gracioso. Precisa ser MENOR que o timeout do `docker stop` (10s),
  // senão o SIGKILL chega antes de terminarmos por conta própria.
  prazoEncerramentoMs: inteiro('PRAZO_ENCERRAMENTO_MS', 8000),

  ambiente: process.env.NODE_ENV || 'development',
};
