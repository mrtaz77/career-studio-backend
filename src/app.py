from fastapi import FastAPI

def create_app() -> FastAPI:
  """Create and configure the FastAPI application."""	
  app = FastAPI(title="Career Studio API")
  return app