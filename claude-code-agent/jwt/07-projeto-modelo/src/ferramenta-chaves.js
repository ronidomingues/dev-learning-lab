#!/usr/bin/env node
/**
 * Ferramenta de linha de comando do chaveiro.
 *
 *   node src/ferramenta-chaves.js listar
 *   node src/ferramenta-chaves.js rotacionar
 *   node src/ferramenta-chaves.js aposentar <kid>
 *   node src/ferramenta-chaves.js jwks
 */

import { carregarOuCriarChaveiro, rotacionar, aposentar } from './chaves.js';
import { config } from './config.js';

const comando = process.argv[2] ?? 'listar';
const chaveiro = carregarOuCriarChaveiro(config.caminhoChaveiro);

switch (comando) {
  case 'listar':
    for (const [kid] of chaveiro.chaves) {
      console.log(`${kid === chaveiro.kidAtiva ? '* ' : '  '}${kid}`);
    }
    console.log(`\n(* = ativa, usada para assinar)`);
    break;

  case 'rotacionar': {
    const anterior = chaveiro.kidAtiva;
    const novo = rotacionar(chaveiro, config.caminhoChaveiro);
    console.log(`nova chave ativa: ${novo}`);
    console.log(`anterior mantida para verificacao: ${anterior}`);
    console.log(`aposente-a somente apos ${config.vidaAccessSegundos}s (vida do access token).`);
    break;
  }

  case 'aposentar': {
    const kid = process.argv[3];
    if (!kid) { console.error('uso: aposentar <kid>'); process.exit(1); }
    aposentar(chaveiro, kid, config.caminhoChaveiro);
    console.log(`chave ${kid} removida do chaveiro`);
    break;
  }

  case 'jwks':
    console.log(JSON.stringify(chaveiro.jwks(), null, 2));
    break;

  default:
    console.error(`comando desconhecido: ${comando}`);
    process.exit(1);
}
