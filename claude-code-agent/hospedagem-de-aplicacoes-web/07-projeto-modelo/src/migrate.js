/**
 * Migrador mínimo, sem dependência extra.
 * Aplica os arquivos .sql de ./sql em ordem alfabética e registra o que já rodou.
 *
 * Em projeto de verdade, prefira node-pg-migrate, Prisma Migrate, Drizzle Kit ou Flyway.
 * Este arquivo existe para você VER o mecanismo, que é sempre o mesmo:
 *   uma tabela de controle + arquivos ordenados + uma transação por arquivo.
 */
import pg from "pg";
import { readdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL("../sql", import.meta.url));

const url = process.env.DATABASE_URL;
if (!url) {
  console.error("DATABASE_URL não definida. Nada a migrar (modo memória não tem esquema).");
  process.exit(1);
}

const cliente = new pg.Client({
  connectionString: url,
  ssl: /sslmode=(require|verify)/.test(url) ? { rejectUnauthorized: false } : undefined,
});
await cliente.connect();

await cliente.query(`
  CREATE TABLE IF NOT EXISTS migracao (
    nome       text PRIMARY KEY,
    aplicada_em timestamptz NOT NULL DEFAULT now()
  )`);

const { rows } = await cliente.query("SELECT nome FROM migracao");
const jaAplicadas = new Set(rows.map((r) => r.nome));

const arquivos = (await readdir(DIR)).filter((f) => f.endsWith(".sql")).sort();
let aplicadas = 0;

for (const arquivo of arquivos) {
  if (jaAplicadas.has(arquivo)) { console.log(`= ${arquivo} (já aplicada)`); continue; }
  const sql = await readFile(`${DIR}/${arquivo}`, "utf8");
  try {
    // Uma transação por arquivo: ou a migração inteira entra, ou nada dela entra.
    await cliente.query("BEGIN");
    await cliente.query(sql);
    await cliente.query("INSERT INTO migracao (nome) VALUES ($1)", [arquivo]);
    await cliente.query("COMMIT");
    console.log(`+ ${arquivo} aplicada`);
    aplicadas++;
  } catch (e) {
    await cliente.query("ROLLBACK");
    console.error(`x ${arquivo} FALHOU: ${e.message}`);
    await cliente.end();
    process.exit(1);
  }
}

console.log(`pronto: ${aplicadas} migração(ões) nova(s), ${arquivos.length} no total`);
await cliente.end();
