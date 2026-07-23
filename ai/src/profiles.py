import datetime
import re
from typing import Any, Dict, Iterable, Tuple
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = "America/New_York"
ROLLING_24_HOURS = "rolling_24h"
CALENDAR_DAY = "calendar_day"

PROFILE_DEFINITIONS = (
    {
        "slug": "cybersecurity",
        "name": "Cybersecurity",
        "description": "US cybersecurity roles from the rolling previous 24 hours.",
        "window_type": ROLLING_24_HOURS,
    },
    {
        "slug": "java-developer",
        "name": "Java Developer",
        "description": "US Java developer roles posted or first discovered today in America/New_York.",
        "window_type": CALENDAR_DAY,
    },
    {
        "slug": "dotnet-developer",
        "name": ".NET Developer",
        "description": "US .NET and C# developer roles posted or first discovered today in America/New_York.",
        "window_type": CALENDAR_DAY,
    },
)

CYBER_PATTERNS = (
    r"\bsecurity\b", r"\bcyber(?:security)?\b", r"\binfosec\b", r"\bsecops\b",
    r"\bsoc\b", r"\bpentest\b", r"\bpenetration\b", r"\bvulnerability\b",
    r"\biam\b", r"\bgrc\b", r"\bthreat\b", r"\bincident response\b",
    r"\bsiem\b", r"\bcryptograph(?:y|ic)\b", r"\bdevsecops\b",
)
CYBER_EXCLUSIONS = (
    r"\bsecurities\b", r"\bphysical security\b", r"\bsecurity guard\b",
    r"\bloss prevention\b", r"\bfood security\b", r"\bhome security\b",
)
DEVELOPER_ROLE_PATTERN = re.compile(
    r"\b(developer|engineer|architect|programmer|consultant|specialist)\b", re.IGNORECASE
)
JAVA_PATTERN = re.compile(r"(?<![A-Za-z0-9])java(?![A-Za-z0-9])", re.IGNORECASE)
DOTNET_PATTERN = re.compile(r"(?<!\w)\.net\b|\bdotnet\b|(?<!\w)c#(?!\w)", re.IGNORECASE)


def profile_value(profile: Any, key: str, default: Any = None) -> Any:
    if isinstance(profile, dict):
        return profile.get(key, default)
    return getattr(profile, key, default)


def matches_profile_title(title: str, profile: Any) -> Tuple[bool, str]:
    slug = profile_value(profile, "slug")
    normalized_title = title.strip()
    if slug == "cybersecurity":
        if any(re.search(pattern, normalized_title, re.IGNORECASE) for pattern in CYBER_EXCLUSIONS):
            return False, "Excluded non-cybersecurity use of security"
        if any(re.search(pattern, normalized_title, re.IGNORECASE) for pattern in CYBER_PATTERNS):
            return True, "Cybersecurity title keyword matched"
        return False, "Title is not a cybersecurity role"

    if slug == "java-developer":
        if not JAVA_PATTERN.search(normalized_title):
            return False, "Title does not contain the Java language keyword"
        if not DEVELOPER_ROLE_PATTERN.search(normalized_title):
            return False, "Java title is not a developer role"
        return True, "Java developer title matched"

    if slug == "dotnet-developer":
        if not DOTNET_PATTERN.search(normalized_title):
            return False, "Title does not contain .NET, dotnet, or C#"
        if not DEVELOPER_ROLE_PATTERN.search(normalized_title):
            return False, ".NET/C# title is not a developer role"
        return True, ".NET/C# developer title matched"

    return False, f"Unsupported job profile: {slug}"


def ensure_aware_utc(value: datetime.datetime | None) -> datetime.datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc)


def profile_window_bounds(profile: Any, now: datetime.datetime | None = None) -> Tuple[datetime.datetime, datetime.datetime]:
    now_utc = ensure_aware_utc(now) or datetime.datetime.now(datetime.timezone.utc)
    window_type = profile_value(profile, "window_type")
    timezone_name = profile_value(profile, "timezone", DEFAULT_TIMEZONE)
    if window_type == ROLLING_24_HOURS:
        return now_utc - datetime.timedelta(hours=24), now_utc
    if window_type == CALENDAR_DAY:
        local_timezone = ZoneInfo(timezone_name)
        local_now = now_utc.astimezone(local_timezone)
        local_start = datetime.datetime.combine(local_now.date(), datetime.time.min, tzinfo=local_timezone)
        return local_start.astimezone(datetime.timezone.utc), now_utc
    raise ValueError(f"Unsupported profile window type: {window_type}")


def is_job_in_profile_window(
    profile: Any,
    source_posted_at: datetime.datetime | None,
    first_seen_at: datetime.datetime | None,
    now: datetime.datetime | None = None,
) -> bool:
    start, end = profile_window_bounds(profile, now)
    candidates: Iterable[datetime.datetime | None] = (source_posted_at, first_seen_at)
    return any(start <= timestamp <= end for value in candidates if (timestamp := ensure_aware_utc(value)))


def seed_job_profiles(session) -> None:
    from db import JobProfile

    for definition in PROFILE_DEFINITIONS:
        profile = session.query(JobProfile).filter(JobProfile.slug == definition["slug"]).first()
        if profile is None:
            profile = JobProfile(timezone=DEFAULT_TIMEZONE, enabled=True, **definition)
            session.add(profile)
        else:
            profile.name = definition["name"]
            profile.description = definition["description"]
            profile.window_type = definition["window_type"]
    session.commit()
