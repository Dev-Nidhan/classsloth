"""ClassSloth entry point."""

from datetime import datetime

import streamlit as st

from classsloth.config import load_settings
from classsloth.services import effective, ensure_public_demo, student_zone
from classsloth.ui.common import get_db, inject
from classsloth.ui.courses import render as render_courses
from classsloth.ui.dashboard import render as render_dashboard
from classsloth.ui.exam import render as render_exam
from classsloth.ui.settings_page import render as render_settings
from classsloth.ui.week import render as render_week

st.set_page_config(
    page_title="ClassSloth",
    page_icon="🦥",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject()

_settings = effective(load_settings(), get_db())
if _settings.public_demo:
    _zone = student_zone(_settings)
    ensure_public_demo(get_db(), _settings, datetime.now(_zone), _zone)
    st.info(
        "Assignments on this site are the labeled demo set. Gemma 3 4B runs inside this Render service for that demo. "
        "Google sign-in, private uploads, web search, and audio stay off. The model is not exposed as its own public address.",
        title="Public demo",
    )

if "source_filter" not in st.session_state:
    st.session_state["source_filter"] = "all"

with st.sidebar:
    st.segmented_control(
        "Records",
        options=["all", "live", "demo"],
        format_func=lambda item: {"all": "All", "live": "Classroom", "demo": "Demo"}[item],
        key="source_filter",
    )
    st.caption("Demo rows stay labeled. A Classroom sync never overwrites them.")

navigation = st.navigation(
    [
        st.Page(render_dashboard, title="Dashboard", icon=":material/dashboard:", default=True, url_path="dashboard"),
        st.Page(render_week, title="This week", icon=":material/calendar_month:", url_path="week"),
        st.Page(render_courses, title="Courses and materials", icon=":material/menu_book:", url_path="courses"),
        st.Page(render_exam, title="Exam prep", icon=":material/school:", url_path="exam"),
        st.Page(render_settings, title="Settings", icon=":material/settings:", url_path="settings"),
    ]
)
navigation.run()
