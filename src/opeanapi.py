from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.auth.docs import auth_tags_metadata

all_tags_metadata = auth_tags_metadata


def inject_global_bearer_auth(app: FastAPI) -> None:
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
