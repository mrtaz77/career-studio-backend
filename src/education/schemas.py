from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EducationBase(BaseModel):
    degree: str
    institution: str
    location: str
    start_date: datetime
    end_date: datetime
    gpa: float
    honors: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None
    honors: Optional[str] = None


class EducationOut(EducationBase):
    id: int
