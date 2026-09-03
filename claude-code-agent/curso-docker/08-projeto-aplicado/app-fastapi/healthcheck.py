"""Healthcheck do container, sem curl.

Por que não `HEALTHCHECK CMD curl -f http://localhost:8000/health`?
Porque a imagem python:slim NÃO tem curl. Instalar curl só para isso
adiciona pacote, superfície de ataque e CVEs à imagem final. A imagem
já tem Python — então o healthcheck usa Python.

Sai com 0 = healthy, 1 = unhealthy. É esse exit code que o Docker lê.

--------------------------------------------------------------------
ARMADILHA REAL (encontrada ao validar este curso, não é hipotética):
se houver HTTP_PROXY/HTTPS_PROXY no ambiente, o urllib do Python tenta
mandar até o 127.0.0.1 para o proxy e o healthcheck falha com 502,
enquanto `curl` no mesmo endereço responde 200 — porque o urllib não
casa entradas de `no_proxy` que tenham espaço depois da vírgula
("localhost, 127.0.0.0/8"), e o curl casa.

Sintoma: container marcado `unhealthy` embora a aplicação esteja no ar.
Correção: um opener com ProxyHandler({}) vazio, que ignora proxy sempre.
Chamada a localhost jamais deve passar por proxy.
--------------------------------------------------------------------
"""
import sys
import urllib.request

URL = "http://127.0.0.1:8000/health"

# ProxyHandler({}) = "nenhum proxy", imune a qualquer variável de ambiente.
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

try:
    with opener.open(URL, timeout=3) as resposta:
        sys.exit(0 if resposta.status == 200 else 1)
except Exception:
    sys.exit(1)
