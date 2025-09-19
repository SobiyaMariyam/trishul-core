from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

load_dotenv()

class Settings(BaseSettings):
    # required/used by your app
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # optional extras (present in your .env) -> won’t break if unused
    ACCESS_TOKEN_EXPIRE_MINUTES: int | None = None
    JWT_AUDIENCE: str | None = None
    ALLOWED_ORIGINS: str | None = None
    JWT_SECRET: str | None = None  # legacy support

    # accept unknown env vars to avoid crashes
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

def _coalesce_secret() -> str:
    # Prefer SECRET_KEY, else fall back to JWT_SECRET
    s = os.getenv("SECRET_KEY")
    if s:
        return s
    legacy = os.getenv("JWT_SECRET")
    if legacy:
        return legacy
    raise RuntimeError("SECRET_KEY (or JWT_SECRET) is required")

# Instantiate, but coerce SECRET_KEY if only JWT_SECRET exists
tmp = Settings()
if not os.getenv("SECRET_KEY") and tmp.JWT_SECRET:
    # reconstruct with SECRET_KEY taken from JWT_SECRET
    os.environ["SECRET_KEY"] = tmp.JWT_SECRET
    tmp = Settings()

settings = tmp
