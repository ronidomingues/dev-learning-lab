// Cliente HTTP do catálogo. É aqui que mora o "lado de fora" do optimistic locking:
// guardar o ETag recebido no GET e devolvê-lo no If-Match do PUT.

import { comRetentativa } from './retry.js';

/** Erro que representa um 412 vindo do servidor. */
export class ConflitoHttp extends Error {
  constructor(corpo, etag) {
    super(`412: versão enviada ${corpo.versao_enviada}, atual ${corpo.versao_atual}`);
    this.name = 'ConflitoDeVersao'; // mesmo nome do erro do repo: a política de retry serve aos dois
    this.corpo = corpo;
    this.etag = etag;
  }
}

export function criarCliente(base) {
  const url = (p) => new URL(p, base).toString();

  async function obter(id) {
    const r = await fetch(url(`/produtos/${id}`));
    if (!r.ok) throw new Error(`GET ${id}: HTTP ${r.status}`);
    return { produto: await r.json(), etag: r.headers.get('etag') };
  }

  async function salvar(id, etag, campos, autor = 'anon') {
    const cabecalhos = { 'content-type': 'application/json', 'x-autor': autor };
    if (etag !== null && etag !== undefined) cabecalhos['if-match'] = etag;

    const r = await fetch(url(`/produtos/${id}`), {
      method: 'PUT',
      headers: cabecalhos,
      body: JSON.stringify(campos),
    });
    if (r.status === 412) throw new ConflitoHttp(await r.json(), r.headers.get('etag'));
    if (!r.ok) throw new Error(`PUT ${id}: HTTP ${r.status} ${await r.text()}`);
    return { produto: await r.json(), etag: r.headers.get('etag') };
  }

  /**
   * Leitura-modificação-escrita segura: relê a cada tentativa e reaplica `transformar`
   * sobre o estado NOVO. Reler é obrigatório — retentar com o mesmo ETag falha para sempre.
   */
  async function editar(id, transformar, opts = {}) {
    return comRetentativa(async () => {
      const { produto, etag } = await obter(id);
      const campos = transformar(produto);
      return salvar(id, etag, campos, opts.autor);
    }, opts);
  }

  /** Versão deliberadamente quebrada, usada na demonstração. Não copie. */
  async function editarSemProtecao(id, transformar) {
    const { produto } = await obter(id);
    const campos = transformar(produto);
    const r = await fetch(url(`/inseguro/produtos/${id}`), {
      method: 'PUT',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(campos),
    });
    return r.json();
  }

  async function baixarEstoque(id, qtd) {
    const r = await fetch(url(`/produtos/${id}/baixa`), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ qtd }),
    });
    return { status: r.status, corpo: await r.json() };
  }

  async function auditoria(id) {
    const r = await fetch(url(`/auditoria/${id}`));
    return r.json();
  }

  return { obter, salvar, editar, editarSemProtecao, baixarEstoque, auditoria };
}
