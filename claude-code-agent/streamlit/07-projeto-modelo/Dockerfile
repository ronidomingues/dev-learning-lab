# Imagem de produção. Três decisões que importam:
#
# 1. `--no-cache-dir` e uma camada só para dependências: o `COPY . .` invalida a
#    camada seguinte a cada mudança de código; as dependências, não.
# 2. Usuário sem privilégio: se alguém escapar do processo, não é root.
# 3. HEALTHCHECK no endpoint que o próprio Streamlit expõe (`/_stcore/health`).
#    O orquestrador precisa de um sinal melhor que "o processo está vivo".
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PAINEL_AMBIENTE=prod \
    PAINEL_BANCO=/dados/painel.db

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --uid 10001 painel \
 && mkdir -p /dados && chown -R painel:painel /dados /app
USER painel

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').read()==b'ok' else 1)"

# --server.address=0.0.0.0 é obrigatório em contêiner: o padrão escuta só no
# localhost DE DENTRO do contêiner, e a porta publicada não chega em ninguém.
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
