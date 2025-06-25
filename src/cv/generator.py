import os

import requests
from jinja2 import Environment, FileSystemLoader

from src.certificate.schemas import CertificateOut
from src.cv.schemas import ExperienceIn, ProjectIn, PublicationIn, TechnicalSkillIn
from src.education.schemas import EducationOut
from src.users.schemas import UserProfile

TEMPLATE_DIR = "src/cv/templates"
TEMPLATE_FILE = "template.tex"
RESUME_CLS_FILE = "resume.cls"


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
    env = Environment(
        loader=FileSystemLoader(os.path.join(TEMPLATE_DIR, str(template))),
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="(((",
        variable_end_string=")))",
        comment_start_string="((#",
        comment_end_string="#))",
        autoescape=True,
    )
    tpl = env.get_template(TEMPLATE_FILE)
    return tpl.render(
        user=user,
        educations=educations,
        experiences=experiences,
        projects=projects,
        technical_skills=technical_skills,
        publications=publications,
        certificates=certificates,
    )


def compile_latex_remotely(latex_code: str, template: int) -> bytes:
    resume_cls_path = os.path.join(TEMPLATE_DIR, str(template), RESUME_CLS_FILE)
    with open(resume_cls_path, "r") as f:
        resume_cls_content = f.read()

    url = "https://latex.ytotech.com/builds/sync"

    payload = {
        "compiler": "pdflatex",
        "resources": [
            {"main": True, "content": latex_code},
            {"path": "resume.cls", "content": resume_cls_content},
        ],
    }

    response = requests.post(url, json=payload)

    if response.status_code != 201:
        raise RuntimeError(f"LaTeX API error: {response.status_code}")

    return response.content
