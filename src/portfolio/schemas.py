from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class Achievement(BaseModel):
    title: str
    description: Optional[str]
    date: Optional[str]


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    link: Optional[HttpUrl]


class Experience(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: Optional[str]
    description: Optional[str]


class SocialLink(BaseModel):
    platform: str
    url: HttpUrl


class PortfolioFromUserRequest(BaseModel):
    title: str
    summary: Optional[str]
    theme: Optional[str] = "minimal"

    achievements: Optional[List[Achievement]]
    projects: Optional[List[Project]]
    experiences: Optional[List[Experience]]
    skills: Optional[List[str]]
    social_links: Optional[List[SocialLink]]


class PortfolioFromCVRequest(BaseModel):
    cv_id: int
    title: Optional[str]
    theme: Optional[str] = "minimal"
    summary: Optional[str]
