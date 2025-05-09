from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, HttpUrl

# === Reusable Sub-sections ===


class Link(BaseModel):
    label: str
    url: HttpUrl


class EducationEntry(BaseModel):
    degree: str
    institution: str
    location: Optional[str]
    start_year: int
    end_year: Optional[int]
    gpa: Optional[float]
    honors: Optional[str]


class ExperienceEntry(BaseModel):
    job_title: str
    company: str
    location: Optional[str]
    start_date: str  # Format: "Jan 2020"
    end_date: Optional[str]
    responsibilities: List[str]


class ProjectEntry(BaseModel):
    name: str
    description: str
    technologies: List[str]
    link: Optional[HttpUrl]


class CertificationEntry(BaseModel):
    title: str
    issuer: str
    date: str


class PublicationEntry(BaseModel):
    title: str
    authors: List[str]
    journal: str
    year: int
    link: Optional[HttpUrl]


# === Main Request Schema ===


class CVGenerationRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str]
    address: Optional[str]
    links: Optional[List[Link]]

    summary: Optional[str]

    education: List[EducationEntry]
    experience: List[ExperienceEntry]
    projects: Optional[List[ProjectEntry]]
    skills: List[str]
    certifications: Optional[List[CertificationEntry]]
    publications: Optional[List[PublicationEntry]]

    cv_type: Literal["academic", "industry"]
    tone: Optional[Literal["formal", "concise", "creative"]]
    language: Optional[str]  # e.g., "en", "de"


class CVUpdateRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    address: Optional[str]
    links: Optional[List[Link]]

    summary: Optional[str]

    education: Optional[List[EducationEntry]]
    experience: Optional[List[ExperienceEntry]]
    projects: Optional[List[ProjectEntry]]
    skills: Optional[List[str]]
    certifications: Optional[List[CertificationEntry]]
    publications: Optional[List[PublicationEntry]]

    cv_type: Optional[Literal["academic", "industry"]]
    tone: Optional[Literal["formal", "concise", "creative"]]
    language: Optional[str]
