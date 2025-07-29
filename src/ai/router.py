from logging import getLogger

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse

from src.ai.exceptions import (
    RequestLengthExceeded,
    RequestLimitExceeded,
    UploadLimitExceeded,
)
from src.ai.schemas import OptimizaitonRequest, ResumeAnalysisResponse
from src.ai.service import analyze_resume_file, optimize_text

router = APIRouter(tags=["AI"], prefix="/ai")
logger = getLogger(__name__)


@router.post(
    "/optimize", summary="Optimize resume description section using AI", status_code=200
)
async def optimize_resume(
    request: Request, payload: OptimizaitonRequest
) -> JSONResponse:
    try:
        user_id: str = request.state.user.get("uid", "")
        optimized_text: str = await optimize_text(user_id, payload.description)
        return JSONResponse(status_code=200, content={"optimized_text": optimized_text})
    except RequestLimitExceeded as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.message})
    except RequestLengthExceeded as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.message})
    except Exception as e:
        logger.error(f"Unexpected error during resume optimization: {e}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


@router.post(
    "/analyze",
    summary="Analyze resume PDF or DOCX using AI",
    response_model=ResumeAnalysisResponse,
    status_code=200,
)
async def analyze_resume(
    request: Request, file: UploadFile = File(...)
) -> JSONResponse:
    user_id = request.state.user.get("uid", "")
    try:
        result = await analyze_resume_file(user_id, file)
        return result
    except UploadLimitExceeded as e:
        return JSONResponse(status_code=429, content={"error": e.message})
    except RequestLimitExceeded as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.message})
    except RequestLengthExceeded as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.message})
    except Exception as e:
        logger.error(f"Unexpected error during resume analysis: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
