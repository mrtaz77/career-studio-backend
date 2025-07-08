import json
from datetime import datetime, timezone
from logging import getLogger
from typing import List
from uuid import uuid4

import redis.asyncio as aioredis
from supabase import Client

from src.certificate.schemas import CertificateOut
from src.certificate.service import STORAGE_BUCKET as CERTIFICATE_STORAGE_BUCKET
from src.certificate.service import generate_signed_url
from src.config import settings
from src.cv.exceptions import (
    CVInvalidTemplateException,
    CVInvalidTypeException,
    CVNotFoundException,
    CVSaveException,
)
from src.cv.generator import (
    compile_latex_remotely,
    render_resume_latex,
    render_resume_html,
)
from src.cv.schemas import (
    CVAutoSaveRequest,
    CVFullOut,
    CVListOut,
    CVOut,
    CVSaveContent,
    CVSaveRequest,
    ExperienceIn,
    ProjectIn,
    ProjectTechnologyIn,
    PublicationIn,
    ResourceURLIn,
    TechnicalSkillIn,
)
from src.database import get_db, get_supabase
from src.education.schemas import EducationOut
from src.prisma_client import Prisma, models
from src.users.schemas import UserProfile
from src.util import serialize_for_json, to_datetime
from fastapi.encoders import jsonable_encoder

logger = getLogger(__name__)
REDIS_AUTOSAVE_PREFIX = "autosave:cv:"
STORAGE_BUCKET = "cvs"
NUMBER_OF_CV_TEMPLATES = 1

redis_client = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True
)  # type: ignore[no-untyped-call]


async def autosave_cv(uid: str, payload: CVAutoSaveRequest) -> None:
    key = f"{REDIS_AUTOSAVE_PREFIX}{payload.cv_id}"
    try:
        raw = {
            "user_id": uid,
            "draft_content": payload.draft_content.model_dump(),
            "timestamp": datetime.now(timezone.utc),
        }
        value = json.dumps(serialize_for_json(raw))
        await redis_client.set(key, value, ex=3600)
    except Exception as e:
        logger.exception("Autosave failed", exc_info=True)
        raise CVSaveException("Autosave failed.") from e


async def save_cv_version(uid: str, payload: CVSaveRequest) -> CVOut:
    async with get_db() as db:
        await validate_cv_ownership(db, uid, payload.cv_id)
        version = await create_new_version(db, payload)
        updated_cv = await update_cv(db, payload.cv_id, version.id)
        await clear_existing_links(db, payload.cv_id)
        await process_content(db, payload.cv_id, payload.save_content)
        await redis_client.delete(f"{REDIS_AUTOSAVE_PREFIX}{payload.cv_id}")
        return build_cv_out(updated_cv, version.version_number)


async def clear_existing_links(db: Prisma, cv_id: int) -> None:
    await db.cv_experience.delete_many(where={"cv_id": cv_id})
    await db.cv_publication.delete_many(where={"cv_id": cv_id})
    await db.cv_technicalskill.delete_many(where={"cv_id": cv_id})
    await db.cv_project.delete_many(where={"cv_id": cv_id})


async def validate_cv_ownership(db: Prisma, uid: str, cv_id: int) -> models.CV:
    cv = await db.cv.find_unique(where={"id": cv_id})
    if not cv or cv.user_id != uid:
        raise CVNotFoundException()
    return cv


async def create_new_version(db: Prisma, payload: CVSaveRequest) -> models.CVVersion:
    existing_versions = await db.cvversion.find_many(
        where={"cv_id": payload.cv_id}, order={"version_number": "desc"}, take=1
    )
    last_version = existing_versions[0] if existing_versions else None
    new_version_num = last_version.version_number + 1 if last_version else 1
    parent_version_id = last_version.id if last_version else None

    return await db.cvversion.create(
        data={
            "cv_id": payload.cv_id,
            "version_number": new_version_num,
            "pdf_url": payload.pdf_url or "",
            "parent_version_id": parent_version_id,
        }
    )


async def update_cv(db: Prisma, cv_id: int, version_id: int) -> models.CV:
    return await db.cv.update(
        where={"id": cv_id},
        data={
            "latest_saved_version_id": version_id,
            "is_draft": False,
        },
    )


async def process_content(db: Prisma, cv_id: int, content: CVSaveContent) -> None:
    await process_experiences(db, cv_id, content.experiences)
    await process_publications(db, cv_id, content.publications)
    await process_technical_skills(db, cv_id, content.technical_skills)
    await process_projects(db, cv_id, content.projects)


