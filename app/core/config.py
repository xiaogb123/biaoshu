"""全局配置：唯一读环境变量的地方，别的地方一律 from app.core.config import settings。"""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# app/core/config.py -> app/core -> app -> 项目根
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "BidSentry"
    ENV: str = "dev"

    # 注意驱动名：SQLAlchemy 2 + psycopg3 是 postgresql+psycopg://
    DATABASE_URL: str = "postgresql+psycopg://bidsentry:bidsentry@localhost:5433/bidsentry"

    SECRET_KEY: str = "dev-only-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    MAX_UPLOAD_MB: int = 50

    DEEPSEEK_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"


    @field_validator("UPLOAD_DIR")
    @classmethod
    def _absolute(cls, v: Path) -> Path:
        # .env 里写的是相对路径，解析成绝对路径再往下传：
        # 否则换个 cwd 启动，文件就落到别处去了。
        return v if v.is_absolute() else (BASE_DIR / v).resolve()

    @property
    def is_dev(self) -> bool:
        return self.ENV == "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
