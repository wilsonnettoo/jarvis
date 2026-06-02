"""Grava uma amostra de voz do microfone para clonagem (XTTS/ElevenLabs).

Uso:
    python -m app.audio.record_sample            # grava 20s no caminho padrão
    python -m app.audio.record_sample 15 minha   # 15s -> app/storage/minha.wav

Uma amostra boa tem ~6-30s de voz limpa (sem música/ruído), falando
naturalmente. Aponte JARVIS_VOICE_SAMPLE no .env para o arquivo gerado.
"""

from __future__ import annotations

import sys

from app.config import STORAGE_DIR

SAMPLE_RATE = 22_050


def gravar(segundos: int = 20, nome: str = "voz_sample") -> str:
    import sounddevice as sd
    import soundfile as sf

    print(f"Gravando {segundos}s — fale naturalmente agora...", flush=True)
    audio = sd.rec(
        int(segundos * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32"
    )
    sd.wait()
    destino = str(STORAGE_DIR / f"{nome}.wav")
    sf.write(destino, audio, SAMPLE_RATE)
    print(f"Amostra salva em: {destino}")
    print("Aponte JARVIS_VOICE_SAMPLE para esse caminho no .env.")
    return destino


if __name__ == "__main__":
    segundos = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    nome = sys.argv[2] if len(sys.argv) > 2 else "voz_sample"
    gravar(segundos, nome)
