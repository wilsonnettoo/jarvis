"""Testes das ferramentas de arquivo.

Usam tmp_path (pytest) para não tocar em arquivos reais do usuário.
Validam tanto o comportamento quanto a classificação de risco.
"""

from __future__ import annotations

from app.security.permissions import RiskLevel
from app.tools import file_tools
from app.tools.registry import get_tool


def test_criar_e_ler_arquivo(tmp_path):
    destino = tmp_path / "nota.txt"
    msg = file_tools.criar_arquivo(str(destino), "olá jarvis")
    assert "Criei" in msg
    assert destino.read_text(encoding="utf-8") == "olá jarvis"

    conteudo = file_tools.ler_arquivo(str(destino))
    assert conteudo == "olá jarvis"


def test_ler_arquivo_inexistente(tmp_path):
    msg = file_tools.ler_arquivo(str(tmp_path / "nao_existe.txt"))
    assert "não encontrado" in msg.lower()


def test_listar_e_pesquisar(tmp_path):
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "b.md").write_text("y", encoding="utf-8")

    listagem = file_tools.listar_arquivos(str(tmp_path))
    assert "a.txt" in listagem and "b.md" in listagem

    resultado = file_tools.pesquisar_arquivo("*.md", str(tmp_path))
    assert "b.md" in resultado and "a.txt" not in resultado


def test_mover_arquivo(tmp_path):
    origem = tmp_path / "origem.txt"
    origem.write_text("conteudo", encoding="utf-8")
    destino = tmp_path / "sub" / "destino.txt"

    msg = file_tools.mover_arquivo(str(origem), str(destino))
    assert "Movi" in msg
    assert not origem.exists()
    assert destino.read_text(encoding="utf-8") == "conteudo"


def test_riscos_corretos():
    # Outro teste pode ter limpado o registry global; recarrega para garantir
    # que as ferramentas de arquivo estão registradas.
    import importlib

    importlib.reload(file_tools)

    # Ações de escrita devem ser MÉDIO; leitura/listagem BAIXO.
    assert get_tool("criar_arquivo").risk is RiskLevel.MEDIUM
    assert get_tool("mover_arquivo").risk is RiskLevel.MEDIUM
    assert get_tool("ler_arquivo").risk is RiskLevel.LOW
    assert get_tool("listar_arquivos").risk is RiskLevel.LOW
    assert get_tool("pesquisar_arquivo").risk is RiskLevel.LOW
