from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # DATABASE_URL can override the component-based settings for hosted databases.
    database_url: str | None = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_USER", "POSTGRES_USER"),
    )
    database_password: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_PASSWORD", "POSTGRES_PASSWORD"),
    )
    database_name: str = Field(
        default="gigbridge",
        validation_alias=AliasChoices("DATABASE_NAME", "POSTGRES_DB"),
    )

    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: SecretStr | None = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    aws_s3_bucket: str = "gigbridge-media"
    aws_region: str = "ap-south-1"

    @property
    def sqlalchemy_database_url(self) -> URL | str:
        if self.database_url:
            return self.database_url

        password = (
            self.database_password.get_secret_value()
            if self.database_password is not None
            else None
        )
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.database_user,
            password=password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )


settings = Settings()
