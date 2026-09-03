---
paths:
  - "test/**/*.js"
  - "src/**/*.js"
---

# Regras de teste

Carregado só quando o Claude toca em `src/` ou `test/` — por isso pode ser detalhado
sem custar contexto em toda sessão.

- Um `test(...)` por comportamento, com nome que descreve o **comportamento**, não a função.
  Bom: `rejeita título vazio`. Ruim: `testa criar`.
- Toda validação numérica ou de tamanho ganha **teste de fronteira**: o valor limite que
  passa e o primeiro que falha. Veja `rejeita título longo demais na fronteira`.
- Tempo nunca vem de `new Date()` dentro do código testado: injete o relógio, como em
  `new RepositorioDeTarefas(() => new Date('2026-08-13T12:00:00.000Z'))`.
- Testes de HTTP sobem o servidor em porta 0 (`servidor.listen(0)`) e fecham em `t.after`.
  Nunca fixe uma porta: dois testes em paralelo colidiriam.
- Nada de `mock` do módulo inteiro. Se um teste precisa de mock pesado, o problema é o
  desenho do código — conserte o desenho.
- Asserções com `node:assert/strict`. `assert.equal` já é estrito nesse import.
