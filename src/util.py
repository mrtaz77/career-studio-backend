from datetime import date, datetime
from typing import Any


def serialize_for_json(obj: Any) -> Any:
    """
    Recursively convert date/datetime objects to ISO strings
    so they can be safely passed to json.dumps.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize_for_json(value) for key, value in obj.items()}
    else:
        return obj


def to_datetime(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time())
