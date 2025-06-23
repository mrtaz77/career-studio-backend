from logging import getLogger

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.cv.constants import CV_AUTOSAVE_SUCCESS, CV_SAVE_FAILED
from src.cv.exceptions import (
    CVInvalidTypeException,
    CVNotFoundException,
    CVSaveException,
)
from src.cv.schemas import (
    CVAutoSaveRequest,
    CVCreateRequest,
    CVFullOut,
    CVOut,
    CVSaveRequest,
)
from src.cv.services import autosave_cv, create_new_cv, get_cv_details, save_cv_version

router = APIRouter(tags=["CV"], prefix="/cv")
logger = getLogger(__name__)


@router.post(
    "/autosave",
    summary="Autosave CV draft with full content",
    status_code=status.HTTP_200_OK,
)
async def autosave_endpoint(
    request: Request, payload: CVAutoSaveRequest
) -> dict[str, str]:
    try:
        uid = request.state.user.get("uid", "")
        await autosave_cv(uid, payload)
        return {"message": CV_AUTOSAVE_SUCCESS}
    except CVSaveException as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception:
        logger.exception("Unexpected error during CV autosave")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/save",
    summary="Manually save CV and create a version",
    response_model=CVOut,
    status_code=status.HTTP_200_OK,
)
async def save_endpoint(request: Request, payload: CVSaveRequest) -> CVOut:
    try:
        uid = request.state.user.get("uid", "")
        return await save_cv_version(uid, payload)
    except CVNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except CVSaveException as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception:
        logger.exception("Unexpected error during CV save")
        raise HTTPException(status_code=500, detail=CV_SAVE_FAILED)


@router.post("/create", summary="Create a new CV entry")
async def create_cv(request: Request, payload: CVCreateRequest) -> JSONResponse:
    try:
        uid = request.state.user.get("uid", "")
        cv_id = await create_new_cv(uid, payload.type)
        return JSONResponse(status_code=201, content={"cv_id": cv_id})
    except CVInvalidTypeException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception:
        logger.exception("CV creation failed")
        raise HTTPException(status_code=500, detail="Failed to create CV")


@router.get(
    "/{cv_id}",
    summary="Get full CV details for editing",
    response_model=CVFullOut,
    status_code=status.HTTP_200_OK,
)
async def get_cv_endpoint(request: Request, cv_id: int) -> CVFullOut:
    try:
        uid = request.state.user.get("uid", "")
        return await get_cv_details(uid, cv_id)
    except CVNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception:
        logger.exception("Failed to retrieve CV details")
        raise HTTPException(status_code=500, detail="Internal server error")
