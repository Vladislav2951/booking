from ipaddress import IPv4Address
from pathlib import Path
import tomllib
from typing import Literal, Union

from pydantic import IPvAnyAddress, computed_field
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
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "booking_db"

    REDIS_URI: str = "redis://localhost:6379/0"
    RATE_LIMIT_STORAGE_URI: str = "memory://"
    VERSION: str = _get_version_from_pyproject()

    model_config = {"env_file": ".env", "extra": "ignore"}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URI(self) -> str:
        return (
            "postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}".format(
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                database=self.POSTGRES_DB,
            )
        )


settings = Settings()
