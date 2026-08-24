"""
Timezone-aware Date & Time Utilities (Africa/Lagos UTC+1 & UTC).
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import dateutil.parser


# Africa/Lagos is strictly UTC+1 all year (no daylight saving time)
LAGOS_TZ = timezone(timedelta(hours=1))
UTC_TZ = timezone.utc


def get_utc_now() -> datetime:
    """Returns current datetime in UTC."""
    return datetime.now(UTC_TZ)


def get_lagos_now() -> datetime:
    """Returns current datetime in Africa/Lagos (UTC+1)."""
    return datetime.now(LAGOS_TZ)


def to_iso_string(dt: Optional[datetime] = None) -> str:
    """Formats datetime to ISO 8601 string."""
    if dt is None:
        dt = get_utc_now()
    return dt.isoformat()


def parse_date(date_val: Optional[Union[str, datetime]]) -> Optional[datetime]:
    """Parses various date string formats into a timezone-aware UTC datetime."""
    if date_val is None:
        return None
    if isinstance(date_val, datetime):
        if date_val.tzinfo is None:
            return date_val.replace(tzinfo=UTC_TZ)
        return date_val.astimezone(UTC_TZ)

    date_str = str(date_val).strip()
    if not date_str or date_str.lower() in ["none", "n/a", "unknown"]:
        return None

    try:
        dt = dateutil.parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC_TZ)
        return dt.astimezone(UTC_TZ)
    except Exception:
        return None


def days_since(date_val: Optional[Union[str, datetime]]) -> int:
    """Calculates integer days elapsed since the given date relative to UTC now."""
    dt = parse_date(date_val)
    if dt is None:
        return 999  # Default to older if date cannot be parsed

    now = get_utc_now()
    diff = (now - dt).total_seconds()
    if diff < 0:
        return 0  # Future dates (events) have 0 days elapsed
    return int(diff // 86400)


def get_week_number(dt: Optional[datetime] = None) -> int:
    """Returns the ISO week number (1-52)."""
    if dt is None:
        dt = get_lagos_now()
    return dt.isocalendar()[1]


def format_lagos_time(dt: Optional[Union[str, datetime]] = None, format_str: str = "%A, %d %B %Y | %I:%M %p WAT") -> str:
    """Formats datetime in Africa/Lagos (West Africa Time - WAT)."""
    if dt is None:
        parsed_dt = get_lagos_now()
    elif isinstance(dt, str):
        parsed = parse_date(dt)
        parsed_dt = parsed.astimezone(LAGOS_TZ) if parsed else get_lagos_now()
    else:
        if dt.tzinfo is None:
            parsed_dt = dt.replace(tzinfo=LAGOS_TZ)
        else:
            parsed_dt = dt.astimezone(LAGOS_TZ)

    return parsed_dt.strftime(format_str)
