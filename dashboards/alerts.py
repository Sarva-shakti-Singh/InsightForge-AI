"""Alerts & Anomaly Detection module."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from utils import Memory


def detect_anomalies(df: pd.DataFrame, column: str, threshold: float = 2.0) -> pd.DataFrame:
    """Detect anomalies using z-score method."""
    numeric_df = df.select_dtypes(include=[np.number])
    if column not in numeric_df.columns:
        return pd.DataFrame()
    
    col_data = numeric_df[column]
    mean = col_data.mean()
    std = col_data.std()
    
    z_scores = np.abs((col_data - mean) / std)
    anomalies = df[z_scores > threshold].copy()
    anomalies["z_score"] = z_scores[z_scores > threshold]
    
    return anomalies


def render(df: pd.DataFrame, memory: Memory):
    st.header("🚨 Alerts & Anomaly Detection")
    st.markdown("Monitor KPIs and detect data anomalies automatically.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Set KPI Alerts")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            kpi_col = st.selectbox("Select metric", numeric_cols, key="kpi_alert")
            alert_type = st.radio("Alert type", ["Min threshold", "Max threshold", "Change %"])
            threshold_val = st.number_input("Threshold value", step=0.1)
            
            if st.button("Set Alert", key="set_kpi_alert", use_container_width=True):
                current_val = df[kpi_col].mean()
                
                alert_triggered = False
                if alert_type == "Min threshold":
                    alert_triggered = current_val < threshold_val
                elif alert_type == "Max threshold":
                    alert_triggered = current_val > threshold_val
                elif alert_type == "Change %":
                    if len(df) > 1:
                        first_val = df[kpi_col].iloc[0]
                        pct_change = ((current_val - first_val) / abs(first_val) * 100) if first_val != 0 else 0
                        alert_triggered = abs(pct_change) > threshold_val
                
                memory.add("kpi_alert_set", {
                    "metric": kpi_col,
                    "type": alert_type,
                    "threshold": threshold_val,
                    "triggered": alert_triggered,
                    "current_value": float(current_val)
                })
                
                if alert_triggered:
                    st.warning(f"⚠️ Alert triggered! {kpi_col} = {current_val:.2f}")
                else:
                    st.success(f"✅ Alert set. Current value: {current_val:.2f}")
        else:
            st.info("No numeric columns found.")
    
    with col2:
        st.subheader("Detect Anomalies")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            anomaly_col = st.selectbox("Select column", numeric_cols, key="anomaly_col")
            sensitivity = st.slider("Sensitivity (lower = more sensitive)", 1.0, 3.0, 2.0, step=0.1)
            
            if st.button("Detect", key="detect_anomalies", use_container_width=True):
                anomalies = detect_anomalies(df, anomaly_col, threshold=sensitivity)
                
                if len(anomalies) > 0:
                    st.warning(f"Found {len(anomalies)} anomalies in {anomaly_col}")
                    st.dataframe(anomalies[[anomaly_col, "z_score"]].head(20), use_container_width=True)
                    memory.add("anomaly_detected", {
                        "column": anomaly_col,
                        "count": len(anomalies),
                        "sensitivity": sensitivity
                    })
                else:
                    st.success(f"No anomalies detected in {anomaly_col}")
        else:
            st.info("No numeric columns found.")
