from src.config import settings

origins = [settings.FRONTEND_URL]

methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

headers = [
    "Authorization",
    "Content-Type",
    "X-Requested-With",
]

VERSION = "1.0.0"

API_PREFIX = "/api/v1"
