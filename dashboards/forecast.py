"""Forecast dashboard — Prophet/ARIMA prediction with prediction intervals."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.kpis import detect_columns
from utils.ui import section, info_panel
from agents import ForecastAgent


def render(df: pd.DataFrame, memory):
    section("🔮 Forecast", "Predict revenue, units, or any numeric metric over time.")
    cols = detect_columns(df)
    if not cols["datetime"] or not cols["numeric"]:
        st.warning("Need at least one date column and one numeric column to forecast.")
        return

    c1, c2, c3 = st.columns(3)
    date_col = c1.selectbox("Date column", cols["datetime"])
    value_col = c2.selectbox("Metric to forecast", cols["numeric"])
    horizon = c3.slider("Horizon (days)", 7, 365, 60)

    if st.button("🚀 Run forecast", type="primary"):
        with st.spinner("Training model..."):
            try:
                res = ForecastAgent().forecast(df, date_col, value_col, horizon)
            except Exception as e:
                st.error(f"Forecast failed: {e}")
                return

        memory.add("forecast", {"date_col": date_col, "value_col": value_col,
                                "horizon": horizon, "method": res["method"]})

        info_panel(f"Model used: <b>{res['method'].upper()}</b> · "
                   f"Risk score: <b>{res['risk_score']:.2f}</b> "
                   f"({'high' if res['risk_score']>0.4 else 'low'} volatility)")

        fc = res["forecast"]
        hist = res["history"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist[date_col], y=hist[value_col],
                                 name="Actual", mode="lines",
                                 line=dict(color="#0F172A", width=2)))
        fig.add_trace(go.Scatter(x=fc[date_col], y=fc["forecast"],
                                 name="Forecast", mode="lines",
                                 line=dict(color="#4F46E5", width=2, dash="dash")))
        fig.add_trace(go.Scatter(
            x=list(fc[date_col]) + list(fc[date_col])[::-1],
            y=list(fc["upper"]) + list(fc["lower"])[::-1],
            fill="toself", fillcolor="rgba(79,70,229,0.15)",
            line=dict(color="rgba(0,0,0,0)"), name="80% interval", showlegend=True,
        ))
        fig.update_layout(height=480, margin=dict(t=40, l=10, r=10, b=10),
                          title=f"{value_col} — actual vs forecast ({res['method']})")
        st.plotly_chart(fig, use_container_width=True)

        future_only = fc.tail(horizon)
        st.subheader("📋 Forecast table")
        st.dataframe(future_only, use_container_width=True, height=260)

        total_pred = float(future_only["forecast"].sum())
        st.metric(f"Predicted total {value_col} (next {horizon}d)", f"{total_pred:,.0f}")
