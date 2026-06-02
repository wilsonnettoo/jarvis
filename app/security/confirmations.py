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
