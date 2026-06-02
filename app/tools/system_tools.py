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
