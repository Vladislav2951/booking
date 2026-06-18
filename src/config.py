from pathlib import Path
import tomllib
from typing import Literal

from pydantic_settings import BaseSettings


_PROJECT_ROOT = Path(__file__).parent.parent.parent


def _get_version_from_pyproject():
    try:
        pyproject_path = _PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


class Settings(BaseSettings):
    DATABASE_URI: str = "postgresql+asyncpg://postgres:password@localhost:5432/booking_db"
    REDIS_URI: str = "redis://localhost:6379/0"
    RATE_LIMIT_STORAGE_URI: str = "memory://"
    APP_ENV: Literal["dev", "prod", "test"] = "dev"
    VERSION: str = _get_version_from_pyproject()

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
