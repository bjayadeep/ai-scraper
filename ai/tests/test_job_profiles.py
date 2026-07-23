import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base, Company, Job, JobProfileMatch
from src import ingestion
from src.filters.parser import filter_job
from src.profiles import is_job_in_profile_window, matches_profile_title


CYBERSECURITY = {
    "slug": "cybersecurity",
    "name": "Cybersecurity",
    "window_type": "rolling_24h",
    "timezone": "America/New_York",
}
JAVA = {
    "slug": "java-developer",
    "name": "Java Developer",
    "window_type": "calendar_day",
    "timezone": "America/New_York",
}
DOTNET = {
    "slug": "dotnet-developer",
    "name": ".NET Developer",
    "window_type": "calendar_day",
    "timezone": "America/New_York",
}


def job(title: str):
    return {
        "company": "Example",
        "title": title,
        "location": "New York, NY",
        "description": "This role requires 3 years of relevant experience.",
        "apply_link": "https://example.com/jobs/1",
    }


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Java Software Developer", True),
        ("JavaScript Developer", False),
        ("Senior JavaScript Engineer", False),
        ("Java / JavaScript Developer", True),
    ],
)
def test_java_does_not_confuse_javascript(title, expected):
    assert matches_profile_title(title, JAVA)[0] is expected


@pytest.mark.parametrize("title", [".NET Developer", "Dotnet Software Engineer", "C# Developer"])
def test_dotnet_and_csharp_classification(title):
    matched, _, _ = filter_job(job(title), DOTNET)
    assert matched is True


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Cloud Security Engineer", True),
        ("SOC Analyst", True),
        ("Physical Security Guard", False),
        ("Software Engineer", False),
    ],
)
def test_cybersecurity_classification(title, expected):
    matched, _, _ = filter_job(job(title), CYBERSECURITY)
    assert matched is expected


def test_rolling_24_hour_filtering_uses_posted_or_first_seen():
    now = datetime.datetime(2026, 7, 23, 16, 0, tzinfo=datetime.timezone.utc)
    assert is_job_in_profile_window(
        CYBERSECURITY,
        source_posted_at=now - datetime.timedelta(hours=23, minutes=59),
        first_seen_at=now - datetime.timedelta(days=2),
        now=now,
    )
    assert is_job_in_profile_window(
        CYBERSECURITY,
        source_posted_at=now - datetime.timedelta(days=2),
        first_seen_at=now - datetime.timedelta(hours=1),
        now=now,
    )
    assert not is_job_in_profile_window(
        CYBERSECURITY,
        source_posted_at=now - datetime.timedelta(hours=24, seconds=1),
        first_seen_at=now - datetime.timedelta(days=3),
        now=now,
    )


def test_calendar_day_filtering_uses_new_york_day_and_either_timestamp():
    now = datetime.datetime(2026, 7, 23, 16, 0, tzinfo=datetime.timezone.utc)
    before_new_york_midnight = datetime.datetime(2026, 7, 23, 3, 59, tzinfo=datetime.timezone.utc)
    after_new_york_midnight = datetime.datetime(2026, 7, 23, 4, 1, tzinfo=datetime.timezone.utc)

    assert is_job_in_profile_window(JAVA, before_new_york_midnight, after_new_york_midnight, now)
    assert is_job_in_profile_window(JAVA, after_new_york_midnight, before_new_york_midnight, now)
    assert not is_job_in_profile_window(JAVA, before_new_york_midnight, before_new_york_midnight, now)


def test_company_is_scraped_once_and_classified_against_all_profiles(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    company = Company(name="Example", ats="playwright", careers_url="https://example.com/careers")
    session.add(company)
    session.commit()

    calls = {"count": 0}

    class FakeScraper:
        def scrape(self):
            calls["count"] += 1
            return [
                {**job("Java Software Developer"), "apply_link": "https://example.com/jobs/java"},
                {**job("Cloud Security Engineer"), "apply_link": "https://example.com/jobs/security"},
            ]

    monkeypatch.setattr(ingestion, "build_scraper", lambda _: FakeScraper())
    result = ingestion.ingest_company(company.id, session=session)

    matched_slugs = {
        match.profile.slug
        for match in session.query(JobProfileMatch).all()
    }
    assert result["success"] is True
    assert calls["count"] == 1
    assert session.query(Job).count() == 2
    assert matched_slugs == {"java-developer", "cybersecurity"}
