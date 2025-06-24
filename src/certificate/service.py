import os
from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional
from uuid import uuid4

from starlette.datastructures import UploadFile
from supabase import Client

from src.certificate.exceptions import (
    CertificateNotFoundException,
    CertificateUploadException,
)
from src.certificate.schemas import CertificateFormData, CertificateOut
from src.database import get_db, get_supabase
from src.prisma_client import Prisma

logger = getLogger(__name__)

STORAGE_BUCKET = "certificates"
MAX_FILE_SIZE_MB = 5


def generate_signed_url(
    supabase: Client, path: str, storage_bucket: str, expires: int = 3600
) -> str:
    result = supabase.storage.from_(storage_bucket).create_signed_url(
        path, expires_in=expires
    )
    signed_url = result.get("signedURL") or ""
    if not signed_url:
        raise CertificateUploadException("Failed to generate signed URL.")
    return signed_url


async def upload_file_to_supabase(
    supabase: Client, uid: str, file: UploadFile, storage_bucket: str
) -> str:
    filename = file.filename or ""
    contents = await file.read()
    validate_file(filename, contents)
    ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uid}/{uuid4()}{ext}"

    try:
        supabase.storage.from_(storage_bucket).upload(
            unique_filename, contents, {"content-type": "application/pdf"}
        )
    except Exception:
        raise CertificateUploadException()

    return unique_filename


async def get_certificate_or_404(db: Prisma, uid: str, cert_id: int) -> CertificateOut:
    cert = await db.certification.find_unique(where={"id": cert_id})
    if not cert or cert.user_id != uid:
        raise CertificateNotFoundException()
    return CertificateOut(
        id=cert.id,
        title=cert.title,
        issuer=cert.issuer,
        issued_date=cert.issued_date,
        link=cert.link,
    )


def validate_file(filename: str, contents: bytes) -> None:
    ext = os.path.splitext(filename)[1].lower()
    print(ext)
    if ext != ".pdf":
        raise CertificateUploadException("Only PDF files are supported.")
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise CertificateUploadException("File size exceeds 5MB limit.")


async def process_certificate_uploads(
    uid: str, certs: list[CertificateFormData]
) -> None:
    async with get_db() as db, get_supabase() as supabase:
        for cert in certs:

            cert_file = cert["file"]

            path = await upload_file_to_supabase(
                supabase, uid, cert_file, STORAGE_BUCKET
            )

            await db.certification.create(
                data={
                    "user_id": uid,
                    "title": cert["title"],
                    "issuer": cert["issuer"],
                    "issued_date": datetime.fromisoformat(cert["issued_date"]),
                    "link": path,
                }
            )


async def get_user_certificates(uid: str) -> List[CertificateOut]:
    async with get_db() as db, get_supabase() as supabase:
        certs = await db.certification.find_many(where={"user_id": uid})
        return [
            CertificateOut(
                id=cert.id,
                title=cert.title,
                issuer=cert.issuer,
                issued_date=cert.issued_date,
                link=generate_signed_url(supabase, cert.link, STORAGE_BUCKET),
            )
            for cert in certs
        ]


async def update_user_certificate(
    uid: str,
    cert_id: int,
    title: Optional[str],
    issuer: Optional[str],
    issued_date: Optional[str],
    file: Optional[UploadFile],
) -> CertificateOut:
    async with get_db() as db, get_supabase() as supabase:
        await get_certificate_or_404(db, uid, cert_id)

        update_data: Dict[str, object] = {}

        if title:
            update_data["title"] = title
        if issuer:
            update_data["issuer"] = issuer
        if issued_date:
            try:
                update_data["issued_date"] = datetime.fromisoformat(issued_date).date()
            except Exception:
                raise CertificateUploadException(
                    "Invalid issued_date format. Use YYYY-MM-DD."
                )

        if file:
            update_data["link"] = await upload_file_to_supabase(
                supabase, uid, file, STORAGE_BUCKET
            )

        updated = await db.certification.update(where={"id": cert_id}, data=update_data)

        return CertificateOut(
            id=updated.id,
            title=updated.title,
            issuer=updated.issuer,
            issued_date=updated.issued_date,
            link=generate_signed_url(supabase, updated.link, STORAGE_BUCKET),
        )


async def delete_user_certificate(uid: str, cert_id: int) -> None:
    async with get_db() as db:
        await get_certificate_or_404(db, uid, cert_id)
        await db.certification.delete(where={"id": cert_id})
