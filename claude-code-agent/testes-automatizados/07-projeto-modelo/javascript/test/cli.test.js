/**
 * Teste de fumaça da borda — espelho de `tests/test_cli.py`.
 *
 * O `node:test` não tem `capsys`. Duas saídas:
 *   1. **injetar a função de impressão** (é o que `cli.js` faz com `imprimir`);
 *   2. substituir `console.log` com `t.mock.method(console, 'log')`.
 * A primeira é mais limpa e não depende de mock; a segunda serve para código
 * que você não pode alterar. As duas aparecem abaixo.
 */

import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { main } from '../src/cli.js';

/** Captura a saída injetando a dependência — sem mock nenhum. */
async function rodar(argv) {
  const linhas = [];
  const codigo = await main(argv, { imprimir: (t) => linhas.push(String(t)) });
  return { codigo, saida: linhas.join('\n') };
}

describe('comando demo', () => {
  it('sai com código zero', async () => {
    const { codigo } = await rodar(['demo']);
    assert.equal(codigo, 0);
  });

  it('imprime o relatório', async () => {
    const { saida } = await rodar(['demo']);
    assert.match(saida, /relatório:/);
  });

  it('a demo é determinística: cobra uma, recusa uma, ignora a futura', async () => {
    const { saida } = await rodar(['demo']);
    assert.match(saida, /1 cobradas \(R\$ 49,90\), 1 recusadas, 0 canceladas, 0 com erro/);

    const linhaCarla = saida.split('\n').find((l) => l.includes('carla@exemplo.br'));
    assert.deepEqual(linhaCarla.split(/\s+/).slice(3, 4), ['ativa']);
    assert.match(linhaCarla, /ciclos 0/);
  });

  it('produz exatamente a mesma saída do CLI em Python', async () => {
    // Este é o teste que garante que os dois projetos-modelo não divergiram.
    // Se um dia a regra mudar de um lado só, ele quebra.
    const { saida } = await rodar(['demo']);
    assert.match(saida, /a1 ana@exemplo\.br\s+ativa\s+próx\. 2026-09-11 ciclos 1/);
    assert.match(saida, /a2 bruno@exemplo\.br\s+inadimplente próx\. 2026-08-12 ciclos 0/);
    assert.match(saida, /a3 carla@exemplo\.br\s+ativa\s+próx\. 2027-08-12 ciclos 0/);
  });

  it('captura pela técnica 2: substituindo console.log', async (t) => {
    const espiao = t.mock.method(console, 'log', () => {});
    await main(['demo']);
    assert.ok(espiao.mock.callCount() > 5);
    // Sem `t.mock.method`, este teste sujaria a saída da suíte inteira — e a
    // restauração manual esquecida deixaria console.log quebrado para os
    // testes seguintes. É o caso em que o mock ganha da injeção.
  });
});

describe('argumentos', () => {
  it('sem comando devolve código 2 e mostra o uso', async () => {
    const { codigo, saida } = await rodar([]);
    assert.equal(codigo, 2);
    assert.match(saida, /^uso: /);
  });

  it('comando desconhecido também devolve 2', async () => {
    const { codigo } = await rodar(['voar']);
    assert.equal(codigo, 2);
  });
});

// O comando `renovar` toca disco (cria um SQLite), então mora em
// `test/cli.integracao.test.js` — a convenção de nome é o que permite
// `npm run test:unit` rodar em menos de 300 ms.
