from typing import Any, Dict

from src.ingestion import ingest_company

def scrape_single_company(company_id: int, user_id: int = None) -> Dict[str, Any]:
    """
    Triggers the scraper for a single company, runs it through the filter pipeline,
    saves new matching jobs to PostgreSQL, and logs the activity.
    """
    return ingest_company(company_id, user_id=user_id)
