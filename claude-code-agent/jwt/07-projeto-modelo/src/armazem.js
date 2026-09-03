/**
 * Armazenamento em memoria. Em producao isso seria Postgres + Redis; a
 * interface foi mantida pequena de proposito para que a troca seja obvia.
 *
 * O ponto didatico deste arquivo: **um sistema com JWT ainda tem estado no
 * servidor.** A promessa de "JWT e stateless" so vale para o access token de
 * vida curta. Refresh token, revogacao e deteccao de reuso sao estado, e nao
 * ha como fugir disso sem abrir mao de poder deslogar alguem.
 */

import { randomUUID, randomBytes, createHash } from 'node:crypto';

export class Armazem {
  constructor() {
    this.usuariosPorEmail = new Map();
    this.usuariosPorId = new Map();
    /** hashDoRefresh -> { id, usuarioId, familiaId, expEm, usado, substituidoPor } */
    this.refresh = new Map();
    /** familiaId -> true, quando a familia inteira foi invalidada por reuso */
    this.familiasQueimadas = new Set();
    /** jti -> expEm (segundos). Lista de negacao de access tokens. */
    this.jtiRevogados = new Map();
    /** usuarioId -> [nota] */
    this.notas = new Map();
  }

  // --- usuarios ------------------------------------------------------------

  criarUsuario({ email, hashDaSenha, papeis = ['usuario'] }) {
    if (this.usuariosPorEmail.has(email)) {
      const erro = new Error('email ja cadastrado');
      erro.codigo = 'email_duplicado';
      throw erro;
    }
    const usuario = { id: randomUUID(), email, hashDaSenha, papeis, criadoEm: new Date().toISOString() };
    this.usuariosPorEmail.set(email, usuario);
    this.usuariosPorId.set(usuario.id, usuario);
    this.notas.set(usuario.id, []);
    return usuario;
  }

  usuarioPorEmail(email) {
    return this.usuariosPorEmail.get(email) ?? null;
  }

  usuarioPorId(id) {
    return this.usuariosPorId.get(id) ?? null;
  }

  // --- refresh tokens ------------------------------------------------------

  /**
   * O refresh token e OPACO: 32 bytes aleatorios, sem estrutura, sem
   * significado. Nao e um JWT — e nem deveria ser. Um JWT de refresh nao
   * traria vantagem nenhuma (ele SEMPRE bate no banco, entao a auto-suficiencia
   * do JWT nao serve para nada) e traria a desvantagem de expor o conteudo.
   *
   * Guardamos apenas o SHA-256 do token, nunca o token. Se o banco vazar,
   * quem vazou nao consegue reautenticar — mesmo raciocinio de guardar hash
   * de senha. (SHA-256 puro basta aqui porque a entrada tem 256 bits de
   * entropia real; para senha humana seria imperdoavel.)
   */
  emitirRefresh({ usuarioId, familiaId = randomUUID(), vidaSegundos, agora }) {
    const segredo = randomBytes(32).toString('base64url');
    const registro = {
      id: randomUUID(),
      usuarioId,
      familiaId,
      expEm: agora + vidaSegundos,
      usado: false,
      substituidoPor: null,
      criadoEm: agora,
    };
    this.refresh.set(hashDoToken(segredo), registro);
    return { segredo, registro };
  }

  buscarRefresh(segredo) {
    return this.refresh.get(hashDoToken(segredo)) ?? null;
  }

  marcarRefreshUsado(segredo, novoId) {
    const registro = this.refresh.get(hashDoToken(segredo));
    if (registro) {
      registro.usado = true;
      registro.substituidoPor = novoId;
    }
  }

  /**
   * Deteccao de reuso: se um refresh JA usado voltar a aparecer, ou o cliente
   * esta com bug, ou alguem roubou o token. Nao da para distinguir os dois
   * casos, entao o protocolo manda assumir o pior e queimar a familia inteira
   * — todos os refresh descendentes daquele login. Ver 17-ciclo-de-vida-sessao.md.
   */
  queimarFamilia(familiaId) {
    this.familiasQueimadas.add(familiaId);
    let queimados = 0;
    for (const [chave, registro] of this.refresh) {
      if (registro.familiaId === familiaId) {
        this.refresh.delete(chave);
        queimados += 1;
      }
    }
    return queimados;
  }

  familiaEstaQueimada(familiaId) {
    return this.familiasQueimadas.has(familiaId);
  }

  // --- revogacao de access token ------------------------------------------

  /**
   * Lista de negacao por `jti`. O custo dela e limitado: uma entrada so
   * precisa viver ate `exp`. Com access token de 15 minutos, a lista guarda no
   * maximo 15 minutos de logouts — em qualquer sistema real isso cabe folgado
   * num Redis. E a resposta pratica para "JWT nao da para revogar".
   */
  revogarJti(jti, expEm) {
    this.jtiRevogados.set(jti, expEm);
  }

  jtiEstaRevogado(jti) {
    return this.jtiRevogados.has(jti);
  }

  /** Limpeza: entradas expiradas nao servem para nada, ja que o token morreu. */
  limpar(agora) {
    let removidos = 0;
    for (const [jti, expEm] of this.jtiRevogados) {
      if (expEm <= agora) { this.jtiRevogados.delete(jti); removidos += 1; }
    }
    for (const [chave, registro] of this.refresh) {
      if (registro.expEm <= agora) { this.refresh.delete(chave); removidos += 1; }
    }
    return removidos;
  }

  // --- notas ---------------------------------------------------------------

  listarNotas(usuarioId) {
    return this.notas.get(usuarioId) ?? [];
  }

  criarNota(usuarioId, texto) {
    const nota = { id: randomUUID(), texto, criadaEm: new Date().toISOString() };
    this.notas.get(usuarioId).push(nota);
    return nota;
  }

  apagarNota(usuarioId, notaId) {
    const lista = this.notas.get(usuarioId) ?? [];
    const indice = lista.findIndex((n) => n.id === notaId);
    if (indice === -1) return false;
    lista.splice(indice, 1);
    return true;
  }
}

export function hashDoToken(segredo) {
  return createHash('sha256').update(segredo, 'utf8').digest('base64url');
}
