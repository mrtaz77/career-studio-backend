from logging import getLogger
from uuid import uuid4

from src.database import get_db
from src.portfolio.exceptions import PortfolioInvalidThemeException
from src.portfolio.schemas import PortfolioOut

logger = getLogger(__name__)


async def create_new_portfolio(uid: str, theme: str) -> int:
    if theme not in ["modern", "classic"]:
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


async def list_of_portfolios(uid: str) -> list[PortfolioOut]:
    async with get_db() as db:
        portfolios = await db.portfolio.find_many(
            where={"user_id": uid},
            order={"updated_at": "desc"},
        )
        return [
            PortfolioOut(
                portfolio_id=portfolio.id,
                title=portfolio.title,
                theme=portfolio.theme,
                created_at=portfolio.created_at,
                updated_at=portfolio.updated_at,
                is_public=portfolio.is_public,
                bio=portfolio.bio or "",
            )
            for portfolio in portfolios
        ]
