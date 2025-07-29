from pydantic import BaseModel


class PortfolioCreateRequest(BaseModel):
    theme: str
