"""Camada de confirmação humana.

Abstrai *como* o Jarvis pede confirmação. Hoje é via terminal (texto);
na fase de voz, basta trocar a implementação por uma que fale a pergunta
e ouça a resposta — o resto do sistema não muda.
"""

from __future__ import annotations

from typing import Protocol

from rich.console import Console
from rich.prompt import Confirm

_console = Console()


class Confirmer(Protocol):
    """Contrato de um confirmador (texto, voz, GUI...)."""

    def confirm(self, message: str) -> bool:  # pragma: no cover - protocolo
        ...


class TerminalConfirmer:
    """Pede confirmação no terminal. Padrão da Etapa 0."""

    def confirm(self, message: str) -> bool:
        _console.print(f"\n[bold yellow]⚠  {message}[/bold yellow]")
        return Confirm.ask("[bold]Posso continuar?[/bold]", default=False)


class AutoDenyConfirmer:
    """Nega tudo. Útil em testes e execuções não interativas."""

    def confirm(self, message: str) -> bool:  # noqa: ARG002
        return False


class AutoApproveConfirmer:
    """Aprova tudo. Use APENAS em testes controlados — nunca em produção."""

    def confirm(self, message: str) -> bool:  # noqa: ARG002
        return True


# Palavras que indicam autorização / recusa numa resposta falada.
_SIM = ("sim", "pode", "claro", "autorizo", "confirmo", "positivo", "isso", "ok")
_NAO = ("não", "nao", "negativo", "cancela", "cancele", "para", "pare", "jamais")


def interpretar_resposta(texto: str) -> bool:
    """Interpreta uma resposta falada como sim/não. Em dúvida, nega (seguro)."""
    t = texto.lower()
    # Recusa tem prioridade ("não pode" deve negar).
    if any(p in t for p in _NAO):
        return False
    return any(p in t for p in _SIM)


class VoiceConfirmer:
    """Confirma por voz: fala a pergunta (TTS) e ouve a resposta (STT).

    Recebe um `speaker` e um `transcriber` já prontos (injetados pelo loop
    de voz). Mantém a camada de segurança independente dos detalhes de áudio.
    """

    def __init__(self, speaker, transcriber):
        self.speaker = speaker
        self.transcriber = transcriber

    def confirm(self, message: str) -> bool:
        from app.audio.recorder import gravar_ate_silencio

        self.speaker.say(f"{message} Posso continuar? Responda sim ou não.")
        _console.print("[bold red]🎤 ouvindo sua confirmação...[/bold red]")
        audio = gravar_ate_silencio(max_segundos=6)
        resposta = self.transcriber.transcrever(audio)
        _console.print(f"[dim]você disse: {resposta or '(nada)'}[/dim]")
        return interpretar_resposta(resposta)
