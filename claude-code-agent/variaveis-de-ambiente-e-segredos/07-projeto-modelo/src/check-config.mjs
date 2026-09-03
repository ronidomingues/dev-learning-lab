#!/usr/bin/env node
/**
 * check-config.mjs — valida a configuração e sai. Não abre porta, não toca em rede.
 *
 * Para que serve, na vida real:
 *   • no `install.sh`, ANTES de gravar o arquivo de ambiente no servidor do cliente;
 *   • no CI, para o pipeline falhar antes de publicar uma versão que não sobe;
 *   • em `ExecStartPre=` do systemd, para falhar com mensagem legível;
 *   • no suporte: "rode isto e me mande a saída" — ela é segura, mascara os valores.
 *
 * Uso:
 *   node src/check-config.mjs
 *   node --env-file=.env src/check-config.mjs
 */
import { criarConfig, configParaLog } from './config.mjs';
import { redigirUrl } from './log.mjs';

const { config, problemas } = criarConfig(process.env);

if (problemas.length > 0) {
  process.stderr.write('\n❌ Configuração inválida:\n');
  for (const p of problemas) process.stderr.write(`   • ${p}\n`);
  process.stderr.write('\nConsulte .env.example para a lista completa de variáveis.\n\n');
  process.exit(78); // EX_CONFIG
}

process.stdout.write('✅ Configuração válida.\n\n');
const visao = { ...configParaLog(config), databaseUrl: redigirUrl(config.databaseUrl) };
for (const [chave, valor] of Object.entries(visao)) {
  process.stdout.write(`   ${chave.padEnd(16)} ${valor}\n`);
}
process.stdout.write('\n');
