"""Ferramentas de sistema do Jarvis (macOS).

Etapa 0: implementamos as de risco BAIXO para validar o fluxo fim-a-fim
(LLM -> tool -> guard -> execução). As demais (executar comando, etc.)
entram nas próximas fases, já cobertas pela camada de risco.

Importante: importar este módulo registra as ferramentas no catálogo
(via decorator `@tool`). Por isso o orquestrador faz `import system_tools`.
"""

from __future__ import annotations

import subprocess
import webbrowser
from pathlib import Path

from app.security.permissions import RiskLevel
from app.tools.registry import tool


@tool(risk=RiskLevel.LOW, description="Abre uma URL no navegador padrão.")
def abrir_site(url: str) -> str:
    """Abre uma URL no navegador padrão do sistema."""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    webbrowser.open(url)
    return f"Abri {url} no navegador."


@tool(
    risk=RiskLevel.LOW,
    description="Abre um aplicativo do macOS pelo nome (ex.: 'Safari', 'VS Code').",
)
def abrir_programa(nome: str) -> str:
    """Abre um aplicativo no macOS usando o comando `open -a`."""
    resultado = subprocess.run(
        ["open", "-a", nome],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        erro = resultado.stderr.strip() or "aplicativo não encontrado"
        return f"Não consegui abrir '{nome}': {erro}"
    return f"Abri o aplicativo '{nome}'."


@tool(
    risk=RiskLevel.LOW,
    description="Abre uma pasta de projeto no VS Code.",
)
def abrir_projeto_vscode(caminho: str) -> str:
    """Abre um diretório no VS Code (via `code` ou, se faltar, `open -a`)."""
    alvo = str(Path(caminho).expanduser().resolve())
    # Tenta a CLI `code`; se não estiver no PATH, usa o `open -a`.
    resultado = subprocess.run(["code", alvo], capture_output=True, text=True)
    if resultado.returncode != 0:
        fallback = subprocess.run(
            ["open", "-a", "Visual Studio Code", alvo],
            capture_output=True,
            text=True,
        )
        if fallback.returncode != 0:
            erro = fallback.stderr.strip() or "VS Code não encontrado"
            return f"Não consegui abrir o VS Code em '{alvo}': {erro}"
    return f"Abri o projeto '{alvo}' no VS Code."


@tool(
    risk=RiskLevel.LOW,
    description="Verifica os containers Docker em execução.",
)
def verificar_status_docker() -> str:
    """Lista containers em execução (`docker ps`). Apenas leitura."""
    resultado = subprocess.run(
        ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Image}}"],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        erro = resultado.stderr.strip() or "Docker não disponível"
        return f"Não consegui consultar o Docker: {erro}"
    saida = resultado.stdout.strip()
    return saida or "Nenhum container em execução."


@tool(
    risk=RiskLevel.LOW,
    description="Lista os processos em execução, opcionalmente filtrando por nome.",
)
def listar_processos(filtro: str = "") -> str:
    """Lista processos (via `ps`), filtrando pelo termo informado se houver."""
    resultado = subprocess.run(
        ["ps", "-axo", "pid,pcpu,pmem,comm"],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        return f"Não consegui listar processos: {resultado.stderr.strip()}"
    linhas = resultado.stdout.strip().splitlines()
    if filtro:
        cabecalho = linhas[:1]
        corpo = [ln for ln in linhas[1:] if filtro.lower() in ln.lower()]
        linhas = cabecalho + corpo[:50]
        if len(corpo) == 0:
            return f"Nenhum processo casando com '{filtro}'."
    else:
        linhas = linhas[:50]
    return "\n".join(linhas)
