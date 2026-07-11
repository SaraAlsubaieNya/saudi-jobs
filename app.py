
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path("data/processed")
TOP_N = 15

st.set_page_config(page_title="Saudi Data Jobs", layout="wide")


@st.cache_data
def load_data():
    jobs = pd.read_csv(DATA / "jobs.csv")
    jobs["skills"] = jobs["skills"].fillna("")
    jobs["skill_list"] = jobs["skills"].str.split("|").apply(
        lambda xs: [s for s in xs if s]
    )
    return jobs


jobs = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
roles = sorted(jobs["role_family"].dropna().unique())
seniorities = ["Junior/Entry", "Mid", "Senior", "Lead/Manager+"]
seniorities = [s for s in seniorities if s in jobs["seniority"].unique()]

sel_roles = st.sidebar.multiselect("Role family", roles, default=roles)
sel_sen = st.sidebar.multiselect("Seniority", seniorities, default=seniorities)

df = jobs[jobs["role_family"].isin(sel_roles) & jobs["seniority"].isin(sel_sen)]

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: live Saudi job postings via the JSearch API "
    "(aggregating LinkedIn, Indeed, Bayt & more). "
    "Skills detected by keyword matching; junk/aggregator postings filtered out."
)

# ---------- Header & KPIs ----------
st.title("What Saudi employers want from data professionals")
st.caption("Skills demand extracted from real job postings -filter by role and seniority")

n = len(df)
if n == 0:
    st.warning("No postings match the current filters.")
    st.stop()

exploded = df.explode("skill_list").dropna(subset=["skill_list"]).reset_index(drop=True)
skill_counts = exploded["skill_list"].value_counts()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Postings", n)
c2.metric("Top skill", skill_counts.index[0] if len(skill_counts) else "—")
junior_pct = (df["seniority"] == "Junior/Entry").mean() * 100
c3.metric("Junior/entry roles", f"{junior_pct:.0f}%")
genai_pct = df["skill_list"].apply(lambda xs: "GenAI / LLMs" in xs).mean() * 100
c4.metric("Mention GenAI/LLMs", f"{genai_pct:.0f}%")

st.markdown("---")

# ---------- Chart 1: top skills ----------
top = skill_counts.head(TOP_N)
pct = (top / n * 100).round(1).iloc[::-1]
fig = px.bar(
    x=pct.values, y=pct.index, orientation="h",
    labels={"x": "% of postings", "y": ""},
    title=f"Most in-demand skills (n={n} postings)",
)
fig.update_traces(marker_color="#2a9d8f", texttemplate="%{x}%", textposition="outside")
fig.update_layout(height=520, margin=dict(l=10, r=10, t=50, b=10))
st.plotly_chart(fig)

# ---------- Chart 2 & 3 side by side ----------
left, right = st.columns(2)

with left:
    sub = exploded[exploded["skill_list"].isin(top.index)]
    pivot = pd.crosstab(sub["skill_list"], sub["seniority"], normalize="columns") * 100
    pivot = pivot[[s for s in seniorities if s in pivot.columns]].reindex(top.index)
    fig2 = px.imshow(
        pivot.round(0), text_auto=True, color_continuous_scale="YlGnBu",
        labels=dict(x="Seniority", y="", color="% of mentions"),
        title="Skill demand by seniority",
        aspect="auto",
    )
    fig2.update_layout(height=560, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig2)

with right:
    skills_list = top.index.tolist()
    mat = pd.DataFrame(0, index=skills_list, columns=skills_list, dtype=int)
    for xs in df["skill_list"]:
        present = [s for s in skills_list if s in xs]
        for a in present:
            for b in present:
                mat.loc[a, b] += 1
    fig3 = px.imshow(
        mat, color_continuous_scale="OrRd",
        title="Skill co-occurrence (postings mentioning both)",
        aspect="auto",
    )
    fig3.update_layout(height=560, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig3)

# ---------- Data table ----------
st.markdown("---")
st.subheader("Browse the postings")
show = df[["title", "company", "city", "seniority", "role_family", "skills", "url"]]
st.dataframe(
    show, width="stretch", hide_index=True,
    column_config={"url": st.column_config.LinkColumn("posting", display_text="open")},
)
st.download_button(
    "Download filtered data (CSV)",
    show.to_csv(index=False).encode(),
    file_name="saudi_data_jobs_filtered.csv",
    mime="text/csv",
)