async def process_experiences(
    db: Prisma, cv_id: int, experiences: List[ExperienceIn]
) -> None:
    for item in experiences:
        exp_id = item.id
        if not exp_id:
            new_exp_data = serialize_for_json(item.model_dump(exclude={"id"}))
            new_exp_data["start_date"] = to_datetime(item.start_date)
            new_exp_data["end_date"] = to_datetime(item.end_date)
            new_exp = await db.experience.create(data=new_exp_data)
            exp_id = new_exp.id
        await db.cv_experience.create(data={"cv_id": cv_id, "experience_id": exp_id})


async def process_publications(
    db: Prisma, cv_id: int, publications: List[PublicationIn]
) -> None:
    for item in publications:
        pub_id = item.id
        if not pub_id:
            new_pub_data = serialize_for_json(item.model_dump(exclude={"id", "urls"}))
            new_pub = await db.publication.create(data=new_pub_data)
            pub_id = new_pub.id
        await db.cv_publication.create(data={"cv_id": cv_id, "publication_id": pub_id})
        await process_publication_details(db, pub_id, item)


async def process_publication_details(
    db: Prisma, pub_id: int, publication: PublicationIn
) -> None:
    await db.resourceurl.delete_many(
        where={"source_id": pub_id, "source_type": "publication"}
    )

    for url in publication.urls:
        await db.resourceurl.create(
            data={
                "source_id": pub_id,
                "source_type": "publication",
                "label": url.label,
                "url": url.url,
            }
        )


async def process_technical_skills(
    db: Prisma, cv_id: int, skills: List[TechnicalSkillIn]
) -> None:
    for item in skills:
        skill_id = item.id
        if not skill_id:
            new_skill_data = serialize_for_json(item.model_dump(exclude={"id"}))
            new_skill = await db.technicalskill.create(data=new_skill_data)
            skill_id = new_skill.id
        await db.cv_technicalskill.create(
            data={"cv_id": cv_id, "tech_skill_id": skill_id}
        )


async def process_projects(db: Prisma, cv_id: int, projects: List[ProjectIn]) -> None:
    for project in projects:
        proj_id = project.id
        if not proj_id:
            new_proj_data = serialize_for_json(
                {"name": project.name, "description": project.description}
            )
            new_proj = await db.project.create(data=new_proj_data)
            proj_id = new_proj.id
        await db.cv_project.create(data={"cv_id": cv_id, "project_id": proj_id})
        await process_project_details(db, proj_id, project)


async def process_project_details(db: Prisma, proj_id: int, project: ProjectIn) -> None:
    await db.projecttechnology.delete_many(where={"project_id": proj_id})
    await db.resourceurl.delete_many(
        where={"source_id": proj_id, "source_type": "project"}
    )

    for tech in project.technologies:
        await db.projecttechnology.create(
            data={"project_id": proj_id, "technology": tech.technology}
        )

    for url in project.urls:
        await db.resourceurl.create(
            data={
                "source_id": proj_id,
                "source_type": "project",
                "label": url.label,
                "url": url.url,
            }
        )


def build_cv_out(updated_cv: models.CV, version: int) -> CVOut:
    return CVOut(
        id=updated_cv.id,
        title=updated_cv.title,
        template=updated_cv.template,
        type=updated_cv.type,
        is_draft=updated_cv.is_draft,
        bookmark=updated_cv.bookmark,
        pdf_url=updated_cv.pdf_url,
        latest_saved_version_id=updated_cv.latest_saved_version_id,
        version_number=version,
        created_at=updated_cv.created_at,
        updated_at=updated_cv.updated_at,
    )


async def create_new_cv(uid: str, cv_type: str, cv_template: int) -> int:
    if cv_type not in {"academic", "industry"}:
        raise CVInvalidTypeException()

    if cv_template <= 0 or cv_template > NUMBER_OF_CV_TEMPLATES:
        raise CVInvalidTemplateException()

    async with get_db() as db:
        new_cv = await db.cv.create(
            data={
                "user_id": uid,
                "type": cv_type,
                "is_draft": True,
                "bookmark": False,
                "title": f"CV-{uuid4().hex[:8]}",
                "template": cv_template,
            }
        )
        return int(new_cv.id)


