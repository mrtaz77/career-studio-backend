from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.ai.docs import ai_tags_metadata
from src.auth.docs import auth_tags_metadata
from src.certificate.docs import certification_tags_metadata
from src.cv.docs import cv_tags_metadata
from src.education.docs import education_tags_metadata
from src.portfolio.docs import portfolio_tags_metadata
from src.users.docs import user_tags_metadata

all_tags_metadata = (
    auth_tags_metadata
    + user_tags_metadata
    + cv_tags_metadata
    + portfolio_tags_metadata
    + education_tags_metadata
    + certification_tags_metadata
    + portfolio_tags_metadata
    + ai_tags_metadata
)


def inject_global_bearer_auth(app: FastAPI) -> None:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            license_info=app.license_info,
            routes=app.routes,
            tags=all_tags_metadata,
        )

        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter your Firebase token like: **Bearer &lt;token&gt;**",
            }
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    object.__setattr__(app, "openapi", custom_openapi)  # ✅ bypass mypy restriction
