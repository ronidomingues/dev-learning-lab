---
description: Lista todas as rotas HTTP realmente implementadas, lidas do código-fonte.
---

Comando no formato antigo (`.claude/commands/`), mantido de propósito para mostrar que
ele continua funcionando e é equivalente a uma skill sem arquivos de apoio.

Rotas declaradas no roteador:

!`grep -n "url.pathname\|partes\[" src/servidor.js`

Com base **apenas** na saída acima e no conteúdo de @src/servidor.js, monte a tabela
`método | rota | status de sucesso | erros possíveis`. Não invente rota que não esteja
no código. Se alguma rota estiver no README e não no código, diga isso explicitamente.
