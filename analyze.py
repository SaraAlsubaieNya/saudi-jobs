
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PROCESSED = Path("data/processed")
FIG_DIR = Path("figures")
TOP_N = 15


def top_skills(long_df: pd.DataFrame, n_jobs: int) -> pd.Series:
    counts = long_df["skills"].value_counts().head(TOP_N)
    pct = (counts / n_jobs * 100).round(1)

    fig, ax = plt.subplots(figsize=(9, 6))
    pct.sort_values().plot.barh(ax=ax, color="#2a9d8f")
    ax.set_xlabel("% of Saudi data-role postings mentioning the skill")
    ax.set_title(f"Most in-demand skills — Saudi data roles (n={n_jobs} postings)")
    for i, v in enumerate(pct.sort_values()):
        ax.text(v + 0.5, i, f"{v}%", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "top_skills.png", dpi=200)
    plt.close(fig)
    return counts


def skills_by_seniority(long_df: pd.DataFrame, top: pd.Series) -> None:
    sub = long_df[long_df["skills"].isin(top.index)]
    pivot = pd.crosstab(sub["skills"], sub["seniority"], normalize="columns") * 100
    order = ["Junior/Entry", "Mid", "Senior", "Lead/Manager+"]
    pivot = pivot[[c for c in order if c in pivot.columns]].loc[top.index]

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(pivot.values, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=20)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.iat[i, j]:.0f}", ha="center", va="center", fontsize=8)
    ax.set_title("Skill demand by seniority (% of mentions within each level)")
    fig.colorbar(im, ax=ax, shrink=0.7)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "skills_by_seniority.png", dpi=200)
    plt.close(fig)


def cooccurrence(jobs_df: pd.DataFrame, top: pd.Series) -> None:
    skills = top.index.tolist()
    sets = jobs_df["skills"].fillna("").str.split("|").apply(lambda x: {s for s in x if s})
    mat = pd.DataFrame(0, index=skills, columns=skills, dtype=int)
    for s in sets:
        present = [k for k in skills if k in s]
        for a in present:
            for b in present:
                mat.loc[a, b] += 1

    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(mat.values, cmap="OrRd")
    ax.set_xticks(range(len(skills)), skills, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(skills)), skills, fontsize=8)
    ax.set_title("Skill co-occurrence — how often two skills appear in the same posting")
    fig.colorbar(im, ax=ax, shrink=0.7)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "skill_cooccurrence.png", dpi=200)
    plt.close(fig)


def main() -> None:
    jobs_df = pd.read_csv(PROCESSED / "jobs.csv")
    long_df = pd.read_csv(PROCESSED / "job_skills.csv")
    FIG_DIR.mkdir(exist_ok=True)

    top = top_skills(long_df, n_jobs=len(jobs_df))
    skills_by_seniority(long_df, top)
    cooccurrence(jobs_df, top)

    print(f"Charts saved to {FIG_DIR}/")
    print("\nTop skills:")
    print(top.to_string())
    # auto-update README stats block
    from datetime import date
    n = len(jobs_df)
    junior_pct = (jobs_df["seniority"] == "Junior/Entry").mean() * 100
    genai_pct = jobs_df["skills"].fillna("").str.contains("GenAI").mean() * 100
    arabic_pct = jobs_df["skills"].fillna("").str.contains("Arabic").mean() * 100
    stats = (f"<!-- STATS:START -->\n"
             f"**Latest snapshot ({date.today():%b %d, %Y}): {n} postings** · "
             f"junior/entry roles: {junior_pct:.0f}% · "
             f"mention GenAI/LLMs: {genai_pct:.0f}% · "
             f"require Arabic: {arabic_pct:.0f}%\n"
             f"<!-- STATS:END -->")
    import re as _re
    readme = Path("README.md")
    if readme.exists():
        content = readme.read_text()
        new = _re.sub(r"<!-- STATS:START -->.*?<!-- STATS:END -->", stats,
                      content, flags=_re.DOTALL)
        if new != content:
            readme.write_text(new)
            print("README stats refreshed")


if __name__ == "__main__":
    main()
