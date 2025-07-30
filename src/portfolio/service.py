import json
from datetime import datetime
from logging import getLogger
from typing import Any, Optional
from uuid import uuid4

from fastapi import UploadFile

from src.certificate.service import generate_signed_url, get_user_certificates
from src.cv.schemas import (
    ExperienceIn,
    ProjectTechnologyIn,
    PublicationIn,
    ResourceURLIn,
    TechnicalSkillIn,
)
from src.database import get_db, get_supabase
from src.education.service import get_user_education
from src.portfolio.exceptions import (
    PortfolioInvalidThemeException,
    PortfolioNotFoundException,
)
from src.portfolio.schemas import (
    FeedbackIn,
    PortfolioFullOut,
    PortfolioListOut,
    PortfolioOut,
    PortfolioProjectIn,
    PortfolioSaveRequest,
    PublicPortfolioOut,
)
from src.users.service import get_user_profile_by_uid
from src.util import to_datetime

logger = getLogger(__name__)

PORTFOLIO_IMAGE_BUCKET = "portfolio-images"


async def create_new_portfolio(uid: str, theme: str) -> int:
    if theme not in ["modern", "classic"]:
        raise PortfolioInvalidThemeException()

    async with get_db() as db:
        new_portfolio = await db.portfolio.create(
            data={
                "user_id": uid,
                "theme": theme,
                "title": f"Portfolio-{uuid4().hex[:8]}-{theme}",
            }
        )
        return int(new_portfolio.id)


async def list_of_portfolios(uid: str) -> list[PortfolioListOut]:
    async with get_db() as db:
        portfolios = await db.portfolio.find_many(
            where={"user_id": uid},
            order={"updated_at": "desc"},
        )
        return [
            PortfolioListOut(
                portfolio_id=portfolio.id,
                title=portfolio.title,
                theme=portfolio.theme,
                created_at=portfolio.created_at,
                updated_at=portfolio.updated_at,
                is_public=portfolio.is_public,
                bio=portfolio.bio or "",
            )
            for portfolio in portfolios
        ]


