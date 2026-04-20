"""Insights dashboard — AI explanations of trends, anomalies, root causes."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.ui import section, info_panel
from agents import InsightAgent, DataAgent


def render(df: pd.DataFrame, memory):
    section("🧠 Insights", "AI-generated explanations of what's happening in your data.")
    if st.button("✨ Generate insights", type="primary"):
        with st.spinner("Analyzing..."):
            insights = InsightAgent().generate(df)
        memory.add("insights", {"items": insights})
        for ins in insights:
            info_panel(ins.replace("\n", "<br/>"))
            st.write("")

    st.divider()
    st.subheader("💬 Ask the Data Agent")
    q = st.text_input("Ask a question about your dataset",
                      placeholder="e.g. What drove the recent decline in revenue?")
    if q and st.button("Ask"):
        with st.spinner("Thinking..."):
            ans = DataAgent().ask(df, q)
        memory.add("query", {"question": q, "answer": ans[:1000]})
        st.markdown(ans)
