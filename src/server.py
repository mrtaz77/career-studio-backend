import uvicorn
from src.app import create_app
from src.config import settings

app = create_app()

if __name__ == "__main__":
  uvicorn.run("src.server:app", host=settings.HOST, port=settings.PORT, reload=True)