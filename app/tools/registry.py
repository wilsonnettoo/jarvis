"""Registro central de ferramentas do Jarvis.

Cada ferramenta é uma função Python decorada com `@tool(...)`, que:
  1. associa um nível de risco (ver security.permissions);
  2. gera automaticamente o JSON Schema (formato OpenAI/LiteLLM) a partir
     da assinatura e da docstring da função;
  3. registra a função num catálogo global consultável pelo orquestrador.

Assim, adicionar uma capacidade nova ao Jarvis é só escrever uma função
decorada — o schema e a integração com o LLM saem de graça.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, get_type_hints

from app.security.permissions import RiskLevel

# Mapeia tipos Python -> tipos JSON Schema.
_PY_TO_JSON = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


@dataclass(frozen=True)
class Tool:
    """Uma ferramenta registrada: função + metadados de risco + schema."""

    name: str
    description: str
    risk: RiskLevel
    func: Callable[..., Any]
    schema: dict[str, Any]

    def __call__(self, **kwargs: Any) -> Any:
        return self.func(**kwargs)


# Catálogo global: nome -> Tool.
_REGISTRY: dict[str, Tool] = {}


def _build_schema(func: Callable[..., Any], description: str) -> dict[str, Any]:
    """Constrói o JSON Schema da ferramenta a partir da assinatura."""
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    properties: dict[str, Any] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue
        py_type = hints.get(param_name, str)
        json_type = _PY_TO_JSON.get(py_type, "string")
        properties[param_name] = {"type": json_type}
        # Parâmetro sem default é obrigatório.
        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def tool(
    *, risk: RiskLevel, description: str | None = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator que registra uma função como ferramenta do Jarvis.

    Uso:
        @tool(risk=RiskLevel.LOW, description="Abre uma URL no navegador.")
        def abrir_site(url: str) -> str:
            ...

    A descrição, se omitida, vem da primeira linha da docstring.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        desc = description or (func.__doc__ or "").strip().split("\n")[0]
        if not desc:
            raise ValueError(
                f"A ferramenta '{func.__name__}' precisa de uma descrição "
                "(no decorator ou na docstring)."
            )
        schema = _build_schema(func, desc)
        _REGISTRY[func.__name__] = Tool(
            name=func.__name__,
            description=desc,
            risk=risk,
            func=func,
            schema=schema,
        )
        return func

    return decorator


def get_tool(name: str) -> Tool | None:
    """Retorna a ferramenta registrada com esse nome, ou None."""
    return _REGISTRY.get(name)


def all_tools() -> list[Tool]:
    """Lista todas as ferramentas registradas."""
    return list(_REGISTRY.values())


def tool_schemas() -> list[dict[str, Any]]:
    """Lista os JSON Schemas, no formato que o LiteLLM/LLM espera."""
    return [t.schema for t in _REGISTRY.values()]


def clear_registry() -> None:
    """Limpa o catálogo. Usado em testes."""
    _REGISTRY.clear()
