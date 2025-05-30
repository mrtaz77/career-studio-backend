from datetime import date
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.cv.schemas import CVGenerationRequest, CVUpdateRequest

router = APIRouter(tags=["CV"], prefix="/cv")
security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


# ====================
# Response Schemas
# ====================


class CVResponse(BaseModel):
    id: int
    title: str
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "Academic CV",
                "message": "CV generated successfully",
            }
        }
    }


# ====================
# Routes
# ====================


@router.post(
    "/generate",
    summary="Generate a CV",
    description="Generates and stores a CV using user data and CV type (academic or industry).",
    response_model=CVResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_cv(
    payload: CVGenerationRequest,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> CVResponse:
    return CVResponse(
        id=1,
        title=f"{payload.cv_type.capitalize()} CV",
        message="CV generated successfully",
    )


@router.get(
    "/{cv_id}",
    summary="Get a CV by ID",
    description="Returns the full metadata of a specific CV by its ID.",
    response_model=CVResponse,
    responses={
        200: {"description": "CV found"},
        404: {"description": "CV not found"},
        401: {"description": "Unauthorized"},
    },
)
async def get_cv_by_id(
    cv_id: int,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> CVResponse:
    return CVResponse(
        id=cv_id,
        title="Example CV",
        message="CV fetched successfully",
    )


@router.get(
    "/{cv_id}/preview",
    summary="Preview generated CV",
    description="Returns the generated CV in PDF format for in-browser preview.",
    responses={
        200: {"content": {"application/pdf": {}}},
        404: {"description": "CV not found"},
    },
)
async def preview_cv(
    _cv_id: int,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> FileResponse:
    pdf_path = "generated_cvs/cv_preview.pdf"
    return FileResponse(path=pdf_path, media_type="application/pdf")


@router.get(
    "/{cv_id}/download",
    summary="Download generated CV",
    description="Triggers a file download of the generated CV as a PDF.",
    responses={
        200: {"content": {"application/pdf": {}}},
        404: {"description": "CV not found"},
    },
)
async def download_cv(
    _cv_id: int,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> FileResponse:
    pdf_path = "generated_cvs/cv_download.pdf"
    return FileResponse(
        path=pdf_path,
        filename="cv_download.pdf",
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="cv_download.pdf"'},
    )


@router.get(
    "/list",
    summary="List CVs with filters",
    description="Returns a filtered list of CVs by type, title, or creation date.",
    response_model=List[CVResponse],
)
async def list_cvs(
    _type: Literal["academic", "industry", "all"] = Query("all"),
    _title: Optional[str] = Query(None),
    _created_before: Optional[date] = Query(None),
    _created_after: Optional[date] = Query(None),
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> List[CVResponse]:
    return []


class BookmarkRequest(BaseModel):
    category: Literal["academic", "industry"]


@router.post(
    "/{cv_id}/bookmark",
    summary="Bookmark a CV",
    description="Bookmarks a CV under either 'academic' or 'industry' category.",
    responses={
        200: {"description": "Bookmark added"},
        409: {"description": "CV already bookmarked under this category"},
        404: {"description": "CV not found"},
        400: {"description": "Invalid input"},
    },
)
async def bookmark_cv(
    cv_id: int,
    data: BookmarkRequest,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    return {"message": f"Bookmarked CV {cv_id} under {data.category}"}


@router.get(
    "/bookmarks",
    summary="View bookmarked CVs",
    description="Returns bookmarked CVs by type, title, or creation date.",
    response_model=List[CVResponse],
)
async def view_bookmarks(
    _type: Literal["academic", "industry", "all"] = Query("all"),
    _title: Optional[str] = Query(None),
    _created_before: Optional[date] = Query(None),
    _created_after: Optional[date] = Query(None),
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> List[CVResponse]:
    return []


@router.delete(
    "/{cv_id}",
    summary="Delete a CV",
    description="Deletes a CV by ID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cv(
    cv_id: int,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    return


@router.patch(
    "/{cv_id}/save",
    summary="Autosave CV (partial update)",
    description="Used to autosave updates made to a CV without requiring full data.",
    response_model=CVResponse,
    responses={
        200: {"description": "CV autosaved successfully"},
        404: {"description": "CV not found"},
        400: {"description": "Invalid input"},
    },
)
async def autosave_cv(
    cv_id: int,
    data: CVUpdateRequest,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> CVResponse:
    return CVResponse(
        id=cv_id,
        title=data.full_name or "Autosaved CV",
        message="CV autosaved successfully",
    )


@router.put(
    "/{cv_id}/save",
    summary="Manually save CV (full update)",
    description="Fully updates the CV. Used when a user clicks 'Save' button to persist all fields.",
    response_model=CVResponse,
    responses={
        200: {"description": "CV successfully saved"},
        404: {"description": "CV not found"},
        400: {"description": "Invalid input"},
    },
)
async def save_cv(
    cv_id: int,
    data: CVGenerationRequest,
    _creds: HTTPAuthorizationCredentials = Depends(security),
) -> CVResponse:
    return CVResponse(
        id=cv_id,
        title=f"{data.cv_type.capitalize()} CV",
        message="CV successfully saved",
    )
