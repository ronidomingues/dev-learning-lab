/**
 * Configuração do Vitest 4.
 *
 * Este projeto usa `node:test` como corredor principal (zero dependência) e
 * mantém a pasta `vitest/` só para demonstrar a tradução. Num projeto real você
 * escolheria UM dos dois — manter os dois é custo de manutenção sem benefício.
 */

import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Só os arquivos da pasta vitest/: os de test/ usam a API do node:test e
    // não rodariam aqui (`t.mock`, `assert.rejects` com opções etc.).
    include: ['vitest/**/*.vitest.js'],

    // `globals: false` é o padrão do Vitest e a recomendação: importar
    // `describe/it/expect` explicitamente evita colisão de nomes e faz o editor
    // resolver os tipos sem plugin. Jest, por herança, usa globais.
    globals: false,

    environment: 'node', // 'jsdom'/'happy-dom' quando houver DOM

    coverage: {
      provider: 'v8', // mesma instrumentação que o node:test usa
      include: ['src/**'],
      reporter: ['text', 'html'],
      thresholds: { lines: 60, branches: 60 },
    },

    // Falhar em vez de passar silenciosamente quando nenhum teste casar com o
    // filtro. Já custou horas de "os testes passaram" com zero testes rodando.
    passWithNoTests: false,
  },
});
