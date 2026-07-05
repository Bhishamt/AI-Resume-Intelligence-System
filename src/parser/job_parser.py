"""
Job description parser with Playwright-based dynamic rendering.

Supports
────────
  - Raw text parsing (paste-in)
  - URL scraping via headless Chromium with anti-bot headers
  - Platform-specific selectors for LinkedIn, Naukri, Indeed,
    Wellfound, and generic career pages
"""

import re
from bs4 import BeautifulSoup


class JobParser:
    """Parses job descriptions from raw text or live URLs."""

    # Platform-specific CSS selectors for cleaner extraction
    PLATFORM_SELECTORS: dict[str, list[str]] = {
        "linkedin.com": [
            ".description__text",
            ".show-more-less-html",
            ".jobs-description__content",
        ],
        "naukri.com": [
            ".job-desc",
            ".jd-container",
            ".styles_JDC__dang-inner-html__h0K4t",
        ],
        "indeed.com": [
            "#jobDescriptionText",
            ".jobsearch-jobDescriptionText",
        ],
        "wellfound.com": [
            ".job-description",
            "[class*='description']",
        ],
    }

    # ── Raw-text parsing ─────────────────────────────────────────────

    @staticmethod
    def parse_raw_text(text: str) -> dict:
        """Extracts title and company from plain-text job descriptions."""
        lines  = text.strip().split("\n")
        title   = "Target Position"
        company = "Target Company"

        for line in lines[:15]:
            lo = line.lower().strip()
            if any(k in lo for k in ("role:", "title:", "position:")):
                title = line.split(":", 1)[-1].strip() or title
            if "company:" in lo:
                company = line.split(":", 1)[-1].strip() or company

        return {
            "title":    title,
            "company":  company,
            "raw_text": text.strip(),
        }

    # ── URL scraping ─────────────────────────────────────────────────

    @classmethod
    def parse_url(cls, url: str) -> dict:
        """
        Scrapes a job posting URL using a Playwright headless browser.

        Falls back to the full-page text if no platform-specific
        selector matches.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "error": (
                    "Playwright is not installed.  Run:\n"
                    "  pip install playwright && playwright install"
                ),
                "raw_text": "",
            }

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/126.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": (
                            "text/html,application/xhtml+xml,"
                            "application/xml;q=0.9,*/*;q=0.8"
                        ),
                        "DNT": "1",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-Mode": "navigate",
                    },
                )
                page = context.new_page()

                # Navigate — domcontentloaded is faster & safer than
                # networkidle on heavy pages
                page.goto(url, wait_until="domcontentloaded", timeout=30_000)

                # Extra wait for JS-rendered content
                page.wait_for_timeout(3_000)

                # Try platform-specific selectors first
                extracted = cls._try_platform_selectors(page, url)

                # Fallback: full-page text extraction
                if not extracted:
                    extracted = cls._extract_full_page(page)

                browser.close()

            # Clean up whitespace
            extracted = re.sub(r"\n{3,}", "\n\n", extracted)
            extracted = re.sub(r"[ \t]{4,}", "   ", extracted)

            return cls.parse_raw_text(extracted.strip())

        except Exception as exc:
            return {
                "error": f"Scraping failed: {exc}",
                "raw_text": "",
            }

    # ── Private helpers ──────────────────────────────────────────────

    @classmethod
    def _try_platform_selectors(cls, page, url: str) -> str:
        """Attempts to extract text using platform-aware CSS selectors."""
        url_lower = url.lower()
        for domain, selectors in cls.PLATFORM_SELECTORS.items():
            if domain not in url_lower:
                continue
            for selector in selectors:
                try:
                    el = page.query_selector(selector)
                    if el:
                        text = el.inner_text()
                        if len(text.strip()) > 50:
                            return text
                except Exception:
                    continue
        return ""

    @staticmethod
    def _extract_full_page(page) -> str:
        """Fallback: grabs full page HTML, strips boilerplate."""
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Remove non-content elements
        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "noscript"]
        ):
            tag.decompose()

        return soup.get_text(separator="\n")
