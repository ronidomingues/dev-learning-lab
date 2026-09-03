// Núcleo de domínio: sem HTTP, sem I/O, sem relógio global.
// Tudo que é "mundo externo" entra por parâmetro — é o que torna o código testável
// e é o que faz um agente conseguir alterar isto sem quebrar o resto.

/** Erro de validação: o chamador errou a entrada. */
export class ErroDeValidacao extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'ErroDeValidacao';
    this.status = 400;
  }
}

/** Erro de recurso inexistente. */
export class NaoEncontrado extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'NaoEncontrado';
    this.status = 404;
  }
}

const PRIORIDADES = new Set(['baixa', 'media', 'alta']);
const TAMANHO_MAXIMO_TITULO = 120;

/**
 * Repositório em memória de tarefas.
 * `agora` é injetado para o teste poder congelar o tempo.
 */
export class RepositorioDeTarefas {
  #tarefas = new Map();
  #proximoId = 1;
  #agora;

  /** @param {() => Date} agora relógio injetado */
  constructor(agora = () => new Date()) {
    this.#agora = agora;
  }

  criar({ titulo, prioridade = 'media' }) {
    const tituloLimpo = typeof titulo === 'string' ? titulo.trim() : '';
    if (tituloLimpo.length === 0) {
      throw new ErroDeValidacao('titulo é obrigatório');
    }
    if (tituloLimpo.length > TAMANHO_MAXIMO_TITULO) {
      throw new ErroDeValidacao(
        `titulo deve ter no máximo ${TAMANHO_MAXIMO_TITULO} caracteres`,
      );
    }
    if (!PRIORIDADES.has(prioridade)) {
      throw new ErroDeValidacao(
        `prioridade deve ser uma de: ${[...PRIORIDADES].join(', ')}`,
      );
    }

    const tarefa = {
      id: this.#proximoId++,
      titulo: tituloLimpo,
      prioridade,
      concluida: false,
      criadaEm: this.#agora().toISOString(),
      concluidaEm: null,
    };
    this.#tarefas.set(tarefa.id, tarefa);
    return { ...tarefa };
  }

  listar({ concluida = null, prioridade = null } = {}) {
    let itens = [...this.#tarefas.values()];
    if (concluida !== null) itens = itens.filter((t) => t.concluida === concluida);
    if (prioridade !== null) itens = itens.filter((t) => t.prioridade === prioridade);
    // ordem estável: alta primeiro, depois por id
    const peso = { alta: 0, media: 1, baixa: 2 };
    itens.sort((a, b) => peso[a.prioridade] - peso[b.prioridade] || a.id - b.id);
    return itens.map((t) => ({ ...t }));
  }

  obter(id) {
    const tarefa = this.#tarefas.get(Number(id));
    if (!tarefa) throw new NaoEncontrado(`tarefa ${id} não existe`);
    return { ...tarefa };
  }

  concluir(id) {
    const tarefa = this.#tarefas.get(Number(id));
    if (!tarefa) throw new NaoEncontrado(`tarefa ${id} não existe`);
    if (tarefa.concluida) return { ...tarefa }; // idempotente de propósito
    tarefa.concluida = true;
    tarefa.concluidaEm = this.#agora().toISOString();
    return { ...tarefa };
  }

  remover(id) {
    if (!this.#tarefas.delete(Number(id))) {
      throw new NaoEncontrado(`tarefa ${id} não existe`);
    }
  }

  get total() {
    return this.#tarefas.size;
  }
}
