
import json
import re
from pathlib import Path

import pandas as pd

from skills_config import ROLE_PATTERNS, SENIORITY_PATTERNS, SKILL_PATTERNS

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")

# Pre-compile everything once
COMPILED_SKILLS = {
    skill: [re.compile(p, re.IGNORECASE) for p in patterns]
    for skill, patterns in SKILL_PATTERNS.items()
}
COMPILED_SENIORITY = [(label, re.compile(p, re.IGNORECASE)) for label, p in SENIORITY_PATTERNS]
COMPILED_ROLES = [(label, re.compile(p, re.IGNORECASE)) for label, p in ROLE_PATTERNS]


def detect_skills(text: str) -> list[str]:
    return [skill for skill, pats in COMPILED_SKILLS.items()
            if any(p.search(text) for p in pats)]


def classify_seniority(title: str, description: str) -> str:
    for label, pat in COMPILED_SENIORITY:
        if pat.search(title):
            return label
    # Fall back to years-of-experience mentions in the description
    m = re.search(r"(\d+)\s*(?:\+|-\s*\d+)?\s*years?", description, re.IGNORECASE)
    if m:
        years = int(m.group(1))
        if years >= 7:
            return "Lead/Manager+"
        if years >= 4:
            return "Senior"
        if years <= 1:
            return "Junior/Entry"
    return "Mid"


def classify_role(title: str) -> str:
    for label, pat in COMPILED_ROLES:
        if pat.search(title):
            return label
    return "Other Data Role"


def normalize(job: dict) -> dict:
    """Map JSearch and Bayt fields onto one schema."""
    return {
        "title": job.get("job_title", "") or "",
        "company": job.get("employer_name", job.get("company", "")) or "",
        "city": job.get("job_city", "") or "",
        "posted_at": job.get("job_posted_at_datetime_utc", "") or "",
        "url": job.get("job_apply_link", "") or "",
        "description": job.get("job_description", "") or "",
        "source": job.get("source", "jsearch"),
    }


def main() -> None:
    raw_files = sorted(RAW_DIR.glob("*.json"))
    if not raw_files:
        raise SystemExit("No raw files found. Run collect_jsearch.py or scrape_bayt.py first.")

    rows, seen = [], set()
    for f in raw_files:
        for job in json.loads(f.read_text()):
            rec = normalize(job)
            key = (rec["title"].lower(), rec["company"].lower())
            if not rec["description"] or key in seen:
                continue
            seen.add(key)

            full_text = f"{rec['title']}\n{rec['description']}"
            rec["skills"] = detect_skills(full_text)
            rec["n_skills"] = len(rec["skills"])
            rec["seniority"] = classify_seniority(rec["title"], rec["description"])
            rec["role_family"] = classify_role(rec["title"])
            # skip SEO aggregator pages and postings with no detectable skills
            if rec["n_skills"] == 0 or re.search(r"\bjobs?\s+in\s+\w+", rec["title"], re.IGNORECASE):
                continue
            rows.append(rec)

    df = pd.DataFrame(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    jobs_df = df.drop(columns=["description"]).copy()
    jobs_df["skills"] = jobs_df["skills"].apply("|".join)
    jobs_df.to_csv(OUT_DIR / "jobs.csv", index=False)

    long_df = df[["title", "company", "seniority", "role_family", "skills"]].explode("skills").dropna(subset=["skills"])
    long_df.to_csv(OUT_DIR / "job_skills.csv", index=False)

    print(f"Parsed {len(df)} unique jobs from {len(raw_files)} raw file(s)")
    print(f"  -> {OUT_DIR/'jobs.csv'}")
    print(f"  -> {OUT_DIR/'job_skills.csv'}")
    print("\nSeniority breakdown:")
    print(df["seniority"].value_counts().to_string())
    print("\nRole family breakdown:")
    print(df["role_family"].value_counts().to_string())


if __name__ == "__main__":
    main()
