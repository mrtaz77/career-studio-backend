import uvicorn

from src.app import create_app
from src.config import settings
from src.logger import setup_logging

app = create_app()

if __name__ == "__main__":
    setup_logging()
    uvicorn.run("src.server:app", host=settings.HOST, port=settings.PORT, reload=True)
