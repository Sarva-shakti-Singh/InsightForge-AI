"""AI Business Analyst Platform — Streamlit entry point."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path

from auth import AuthManager, ROLES
from utils import Memory
from data import load_csv, load_gsheet, load_rest
from dashboards import overview, forecast, insights, actions, chat, export, alerts, collaboration, advanced_analytics, data_quality, custom
from agents.llm_client import LLMClient

st.set_page_config(
    page_title="InsightForge AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "df" not in st.session_state:
    st.session_state.df = None

auth = AuthManager()


# ---------- Login screen ----------
def login_view():
    st.markdown(
        """
        <div style="max-width:520px;margin:40px auto 24px;text-align:center;">
          <h1 style="margin-bottom:6px;">🧠 InsightForge AI</h1>
          <p style="color:#64748B;">
            Enterprise BI with AI agents — analyze, forecast, decide.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["🔐 Sign in", "🆕 Create account"])
    with tab1:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            ok = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if ok:
            user = auth.login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.caption("Demo: ceo / ceo123 · manager / manager123 · analyst / analyst123")

    with tab2:
        with st.form("register"):
            ru = st.text_input("Username", key="ru")
            rn = st.text_input("Display name", key="rn")
            rp = st.text_input("Password", type="password", key="rp")
            rr = st.selectbox("Role", ROLES)
            ok = st.form_submit_button("Create account", use_container_width=True)
        if ok:
            if auth.register(ru, rp, rr, rn):
                st.success("Account created — sign in.")
            else:
                st.error("Username already exists or invalid role.")


# ---------- Data loaders ----------
def data_sidebar() -> pd.DataFrame | None:
    st.sidebar.markdown("### 📥 Data source")
    src = st.sidebar.radio("Select source", ["Sample data", "CSV upload",
                                             "Google Sheets", "REST API"],
                           label_visibility="collapsed")
    df = None
    try:
        if src == "Sample data":
            df = pd.read_csv(Path(__file__).parent / "data" / "sample_sales.csv")
        elif src == "CSV upload":
            f = st.sidebar.file_uploader("Upload CSV", type=["csv"])
            if f:
                df = load_csv(f)
        elif src == "Google Sheets":
            url = st.sidebar.text_input("Public Google Sheet URL")
            if url and st.sidebar.button("Load sheet"):
                df = load_gsheet(url)
        elif src == "REST API":
            url = st.sidebar.text_input("REST endpoint (JSON)")
            path = st.sidebar.text_input("JSON path (optional)",
                                         placeholder="e.g. data.items")
            if url and st.sidebar.button("Fetch"):
                df = load_rest(url, json_path=path or None)
    except Exception as e:
        st.sidebar.error(f"Load failed: {e}")
    return df


# ---------- Main app ----------
def main_view():
    user = st.session_state.user
    role = user["role"]
    memory = Memory(user["username"])
    llm = LLMClient()

    # Sidebar
    st.sidebar.markdown(f"### 👤 {user['name']}")
    st.sidebar.caption(f"Role: **{role}**")
    if llm.enabled:
        st.sidebar.success("AI: connected")
    else:
        st.sidebar.warning("AI: mock mode")
    st.sidebar.divider()

    new_df = data_sidebar()
    if new_df is not None:
        st.session_state.df = new_df
        memory.add("dataset_loaded", {"shape": list(new_df.shape),
                                      "columns": list(new_df.columns)})

    st.sidebar.divider()
    with st.sidebar.expander("🧠 Memory (recent)"):
        for ev in memory.recent(limit=10):
            st.caption(f"`{ev['ts'][:19]}` · **{ev['kind']}**")
        if st.button("Clear memory"):
            memory.clear()
            st.rerun()

    if st.sidebar.button("🚪 Sign out", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    # Header
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:6px 0 14px;">
          <div>
            <h2 style="margin:0;">InsightForge AI</h2>
            <div style="color:#64748B;font-size:14px;">
              Role-based BI · {role} workspace
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = st.session_state.df
    if df is None:
        st.info("👈 Pick a data source from the sidebar to begin.")
        return

    # Role-based tab availability
    all_tabs = ["📊 Overview", "🔮 Forecast", "🧠 Insights", "🎯 Actions", "💬 Chat", "📄 Export", "🚨 Alerts", "👥 Collab", "📊 Advanced", "🛡️ Quality", "🎨 Custom"]
    if role == "Analyst":
        # analysts focus on data + forecast + insights
        tabs_to_show = all_tabs
    elif role == "Manager":
        tabs_to_show = all_tabs
    else:  # CEO
        tabs_to_show = all_tabs

    tabs = st.tabs(tabs_to_show)
    with tabs[0]:
        overview.render(df, role)
    with tabs[1]:
        forecast.render(df, memory)
    with tabs[2]:
        insights.render(df, memory)
    with tabs[3]:
        actions.render(df, role, memory)
    with tabs[4]:
        chat.render(df, memory)
    with tabs[5]:
        export.render()
    with tabs[6]:
        alerts.render(df, memory)
    with tabs[7]:
        collaboration.render(df, memory, user["username"])
    with tabs[8]:
        advanced_analytics.render(df)
    with tabs[9]:
        data_quality.render(df, memory, user["username"])
    with tabs[10]:
        custom.render(df, memory, user["username"])


# ---------- Router ----------
if st.session_state.user is None:
    login_view()
else:
    main_view()
