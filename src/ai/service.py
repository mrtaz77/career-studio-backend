from datetime import datetime
from logging import getLogger

from fastapi import UploadFile
from fastapi.responses import JSONResponse
from groq import Groq

from src.ai.constants import (
    AI_USAGE_LIMIT,
    MODEL,
    REQUEST_LENGTH_LIMIT,
    SYSTEM_PROMPT,
    UPLOAD_USAGE_LIMIT,
)
from src.ai.exceptions import (
    RequestLengthExceeded,
    RequestLimitExceeded,
    UploadLimitExceeded,
)
from src.ai.resume_analyzer import AIResumeAnalyzer
from src.ai.schemas import ResumeAnalysisResponse
from src.config import settings
from src.database import get_db

logger = getLogger(__name__)

MAX_FILE_SIZE: int = 8 * 1024 * 1024  # 8MB


async def check_and_update_request_limit(user_id: str) -> None:
    async with get_db() as db:
        now: datetime = datetime.now()
        ai_request = await db.ai_request.find_first(where={"user_id": user_id})

        if not ai_request:
            # No entry, create and initialize for current month
            await db.ai_request.create(
                data={
                    "user_id": user_id,
                    "request_count": 1,
                    "init_request_at": now,
                    "last_request_at": now,
                }
            )
        else:
            init_month: int = ai_request.init_request_at.month
            init_year: int = ai_request.init_request_at.year
            now_month: int = now.month
            now_year: int = now.year

            if (init_year != now_year) or (init_month != now_month):
                # New month, reset count and update init_request_at
                await db.ai_request.update(
                    where={"id": ai_request.id},
                    data={
                        "request_count": 1,
                        "init_request_at": now,
                        "last_request_at": now,
                    },
                )
            elif ai_request.request_count >= AI_USAGE_LIMIT:
                # Same month, limit exceeded
                raise RequestLimitExceeded()
            else:
                # Same month, increment count
                await db.ai_request.update(
                    where={"id": ai_request.id},
                    data={
                        "request_count": ai_request.request_count + 1,
                        "last_request_at": now,
                    },
                )


async def check_and_update_upload_limit(user_id: str) -> None:
    async with get_db() as db:
        now: datetime = datetime.now()
        ai_request = await db.ai_request.find_first(where={"user_id": user_id})

        if not ai_request:
            # No entry, create and initialize for current month
            await db.ai_request.create(
                data={
                    "user_id": user_id,
                    "upload_count": 1,
                    "init_upload_at": now,
                    "last_upload_at": now,
                    "request_count": 0,
                    "init_request_at": now,
                    "last_request_at": now,
                }
            )
        else:
            init_month: int = ai_request.init_upload_at.month
            init_year: int = ai_request.init_upload_at.year
            now_month: int = now.month
            now_year: int = now.year

            if (init_year != now_year) or (init_month != now_month):
                # New month, reset upload count and update init_upload_at
                await db.ai_request.update(
                    where={"id": ai_request.id},
                    data={
                        "upload_count": 1,
                        "init_upload_at": now,
                        "last_upload_at": now,
                    },
                )
            elif ai_request.upload_count >= UPLOAD_USAGE_LIMIT:
                # Same month, upload limit exceeded
                raise UploadLimitExceeded()
            else:
                # Same month, increment upload count
                await db.ai_request.update(
                    where={"id": ai_request.id},
                    data={
                        "upload_count": ai_request.upload_count + 1,
                        "last_upload_at": now,
                    },
                )


async def optimize_text(user_id: str, description: str) -> str:
    if len(description) > REQUEST_LENGTH_LIMIT:
        raise RequestLengthExceeded()
    await check_and_update_request_limit(user_id)

    client: Groq = Groq(api_key=settings.GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": description},
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return completion.choices[0].message.content or ""


async def analyze_resume_file(user_id: str, file: UploadFile) -> JSONResponse:
    contents: bytes = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=413,
            content={
                "error": "Uploaded file is too large. Maximum allowed size is 8MB."
            },
        )
    try:
        await check_and_update_upload_limit(user_id)
        analyzer = AIResumeAnalyzer()
        resume_text: str = ""
        # Accept both application/pdf and application/octet-stream for PDF
        if file.content_type in ["application/pdf", "application/octet-stream"] or (
            file.filename is not None and file.filename.lower().endswith(".pdf")
        ):
            extracted = analyzer.extract_text_from_pdf(contents)
            resume_text = extracted if isinstance(extracted, str) else ""
        elif file.content_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ] or (file.filename is not None and file.filename.lower().endswith(".docx")):
            extracted = analyzer.extract_text_from_docx(file)
            resume_text = extracted if isinstance(extracted, str) else ""
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file type. Please upload PDF or DOCX."},
            )
        result = analyzer.analyze_resume_with_gemini(resume_text)
        # Map result to ResumeAnalysisResponse, including computed scores
        response = ResumeAnalysisResponse(
            overall_assessment=result.get("overall_assessment"),
            skills=result.get("skills"),
            missing_skills=result.get("missing_skills"),
            experience_summary=result.get("experience_summary"),
            education_summary=result.get("education_summary"),
            strengths=result.get("strengths"),
            weaknesses=result.get("weaknesses"),
            recommended_courses=result.get("recommendations"),
            resume_score=result.get("resume_score"),
            analysis=result.get("analysis"),
            ats_score=result.get("ats_score"),
            keyword_match_score=result.get("keyword_match_score"),
            formatting_score=result.get("formatting_score"),
        )
        return JSONResponse(status_code=200, content=response.model_dump())
    except UploadLimitExceeded as e:
        return JSONResponse(status_code=429, content={"error": e.message})
    except Exception as e:
        logger.error(f"Unexpected error during resume analysis: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
