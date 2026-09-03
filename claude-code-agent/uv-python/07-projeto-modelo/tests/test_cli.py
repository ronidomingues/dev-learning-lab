"""Testes da CLI — chamam main() diretamente, sem subprocesso."""

import json
from pathlib import Path

import pytest

from lockspect.cli import main

LOCK = str(Path(__file__).parent / "dados" / "exemplo.uv.lock")


def test_resumo_e_o_padrao(capsys):
    assert main(["--arquivo", LOCK, "--sem-cor"]) == 0
    saida = capsys.readouterr().out
    assert "Resumo do uv.lock" in saida
    assert "legado-sem-wheel" in saida


def test_arvore(capsys):
    assert main(["--arquivo", LOCK, "--sem-cor", "arvore"]) == 0
    saida = capsys.readouterr().out
    assert "app-exemplo" in saida
    assert "urllib3" in saida


def test_arvore_com_profundidade_limitada(capsys):
    assert main(["--arquivo", LOCK, "--sem-cor", "arvore", "-d", "1"]) == 0
    saida = capsys.readouterr().out
    assert "requests" in saida
    assert "urllib3" not in saida  # nível 2, cortado pela profundidade


def test_quem_depende(capsys):
    assert main(["--arquivo", LOCK, "--sem-cor", "quem", "urllib3"]) == 0
    assert "requests" in capsys.readouterr().out


def test_quem_com_pacote_inexistente_sai_com_1(capsys):
    assert main(["--arquivo", LOCK, "--sem-cor", "quem", "inexistente"]) == 1


def test_json_e_valido(capsys):
    assert main(["--arquivo", LOCK, "--json"]) == 0
    dados = json.loads(capsys.readouterr().out)
    assert dados["version"] == 1
    assert len(dados["packages"]) == 8
    assert any(p["sdist_only"] for p in dados["packages"])


def test_arquivo_ausente_sai_com_2(capsys, tmp_path):
    assert main(["--arquivo", str(tmp_path / "x.lock")]) == 2
    assert "dica:" in capsys.readouterr().err


def test_lock_invalido_sai_com_3(capsys, tmp_path):
    ruim = tmp_path / "uv.lock"
    ruim.write_text("version = 99\n", encoding="utf-8")
    assert main(["--arquivo", str(ruim)]) == 3


def test_variavel_de_ambiente_define_o_padrao(monkeypatch, capsys):
    monkeypatch.setenv("LOCKSPECT_LOCK", LOCK)
    import importlib

    from lockspect import cli

    importlib.reload(cli)
    try:
        assert cli.main(["--sem-cor"]) == 0
        assert "Resumo do uv.lock" in capsys.readouterr().out
    finally:
        monkeypatch.delenv("LOCKSPECT_LOCK")
        importlib.reload(cli)


def test_version(capsys):
    with pytest.raises(SystemExit) as saida:
        main(["--version"])
    assert saida.value.code == 0
    assert "lockspect" in capsys.readouterr().out
