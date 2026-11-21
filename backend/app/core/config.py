from pathlib import Path
import ipaddress
from urllib.parse import urlsplit

from typing import Literal

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
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
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_issuer: str = "gigbridge-api"
    jwt_audience: str = "gigbridge-clients"
    access_token_expire_minutes: int = Field(default=15, gt=0, le=60)
    refresh_token_expire_days: int = Field(default=30, gt=0, le=90)
    app_environment: Literal["development", "test", "production"] = "development"
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    auth_cookie_samesite: Literal["lax", "strict"] = "lax"
    trusted_proxy_ips: list[str] = Field(default_factory=list)
    auth_rate_limit_hmac_secret: SecretStr | None = None
    auth_register_ip_limit: int = Field(default=10, gt=0)
    auth_register_ip_window_seconds: int = Field(default=3600, gt=0)
    auth_register_account_limit: int = Field(default=3, gt=0)
    auth_register_account_window_seconds: int = Field(default=3600, gt=0)
    auth_login_ip_limit: int = Field(default=20, gt=0)
    auth_login_ip_window_seconds: int = Field(default=900, gt=0)
    auth_login_account_limit: int = Field(default=10, gt=0)
    auth_login_account_window_seconds: int = Field(default=900, gt=0)
    aws_s3_bucket: str = "gigbridge-media"
    aws_region: str = "ap-south-1"

    @field_validator("cors_allowed_origins")
    @classmethod
    def validate_cors_allowed_origins(cls, origins: list[str]) -> list[str]:
        if not origins:
            raise ValueError("At least one explicit CORS origin is required.")

        normalized_origins: list[str] = []
        for origin in origins:
            normalized = origin.strip().rstrip("/")
            parsed = urlsplit(normalized)
            if (
                not normalized
                or "*" in normalized
                or parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("CORS origins must be explicit HTTP(S) origins without paths or wildcards.")
            normalized_origins.append(normalized)
        return normalized_origins

    @field_validator("trusted_proxy_ips")
    @classmethod
    def validate_trusted_proxy_ips(cls, proxies: list[str]) -> list[str]:
        for proxy in proxies:
            try:
                ipaddress.ip_network(proxy, strict=False)
            except ValueError as exc:
                raise ValueError("TRUSTED_PROXY_IPS must contain valid IPs or CIDRs.") from exc
        return proxies

    @model_validator(mode="after")
    def validate_production_auth_settings(self) -> "Settings":
        if self.app_environment == "production":
            if any(urlsplit(origin).scheme != "https" for origin in self.cors_allowed_origins):
                raise ValueError("Production CORS origins must all use HTTPS.")
            if self.auth_cookie_samesite not in {"lax", "strict"}:
                raise ValueError("Production auth cookies require SameSite=Lax or Strict.")
        return self

    @property
    def secure_auth_cookies(self) -> bool:
        return self.app_environment == "production"

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
