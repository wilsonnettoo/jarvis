"""Hotword ("Jarvis") — ativação por palavra-chave.

NÃO IMPLEMENTADO no MVP de voz. A ativação atual é push-to-talk (Enter),
porque a hotword via Picovoice Porcupine exige uma chave de acesso
(PICOVOICE_ACCESS_KEY) que ainda não foi configurada.

Plano de implementação (fase futura):
  1. Obter chave grátis em console.picovoice.ai e pôr em PICOVOICE_ACCESS_KEY.
  2. Usar pvporcupine com o keyword "jarvis" para escutar continuamente.
  3. Ao detectar, disparar gravar_ate_silencio() do recorder.

Esta camada substituirá o push-to-talk sem mexer no resto do pipeline.
"""

from __future__ import annotations


def hotword_disponivel() -> bool:
    """Indica se a ativação por hotword está pronta para uso (ainda não)."""
    return False
