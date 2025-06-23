from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.portfolio.schemas import (
    Achievement,
    Experience,
    PortfolioFromCVRequest,
    Project,
    SocialLink,
)

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")
security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


# === Schemas ===


class PortfolioResponse(BaseModel):
    id: int
    slug: str
    cv_id: Optional[int]
    title: str
    summary: Optional[str]
    description: Optional[str]
    theme: Optional[str]
    published: bool
    last_saved_at: datetime


class PortfolioUpdateRequest(BaseModel):
    title: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    theme: Optional[str]
    published: Optional[bool]


class PortfolioEditResponse(BaseModel):
    title: str
    summary: Optional[str]
    theme: Optional[str]
    achievements: Optional[List[Achievement]]
    projects: Optional[List[Project]]
    experiences: Optional[List[Experience]]
    skills: Optional[List[str]]
    social_links: Optional[List[SocialLink]]
    last_saved_at: datetime


# === Routes ===


@router.post(
    "/{portfolio_id}/publish",
    summary="Publish an existing portfolio",
    description="Marks the portfolio as published and generates a public slug.",
    response_model=PortfolioResponse,
)
async def publish_existing_portfolio(
    portfolio_id: int, _creds: HTTPAuthorizationCredentials = Depends(security)
) -> PortfolioResponse:
    return PortfolioResponse(
        id=portfolio_id,
        slug=f"portfolio-{portfolio_id}",
        cv_id=None,
        title="Published Portfolio",
        summary="Ready to share",
        description="Public view enabled",
        theme="minimal",
        published=True,
        last_saved_at=datetime.now(timezone.utc),
    )


@router.post(
    "/from-cv",
    summary="Create portfolio from existing CV",
    description="Creates a portfolio using an existing CV ID.",
    response_model=PortfolioResponse,
)
async def create_portfolio_from_cv(
    data: PortfolioFromCVRequest,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> PortfolioResponse:
    return PortfolioResponse(
        id=101,
        slug="cvport123",
        cv_id=data.cv_id,
        title=data.title or "My CV Portfolio",
        summary=data.summary,
        description=None,
        theme=data.theme,
        published=False,
        last_saved_at=datetime.now(timezone.utc),
    )


@router.get(
    "/{slug}",
    summary="View a public portfolio",
    description="Returns public portfolio data viewable by anyone.",
    response_model=PortfolioResponse,
)
async def get_public_portfolio(slug: str) -> PortfolioResponse:
    return PortfolioResponse(
        id=1,
        slug=slug,
        cv_id=None,
        title="Public Portfolio",
        summary="Public summary",
        description="My awesome portfolio",
        theme="minimal",
        published=True,
        last_saved_at=datetime.now(timezone.utc),
    )


@router.get(
    "/me",
    summary="Get my portfolios",
    description="Returns all portfolios owned by the authenticated user.",
    response_model=List[PortfolioResponse],
)
async def get_my_portfolios(
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> List[PortfolioResponse]:
    return [
        PortfolioResponse(
            id=1,
            slug="abc123",
            cv_id=None,
            title="Full Stack Portfolio",
            summary="Built with FastAPI",
            description="All projects and experience",
            theme="minimal",
            published=True,
            last_saved_at=datetime.now(timezone.utc),
        )
    ]


@router.get(
    "/edit/{portfolio_id}",
    summary="Get portfolio content for editing",
    description="Returns all structured content of a portfolio to populate the editor.",
    response_model=PortfolioEditResponse,
)
async def get_portfolio_for_editing(
    portfolio_id: int, _creds: HTTPAuthorizationCredentials = Depends(security)
) -> PortfolioEditResponse:
    return PortfolioEditResponse(
        title="Editable Portfolio",
        summary="Open to changes",
        theme="minimal",
        achievements=[],
        projects=[],
        experiences=[],
        skills=["Python", "FastAPI"],
        social_links=[],
        last_saved_at=datetime.now(timezone.utc),
    )


@router.patch(
    "/{portfolio_id}/save",
    summary="Autosave portfolio content (partial update)",
    description="Partially updates portfolio content during autosave or quick edits.",
    response_model=PortfolioResponse,
)
async def autosave_portfolio(
    portfolio_id: int,
    data: PortfolioUpdateRequest,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> PortfolioResponse:
    return PortfolioResponse(
        id=portfolio_id,
        slug="abc123",
        cv_id=None,
        title=data.title or "Updated Title",
        summary=data.summary,
        description=data.description or "Updated description",
        theme=data.theme or "classic",
        published=data.published if data.published is not None else False,
        last_saved_at=datetime.now(timezone.utc),
    )


@router.delete(
    "/{portfolio_id}",
    summary="Delete a portfolio",
    description="Unpublishes and removes portfolio from public access.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_portfolio(
    portfolio_id: int, _creds: HTTPAuthorizationCredentials = Depends(security)
) -> None:
    return
