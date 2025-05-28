from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }

    ENVIRONMENT: str = Field(default="development")
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8000)
    FRONTEND_URL: str = Field(default="your_frontend_url")
    REDIS_PORT: int = Field(default=6379)


settings = Settings()
