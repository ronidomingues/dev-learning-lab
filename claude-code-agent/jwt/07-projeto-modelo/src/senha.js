/**
 * Hash de senha com scrypt (RFC 7914), que ja vem no Node.
 *
 * Isto nao e sobre JWT — e o passo ANTES do JWT. Colocamos aqui porque um
 * projeto de autenticacao que guarda senha em texto puro, ou com SHA-256 seco,
 * ensina a coisa errada. scrypt e deliberadamente lento e faminto por memoria:
 * o objetivo e que quem roubar o banco nao consiga testar bilhoes de senhas
 * por segundo numa GPU.
 *
 * Se puder usar dependencia, argon2id e a recomendacao atual da OWASP.
 * scrypt e a melhor opcao que existe sem instalar nada.
 */

import { scrypt, randomBytes, timingSafeEqual } from 'node:crypto';
import { promisify } from 'node:util';

const scryptAsync = promisify(scrypt);

// N=2^15 custa ~32 MB e ~50-100 ms por hash em hardware de 2026.
const PARAMETROS = { N: 32768, r: 8, p: 1, maxmem: 64 * 1024 * 1024 };
const TAMANHO = 32;

export async function gerarHash(senha) {
  const sal = randomBytes(16);
  const derivada = await scryptAsync(senha.normalize('NFKC'), sal, TAMANHO, PARAMETROS);
  // Formato auto-descritivo: da para trocar os parametros no futuro sem
  // invalidar os hashes antigos.
  return `scrypt$${PARAMETROS.N}$${PARAMETROS.r}$${PARAMETROS.p}$${sal.toString('base64url')}$${derivada.toString('base64url')}`;
}

export async function conferir(senha, hashGuardado) {
  const partes = String(hashGuardado).split('$');
  if (partes.length !== 6 || partes[0] !== 'scrypt') return false;
  const [, N, r, p, salB64, esperadoB64] = partes;
  const sal = Buffer.from(salB64, 'base64url');
  const esperado = Buffer.from(esperadoB64, 'base64url');
  const derivada = await scryptAsync(senha.normalize('NFKC'), sal, esperado.length, {
    N: Number(N), r: Number(r), p: Number(p), maxmem: 64 * 1024 * 1024,
  });
  return derivada.length === esperado.length && timingSafeEqual(derivada, esperado);
}
