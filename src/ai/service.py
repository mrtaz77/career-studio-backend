from datetime import datetime
from logging import getLogger

from groq import Groq

from src.ai.constants import AI_USAGE_LIMIT, MODEL, REQUEST_LENGTH_LIMIT, SYSTEM_PROMPT
from src.ai.exceptions import RequestLengthExceeded, RequestLimitExceeded
from src.config import settings
from src.database import get_db

logger = getLogger(__name__)


async def check_and_update_request_limit(user_id: str) -> None:
    async with get_db() as db:
        now = datetime.now()
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
            init_month = ai_request.init_request_at.month
            init_year = ai_request.init_request_at.year
            now_month = now.month
            now_year = now.year

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


async def optimize_text(user_id: str, description: str) -> str:
    if len(description) > REQUEST_LENGTH_LIMIT:
        raise RequestLengthExceeded()
    await check_and_update_request_limit(user_id)

    client = Groq(api_key=settings.GROQ_API_KEY)
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
