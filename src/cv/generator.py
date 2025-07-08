import os
from datetime import datetime
from logging import getLogger

import requests
from jinja2 import Environment, FileSystemLoader

from src.certificate.schemas import CertificateOut
from src.cv.schemas import ExperienceIn, ProjectIn, PublicationIn, TechnicalSkillIn
from src.education.schemas import EducationOut
from src.users.schemas import UserProfile

TEMPLATE_DIR = "src/cv/templates"
TEMPLATE_TEX_FILE = "template.tex"
TEMPLATE_HTML_FILE = "template.html"
LATEX_API_URL = "https://latex.ytotech.com/builds/sync"

logger = getLogger(__name__)


def format_date(value: str, fmt: str = "%b %Y") -> str:
    """Formats a date string into the specified format."""
    return datetime.fromisoformat(value).strftime(fmt)


def create_jinja_environment(template: int) -> Environment:
    """Creates and configures a Jinja2 environment."""
    env = Environment(
        loader=FileSystemLoader(os.path.join(TEMPLATE_DIR, str(template))),
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="(((",
        variable_end_string=")))",
        comment_start_string="((#",
        comment_end_string="#))",
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["format_date"] = format_date
    return env


def render_template(
    template_file: str,
    user: UserProfile,
    educations: list[EducationOut],
    experiences: list[ExperienceIn],
    projects: list[ProjectIn],
    technical_skills: list[TechnicalSkillIn],
    publications: list[PublicationIn],
    certificates: list[CertificateOut],
    template: int,
) -> str:
    """Renders a template with the provided data."""
    env = create_jinja_environment(template)
    tpl = env.get_template(template_file)
    return tpl.render(
        user=user,
        educations=educations,
        experiences=experiences,
        projects=projects,
        technical_skills=technical_skills,
        publications=publications,
        certificates=certificates,
    )


def render_resume_latex(
    user: UserProfile,
    educations: list[EducationOut],
    experiences: list[ExperienceIn],
    projects: list[ProjectIn],
    technical_skills: list[TechnicalSkillIn],
    publications: list[PublicationIn],
    certificates: list[CertificateOut],
    template: int,
) -> str:
    """Renders a LaTeX resume."""
    return render_template(
        TEMPLATE_TEX_FILE,
        user,
        educations,
        experiences,
        projects,
        technical_skills,
        publications,
        certificates,
        template,
    )


def render_resume_html(
    user: UserProfile,
    educations: list[EducationOut],
    experiences: list[ExperienceIn],
    projects: list[ProjectIn],
    technical_skills: list[TechnicalSkillIn],
    publications: list[PublicationIn],
    certificates: list[CertificateOut],
    template: int,
) -> str:
    """Renders an HTML resume."""
    return render_template(
        TEMPLATE_HTML_FILE,
        user,
        educations,
        experiences,
        projects,
        technical_skills,
        publications,
        certificates,
        template,
    )


def compile_latex_remotely(latex_code: str) -> bytes:
    """Compiles LaTeX code remotely using an API."""
    payload = {
        "compiler": "pdflatex",
        "resources": [{"main": True, "content": latex_code}],
    }

    response = requests.post(LATEX_API_URL, json=payload)

    if response.status_code != 201:
        raise RuntimeError(f"LaTeX API error: {response.status_code}")
    return response.content
