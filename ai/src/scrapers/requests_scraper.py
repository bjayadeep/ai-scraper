import logging
from typing import List, Dict, Any
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

SECURITY_KEYWORDS = ["security", "cyber", "information security", "secops", "infosec", "penetration", "compliance"]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class RequestsScraper(BaseScraper):
    """
    Lightweight fallback for custom careers pages: plain HTTP GET + HTML parsing,
    no browser. Much cheaper than PlaywrightScraper, but only works on
    server-rendered pages. Returns [] (not an error) if the page requires
    JS rendering to reveal its links, so callers can fall back to Playwright.
    """

    def scrape(self) -> List[Dict[str, Any]]:
        jobs_list = []
        logger.info(f"Fetching {self.company_name} careers page via plain HTTP: {self.careers_url}")

        resp = requests.get(
            self.careers_url,
            headers={"User-Agent": USER_AGENT},
            timeout=15,
            allow_redirects=True,
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        parsed_url = urlparse(self.careers_url)

        for link in soup.find_all("a"):
            href = link.get("href")
            text = link.get_text(strip=True)

            if not href or not text:
                continue

            if href.startswith("/"):
                href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
            elif not href.startswith("http"):
                continue

            text_lower = text.lower()
            if any(kw in text_lower for kw in SECURITY_KEYWORDS):
                jobs_list.append({
                    "company": self.company_name,
                    "title": text,
                    "location": "USA (Verify)",
                    "apply_link": href,
                    "description": f"Scraped link text: {text}. See career page for full details.",
                    "date_posted": ""
                })

        logger.info(f"Successfully scraped {len(jobs_list)} potential jobs for {self.company_name} via plain HTTP.")
        return jobs_list
