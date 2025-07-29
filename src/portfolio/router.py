from logging import getLogger

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from src.portfolio.exceptions import (
    PortfolioInvalidThemeException,
    PortfolioNotFoundException,
)
from src.portfolio.schemas import (
    PortfolioCreateRequest,
    PortfolioFullOut,
    PortfolioListOut,
    PortfolioOut,
)
from src.portfolio.service import (
    create_new_portfolio,
    get_portfolio_details,
    list_of_portfolios,
    update_portfolio,
)

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
    response_model=list[PortfolioListOut],
)
async def list_portfolios(request: Request) -> list[PortfolioListOut]:
    uid = request.state.user.get("uid", "")
    return await list_of_portfolios(uid)


@router.get(
    "/{portfolio_id}",
    summary="Get full portfolio details for editing",
    response_model=PortfolioFullOut,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_detail(request: Request, portfolio_id: int) -> PortfolioFullOut:
    try:
        uid = request.state.user.get("uid", "")
        return await get_portfolio_details(uid, portfolio_id)
    except PortfolioNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to retrieve portfolio details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch(
    "/update",
    summary="Update portfolio content (with images)",
    response_model=PortfolioOut,
    status_code=status.HTTP_200_OK,
)
async def update_portfolio_endpoint(
    request: Request,
    portfolio_id: int = Form(...),
    title: str = Form(None),
    bio: str = Form(None),
    experiences: str = Form(...),  # JSON string
    projects: str = Form(...),  # JSON string
    publications: str = Form(...),  # JSON string
    technical_skills: str = Form(...),  # JSON string
    project_thumbnails: list[UploadFile] = File([]),
    company_logos: list[UploadFile] = File([]),
) -> PortfolioOut:
    """
    Accepts multipart/form-data for portfolio update.
    - experiences, projects, publications, technical_skills: JSON strings
    - project_thumbnails: list of image files (order matches projects)
    - company_logos: list of image files (order matches experiences)
    """
    try:
        uid = request.state.user.get("uid", "")
        return await update_portfolio(
            uid=uid,
            portfolio_id=portfolio_id,
            title=title,
            bio=bio,
            experiences_json=experiences,
            projects_json=projects,
            publications_json=publications,
            technical_skills_json=technical_skills,
            project_thumbnails=project_thumbnails,
            company_logos=company_logos,
        )
    except PortfolioNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to update portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to update portfolio")
