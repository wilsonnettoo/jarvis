"""Ponto de entrada do Jarvis.

Modos:
    python -m app.main           # chat por texto (terminal)
    python -m app.main --voz     # conversa por voz (push-to-talk)

O núcleo (orquestrador, ferramentas, segurança, memória) é o mesmo nos
dois modos; muda apenas a borda de entrada/saída.
"""

from __future__ import annotations

import argparse
import asyncio

from rich.console import Console
from rich.panel import Panel

# Importar os módulos de ferramentas REGISTRA as ferramentas no catálogo.
import app.tools.database_tools  # noqa: F401
import app.tools.file_tools  # noqa: F401
import app.tools.git_tools  # noqa: F401
import app.tools.system_tools  # noqa: F401
from app.agent.orchestrator import Orchestrator
from app.config import settings

console = Console()


async def modo_texto() -> None:
    """REPL de texto no terminal."""
    console.print(
        Panel.fit(
            "[bold cyan]Jarvis[/bold cyan] — assistente pessoal (texto)\n"
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


async def modo_voz() -> None:
    """Conversa por voz: push-to-talk -> STT -> LLM -> TTS."""
    # Imports de áudio aqui dentro: só carregam quando o modo voz é usado.
    from app.audio.recorder import Transcriber, gravar_ate_silencio
    from app.audio.speaker import Speaker

    console.print(
        Panel.fit(
            "[bold cyan]Jarvis[/bold cyan] — assistente pessoal (voz)\n"
            f"Modelo: [yellow]{settings.jarvis_model}[/yellow] | "
            f"STT: [yellow]{settings.jarvis_stt_model}[/yellow] | "
            f"voz: [yellow]{settings.jarvis_tts_voice}[/yellow]\n"
            "[bold]Enter[/bold] para falar · diga/[bold]sair[/bold] para encerrar.",
            border_style="cyan",
        )
    )

    orchestrator = Orchestrator()
    speaker = Speaker()

    with console.status("[cyan]Carregando modelo de voz...[/cyan]"):
        transcriber = Transcriber()

    while True:
        try:
            console.input("\n[dim](Enter para falar)[/dim] ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Até logo, Wilson.[/dim]")
            break

        console.print("[bold red]🎤 ouvindo...[/bold red]")
        audio = gravar_ate_silencio()

        with console.status("[cyan]🧠 transcrevendo...[/cyan]"):
            texto = transcriber.transcrever(audio)

        if not texto:
            console.print("[dim]Não entendi nada. Tente de novo.[/dim]")
            continue

        console.print(f"[bold green]você[/bold green] › {texto}")
        if texto.lower().strip(" .!?") in {"sair", "encerrar", "tchau"}:
            speaker.say("Até logo, Wilson.")
            console.print("[dim]Até logo, Wilson.[/dim]")
            break

        with console.status("[cyan]🧠 pensando...[/cyan]"):
            resposta = await orchestrator.send(texto)

        console.print(f"[bold cyan]jarvis[/bold cyan] › {resposta}")
        console.print("[bold blue]🔊 falando...[/bold blue]")
        speaker.say(resposta)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis — assistente pessoal")
    parser.add_argument(
        "--voz", action="store_true", help="inicia no modo de conversa por voz"
    )
    args = parser.parse_args()
    asyncio.run(modo_voz() if args.voz else modo_texto())


if __name__ == "__main__":
    main()
