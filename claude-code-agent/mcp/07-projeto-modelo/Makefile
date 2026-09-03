.PHONY: ajuda instalar semear rodar http testar inspecionar limpar

ajuda:
	@echo "make instalar     — cria o ambiente e instala dependências"
	@echo "make semear       — cria o banco com o acervo de exemplo"
	@echo "make rodar        — sobe o servidor em stdio (para um host MCP)"
	@echo "make http         — sobe o servidor em http://127.0.0.1:8931/mcp"
	@echo "make testar       — roda a suíte de testes"
	@echo "make inspecionar  — lista as ferramentas com o MCP Inspector"
	@echo "make limpar       — apaga banco, cache e ambiente"

instalar:
	uv sync

semear:
	uv run python -c "from biblioteca import dados; dados.criar_esquema('biblioteca.db'); print('acervo criado em biblioteca.db')"

rodar:
	uv run python servidor.py

http:
	uv run python servidor.py --http

testar:
	uv run pytest

inspecionar:
	npx -y @modelcontextprotocol/inspector --cli uv run python servidor.py --method tools/list

limpar:
	rm -rf .venv .pytest_cache __pycache__ biblioteca/__pycache__ testes/__pycache__ biblioteca.db
