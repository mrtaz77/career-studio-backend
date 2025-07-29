from logging import getLogger

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from src.portfolio.exceptions import PortfolioInvalidThemeException
from src.portfolio.schemas import PortfolioCreateRequest
from src.portfolio.service import create_new_portfolio

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")
security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")

logger = getLogger(__name__)


@router.post("/create", summary="Create a new portfolio", status_code=201)
async def create_portfolio(
    request: Request, payload: PortfolioCreateRequest
) -> JSONResponse:
    try:
        uid = request.state.user.get("uid", "")
        portfolio_id = await create_new_portfolio(uid, payload.theme)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Portfolio created successfully",
                "portfolio_id": portfolio_id,
            },
        )
    except PortfolioInvalidThemeException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
