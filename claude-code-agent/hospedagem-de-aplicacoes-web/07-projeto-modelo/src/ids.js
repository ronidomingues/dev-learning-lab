import { randomBytes } from "node:crypto";

// Alfabeto sem caracteres ambíguos: nada de 0/O nem 1/l/I.
// Motivo prático: link curto é lido em voz alta e digitado à mão.
const ALFABETO = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ";

/**
 * Gera um slug aleatório.
 * Usa randomBytes (CSPRNG), não Math.random: slug previsível permite
 * enumerar os links de todo mundo.
 */
export function gerarSlug(tamanho = 7) {
  if (tamanho < 4 || tamanho > 32) throw new Error("tamanho de slug fora da faixa");
  const bytes = randomBytes(tamanho);
  let saida = "";
  for (let i = 0; i < tamanho; i++) saida += ALFABETO[bytes[i] % ALFABETO.length];
  return saida;
}

// Espaço de chaves: 56^7 ≈ 1,7 trilhão. Pelo paradoxo do aniversário, a chance de
// colisão passa de 1% depois de ~5,9 milhões de links. Por isso o banco tem UNIQUE
// no slug e a criação tenta de novo em caso de colisão (ver repositorio).
export const ESPACO_DE_CHAVES = ALFABETO.length ** 7;

export { ALFABETO };
