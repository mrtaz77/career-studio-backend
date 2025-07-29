from logging import getLogger

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.ai.exceptions import RequestLengthExceeded, RequestLimitExceeded
from src.ai.schemas import OptimizaitonRequest
from src.ai.service import optimize_text

router = APIRouter(tags=["AI"], prefix="/ai")
logger = getLogger(__name__)


@router.post(
    "/optimize", summary="Optimize resume description section using AI", status_code=200
)
async def optimize_resume(
    request: Request, payload: OptimizaitonRequest
) -> JSONResponse:
    try:
        user_id = request.state.user.get("uid", "")
        optimized_text = await optimize_text(user_id, payload.description)
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
