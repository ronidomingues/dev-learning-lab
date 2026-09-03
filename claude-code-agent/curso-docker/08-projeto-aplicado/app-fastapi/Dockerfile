# syntax=docker/dockerfile:1
# ^ Habilita a sintaxe moderna do BuildKit (--mount=type=cache, etc.)

# =====================================================================
# ESTÁGIO 1 — builder: compila as dependências
# =====================================================================
# Só existe para produzir a pasta de pacotes instalados. Tudo que for
# ferramenta de compilação (gcc, headers) morre com este estágio e NÃO
# entra na imagem final. É isso que "multi-stage" resolve.
FROM python:3.12-slim-trixie AS builder

# Boas práticas de Python em container:
#   PYTHONDONTWRITEBYTECODE=1 -> não gera .pyc (lixo na imagem)
#   PYTHONUNBUFFERED=1        -> log sai na hora, sem ficar preso no buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Instala toolchain de compilação. asyncpg tem extensão em C: sem gcc,
# o pip tenta compilar e falha com "error: command 'gcc' failed".
# O `rm -rf /var/lib/apt/lists/*` NA MESMA camada é obrigatório: se for
# em um RUN separado, os arquivos já estão gravados na camada anterior
# e a imagem não encolhe.
# DL3008 pede pinar a versão do pacote apt. Aqui a gente ignora DE PROPÓSITO:
#   - este pacote existe só no builder e NÃO vai para a imagem final;
#   - o pino quebra o build sozinho quando o Debian publica uma correção
#     de segurança (o .deb antigo some do mirror e o apt falha com 404).
# A reprodutibilidade que importa vem de duas outras coisas: a tag de suite
# fixa acima (slim-trixie) e o pino exato do requirements.txt.
# (a diretiva abaixo precisa ser a ÚLTIMA linha antes do RUN para valer)
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cria o virtualenv que será COPIADO inteiro para o estágio final.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# --- ORDEM DE CAMADAS: o ponto mais importante deste arquivo ---
# requirements.txt é copiado SOZINHO e instalado ANTES do código.
# Como o código muda toda hora e as dependências quase nunca, o Docker
# reaproveita a camada de pip install em ~99% dos builds.
# Se você fizesse `COPY . .` antes, cada `print()` novo invalidaria o
# cache e reinstalaria tudo. Diferença real: ~2s contra ~90s por build.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --require-hashes=false -r requirements.txt

# =====================================================================
# ESTÁGIO 2 — runtime: a imagem que vai para produção
# =====================================================================
FROM python:3.12-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Usuário não-root. Criado ANTES do COPY para que o chown funcione.
# UID fixo (10001) e não o próximo livre: assim as permissões de volume
# são previsíveis entre máquinas diferentes.
#   --system        -> conta de serviço, sem senha e sem login
#   --no-create-home-> o app não precisa de /home
RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Traz só o resultado do builder: o venv pronto. gcc e headers ficam para trás.
COPY --from=builder /opt/venv /opt/venv

# --chown no COPY evita um `RUN chown -R` depois, que duplicaria todos
# os arquivos em uma nova camada (imagem cresce ao dobro).
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup healthcheck.py ./

# Pasta de dados para o SQLite. Precisa existir e pertencer ao appuser,
# senão o container sobe e morre com "unable to open database file".
RUN mkdir -p /app/data && chown appuser:appgroup /app/data

# A partir daqui o processo roda sem privilégio. Se alguém escapar da
# aplicação, cai como appuser, não como root.
# Numérico (não `USER appuser`) de propósito: orquestradores como o
# Kubernetes precisam avaliar `runAsNonRoot` SEM abrir a imagem para ler
# o /etc/passwd. Com nome, eles não conseguem provar que não é root.
USER 10001:10001

EXPOSE 8000

# EXPOSE é documentação + descoberta; NÃO publica porta sozinho.
# Quem publica é `-p` no run ou `ports:` no compose.

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]

# Forma exec (JSON array), não forma shell. Na forma shell o processo
# vira filho de /bin/sh, que não repassa SIGTERM: o container ignora o
# `docker stop` e leva 10s de timeout até o SIGKILL.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
