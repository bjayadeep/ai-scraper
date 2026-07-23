import logging
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

class PlaywrightScraper(BaseScraper):
    def scrape(self) -> List[Dict[str, Any]]:
        jobs_list = []
        # Playwright scraper fallback for custom sites
        logger.info(f"Launching Playwright scraper fallback for {self.company_name} at URL: {self.careers_url}")
        
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("playwright package is not installed. Skipping Playwright scraper.")
            return []
            
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Create a page with standard user agent to avoid bot blocks
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(self.careers_url, wait_until="networkidle", timeout=30000)
                
                # Collect generic job-detail links. Profile classification happens later.
                links = page.query_selector_all("a")
                seen_urls = set()
                
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        text = link.inner_text().strip()
                        
                        if not href or not text:
                            continue
                            
                        href = urljoin(self.careers_url, href)
                        if urlparse(href).scheme not in ("http", "https"):
                            continue
                        normalized_url = href.split("#", 1)[0]
                        if normalized_url in seen_urls:
                            continue

                        href_lower = normalized_url.lower()
                        job_path_markers = (
                            "/job/", "/jobs/", "/position/", "/positions/", "/opening/",
                            "/openings/", "/posting/", "/postings/", "jobid=", "job_id=",
                        )
                        generic_labels = {"jobs", "careers", "open positions", "view jobs", "search jobs"}
                        looks_like_job = any(marker in href_lower for marker in job_path_markers)
                        if looks_like_job and text.lower() not in generic_labels:
                            seen_urls.add(normalized_url)
                            jobs_list.append({
                                "company": self.company_name,
                                "title": text,
                                "location": "USA (Verify)",  # Browser extraction fallback
                                "apply_link": normalized_url,
                                "description": f"Scraped link text: {text}. See career page for full details.",
                                "date_posted": "",
                                "source_posted_at": None,
                                "source_updated_at": None,
                            })
                    except Exception:
                        continue
                        
                browser.close()
                logger.info(f"Successfully scraped {len(jobs_list)} potential jobs for {self.company_name} using Playwright.")
        except Exception as e:
            logger.error(f"Error scraping with Playwright for {self.company_name}: {str(e)}", exc_info=True)
            
        return jobs_list
