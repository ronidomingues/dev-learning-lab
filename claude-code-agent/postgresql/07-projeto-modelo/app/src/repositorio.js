// repositorio.js — todas as consultas SQL da aplicação, num lugar só.
//
// Por que centralizar: SQL espalhado pelo código é impossível de auditar e otimizar.
// Aqui cada função é uma operação de negócio, e toda SQL é parametrizada.

import { query, comTransacao } from './db.js';

export class ErroNegocio extends Error {
  constructor(mensagem, codigo) {
    super(mensagem);
    this.name = 'ErroNegocio';
    this.codigo = codigo; // ex.: 'indisponivel', 'nao_encontrado'
  }
}

// ---- Consultas de leitura --------------------------------------------------

export async function listarLivros({ busca = null, limite = 50 } = {}) {
  // Um livro com seus autores agregados e a contagem de exemplares disponíveis.
  const { rows } = await query(
    `
    SELECT
      l.id,
      l.titulo,
      l.ano,
      l.dados->>'genero' AS genero,
      COALESCE(
        array_agg(DISTINCT a.nome) FILTER (WHERE a.nome IS NOT NULL),
        '{}'
      ) AS autores,
      (SELECT count(*) FROM livros_disponiveis d WHERE d.livro_id = l.id) AS disponiveis
    FROM livros l
    LEFT JOIN livros_autores la ON la.livro_id = l.id
    LEFT JOIN autores a         ON a.id = la.autor_id
    WHERE ($1::text IS NULL OR lower(l.titulo) LIKE '%' || lower($1) || '%')
    GROUP BY l.id
    ORDER BY l.titulo
    LIMIT $2
    `,
    [busca, limite],
  );
  return rows;
}

export async function exemplaresDisponiveis(livroId) {
  const { rows } = await query(
    `SELECT exemplar_id, codigo FROM livros_disponiveis WHERE livro_id = $1 ORDER BY codigo`,
    [livroId],
  );
  return rows;
}

export async function atrasados() {
  const { rows } = await query(`SELECT * FROM emprestimos_atrasados()`);
  return rows;
}

export async function emprestimosDoMembro(membroId) {
  const { rows } = await query(
    `
    SELECT em.id, l.titulo, e.codigo, em.emprestado_em, em.vence_em, em.devolvido_em
    FROM emprestimos em
    JOIN exemplares e ON e.id = em.exemplar_id
    JOIN livros l     ON l.id = e.livro_id
    WHERE em.membro_id = $1
    ORDER BY em.emprestado_em DESC
    `,
    [membroId],
  );
  return rows;
}

// ---- Operações de escrita (regras de negócio) ------------------------------

// Empresta usando a função do banco: a lógica e a atomicidade vivem lá.
// Mapeamos os erros do Postgres para erros de negócio limpos.
export async function emprestar(exemplarId, membroId, dias = 14) {
  try {
    const { rows } = await query(`SELECT emprestar($1, $2, $3) AS id`, [exemplarId, membroId, dias]);
    return rows[0].id;
  } catch (e) {
    // ERRCODEs levantados pela função (ver 002_functions.sql)
    if (e.code === 'P0001' || e.code === '23505' || e.code === '23P01') {
      throw new ErroNegocio(e.message.replace(/^.*?:\s*/, ''), 'indisponivel');
    }
    throw e;
  }
}

export async function devolver(exemplarId) {
  const { rows } = await query(`SELECT devolver($1) AS estava_emprestado`, [exemplarId]);
  return rows[0].estava_emprestado;
}

// Exemplo de transação em código de aplicação (em vez de função no banco):
// cadastrar um livro com seus autores, tudo ou nada.
export async function cadastrarLivro({ titulo, ano, isbn = null, genero = null, autores = [] }) {
  return comTransacao(async (cli) => {
    const { rows } = await cli.query(
      `INSERT INTO livros (titulo, ano, isbn, dados)
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [titulo, ano, isbn, genero ? { genero } : {}],
    );
    const livroId = rows[0].id;

    for (const nomeAutor of autores) {
      // Encontra ou cria o autor (UPSERT), depois liga ao livro.
      const a = await cli.query(
        `INSERT INTO autores (nome) VALUES ($1)
         ON CONFLICT DO NOTHING RETURNING id`,
        [nomeAutor],
      );
      const autorId = a.rows[0]?.id
        ?? (await cli.query(`SELECT id FROM autores WHERE nome = $1`, [nomeAutor])).rows[0].id;
      await cli.query(
        `INSERT INTO livros_autores (livro_id, autor_id) VALUES ($1, $2)
         ON CONFLICT DO NOTHING`,
        [livroId, autorId],
      );
    }
    return livroId;
  });
}
