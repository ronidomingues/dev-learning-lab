// repositorio.js — persistência em arquivo JSON, com escrita atômica.
//
// Este é o ponto do projeto que ensina VOLUME. O arquivo vive em /dados, que no compose.yaml
// é um volume nomeado. Sem o volume, tudo aqui morre junto com o container — e essa é
// exatamente a demonstração pedida no laboratório 2 do README.
//
// Por que arquivo JSON e não um banco de verdade: para o projeto rodar com ZERO dependências
// de npm, o que o torna reproduzível sem rede no momento do build. O README explica como
// trocar por Postgres, que é o próximo passo natural.

import { randomUUID } from 'node:crypto';
import { readFile, writeFile, rename, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

export class ErroValidacao extends Error {
  constructor(mensagem) {
    super(mensagem);
    this.name = 'ErroValidacao';
  }
}

export class Repositorio {
  #caminho;
  #limite;
  #tamanhoMaxTexto;
  #cache = null;

  // Serializa as escritas: sem isto, duas requisições simultâneas leem o mesmo estado,
  // cada uma acrescenta o seu recado e uma sobrescreve a outra (lost update).
  #fila = Promise.resolve();

  constructor({ caminho, limite = 500, tamanhoMaxTexto = 280 }) {
    this.#caminho = caminho;
    this.#limite = limite;
    this.#tamanhoMaxTexto = tamanhoMaxTexto;
  }

  async iniciar() {
    await mkdir(dirname(this.#caminho), { recursive: true });
    this.#cache = await this.#lerDoDisco();
    return this.#cache.length;
  }

  async #lerDoDisco() {
    try {
      const bruto = await readFile(this.#caminho, 'utf8');
      const dados = JSON.parse(bruto);
      if (!Array.isArray(dados)) throw new Error('conteúdo não é uma lista');
      return dados;
    } catch (e) {
      // Arquivo ainda não existe: primeira execução. Estado inicial vazio é legítimo.
      if (e.code === 'ENOENT') return [];
      // Arquivo corrompido: NÃO apagamos silenciosamente. Propagar é mais honesto que
      // fingir que o mural sempre esteve vazio.
      throw new Error(`arquivo de dados ilegível em ${this.#caminho}: ${e.message}`);
    }
  }

  // Escrita atômica: grava num temporário e renomeia. `rename` no mesmo sistema de arquivos
  // é atômico no Linux — ou o arquivo antigo está lá, ou o novo, nunca metade dos dois.
  // Se o container morrer no meio de um writeFile direto, o JSON fica truncado e o app não
  // sobe mais. Esta é a diferença entre um exemplo de tutorial e código que aguenta um kill.
  async #gravar(dados) {
    const temporario = `${this.#caminho}.tmp`;
    await writeFile(temporario, JSON.stringify(dados, null, 2), 'utf8');
    await rename(temporario, this.#caminho);
  }

  #enfileirar(tarefa) {
    const resultado = this.#fila.then(tarefa, tarefa);
    // A fila não pode "quebrar" por causa de uma falha; ela segue para a próxima tarefa.
    this.#fila = resultado.then(
      () => undefined,
      () => undefined,
    );
    return resultado;
  }

  listar({ limite = 50 } = {}) {
    return this.#cache.slice(-limite).reverse();
  }

  total() {
    return this.#cache.length;
  }

  validar({ autor, texto }) {
    if (typeof autor !== 'string' || autor.trim().length === 0) {
      throw new ErroValidacao('campo "autor" é obrigatório');
    }
    if (autor.trim().length > 60) {
      throw new ErroValidacao('campo "autor" excede 60 caracteres');
    }
    if (typeof texto !== 'string' || texto.trim().length === 0) {
      throw new ErroValidacao('campo "texto" é obrigatório');
    }
    if (texto.trim().length > this.#tamanhoMaxTexto) {
      throw new ErroValidacao(`campo "texto" excede ${this.#tamanhoMaxTexto} caracteres`);
    }
    return { autor: autor.trim(), texto: texto.trim() };
  }

  async adicionar(entrada) {
    const limpo = this.validar(entrada);
    return this.#enfileirar(async () => {
      const recado = {
        id: randomUUID(),
        autor: limpo.autor,
        texto: limpo.texto,
        criadoEm: new Date().toISOString(),
      };
      const proximo = [...this.#cache, recado];
      // Limite de crescimento: sem isto, o volume enche até o disco acabar.
      const podado = proximo.slice(-this.#limite);
      await this.#gravar(podado);
      this.#cache = podado;
      return recado;
    });
  }

  async remover(id) {
    return this.#enfileirar(async () => {
      const proximo = this.#cache.filter((r) => r.id !== id);
      if (proximo.length === this.#cache.length) return false;
      await this.#gravar(proximo);
      this.#cache = proximo;
      return true;
    });
  }

  // Usado pelo healthcheck: confirma que o disco ainda aceita escrita. Um healthcheck que só
  // responde "ok" sem tocar na dependência crítica não informa nada.
  async verificarSaude() {
    const sonda = `${this.#caminho}.saude`;
    await writeFile(sonda, String(Date.now()), 'utf8');
    return true;
  }
}
