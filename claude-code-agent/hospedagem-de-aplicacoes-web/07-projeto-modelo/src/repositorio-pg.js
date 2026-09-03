import pg from "pg";
import { erroSlugEmUso } from "./erros.js";

/**
 * Repositório PostgreSQL.
 *
 * Decisões que este arquivo ensina:
 *  - Pool, não Client: abrir conexão por requisição é o erro de performance nº 1.
 *  - `max` pequeno: planos gratuitos têm poucas conexões. Com N instâncias da aplicação,
 *    o total é N × max — e é assim que se estoura o limite do banco sem perceber.
 *  - Consulta parametrizada ($1, $2): a única defesa correta contra SQL injection.
 *  - Erro 23505 (unique_violation) traduzido para erro de domínio: a camada HTTP
 *    não deve conhecer códigos do PostgreSQL.
 */
export function criarRepositorioPg(connectionString, { max = 5 } = {}) {
  const pool = new pg.Pool({
    connectionString,
    max,
    idleTimeoutMillis: 10_000,
    connectionTimeoutMillis: 5_000,
    // Provedores gerenciados (Neon, Supabase, Render) exigem TLS com CA própria.
    ssl: /sslmode=(require|verify)/.test(connectionString) ? { rejectUnauthorized: false } : undefined,
  });

  // Um erro num cliente ocioso do pool não deve derrubar o processo inteiro.
  pool.on("error", (e) => console.error(JSON.stringify({ nivel: "erro", origem: "pool_pg", msg: e.message })));

  return {
    tipo: "postgres",

    async ping() {
      await pool.query("SELECT 1");
      return true;
    },

    async criar({ slug, destino }) {
      try {
        const { rows } = await pool.query(
          `INSERT INTO link (slug, destino) VALUES ($1, $2)
           RETURNING id, slug, destino, cliques, criado_em`,
          [slug, destino]
        );
        return rows[0];
      } catch (e) {
        if (e.code === "23505") throw erroSlugEmUso(slug);  // unique_violation
        throw e;
      }
    },

    async buscarPorSlug(slug) {
      const { rows } = await pool.query(
        `SELECT id, slug, destino, cliques, criado_em FROM link WHERE slug = $1`,
        [slug]
      );
      return rows[0] ?? null;
    },

    async registrarClique(slug) {
      // UPDATE simples e atômico. Em volume MUITO alto, o certo é acumular no Redis
      // e descarregar em lote — ver 60-teoria-avancada.md, seção "escrita quente".
      await pool.query(`UPDATE link SET cliques = cliques + 1 WHERE slug = $1`, [slug]);
    },

    async top(limite = 10) {
      const { rows } = await pool.query(
        `SELECT slug, destino, cliques FROM link ORDER BY cliques DESC, id DESC LIMIT $1`,
        [limite]
      );
      return rows;
    },

    async fechar() { await pool.end(); },
  };
}
