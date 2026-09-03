# central-de-pedidos — atalhos.  Rode `make` para ver a lista.
SHELL := /bin/bash
COMPOSE := docker compose

.DEFAULT_GOAL := ajuda

.PHONY: ajuda preparar subir importar publicar reiniciar testar logs psql relatorio parar limpar

ajuda:  ## mostra esta ajuda
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

preparar:  ## gera .env e a credencial do Postgres (rode uma vez)
	@./scripts/preparar.sh

subir: preparar  ## sobe n8n + Postgres
	$(COMPOSE) up -d
	@echo "aguardando o n8n responder..."
	@until curl -sf http://localhost:5678/healthz >/dev/null; do sleep 2; done
	@echo "✓ n8n no ar em http://localhost:5678"

importar:  ## importa credencial e os 4 workflows
	$(COMPOSE) exec -T n8n n8n import:credentials --input=/import/credenciais/postgres.json
	$(COMPOSE) exec -T n8n n8n import:workflow --separate --input=/import/workflows
	@echo "✓ importado. Agora rode: make publicar"

publicar:  ## publica (ativa) os workflows e reinicia o n8n
	-$(COMPOSE) exec -T n8n n8n publish:workflow --id=cp01receberpedido
	-$(COMPOSE) exec -T n8n n8n publish:workflow --id=cp02consultarped
	-$(COMPOSE) exec -T n8n n8n publish:workflow --id=cp03relatoriodia
	-$(COMPOSE) exec -T n8n n8n publish:workflow --id=cp04alertafalhas
	$(MAKE) reiniciar

reiniciar:  ## reinicia o n8n (necessario apos mexer por CLI)
	$(COMPOSE) restart n8n
	@until curl -sf http://localhost:5678/healthz >/dev/null; do sleep 2; done
	@echo "✓ n8n reiniciado"

testar:  ## roda o teste de ponta a ponta
	@set -a; . ./.env; set +a; ./scripts/testar.sh

logs:  ## acompanha os logs do n8n
	$(COMPOSE) logs -f n8n

psql:  ## abre o psql no banco do projeto
	@set -a; . ./.env; set +a; $(COMPOSE) exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB

relatorio:  ## roda o relatorio diario agora, sem esperar as 07:00
	$(COMPOSE) exec -T n8n n8n execute --id=cp03relatoriodia
	@ls -l saida/

parar:  ## para tudo (os dados ficam)
	$(COMPOSE) down

limpar:  ## APAGA TUDO, inclusive os volumes e os dados
	$(COMPOSE) down -v
	rm -f .env credenciais/postgres.json
	rm -f saida/*.csv
