import os
from datetime import date, datetime
from logging import getLogger
from typing import Dict, List, Optional, Union
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

# Date validation messages
DATE_FUTURE_ERROR = "Certificate issue date cannot be in the future."
DATE_FORMAT_ERROR = "Invalid issued_date format. Use YYYY-MM-DD."
DATE_RANGE_ERROR = "Certificate issue date must be from 1900 onwards."


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
        issued_date=format_date_for_output(cert.issued_date),
        link=cert.link,
    )


def validate_file(filename: str, contents: bytes) -> None:
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".pdf":
        raise CertificateUploadException("Only PDF files are supported.")
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise CertificateUploadException("File size exceeds 5MB limit.")


def validate_and_format_date(date_str: str) -> str:
    """
    Validate and format a date string for certificate issued_date.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        ISO datetime string formatted for database storage

    Raises:
        CertificateUploadException: If date format is invalid or date is in future
    """
    try:
        parsed_date = date.fromisoformat(date_str)

        # Validate date is not in the future (allow today)
        if parsed_date > date.today():
            raise CertificateUploadException(DATE_FUTURE_ERROR)

        # Validate date is reasonable (not too far in the past)
        # Allow certificates from 1900 onwards
        if parsed_date.year < 1900:
            raise CertificateUploadException(DATE_RANGE_ERROR)

        return f"{date_str}T00:00:00.000Z"

    except ValueError:
        raise CertificateUploadException(DATE_FORMAT_ERROR)


async def process_certificate_uploads(
    uid: str, certs: List[CertificateFormData]
) -> None:
    async with get_db() as db, get_supabase() as supabase:
        for cert in certs:
            # 1) Validate and format date
            full_dt = validate_and_format_date(cert["issued_date"])

            # 2) Upload file
            path = await upload_file_to_supabase(
                supabase, uid, cert["file"], STORAGE_BUCKET
            )

            # 3) Create record
            await db.certification.create(
                data={
                    "user_id": uid,
                    "title": cert["title"],
                    "issuer": cert["issuer"],
                    "issued_date": full_dt,  # ISO-8601 DateTime string
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
                issued_date=format_date_for_output(cert.issued_date),
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
        cert = await get_certificate_or_404(db, uid, cert_id)

        update_data: Dict[str, object] = {}

        if title is not None:
            update_data["title"] = title

        if issuer is not None:
            update_data["issuer"] = issuer

        if issued_date:
            iso_dt = validate_and_format_date(issued_date)
            update_data["issued_date"] = iso_dt

        if file:
            supabase.storage.from_(STORAGE_BUCKET).remove([cert.link])
            update_data["link"] = await upload_file_to_supabase(
                supabase, uid, file, STORAGE_BUCKET
            )

        if not update_data:
            raise CertificateUploadException("No fields provided to update")

        updated = await db.certification.update(where={"id": cert_id}, data=update_data)

        return CertificateOut(
            id=updated.id,
            title=updated.title,
            issuer=updated.issuer,
            issued_date=format_date_for_output(updated.issued_date),
            link=generate_signed_url(supabase, updated.link, STORAGE_BUCKET),
        )


async def delete_user_certificate(uid: str, cert_id: int) -> None:
    async with get_db() as db, get_supabase() as supabase:
        cert = await get_certificate_or_404(db, uid, cert_id)
        supabase.storage.from_(STORAGE_BUCKET).remove([cert.link])
        await db.certification.delete(where={"id": cert_id})


def format_date_for_output(dt_obj: Union[datetime, date, str]) -> str:
    """
    Format a datetime object to a consistent date string for API output.

    Args:
        dt_obj: DateTime object from the database (can be datetime, date, or string)

    Returns:
        Date string in YYYY-MM-DD format

    Raises:
        CertificateUploadException: If the date cannot be formatted
    """
    try:
        if dt_obj is None:
            raise CertificateUploadException("Date value cannot be None")

        if hasattr(dt_obj, "date"):
            # If it's a datetime object, extract just the date part
            return str(dt_obj.date().isoformat())
        elif hasattr(dt_obj, "isoformat"):
            # If it's a date object
            return str(dt_obj.isoformat())
        else:
            # If it's already a string, try to parse and reformat for consistency
            dt_str = str(dt_obj).strip()
            if not dt_str:
                raise CertificateUploadException("Date value cannot be empty")

            if "T" in dt_str:
                # Extract date part from ISO datetime string
                date_part = dt_str.split("T")[0]
                # Validate it's a proper date format
                date.fromisoformat(date_part)
                return date_part
            else:
                # Assume it's already in YYYY-MM-DD format, validate it
                date.fromisoformat(dt_str)
                return dt_str

    except (ValueError, AttributeError) as e:
        raise CertificateUploadException(f"Invalid date format: {dt_obj}") from e
