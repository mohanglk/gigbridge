from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://gigbridge:gigbridge@localhost:5432/gigbridge"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    aws_s3_bucket: str = "gigbridge-media"
    aws_region: str = "ap-south-1"

    class Config:
        env_file = ".env"


settings = Settings()
