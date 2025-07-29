from logging import getLogger

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.portfolio.exceptions import PortfolioInvalidThemeException
from src.portfolio.schemas import PortfolioCreateRequest, PortfolioOut
from src.portfolio.service import create_new_portfolio, list_of_portfolios

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")
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


@router.get(
    "/list",
    summary="List all portfolios for a user",
    status_code=200,
    response_model=list[PortfolioOut],
)
async def list_portfolios(request: Request) -> list[PortfolioOut]:
    uid = request.state.user.get("uid", "")
    return await list_of_portfolios(uid)
