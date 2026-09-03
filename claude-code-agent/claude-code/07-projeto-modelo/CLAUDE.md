# API de Tarefas

API HTTP mínima em Node, **sem dependências externas**. Existe para servir de
alvo a uma configuração completa de Claude Code (regras, hooks, subagente, skills).

## Comandos

- `npm test` — roda toda a suíte (`node --test`). **Precisa passar antes de qualquer commit.**
- `npm start` — sobe o servidor em `http://localhost:3000` (variável `PORTA` muda a porta).
- `npm run verificar` — valida a configuração do `.claude/` e roda os testes.

## Arquitetura

- `src/tarefas.js` — domínio puro. Sem HTTP, sem I/O, sem `new Date()` solto: o relógio é injetado.
- `src/servidor.js` — só traduz HTTP ↔ domínio. **Nenhuma regra de negócio aqui.**
- `src/index.js` — ponto de entrada e desligamento gracioso.
- `test/` — testes com `node:test`; um arquivo por módulo de `src/`.

## Convenções

- ESM (`import`/`export`), nunca `require`.
- Zero dependências de produção. Antes de sugerir um pacote, pergunte.
- Erros de domínio são classes com `status`; a camada HTTP só as traduz.
- Nomes de identificadores em português, como o resto do repositório.
- Toda mudança em `src/` vem acompanhada de teste em `test/`.

## O que não fazer

- Não editar `.env` nem arquivos fora deste diretório.
- Não fazer commit sem `npm test` verde.
- Não trocar `node:test` por outro runner sem discussão.
