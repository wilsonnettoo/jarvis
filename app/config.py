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

    # --- Banco de dados (ferramentas técnicas) ---
    # String de conexão PostgreSQL, ex.: postgresql://user:senha@host:5432/db
    database_url: str | None = None

    # --- Voz ---
    picovoice_access_key: str | None = None
    # Idioma usado para STT/TTS.
    jarvis_language: str = "pt"
    # Tamanho do modelo faster-whisper: tiny/base/small/medium/large-v3.
    # "small" é um bom equilíbrio de qualidade x velocidade em PT-BR.
    jarvis_stt_model: str = "small"
    # Motor de TTS: "openai" (natural, usa OPENAI_API_KEY) ou "say" (macOS, offline).
    jarvis_tts_engine: str = "openai"
    # Modelo OpenAI de TTS (tts-1 = rápido; tts-1-hd = maior qualidade).
    jarvis_tts_model: str = "tts-1"
    # Voz OpenAI: alloy/echo/fable/onyx/nova/shimmer (nova soa bem em PT-BR).
    jarvis_openai_voice: str = "nova"
    # Voz do macOS `say` (fallback): ex. "Luciana" (PT-BR). Vazio = padrão.
    jarvis_tts_voice: str = "Luciana"

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
