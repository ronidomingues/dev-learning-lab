/**
 * Armazenamento em memória.
 *
 * TODO(producao): trocar por SQLite (node:sqlite, nativo no Node 22+) ou Postgres.
 * A interface pública deste módulo foi desenhada para que essa troca NÃO exija
 * mudar nenhum teste — se um teste quebrar na troca, a abstração vazou.
 * É o Exercício 4 do README.
 */
import { randomUUID } from 'node:crypto';

/** Ordenação estável: por criação e, em empate, por id. Base da paginação por cursor. */
const porCriacao = (a, b) =>
  a.criado_em.localeCompare(b.criado_em) || a.id.localeCompare(b.id);

export function criarRepositorio() {
  const livros = new Map();
  const emprestimos = new Map();

  function semear() {
    const iniciais = [
      { titulo: 'Dom Casmurro',           autor: 'Machado de Assis',  ano: 1899, isbn: '9788572326972' },
      { titulo: 'Grande Sertão: Veredas', autor: 'Guimarães Rosa',    ano: 1956, isbn: '9788520925102' },
      { titulo: 'A Hora da Estrela',      autor: 'Clarice Lispector', ano: 1977, isbn: '9788532511010' },
      { titulo: 'Vidas Secas',            autor: 'Graciliano Ramos',  ano: 1938, isbn: '9788501069658' },
      { titulo: 'Macunaíma',              autor: 'Mário de Andrade',  ano: 1928, isbn: '9788526016439' }
    ];
    iniciais.forEach((l, i) => {
      const id = randomUUID();
      // Timestamps determinísticos e crescentes: a ordenação do seed é estável,
      // então os testes de paginação são reprodutíveis.
      const criado = new Date(Date.UTC(2026, 0, 1, 0, 0, i)).toISOString();
      livros.set(id, {
        id, ...l, disponivel: true,
        criado_em: criado, atualizado_em: criado, versao: 1
      });
    });
  }

  return {
    semear,

    // ---------------- livros ----------------
    listarLivros({ limite = 20, depoisDe = null, autor = null, disponivel = null } = {}) {
      let itens = [...livros.values()].sort(porCriacao);

      if (autor) {
        const alvo = autor.toLowerCase();
        itens = itens.filter(l => l.autor.toLowerCase().includes(alvo));
      }
      if (disponivel !== null) {
        itens = itens.filter(l => l.disponivel === disponivel);
      }

      let inicio = 0;
      if (depoisDe) {
        const i = itens.findIndex(l => l.id === depoisDe);
        // Cursor que não existe mais (item removido): recomeça do início, sem erro.
        inicio = i === -1 ? 0 : i + 1;
      }

      // Pede um a mais para saber se há próxima página, sem contar o total.
      const pagina = itens.slice(inicio, inicio + limite + 1);
      const temMais = pagina.length > limite;
      const dados = temMais ? pagina.slice(0, limite) : pagina;

      return { dados, proximoId: temMais ? dados.at(-1).id : null, total: itens.length };
    },

    obterLivro: id => livros.get(id) ?? null,

    livroPorIsbn(isbn) {
      if (!isbn) return null;
      const normalizado = isbn.replaceAll('-', '');
      return [...livros.values()].find(l => l.isbn?.replaceAll('-', '') === normalizado) ?? null;
    },

    criarLivro(dados) {
      const agora = new Date().toISOString();
      const livro = {
        id: randomUUID(),
        titulo: dados.titulo.trim(),
        autor: dados.autor.trim(),
        ano: dados.ano ?? null,
        isbn: dados.isbn ?? null,
        disponivel: true,
        criado_em: agora,
        atualizado_em: agora,
        versao: 1
      };
      livros.set(livro.id, livro);
      return livro;
    },

    atualizarLivro(id, alteracoes) {
      const atual = livros.get(id);
      if (!atual) return null;
      const atualizado = {
        ...atual,
        ...alteracoes,
        id: atual.id,                       // o id nunca muda, venha o que vier no corpo
        atualizado_em: new Date().toISOString(),
        versao: atual.versao + 1
      };
      livros.set(id, atualizado);
      return atualizado;
    },

    // ---------------- empréstimos ----------------
    listarEmprestimos({ livroId = null, apenasAbertos = false } = {}) {
      let itens = [...emprestimos.values()].sort(porCriacao);
      if (livroId) itens = itens.filter(e => e.livro_id === livroId);
      if (apenasAbertos) itens = itens.filter(e => e.devolvido_em === null);
      return itens;
    },

    obterEmprestimo: id => emprestimos.get(id) ?? null,

    /** Empréstimo e indisponibilidade do livro mudam JUNTOS — nunca separadamente. */
    criarEmprestimo({ livroId, pessoa }) {
      const livro = livros.get(livroId);
      if (!livro || !livro.disponivel) return null;

      const agora = new Date().toISOString();
      const emprestimo = {
        id: randomUUID(),
        livro_id: livroId,
        pessoa: pessoa.trim(),
        emprestado_em: agora,
        devolvido_em: null,
        criado_em: agora
      };
      emprestimos.set(emprestimo.id, emprestimo);
      livros.set(livroId, { ...livro, disponivel: false, versao: livro.versao + 1,
                            atualizado_em: agora });
      return emprestimo;
    },

    devolver(emprestimoId) {
      const emprestimo = emprestimos.get(emprestimoId);
      if (!emprestimo || emprestimo.devolvido_em !== null) return null;

      const agora = new Date().toISOString();
      const devolvido = { ...emprestimo, devolvido_em: agora };
      emprestimos.set(emprestimoId, devolvido);

      const livro = livros.get(emprestimo.livro_id);
      if (livro) {
        livros.set(livro.id, { ...livro, disponivel: true, versao: livro.versao + 1,
                               atualizado_em: agora });
      }
      return devolvido;
    },

    // ---------------- apoio ----------------
    estatisticas: () => ({
      livros: livros.size,
      emprestimos: emprestimos.size,
      emprestimos_abertos: [...emprestimos.values()].filter(e => e.devolvido_em === null).length
    }),

    limpar() { livros.clear(); emprestimos.clear(); }
  };
}
