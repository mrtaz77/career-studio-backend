from typing import List, Optional

from pydantic import BaseModel

# === Schemas ===


class JobListing(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    is_remote: bool
    tags: List[str]


class JobSearchFilters(BaseModel):
    keyword: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    tags: Optional[List[str]] = None


class JobSearchHistoryItem(BaseModel):
    query: str
    timestamp: str


class ApplicationRequest(BaseModel):
    job_id: int
    cv_id: int
    portfolio_id: Optional[int]
