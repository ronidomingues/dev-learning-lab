#!/usr/bin/env python3
"""
cofre-tls · servidor
====================
Uma API de notas protegida por **mTLS**: não há senha, não há token. A única
credencial é o certificado de cliente emitido pela CA do projeto.

O que este arquivo demonstra, e que tutoriais de TLS costumam omitir:

1. **Autenticação** (quem é você) é feita pelo TLS, com `CERT_REQUIRED`.
2. **Autorização** (o que você pode fazer) é feita pela aplicação, a partir do
   CN do certificado. TLS não faz autorização — quem acha que faz constrói um
   sistema em que qualquer cliente da CA pode tudo.
3. **Revogação** é verificada de verdade, com CRL (`VERIFY_CRL_CHECK_LEAF`).
4. **Configuração** vem do ambiente, com padrões seguros.
5. **Erros de TLS** são tratados e registrados sem derrubar o servidor.

Uso:
    python3 servidor.py                 # 127.0.0.1:8443
    COFRE_PORTA=9443 python3 servidor.py

Somente biblioteca padrão. Nenhuma dependência.
"""
from __future__ import annotations

import json
import logging
import os
import ssl
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ── Configuração ─────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent
PKI = BASE / "pki"

ENDERECO = os.environ.get("COFRE_ENDERECO", "127.0.0.1")
PORTA = int(os.environ.get("COFRE_PORTA", "8443"))
CERT_SERVIDOR = Path(os.environ.get("COFRE_CERT", PKI / "servidor.crt"))
CHAVE_SERVIDOR = Path(os.environ.get("COFRE_CHAVE", PKI / "servidor.key"))
# ca-com-crl.pem = certificado da CA + CRL no mesmo arquivo. O OpenSSL aceita
# os dois concatenados; é assim que se habilita a checagem de revogação.
CA_E_CRL = Path(os.environ.get("COFRE_CA", PKI / "ca-com-crl.pem"))
CHECAR_CRL = os.environ.get("COFRE_CHECAR_CRL", "1") == "1"

logging.basicConfig(
    level=os.environ.get("COFRE_LOG", "INFO"),
    format="%(asctime)s %(levelname)-7s %(message)s",
)
log = logging.getLogger("cofre")

# ── Autorização: CN do certificado → o que pode fazer ────────────────────────
# Deliberadamente explícito e sem curinga. Quem não está aqui não faz nada.
PERMISSOES: dict[str, set[str]] = {
    "admin": {"ler", "escrever", "apagar"},
    "escritor": {"ler", "escrever"},
    "leitor": {"ler"},
}

# ── Estado (em memória; um banco de verdade não muda nada do que é ensinado) ──
_trava = threading.Lock()
_notas: dict[int, dict] = {}
_proximo_id = 1


