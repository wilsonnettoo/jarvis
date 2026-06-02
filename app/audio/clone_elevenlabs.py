"""Clona uma voz no ElevenLabs a partir de uma amostra de áudio.

Pré-requisitos:
  - ELEVENLABS_API_KEY no .env
  - plano que permita Instant Voice Cloning (IVC) — o tier grátis NÃO clona;
    é preciso um plano pago (Starter+).

Uso:
    python -m app.audio.clone_elevenlabs                 # usa JARVIS_VOICE_SAMPLE
    python -m app.audio.clone_elevenlabs Jarvis caminho.wav

Ao final, imprime o ELEVENLABS_VOICE_ID para você colar no .env e trocar
JARVIS_TTS_ENGINE para "elevenlabs".
"""

from __future__ import annotations

import sys

from app.config import settings


def clonar(nome: str = "Jarvis", sample_path: str | None = None) -> str:
    from elevenlabs.client import ElevenLabs

    if not settings.elevenlabs_api_key:
        raise SystemExit("Defina ELEVENLABS_API_KEY no .env antes de clonar.")

    sample = sample_path or settings.jarvis_voice_sample
    if not sample:
        raise SystemExit("Sem amostra: defina JARVIS_VOICE_SAMPLE ou passe o caminho.")

    client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    print(f"Enviando amostra '{sample}' para clonagem (limpando ruído)...")
    with open(sample, "rb") as f:
        voz = client.voices.ivc.create(
            name=nome,
            files=[f],
            remove_background_noise=True,  # ajuda com trilha/efeitos da amostra
        )

    print("\n✅ Voz clonada!")
    print(f"voice_id: {voz.voice_id}")
    print("\nCole no .env:")
    print(f"  ELEVENLABS_VOICE_ID={voz.voice_id}")
    print("  JARVIS_TTS_ENGINE=elevenlabs")
    return voz.voice_id


if __name__ == "__main__":
    nome_arg = sys.argv[1] if len(sys.argv) > 1 else "Jarvis"
    caminho_arg = sys.argv[2] if len(sys.argv) > 2 else None
    clonar(nome_arg, caminho_arg)
