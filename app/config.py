from functools import cached_property
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 직접 넣으면 이 값이 우선. 비밀번호에 @ 등이 있으면 URL 인코딩 필수.
    database_url: str | None = None

    postgres_user: str = "qrious"
    postgres_password: str = "qrious"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "qrious"

    @cached_property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg2://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
