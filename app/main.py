"""Ponto de entrada do Jarvis (Etapa 0: chat por texto no terminal).

Uso:
    python -m app.main

A voz (hotword, STT, TTS) entra nas fases finais; o núcleo aqui já é o
mesmo que a voz vai usar — só muda a borda de entrada/saída.
"""

from __future__ import annotations

import asyncio

from rich.console import Console
from rich.panel import Panel

# Importar os módulos de ferramentas REGISTRA as ferramentas no catálogo.
import app.tools.file_tools  # noqa: F401
import app.tools.system_tools  # noqa: F401
from app.agent.orchestrator import Orchestrator
from app.config import settings

console = Console()


async def main() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]Jarvis[/bold cyan] — assistente pessoal\n"
            f"Modelo: [yellow]{settings.jarvis_model}[/yellow]\n"
            "Digite sua mensagem. Use [bold]sair[/bold] para encerrar.",
            border_style="cyan",
        )
    )

    orchestrator = Orchestrator()

    while True:
        try:
            user_input = console.input("\n[bold green]você[/bold green] › ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Até logo, Wilson.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"sair", "exit", "quit"}:
            console.print("[dim]Até logo, Wilson.[/dim]")
            break

        with console.status("[cyan]Jarvis pensando...[/cyan]"):
            resposta = await orchestrator.send(user_input)

        console.print(f"[bold cyan]jarvis[/bold cyan] › {resposta}")


if __name__ == "__main__":
    asyncio.run(main())
