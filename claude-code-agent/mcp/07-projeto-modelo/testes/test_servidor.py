"""Testes do servidor MCP pela interface do protocolo.

Conectamos com `Client(server)` — em processo, sem subprocesso e sem porta.
É rápido o bastante para rodar a cada salvamento, e exercita o caminho real:
validação de schema, serialização, `isError`, `structured_content`.
"""
import mcp.types as types
import pytest
from mcp.client import Client

ISBN_ROSA = "9788535902778"      # 3 exemplares
ISBN_CLARICE = "9788576570271"   # 1 exemplar


async def aceitar(context, params):
    """Cliente que confirma toda elicitação."""
    return types.ElicitResult(action="accept", content={"confirmar": True})


async def recusar(context, params):
    return types.ElicitResult(action="decline")


# --------------------------------------------------------------------------- #
# Contrato: o que o modelo enxerga
# --------------------------------------------------------------------------- #
@pytest.mark.anyio
async def test_lista_de_ferramentas_e_estavel(servidor):
    async with Client(servidor) as c:
        nomes = sorted(t.name for t in (await c.list_tools()).tools)
    assert nomes == [
        "buscar_livros",
        "detalhar_livro",
        "devolver_livro",
        "emprestar_livro",
        "emprestimos_do_leitor",
        "estatisticas_do_acervo",
    ]


@pytest.mark.anyio
async def test_toda_ferramenta_tem_descricao_util(servidor):
    """Sem descrição, o modelo chuta. Isto é um teste de contrato, não de estilo."""
    async with Client(servidor) as c:
        for t in (await c.list_tools()).tools:
            assert t.description and len(t.description) > 40, t.name


@pytest.mark.anyio
async def test_parametro_de_confirmacao_nao_vaza_para_o_modelo(servidor):
    """`confirmacao` é preenchido pelo usuário via MRTR, não pelo modelo."""
    async with Client(servidor, elicitation_callback=aceitar) as c:
        t = next(t for t in (await c.list_tools()).tools if t.name == "emprestar_livro")
    assert set(t.input_schema["properties"]) == {"isbn", "leitor"}


# --------------------------------------------------------------------------- #
# Caminho feliz
# --------------------------------------------------------------------------- #
@pytest.mark.anyio
async def test_busca_encontra_por_autor(servidor):
    async with Client(servidor) as c:
        r = await c.call_tool("buscar_livros", {"termo": "Machado"})
    assert not r.is_error
    assert r.structured_content["encontrados"] == 1
    assert r.structured_content["livros"][0]["isbn"] == "9788525406958"


@pytest.mark.anyio
async def test_emprestar_e_devolver(servidor):
    async with Client(servidor, elicitation_callback=aceitar) as c:
        e = await c.call_tool("emprestar_livro", {"isbn": ISBN_ROSA, "leitor": "Ana"})
        assert not e.is_error
        assert e.structured_content["titulo"].startswith("Grande Sertão")

        d = await c.call_tool("detalhar_livro", {"isbn": ISBN_ROSA})
        assert d.structured_content["disponiveis"] == 2

        abertos = await c.call_tool("emprestimos_do_leitor", {"leitor": "Ana"})
        assert len(abertos.structured_content["result"]) == 1

        v = await c.call_tool("devolver_livro", {"isbn": ISBN_ROSA, "leitor": "Ana"})
        assert not v.is_error

        d2 = await c.call_tool("detalhar_livro", {"isbn": ISBN_ROSA})
        assert d2.structured_content["disponiveis"] == 3


# --------------------------------------------------------------------------- #
# Caminhos ruins — a metade que os tutoriais omitem.
# O que testamos aqui é a MENSAGEM, porque é ela que o modelo lê para se corrigir.
# --------------------------------------------------------------------------- #
@pytest.mark.anyio
async def test_isbn_inexistente_orienta_o_modelo(servidor):
    async with Client(servidor) as c:
        r = await c.call_tool("detalhar_livro", {"isbn": "0000000000000"})
    assert r.is_error
    assert "buscar_livros" in r.content[0].text


@pytest.mark.anyio
async def test_sem_exemplar_disponivel(servidor):
    async with Client(servidor, elicitation_callback=aceitar) as c:
        a = await c.call_tool("emprestar_livro", {"isbn": ISBN_CLARICE, "leitor": "Ana"})
        assert not a.is_error
        b = await c.call_tool("emprestar_livro", {"isbn": ISBN_CLARICE, "leitor": "Bruno"})
    assert b.is_error
    assert "Não há exemplar disponível" in b.content[0].text


@pytest.mark.anyio
async def test_mesmo_leitor_nao_leva_dois_exemplares_do_mesmo_titulo(servidor):
    async with Client(servidor, elicitation_callback=aceitar) as c:
        await c.call_tool("emprestar_livro", {"isbn": ISBN_ROSA, "leitor": "Ana"})
        r = await c.call_tool("emprestar_livro", {"isbn": ISBN_ROSA, "leitor": "Ana"})
    assert r.is_error
    assert "já está com um exemplar" in r.content[0].text


@pytest.mark.anyio
async def test_devolver_sem_emprestimo_aberto(servidor):
    async with Client(servidor) as c:
        r = await c.call_tool("devolver_livro", {"isbn": ISBN_ROSA, "leitor": "Ninguém"})
    assert r.is_error
    assert "emprestimos_do_leitor" in r.content[0].text


@pytest.mark.anyio
async def test_usuario_recusa_a_confirmacao_nao_altera_nada(servidor):
    async with Client(servidor, elicitation_callback=recusar) as c:
        r = await c.call_tool("emprestar_livro", {"isbn": ISBN_ROSA, "leitor": "Ana"})
        assert r.is_error
        assert "não confirmou" in r.content[0].text
        d = await c.call_tool("detalhar_livro", {"isbn": ISBN_ROSA})
    assert d.structured_content["disponiveis"] == 3


# --------------------------------------------------------------------------- #
# Defesas
# --------------------------------------------------------------------------- #
@pytest.mark.anyio
async def test_limite_acima_do_maximo_e_recusado_pelo_schema(servidor):
    """O modelo VAI tentar limite=10000."""
    async with Client(servidor) as c:
        r = await c.call_tool("buscar_livros", {"termo": "a", "limite": 10000})
    assert r.is_error


@pytest.mark.anyio
async def test_termo_curto_demais_e_recusado(servidor):
    async with Client(servidor) as c:
        r = await c.call_tool("buscar_livros", {"termo": "a"})
    assert r.is_error


@pytest.mark.anyio
async def test_injecao_de_sql_no_termo_nao_derruba_nem_apaga(servidor):
    """Consulta parametrizada: o texto é DADO, nunca CÓDIGO."""
    async with Client(servidor) as c:
        r = await c.call_tool("buscar_livros", {"termo": "'; DROP TABLE livros; --"})
        assert not r.is_error
        assert r.structured_content["encontrados"] == 0
        e = await c.call_tool("estatisticas_do_acervo", {})
    assert e.structured_content["titulos"] == 6


# --------------------------------------------------------------------------- #
# Recurso e prompt
# --------------------------------------------------------------------------- #
@pytest.mark.anyio
async def test_recurso_de_politica(servidor):
    async with Client(servidor) as c:
        r = await c.read_resource("biblioteca://politica")
    assert "REGULAMENTO" in r.contents[0].text


@pytest.mark.anyio
async def test_prompt_de_relatorio(servidor):
    async with Client(servidor) as c:
        p = await c.get_prompt("relatorio_de_atrasos", {"tom": "formal"})
    assert "formal" in p.messages[0].content.text
