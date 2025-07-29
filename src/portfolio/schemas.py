from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.cv.schemas import ExperienceIn, ProjectIn, PublicationIn, TechnicalSkillIn


class PortfolioCreateRequest(BaseModel):
    theme: str


class FeedbackIn(BaseModel):
    id: Optional[int] = None
    reviewer_id: Optional[str] = None
    reviewer_name: str
    rating: int
    comment: str
    created_at: datetime


class PortfolioListOut(BaseModel):
    portfolio_id: int
    title: str
    theme: str
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    bio: str


class PortfolioProjectIn(ProjectIn):
    thumbnail_url: Optional[str] = None


class PortfolioSaveContent(BaseModel):
    title: Optional[str] = None
    bio: Optional[str] = None
    experiences: List[ExperienceIn] = []
    projects: List[PortfolioProjectIn] = []
    publications: List[PublicationIn] = []
    technical_skills: List[TechnicalSkillIn] = []


class PortfolioSaveRequest(BaseModel):
    portfolio_id: int
    save_content: PortfolioSaveContent


class PortfolioFullOut(BaseModel):
    id: int
    theme: str
    title: str
    is_public: bool = False
    bio: str
    created_at: datetime
    updated_at: datetime
    published_url: Optional[str] = None
    published_at: Optional[datetime] = None
    experiences: List[ExperienceIn]
    publications: List[PublicationIn]
    technical_skills: List[TechnicalSkillIn]
    projects: List[PortfolioProjectIn]
    feedbacks: List[FeedbackIn]


class PortfolioOut(BaseModel):
    id: int
    title: str
    theme: str
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    bio: str
