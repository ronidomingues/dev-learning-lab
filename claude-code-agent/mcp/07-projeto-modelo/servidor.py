"""Servidor MCP da biblioteca.

Camada fina: valida entrada, chama o domínio, formata a saída para o modelo.
Nenhuma regra de negócio mora aqui — isso é o que torna o domínio testável sem MCP.

Rodar:
    uv run python servidor.py                 # stdio (para um host)
    uv run python servidor.py --http          # Streamable HTTP em 127.0.0.1:8931
"""
from __future__ import annotations

import logging
import sys
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from biblioteca import dados
from biblioteca.config import Config
from mcp.server.mcpserver import (
    AcceptedElicitation,
    Elicit,
    ElicitationResult,
    MCPServer,
    Resolve,
)
from mcp.server.mcpserver.exceptions import ToolError

CFG = Config.do_ambiente()

# stderr, NUNCA stdout: stdout é a fita do protocolo JSON-RPC.
logging.basicConfig(
    stream=sys.stderr,
    level=getattr(logging, CFG.nivel_log, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("biblioteca")

server = MCPServer(
    "biblioteca",
    version="1.0.0",
    title="Biblioteca",
    description="Consulta de acervo e controle de empréstimos de uma biblioteca.",
    instructions=(
        "Use `buscar_livros` para encontrar um livro pelo título ou autor e obter o ISBN. "
        "Só então use `emprestar_livro` ou `devolver_livro`, que exigem o ISBN exato. "
        "Empréstimos duram 14 dias. Sempre confirme com o usuário antes de emprestar."
    ),
)


# --------------------------------------------------------------------------- #
# Modelos de saída — geram `outputSchema` e `structuredContent`.
# Retornar `dict` cru NÃO gera outputSchema; por isso declaramos tudo.
# --------------------------------------------------------------------------- #
class Livro(BaseModel):
    isbn: str
    titulo: str
    autor: str
    ano: int
    exemplares: int
    disponiveis: int


class ResultadoBusca(BaseModel):
    encontrados: int = Field(description="Quantos livros vieram nesta resposta")
    truncado: bool = Field(description="True se havia mais resultados do que o limite")
    livros: list[Livro]


class Emprestimo(BaseModel):
    isbn: str
    titulo: str
    leitor: str
    devolver_ate: str = Field(description="Data limite de devolução, AAAA-MM-DD")


class Devolucao(BaseModel):
    isbn: str
    leitor: str
    mensagem: str


class EmprestimoAberto(BaseModel):
    isbn: str
    titulo: str
    emprestado: str
    devolver_ate: str


class Estatisticas(BaseModel):
    titulos: int
    exemplares: int
    emprestimos_abertos: int
    atrasados: int


# --------------------------------------------------------------------------- #
# Ferramentas
# --------------------------------------------------------------------------- #
@server.tool()
def buscar_livros(
    termo: Annotated[
        str,
        Field(description="Trecho do título ou do nome do autor. Mínimo 2 caracteres.",
              min_length=2, max_length=80),
    ],
    limite: Annotated[
        int, Field(description="Máximo de livros a devolver (1 a 25).", ge=1, le=25)
    ] = 10,
) -> ResultadoBusca:
    """Busca livros no acervo por título ou autor e devolve o ISBN de cada um.

    Use esta ferramenta primeiro: `emprestar_livro` e `devolver_livro` exigem o ISBN
    exato, que só se obtém aqui. Não empresta nada — é apenas consulta.
    """
    limite = min(limite, CFG.max_linhas)
    linhas = dados.buscar(CFG.caminho_db, termo, limite)
    truncado = len(linhas) > limite
    log.info("buscar_livros termo=%r limite=%s -> %s", termo, limite, len(linhas[:limite]))
    return ResultadoBusca(
        encontrados=len(linhas[:limite]),
        truncado=truncado,
        livros=[Livro(**l) for l in linhas[:limite]],
    )


@server.tool()
def detalhar_livro(isbn: Annotated[str, Field(description="ISBN exato, 13 dígitos")]) -> Livro:
    """Devolve os dados de um livro pelo ISBN exato.

    Se você não tem o ISBN, use `buscar_livros` antes.
    """
    livro = dados.obter(CFG.caminho_db, isbn.strip())
    if livro is None:
        raise ToolError(
            f"Não existe livro com ISBN {isbn!r}. "
            f"Use `buscar_livros` para achar o ISBN correto pelo título ou autor."
        )
    return Livro(**livro)


def _confirmar_emprestimo(isbn: str, leitor: str):
    """Resolver do MRTR: pergunta ao usuário antes de alterar o acervo.

    Roda ANTES do corpo da ferramenta. O parâmetro que ele preenche não aparece
    no `inputSchema`, então o modelo não sabe que existe e não pode forjá-lo.
    """
    return Elicit(
        f"Confirmar empréstimo do livro {isbn} para {leitor}? "
        f"O prazo de devolução é de {dados.DIAS_DE_EMPRESTIMO} dias.",
        Confirmacao,
    )


class Confirmacao(BaseModel):
    confirmar: bool = Field(description="Confirma o empréstimo?")


@server.tool()
def emprestar_livro(
    isbn: Annotated[str, Field(description="ISBN exato do livro, obtido em `buscar_livros`")],
    leitor: Annotated[
        str, Field(description="Nome do leitor", min_length=2, max_length=80)
    ],
    confirmacao: Annotated[
        ElicitationResult[Confirmacao], Resolve(_confirmar_emprestimo)
    ],
) -> Emprestimo:
    """Empresta um exemplar do livro para um leitor, por 14 dias.

    ALTERA o acervo. O usuário é consultado para confirmar antes da alteração.
    Falha se o livro não existir, se não houver exemplar disponível, ou se este
    leitor já estiver com um exemplar deste mesmo livro.
    """
    if not (isinstance(confirmacao, AcceptedElicitation) and confirmacao.data.confirmar):
        raise ToolError("O usuário não confirmou o empréstimo. Nada foi alterado.")

    r = dados.emprestar(CFG.caminho_db, isbn.strip(), leitor.strip())
    if not r["ok"]:
        motivos = {
            "inexistente": (
                f"Não existe livro com ISBN {isbn!r}. Use `buscar_livros` para achar o correto."
            ),
            "sem_exemplar": (
                f"Não há exemplar disponível do ISBN {isbn!r} no momento. "
                f"Consulte `detalhar_livro` para ver quantos existem."
            ),
            "ja_emprestado_para_este_leitor": (
                f"{leitor} já está com um exemplar do ISBN {isbn!r}. "
                f"Devolva antes de emprestar de novo."
            ),
        }
        raise ToolError(motivos[r["motivo"]])

    log.info("emprestar_livro isbn=%s leitor=%r ok", isbn, leitor)
    return Emprestimo(**{k: r[k] for k in ("isbn", "titulo", "leitor", "devolver_ate")})


@server.tool()
def devolver_livro(
    isbn: Annotated[str, Field(description="ISBN exato do livro")],
    leitor: Annotated[str, Field(description="Nome do leitor", min_length=2, max_length=80)],
) -> Devolucao:
    """Registra a devolução de um exemplar emprestado a um leitor.

    ALTERA o acervo. Falha se não houver empréstimo aberto desse livro para esse leitor.
    """
    r = dados.devolver(CFG.caminho_db, isbn.strip(), leitor.strip())
    if not r["ok"]:
        raise ToolError(
            f"Não há empréstimo aberto do ISBN {isbn!r} para {leitor!r}. "
            f"Use `emprestimos_do_leitor` para ver o que está emprestado."
        )
    log.info("devolver_livro isbn=%s leitor=%r ok", isbn, leitor)
    return Devolucao(isbn=r["isbn"], leitor=r["leitor"], mensagem="Devolução registrada.")


@server.tool()
def emprestimos_do_leitor(
    leitor: Annotated[str, Field(description="Nome do leitor", min_length=2, max_length=80)],
) -> list[EmprestimoAberto]:
    """Lista os empréstimos ainda em aberto de um leitor, do mais urgente ao menos."""
    linhas = dados.emprestimos_do_leitor(CFG.caminho_db, leitor.strip(), CFG.max_linhas)
    return [EmprestimoAberto(**l) for l in linhas]


@server.tool()
def estatisticas_do_acervo() -> Estatisticas:
    """Números gerais do acervo: títulos, exemplares, empréstimos abertos e atrasados."""
    return Estatisticas(**dados.estatisticas(CFG.caminho_db))


# --------------------------------------------------------------------------- #
# Recurso — substantivo, escolhido pela aplicação, não pelo modelo.
# --------------------------------------------------------------------------- #
@server.resource("biblioteca://politica")
def politica() -> str:
    """Regulamento de empréstimo da biblioteca."""
    return (
        "REGULAMENTO\n"
        f"1. O prazo de empréstimo é de {dados.DIAS_DE_EMPRESTIMO} dias corridos.\n"
        "2. Um leitor não pode ter dois exemplares do mesmo título ao mesmo tempo.\n"
        "3. Não há renovação automática: devolva e empreste de novo.\n"
        "4. Atraso suspende novos empréstimos até a regularização.\n"
    )


# --------------------------------------------------------------------------- #
# Prompt — verbo escolhido pelo USUÁRIO (vira comando de barra no host).
# --------------------------------------------------------------------------- #
@server.prompt()
def relatorio_de_atrasos(tom: Literal["formal", "cordial"] = "cordial") -> str:
    """Roteiro para gerar o relatório de empréstimos atrasados."""
    return (
        f"Use `estatisticas_do_acervo` para obter os números gerais. "
        f"Depois escreva um relatório em tom {tom}, em português do Brasil, com:\n"
        f"1. Um parágrafo de resumo com os números.\n"
        f"2. Uma avaliação de gravidade (proporção de atrasados sobre abertos).\n"
        f"3. Uma recomendação de ação, no máximo duas frases.\n"
        f"Não invente nomes de leitores: use apenas os números devolvidos pela ferramenta."
    )


def main() -> None:
    dados.criar_esquema(CFG.caminho_db)
    if "--http" in sys.argv:
        log.info("subindo em http://127.0.0.1:8931/mcp")
        server.run(transport="streamable-http", host="127.0.0.1", port=8931)
    else:
        server.run()


if __name__ == "__main__":
    main()
