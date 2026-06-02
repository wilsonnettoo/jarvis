"""Configuração central do Jarvis.

Carrega variáveis do arquivo `.env` usando pydantic-settings. Todo o resto
do sistema deve importar `settings` daqui, em vez de ler `os.environ`
diretamente — assim há um único ponto de verdade para configuração.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz do projeto (…/jarvis). Usada para resolver caminhos de storage.
ROOT_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = ROOT_DIR / "app" / "storage"


class Settings(BaseSettings):
    """Configuração do Jarvis, lida do ambiente / arquivo .env."""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Cérebro (LLM) ---
    # Formato do modelo segue o LiteLLM. Ex.: "gpt-4o-mini",
    # "claude-sonnet-4-6", "gemini/gemini-1.5-pro", "ollama/llama3.1".
    jarvis_model: str = "gpt-4o-mini"
    jarvis_temperature: float = 0.4

    # --- Chaves de API (todas opcionais; só as do provedor em uso importam) ---
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_api_base: str | None = None

    # --- Voz (fases finais) ---
    picovoice_access_key: str | None = None

    # --- Segurança ---
    # Quando True, ações de risco MÉDIO/ALTO sempre pedem confirmação.
    jarvis_require_confirmation: bool = True

    # --- Caminhos derivados ---
    @property
    def db_path(self) -> Path:
        """Caminho do banco SQLite (memória + auditoria)."""
        return STORAGE_DIR / "jarvis.db"

    @property
    def profile_path(self) -> Path:
        """Caminho do perfil de memória estruturada (YAML)."""
        return STORAGE_DIR / "profile.yaml"


@lru_cache
def get_settings() -> Settings:
    """Retorna a configuração (cacheada) e garante que o storage exista."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()


# Instância global de conveniência.
settings = get_settings()
