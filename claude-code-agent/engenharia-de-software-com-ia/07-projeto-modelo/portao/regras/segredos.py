"""Regra: nenhuma credencial entra no repositório.

Duas estratégias combinadas, porque nenhuma sozinha basta:

1. **Padrões conhecidos** — pegam credenciais com formato reconhecível.
   Baixo falso positivo, cobertura limitada ao que já se conhece.
2. **Entropia de Shannon** — pega segredo genérico, sem formato.
   Cobertura ampla, falso positivo maior — por isso só dispara em linha
   que *parece* atribuição de credencial.

O escape `portao: ignora-segredo` existe porque toda regra sem escape acaba
desligada inteira. Melhor uma exceção anotada e visível no diff do que a
regra removida.
"""

from __future__ import annotations

import math
import re
from fnmatch import fnmatch

from ..config import Config
from ..diff import Diff
from ..modelo import Achado, Resultado, Severidade

NOME = "segredos"

ESCAPE = "portao: ignora-segredo"

PADROES: list[tuple[str, re.Pattern]] = [
    ("chave privada", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("chave de acesso AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("token do GitHub", re.compile(r"\b gh[pousr]_[A-Za-z0-9]{36,} \b".replace(" ", ""))),
    ("chave da Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("chave da OpenAI", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("token do Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("URL com senha", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:[^\s:/@]+@")),
    ("JSON Web Token", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
]

ATRIBUICAO = re.compile(
    r"(?i)\b(senha|password|passwd|secret|segredo|token|api[_\-]?key|apikey|"
    r"access[_\-]?key|private[_\-]?key|credential)\b\s*[:=]\s*"
    r"[\"']?(?P<valor>[^\s\"',;]{8,})[\"']?"
)

PLACEHOLDERS = re.compile(
    r"(?i)^(x{3,}|\.{3,}|<[^>]+>|\$\{[^}]+\}|\{\{[^}]+\}\}|change[_\-]?me|"
    r"seu[_\-]?token|your[_\-]?\w+|todo|fixme|example|exemplo|dummy|fake|"
    r"placeholder|redacted|null|none|undefined|test|teste)$"
)


def entropia(s: str) -> float:
    """Entropia de Shannon em bits por caractere."""
    if not s:
        return 0.0
    total = len(s)
    return -sum(
        (n / total) * math.log2(n / total)
        for n in (s.count(c) for c in set(s))
    )


def _ignorado(caminho: str, cfg: Config) -> bool:
    return any(fnmatch(caminho, p) for p in cfg.segredos_ignorar_caminhos)


def verificar(diff: Diff, cfg: Config) -> Resultado:
    r = Resultado(regra=NOME)
    for arq in diff.arquivos:
        if _ignorado(arq.caminho, cfg):
            continue
        for linha in arq.adicionadas:
            texto = linha.texto
            if ESCAPE in texto:
                continue

            achou_padrao = False
            for rotulo, padrao in PADROES:
                if padrao.search(texto):
                    r.achados.append(
                        Achado(
                            arquivo=arq.caminho,
                            linha=linha.numero,
                            mensagem=f"possível {rotulo} em linha adicionada",
                            detalhe="rotacione a credencial ANTES de remover do diff",
                        )
                    )
                    achou_padrao = True
                    break
            if achou_padrao:
                continue

            m = ATRIBUICAO.search(texto)
            if not m:
                continue
            valor = m.group("valor")
            if PLACEHOLDERS.match(valor):
                continue
            if len(valor) < cfg.tamanho_minimo_entropia:
                continue
            e = entropia(valor)
            if e >= cfg.entropia_minima:
                r.achados.append(
                    Achado(
                        arquivo=arq.caminho,
                        linha=linha.numero,
                        mensagem="valor de alta entropia atribuído a nome de credencial",
                        severidade=Severidade.AVISA,
                        detalhe=f"entropia {e:.2f} bits/char, {len(valor)} chars",
                    )
                )
    return r
