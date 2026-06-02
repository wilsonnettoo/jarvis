"""Memória do Jarvis.

Duas camadas, conforme o ADR:

1. Memória estruturada (perfil): fatos estáveis sobre o usuário, o trabalho
   e o ambiente técnico (seção 4 do README). Fica num YAML legível e é
   INJETADA no system prompt a cada conversa. Sem vetores no MVP.

2. Histórico + auditoria (SQLite): registro de mensagens e de ações
   executadas (com risco e se foram aprovadas). Serve para continuidade
   e para o log de segurança (pilar "segurança antes de autonomia").
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.config import settings

# Perfil-semente, baseado na seção 4 do README. Criado no primeiro uso.
_DEFAULT_PROFILE: dict[str, Any] = {
    "pessoal": [
        "Prefere português do Brasil.",
        "Gosta de comandos práticos.",
        "Prefere respostas objetivas e com passo a passo.",
        "Quer confirmação antes de ações sensíveis.",
    ],
    "profissional": [
        "Trabalha com agência de viagens chamada MV Travel.",
        "Foco em viagens de experiência e roteiros personalizados.",
        "Quer digitalizar atendimento e operação.",
        "Quer apoio em marketing, propostas e automações.",
    ],
    "tecnico": [
        "Usa MacBook Pro M4 Pro (macOS).",
        "Usa PostgreSQL, Docker e VS Code.",
        "Trabalha com projetos locais.",
    ],
}


class Memory:
    """Acesso à memória estruturada e ao histórico/auditoria em SQLite."""

    def __init__(self, db_path: Path | None = None, profile_path: Path | None = None):
        self.db_path = db_path or settings.db_path
        self.profile_path = profile_path or settings.profile_path
        self._init_db()
        self._ensure_profile()

    # ------------------------------------------------------------------ #
    # SQLite (histórico + auditoria)
    # ------------------------------------------------------------------ #
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    role      TEXT NOT NULL,
                    content   TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_log (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool       TEXT NOT NULL,
                    arguments  TEXT,
                    risk       TEXT NOT NULL,
                    approved   INTEGER NOT NULL,
                    result     TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )

    def save_message(self, role: str, content: str | None) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (role, content, created_at) VALUES (?, ?, ?)",
                (role, content, _now()),
            )

    def log_action(
        self,
        tool: str,
        arguments: dict[str, Any],
        risk: str,
        approved: bool,
        result: str | None,
    ) -> None:
        """Registra uma tentativa de execução de ferramenta (auditoria)."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_log (tool, arguments, risk, approved, result, "
                "created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (tool, json.dumps(arguments, ensure_ascii=False), risk,
                 int(approved), result, _now()),
            )

    # ------------------------------------------------------------------ #
    # Perfil (memória estruturada)
    # ------------------------------------------------------------------ #
    def _ensure_profile(self) -> None:
        if not self.profile_path.exists():
            self.profile_path.write_text(
                yaml.safe_dump(_DEFAULT_PROFILE, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

    def load_profile(self) -> dict[str, Any]:
        raw = self.profile_path.read_text(encoding="utf-8")
        return yaml.safe_load(raw) or {}

    def profile_as_text(self) -> str:
        """Renderiza o perfil como texto para injetar no system prompt."""
        profile = self.load_profile()
        linhas: list[str] = []
        titulos = {
            "pessoal": "Sobre o Wilson (pessoal)",
            "profissional": "Trabalho (MV Travel)",
            "tecnico": "Ambiente técnico",
            "operacional": "Operação",
        }
        for chave, itens in profile.items():
            titulo = titulos.get(chave, chave.capitalize())
            linhas.append(f"## {titulo}")
            for item in itens:
                linhas.append(f"- {item}")
            linhas.append("")
        return "\n".join(linhas).strip()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
