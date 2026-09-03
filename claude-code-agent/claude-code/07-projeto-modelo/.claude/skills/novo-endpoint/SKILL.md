---
name: novo-endpoint
description: Adiciona um endpoint novo à API de tarefas seguindo a arquitetura do projeto — domínio primeiro, teste junto, HTTP por último.
argument-hint: [método] [rota] [o que faz]
disable-model-invocation: true
allowed-tools: Read, Edit, Bash(npm test)
---

Adicione o endpoint pedido: **$ARGUMENTS**

Siga exatamente esta ordem. Ela não é decorativa: escrever o HTTP primeiro é o erro
que faz regra de negócio vazar para a camada de transporte.

1. **Domínio primeiro.** Implemente o comportamento em `src/tarefas.js` como método do
   `RepositorioDeTarefas`. Erros de entrada levantam `ErroDeValidacao`; recurso ausente
   levanta `NaoEncontrado`. Nunca use `new Date()` direto — use `this.#agora()`.
2. **Teste do domínio.** Em `test/tarefas.test.js`, adicione: caso feliz, caso de
   validação inválida e, se houver limite numérico ou de tamanho, o teste de fronteira.
3. **Camada HTTP.** Só agora edite `src/servidor.js`. A função deve apenas ler a
   requisição, chamar o domínio e traduzir a resposta. Zero `if` de negócio.
4. **Teste HTTP.** Em `test/servidor.test.js`, cubra o status de sucesso e pelo menos
   um status de erro, usando o helper `subir()` que já existe.
5. **Rode `npm test`.** Se falhar, conserte antes de responder. Não relate sucesso sem
   ter visto a saída verde.
6. **Documente** a rota nova no `README.md`, na tabela de endpoints.

Ao final, mostre apenas: as rotas novas, os testes adicionados e a contagem final da suíte.
