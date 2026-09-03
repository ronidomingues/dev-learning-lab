# Makefile do historiador de planta.
# `make` sem argumento constrói o banco e roda tudo.
#
# Se você não tem `make` (Windows sem WSL), os comandos equivalentes estão
# no README.md — cada alvo é uma linha só.

PY ?= python3
BANCO ?= planta.db

.PHONY: tudo banco consultas teste plano limpar shell

tudo: banco consultas teste

banco: $(BANCO)

$(BANCO): sql/001-esquema.sql sql/002-views.sql sql/003-seed-cadastro.sql scripts/gerar_dados.py
	$(PY) scripts/gerar_dados.py $(BANCO)

consultas: banco
	$(PY) scripts/consultar.py

plano: banco
	$(PY) scripts/consultar.py --plano

teste: banco
	$(PY) -m unittest discover -s testes -v

shell: banco
	sqlite3 $(BANCO)

limpar:
	rm -f $(BANCO) $(BANCO)-wal $(BANCO)-shm
