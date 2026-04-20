"""Actions dashboard — recommended business actions with priorities."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.ui import section
from agents import InsightAgent, DecisionAgent


PRIORITY_COLORS = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}


def render(df: pd.DataFrame, role: str, memory):
    section("🎯 Recommended actions",
            f"AI-prioritized next steps tailored for your role ({role}).")

    if st.button("🚀 Recommend actions", type="primary"):
        with st.spinner("Reasoning..."):
            insights = InsightAgent().generate(df)
            recs = DecisionAgent().recommend(df, insights, role=role)
        memory.add("actions", {"recs": recs})
        for r in recs:
            color = PRIORITY_COLORS.get(r.get("priority", "Medium"), "#6B7280")
            st.markdown(
                f"""
                <div style="border-left:4px solid {color};padding:10px 16px;
                            background:#F9FAFB;border-radius:6px;margin-bottom:10px;">
                  <div style="font-weight:600;color:#111827;">{r.get('title','')}</div>
                  <div style="color:#374151;font-size:14px;">{r.get('rationale','')}</div>
                  <div style="color:{color};font-size:12px;font-weight:600;
                              margin-top:4px;">PRIORITY · {r.get('priority','Medium').upper()}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
