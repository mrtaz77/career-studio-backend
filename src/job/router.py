from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.job.schemas import (
    ApplicationRequest,
    JobListing,
    JobSearchFilters,
    JobSearchHistoryItem,
)

router = APIRouter(tags=["Job"], prefix="/jobs")
security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


# === Routes ===


@router.get(
    "/search",
    summary="Search for jobs",
    description="Performs a job search based on keyword, location, remote preference, and tags.",
    response_model=List[JobListing],
)
async def search_jobs(
    keyword: Optional[str] = Query(
        None, description="Search term to match job titles or descriptions"
    ),
    location: Optional[str] = Query(None, description="Preferred job location"),
    remote: Optional[bool] = Query(None, description="Filter for remote jobs only"),
    tags: Optional[List[str]] = Query(
        None, description="List of required skills or tags"
    ),
    n: Optional[int] = Query(
        None, description="Maximum number of job listings to return"
    ),
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> List[JobListing]:
    _filters = JobSearchFilters(
        keyword=keyword,
        location=location,
        remote=remote,
        tags=tags,
    )
    # Stubbed job search response
    return []


@router.get(
    "/{job_id}/similar",
    summary="Find similar jobs",
    description="Fetches a list of job postings similar to the one specified by job ID.",
    response_model=List[JobListing],
)
async def get_similar_jobs(
    job_id: int,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> List[JobListing]:
    return []


@router.get(
    "/history",
    summary="Get job search history",
    description="Returns the authenticated user's past job search queries and timestamps.",
    response_model=List[JobSearchHistoryItem],
)
async def get_search_history(
    n: Optional[int] = Query(
        None, description="Maximum number of history entries to return"
    ),
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> List[JobSearchHistoryItem]:
    return []


@router.get(
    "/suggested",
    summary="Get suggested jobs",
    description="Returns job recommendations based on user's profile and search history.",
    response_model=List[JobListing],
)
async def get_suggested_jobs(
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> List[JobListing]:
    return []


@router.post(
    "/apply",
    summary="One-click apply to a job",
    description="Submits an application for a job using the user's CV and optional portfolio.",
    status_code=status.HTTP_200_OK,
)
async def apply_to_job(
    data: ApplicationRequest,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    return {
        "message": f"Application to job {data.job_id} submitted with CV {data.cv_id}"
        + (f" and portfolio {data.portfolio_id}" if data.portfolio_id else "")
    }
