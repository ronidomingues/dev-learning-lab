# Makefile — atalhos para os comandos do projeto.
# Rode `make` sem argumento para ver a lista.

.DEFAULT_GOAL := ajuda
.PHONY: ajuda subir derrubar logs testes dev shell saude backup restaurar limpar reconstruir tamanho

ajuda:  ## Mostra esta ajuda
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

subir:  ## Sobe a stack (proxy + api) em segundo plano e espera ficar saudável
	@test -f .env || (echo "crie o .env primeiro:  cp .env.example .env" && exit 1)
	docker compose up -d --build --wait
	@echo "pronto: http://localhost:$${PORTA_PUBLICA:-8080}"

derrubar:  ## Para e remove containers e redes (os volumes SÃO PRESERVADOS)
	docker compose down

logs:  ## Acompanha os logs de todos os serviços
	docker compose logs -f

testes:  ## Roda a suíte de testes num container efêmero
	docker compose --profile testes run --rm testes

dev:  ## Sobe o modo de desenvolvimento com recarga automática (porta 3000)
	docker compose --profile dev up --build

shell:  ## Abre um shell dentro do container da api
	docker compose exec api sh

saude:  ## Mostra o estado do healthcheck da api
	@docker inspect --format '{{json .State.Health}}' $$(docker compose ps -q api) | \
		python3 -m json.tool 2>/dev/null || \
		docker inspect --format '{{.State.Health.Status}}' $$(docker compose ps -q api)

backup:  ## Salva o volume de dados em ./backups/
	@mkdir -p backups
	docker run --rm -v mural_dados-mural:/dados:ro -v "$$PWD/backups:/backup" alpine \
		tar czf /backup/dados-$$(date +%F_%H%M%S).tgz -C /dados .
	@ls -lh backups | tail -1

restaurar:  ## Restaura o backup mais recente de ./backups/ (ARQUIVO=... para escolher outro)
	@ARQ=$${ARQUIVO:-$$(ls -1t backups/*.tgz | head -1)}; \
	echo "restaurando $$ARQ"; \
	docker compose stop api; \
	docker run --rm -v mural_dados-mural:/dados -v "$$PWD/backups:/backup" alpine \
		sh -c "rm -rf /dados/* && tar xzf /backup/$$(basename $$ARQ) -C /dados"; \
	docker compose start api

tamanho:  ## Mostra o tamanho da imagem e as camadas que mais pesam
	@docker images mural-de-recados:1.0 --format "imagem: {{.Size}}"
	@docker history mural-de-recados:1.0 --format "table {{.Size}}\t{{.CreatedBy}}" | head -12

reconstruir:  ## Reconstrói do zero, sem cache
	docker compose build --no-cache

limpar:  ## ⚠️ Derruba tudo E APAGA OS VOLUMES (perde os recados)
	docker compose down -v
