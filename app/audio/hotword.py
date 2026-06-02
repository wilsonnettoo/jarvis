"""Hotword ("Hey Jarvis") — ativação por palavra-chave.

Implementado com **openWakeWord** (open-source, grátis, offline, SEM chave
de API). Usa o modelo pré-treinado "hey_jarvis". É a alternativa ao
Picovoice Porcupine — que funcionaria igual, mas exige PICOVOICE_ACCESS_KEY.

Fluxo: escuta o microfone em blocos de 80 ms; quando o score do modelo
passa do limiar, considera que ouviu "Hey Jarvis" e devolve o controle ao
loop de voz, que então grava o comando.
"""

from __future__ import annotations

_FRAME = 1280  # 80 ms a 16 kHz — tamanho de bloco que o openWakeWord espera.
_MODELO = "hey_jarvis"


class HotwordListener:
    """Escuta continuamente até ouvir 'Hey Jarvis' (openWakeWord)."""

    def __init__(self, limiar: float = 0.5, modelo: str = _MODELO):
        self.limiar = limiar
        self.modelo = modelo
        self._model = None  # carregamento preguiçoso

    @staticmethod
    def disponivel() -> bool:
        """True se o openWakeWord está instalado e utilizável."""
        try:
            import openwakeword  # noqa: F401

            return True
        except Exception:  # noqa: BLE001
            return False

    def _ensure_model(self):
        if self._model is None:
            from openwakeword.model import Model

            self._model = Model(
                wakeword_models=[self.modelo], inference_framework="onnx"
            )
        return self._model

    def aguardar(self) -> bool:
        """Bloqueia até detectar a hotword. Retorna True quando ouve.

        Importa `sounddevice` aqui dentro para não exigir áudio em quem só
        usa o modo texto.
        """
        import numpy as np
        import sounddevice as sd

        model = self._ensure_model()
        model.reset()

        with sd.InputStream(
            samplerate=16_000, channels=1, dtype="int16", blocksize=_FRAME
        ) as stream:
            while True:
                frame, _overflow = stream.read(_FRAME)
                frame = np.asarray(frame, dtype=np.int16).reshape(-1)
                scores = model.predict(frame)
                if scores.get(self.modelo, 0.0) >= self.limiar:
                    return True
