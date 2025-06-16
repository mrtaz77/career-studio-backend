from logging import getLogger
from typing import Dict, List, Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi import UploadFile as FastAPIUploadFile
from fastapi import status
from starlette.datastructures import FormData
from starlette.datastructures import UploadFile as StarletteUploadFile

from src.certificate.constants import (
    CERTIFICATION_ADDITION_SUCCESS,
    CERTIFICATION_FILE_MISSING,
    CERTIFICATION_METADATA_MISSING,
)
from src.certificate.exceptions import (
    CertificateNotFoundException,
    CertificateUploadException,
    CertificateValidationException,
)
from src.certificate.schemas import CertificateFormData, CertificateOut
from src.certificate.service import (
    delete_user_certificate,
    get_user_certificates,
    process_certificate_uploads,
    update_user_certificate,
)

router = APIRouter(tags=["Certificate"], prefix="/certificate")
logger = getLogger(__name__)


@router.post(
    "/add", summary="Batch upload certifications", status_code=status.HTTP_201_CREATED
)
async def add_certifications(request: Request) -> Dict[str, str]:
    try:
        form = await request.form()
        uid = request.state.user.get("uid", "")

        certs = extract_certification_metadata(form)
        await process_certificate_uploads(uid, certs)

        return {"message": CERTIFICATION_ADDITION_SUCCESS}

    except CertificateValidationException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except CertificateUploadException as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception:
        logger.exception("Unexpected error during certification upload")
        raise HTTPException(status_code=500, detail="Internal server error")


def extract_certification_metadata(form: FormData) -> List[CertificateFormData]:
    certs: List[CertificateFormData] = []
    index = 0

    while True:
        raw_title = form.get(f"title_{index}")
        raw_issuer = form.get(f"issuer_{index}")
        raw_issued_date = form.get(f"issued_date_{index}")
        file = form.get(f"file_{index}")

        if not any([raw_title, raw_issuer, raw_issued_date, file]):
            break

        if not all([raw_title, raw_issuer, raw_issued_date]):
            raise CertificateValidationException(CERTIFICATION_METADATA_MISSING)

        if not isinstance(file, StarletteUploadFile):
            raise CertificateValidationException(CERTIFICATION_FILE_MISSING)

        title = str(raw_title)
        issuer = str(raw_issuer)
        issued_date = str(raw_issued_date)

        certs.append(
            {
                "title": title,
                "issuer": issuer,
                "issued_date": issued_date,
                "file": file,
            }
        )

        index += 1

    if not certs:
        raise CertificateValidationException(CERTIFICATION_METADATA_MISSING)

    return certs


@router.get(
    "",
    summary="Get all certifications for the current user",
    response_model=List[CertificateOut],
    status_code=status.HTTP_200_OK,
)
async def list_certificates(request: Request) -> List[CertificateOut]:
    try:
        uid = request.state.user.get("uid", "")
        return await get_user_certificates(uid)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not retrieve certificates")


@router.patch(
    "/{certificate_id}",
    summary="Update certificate metadata and/or file",
    response_model=CertificateOut,
    status_code=status.HTTP_200_OK,
)
async def update_certificate(
    request: Request,
    certificate_id: int,
    title: Optional[str] = Form(None),
    issuer: Optional[str] = Form(None),
    issued_date: Optional[str] = Form(None),
    file: Optional[FastAPIUploadFile] = None,
) -> CertificateOut:
    try:
        uid = request.state.user.get("uid", "")
        return await update_user_certificate(
            uid,
            certificate_id,
            title=title,
            issuer=issuer,
            issued_date=issued_date,
            file=file,
        )
    except CertificateUploadException as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception:
        raise HTTPException(status_code=500, detail="Update failed")


@router.delete(
    "/{certificate_id}",
    summary="Delete a certificate",
    status_code=status.HTTP_200_OK,
)
async def delete_certificate(request: Request, certificate_id: int) -> Dict[str, str]:
    try:
        uid = request.state.user.get("uid", "")
        await delete_user_certificate(uid, certificate_id)
        return {"message": "Certificate deleted successfully"}
    except CertificateNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception:
        raise HTTPException(status_code=500, detail="Delete failed")
