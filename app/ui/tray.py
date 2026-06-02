"""Bandeja na barra de menu do macOS (rumps). EXPERIMENTAL.

Mostra o estado do Jarvis como ícone no topo da tela e permite acionar a
conversa por voz com um clique. O CLI `python -m app.main --voz` continua
sendo o caminho principal/estável; esta bandeja é uma camada visual por cima
do mesmo núcleo.

Rodar:
    python -m app.ui.tray

Observação: precisa de uma sessão gráfica do macOS (não roda "headless").
A captura de voz roda numa thread de trabalho; o ícone é atualizado por um
timer na thread principal (padrão seguro para UI no Cocoa).
"""

from __future__ import annotations

import asyncio
import threading

import rumps

_ICONES = {
    "idle": "🟣 Jarvis",
    "ouvindo": "🔴 ouvindo",
    "pensando": "🟡 pensando",
    "falando": "🔵 falando",
}
_ITEM_FALAR = "🎤 Falar com o Jarvis"


class JarvisTray(rumps.App):
    """App de barra de menu que aciona o pipeline de voz do Jarvis."""

    def __init__(self):
        super().__init__("Jarvis", title=_ICONES["idle"], quit_button="Sair")
        self.menu = [_ITEM_FALAR]
        self.estado = "idle"
        self._busy = threading.Lock()
        self._iniciar_nucleo()

    def _iniciar_nucleo(self) -> None:
        # Registra ferramentas e prepara orquestrador/áudio.
        import app.tools.database_tools  # noqa: F401
        import app.tools.file_tools  # noqa: F401
        import app.tools.git_tools  # noqa: F401
        import app.tools.system_tools  # noqa: F401
        from app.agent.orchestrator import Orchestrator
        from app.audio.recorder import Transcriber
        from app.audio.speaker import Speaker
        from app.security.confirmations import VoiceConfirmer

        self.speaker = Speaker()
        self.transcriber = Transcriber()
        self.orchestrator = Orchestrator(
            confirmer=VoiceConfirmer(self.speaker, self.transcriber)
        )

    @rumps.clicked(_ITEM_FALAR)
    def _ao_clicar_falar(self, _sender) -> None:
        if self._busy.locked():
            return
        threading.Thread(target=self._ciclo_de_voz, daemon=True).start()

    @rumps.timer(0.4)
    def _atualizar_icone(self, _timer) -> None:
        self.title = _ICONES.get(self.estado, _ICONES["idle"])

    def _ciclo_de_voz(self) -> None:
        from app.audio.recorder import gravar_ate_silencio

        with self._busy:
            try:
                self.estado = "ouvindo"
                audio = gravar_ate_silencio()
                self.estado = "pensando"
                texto = self.transcriber.transcrever(audio)
                if not texto:
                    return
                resposta = asyncio.run(self.orchestrator.send(texto))
                self.estado = "falando"
                self.speaker.say(resposta)
            finally:
                self.estado = "idle"


def main() -> None:
    JarvisTray().run()


if __name__ == "__main__":
    main()
