---
name: relatorio
description: Gera o relatório semanal de tarefas em Markdown, no formato da equipe. Use quando pedirem "relatório", "resumo da semana" ou "status das tarefas".
---

# Relatório semanal de tarefas

Siga exatamente estes passos.

1. Chame `mcp__tarefas__estatisticas` para os totais.
2. Chame `mcp__tarefas__listar_tarefas` com `status: "aberta"`.
3. Chame `mcp__tarefas__listar_tarefas` com `status: "concluida"`.
4. Monte o Markdown abaixo. **Não invente seções nem reordene.**

```markdown
# Status — <data de hoje, formato DD/MM/AAAA>

**Concluídas:** <n>  ·  **Abertas:** <n>

## Abertas, por prioridade
- **alta** — #id título
- **media** — #id título
- **baixa** — #id título

## Concluídas nesta rodada
- #id título

## Atenção
<uma linha, só se houver alguma tarefa de prioridade alta ainda aberta;
caso contrário, omita a seção inteira>
```

Se não houver nenhuma tarefa, responda apenas `Nenhuma tarefa registrada.` e
não gere o relatório.

## Por que isso é uma skill e não uma linha no CLAUDE.md

O `CLAUDE.md` entra no contexto em **toda** sessão. Este formato só interessa
quando alguém pede o relatório — uma vez por semana. Como skill, apenas a
linha `description` acima fica no contexto; o corpo só é carregado quando o
pedido casa. Ver [18-skills-plugins-extensibilidade.md](../../../../18-skills-plugins-extensibilidade.md).
