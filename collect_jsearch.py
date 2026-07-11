
import json
import os
import time
from datetime import date
from pathlib import Path

import requests

from skills_config import SEARCH_QUERIES

API_URL = "https://jsearch.p.rapidapi.com/search-v2"
RAW_DIR = Path("data/raw")
PAGES_PER_QUERY = 3          # cursor hops per query; free tier = 200 req/month
REQUEST_DELAY_S = 1.5


def fetch_page(session: requests.Session, query: str, cursor: str | None) -> dict:
    params = {
        "query": f"{query} in Saudi Arabia",
        "country": "sa",
        "language": "en",         # avoid Arabic-default descriptions
        "date_posted": "month",   # use "all" later for more volume
    }
    if cursor:
        params["cursor"] = cursor
    resp = session.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_jobs(payload: dict) -> list[dict]:
    """Jobs live under data['jobs'] in v5; tolerate older list shape too."""
    data = payload.get("data")
    if isinstance(data, dict):
        return data.get("jobs", []) or []
    if isinstance(data, list):
        return [j for j in data if isinstance(j, dict)]
    return []


def find_cursor(payload: dict) -> str | None:
    """Look for the next-page cursor in the places JSearch might put it."""
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    for container in (data, payload, payload.get("parameters") or {}):
        for key in ("cursor", "next_cursor", "next_page_cursor"):
            val = container.get(key)
            if val:
                return val
    return None


def main() -> None:
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        raise SystemExit("Set RAPIDAPI_KEY first: export RAPIDAPI_KEY='...'")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    })

    all_jobs, seen_ids = [], set()
    for query in SEARCH_QUERIES:
        cursor = None
        for hop in range(1, PAGES_PER_QUERY + 1):
            try:
                payload = fetch_page(session, query, cursor)
            except requests.HTTPError as exc:
                print(f"[warn] {query!r} hop {hop}: {exc}")
                break

            jobs = extract_jobs(payload)
            if not jobs:
                print(f"[info] {query!r} hop {hop}: no results")
                break

            new = 0
            for job in jobs:
                jid = job.get("job_id")
                if jid and jid not in seen_ids:
                    seen_ids.add(jid)
                    job["_search_query"] = query
                    all_jobs.append(job)
                    new += 1
            print(f"[ok] {query!r} hop {hop}: {new} new jobs (total {len(all_jobs)})")

            cursor = find_cursor(payload)
            if not cursor:
                break
            time.sleep(REQUEST_DELAY_S)

    out = RAW_DIR / f"jsearch_{date.today().isoformat()}.json"
    out.write_text(json.dumps(all_jobs, ensure_ascii=False, indent=2))
    print(f"\nSaved {len(all_jobs)} unique postings -> {out}")


if __name__ == "__main__":
    main()