from uuid import uuid4

from src.database import get_db
from src.portfolio.exceptions import PortfolioInvalidThemeException


async def create_new_portfolio(uid: str, theme: str) -> int:
    if theme not in ["default", "modern", "classic"]:
        raise PortfolioInvalidThemeException()

    async with get_db() as db:
        new_portfolio = await db.portfolio.create(
            data={
                "user_id": uid,
                "theme": theme,
                "title": f"Portfolio-{uuid4().hex[:8]}-{theme}",
            }
        )
        return int(new_portfolio.id)
