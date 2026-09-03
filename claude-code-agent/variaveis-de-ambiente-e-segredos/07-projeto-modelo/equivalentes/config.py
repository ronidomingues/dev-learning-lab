"""
config.py — o MESMO contrato do src/config.mjs, em Python, só com a biblioteca padrão.

Existe aqui para provar o ponto central do curso: o mecanismo é do sistema
operacional, não da linguagem. O `.env` some em produção nas três linguagens,
e as três leem exatamente o mesmo ambiente.

Rode:
    python3 equivalentes/config.py
    DATABASE_URL=memory://x SESSION_SECRET=$(head -c 40 /dev/urandom | base64) \
      API_KEY=sk_test_abc123 python3 equivalentes/config.py
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

SEGREDO_DE_EXEMPLO = "desenvolvimento-apenas-troque-isto-em-producao"
CHAVES_SECRETAS = ("session_secret", "api_key", "database_url")


# ── validadores ────────────────────────────────────────────────────────────
def url(*esquemas):
    def _v(valor: str):
        p = urlparse(valor)
        if not p.scheme or not p.netloc:
            return "não é uma URL válida"
        if esquemas and p.scheme not in esquemas:
            return f'esquema deve ser um de {", ".join(esquemas)} (veio "{p.scheme}")'
        return None
    return _v


def inteiro(minimo: int, maximo: int):
    def _v(valor: str):
        ok = valor.isdigit() and minimo <= int(valor) <= maximo
        return None if ok else f"esperado inteiro entre {minimo} e {maximo}"
    return _v


def um_de(*opcoes: str):
    return lambda v: None if v in opcoes else f'esperado um de {", ".join(opcoes)}'


def minimo(n: int):
    return lambda v: None if len(v) >= n else f"precisa ter ao menos {n} caracteres (tem {len(v)})"


def booleano(v: str):
    return None if v in ("true", "false") else 'esperado "true" ou "false"'


@dataclass(frozen=True)
class Config:
    ambiente: str
    porta: int
    log_level: str
    database_url: str
    session_secret: str
    api_key: str
    max_recados: int
    expor_metricas: bool


def mascarar(valor: str) -> str:
    if not isinstance(valor, str) or not valor:
        return valor
    if len(valor) <= 8:
        return "********"
    return f"{valor[:3]}…{valor[-2:]} ({len(valor)} chars)"


def config_para_log(config: Config) -> dict:
    return {
        k: (mascarar(v) if k in CHAVES_SECRETAS else v)
        for k, v in asdict(config).items()
    }


def redigir_url(texto: str) -> str:
    """postgres://app:senha@host/db → postgres://app:***@host/db"""
    p = urlparse(texto)
    if p.password:
        return texto.replace(f":{p.password}@", ":***@")
    return texto


def criar_config(env: dict | None = None) -> tuple[Config, list[str]]:
    """Função pura: recebe o ambiente, devolve (config, problemas)."""
    env = os.environ if env is None else env
    problemas: list[str] = []

    def ler(nome: str) -> str | None:
        caminho = env.get(f"{nome}_FILE")
        if caminho:
            try:
                return open(caminho, encoding="utf-8").read().strip()
            except OSError as e:
                problemas.append(f'{nome}_FILE aponta para "{caminho}", ilegível ({e.strerror})')
                return None
        valor = env.get(nome)
        return valor if valor else None   # "" conta como ausente

    def exigido(nome, validar=None):
        v = ler(nome)
        if v is None:
            problemas.append(f"falta {nome}")
            return None
        if validar and (msg := validar(v)):
            problemas.append(f"{nome}: {msg}")
            return None
        return v

    def opcional(nome, padrao, validar=None):
        v = ler(nome)
        if v is None:
            return padrao
        if validar and (msg := validar(v)):
            problemas.append(f"{nome}: {msg}")
            return padrao
        return v

    ambiente = opcional("NODE_ENV", "development", um_de("development", "test", "production"))
    bruta = dict(
        ambiente=ambiente,
        porta=opcional("PORT", "3000", inteiro(1, 65535)),
        log_level=opcional("LOG_LEVEL", "info", um_de("debug", "info", "warn", "error")),
        database_url=exigido("DATABASE_URL", url("postgres", "postgresql", "memory")),
        session_secret=exigido("SESSION_SECRET", minimo(32)),
        api_key=exigido("API_KEY", minimo(8)),
        max_recados=opcional("MAX_RECADOS", "100", inteiro(1, 100000)),
        expor_metricas=opcional("EXPOR_METRICAS", "false", booleano),
    )

    if ambiente == "production":
        if bruta["session_secret"] == SEGREDO_DE_EXEMPLO:
            problemas.append("SESSION_SECRET: o valor de exemplo não pode ser usado com NODE_ENV=production")
        if (bruta["api_key"] or "").startswith("sk_test_"):
            problemas.append("API_KEY: chave de teste (sk_test_…) com NODE_ENV=production")
        if (bruta["database_url"] or "").startswith("memory:"):
            problemas.append("DATABASE_URL: banco em memória com NODE_ENV=production perde tudo a cada reinício")

    config = Config(
        ambiente=bruta["ambiente"],
        porta=int(bruta["porta"]),
        log_level=bruta["log_level"],
        database_url=bruta["database_url"],
        session_secret=bruta["session_secret"],
        api_key=bruta["api_key"],
        max_recados=int(bruta["max_recados"]),
        expor_metricas=bruta["expor_metricas"] == "true",
    )
    return config, problemas


def main() -> int:
    config, problemas = criar_config()
    if problemas:
        print("\n❌ Configuração inválida:", file=sys.stderr)
        for p in problemas:
            print(f"   • {p}", file=sys.stderr)
        print("\nConsulte .env.example para a lista completa de variáveis.\n", file=sys.stderr)
        return 78  # EX_CONFIG
    print("✅ Configuração válida.\n")
    visao = config_para_log(config) | {"database_url": redigir_url(config.database_url)}
    for chave, valor in visao.items():
        print(f"   {chave:<16} {valor}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
