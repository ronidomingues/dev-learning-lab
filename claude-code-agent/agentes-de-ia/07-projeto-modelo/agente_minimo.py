#!/usr/bin/env python3
"""
Um agente inteiro em ~120 linhas, com o laço agêntico escrito à mão.

Reaproveita EXATAMENTE as mesmas funções de domínio do `mcp_tarefas.py`.
Esse é o ponto do projeto: o domínio é um só; o que muda é o *arnês*
(harness) que embrulha o modelo:

    mcp_tarefas.py   → arnês = Claude Code (ou qualquer cliente MCP)
    agente_minimo.py → arnês = este arquivo, escrito por você

Por que escrever o laço na mão se o SDK tem `tool_runner`?
Porque o laço é o conceito central de todo o assunto, e vê-lo cru vale mais
que qualquer diagrama. Em produção, use o `tool_runner` — a última seção do
arquivo mostra a versão de três linhas.

Requisitos:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Uso:
    python3 agente_minimo.py "quais tarefas estão abertas?"
    python3 agente_minimo.py "anote com prioridade alta: revisar o contrato"

ATENÇÃO: este arquivo consome créditos da API e NÃO foi executado durante a
escrita deste material (ver `README.md` → "O que foi e o que não foi
executado"). O `mcp_tarefas.py` e o `teste_mcp.py`, sim.
"""

from __future__ import annotations

import json
import sys

import anthropic

# Reuso do domínio. Nada aqui reimplementa regra de negócio.
from mcp_tarefas import FERRAMENTAS, POR_NOME

MODELO = "claude-opus-5"

SISTEMA = """Você é um assistente de tarefas.

Responda sempre a partir das ferramentas, nunca de memória: o banco pode ter
mudado desde a última mensagem. Se precisar do id de uma tarefa e não o tiver,
liste antes.

Ao terminar, responda em uma ou duas frases, em português do Brasil. Não
narre o que você fez com as ferramentas — diga o resultado."""


def esquema_para_api() -> list[dict]:
    """Converte o catálogo MCP para o formato de `tools` da Claude API.

    A tradução é quase 1:1 — `inputSchema` (MCP, camelCase) vira
    `input_schema` (API, snake_case). Não é coincidência: o MCP foi desenhado
    para carregar exatamente a mesma informação que a API já pedia.
    """
    return [
        {
            "name": f["name"],
            "description": f["description"],
            "input_schema": f["inputSchema"],
        }
        for f in FERRAMENTAS
    ]


def executar(nome: str, argumentos: dict) -> tuple[str, bool]:
    """Executa uma ferramenta. Devolve (texto, houve_erro).

    Regra de ouro: erro de ferramenta NUNCA derruba o laço. Ele volta como
    conteúdo, com `is_error=True`, para o modelo ler e se corrigir. Um agente
    que estoura exceção na primeira ferramenta que falha não é um agente — é
    um script com uma chamada de LLM no meio.
    """
    try:
        return POR_NOME[nome]["_fn"](**argumentos), False
    except Exception as e:
        return f"Erro: {e}", True


def rodar(pergunta: str, max_voltas: int = 10) -> str:
    cliente = anthropic.Anthropic()
    ferramentas = esquema_para_api()
    mensagens: list[dict] = [{"role": "user", "content": pergunta}]

    for volta in range(1, max_voltas + 1):
        # ---- 1. REUNIR CONTEXTO: manda o histórico inteiro. A API não tem
        #         memória; o estado da conversa vive aqui, no seu processo.
        resposta = cliente.messages.create(
            model=MODELO,
            max_tokens=16000,
            system=SISTEMA,
            thinking={"type": "adaptive"},
            tools=ferramentas,
            messages=mensagens,
        )

        # ---- 2. O modelo parou. Por quê?
        if resposta.stop_reason == "refusal":
            return "O pedido foi recusado pelos filtros de segurança."

        if resposta.stop_reason != "tool_use":
            # Sem pedido de ferramenta = fim de turno. Esta é a única
            # condição de parada normal do laço.
            return "".join(b.text for b in resposta.content if b.type == "text")

        # ---- 3. AGIR: o modelo pediu uma ou mais ferramentas.
        # Preserve `resposta.content` inteiro no histórico — inclui os blocos
        # de thinking e de tool_use. Guardar só o texto quebra o próximo turno.
        mensagens.append({"role": "assistant", "content": resposta.content})

        resultados = []
        for bloco in resposta.content:
            if bloco.type != "tool_use":
                continue
            print(f"  [volta {volta}] {bloco.name}({json.dumps(bloco.input, ensure_ascii=False)})",
                  file=sys.stderr)
            texto, houve_erro = executar(bloco.name, bloco.input)
            resultados.append(
                {
                    "type": "tool_result",
                    "tool_use_id": bloco.id,  # tem de casar com o id do pedido
                    "content": texto,
                    "is_error": houve_erro,
                }
            )

        # ---- 4. VERIFICAR: todos os resultados voltam em UMA única mensagem
        # de usuário. Dividi-los em várias ensina o modelo a parar de pedir
        # ferramentas em paralelo.
        mensagens.append({"role": "user", "content": resultados})

    return f"Parei após {max_voltas} voltas sem concluir. Reformule o pedido."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    print(rodar(" ".join(sys.argv[1:])))


# --------------------------------------------------------------------------
# A MESMA COISA COM O `tool_runner` DO SDK (use isto em produção)
#
# O SDK executa o laço acima para você. Você entrega funções decoradas; ele
# cuida de chamar a API, despachar as ferramentas, devolver os resultados e
# parar quando o modelo parar de pedir.
#
#     from anthropic import beta_tool
#
#     @beta_tool
#     def criar_tarefa(titulo: str, prioridade: str = "media") -> str:
#         """Cria uma nova tarefa.
#
#         Args:
#             titulo: descrição curta da tarefa.
#             prioridade: baixa, media ou alta.
#         """
#         return mcp_tarefas.criar_tarefa(titulo, prioridade)
#
#     runner = cliente.beta.messages.tool_runner(
#         model=MODELO, max_tokens=16000, system=SISTEMA,
#         tools=[criar_tarefa, ...],
#         messages=[{"role": "user", "content": pergunta}],
#     )
#     for mensagem in runner:
#         ...  # cada iteração é uma volta do laço; você pode intervir aqui
#
# O esquema JSON é gerado a partir da assinatura e do docstring. É por isso
# que o docstring de uma ferramenta é código de produção, não comentário.
# --------------------------------------------------------------------------
