import json
from datetime import datetime, timezone
from logging import getLogger
from typing import List

import redis.asyncio as aioredis

from src.config import settings
from src.cv.exceptions import (
    CVInvalidTypeException,
    CVNotFoundException,
    CVSaveException,
)
from src.cv.schemas import (
    CVAutoSaveRequest,
    CVFullOut,
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
from src.database import get_db
from src.prisma_client import Prisma, models
from src.util import serialize_for_json, to_datetime

logger = getLogger(__name__)
REDIS_AUTOSAVE_PREFIX = "autosave:cv:"

redis_client = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True
)  # type: ignore[no-untyped-call]


async def autosave_cv(uid: str, payload: CVAutoSaveRequest) -> None:
    key = f"{REDIS_AUTOSAVE_PREFIX}{payload.cv_id}"
    try:
        raw = {
            "user_id": uid,
            "draft_data": payload.draft_data.model_dump(),
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
        await process_content(db, payload.cv_id, payload.content)
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
        type=updated_cv.type,
        is_draft=updated_cv.is_draft,
        bookmark=updated_cv.bookmark,
        pdf_url=updated_cv.pdf_url,
        latest_saved_version_id=updated_cv.latest_saved_version_id,
        version_number=version,
        created_at=updated_cv.created_at,
        updated_at=updated_cv.updated_at,
    )


async def create_new_cv(uid: str, cv_type: str) -> int:
    if cv_type not in {"academic", "industry"}:
        raise CVInvalidTypeException()

    async with get_db() as db:
        new_cv = await db.cv.create(
            data={
                "user_id": uid,
                "type": cv_type,
                "is_draft": True,
                "bookmark": False,
            }
        )
        return int(new_cv.id)


async def get_cv_details(uid: str, cv_id: int) -> CVFullOut:
    redis_key = f"{REDIS_AUTOSAVE_PREFIX}{cv_id}"
    cached = await redis_client.get(redis_key)
    if cached:
        parsed = json.loads(cached)
        draft = parsed["draft_data"]
        return CVFullOut(
            id=cv_id,
            type=draft.get("type", ""),
            is_draft=True,
            bookmark=draft.get("bookmark", False),
            pdf_url=draft.get("pdf_url"),
            latest_saved_version_id=draft.get("latest_saved_version_id"),
            version_number=draft.get("version_number"),
            created_at=draft.get("created_at", datetime.now(timezone.utc)),
            updated_at=draft.get("updated_at", datetime.now(timezone.utc)),
            experiences=[ExperienceIn(**exp) for exp in draft.get("experiences", [])],
            publications=[
                PublicationIn(**pub) for pub in draft.get("publications", [])
            ],
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

    async with get_db() as db:
        cv = await db.cv.find_unique(where={"id": cv_id})
        if not cv or cv.user_id != uid:
            raise CVNotFoundException()

        exp_links = await db.cv_experience.find_many(
            where={"cv_id": cv_id}, include={"experience": True}
        )
        pub_links = await db.cv_publication.find_many(
            where={"cv_id": cv_id}, include={"publication": True}
        )
        skill_links = await db.cv_technicalskill.find_many(
            where={"cv_id": cv_id}, include={"technical_skill": True}
        )
        proj_links = await db.cv_project.find_many(
            where={"cv_id": cv_id}, include={"project": True}
        )
        latest_version = await db.cvversion.find_unique(
            where={"id": cv.latest_saved_version_id}
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
                        ProjectTechnologyIn(id=t.id, technology=t.technology)
                        for t in techs
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
