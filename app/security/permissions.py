"""Classificação de risco e política de permissões do Jarvis.

Segue a seção 6 do README: toda ferramenta tem um nível de risco, e o
nível determina se a execução exige confirmação humana.

    BAIXO  -> executa direto
    MÉDIO  -> pede confirmação
    ALTO   -> pede confirmação explícita (sempre)
    PROIBIDO -> nunca executa

Esta é a camada que garante "segurança antes de autonomia". Nenhuma
ferramenta deve ser executada sem passar pelo guard (ver orchestrator).
"""

from __future__ import annotations

from enum import IntEnum


class RiskLevel(IntEnum):
    """Níveis de risco de uma ação. A ordem (Int) permite comparações."""

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    FORBIDDEN = 3

    @property
    def label(self) -> str:
        return {
            RiskLevel.LOW: "BAIXO",
            RiskLevel.MEDIUM: "MÉDIO",
            RiskLevel.HIGH: "ALTO",
            RiskLevel.FORBIDDEN: "PROIBIDO",
        }[self]


def requires_confirmation(risk: RiskLevel, require_confirmation_setting: bool) -> bool:
    """Diz se uma ação de dado risco precisa de confirmação humana.

    - FORBIDDEN nunca chega aqui para execução (é bloqueado antes).
    - HIGH sempre confirma.
    - MEDIUM confirma se a configuração de segurança estiver ligada.
    - LOW nunca confirma.
    """
    if risk is RiskLevel.HIGH:
        return True
    if risk is RiskLevel.MEDIUM:
        return require_confirmation_setting
    return False


def is_blocked(risk: RiskLevel) -> bool:
    """Ações PROIBIDAS são bloqueadas sem possibilidade de confirmação."""
    return risk is RiskLevel.FORBIDDEN