class Cofre(BaseHTTPRequestHandler):
    server_version = "cofre-tls/1.0"
    protocol_version = "HTTP/1.1"

    # ── utilitários ──────────────────────────────────────────────────────────
    def _identidade(self) -> str | None:
        """Extrai o CN do certificado que o cliente apresentou.

        `getpeercert()` só retorna algo porque o contexto foi criado com
        CERT_REQUIRED e a cadeia já foi validada pelo OpenSSL. Se a validação
        tivesse falhado, esta função nunca seria chamada: o handshake teria
        sido abortado antes de existir uma requisição HTTP.
        """
        cert = self.connection.getpeercert()
        if not cert:
            return None
        for campo in cert.get("subject", ()):
            for chave, valor in campo:
                if chave == "commonName":
                    return valor
        return None

    def _responder(self, codigo: int, corpo: dict) -> None:
        dados = json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        # HSTS não faz sentido aqui (API interna, sem navegador), mas estes fazem:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(dados)

    def _autorizar(self, acao: str) -> str | None:
        """Devolve o CN se ele puder executar `acao`; senão responde 401/403."""
        cn = self._identidade()
        if cn is None:                      # não deveria acontecer com mTLS
            self._responder(401, {"erro": "sem certificado de cliente"})
            return None
        if acao not in PERMISSOES.get(cn, set()):
            log.warning("negado: %s tentou %s", cn, acao)
            self._responder(403, {"erro": f"'{cn}' não pode '{acao}'"})
            return None
        return cn

    def _ler_json(self) -> dict | None:
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho <= 0 or tamanho > 64 * 1024:      # limite: corpo não é ilimitado
            self._responder(400, {"erro": "corpo ausente ou grande demais"})
            return None
        try:
            return json.loads(self.rfile.read(tamanho))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._responder(400, {"erro": "JSON inválido"})
            return None

    # ── rotas ────────────────────────────────────────────────────────────────
    def do_GET(self):
        if self.path == "/saude":
            # Mesmo a rota de saúde exige certificado: o mTLS acontece ANTES do
            # HTTP. Não existe "rota pública" num servidor com CERT_REQUIRED.
            return self._responder(200, {"estado": "ok", "voce": self._identidade()})

        if self.path == "/notas":
            cn = self._autorizar("ler")
            if cn is None:
                return
            with _trava:
                return self._responder(200, {"notas": list(_notas.values())})

        self._responder(404, {"erro": "rota inexistente"})

    def do_POST(self):
        global _proximo_id
        if self.path != "/notas":
            return self._responder(404, {"erro": "rota inexistente"})
        cn = self._autorizar("escrever")
        if cn is None:
            return
        corpo = self._ler_json()
        if corpo is None:
            return
        texto = corpo.get("texto")
        if not isinstance(texto, str) or not texto.strip():
            return self._responder(400, {"erro": "campo 'texto' obrigatório"})
        with _trava:
            nota = {"id": _proximo_id, "texto": texto.strip(), "autor": cn}
            _notas[_proximo_id] = nota
            _proximo_id += 1
        log.info("%s criou a nota %d", cn, nota["id"])
        self._responder(201, nota)

    def do_DELETE(self):
        if not self.path.startswith("/notas/"):
            return self._responder(404, {"erro": "rota inexistente"})
        cn = self._autorizar("apagar")
        if cn is None:
            return
        try:
            ident = int(self.path.rsplit("/", 1)[1])
        except ValueError:
            return self._responder(400, {"erro": "id inválido"})
        with _trava:
            if _notas.pop(ident, None) is None:
                return self._responder(404, {"erro": "nota inexistente"})
        log.info("%s apagou a nota %d", cn, ident)
        self._responder(204, {})

    def log_message(self, formato, *args):        # silencia o log padrão ruidoso
        log.debug("%s - %s", self.address_string(), formato % args)


def montar_contexto() -> ssl.SSLContext:
    """Constrói o contexto TLS do servidor.

    Cada linha aqui é uma decisão de segurança; nenhuma é padrão do Python.
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # 1. Piso de versão explícito. O padrão do Python é bom HOJE; fixar garante
    #    que uma atualização de runtime não afrouxe o que você prometeu.
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    # 2. Identidade do servidor.
    ctx.load_cert_chain(str(CERT_SERVIDOR), str(CHAVE_SERVIDOR))

    # 3. mTLS: o cliente É OBRIGADO a apresentar certificado.
    #    CERT_OPTIONAL seria um erro clássico: aceita quem não tem.
    ctx.verify_mode = ssl.CERT_REQUIRED

    # 4. Só ESTA CA vale. O repositório de raízes do sistema é irrelevante aqui —
    #    e é essa restrição que torna o mTLS interno seguro: nem a DigiCert
    #    consegue emitir um cliente válido para nós.
    ctx.load_verify_locations(str(CA_E_CRL))

    # 5. Revogação. Sem isto, um certificado revogado continua entrando.
    if CHECAR_CRL:
        ctx.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF

    # 6. Sem compressão (histórico: ataque CRIME) — já é o padrão, tornado explícito.
    ctx.options |= ssl.OP_NO_COMPRESSION

    return ctx


def main() -> int:
    for arquivo in (CERT_SERVIDOR, CHAVE_SERVIDOR, CA_E_CRL):
        if not arquivo.exists():
            print(f"faltando: {arquivo}\nRode ./criar-pki.sh primeiro.", file=sys.stderr)
            return 1

    servidor = ThreadingHTTPServer((ENDERECO, PORTA), Cofre)
    servidor.socket = montar_contexto().wrap_socket(servidor.socket, server_side=True)
    log.info("cofre-tls ouvindo em https://%s:%d/ (CRL: %s)",
             ENDERECO, PORTA, "sim" if CHECAR_CRL else "não")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        log.info("encerrando")
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
