"""Orquestrador do Jarvis — o laço central do agente.

Fluxo de um turno:
    usuário -> LLM -> (talvez tool_calls) -> guard de segurança -> execução
            -> resultado volta pro LLM -> ... -> resposta final em texto.

Toda execução de ferramenta passa OBRIGATORIAMENTE pelo guard
(`_executar_ferramenta`), que aplica a política de risco e registra
auditoria. Nenhuma ferramenta é chamada fora daqui.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from app.agent.llm_gateway import LLMGateway
from app.agent.memory import Memory
from app.agent.prompts import build_system_prompt
from app.config import settings
from app.security.confirmations import Confirmer, TerminalConfirmer
from app.security.permissions import RiskLevel, is_blocked, requires_confirmation
from app.tools.registry import get_tool, tool_schemas

# Limite de iterações de tool-calling por turno (evita loop infinito).
_MAX_STEPS = 8


class Orchestrator:
    """Coordena LLM, ferramentas, segurança e memória."""

    def __init__(
        self,
        gateway: LLMGateway | None = None,
        memory: Memory | None = None,
        confirmer: Confirmer | None = None,
    ):
        self.gateway = gateway or LLMGateway()
        self.memory = memory or Memory()
        self.confirmer = confirmer or TerminalConfirmer()

        system_prompt = build_system_prompt(self.memory.profile_as_text())
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    async def send(self, user_input: str) -> str:
        """Processa uma fala/texto do usuário e devolve a resposta final."""
        self.messages.append({"role": "user", "content": user_input})
        self.memory.save_message("user", user_input)

        for _ in range(_MAX_STEPS):
            message = await self.gateway.complete(
                messages=self.messages,
                tools=tool_schemas(),
            )
            self.messages.append(message.model_dump())

            tool_calls = getattr(message, "tool_calls", None)
            if not tool_calls:
                content = message.content or ""
                self.memory.save_message("assistant", content)
                return content

            # Executa cada ferramenta pedida e devolve o resultado ao modelo.
            for call in tool_calls:
                resultado = self._executar_ferramenta(
                    call.function.name,
                    _parse_args(call.function.arguments),
                )
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": resultado,
                    }
                )

        return "Atingi o limite de passos para esta tarefa. Pode reformular?"

    def _executar_ferramenta(self, nome: str, args: dict[str, Any]) -> str:
        """Guard de segurança + execução. Único ponto que roda ferramentas."""
        ferramenta = get_tool(nome)
        if ferramenta is None:
            return f"[erro] Ferramenta desconhecida: {nome}"

        risco: RiskLevel = ferramenta.risk

        # 1. Ações proibidas nunca rodam.
        if is_blocked(risco):
            self.memory.log_action(nome, args, risco.label, approved=False,
                                   result="bloqueada (proibida)")
            return f"[bloqueado] A ação '{nome}' é proibida por política de segurança."

        # 2. Ações de risco médio/alto pedem confirmação humana.
        if requires_confirmation(risco, settings.jarvis_require_confirmation):
            msg = (
                f"Wilson, a ação '{nome}' é de risco {risco.label} "
                f"com os parâmetros {args}."
            )
            if not self.confirmer.confirm(msg):
                self.memory.log_action(nome, args, risco.label, approved=False,
                                       result="recusada pelo usuário")
                return f"[cancelado] Você não autorizou a ação '{nome}'."

        # 3. Executa e registra auditoria.
        try:
            resultado = str(ferramenta(**args))
            self.memory.log_action(nome, args, risco.label, approved=True,
                                   result=resultado)
            return resultado
        except Exception as exc:  # noqa: BLE001 - reportar erro ao modelo
            erro = f"[erro] Falha ao executar '{nome}': {exc}"
            self.memory.log_action(nome, args, risco.label, approved=True, result=erro)
            return erro


def _parse_args(raw: str | None) -> dict[str, Any]:
    """Argumentos vêm como string JSON do LLM. Converte com tolerância."""
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
