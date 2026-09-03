---
name: checar-tudo
description: Roda a verificação completa do projeto (configuração do .claude + suíte de testes) e relata o que quebrou, em uma tela.
context: fork
background: false
disable-model-invocation: true
allowed-tools: Bash(npm run verificar), Bash(npm test), Read
---

Rode `npm run verificar` e relate o resultado.

`context: fork` faz esta skill rodar num subagente que herda a conversa: toda a saída
ruidosa do script fica no contexto dele, e só o resumo volta para a sessão principal.
É o padrão para qualquer coisa que cospe muitas linhas.

Formato da resposta:

```
CONFIGURAÇÃO: ok | N problemas
TESTES: N passaram, M falharam
PROBLEMAS (se houver):
- <arquivo>: <o que está errado> → <como corrigir>
```

Não conserte nada sem me perguntar. Este comando é diagnóstico.
