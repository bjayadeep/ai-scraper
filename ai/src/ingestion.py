import datetime
import logging
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

from config import settings
from db import ActivityLog, Company, Job, JobProfile, JobProfileMatch, SessionLocal
from src.filters import filter_job, verify_job_with_ai
from src.profiles import seed_job_profiles
from src.scrapers import AshbyScraper, GreenhouseScraper, LeverScraper, PlaywrightScraper


logger = logging.getLogger(__name__)


def parse_source_datetime(value: Any) -> Optional[datetime.datetime]:
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        parsed = value
    elif isinstance(value, datetime.date):
        parsed = datetime.datetime.combine(value, datetime.time.min)
    else:
        text = str(value).strip().replace("Z", "+00:00")
        try:
            parsed = datetime.datetime.fromisoformat(text)
        except ValueError:
            try:
                parsed = datetime.datetime.strptime(text[:10], "%Y-%m-%d")
            except ValueError:
                return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def build_scraper(company: Company):
    scraper_types = {
        "greenhouse": GreenhouseScraper,
        "lever": LeverScraper,
        "ashby": AshbyScraper,
        "playwright": PlaywrightScraper,
    }
    scraper_class = scraper_types.get(company.ats, PlaywrightScraper)
    return scraper_class(company.name, company.token, company.careers_url)


def _profile_result(profile: JobProfile, job: Dict[str, Any]) -> tuple[bool, str, Dict[str, Any]]:
    is_match, reason, enriched_job = filter_job(job, profile)
    if not is_match:
        return False, reason, enriched_job
    if settings.USE_AI_FILTER and settings.CLAUDE_API_KEY:
        ai_match, ai_reason = verify_job_with_ai(enriched_job, profile)
        if not ai_match:
            return False, ai_reason, enriched_job
        enriched_job["experience_metadata"] = (
            f"{enriched_job.get('experience_metadata', '')} | {ai_reason}"
        ).strip(" |")
        reason = f"{reason}; {ai_reason}"
    return True, reason, enriched_job


def ingest_company(company_id: int, user_id: int | None = None, session=None) -> Dict[str, Any]:
    owns_session = session is None
    db = session or SessionLocal()
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        seed_job_profiles(db)
        company = db.query(Company).filter(Company.id == company_id).first()
        if company is None:
            return {"success": False, "error": f"Company ID {company_id} not found."}

        raw_jobs = build_scraper(company).scrape()
        profiles = db.query(JobProfile).filter(JobProfile.enabled.is_(True)).all()
        stats = defaultdict(int)
        jobs_added: List[Dict[str, Any]] = []

        for raw_job in raw_jobs:
            apply_link = raw_job.get("apply_link", "").strip()
            title = raw_job.get("title", "").strip()
            if not apply_link or not title:
                stats["invalid"] += 1
                continue

            raw_job["company"] = company.name
            source_posted_at = parse_source_datetime(raw_job.get("source_posted_at"))
            source_updated_at = parse_source_datetime(raw_job.get("source_updated_at"))
            matches = []
            enriched_by_profile = {}
            for profile in profiles:
                is_match, reason, enriched_job = _profile_result(profile, raw_job)
                if is_match:
                    matches.append((profile, reason))
                    enriched_by_profile[profile.slug] = enriched_job

            job = db.query(Job).filter(Job.apply_link == apply_link).first()
            if job is None and not matches:
                stats["filtered"] += 1
                continue

            if job is None:
                representative = enriched_by_profile[matches[0][0].slug]
                job = Job(
                    company=company.name,
                    title=title,
                    location=raw_job.get("location"),
                    experience_metadata=representative.get("experience_metadata"),
                    apply_link=apply_link,
                    date_posted=raw_job.get("date_posted") or (
                        source_posted_at.date().isoformat() if source_posted_at else now.date().isoformat()
                    ),
                    scraped_at=now.replace(tzinfo=None),
                    source_posted_at=source_posted_at,
                    source_updated_at=source_updated_at,
                    first_seen_at=now,
                    last_seen_at=now,
                )
                db.add(job)
                db.flush()
                stats["new_jobs"] += 1
                jobs_added.append({"title": title, "location": job.location, "link": apply_link})
            else:
                job.last_seen_at = now
                job.scraped_at = now.replace(tzinfo=None)
                job.title = title
                job.location = raw_job.get("location") or job.location
                if source_posted_at:
                    job.source_posted_at = source_posted_at
                    job.date_posted = source_posted_at.date().isoformat()
                if source_updated_at:
                    job.source_updated_at = source_updated_at
                stats["seen_jobs"] += 1

            existing_profile_ids = {match.profile_id for match in job.profile_matches}
            for profile, reason in matches:
                if profile.id not in existing_profile_ids:
                    db.add(JobProfileMatch(
                        job_id=job.id,
                        profile_id=profile.id,
                        classification_reason=reason,
                        matched_at=now,
                    ))
                    stats["new_matches"] += 1
                existing_profile_ids.add(profile.id)

        details = (
            f"Scrape run for {company.name}: {len(raw_jobs)} collected, "
            f"{stats['new_jobs']} jobs added, {stats['new_matches']} profile matches added, "
            f"{stats['filtered']} unmatched jobs skipped."
        )
        db.add(ActivityLog(
            user_id=user_id,
            action="SCRAPE_RUN",
            details=details,
            created_at=now.replace(tzinfo=None),
        ))
        db.commit()
        return {
            "success": True,
            "raw_scraped": len(raw_jobs),
            "new_jobs_added": stats["new_jobs"],
            "new_profile_matches": stats["new_matches"],
            "skipped_filtered": stats["filtered"],
            "jobs": jobs_added,
            "log": details,
        }
    except Exception as exc:
        db.rollback()
        logger.error("Company ingestion failed for ID %s: %s", company_id, exc, exc_info=True)
        try:
            db.add(ActivityLog(
                user_id=user_id,
                action="SCRAPE_FAIL",
                details=f"Scrape run for company ID {company_id} failed: {exc}",
            ))
            db.commit()
        except Exception:
            db.rollback()
        return {"success": False, "error": str(exc)}
    finally:
        if owns_session:
            db.close()


def ingest_all_companies(user_id: int | None = None, company_ids: Iterable[int] | None = None) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        query = db.query(Company).order_by(Company.name)
        if company_ids is not None:
            query = query.filter(Company.id.in_(list(company_ids)))
        ids = [company.id for company in query.all()]
    finally:
        db.close()

    results = [ingest_company(company_id, user_id=user_id) for company_id in ids]
    return {
        "success": all(result.get("success") for result in results),
        "companies_scraped": len(results),
        "new_jobs_added": sum(result.get("new_jobs_added", 0) for result in results),
        "new_profile_matches": sum(result.get("new_profile_matches", 0) for result in results),
        "results": results,
    }
