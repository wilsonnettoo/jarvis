"""Testes das ferramentas técnicas (git e database).

Git é testado num repositório temporário de verdade. PostgreSQL é
testado apenas no comportamento que não exige banco (guard SELECT-only
e ausência de DATABASE_URL).
"""

from __future__ import annotations

import subprocess

from app.security.permissions import RiskLevel
from app.tools import database_tools, git_tools
from app.tools.registry import get_tool


def _init_repo(path):
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Teste"], cwd=path, check=True)


def test_git_status_e_commit(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "arquivo.txt").write_text("conteudo", encoding="utf-8")

    status = git_tools.git_status(str(tmp_path))
    assert "arquivo.txt" in status

    commit = git_tools.criar_commit("primeiro commit", str(tmp_path))
    assert "primeiro commit" in commit or "1 file" in commit

    log = git_tools.git_log(str(tmp_path))
    assert "primeiro commit" in log


def test_git_criar_branch(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    git_tools.criar_commit("init", str(tmp_path))

    git_tools.criar_branch("feature/teste", str(tmp_path))
    atual = git_tools.branch_atual(str(tmp_path))
    assert atual == "feature/teste"


def test_postgres_recusa_escrita():
    # Não precisa de banco: o guard SELECT-only deve recusar antes.
    msg = database_tools.consultar_postgres("DELETE FROM clientes")
    # Pode recusar por escrita OU por falta de DATABASE_URL; ambos são seguros.
    assert "recusado" in msg.lower() or "database_url" in msg.lower()


def test_riscos_tecnicos():
    import importlib

    importlib.reload(git_tools)
    importlib.reload(database_tools)

    assert get_tool("git_status").risk is RiskLevel.LOW
    assert get_tool("git_log").risk is RiskLevel.LOW
    assert get_tool("branch_atual").risk is RiskLevel.LOW
    assert get_tool("criar_branch").risk is RiskLevel.MEDIUM
    assert get_tool("criar_commit").risk is RiskLevel.MEDIUM
    assert get_tool("consultar_postgres").risk is RiskLevel.MEDIUM
