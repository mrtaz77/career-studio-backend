from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")
    HOST: str = Field(default="127.0.0.1", validation_alias="HOST")
    PORT: int = Field(default=8000, validation_alias="PORT")

    FRONTEND_URL: str = Field(..., validation_alias="FRONTEND_URL")


settings = Settings()
