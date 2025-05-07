import uvicorn
from app import create_app
from config import settings

app = create_app()

if __name__ == "__main__":
  uvicorn.run("server:app", host=settings.HOST, port=settings.PORT, reload=True)