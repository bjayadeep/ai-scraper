import logging
from typing import Any, Dict

from db import Job, JobProfile, JobProfileMatch, SessionLocal
from src.ingestion import ingest_all_companies
from src.profiles import is_job_in_profile_window, seed_job_profiles
from src.reporting import generate_styled_excel, send_email_with_report
from src.scrapers import AshbyScraper, GreenhouseScraper, LeverScraper, PlaywrightScraper


logger = logging.getLogger(__name__)


def rate_job_relevance(job: Dict[str, Any]) -> int:
    title = job.get("title", "").lower()
    score = 0
    for keyword, points in (
        ("engineer", 15), ("developer", 15), ("analyst", 12),
        ("specialist", 10), ("consultant", 8), ("architect", 5),
    ):
        if keyword in title:
            score += points
    if any(keyword in title for keyword in ("intern", "co-op", "student")):
        score -= 20
    return score


def _job_dict(job: Job, profile: JobProfile) -> Dict[str, Any]:
    return {
        "id": job.id,
        "company": job.company,
        "title": job.title,
        "location": job.location,
        "experience_metadata": job.experience_metadata,
        "apply_link": job.apply_link,
        "date_posted": job.date_posted,
        "source_posted_at": job.source_posted_at,
        "first_seen_at": job.first_seen_at,
        "profile_slug": profile.slug,
        "profile_name": profile.name,
    }


def run_pipeline() -> bool:
    logger.info("Initializing multi-domain job platform pipeline.")
    ingestion_result = ingest_all_companies()
    if not ingestion_result["success"]:
        logger.warning("One or more companies failed during ingestion; continuing with reports.")

    db = SessionLocal()
    report_success = True
    try:
        seed_job_profiles(db)
        profiles = db.query(JobProfile).filter(JobProfile.enabled.is_(True)).order_by(JobProfile.id).all()
        for profile in profiles:
            rows = (
                db.query(Job)
                .join(JobProfileMatch, JobProfileMatch.job_id == Job.id)
                .filter(JobProfileMatch.profile_id == profile.id)
                .all()
            )
            visible_jobs = [
                _job_dict(job, profile)
                for job in rows
                if is_job_in_profile_window(
                    profile, job.source_posted_at, job.first_seen_at
                )
            ]
            visible_jobs.sort(
                key=lambda job: job.get("source_posted_at") or job.get("first_seen_at"),
                reverse=True,
            )
            final_selection = visible_jobs[:40]
            if not final_selection:
                logger.info("No visible jobs for profile %s.", profile.name)
                continue
            try:
                excel_path = generate_styled_excel(final_selection, profile)
                send_email_with_report(excel_path, final_selection, profile)
            except Exception as exc:
                report_success = False
                logger.error("Reporting failed for %s: %s", profile.name, exc, exc_info=True)
    finally:
        db.close()

    return ingestion_result["success"] and report_success


def scrape_try_all(company_name: str, token: str, careers_url: str) -> tuple:
    """Detect an ATS by trying each scraper and falling back to generic Playwright links."""
    for ats_type, scraper_class in (
        ("greenhouse", GreenhouseScraper),
        ("lever", LeverScraper),
        ("ashby", AshbyScraper),
    ):
        if not token:
            continue
        try:
            jobs = scraper_class(company_name, token, careers_url).scrape()
            if jobs:
                return ats_type, jobs
        except Exception as exc:
            logger.warning("ATS detection failed for %s via %s: %s", company_name, ats_type, exc)

    if careers_url:
        try:
            jobs = PlaywrightScraper(company_name, token, careers_url).scrape()
            if jobs:
                return "playwright", jobs
            import requests
            response = requests.get(careers_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return "playwright", []
        except Exception as exc:
            logger.warning("Playwright detection failed for %s: %s", company_name, exc)
    return None, []
