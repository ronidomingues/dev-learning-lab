# agente-tarefas

Projeto-modelo do curso [agentes-de-ia](../00-MAPA.md). Um gerenciador de
tarefas minúsculo, exposto ao Claude Code por um servidor MCP escrito à mão.

## Regras deste projeto

- O banco é `tarefas.db` (SQLite, criado na primeira execução). **Nunca**
  edite o `.db` com `sqlite3` na mão: use as ferramentas `mcp__tarefas__*`.
  O ponto do projeto é exercitar o caminho pelas ferramentas.
- `mcp_tarefas.py` não tem dependências externas, e deve continuar assim.
  Se precisar de uma biblioteca, discuta antes.
- Toda mudança em `mcp_tarefas.py` exige rodar `python3 teste_mcp.py`.
  O hook `PostToolUse` faz isso automaticamente — leia a saída dele.
- Mensagens de erro de ferramenta são lidas pelo modelo. Escreva-as dizendo
  **como corrigir**, não só que falhou.

## Comandos

```bash
python3 teste_mcp.py                     # 19 verificações, sem rede
python3 agente_minimo.py "sua pergunta"  # exige ANTHROPIC_API_KEY
rm -f tarefas.db                         # zera o estado
```
