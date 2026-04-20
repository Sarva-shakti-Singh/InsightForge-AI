"""Overview dashboard — KPI cards + key charts."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.kpis import compute_kpis, detect_columns
from utils.ui import section


def render(df: pd.DataFrame, role: str):
    section("📊 Overview", f"High-level KPIs for {role}.")
    kpis = compute_kpis(df)
    cols = detect_columns(df)

    metric_cols = st.columns(4)
    keys = list(kpis.keys())[:4]
    for i, k in enumerate(keys):
        v = kpis[k]
        display = f"{v:,.2f}" if isinstance(v, float) else str(v)
        metric_cols[i].metric(k.replace("_", " ").title(), display)

    if "growth_pct" in kpis:
        st.metric("📈 Growth (first vs last quartile)", f"{kpis['growth_pct']:+.2f}%")

    st.divider()
    if cols["datetime"] and cols["numeric"]:
        d, n = cols["datetime"][0], cols["numeric"][0]
        df2 = df[[d, n]].copy()
        df2[d] = pd.to_datetime(df2[d], errors="coerce")
        df2 = df2.dropna().groupby(d, as_index=False)[n].sum()
        fig = px.line(df2, x=d, y=n, title=f"{n} over time", markers=False)
        fig.update_layout(height=380, margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    if cols["categorical"] and cols["numeric"]:
        c, n = cols["categorical"][0], cols["numeric"][0]
        agg = df.groupby(c, as_index=False)[n].sum().sort_values(n, ascending=False).head(10)
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(agg, x=c, y=n, title=f"Total {n} by {c}", color=c)
            fig.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.pie(agg, names=c, values=n, title=f"Share of {n} by {c}", hole=0.45)
            fig.update_layout(height=360)
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔍 Raw data preview"):
        st.dataframe(df.head(200), use_container_width=True)
