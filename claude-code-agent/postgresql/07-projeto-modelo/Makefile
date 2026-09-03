# Makefile — atalhos do projeto. Rode `make` para ver a lista.
.DEFAULT_GOAL := ajuda
.PHONY: ajuda subir derrubar psql testes logs backup limpar reaplicar-schema

ajuda:  ## Mostra esta ajuda
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n",$$1,$$2}'

subir:  ## Sobe banco + app (o schema é aplicado na primeira vez)
	@test -f .env || (echo "crie o .env:  cp .env.example .env" && exit 1)
	docker compose up -d --build
	@echo "app: http://localhost:3000/livros   ·   banco: localhost:5432"

derrubar:  ## Para e remove os containers (os dados PERMANECEM no volume)
	docker compose down

psql:  ## Abre um psql no banco
	docker compose exec db psql -U biblioteca -d biblioteca

testes:  ## Roda os testes de integração contra o banco
	docker compose --profile testes run --rm testes

logs:  ## Acompanha os logs
	docker compose logs -f

backup:  ## Faz um backup verificado em ./backups
	./scripts/backup.sh

reaplicar-schema:  ## Reaplica o schema num banco JÁ existente (⚠️ apaga as tabelas)
	@for f in schema/001_schema.sql schema/002_functions.sql schema/003_seed.sql; do \
		echo ">> $$f"; docker compose exec -T db psql -v ON_ERROR_STOP=1 -U biblioteca -d biblioteca < $$f; \
	done

limpar:  ## ⚠️ Derruba tudo e APAGA o volume de dados
	docker compose down -v
