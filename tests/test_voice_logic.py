"""Testes da lógica de voz que não exige microfone.

- Interpretação de respostas faladas (sim/não) — núcleo da confirmação por voz.
- Disponibilidade da hotword (openWakeWord instalado).
- VoiceConfirmer com speaker/transcriber falsos (sem áudio real).
"""

from __future__ import annotations

import numpy as np
import pytest

from app.security.confirmations import VoiceConfirmer, interpretar_resposta


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("sim", True),
        ("sim, pode", True),
        ("claro que sim", True),
        ("pode continuar", True),
        ("autorizo", True),
        ("não", False),
        ("não pode", False),  # recusa tem prioridade
        ("nao, cancela", False),
        ("", False),  # silêncio = não (seguro)
        ("talvez", False),  # ambíguo = não (seguro)
    ],
)
def test_interpretar_resposta(texto, esperado):
    assert interpretar_resposta(texto) is esperado


def test_hotword_disponivel():
    from app.audio.hotword import HotwordListener

    # openWakeWord está nas dependências, então deve estar disponível.
    assert HotwordListener.disponivel() is True


class _SpeakerFalso:
    def __init__(self):
        self.ditos = []

    def say(self, texto):
        self.ditos.append(texto)


class _TranscriberFalso:
    def __init__(self, resposta):
        self.resposta = resposta

    def transcrever(self, audio):  # noqa: ARG002
        return self.resposta


def test_voice_confirmer_sim(monkeypatch):
    # Evita abrir o microfone: gravar_ate_silencio retorna áudio vazio.
    import app.audio.recorder as recorder

    monkeypatch.setattr(
        recorder, "gravar_ate_silencio", lambda **k: np.zeros(0, dtype=np.float32)
    )
    conf = VoiceConfirmer(_SpeakerFalso(), _TranscriberFalso("sim, pode"))
    assert conf.confirm("Vou apagar o arquivo.") is True


def test_voice_confirmer_nao(monkeypatch):
    import app.audio.recorder as recorder

    monkeypatch.setattr(
        recorder, "gravar_ate_silencio", lambda **k: np.zeros(0, dtype=np.float32)
    )
    conf = VoiceConfirmer(_SpeakerFalso(), _TranscriberFalso("não"))
    assert conf.confirm("Vou apagar o arquivo.") is False
