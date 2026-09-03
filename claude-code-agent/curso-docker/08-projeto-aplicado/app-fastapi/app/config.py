"""Configuração da aplicação, lida de variáveis de ambiente.

Regra de ouro do 12-factor: a aplicação NUNCA lê um arquivo de config
específico de ambiente. Ela lê variáveis de ambiente. Quem popula essas
variáveis é o Docker (via `environment:`, `env_file:` ou secrets).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # env_file só é usado em desenvolvimento local, fora de container.
    # Dentro do container, as variáveis chegam pelo ambiente do processo.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # aiosqlite = zero dependência externa, roda em qualquer lugar.
    # Em produção troque por: postgresql+asyncpg://user:pass@db:5432/app
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # Sempre que possível, o app deve saber em que ambiente está rodando.
    app_env: str = "development"

    # Usado pelo /health para reportar qual build está no ar.
    app_version: str = "dev"


settings = Settings()
