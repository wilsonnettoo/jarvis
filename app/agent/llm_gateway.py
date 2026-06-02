"""Gateway de LLM — abstração sobre o provedor (OpenAI/Claude/Gemini/Ollama).

Usa LiteLLM para falar com qualquer provedor através de uma única interface
no formato OpenAI. Trocar de modelo é só mudar `JARVIS_MODEL` no `.env`.

O resto do sistema só conhece este gateway — nunca importa SDKs de
provedor diretamente.
"""

from __future__ import annotations

from typing import Any

import litellm

from app.config import settings

# Silencia logs verbosos do LiteLLM; deixamos a UI cuidar do output.
litellm.suppress_debug_info = True


class LLMGateway:
    """Cliente fino sobre o LiteLLM, configurado pelo `settings`."""

    def __init__(self, model: str | None = None, temperature: float | None = None):
        self.model = model or settings.jarvis_model
        self.temperature = (
            temperature if temperature is not None else settings.jarvis_temperature
        )

    async def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Faz uma chamada de chat (async). Retorna a `message` da resposta.

        Se `tools` for passado, o modelo pode devolver `tool_calls` no lugar
        (ou além) do conteúdo textual — o orquestrador trata isso.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await litellm.acompletion(**kwargs)
        return response.choices[0].message
