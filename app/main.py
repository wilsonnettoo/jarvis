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
            "Digite sua mensagem. Use [bold]vai dormir[/bold] para encerrar.",
            border_style="cyan",
        )
    )

    orchestrator = Orchestrator()

    while True:
        try:
            user_input = console.input("\n[bold green]você[/bold green] › ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Boa noite, Wilson.[/dim]")
            break

        if not user_input:
            continue
        if "vai dormir" in user_input.lower():
            console.print("[dim]Boa noite, Wilson.[/dim]")
            break

        with console.status("[cyan]Jarvis pensando...[/cyan]"):
            resposta = await orchestrator.send(user_input)

        console.print(f"[bold cyan]jarvis[/bold cyan] › {resposta}")


async def modo_voz(forcar_ptt: bool = False) -> None:
    """Conversa por voz: (hotword|push-to-talk) -> STT -> LLM -> TTS."""
    # Imports de áudio aqui dentro: só carregam quando o modo voz é usado.
    from app.audio.hotword import HotwordListener
    from app.audio.recorder import Transcriber, gravar_ate_silencio
    from app.audio.speaker import Speaker
    from app.security.confirmations import VoiceConfirmer

    usar_hotword = HotwordListener.disponivel() and not forcar_ptt
    ativacao = "diga 'Hey Jarvis'" if usar_hotword else "Enter para falar"

    console.print(
        Panel.fit(
            "[bold cyan]Jarvis[/bold cyan] — assistente pessoal (voz)\n"
            f"Modelo: [yellow]{settings.jarvis_model}[/yellow] | "
            f"STT: [yellow]{settings.jarvis_stt_model}[/yellow] | "
            f"voz: [yellow]{settings.jarvis_openai_voice}[/yellow]\n"
            f"Ativação: [bold]{ativacao}[/bold] · diga [bold]vai dormir[/bold] para encerrar.",
            border_style="cyan",
        )
    )

    speaker = Speaker()
    with console.status("[cyan]Carregando modelos de voz...[/cyan]"):
        transcriber = Transcriber()
        listener = HotwordListener() if usar_hotword else None

    # Confirmações de ações sensíveis acontecem por voz neste modo.
    confirmer = VoiceConfirmer(speaker, transcriber)
    orchestrator = Orchestrator(confirmer=confirmer)

    while True:
        try:
            if usar_hotword:
                console.print("\n[dim](aguardando 'Hey Jarvis'...)[/dim]")
                await asyncio.to_thread(listener.aguardar)
                speaker.beep()
            else:
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
        if "vai dormir" in texto.lower():
            speaker.say("Boa noite, senhor. Entrando em modo de repouso.")
            console.print("[dim]Boa noite, Wilson.[/dim]")
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
    parser.add_argument(
        "--ptt",
        action="store_true",
        help="no modo voz, força push-to-talk (ignora a hotword)",
    )
    args = parser.parse_args()
    asyncio.run(modo_voz(forcar_ptt=args.ptt) if args.voz else modo_texto())


if __name__ == "__main__":
    main()
