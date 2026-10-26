from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    VERIFY_TOKEN: str = ""
    IG_ACCESS_TOKEN: str = ""
    APP_SECRET: str = ""
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    SYSTEM_PROMPT: str = "You are a friendly, concise Instagram DM assistant."
    HISTORY_LIMIT: int = 10
    RATE_LIMIT_PER_MIN: int = 15


settings = Settings()
