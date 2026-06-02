"""Entrada de voz do Jarvis: captura do microfone + transcrição (STT).

- Captura via `sounddevice` a 16 kHz mono (formato que o Whisper espera).
- Para de gravar por detecção de silêncio (energia/RMS): começa a contar
  quando detecta fala e encerra após um período de silêncio.
- STT local com `faster-whisper` (grátis, offline). O modelo é carregado
  preguiçosamente e reutilizado entre transcrições.

A classe `Transcriber` isola o STT, permitindo trocar por OpenAI Whisper
API no futuro sem mexer no resto.
"""

from __future__ import annotations

import numpy as np

from app.config import settings

SAMPLE_RATE = 16_000  # Hz, mono — formato nativo do Whisper.
_BLOCK = 1600  # ~100 ms por bloco de leitura.


def gravar_ate_silencio(
    max_segundos: float = 15.0,
    silencio_seg: float = 1.2,
    limiar: float | None = None,
) -> np.ndarray:
    """Grava do microfone até detectar silêncio (ou atingir o tempo máximo).

    Se `limiar` for None (padrão), calibra automaticamente o limiar de fala
    a partir do ruído de fundo medido nos primeiros ~0,4s — isso adapta a
    detecção a microfones de ganhos diferentes.

    Retorna o áudio como ndarray float32 mono em 16 kHz. Importa o
    `sounddevice` aqui dentro para não exigir áudio em quem só usa texto.
    """
    import sounddevice as sd

    blocos: list[np.ndarray] = []
    blocos_silencio = 0
    blocos_para_parar = int(silencio_seg * SAMPLE_RATE / _BLOCK)
    max_blocos = int(max_segundos * SAMPLE_RATE / _BLOCK)
    houve_fala = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=_BLOCK
    ) as stream:
        # Calibração: estima o ruído de fundo em ~0,4s (4 blocos de 100 ms).
        if limiar is None:
            ruido = []
            for _ in range(4):
                bloco, _ = stream.read(_BLOCK)
                bloco = bloco.reshape(-1)
                blocos.append(bloco)
                ruido.append(float(np.sqrt(np.mean(bloco**2))))
            piso = float(np.mean(ruido))
            # Limiar = 3x o ruído de fundo, com um mínimo de segurança.
            limiar = max(piso * 3.0, 0.008)

        for _ in range(max_blocos):
            bloco, _overflow = stream.read(_BLOCK)
            bloco = bloco.reshape(-1)
            blocos.append(bloco)

            rms = float(np.sqrt(np.mean(bloco**2)))
            if rms >= limiar:
                houve_fala = True
                blocos_silencio = 0
            elif houve_fala:
                blocos_silencio += 1
                if blocos_silencio >= blocos_para_parar:
                    break

    if not blocos:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(blocos).astype(np.float32)


class Transcriber:
    """Transcreve áudio em texto com faster-whisper (carregado uma vez)."""

    def __init__(self, model_size: str | None = None, language: str | None = None):
        self.model_size = model_size or settings.jarvis_stt_model
        self.language = language or settings.jarvis_language
        self._model = None  # carregamento preguiçoso

    def _ensure_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            # int8 em CPU é rápido e leve; ideal para Mac sem GPU dedicada.
            self._model = WhisperModel(
                self.model_size, device="cpu", compute_type="int8"
            )
        return self._model

    def transcrever(self, audio: np.ndarray) -> str:
        """Converte áudio (float32 16 kHz) em texto. Vazio se nada audível."""
        if audio.size == 0:
            return ""
        model = self._ensure_model()
        segmentos, _info = model.transcribe(audio, language=self.language)
        return " ".join(seg.text for seg in segmentos).strip()