async def get_cv_details(uid: str, cv_id: int) -> CVFullOut:
    redis_key = f"{REDIS_AUTOSAVE_PREFIX}{cv_id}"
    cached = await redis_client.get(redis_key)
    if cached:
        return _build_cv_from_cache(cv_id, cached)

    async with get_db() as db:
        cv = await db.cv.find_unique(where={"id": cv_id})
        if not cv or cv.user_id != uid:
            raise CVNotFoundException()
        return await _build_cv_from_db(db, cv)


def _build_cv_from_cache(cv_id: int, cached: str) -> CVFullOut:
    parsed = json.loads(cached)
    draft = parsed["draft_content"]
    return CVFullOut(
        id=cv_id,
        type=draft.get("type", ""),
        template=draft.get("template", 1),
        title=draft.get("title", ""),
        is_draft=True,
        bookmark=draft.get("bookmark", False),
        pdf_url=draft.get("pdf_url"),
        latest_saved_version_id=draft.get("latest_saved_version_id"),
        version_number=draft.get("version_number"),
        created_at=draft.get("created_at", datetime.now(timezone.utc)),
        updated_at=draft.get("updated_at", datetime.now(timezone.utc)),
        experiences=[ExperienceIn(**exp) for exp in draft.get("experiences", [])],
        publications=[PublicationIn(**pub) for pub in draft.get("publications", [])],
        technical_skills=[
            TechnicalSkillIn(**s) for s in draft.get("technical_skills", [])
        ],
        projects=[
            ProjectIn(
                id=proj.get("id"),
                name=proj["name"],
                description=proj["description"],
                technologies=[
                    models.ProjectTechnology(**tech)
                    for tech in proj.get("technologies", [])
                ],
                urls=[ResourceURLIn(**url) for url in proj.get("urls", [])],
            )
            for proj in draft.get("projects", [])
        ],
    )


async def _build_cv_from_db(db: Prisma, cv: models.CV) -> CVFullOut:
    exp_links, pub_links, skill_links, proj_links, latest_version = (
        await _fetch_cv_related_entities(db, cv)
    )
    version_number = latest_version.version_number if latest_version else None

    experiences = [ExperienceIn(**link.experience.__dict__) for link in exp_links]
    publications = []
    for link in pub_links:
        p = link.publication
        urls = await db.resourceurl.find_many(
            where={"source_id": p.id, "source_type": "publication"}
        )
        publications.append(
            PublicationIn(
                id=p.id,
                title=p.title,
                journal=p.journal,
                year=p.year,
                urls=[
                    ResourceURLIn(
                        id=u.id, label=u.label, url=u.url, source_type=u.source_type
                    )
                    for u in urls
                ],
            )
        )

    technical_skills = [
        TechnicalSkillIn(**link.technical_skill.__dict__) for link in skill_links
    ]

    projects = []
    for link in proj_links:
        p = link.project
        techs = await db.projecttechnology.find_many(where={"project_id": p.id})
        urls = await db.resourceurl.find_many(
            where={"source_id": p.id, "source_type": "project"}
        )
        projects.append(
            ProjectIn(
                id=p.id,
                name=p.name,
                description=p.description,
                technologies=[
                    ProjectTechnologyIn(id=t.id, technology=t.technology) for t in techs
                ],
                urls=[
                    ResourceURLIn(
                        id=u.id, label=u.label, url=u.url, source_type=u.source_type
                    )
                    for u in urls
                ],
            )
        )

    return CVFullOut(
        id=cv.id,
        type=cv.type,
        title=cv.title,
        template=cv.template,
        is_draft=cv.is_draft,
        bookmark=cv.bookmark,
        pdf_url=cv.pdf_url,
        latest_saved_version_id=cv.latest_saved_version_id,
        version_number=version_number,
        created_at=cv.created_at,
        updated_at=cv.updated_at,
        experiences=experiences,
        publications=publications,
        technical_skills=technical_skills,
        projects=projects,
    )


async def _fetch_cv_related_entities(db: Prisma, cv: models.CV) -> tuple[
    List[models.CV_Experience],
    List[models.CV_Publication],
    List[models.CV_TechnicalSkill],
    List[models.CV_Project],
    models.CVVersion | None,
]:
    exp_links = await db.cv_experience.find_many(
        where={"cv_id": cv.id}, include={"experience": True}
    )
    pub_links = await db.cv_publication.find_many(
        where={"cv_id": cv.id}, include={"publication": True}
    )
    skill_links = await db.cv_technicalskill.find_many(
        where={"cv_id": cv.id}, include={"technical_skill": True}
    )
    proj_links = await db.cv_project.find_many(
        where={"cv_id": cv.id}, include={"project": True}
    )
    if cv.latest_saved_version_id:
        latest_version = await db.cvversion.find_unique(
            where={"id": cv.latest_saved_version_id}
        )
    else:
        latest_version = 0
    return exp_links, pub_links, skill_links, proj_links, latest_version


