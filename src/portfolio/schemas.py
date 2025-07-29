from datetime import datetime

from pydantic import BaseModel


class PortfolioCreateRequest(BaseModel):
    theme: str


class PortfolioOut(BaseModel):
    portfolio_id: int
    title: str
    theme: str
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    bio: str
