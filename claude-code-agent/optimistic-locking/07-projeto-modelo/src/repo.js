// Repositório: o único lugar do sistema que sabe escrever na tabela `produtos`.
// Toda a política de concorrência mora aqui. Se ela vazar para o controlador
// ou para o cliente, mais cedo ou mais tarde alguém escreve sem a guarda.

/** Erro de conflito otimista. Carrega o estado atual para permitir merge/diagnóstico. */
export class ConflitoDeVersao extends Error {
  constructor(esperada, atual, atualDoBanco) {
    super(`conflito de versão: cliente enviou ${esperada}, banco está em ${atual}`);
    this.name = 'ConflitoDeVersao';
    this.versaoEsperada = esperada;
    this.versaoAtual = atual;
    this.registroAtual = atualDoBanco; // permite ao chamador tentar um merge
  }
}

/** Erro para "o recurso não existe" — distinto de conflito, e o HTTP trata diferente. */
export class NaoEncontrado extends Error {
  constructor(id) {
    super(`produto ${id} não existe`);
    this.name = 'NaoEncontrado';
  }
}

/** Erro de regra de negócio: estoque insuficiente. */
export class EstoqueInsuficiente extends Error {
  constructor(pedido, disponivel) {
    super(`estoque insuficiente: pedido ${pedido}, disponível ${disponivel}`);
    this.name = 'EstoqueInsuficiente';
  }
}

export function buscar(db, id) {
  const row = db.prepare('SELECT * FROM produtos WHERE id = ?').get(id);
  if (!row) throw new NaoEncontrado(id);
  return { ...row }; // cópia rasa: o objeto devolvido por node:sqlite tem protótipo nulo
}

/**
 * ATUALIZAÇÃO OTIMISTA — o núcleo do projeto.
 *
 * A guarda inteira cabe em duas linhas de SQL:
 *
 *   UPDATE ... SET ..., version = version + 1
 *   WHERE id = ? AND version = ?      <-- se a versão mudou, 0 linhas afetadas
 *
 * Três propriedades que fazem isso funcionar e que quase todo tutorial omite:
 *
 * 1. A comparação e a escrita acontecem NO MESMO comando. Não existe janela entre
 *    "conferi a versão" e "gravei" — é o banco que garante a atomicidade da linha.
 *    Um `SELECT version` seguido de `UPDATE` seria exatamente o bug que queremos evitar.
 * 2. `version = version + 1` é calculado pelo banco, não pelo cliente. Se o cliente
 *    mandasse a nova versão, dois clientes poderiam mandar o mesmo número.
 * 3. Zero linhas afetadas é a DETECÇÃO. Não é erro do driver, não é exceção: é um
 *    número que você precisa conferir. Ignorar o retorno do UPDATE é o erro nº 1.
 */
export function atualizar(db, id, versaoEsperada, campos, autor = 'anon', agora = new Date().toISOString()) {
  if (!Number.isInteger(versaoEsperada)) {
    throw new TypeError('versaoEsperada precisa ser um inteiro');
  }

  const permitidos = ['nome', 'descricao', 'preco_centavos', 'estoque'];
  const chaves = Object.keys(campos).filter((k) => permitidos.includes(k));
  if (chaves.length === 0) throw new TypeError('nenhum campo atualizável enviado');

  const sets = chaves.map((k) => `${k} = ?`).join(', ');
  const valores = chaves.map((k) => campos[k]);

  // A transação envolve UPDATE + auditoria: ou os dois acontecem, ou nenhum.
  db.exec('BEGIN IMMEDIATE');
  try {
    const res = db
      .prepare(
        `UPDATE produtos
            SET ${sets}, version = version + 1, atualizado_em = ?
          WHERE id = ? AND version = ?`
      )
      .run(...valores, agora, id, versaoEsperada);

    if (res.changes === 0) {
      // Zero linhas: ou o registro sumiu, ou a versão mudou. Descobrimos qual.
      const atual = db.prepare('SELECT * FROM produtos WHERE id = ?').get(id);
      db.exec('ROLLBACK');
      if (!atual) throw new NaoEncontrado(id);
      throw new ConflitoDeVersao(versaoEsperada, atual.version, { ...atual });
    }

    const novo = db.prepare('SELECT * FROM produtos WHERE id = ?').get(id);
    db.prepare(
      'INSERT INTO auditoria (produto_id, version_nova, autor, quando) VALUES (?, ?, ?, ?)'
    ).run(id, novo.version, autor, agora);

    db.exec('COMMIT');
    return { ...novo };
  } catch (e) {
    // Se já demos ROLLBACK acima, este segundo tentará falhar; por isso o try vazio.
    try { db.exec('ROLLBACK'); } catch { /* transação já encerrada */ }
    throw e;
  }
}

/**
 * BAIXA DE ESTOQUE — o contraexemplo pedagógico.
 *
 * Aqui NÃO usamos versão. Um decremento é comutativo: se dois pedidos tiram 1 cada,
 * o resultado correto é -2, e não há conflito real a relatar ao usuário. Usar
 * optimistic locking aqui geraria conflitos falsos e retentativas inúteis.
 *
 * A guarda certa é a própria regra de negócio dentro do WHERE:
 *   WHERE id = ? AND estoque >= ?
 *
 * Regra prática: use optimistic locking quando a intenção do usuário é
 * "substituir o valor que eu li"; use UPDATE atômico relativo quando a intenção é
 * "aplicar este delta ao valor que estiver lá".
 */
export function baixarEstoque(db, id, qtd, agora = new Date().toISOString()) {
  if (!Number.isInteger(qtd) || qtd <= 0) throw new TypeError('qtd precisa ser inteiro positivo');

  const res = db
    .prepare(
      `UPDATE produtos
          SET estoque = estoque - ?, version = version + 1, atualizado_em = ?
        WHERE id = ? AND estoque >= ?`
    )
    .run(qtd, agora, id, qtd);

  if (res.changes === 0) {
    const atual = db.prepare('SELECT * FROM produtos WHERE id = ?').get(id);
    if (!atual) throw new NaoEncontrado(id);
    throw new EstoqueInsuficiente(qtd, atual.estoque);
  }
  return buscar(db, id);
}

/**
 * ATUALIZAÇÃO INSEGURA — existe só para o `npm run demo:perde` mostrar o bug.
 * NUNCA faça isso em produção. Note que ela também incrementa a versão:
 * é o padrão sutil de quem "implementou optimistic locking" mas esqueceu do WHERE.
 */
export function atualizarInseguro(db, id, campos, agora = new Date().toISOString()) {
  const permitidos = ['nome', 'descricao', 'preco_centavos', 'estoque'];
  const chaves = Object.keys(campos).filter((k) => permitidos.includes(k));
  const sets = chaves.map((k) => `${k} = ?`).join(', ');
  const valores = chaves.map((k) => campos[k]);
  const res = db
    .prepare(`UPDATE produtos SET ${sets}, version = version + 1, atualizado_em = ? WHERE id = ?`)
    .run(...valores, agora, id);
  if (res.changes === 0) throw new NaoEncontrado(id);
  return buscar(db, id);
}
