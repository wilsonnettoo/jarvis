"""Ferramentas de git do Jarvis.

Chamam a CLI `git` via subprocess no diretório indicado (padrão: diretório
atual). Riscos conforme a seção 6 do README:
  - status/log/branch atual  -> BAIXO (só leitura)
  - criar branch / commit    -> MÉDIO (altera o repositório)

Operações destrutivas (reset --hard, push --force, etc.) não são expostas
aqui; entrariam como risco ALTO numa fase futura.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from app.security.permissions import RiskLevel
from app.tools.registry import tool


def _git(args: list[str], caminho: str) -> str:
    """Executa um comando git em `caminho` e devolve stdout/stderr."""
    repo = Path(caminho).expanduser().resolve()
    if not repo.is_dir():
        return f"Diretório não encontrado: {repo}"
    resultado = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    saida = (resultado.stdout or "").strip()
    erro = (resultado.stderr or "").strip()
    if resultado.returncode != 0:
        return f"[git erro] {erro or saida or 'falha desconhecida'}"
    return saida or erro or "(sem saída)"


@tool(risk=RiskLevel.LOW, description="Mostra o status do repositório git (arquivos modificados).")
def git_status(caminho: str = ".") -> str:
    """Retorna o `git status` resumido do repositório."""
    return _git(["status", "--short", "--branch"], caminho)


@tool(risk=RiskLevel.LOW, description="Mostra os últimos commits do repositório git.")
def git_log(caminho: str = ".", quantidade: int = 10) -> str:
    """Lista os últimos commits (hash curto + mensagem)."""
    return _git(["log", f"-{max(1, quantidade)}", "--oneline"], caminho)


@tool(risk=RiskLevel.LOW, description="Mostra o branch atual do repositório git.")
def branch_atual(caminho: str = ".") -> str:
    """Retorna o nome do branch ativo."""
    return _git(["rev-parse", "--abbrev-ref", "HEAD"], caminho)


@tool(risk=RiskLevel.MEDIUM, description="Cria um novo branch git e muda para ele.")
def criar_branch(nome: str, caminho: str = ".") -> str:
    """Cria e ativa um novo branch. Risco MÉDIO: confirma."""
    return _git(["checkout", "-b", nome], caminho)


@tool(
    risk=RiskLevel.MEDIUM,
    description="Faz commit de todas as mudanças com a mensagem informada.",
)
def criar_commit(mensagem: str, caminho: str = ".") -> str:
    """Roda `git add -A` e cria um commit. Risco MÉDIO: confirma."""
    add = _git(["add", "-A"], caminho)
    if add.startswith("[git erro]"):
        return add
    return _git(["commit", "-m", mensagem], caminho)
