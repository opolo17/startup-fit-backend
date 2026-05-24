from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# app/config.py → 백엔드 프로젝트 루트 (startup-fit-backend)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILES = (
    PROJECT_ROOT / '.env',
    PROJECT_ROOT / '.env.local',
)


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = 'gpt-4o-mini'

    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding='utf-8',
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def env_file_hint() -> str:
    existing = [str(path) for path in ENV_FILES if path.is_file()]
    if existing:
        return ', '.join(existing)
    return f'{PROJECT_ROOT / ".env"} (없음 — .env.example 을 복사하세요)'
