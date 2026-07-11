import json
import random
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = "https://www.bayt.com"
SEARCH_SLUGS = [
    "/en/saudi-arabia/jobs/data-analyst-jobs/",
    "/en/saudi-arabia/jobs/data-scientist-jobs/",
    "/en/saudi-arabia/jobs/data-engineer-jobs/",
    "/en/saudi-arabia/jobs/business-intelligence-jobs/",
]
MAX_PAGES = 3
RAW_DIR = Path("data/raw")

# Update these two if Bayt changes its markup:
JOB_CARD_SELECTOR = "li[data-js-job] h2 a, div.jb-title a, h2.jb-title a"
DESCRIPTION_SELECTOR = "div.card-content, div[class*='jb-descr'], article"


def polite_sleep():
    time.sleep(random.uniform(2.5, 5.0))


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/126.0 Safari/537.36"),
            locale="en-US",
        )

        job_links = set()
        for slug in SEARCH_SLUGS:
            for pnum in range(1, MAX_PAGES + 1):
                url = urljoin(BASE, slug) + (f"?page={pnum}" if pnum > 1 else "")
                print(f"[list] {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                polite_sleep()
                anchors = page.query_selector_all(JOB_CARD_SELECTOR)
                if not anchors:
                    print("  [warn] no job cards found — selectors may need updating")
                    break
                for a in anchors:
                    href = a.get_attribute("href")
                    title = (a.inner_text() or "").strip()
                    if href:
                        job_links.add((title, urljoin(BASE, href)))
                print(f"  found {len(anchors)} cards (total unique: {len(job_links)})")

        print(f"\nFetching {len(job_links)} job descriptions...")
        for i, (title, link) in enumerate(sorted(job_links), 1):
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=45000)
                polite_sleep()
                desc_el = page.query_selector(DESCRIPTION_SELECTOR)
                description = desc_el.inner_text().strip() if desc_el else ""
                jobs.append({
                    "job_title": title,
                    "job_apply_link": link,
                    "job_description": description,
                    "job_country": "SA",
                    "source": "bayt",
                })
                print(f"  [{i}/{len(job_links)}] {title[:60]}")
            except Exception as exc:  # keep going on individual failures
                print(f"  [skip] {link}: {exc}")

        browser.close()

    out = RAW_DIR / f"bayt_{date.today().isoformat()}.json"
    out.write_text(json.dumps(jobs, ensure_ascii=False, indent=2))
    print(f"\nSaved {len(jobs)} postings -> {out}")


if __name__ == "__main__":
    main()
