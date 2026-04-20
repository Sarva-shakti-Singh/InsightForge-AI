"""Reusable UI helpers."""
import streamlit as st


def kpi_card(label: str, value, delta: str | None = None):
    st.metric(label=label, value=value, delta=delta)


def section(title: str, subtitle: str = ""):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def info_panel(text: str):
    st.markdown(
        f"""
        <div style="padding:14px 18px;border-radius:10px;
                    background:linear-gradient(135deg,#EEF2FF,#F5F3FF);
                    border:1px solid #E0E7FF;color:#1E1B4B;font-size:14px;
                    line-height:1.5;">{text}</div>
        """,
        unsafe_allow_html=True,
    )
