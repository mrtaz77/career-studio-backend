from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from constants import origins, methods, headers

def add_cors_middleware(app: FastAPI) -> None:
  """Add CORS middleware to the FastAPI application."""
  app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
    max_age=2400
  )

def create_app() -> FastAPI:
  """Create and configure the FastAPI application."""	
  app = FastAPI(title="Career Studio API")
  add_cors_middleware(app)
  return app