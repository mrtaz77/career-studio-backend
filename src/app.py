from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from src.auth.router import router as auth_router
from src.constants import API_PREFIX, VERSION, headers, methods, origins
from src.cv.router import router as cv_router
from src.database import lifespan
from src.education.router import router as education_router
from src.job.router import router as job_router
from src.middlewares import FirebaseAuthMiddleware, LimitBodySizeMiddleware
from src.opeanapi import inject_global_bearer_auth
from src.portfolio.router import router as portfolio_router
from src.users.router import router as user_router


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
    """Add Gzip compression middleware."""
    app.add_middleware(GZipMiddleware, minimum_size=1000)


def configure_limit_body_size(app: FastAPI) -> None:
    """Add body size limit middleware."""
    app.add_middleware(LimitBodySizeMiddleware, max_bytes=1024 * 1024 * 10)  # 10MB


def configure_firebase_auth(app: FastAPI) -> None:
    """Add Firebase authentication middleware."""
    app.add_middleware(FirebaseAuthMiddleware)


def add_middlewares(app: FastAPI) -> None:
    """Attach all middlewares to the app."""
    configure_cors(app)
    configure_gzip(app)
    configure_limit_body_size(app)
    configure_firebase_auth(app)


def include_routers(app: FastAPI) -> None:
    """Include all routers in the app."""
    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(user_router, prefix=API_PREFIX)
    app.include_router(cv_router, prefix=API_PREFIX)
    app.include_router(portfolio_router, prefix=API_PREFIX)
    app.include_router(job_router, prefix=API_PREFIX)
    app.include_router(education_router, prefix=API_PREFIX)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Career Studio API",
        description="API documentation for Career Studio backend",
        version=VERSION,
        license_info={
            "name": "Apache 2.0",
            "url": "https://opensource.org/licenses/Apache-2.0",
        },
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        lifespan=lifespan,
    )
    add_middlewares(app)
    include_routers(app)
    inject_global_bearer_auth(app)
    return app
