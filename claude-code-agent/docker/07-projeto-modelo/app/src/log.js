// log.js — log estruturado em JSON, uma linha por evento, direto no stdout.
//
// Por que JSON em uma linha: o driver de log do Docker captura stdout/stderr como texto.
// Ferramentas de agregação (Loki, Elasticsearch, CloudWatch) fazem parse de JSON por linha
// sem configuração. Log multi-linha (stack trace solto) quebra essa correlação.
//
// Por que stdout e não arquivo: em container, o processo NÃO gerencia seus próprios arquivos
// de log. Ele escreve em stdout e a plataforma decide onde aquilo vai parar. Escrever em
// arquivo dentro do container é o caminho garantido para encher o disco em silêncio.

function emitir(nivel, mensagem, extras = {}) {
  const linha = {
    ts: new Date().toISOString(),
    nivel,
    msg: mensagem,
    ...extras,
  };
  // Erros não serializam bem por padrão: name/message/stack não são propriedades enumeráveis.
  if (extras.erro instanceof Error) {
    linha.erro = {
      nome: extras.erro.name,
      mensagem: extras.erro.message,
      pilha: extras.erro.stack,
    };
  }
  const destino = nivel === 'erro' ? process.stderr : process.stdout;
  destino.write(JSON.stringify(linha) + '\n');
}

export const log = {
  info: (msg, extras) => emitir('info', msg, extras),
  aviso: (msg, extras) => emitir('aviso', msg, extras),
  erro: (msg, extras) => emitir('erro', msg, extras),
};
