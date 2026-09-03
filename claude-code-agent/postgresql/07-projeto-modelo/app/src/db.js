// db.js — a conexão com o PostgreSQL, via node-postgres (pg).
//
// Lições embutidas:
//   1. NUNCA concatene valores na SQL. Use consultas parametrizadas ($1, $2) — a defesa
//      definitiva contra SQL injection, e o que também deixa o banco reusar o plano.
//   2. Use um POOL de conexões, não uma conexão por requisição. Abrir conexão no Postgres
//      é caro (é um processo no servidor); o pool reaproveita.
//   3. A configuração vem do ambiente. O código não conhece a senha.

import pg from 'pg';

const { Pool } = pg;

// A string de conexão (DATABASE_URL) tem a forma:
//   postgres://usuario:senha@host:porta/banco
// Em produção, adicione ?sslmode=require e configure ssl abaixo.
export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // Limites sensatos: o Postgres tem max_connections (padrão 100). Um pool grande demais,
  // multiplicado por várias instâncias da app, estoura esse limite. Menos é mais.
  max: Number(process.env.DB_POOL_MAX || 10),
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000,
});

// Um único ponto para logar erros de conexão ociosa (senão o processo pode cair silenciosamente).
pool.on('error', (err) => {
  console.error(JSON.stringify({ nivel: 'erro', msg: 'erro no pool de conexões', erro: err.message }));
});

// Atalho para consultas simples, sempre parametrizadas.
export function query(texto, params) {
  return pool.query(texto, params);
}

// Executa uma função dentro de UMA transação, com commit/rollback automáticos.
// É o padrão correto: pega UMA conexão do pool, roda tudo nela, devolve.
export async function comTransacao(fn) {
  const cliente = await pool.connect();
  try {
    await cliente.query('BEGIN');
    const resultado = await fn(cliente);
    await cliente.query('COMMIT');
    return resultado;
  } catch (e) {
    await cliente.query('ROLLBACK');
    throw e;
  } finally {
    cliente.release(); // devolve a conexão ao pool — ESQUECER isto vaza conexões até esgotar
  }
}

export async function fechar() {
  await pool.end();
}
