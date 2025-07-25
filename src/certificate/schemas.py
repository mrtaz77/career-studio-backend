from typing import TypedDict

from pydantic import BaseModel
from starlette.datastructures import UploadFile


class CertificateOut(BaseModel):
    id: int
    title: str
    issuer: str
    issued_date: str
    link: str


class CertificateFormData(TypedDict):
    title: str
    issuer: str
    issued_date: str
    file: UploadFile
