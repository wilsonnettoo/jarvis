"""Saída de voz (TTS) do Jarvis.

MVP usa o comando `say` do macOS: grátis, offline, sem dependências, e com
vozes em português do BR (ex.: "Luciana"). A abstração `Speaker` permite
trocar depois por OpenAI TTS / ElevenLabs / Piper sem mexer no resto.
"""

from __future__ import annotations

import shutil
import subprocess

from app.config import settings


class Speaker:
    """Fala um texto usando o `say` do macOS."""

    def __init__(self, voice: str | None = None):
        # Voz configurável; se a configurada não existir, cai para a padrão.
        self.voice = voice if voice is not None else settings.jarvis_tts_voice
        self._say = shutil.which("say")
        self._voice_ok = self._check_voice()

    def _check_voice(self) -> bool:
        """Confere se a voz configurada está disponível no sistema."""
        if not self._say or not self.voice:
            return False
        listagem = subprocess.run(
            [self._say, "-v", "?"], capture_output=True, text=True
        )
        return self.voice.lower() in listagem.stdout.lower()

    def say(self, texto: str) -> None:
        """Fala o texto. Se o `say` não existir, falha silenciosamente."""
        if not self._say or not texto.strip():
            return
        comando = [self._say]
        if self._voice_ok:
            comando += ["-v", self.voice]
        comando.append(texto)
        subprocess.run(comando)

    def render_to_file(self, texto: str, caminho: str) -> bool:
        """Renderiza a fala para um arquivo (.aiff) em vez de tocar. Útil em testes."""
        if not self._say:
            return False
        comando = [self._say, "-o", caminho]
        if self._voice_ok:
            comando += ["-v", self.voice]
        comando.append(texto)
        return subprocess.run(comando).returncode == 0
