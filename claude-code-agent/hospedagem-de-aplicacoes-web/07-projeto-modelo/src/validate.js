import { erroValidacao } from "./erros.js";
import { ALFABETO } from "./ids.js";

const ALFABETO_SET = new Set(ALFABETO);

/**
 * Valida a URL de destino.
 * Regras, e o porquê de cada uma:
 *  - só http/https  → impede javascript:, data:, file: (vetores de XSS e de leitura local)
 *  - com host       → "http://" sozinho não é destino
 *  - até 2048 chars → limite prático de URL em navegadores e proxies antigos
 *  - sem host local → impede usar o encurtador para atacar a rede interna (SSRF)
 */
export function validarDestino(valor) {
  if (typeof valor !== "string" || valor.trim() === "") {
    throw erroValidacao("destino é obrigatório");
  }
  const bruto = valor.trim();
  if (bruto.length > 2048) throw erroValidacao("destino excede 2048 caracteres");

  let url;
  try {
    url = new URL(bruto);
  } catch {
    throw erroValidacao("destino não é uma URL válida");
  }

  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw erroValidacao("destino deve usar http ou https");
  }
  if (!url.hostname) throw erroValidacao("destino sem host");

  if (ehHostPrivado(url.hostname)) {
    throw erroValidacao("destino aponta para endereço privado ou local");
  }
  return url.toString();
}

// Bloqueio simples de SSRF. Não é completo (nome pode resolver para IP privado —
// a defesa completa exige resolver o DNS e checar o IP no momento da requisição),
// mas pega os casos triviais e está declarado como parcial de propósito.
export function ehHostPrivado(host) {
  const h = host.toLowerCase();
  if (h === "localhost" || h.endsWith(".localhost") || h.endsWith(".internal")) return true;
  if (h === "0.0.0.0" || h === "::1" || h === "[::1]") return true;
  if (/^127\./.test(h)) return true;
  if (/^10\./.test(h)) return true;
  if (/^192\.168\./.test(h)) return true;
  if (/^172\.(1[6-9]|2\d|3[01])\./.test(h)) return true;
  if (/^169\.254\./.test(h)) return true;   // link-local: 169.254.169.254 é o metadata da nuvem
  return false;
}

/** Valida um apelido escolhido pelo usuário. */
export function validarSlug(valor) {
  if (typeof valor !== "string") throw erroValidacao("apelido inválido");
  const s = valor.trim();
  if (s.length < 3 || s.length > 32) throw erroValidacao("apelido deve ter de 3 a 32 caracteres");
  for (const c of s) {
    if (!ALFABETO_SET.has(c)) throw erroValidacao(`caractere não permitido no apelido: "${c}"`);
  }
  // Palavras reservadas: se alguém criar o apelido "api", /api/... deixa de funcionar.
  if (["api", "health", "static", "public", "admin"].includes(s.toLowerCase())) {
    throw erroValidacao("apelido reservado");
  }
  return s;
}
