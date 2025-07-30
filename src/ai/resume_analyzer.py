import json
import os
import re
import tempfile
from typing import TYPE_CHECKING, Any, Dict, Union

import google.generativeai as genai
from docx import Document

from src.ai.constants import GEMINI_RESUME_PROMPT
from src.config import settings

if TYPE_CHECKING:
    pass


class AIResumeAnalyzer:
    def __init__(self) -> None:
        self.google_api_key: str = settings.GOOGLE_API_KEY
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)  # type: ignore[attr-defined]

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        text: str = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_bytes)
            temp_path: str = temp_file.name
        try:
            import pdfplumber

            with pdfplumber.open(temp_path) as pdf:
                for page in pdf.pages:
                    page_text: Union[str, None] = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        return text.strip()

    def extract_text_from_docx(self, docx_file: Any) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(docx_file.getbuffer())
            temp_path: str = temp_file.name
        text: str = ""
        try:
            doc = Document(temp_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        return text.strip()

    def analyze_resume_with_gemini(self, resume_text: str) -> Dict[str, Any]:
        if not resume_text or not self.google_api_key:
            return {"error": "Resume text or Google API key missing."}
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # type: ignore[attr-defined]
            prompt: str = GEMINI_RESUME_PROMPT.format(resume_text=resume_text)
            response = model.generate_content(prompt)
            try:
                match = re.search(r"\{.*\}", response.text, re.DOTALL)
                if match:
                    result: Dict[str, Any] = json.loads(match.group(0))
                else:
                    result = {"analysis": response.text}
            except Exception:
                result = {"analysis": response.text}
        except Exception as e:
            result = {"error": f"Analysis failed: {str(e)}"}

        result["ats_score"] = self.compute_ats_score(resume_text)
        result["keyword_match_score"] = self.compute_keyword_match_score(resume_text)
        result["formatting_score"] = self.compute_formatting_score(resume_text)
        return result

    def compute_ats_score(self, resume_text: str) -> int:
        """
        Simple ATS score: checks for common ATS-friendly features.
        """
        keywords = ["experience", "education", "skills", "project", "certification"]
        score = 0
        for kw in keywords:
            if kw in resume_text.lower():
                score += 20
        # Check for simple formatting issues (no tables, no images)
        if "table" not in resume_text.lower() and "image" not in resume_text.lower():
            score += 10
        return min(score, 100)

    def compute_keyword_match_score(self, resume_text: str) -> int:
        """
        Simple keyword match score: counts presence of common job keywords.
        """
        job_keywords = [
            "python",
            "java",
            "sql",
            "leadership",
            "communication",
            "team",
            "analysis",
            "management",
            "cloud",
            "aws",
            "azure",
            "react",
            "node",
            "machine learning",
        ]
        found = sum(1 for kw in job_keywords if kw in resume_text.lower())
        score = int((found / len(job_keywords)) * 100)
        return min(score, 100)

    def compute_formatting_score(self, resume_text: str) -> int:
        """
        Simple formatting score: checks for bullet points, section headers, and reasonable length.
        """
        score = 0
        if "-" in resume_text or "*" in resume_text or "•" in resume_text:
            score += 30
        if "education" in resume_text.lower() and "experience" in resume_text.lower():
            score += 30
        lines = resume_text.splitlines()
        if 20 <= len(lines) <= 100:
            score += 40
        return min(score, 100)
