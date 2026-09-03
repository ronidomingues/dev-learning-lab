"""Usa o modelo treinado para classificar chamados novos.

Uso:
    python prever.py "não consigo emitir nota fiscal"
    python prever.py                       # roda uma bateria de exemplos de demonstração

Também é o módulo importado pela API (`api.py`) e pelos testes.
"""

from __future__ import annotations

import functools
import sys
from dataclasses import dataclass

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from config import config


@dataclass
class Predicao:
    categoria: str
    confianca: float
    probabilidades: dict[str, float]
    encaminhar_para_humano: bool


@functools.lru_cache(maxsize=1)
def carregar():
    """Carrega modelo e tokenizador UMA vez por processo.

    Sem o cache, uma API recarregaria ~440 MB do disco a cada requisição e a
    latência sairia de ~15 ms para vários segundos. É o erro de produção nº 1
    com modelos da família BERT.
    """
    if not config.dir_saida.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em {config.dir_saida}. Treine primeiro:  python treinar.py"
        )
    tokenizador = AutoTokenizer.from_pretrained(str(config.dir_saida))
    modelo = AutoModelForSequenceClassification.from_pretrained(str(config.dir_saida))
    modelo.eval()  # desliga dropout — sem isso a mesma frase dá respostas diferentes
    return tokenizador, modelo


def prever(texto: str) -> Predicao:
    texto = (texto or "").strip()
    if not texto:
        raise ValueError("texto vazio")

    tokenizador, modelo = carregar()
    entradas = tokenizador(
        texto, truncation=True, max_length=config.max_tokens, return_tensors="pt"
    )

    with torch.no_grad():  # sem gradiente: metade da memória, mais rápido
        logits = modelo(**entradas).logits

    probs = torch.softmax(logits, dim=-1)[0]
    idx = int(probs.argmax())
    confianca = float(probs[idx])
    categoria = modelo.config.id2label[idx]

    return Predicao(
        categoria=categoria,
        confianca=confianca,
        probabilidades={
            modelo.config.id2label[i]: round(float(p), 4) for i, p in enumerate(probs)
        },
        encaminhar_para_humano=confianca < config.limiar_confianca,
    )


EXEMPLOS_DEMO = [
    "minha fatura veio com valor errado",
    "o sistema está fora do ar desde ontem",
    "quero contratar mais dez licenças",
    "solicito o cancelamento do contrato",
    "qual a receita de bolo de cenoura",  # fora do domínio: deve cair no limiar
]


def main() -> None:
    textos = sys.argv[1:] or EXEMPLOS_DEMO
    try:
        for texto in textos:
            p = prever(texto)
            marca = "  <- baixa confiança, triagem humana" if p.encaminhar_para_humano else ""
            print(f"{p.categoria:14s} {p.confianca:6.1%}  {texto!r}{marca}")
    except FileNotFoundError as erro:
        sys.exit(f"ERRO: {erro}")


if __name__ == "__main__":
    main()
