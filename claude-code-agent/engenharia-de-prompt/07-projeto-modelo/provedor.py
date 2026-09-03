"""Provedores de modelo.

Duas implementações com a MESMA interface:

  - SimulatedProvider : roda offline, sem chave de API, sem dependência externa.
  - AnthropicProvider : chama a API real da Anthropic (precisa do pacote `anthropic`).

AVISO IMPORTANTE (leia antes de tirar conclusões):
O provedor simulado NÃO é um modelo de linguagem. É uma caricatura determinística,
escrita à mão, que reage a *características* do prompt (pediu JSON puro? deu exemplos?
listou as categorias?) da mesma forma que um modelo pequeno tende a reagir.
Ele existe para você exercitar o arnês de avaliação sem gastar um centavo.
Os números que ele produz medem o arnês, não a qualidade do prompt.
Para medir prompt de verdade, use `--provedor anthropic`.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata


class ProviderError(RuntimeError):
    """Falha ao obter resposta do modelo."""


# --------------------------------------------------------------------------
# Provedor simulado
# --------------------------------------------------------------------------

_REGRAS = [
    # (categoria, termos que a disparam)
    ("cobranca", ["cobran", "fatura", "boleto", "estorno", "cartao", "cobrado", "reembolso", "pagamento"]),
    ("bug", ["erro", "quebrou", "trava", "500", "nao carrega", "bug", "exception", "falha ao"]),
    ("acesso", ["senha", "login", "entrar", "acesso", "bloqueada", "2fa", "autentic"]),
    ("duvida", ["como faco", "como fazer", "duvida", "possivel", "consigo", "onde fica", "existe"]),
]

_URGENTES = ["producao", "todos os usuarios", "urgente", "parado", "prejuizo", "vazou", "fora do ar"]


def _normalizar(texto: str) -> str:
    """Minúsculas, sem acento — para casar termos sem depender de acentuação."""
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))


class SimulatedProvider:
    """Caricatura determinística de um modelo pequeno.

    Comportamentos que ele imita, todos observados em modelos reais:

    1. Se o prompt não proíbe explicitamente texto ao redor, ele embrulha o JSON
       em cerca de markdown e escreve uma frase de cortesia antes.
    2. Se o prompt não enumera as categorias válidas, ele inventa uma categoria
       plausível fora do conjunto ("financeiro" em vez de "cobranca").
    3. Se o prompt não traz exemplos, ele erra os casos de fronteira — em
       particular, chama de "bug" qualquer chamado que contenha a palavra "erro",
       mesmo quando o assunto é cobrança.
    """

    nome = "simulado"

    def __init__(self, latencia_falsa: float = 0.0) -> None:
        self.latencia_falsa = latencia_falsa
        self.chamadas = 0

    def completar(self, sistema: str, usuario: str) -> str:
        self.chamadas += 1
        prompt = _normalizar(sistema + "\n" + usuario)

        pede_json_puro = "apenas o json" in prompt or "somente o json" in prompt or "sem texto" in prompt
        enumera_categorias = "cobranca" in prompt and "acesso" in prompt and "bug" in prompt
        tem_exemplos = "<exemplo" in prompt or "exemplo 1" in prompt

        chamado = _normalizar(usuario)

        categoria = self._classificar(chamado, tem_exemplos)
        if not enumera_categorias:
            # Sem a lista fechada, o modelo usa o rótulo que ele acha bonito.
            categoria = {"cobranca": "financeiro", "bug": "tecnico",
                         "acesso": "conta", "duvida": "informacao"}.get(categoria, categoria)

        urgencia = "alta" if any(t in chamado for t in _URGENTES) else "normal"

        corpo = json.dumps(
            {"categoria": categoria, "urgencia": urgencia,
             "resumo": self._resumir(usuario)},
            ensure_ascii=False,
        )

        if pede_json_puro:
            return corpo
        return f"Claro! Aqui está a classificação do chamado:\n\n```json\n{corpo}\n```\n\nPosso ajudar em algo mais?"

    @staticmethod
    def _classificar(chamado: str, tem_exemplos: bool) -> str:
        if not tem_exemplos and "erro" in chamado:
            # Falha clássica de zero-shot: a palavra-gatilho domina o sentido.
            return "bug"
        for categoria, termos in _REGRAS:
            if any(t in chamado for t in termos):
                return categoria
        return "duvida"

    @staticmethod
    def _resumir(texto: str) -> str:
        primeira = re.split(r"[.!?\n]", texto.strip())[0]
        return primeira[:80].strip()


# --------------------------------------------------------------------------
# Provedor real
# --------------------------------------------------------------------------


class AnthropicProvider:
    """Chama a API da Anthropic de verdade.

    Requer: pip install anthropic  e  ANTHROPIC_API_KEY no ambiente
    (ou um perfil ativo criado por `ant auth login`).
    """

    nome = "anthropic"

    def __init__(self, modelo: str = "claude-opus-5", max_tokens: int = 1024) -> None:
        try:
            import anthropic  # import tardio: o projeto roda sem o pacote
        except ImportError as exc:  # pragma: no cover - depende do ambiente
            raise ProviderError(
                "pacote 'anthropic' não instalado. Rode: pip install anthropic\n"
                "Ou use --provedor simulado para rodar offline."
            ) from exc

        self._cliente = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY ou o perfil do `ant`
        self.modelo = modelo
        self.max_tokens = max_tokens

    def completar(self, sistema: str, usuario: str) -> str:  # pragma: no cover - precisa de rede
        import anthropic

        try:
            resposta = self._cliente.messages.create(
                model=self.modelo,
                max_tokens=self.max_tokens,
                system=[{"type": "text", "text": sistema,
                         "cache_control": {"type": "ephemeral"}}],  # cache do prefixo estável
                messages=[{"role": "user", "content": usuario}],
            )
        except anthropic.RateLimitError as exc:
            raise ProviderError(f"limite de taxa atingido: {exc}") from exc
        except anthropic.APIStatusError as exc:
            raise ProviderError(f"erro HTTP {exc.status_code}: {exc}") from exc
        except anthropic.APIConnectionError as exc:
            raise ProviderError(f"falha de conexão: {exc}") from exc

        if resposta.stop_reason == "refusal":
            raise ProviderError("o modelo recusou a requisição (stop_reason=refusal)")

        partes = [bloco.text for bloco in resposta.content if bloco.type == "text"]
        return "\n".join(partes)


def obter_provedor(nome: str):
    """Fábrica: nome -> instância."""
    if nome == "simulado":
        return SimulatedProvider()
    if nome == "anthropic":
        return AnthropicProvider(modelo=os.environ.get("MODELO", "claude-opus-5"))
    raise ValueError(f"provedor desconhecido: {nome!r} (use 'simulado' ou 'anthropic')")