def upload_pdf_bytes_to_supabase(
    supabase: Client, uid: str, content: bytes, bucket: str
) -> str:
    filename = f"{uid}/{uuid4()}.pdf"
    supabase.storage.from_(bucket).upload(
        filename, content, {"content-type": "application/pdf"}
    )
    return filename


async def process_cv_generation(
    uid: str, payload: CVAutoSaveRequest, force_regenerate: bool = True
) -> str:
    async with get_db() as db, get_supabase() as supabase:
        cv = await validate_cv_ownership(db, uid, payload.cv_id)

        if not force_regenerate and cv.pdf_url:
            return generate_signed_url(supabase, cv.pdf_url, STORAGE_BUCKET)

        user = await db.user.find_unique(where={"uid": uid})
        certificates = await db.certification.find_many(
            where={"user_id": uid}, order={"issued_date": "desc"}
        )

        user_out = UserProfile(**jsonable_encoder(user))
        certificates_out = [
            CertificateOut(
                id=c.id,
                title=c.title,
                issuer=c.issuer,
                issued_date=str(c.issued_date),
                link=generate_signed_url(
                    supabase, c.link, CERTIFICATE_STORAGE_BUCKET, 36000
                ),
            )
            for c in certificates
        ]

        # Use content directly from payload
        draft = payload.draft_content
        educations = await db.education.find_many(
            where={"user_id": uid}, order={"end_date": "desc"}
        )
        educations_out = [EducationOut(**e.__dict__) for e in educations]

        latex_code = render_resume_latex(
            user_out,
            educations_out,
            sorted(draft.experiences, key=lambda e: e.end_date, reverse=True),
            draft.projects,
            draft.technical_skills,
            draft.publications,
            certificates_out,
            1,
        )

        pdf_bytes = compile_latex_remotely(latex_code)
        path = upload_pdf_bytes_to_supabase(supabase, uid, pdf_bytes, STORAGE_BUCKET)

        await db.cv.update(where={"id": payload.cv_id}, data={"pdf_url": path})

        return generate_signed_url(supabase, path, STORAGE_BUCKET)


async def list_of_cvs(uid: str) -> list[CVListOut]:
    async with get_db() as db:
        cvs = await db.cv.find_many(
            where={"user_id": uid}, include={"latest_version": True}
        )

        return [
            CVListOut(
                cv_id=cv.id,
                title=cv.title,
                template=cv.template,
                latest_saved_version_id=cv.latest_saved_version_id,
                version_number=(
                    cv.latest_version.version_number if cv.latest_version else 0
                ),
                created_at=cv.created_at,
                updated_at=cv.updated_at,
            )
            for cv in cvs
        ]


async def render_cv(uid: str, payload: CVAutoSaveRequest) -> str:
    async with get_db() as db, get_supabase() as supabase:
        # Validate CV access
        await validate_cv_ownership(db, uid, payload.cv_id)

        # Fetch user and certificates
        user = await db.user.find_unique(where={"uid": uid})
        certificates = await db.certification.find_many(
            where={"user_id": uid}, order={"issued_date": "desc"}
        )

        user_out = UserProfile(**jsonable_encoder(user))
        certificates_out = [
            CertificateOut(
                id=c.id,
                title=c.title,
                issuer=c.issuer,
                issued_date=str(c.issued_date),
                link=generate_signed_url(
                    supabase, c.link, CERTIFICATE_STORAGE_BUCKET, 36000
                ),
            )
            for c in certificates
        ]

        # Use draft content from payload
        draft = payload.draft_content

        # Fetch education from DB
        educations = await db.education.find_many(
            where={"user_id": uid}, order={"end_date": "desc"}
        )
        educations_out = [EducationOut(**e.__dict__) for e in educations]

        # Render to HTML (as string)
        html = render_resume_html(
            user_out,
            educations_out,
            sorted(draft.experiences, key=lambda e: e.end_date, reverse=True),
            draft.projects,
            draft.technical_skills,
            draft.publications,
            certificates_out,
            1,
        )

        return html
