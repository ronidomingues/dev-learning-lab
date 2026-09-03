# Makefile do crackme — projeto-modelo de engenharia reversa
#
# Alvos:
#   make            -> compila ./crackme (com símbolos, mais fácil de reverter)
#   make stripped   -> ./crackme_stripped (sem símbolos, mais realista/difícil)
#   make hard       -> ./crackme_hard (otimizado -O2 e stripped, o mais difícil)
#   make run        -> testa manualmente os três níveis com as respostas certas
#   make solve      -> roda o solucionador automático (solver.py) e valida
#   make check      -> compila tudo e roda a suíte de verificação (test.sh)
#   make clean      -> remove os binários gerados
#
# Por que compilar de várias formas? Para o aluno comparar como símbolos e
# otimização mudam DRASTICAMENTE a dificuldade da engenharia reversa.

CC      ?= gcc
CFLAGS  ?= -Wall -Wextra -std=c11
# -g: inclui símbolos de depuração (nomes de função/variável) -> alvo fácil
# -O0: sem otimização -> assembly mais próximo do C original
EASY_FLAGS = -g -O0

.PHONY: all stripped hard run solve check clean

all: crackme

crackme: crackme.c
	$(CC) $(CFLAGS) $(EASY_FLAGS) -o $@ $<
	@echo "[ok] ./crackme compilado (com simbolos). Reverta com: gdb ./crackme"

# Versão "stripped": remove a tabela de símbolos. Nomes de função somem.
crackme_stripped: crackme.c
	$(CC) $(CFLAGS) -O0 -o $@ $<
	strip $@
	@echo "[ok] ./crackme_stripped (sem simbolos) — mais realista"

# Versão difícil: otimizada e stripped. O compilador reorganiza tudo.
crackme_hard: crackme.c
	$(CC) $(CFLAGS) -O2 -s -o $@ $<
	@echo "[ok] ./crackme_hard (-O2, stripped) — o mais dificil"

stripped: crackme_stripped
hard: crackme_hard

# Demonstra as respostas corretas (o "gabarito" vivo).
run: crackme
	@echo "== Nivel 1 (senha em texto claro) =="
	./crackme 1 engenharia-reversa-2026 || true
	@echo "== Nivel 2 (senha por XOR) =="
	./crackme 2 GhidraRadare || true
	@echo "== Nivel 3 (serial por regras) — exemplo valido =="
	./crackme 3 0700-9998-0000 || true

# Roda o solucionador automatico em Python (encontra as respostas sozinho).
solve: crackme
	python3 solver.py ./crackme

# Suite de verificacao completa.
check: crackme crackme_stripped crackme_hard
	bash test.sh

clean:
	rm -f crackme crackme_stripped crackme_hard
	@echo "[ok] binarios removidos"
