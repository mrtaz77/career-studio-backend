from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
  # Default environment
  ENVIRONMENT: str = "development"
  HOST: str = "127.0.0.1"
  PORT: int = 8000
  
  FRONTEND_URL: str = Field(..., env="FRONTEND_URL")

  class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    extra = "allow"

settings = Settings()
