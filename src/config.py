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
    REDIS_HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8000)
    FRONTEND_URL: str = Field(default="your_frontend_url")
    REDIS_PORT: int = Field(default=6379)
    SUPABASE_PROJECT_URL: str = Field(default="your_supabase_project_url")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="your_supabase_service_role_key")
    GROQ_API_KEY: str = Field(default="your_groq_api_key")
    GOOGLE_API_KEY: str = Field(default="your_google_api_key")
    OPENROUTER_API_KEY: str = Field(default="your_openrouter_api_key")


settings = Settings()
