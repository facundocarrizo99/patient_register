from functools import lru_cache

from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    env: str = "development"
    database_url: AnyUrl | str
    mailtrap_user: str = "your_mailtrap_user"
    mailtrap_pass: str = "your_mailtrap_pass"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

