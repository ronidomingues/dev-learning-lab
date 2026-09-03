"""Autenticação local: hash de senha, verificação, papéis.

AVISO HONESTO, LEIA ANTES DE COPIAR PARA PRODUÇÃO
-------------------------------------------------
Este módulo existe para o projeto rodar offline, sem depender de um provedor
externo, e para ensinar como a coisa funciona por dentro. Em produção de
verdade, prefira, nesta ordem:

1. `st.login()` do próprio Streamlit (OIDC: Google, Microsoft Entra, Okta,
   Auth0, Keycloak). Você não guarda senha nenhuma. Ver 22-autenticacao.
2. Um proxy de autenticação na frente da app (oauth2-proxy, Cloudflare Access,
   Authelia). A app nem vê o login.
3. Só então algo caseiro como isto — e aí com bloqueio por tentativa,
   redefinição de senha, 2FA e registro de auditoria.

O que este arquivo faz certo e você deve copiar de qualquer jeito:
- PBKDF2-HMAC-SHA256 com salt por usuário e custo alto (não SHA256 puro, nunca MD5);
- comparação em tempo constante (`compare_digest`), para não vazar por temporização;
- mesma mensagem de erro para "usuário não existe" e "senha errada" (não conte
  ao atacante quais e-mails estão cadastrados).
"""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from nucleo.modelos import Usuario

ALGORITMO = "sha256"


class ErroDeLogin(Exception):
    """Credencial inválida ou conta desativada."""


def gerar_hash(senha: str, iteracoes: int, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """Devolve (hash, salt). Salt novo e aleatório se não vier um."""
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac(ALGORITMO, senha.encode("utf-8"), salt, iteracoes)
    return digest, salt


def senha_confere(senha: str, digest: bytes, salt: bytes, iteracoes: int) -> bool:
    calculado, _ = gerar_hash(senha, iteracoes, salt)
    # compare_digest: tempo constante. `==` em bytes vaza o tamanho do prefixo igual.
    return hmac.compare_digest(calculado, digest)


def criar_usuario(
    caminho: Path, *, email: str, nome: str, senha: str, papel: str, iteracoes: int
) -> int:
    from nucleo.db import transacao

    digest, salt = gerar_hash(senha, iteracoes)
    with transacao(caminho) as con:
        cur = con.execute(
            """INSERT INTO usuarios (email, nome, papel, senha_hash, salt, iteracoes, ativo, criado_em)
               VALUES (?, ?, ?, ?, ?, ?, 1, ?)""",
            (email.strip().lower(), nome, papel, digest, salt, iteracoes,
             datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
        return int(cur.lastrowid)


def autenticar(caminho: Path, email: str, senha: str) -> Usuario:
    """Devolve o Usuario ou levanta ErroDeLogin. Mensagem única de propósito."""
    from nucleo.db import conexao

    con: sqlite3.Connection = conexao(caminho)
    linha = con.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email.strip().lower(),)
    ).fetchone()

    if linha is None:
        # Gasta o mesmo tempo do caminho feliz para não revelar, pelo relógio,
        # que o e-mail não existe.
        gerar_hash(senha, 240_000)
        raise ErroDeLogin("E-mail ou senha incorretos.")

    if not senha_confere(senha, linha["senha_hash"], linha["salt"], linha["iteracoes"]):
        raise ErroDeLogin("E-mail ou senha incorretos.")

    if not linha["ativo"]:
        raise ErroDeLogin("Conta desativada. Fale com o administrador.")

    return Usuario(id=linha["id"], email=linha["email"], nome=linha["nome"], papel=linha["papel"])