async def get_portfolio_details(uid: str, portfolio_id: int) -> PortfolioFullOut:
    async with get_db() as db, get_supabase() as supabase:
        portfolio = await db.portfolio.find_unique(where={"id": portfolio_id})
        if not portfolio or portfolio.user_id != uid:
            raise PortfolioNotFoundException()

        exp_links = await db.portfolio_experience.find_many(
            where={"portfolio_id": portfolio_id}, include={"experience": True}
        )
        proj_links = await db.portfolio_project.find_many(
            where={"portfolio_id": portfolio_id}, include={"project": True}
        )
        pub_links = await db.portfolio_publication.find_many(
            where={"portfolio_id": portfolio_id}, include={"publication": True}
        )
        skill_links = await db.portfolio_technicalskill.find_many(
            where={"portfolio_id": portfolio_id}, include={"technical_skill": True}
        )
        feedbacks = await db.portfoliofeedback.find_many(
            where={"portfolio_id": portfolio_id}
        )

        experiences = []
        for link in exp_links:
            exp_dict = link.experience.__dict__.copy()
            # Handle date fields consistently
            exp_dict["start_date"] = to_datetime(exp_dict["start_date"])
            exp_dict["end_date"] = to_datetime(exp_dict["end_date"])
            logo_url = exp_dict.get("company_logo")
            if logo_url:
                exp_dict["company_logo"] = generate_signed_url(
                    supabase, logo_url, PORTFOLIO_IMAGE_BUCKET
                )
            if exp_dict.get("company_logo") is None:
                exp_dict["company_logo"] = ""
            experiences.append(ExperienceIn(**exp_dict))

        projects = []
        for link in proj_links:
            p = link.project
            techs = await db.projecttechnology.find_many(where={"project_id": p.id})
            urls = await db.resourceurl.find_many(
                where={"source_id": p.id, "source_type": "project"}
            )
            thumb_url = link.thumbnail_url
            if thumb_url:
                thumb_url = generate_signed_url(
                    supabase, thumb_url, PORTFOLIO_IMAGE_BUCKET
                )
            projects.append(
                PortfolioProjectIn(
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
                    thumbnail_url=thumb_url,
                )
            )

        publications = []
        for link in pub_links:
            pub = link.publication
            urls = await db.resourceurl.find_many(
                where={"source_id": pub.id, "source_type": "publication"}
            )
            publications.append(
                PublicationIn(
                    id=pub.id,
                    title=pub.title,
                    journal=pub.journal,
                    year=pub.year,
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

        feedbacks_out = [FeedbackIn(**fb.__dict__) for fb in feedbacks]

        return PortfolioFullOut(
            id=portfolio.id,
            theme=portfolio.theme,
            title=portfolio.title,
            is_public=portfolio.is_public,
            bio=portfolio.bio or "",
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
            published_url=portfolio.published_url,
            published_at=portfolio.published_at,
            experiences=experiences,
            publications=publications,
            technical_skills=technical_skills,
            projects=projects,
            feedbacks=feedbacks_out,
        )


async def update_portfolio_content(
    uid: str, payload: PortfolioSaveRequest
) -> PortfolioOut:
    async with get_db() as db:
        portfolio = await db.portfolio.find_unique(where={"id": payload.portfolio_id})
        if not portfolio or portfolio.user_id != uid:
            raise PortfolioNotFoundException()

        # Delete all shared table links
        await db.portfolio_experience.delete_many(
            where={"portfolio_id": payload.portfolio_id}
        )
        await db.portfolio_project.delete_many(
            where={"portfolio_id": payload.portfolio_id}
        )
        await db.portfolio_publication.delete_many(
            where={"portfolio_id": payload.portfolio_id}
        )
        await db.portfolio_technicalskill.delete_many(
            where={"portfolio_id": payload.portfolio_id}
        )

        save_content = payload.save_content

        # Update main portfolio fields
        updated_portfolio = await db.portfolio.update(
            where={"id": payload.portfolio_id},
            data={
                "title": save_content.title,
                "bio": save_content.bio,
                "updated_at": datetime.now(),
            },
        )

        # Experiences
        for exp in save_content.experiences:
            exp_id = exp.id
            if not exp_id:
                new_exp_data = exp.model_dump(exclude={"id"})
                # Always convert start_date and end_date to datetime
                new_exp_data["start_date"] = to_datetime(new_exp_data["start_date"])
                new_exp_data["end_date"] = to_datetime(new_exp_data["end_date"])
                new_exp = await db.experience.create(data=new_exp_data)
                exp_id = new_exp.id
            await db.portfolio_experience.create(
                data={"portfolio_id": payload.portfolio_id, "exp_id": exp_id}
            )

        # Projects
        for proj in save_content.projects:
            proj_id = proj.id
            if not proj_id:
                new_proj_data = {
                    "name": proj.name,
                    "description": proj.description,
                }
                new_proj = await db.project.create(data=new_proj_data)
                proj_id = new_proj.id
            await db.portfolio_project.create(
                data={
                    "portfolio_id": payload.portfolio_id,
                    "project_id": proj_id,
                    "thumbnail_url": proj.thumbnail_url,
                }
            )
            # Technologies
            await db.projecttechnology.delete_many(where={"project_id": proj_id})
            for tech in proj.technologies:
                await db.projecttechnology.create(
                    data={"project_id": proj_id, "technology": tech.technology}
                )
            # URLs
            await db.resourceurl.delete_many(
                where={"source_id": proj_id, "source_type": "project"}
            )
            for url in proj.urls:
                await db.resourceurl.create(
                    data={
                        "source_id": proj_id,
                        "source_type": url.source_type,
                        "label": url.label,
                        "url": url.url,
                    }
                )

        # Publications
        for pub in save_content.publications:
            pub_id = pub.id
            if not pub_id:
                new_pub_data = pub.model_dump(exclude={"id", "urls"})
                new_pub = await db.publication.create(data=new_pub_data)
                pub_id = new_pub.id
            await db.portfolio_publication.create(
                data={"portfolio_id": payload.portfolio_id, "publication_id": pub_id}
            )
            # URLs
            await db.resourceurl.delete_many(
                where={"source_id": pub_id, "source_type": "publication"}
            )
            for url in pub.urls:
                await db.resourceurl.create(
                    data={
                        "source_id": pub_id,
                        "source_type": url.source_type,
                        "label": url.label,
                        "url": url.url,
                    }
                )

        # Technical Skills
        for skill in save_content.technical_skills:
            skill_id = skill.id
            if not skill_id:
                new_skill_data = skill.model_dump(exclude={"id"})
                new_skill = await db.technicalskill.create(data=new_skill_data)
                skill_id = new_skill.id
            await db.portfolio_technicalskill.create(
                data={"portfolio_id": payload.portfolio_id, "tech_skill_id": skill_id}
            )

        return PortfolioOut(
            id=updated_portfolio.id,
            title=updated_portfolio.title,
            theme=updated_portfolio.theme,
            created_at=updated_portfolio.created_at,
            updated_at=updated_portfolio.updated_at,
            is_public=updated_portfolio.is_public,
            bio=updated_portfolio.bio or "",
        )


async def upload_image_to_supabase(
    supabase: Any, uid: str, file: UploadFile, folder: str
) -> str:
    content = await file.read()
    filename = f"{uid}/{folder}/{uuid4().hex}_{file.filename}"
    supabase.storage.from_("portfolio-images").upload(
        filename, content, {"content-type": file.content_type}
    )
    url: Optional[str] = supabase.storage.from_("portfolio-images").get_public_url(
        filename
    )
    return url if url is not None else ""


async def upload_company_logo(
    supabase: Any, uid: str, experience_id: int, file: UploadFile
) -> str:
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else ""
    filename = f"{uid}/experience-{experience_id}/{uuid4()}.{ext}"
    content = await file.read()
    supabase.storage.from_("portfolio-images").upload(
        filename, content, {"content-type": file.content_type}
    )
    url: Optional[str] = supabase.storage.from_("portfolio-images").get_public_url(
        filename
    )
    return url if url is not None else ""


async def upload_project_thumbnail(
    supabase: Any, uid: str, project_id: int, file: UploadFile
) -> str:
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else ""
    filename = f"{uid}/project-{project_id}/{uuid4()}.{ext}"
    content = await file.read()
    supabase.storage.from_("portfolio-images").upload(
        filename, content, {"content-type": file.content_type}
    )
    url: Optional[str] = supabase.storage.from_("portfolio-images").get_public_url(
        filename
    )
    return url if url is not None else ""


async def delete_existing_image(supabase: Any, image_url: Optional[str]) -> None:
    # Extract path from public URL
    if not image_url or not isinstance(image_url, str):
        return
    if "/storage/v1/object/public/portfolio-images/" not in image_url:
        return
    path = image_url.split("/storage/v1/object/public/portfolio-images/")[-1]
    if path:
        supabase.storage.from_("portfolio-images").remove([path])


async def update_portfolio(
    uid: str,
    portfolio_id: int,
    title: str,
    bio: str,
    experiences_json: str,
    projects_json: str,
    publications_json: str,
    technical_skills_json: str,
    project_thumbnails: list[UploadFile],
    company_logos: list[UploadFile],
) -> PortfolioOut:
    async with get_db() as db, get_supabase() as supabase:
        portfolio = await db.portfolio.find_unique(where={"id": portfolio_id})
        if not portfolio or portfolio.user_id != uid:
            raise PortfolioNotFoundException()

        # Fix: Delete project technologies before deleting portfolio_project links
        proj_links = await db.portfolio_project.find_many(
            where={"portfolio_id": portfolio_id}
        )
        for link in proj_links:
            await db.projecttechnology.delete_many(
                where={"project_id": link.project_id}
            )

        await db.portfolio_experience.delete_many(where={"portfolio_id": portfolio_id})
        await db.portfolio_project.delete_many(where={"portfolio_id": portfolio_id})
        await db.portfolio_publication.delete_many(where={"portfolio_id": portfolio_id})
        await db.portfolio_technicalskill.delete_many(
            where={"portfolio_id": portfolio_id}
        )

        # Parse JSON fields
        experiences = json.loads(experiences_json)
        projects = json.loads(projects_json)
        publications = json.loads(publications_json)
        technical_skills = json.loads(technical_skills_json)

        # Update main portfolio fields
        updated_portfolio = await db.portfolio.update(
            where={"id": portfolio_id},
            data={
                "title": title,
                "bio": bio,
                "updated_at": datetime.now(),
            },
        )

        # Experiences (handle company_logo)
        for idx, exp in enumerate(experiences):
            exp_id = exp.get("id")
            logo_url = None
            # Delete previous logo if present
            if exp_id:
                old_exp = await db.experience.find_unique(where={"id": exp_id})
                if (
                    old_exp
                    and old_exp.company_logo
                    and idx < len(company_logos)
                    and company_logos[idx]
                ):
                    await delete_existing_image(supabase, old_exp.company_logo)
            if idx < len(company_logos) and company_logos[idx]:
                # Ensure exp_id is int for upload_company_logo
                logo_url = await upload_company_logo(
                    supabase,
                    uid,
                    (
                        int(exp_id)
                        if exp_id is not None and isinstance(exp_id, int)
                        else 0
                    ),
                    company_logos[idx],
                )
                exp["company_logo"] = logo_url
            if not exp_id:
                new_exp_data = exp.copy()
                new_exp_data.pop("id", None)
                # Remove company_logo if not present or empty string
                if (
                    "company_logo" not in new_exp_data
                    or not new_exp_data["company_logo"]
                ):
                    new_exp_data.pop("company_logo", None)
                # Always convert start_date and end_date to datetime
                new_exp_data["start_date"] = to_datetime(new_exp_data["start_date"])
                new_exp_data["end_date"] = to_datetime(new_exp_data["end_date"])
                new_exp = await db.experience.create(data=new_exp_data)
                exp_id = new_exp.id
            else:
                # Only update company_logo if a new file was uploaded
                if idx < len(company_logos) and company_logos[idx]:
                    await db.experience.update(
                        where={"id": exp_id},
                        data={"company_logo": exp.get("company_logo")},
                    )
            await db.portfolio_experience.create(
                data={"portfolio_id": portfolio_id, "exp_id": exp_id}
            )

        # Projects (handle thumbnail_url)
        for idx, proj in enumerate(projects):
            proj_id = proj.get("id")
            thumb_url = None
            # If a new thumbnail is uploaded, delete previous and upload new
            if proj_id:
                old_proj = await db.project.find_unique(where={"id": proj_id})
                if (
                    old_proj
                    and old_proj.thumbnail_url
                    and idx < len(project_thumbnails)
                    and project_thumbnails[idx]
                ):
                    await delete_existing_image(supabase, old_proj.thumbnail_url)
            if idx < len(project_thumbnails) and project_thumbnails[idx]:
                # Ensure proj_id is int for upload_project_thumbnail
                thumb_url = await upload_project_thumbnail(
                    supabase,
                    uid,
                    (
                        int(proj_id)
                        if proj_id is not None and isinstance(proj_id, int)
                        else 0
                    ),
                    project_thumbnails[idx],
                )
                proj["thumbnail_url"] = thumb_url
            else:
                # If no new file, keep the existing thumbnail_url if present
                if proj_id and old_proj and old_proj.thumbnail_url:
                    proj["thumbnail_url"] = old_proj.thumbnail_url
            if not proj_id:
                new_proj_data = {
                    "name": proj["name"],
                    "description": proj["description"],
                }
                # Make thumbnail_url optional
                if "thumbnail_url" in proj and proj["thumbnail_url"]:
                    new_proj_data["thumbnail_url"] = proj["thumbnail_url"]
                new_proj = await db.project.create(data=new_proj_data)
                proj_id = new_proj.id
            else:
                # Only update thumbnail_url if a new file was uploaded
                if idx < len(project_thumbnails) and project_thumbnails[idx]:
                    await db.project.update(
                        where={"id": proj_id},
                        data={"thumbnail_url": proj.get("thumbnail_url")},
                    )
            await db.portfolio_project.create(
                data={
                    "portfolio_id": portfolio_id,
                    "project_id": proj_id,
                    "thumbnail_url": proj.get("thumbnail_url"),
                }
            )
            # Technologies
            await db.projecttechnology.delete_many(where={"project_id": proj_id})
            for tech in proj.get("technologies", []):
                await db.projecttechnology.create(
                    data={"project_id": proj_id, "technology": tech["technology"]}
                )
            # URLs
            await db.resourceurl.delete_many(
                where={"source_id": proj_id, "source_type": "project"}
            )
            for url in proj.get("urls", []):
                await db.resourceurl.create(
                    data={
                        "source_id": proj_id,
                        "source_type": url["source_type"],
                        "label": url["label"],
                        "url": url["url"],
                    }
                )

        # Publications
        for pub in publications:
            pub_id = pub.get("id")
            if not pub_id:
                new_pub_data = {k: v for k, v in pub.items() if k not in {"id", "urls"}}
                new_pub = await db.publication.create(data=new_pub_data)
                pub_id = new_pub.id
            await db.portfolio_publication.create(
                data={"portfolio_id": portfolio_id, "publication_id": pub_id}
            )
            # URLs
            await db.resourceurl.delete_many(
                where={"source_id": pub_id, "source_type": "publication"}
            )
            for url in pub.get("urls", []):
                await db.resourceurl.create(
                    data={
                        "source_id": pub_id,
                        "source_type": url["source_type"],
                        "label": url["label"],
                        "url": url["url"],
                    }
                )

        # Technical Skills
        for skill in technical_skills:
            skill_id = skill.get("id")
            if not skill_id:
                new_skill_data = {k: v for k, v in skill.items() if k != "id"}
                new_skill = await db.technicalskill.create(data=new_skill_data)
                skill_id = new_skill.id
            await db.portfolio_technicalskill.create(
                data={"portfolio_id": portfolio_id, "tech_skill_id": skill_id}
            )

        return PortfolioOut(
            id=updated_portfolio.id,
            title=updated_portfolio.title,
            theme=updated_portfolio.theme,
            created_at=updated_portfolio.created_at,
            updated_at=updated_portfolio.updated_at,
            is_public=updated_portfolio.is_public,
            bio=updated_portfolio.bio or "",
        )


async def publish_portfolio_service(uid: str, portfolio_id: int) -> str:
    async with get_db() as db:
        portfolio = await db.portfolio.find_unique(where={"id": portfolio_id})
        if not portfolio or portfolio.user_id != uid:
            raise PortfolioNotFoundException()
        published_url = uuid4().hex + uuid4().hex[:8]
        await db.portfolio.update(
            where={"id": portfolio_id},
            data={
                "is_public": True,
                "published_url": published_url,
                "published_at": datetime.now(),
            },
        )
        return published_url


async def view_public_portfolio_service(published_url: str) -> PublicPortfolioOut:
    async with get_db() as db:
        portfolio = await db.portfolio.find_unique(
            where={"published_url": published_url}
        )
        if not portfolio or not portfolio.is_public:
            from src.portfolio.exceptions import PortfolioNotFoundException

            raise PortfolioNotFoundException()
        # Get full details
        details = await get_portfolio_details(portfolio.user_id, portfolio.id)
        # Remove id fields from response
        details_dict = details.model_dump()
        details_dict.pop("id", None)
        # Remove id from experiences, projects, publications, technical_skills, feedbacks
        for exp in details_dict.get("experiences", []):
            exp.pop("id", None)
        for proj in details_dict.get("projects", []):
            proj.pop("id", None)
            for tech in proj.get("technologies", []):
                tech.pop("id", None)
            for url in proj.get("urls", []):
                url.pop("id", None)
        for pub in details_dict.get("publications", []):
            pub.pop("id", None)
            for url in pub.get("urls", []):
                url.pop("id", None)
        for skill in details_dict.get("technical_skills", []):
            skill.pop("id", None)
        for fb in details_dict.get("feedbacks", []):
            fb.pop("id", None)
        # Return as PublicPortfolioOut (Pydantic will ignore extra fields)
        return PublicPortfolioOut(**details_dict)


async def get_full_public_portfolio(published_url: str) -> PublicPortfolioOut:
    """
    Returns a PublicPortfolioOut with all public info, including user, education, certificates.
    Handles all input/output processing for the /public/{published_url} endpoint.
    Removes id fields from education and certificates.
    """
    details: PublicPortfolioOut = await view_public_portfolio_service(published_url)
    owner_uid: str = await get_portfolio_owner_uid_by_published_url(published_url)
    user_profile = await get_user_profile_by_uid(owner_uid)
    education = await get_user_education(owner_uid)
    certificates = await get_user_certificates(owner_uid)

    # Remove id fields from education and certificates
    education_no_id = [
        (
            {k: v for k, v in e.model_dump().items() if k != "id"}
            if hasattr(e, "model_dump")
            else {k: v for k, v in e.__dict__.items() if k != "id"}
        )
        for e in education
    ]
    certificates_no_id = [
        (
            {k: v for k, v in c.model_dump().items() if k != "id"}
            if hasattr(c, "model_dump")
            else {k: v for k, v in c.__dict__.items() if k != "id"}
        )
        for c in certificates
    ]

    details_dict = details.model_dump()
    details_dict["user_profile"] = user_profile
    details_dict["education"] = education_no_id
    details_dict["certificates"] = certificates_no_id
    return PublicPortfolioOut(**details_dict)


async def unpublish_portfolio_service(uid: str, portfolio_id: int) -> dict[str, str]:
    async with get_db() as db:
        portfolio = await db.portfolio.find_unique(where={"id": portfolio_id})
        if not portfolio or portfolio.user_id != uid:
            raise PortfolioNotFoundException()
        await db.portfolio.update(
            where={"id": portfolio_id},
            data={
                "is_public": False,
                "published_url": None,
                "published_at": datetime.now(),  # Use current time or a valid datetime
            },
        )
        return {"message": "Portfolio unpublished and public URL removed."}


async def get_portfolio_owner_uid_by_published_url(published_url: str) -> str:
    """
    Returns the user_id (owner UID) for a given published_url.
    Raises PortfolioNotFoundException if not found or not public.
    """
    async with get_db() as db:
        portfolio = await db.portfolio.find_unique(
            where={"published_url": published_url}
        )
        if not portfolio or not portfolio.is_public:
            raise PortfolioNotFoundException()
    return str(portfolio.user_id)  # Ensure return type is str
