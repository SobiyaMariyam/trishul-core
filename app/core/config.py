try:
    # Pydantic v2
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        SECRET_KEY: str = Field(default="dev-secret-key")  # used to sign JWTs
        ALGORITHM: str = Field(default="HS256")
        LOCAL_DOMAIN: str = Field(default="lvh.me")

    settings = Settings()

except Exception:
    # Fallback if pydantic-settings isn't installed—keep tests running
    class _FallbackSettings:
        SECRET_KEY: str = "dev-secret-key"
        ALGORITHM: str = "HS256"
        LOCAL_DOMAIN: str = "lvh.me"

    settings = _FallbackSettings()
