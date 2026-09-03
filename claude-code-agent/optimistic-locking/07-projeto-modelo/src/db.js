// Camada de banco: esquema, seed e abertura da conexão.
// Usa o módulo nativo `node:sqlite` (Node 22.5+; estável o bastante em Node 24),
// para que o projeto rode sem `npm install`.

import { DatabaseSync } from 'node:sqlite';

const DDL = `
CREATE TABLE IF NOT EXISTS produtos (
  id             INTEGER PRIMARY KEY,
  nome           TEXT    NOT NULL,
  descricao      TEXT    NOT NULL DEFAULT '',
  preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
  estoque        INTEGER NOT NULL CHECK (estoque >= 0),
  -- A COLUNA DE VERSÃO. É o coração do optimistic locking.
  -- Ela só é escrita pelo repositório, nunca pelo cliente.
  version        INTEGER NOT NULL DEFAULT 1,
  atualizado_em  TEXT    NOT NULL
);

-- Trilha de auditoria: serve para provar, no teste, que nenhuma escrita sumiu.
CREATE TABLE IF NOT EXISTS auditoria (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  produto_id   INTEGER NOT NULL,
  version_nova INTEGER NOT NULL,
  autor        TEXT    NOT NULL,
  quando       TEXT    NOT NULL
);
`;

/**
 * Abre (ou cria) o banco e garante o esquema.
 * @param {string} caminho ':memory:' para banco em memória, ou um caminho de arquivo.
 */
export function abrirBanco(caminho = ':memory:') {
  const db = new DatabaseSync(caminho);
  // WAL permite leitores concorrentes com um escritor. Em arquivo, muda o comportamento
  // sob concorrência; em :memory: é ignorado. Deixamos explícito para você ver a decisão.
  if (caminho !== ':memory:') db.exec('PRAGMA journal_mode = WAL');
  db.exec('PRAGMA foreign_keys = ON');
  db.exec(DDL);
  return db;
}

/** Popula o banco com dados determinísticos. Idempotente: pode rodar quantas vezes quiser. */
export function semear(db, agora = '2026-08-14T00:00:00.000Z') {
  const existe = db.prepare('SELECT COUNT(*) AS n FROM produtos').get();
  if (existe.n > 0) return;

  const ins = db.prepare(`
    INSERT INTO produtos (id, nome, descricao, preco_centavos, estoque, version, atualizado_em)
    VALUES (?, ?, ?, ?, ?, 1, ?)
  `);
  ins.run(1, 'Teclado mecânico ABNT2', 'Switch marrom, 87 teclas.', 39900, 10, agora);
  ins.run(2, 'Monitor 27" 1440p', 'IPS, 165 Hz.', 189900, 4, agora);
  ins.run(3, 'Cadeira ergonômica', 'Apoio lombar ajustável.', 129900, 2, agora);
}
