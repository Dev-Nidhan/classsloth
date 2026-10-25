"""Shared Streamlit pieces. Inference is never started from this module."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from classsloth.config import load_settings
from classsloth.dates import due_label, status_phrase
from classsloth.db import Database
from classsloth.models import Assignment
from classsloth.services import effective, student_zone

CSS = """
<style>
:root {
  --ink: #1c2822;
  --muted: #5d6b64;
  --paper: #f3efe6;
  --card: #fffdf8;
  --line: #e4dccb;
  --green: #1f6b4a;
  --green-deep: #17382c;
  --overdue: #8d3a32;
  --ochre: #8a5a12;
  --demo: #5c4578;
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--paper);
  color: var(--ink);
}
section[data-testid="stSidebar"] {
  background: var(--green-deep);
}
section[data-testid="stSidebar"] * {
  color: #f6f3ec;
}
section[data-testid="stSidebar"] [data-baseweb="radio"] {
  background: transparent;
}
.wordmark {
  font-size: 1.7rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 0;
}
.tagline { color: var(--muted); margin-top: 0.1rem; }
.kicker {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: var(--muted);
  margin-bottom: 0.2rem;
}
.next-title { font-size: 1.55rem; font-weight: 680; line-height: 1.25; }
.badge {
  display: inline-block;
  border-radius: 999px;
  padding: 0.12rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 650;
  border: 1px solid var(--line);
}
.badge.demo { color: var(--demo); background: #f3eefe; }
.badge.live { color: var(--green); background: #e7f4ed; }
.due { font-weight: 650; }
.due.overdue { color: var(--overdue); }
.due.soon { color: var(--green); }
.due.none { color: var(--ochre); }
.note {
  background: #f7f1df;
  border: 1px solid #eadcb8;
  border-radius: 10px;
  padding: 0.7rem 0.9rem;
  color: var(--ink);
}
.source-box {
  background: #f4faf6;
  border-left: 4px solid var(--green);
  padding: 0.6rem 0.8rem;
  margin: 0.4rem 0;
}
.general-box {
  background: #f7f4ef;
  border-left: 4px solid #b9ab96;
  padding: 0.6rem 0.8rem;
  margin: 0.4rem 0;
}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource
def get_db() -> Database:
    settings = load_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return Database(settings.db_path)


def context():
    db = get_db()
    settings = effective(load_settings(), db)
    tz = student_zone(settings)
    now = datetime.now(tz)
    source = st.session_state.get("source_filter") or "all"
    scope = source if source in {"live", "demo"} else None
    return settings, db, tz, now, scope


def go(page: str) -> None:
    st.switch_page(page)


def source_badge(source: str) -> None:
    if source == "demo":
        st.badge("Demo data", color="violet")
    else:
        st.badge("Classroom", color="green")


def due_line(assignment: Assignment, now: datetime, tz) -> None:
    label = due_label(assignment, now, tz)
    if assignment.due_at is None:
        st.markdown(f":orange[{label}]")
    elif "Past due" in label:
        st.markdown(f":red[{label}]")
    else:
        st.markdown(f":green[{label}]")


def status_line(assignment: Assignment) -> str:
    return "Submission status: " + status_phrase(assignment.submission_status)


def assignment_card(assignment: Assignment, now: datetime, tz, *, compact: bool = False) -> None:
    with st.container(border=True):
        left, right = st.columns([5, 1])
        with left:
            st.markdown(f"**{assignment.title}**")
            st.caption(assignment.course_name)
        with right:
            source_badge(assignment.source)
        due_line(assignment, now, tz)
        st.caption(status_line(assignment))
        if assignment.description and not compact:
            st.write(assignment.description[:500])
        if assignment.link:
            st.link_button("Open original", assignment.link)
        elif assignment.source == "demo":
            st.caption("Demo records have no Classroom link.")
        if assignment.materials:
            st.caption("Linked materials")
            for material in assignment.materials:
                st.markdown(f"- [{material.title}]({material.url})")
