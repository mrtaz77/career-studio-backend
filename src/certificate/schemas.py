from datetime import date
from typing import TypedDict

from fastapi import UploadFile
from pydantic import BaseModel


class CertificateOut(BaseModel):
    id: int
    title: str
    issuer: str
    issued_date: date
    link: str


class CertificateFormData(TypedDict):
    title: str
    issuer: str
    issued_date: str
    file: UploadFile
