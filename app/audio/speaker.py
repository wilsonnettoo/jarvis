"""Saída de voz (TTS) do Jarvis.

Dois motores, escolhidos por `JARVIS_TTS_ENGINE`:

  - "openai" (padrão): vozes naturais via OpenAI TTS (usa OPENAI_API_KEY,
    através do LiteLLM). Gera um MP3 e toca com `afplay` (nativo do macOS).
  - "say": comando `say` do macOS — robótico, porém offline e sem custo.
    Usado como fallback automático se o motor OpenAI falhar/sem chave.

A abstração `Speaker` isola tudo isso: trocar de motor não afeta o resto.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from app.config import settings


class Speaker:
    """Fala um texto usando o motor de TTS configurado."""

    def __init__(self, engine: str | None = None, voice: str | None = None):
        self.engine = engine or settings.jarvis_tts_engine
        self.macos_voice = voice if voice is not None else settings.jarvis_tts_voice
        self._say = shutil.which("say")
        self._afplay = shutil.which("afplay")
        self._xtts = None  # modelo XTTS carregado preguiçosamente
        # Degrada para um motor utilizável se faltar pré-requisito.
        if self.engine == "openai" and not settings.openai_api_key:
            self.engine = "say"
        if self.engine == "xtts" and not settings.jarvis_voice_sample:
            # Sem amostra de voz não dá para clonar; usa OpenAI/say.
            self.engine = "openai" if settings.openai_api_key else "say"
        if self.engine == "elevenlabs" and not (
            settings.elevenlabs_api_key and settings.elevenlabs_voice_id
        ):
            self.engine = "openai" if settings.openai_api_key else "say"

    # ------------------------------------------------------------------ #
    # API pública
    # ------------------------------------------------------------------ #
    def say(self, texto: str) -> None:
        """Fala o texto pelo motor configurado; em erro, degrada para o `say`."""
        if not texto.strip():
            return
        motores = {
            "xtts": self._falar_xtts,
            "elevenlabs": self._falar_elevenlabs,
            "openai": self._falar_openai,
        }
        falar = motores.get(self.engine)
        if falar:
            try:
                falar(texto)
                return
            except Exception:  # noqa: BLE001 - degrada para o say
                pass
        self._falar_macos(texto)

    def beep(self) -> None:
        """Toca um som curto do sistema (reconhecimento da hotword)."""
        som = "/System/Library/Sounds/Tink.aiff"
        player = self._afplay or shutil.which("afplay")
        if player and Path(som).exists():
            subprocess.run([player, som])

    def render_to_file(self, texto: str, caminho: str) -> bool:
        """Renderiza a fala para arquivo (usado em testes; usa o `say`)."""
        if not self._say:
            return False
        comando = [self._say, "-o", caminho]
        if self._macos_voice_ok():
            comando += ["-v", self.macos_voice]
        comando.append(texto)
        return subprocess.run(comando).returncode == 0

    # ------------------------------------------------------------------ #
    # Motores
    # ------------------------------------------------------------------ #
    def _falar_openai(self, texto: str) -> None:
        """Gera áudio com OpenAI TTS (via LiteLLM) e toca com afplay."""
        import litellm

        kwargs = {
            "model": settings.jarvis_tts_model,
            "voice": settings.jarvis_openai_voice,
            "input": texto,
        }
        # "instructions" (estilo) só existe nos modelos gpt-4o-*-tts.
        if settings.jarvis_tts_model.startswith("gpt-4o") and settings.jarvis_tts_instructions:
            kwargs["instructions"] = settings.jarvis_tts_instructions
        resposta = litellm.speech(**kwargs)
        destino = Path(tempfile.gettempdir()) / "jarvis_tts.mp3"
        resposta.stream_to_file(str(destino))
        player = self._afplay or shutil.which("afplay")
        if player:
            subprocess.run([player, str(destino)])
        else:
            raise RuntimeError("afplay indisponível para tocar o áudio")

    def _falar_xtts(self, texto: str) -> None:
        """Gera áudio com voz clonada (XTTS-v2 local) e toca com afplay."""
        import os

        os.environ.setdefault("COQUI_TOS_AGREED", "1")  # aceita licença não-interativa
        if self._xtts is None:
            from TTS.api import TTS

            self._xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        destino = Path(tempfile.gettempdir()) / "jarvis_xtts.wav"
        self._xtts.tts_to_file(
            text=texto,
            speaker_wav=settings.jarvis_voice_sample,
            language=settings.jarvis_language,
            file_path=str(destino),
        )
        self._tocar(destino)

    def _falar_elevenlabs(self, texto: str) -> None:
        """Gera áudio com voz clonada na ElevenLabs e toca com afplay."""
        from elevenlabs.client import ElevenLabs

        cliente = ElevenLabs(api_key=settings.elevenlabs_api_key)
        audio = cliente.text_to_speech.convert(
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model,
            text=texto,
            output_format="mp3_44100_128",
        )
        destino = Path(tempfile.gettempdir()) / "jarvis_eleven.mp3"
        with open(destino, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        self._tocar(destino)

    def _tocar(self, caminho: Path) -> None:
        """Toca um arquivo de áudio com afplay (macOS)."""
        player = self._afplay or shutil.which("afplay")
        if player:
            subprocess.run([player, str(caminho)])
        else:
            raise RuntimeError("afplay indisponível para tocar o áudio")

    def _falar_macos(self, texto: str) -> None:
        if not self._say:
            return
        comando = [self._say]
        if self._macos_voice_ok():
            comando += ["-v", self.macos_voice]
        comando.append(texto)
        subprocess.run(comando)

    def _macos_voice_ok(self) -> bool:
        if not self._say or not self.macos_voice:
            return False
        listagem = subprocess.run(
            [self._say, "-v", "?"], capture_output=True, text=True
        )
        return self.macos_voice.lower() in listagem.stdout.lower()
