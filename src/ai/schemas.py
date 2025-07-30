from typing import List, Optional

from pydantic import BaseModel


class OptimizaitonRequest(BaseModel):
    description: str


class ResumeAnalysisResponse(BaseModel):
    overall_assessment: Optional[str] = None
    skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommended_courses: Optional[List[str]] = None
    resume_score: Optional[int] = None
    analysis: Optional[str] = None
    ats_score: Optional[int] = None
    keyword_match_score: Optional[int] = None
    formatting_score: Optional[int] = None
