"""Testes dos módulos de áudio.

Não dependem de microfone nem de placa de som:
- Speaker é testado renderizando para arquivo (`say -o`), pulando se o
  comando não existir (ex.: CI fora do macOS).
- Transcriber é testado quanto ao comportamento com áudio vazio (não
  carrega o modelo de Whisper, que é pesado).
"""

from __future__ import annotations

import shutil

import numpy as np
import pytest

from app.audio.recorder import SAMPLE_RATE, Transcriber
from app.audio.speaker import Speaker


def test_transcrever_audio_vazio_retorna_vazio():
    # Áudio vazio não deve nem carregar o modelo.
    t = Transcriber()
    assert t.transcrever(np.zeros(0, dtype=np.float32)) == ""
    assert t._model is None


def test_sample_rate_e_16k():
    assert SAMPLE_RATE == 16_000


@pytest.mark.skipif(shutil.which("say") is None, reason="comando `say` só no macOS")
def test_speaker_render_para_arquivo(tmp_path):
    destino = tmp_path / "fala.aiff"
    speaker = Speaker()
    ok = speaker.render_to_file("teste de voz do Jarvis", str(destino))
    assert ok is True
    assert destino.exists() and destino.stat().st_size > 0
