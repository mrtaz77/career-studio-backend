from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  # Default environment
  ENVIRONMENT: str = "development"
  HOST: str = "127.0.0.1"
  PORT: int = 8000

  class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    extra = "allow"

settings = Settings()
