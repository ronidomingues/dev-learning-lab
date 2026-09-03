#!/usr/bin/env python3
"""
cofre-tls · cliente
===================
Cliente de linha de comando que fala com o servidor usando um certificado.

    ./cliente.py --como admin    saude
    ./cliente.py --como leitor   listar
    ./cliente.py --como escritor criar "minha nota"
    ./cliente.py --como leitor   criar "vai dar 403"
    ./cliente.py --como admin    apagar 1
    ./cliente.py --como intruso  listar     # certificado de outra CA: nem conecta

O que este arquivo demonstra:

* como um cliente verifica o SERVIDOR (`check_hostname` + `load_verify_locations`);
* como um cliente se apresenta (`load_cert_chain`);
* que a falha de TLS acontece ANTES do HTTP — o erro que você vê é de handshake,
  não um código de status. Distinguir os dois é metade da depuração de mTLS.

Somente biblioteca padrão.
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
PKI = BASE / "pki"


def contexto(identidade: str, ca: Path | None = None) -> ssl.SSLContext:
    """Contexto TLS do CLIENTE."""
    # PROTOCOL_TLS_CLIENT já liga check_hostname e CERT_REQUIRED. Usar
    # SSLContext(PROTOCOL_TLS) "cru" é o erro que desliga a verificação sem avisar.
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    # Confiamos APENAS na CA do projeto — não no repositório do sistema.
    ctx.load_verify_locations(str(ca or PKI / "ca.crt"))

    # Nossa identidade. Se estes arquivos não existirem, o handshake falha com
    # "certificate required" vindo do servidor.
    cert, chave = PKI / f"{identidade}.crt", PKI / f"{identidade}.key"
    if cert.exists() and chave.exists():
        ctx.load_cert_chain(str(cert), str(chave))
    elif identidade != "anonimo":
        raise SystemExit(f"não encontrei {cert} / {chave} — rode ./criar-pki.sh")
    return ctx


def chamar(ctx: ssl.SSLContext, base: str, caminho: str,
           metodo: str = "GET", corpo: dict | None = None) -> tuple[int, object]:
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(base + caminho, data=dados, method=metodo)
    if dados:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            texto = r.read().decode() or "{}"
            return r.status, json.loads(texto) if texto.strip() else {}
    except urllib.error.HTTPError as e:            # erro de APLICAÇÃO (403, 404…)
        texto = e.read().decode() or "{}"
        return e.code, json.loads(texto) if texto.strip() else {}
    except ssl.SSLError as e:                      # erro de TLS (handshake)
        return 0, {"erro_tls": str(e)}
    except urllib.error.URLError as e:             # inclui SSLError embrulhado
        return 0, {"erro_conexao": str(e.reason)}


def main() -> int:
    p = argparse.ArgumentParser(description="cliente do cofre-tls")
    p.add_argument("--como", default="leitor",
                   help="identidade: admin | escritor | leitor | banido | vencido | intruso | anonimo")
    p.add_argument("--url", default="https://localhost:8443")
    p.add_argument("acao", choices=["saude", "listar", "criar", "apagar"])
    p.add_argument("argumento", nargs="?")
    a = p.parse_args()

    ctx = contexto(a.como)
    if a.acao == "saude":
        cod, res = chamar(ctx, a.url, "/saude")
    elif a.acao == "listar":
        cod, res = chamar(ctx, a.url, "/notas")
    elif a.acao == "criar":
        if not a.argumento:
            p.error("criar exige o texto da nota")
        cod, res = chamar(ctx, a.url, "/notas", "POST", {"texto": a.argumento})
    else:
        if not a.argumento:
            p.error("apagar exige o id")
        cod, res = chamar(ctx, a.url, f"/notas/{a.argumento}", "DELETE")

    print(f"[{a.como}] HTTP {cod}: {json.dumps(res, ensure_ascii=False)}")
    return 0 if 200 <= cod < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
