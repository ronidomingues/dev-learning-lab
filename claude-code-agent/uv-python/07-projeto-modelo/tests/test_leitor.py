"""Testes da leitura do lockfile — a parte que pode quebrar quando o uv muda."""

import pytest

from lockspect import LockInvalido, ler_lock
from lockspect.modelo import _normalizar


def test_metadados_do_cabecalho(lock_exemplo):
    assert lock_exemplo.versao_do_formato == 1
    assert lock_exemplo.revisao == 3
    assert lock_exemplo.requires_python == ">=3.10"


def test_conta_pacotes(lock_exemplo):
    assert len(lock_exemplo.pacotes) == 8
    assert len(lock_exemplo.raizes) == 1
    assert len(lock_exemplo.de_terceiros) == 7


def test_projeto_local_e_editavel(lock_exemplo):
    raiz = lock_exemplo.raizes[0]
    assert raiz.nome == "app-exemplo"
    assert raiz.tipo_de_fonte == "editable"
    assert raiz.e_local is True
    assert raiz.dependencias == ("requests",)
    assert raiz.dependencias_de_dev == ("pytest",)


def test_dependencias_vem_ordenadas_e_sem_repeticao(lock_exemplo):
    requests = lock_exemplo.por_nome()["requests"]
    assert requests.dependencias == (
        "certifi",
        "charset-normalizer",
        "idna",
        "legado-sem-wheel",
        "urllib3",
    )


def test_detecta_pacote_sem_wheel(lock_exemplo):
    legado = lock_exemplo.por_nome()["legado-sem-wheel"]
    assert legado.tem_sdist is True
    assert legado.qtd_wheels == 0
    assert legado.so_sdist is True

    idna = lock_exemplo.por_nome()["idna"]
    assert idna.so_sdist is False


def test_dependentes_de(lock_exemplo):
    assert lock_exemplo.dependentes_de("urllib3") == ("requests",)
    assert lock_exemplo.dependentes_de("requests") == ("app-exemplo",)
    assert lock_exemplo.dependentes_de("app-exemplo") == ()


def test_arquivo_inexistente_levanta(tmp_path):
    with pytest.raises(FileNotFoundError):
        ler_lock(tmp_path / "nao-existe.lock")


def test_diretorio_procura_uv_lock_dentro(tmp_path):
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    lock = ler_lock(tmp_path)
    assert lock.versao_do_formato == 1


def test_toml_invalido_levanta_lock_invalido(tmp_path):
    ruim = tmp_path / "uv.lock"
    ruim.write_text("isto ][ não é toml", encoding="utf-8")
    with pytest.raises(LockInvalido, match="não é TOML válido"):
        ler_lock(ruim)


def test_sem_chave_version_levanta(tmp_path):
    ruim = tmp_path / "uv.lock"
    ruim.write_text('[project]\nname = "x"\n', encoding="utf-8")
    with pytest.raises(LockInvalido, match="é mesmo um uv.lock"):
        ler_lock(ruim)


def test_formato_futuro_e_recusado_com_mensagem_util(tmp_path):
    futuro = tmp_path / "uv.lock"
    futuro.write_text("version = 99\n", encoding="utf-8")
    with pytest.raises(LockInvalido, match="Atualize o lockspect"):
        ler_lock(futuro)


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("Foo.Bar_baz", "foo-bar-baz"),
        ("charset_normalizer", "charset-normalizer"),
        ("A__B", "a-b"),
        ("simples", "simples"),
    ],
)
def test_normalizacao_pep503(entrada, esperado):
    assert _normalizar(entrada) == esperado
