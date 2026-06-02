"""Testes da camada de segurança e do registry de ferramentas.

Validam o coração do Jarvis: classificação de risco, política de
confirmação e o guard do orquestrador (nada de ferramenta rodando sem
passar pela política).
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.security.confirmations import AutoApproveConfirmer, AutoDenyConfirmer
from app.security.permissions import RiskLevel, is_blocked, requires_confirmation
from app.tools.registry import clear_registry, get_tool, tool


# --------------------------------------------------------------------- #
# Política de risco
# --------------------------------------------------------------------- #
def test_baixo_risco_nao_confirma():
    assert requires_confirmation(RiskLevel.LOW, True) is False


def test_alto_risco_sempre_confirma():
    # Mesmo com a configuração desligada, ALTO confirma.
    assert requires_confirmation(RiskLevel.HIGH, False) is True


def test_medio_risco_depende_da_config():
    assert requires_confirmation(RiskLevel.MEDIUM, True) is True
    assert requires_confirmation(RiskLevel.MEDIUM, False) is False


def test_proibido_e_bloqueado():
    assert is_blocked(RiskLevel.FORBIDDEN) is True
    assert is_blocked(RiskLevel.HIGH) is False


# --------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------- #
def test_decorator_registra_e_gera_schema():
    clear_registry()

    @tool(risk=RiskLevel.LOW, description="Soma dois números.")
    def somar(a: int, b: int = 0) -> int:
        return a + b

    t = get_tool("somar")
    assert t is not None
    assert t.risk is RiskLevel.LOW
    params = t.schema["function"]["parameters"]
    assert params["properties"]["a"]["type"] == "integer"
    assert "a" in params["required"]
    assert "b" not in params["required"]  # tem default


# --------------------------------------------------------------------- #
# Guard do orquestrador (sem chamar LLM de verdade)
# --------------------------------------------------------------------- #
class _FakeMemory:
    """Memória de mentira: não toca em disco, só guarda os logs."""

    def __init__(self) -> None:
        self.actions: list[dict[str, Any]] = []

    def profile_as_text(self) -> str:
        return "(perfil de teste)"

    def save_message(self, *args: Any, **kwargs: Any) -> None: ...

    def log_action(self, tool, arguments, risk, approved, result):  # noqa: ANN001
        self.actions.append(
            {"tool": tool, "approved": approved, "result": result}
        )


def _make_orchestrator(confirmer):
    # Importado aqui para garantir que o registry já existe.
    from app.agent.orchestrator import Orchestrator

    class _NoLLM:
        async def complete(self, *a, **k):  # pragma: no cover
            raise AssertionError("não deve chamar o LLM neste teste")

    return Orchestrator(gateway=_NoLLM(), memory=_FakeMemory(), confirmer=confirmer)


def test_guard_bloqueia_acao_proibida():
    clear_registry()

    @tool(risk=RiskLevel.FORBIDDEN, description="Ação proibida de teste.")
    def acao_proibida() -> str:
        raise AssertionError("nunca deve executar")

    orq = _make_orchestrator(AutoApproveConfirmer())
    resultado = orq._executar_ferramenta("acao_proibida", {})
    assert "bloqueado" in resultado.lower()
    assert orq.memory.actions[-1]["approved"] is False


def test_guard_cancela_quando_usuario_recusa():
    clear_registry()
    executou = {"sim": False}

    @tool(risk=RiskLevel.HIGH, description="Ação de alto risco de teste.")
    def acao_perigosa() -> str:
        executou["sim"] = True
        return "executei"

    orq = _make_orchestrator(AutoDenyConfirmer())
    resultado = orq._executar_ferramenta("acao_perigosa", {})
    assert "cancelado" in resultado.lower()
    assert executou["sim"] is False  # não executou


def test_guard_executa_baixo_risco_sem_confirmar():
    clear_registry()

    @tool(risk=RiskLevel.LOW, description="Ação inofensiva de teste.")
    def acao_ok(valor: str) -> str:
        return f"ok:{valor}"

    orq = _make_orchestrator(AutoDenyConfirmer())  # negaria, mas nem pergunta
    resultado = orq._executar_ferramenta("acao_ok", {"valor": "abc"})
    assert resultado == "ok:abc"
    assert orq.memory.actions[-1]["approved"] is True
