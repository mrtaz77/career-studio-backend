from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class SourceType(str, Enum):
    project = "project"
    publication = "publication"


# === Experience ===


class ExperienceIn(BaseModel):
    id: Optional[int] = None
    job_title: str
    position: str
    company: str
    company_url: str
    company_logo: str
    location: str
    employment_type: str
    location_type: str
    industry: str
    start_date: date
    end_date: date
    description: str


# === Technical Skill ===


class TechnicalSkillIn(BaseModel):
    id: Optional[int] = None
    name: str
    category: str


# === Project ===


class ProjectTechnologyIn(BaseModel):
    id: Optional[int] = None
    technology: str


class ResourceURLIn(BaseModel):
    id: Optional[int] = None
    label: str
    url: str
    source_type: SourceType


class ProjectIn(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    technologies: List[ProjectTechnologyIn]
    urls: List[ResourceURLIn]


# === Publication ===


class PublicationIn(BaseModel):
    id: Optional[int] = None
    title: str
    journal: str
    year: int
    urls: List[ResourceURLIn]


# === Save Content ===


class CVSaveContent(BaseModel):
    experiences: List[ExperienceIn]
    publications: List[PublicationIn]
    technical_skills: List[TechnicalSkillIn]
    projects: List[ProjectIn]


# === Main Request Schemas ===


class CVAutoSaveRequest(BaseModel):
    cv_id: int
    draft_data: CVSaveContent  # stored as JSON in Redis


class CVSaveRequest(BaseModel):
    cv_id: int
    pdf_url: Optional[str] = None
    content: CVSaveContent


# === Output Schema ===


class CVOut(BaseModel):
    id: int
    type: str
    is_draft: bool
    bookmark: bool
    pdf_url: Optional[str] = None
    latest_saved_version_id: Optional[int] = None
    version_number: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class CVCreateRequest(BaseModel):
    type: str


class CVFullOut(BaseModel):
    id: int
    type: str
    is_draft: bool
    bookmark: bool
    pdf_url: Optional[str] = None
    latest_saved_version_id: Optional[int] = None
    version_number: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    experiences: List[ExperienceIn]
    publications: List[PublicationIn]
    technical_skills: List[TechnicalSkillIn]
    projects: List[ProjectIn]


class CVGenerateRequest(CVAutoSaveRequest):
    force_regenerate: Optional[bool] = False
