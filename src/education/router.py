from logging import getLogger
from typing import Dict, List

from fastapi import APIRouter, Body, HTTPException, Request, status

from src.education.exceptions import EducationNotFoundException
from src.education.schemas import EducationCreate, EducationOut, EducationUpdate
from src.education.service import (
    add_education,
    delete_education,
    get_user_education,
    update_education,
)

logger = getLogger(__name__)
router = APIRouter(tags=["Education"], prefix="/education")


@router.get(
    "",
    summary="Get all education entries",
    response_model=List[EducationOut],
)
async def list_education(request: Request) -> List[EducationOut]:
    try:
        uid = request.state.user.get("uid", "")
        return await get_user_education(uid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/add",
    summary="Add education entries",
    status_code=status.HTTP_201_CREATED,
)
async def add_education_entries(
    request: Request,
    data: List[EducationCreate] = Body(...),
) -> Dict[str, str]:
    try:
        uid = request.state.user.get("uid", "")
        success = await add_education(uid, data)
        if success:
            return {"message": "Education added"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add education",
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete(
    "/{education_id}",
    summary="Delete an education entry",
    status_code=status.HTTP_200_OK,
)
async def delete_education_entry(request: Request, education_id: int) -> Dict[str, str]:
    try:
        uid = request.state.user.get("uid", "")
        success = await delete_education(uid, education_id)
        if success:
            return {"message": "Education entry deleted"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete education",
            )
    except EducationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.patch(
    "/{education_id}",
    summary="Update an education entry",
    response_model=EducationOut,
)
async def patch_education_entry(
    request: Request,
    education_id: int,
    data: EducationUpdate = Body(...),
) -> EducationOut:
    try:
        uid = request.state.user.get("uid", "")
        return await update_education(uid, education_id, data)
    except EducationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
