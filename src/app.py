from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from middlewares import LimitBodySizeMiddleware
from constants import origins, methods, headers

def configure_cors(app: FastAPI) -> None:
    """Add CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=methods,
        allow_headers=headers,
        max_age=2400,
    )

def configure_gzip(app: FastAPI) -> None:
    """Add GZip compression middleware."""
    app.add_middleware(GZipMiddleware, minimum_size=1000)

def configure_limit_body_size(app: FastAPI) -> None:
    """Add middleware to limit request body size."""
    app.add_middleware(LimitBodySizeMiddleware, max_bytes=1024 * 1024 * 10)  # 10 MB

def add_middlewares(app: FastAPI) -> None:
    """Attach all middlewares to the app."""
    configure_cors(app)
    configure_gzip(app)
    configure_limit_body_size(app)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Career Studio API")
    add_middlewares(app)
    return app
