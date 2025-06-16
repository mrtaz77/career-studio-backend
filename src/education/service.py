from logging import getLogger

from src.database import get_db
from src.education.exceptions import EducationNotFoundException
from src.education.schemas import EducationCreate, EducationOut, EducationUpdate

logger = getLogger(__name__)


async def get_user_education(uid: str) -> list[EducationOut]:
    async with get_db() as db:
        records = await db.education.find_many(where={"user_id": uid})
        return [
            EducationOut(
                id=r.id,
                degree=r.degree,
                institution=r.institution,
                location=r.location,
                start_date=r.start_date,
                end_date=r.end_date,
                gpa=r.gpa,
                honors=r.honors,
            )
            for r in records
        ]


async def add_education(uid: str, entries: list[EducationCreate]) -> bool:
    async with get_db() as db:
        for entry in entries:
            await db.education.create(data={"user_id": uid, **entry.model_dump()})
        return True


async def delete_education(uid: str, education_id: int) -> bool:
    async with get_db() as db:
        record = await db.education.find_first(
            where={"id": education_id, "user_id": uid}
        )
        if not record:
            raise EducationNotFoundException()

        await db.education.delete(where={"id": education_id})
        return True


async def update_education(
    uid: str, education_id: int, update: EducationUpdate
) -> EducationOut:
    async with get_db() as db:
        record = await db.education.find_first(
            where={"id": education_id, "user_id": uid}
        )
        if not record:
            raise EducationNotFoundException()

        updated = await db.education.update(
            where={"id": education_id},
            data=update.model_dump(exclude_unset=True, exclude_none=True),
        )

        return EducationOut(
            id=updated.id,
            degree=updated.degree,
            institution=updated.institution,
            location=updated.location,
            start_date=updated.start_date,
            end_date=updated.end_date,
            gpa=updated.gpa,
            honors=updated.honors,
        )
