/**
 * Persistência: fake em memória + SQLite real, mesmo contrato.
 *
 * `node:sqlite` (`DatabaseSync`) vem no Node desde a 22.5 e não precisa de
 * dependência externa nem de flag no Node 24. Ele é **síncrono** — o que aqui
 * é uma vantagem: teste de banco sem `await` em toda linha.
 */

import { DatabaseSync } from 'node:sqlite';

import { Assinatura, Estado } from './assinatura.js';
import { CATALOGO } from './plano.js';

export class RepositorioMemoria {
  #dados = new Map();

  constructor(assinaturas = []) {
    for (const a of assinaturas) this.#dados.set(a.id, a);
  }

  salvar(assinatura) {
    this.#dados.set(assinatura.id, assinatura);
  }

  buscar(id) {
    return this.#dados.get(id) ?? null;
  }

  listarVencidas(hoje) {
    return [...this.#dados.values()]
      .filter((a) => a.estaVencida(hoje))
      .sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  }
}

const ESQUEMA = `
CREATE TABLE IF NOT EXISTS assinaturas (
    id                TEXT PRIMARY KEY,
    cliente           TEXT NOT NULL,
    plano             TEXT NOT NULL,
    inicio            TEXT NOT NULL,
    proxima_cobranca  TEXT NOT NULL,
    estado            TEXT NOT NULL,
    tentativas_falhas INTEGER NOT NULL DEFAULT 0,
    ciclos_pagos      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_vencimento
    ON assinaturas (proxima_cobranca, estado);
`;

export class RepositorioSQLite {
  #db;

  constructor(caminho = 'assinaturas.db') {
    this.#db = new DatabaseSync(caminho);
    this.#db.exec(ESQUEMA);
  }

  fechar() {
    this.#db.close();
  }

  /** Suporte a `using` (explicit resource management), disponível no Node 24. */
  [Symbol.dispose]() {
    this.fechar();
  }

  salvar(assinatura) {
    this.#db
      .prepare(
        `INSERT INTO assinaturas
           (id, cliente, plano, inicio, proxima_cobranca, estado,
            tentativas_falhas, ciclos_pagos)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT(id) DO UPDATE SET
           cliente=excluded.cliente,
           plano=excluded.plano,
           inicio=excluded.inicio,
           proxima_cobranca=excluded.proxima_cobranca,
           estado=excluded.estado,
           tentativas_falhas=excluded.tentativas_falhas,
           ciclos_pagos=excluded.ciclos_pagos`,
      )
      .run(
        assinatura.id,
        assinatura.cliente,
        assinatura.plano.codigo,
        assinatura.inicio,
        assinatura.proximaCobranca,
        assinatura.estado,
        assinatura.tentativasFalhas,
        assinatura.ciclosPagos,
      );
  }

  #hidratar(linha) {
    return new Assinatura({
      id: linha.id,
      cliente: linha.cliente,
      plano: CATALOGO[linha.plano],
      inicio: linha.inicio,
      proximaCobranca: linha.proxima_cobranca,
      estado: linha.estado,
      tentativasFalhas: linha.tentativas_falhas,
      ciclosPagos: linha.ciclos_pagos,
    });
  }

  buscar(id) {
    const linha = this.#db.prepare('SELECT * FROM assinaturas WHERE id = ?').get(id);
    return linha ? this.#hidratar(linha) : null;
  }

  listarVencidas(hoje) {
    const linhas = this.#db
      .prepare(
        `SELECT * FROM assinaturas
          WHERE proxima_cobranca <= ?
            AND estado IN (?, ?)
          ORDER BY id`,
      )
      .all(hoje, Estado.ATIVA, Estado.INADIMPLENTE);
    return linhas.map((linha) => this.#hidratar(linha));
  }
}
