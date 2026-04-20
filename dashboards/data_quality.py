"""Data Quality & Governance module."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from utils import Memory


def validate_data(df: pd.DataFrame) -> dict:
    """Perform comprehensive data quality checks."""
    checks = {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "null_check": {},
        "duplicate_check": len(df) - len(df.drop_duplicates()),
        "data_type_check": {},
        "numeric_issues": {}
    }
    
    # Null values
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            checks["null_check"][col] = {
                "count": int(null_count),
                "percentage": round(null_count / len(df) * 100, 2)
            }
    
    # Data types
    for col, dtype in df.dtypes.items():
        checks["data_type_check"][col] = str(dtype)
    
    # Numeric issues
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        zero_count = (df[col] == 0).sum()
        negative_count = (df[col] < 0).sum()
        if zero_count > 0 or negative_count > 0:
            checks["numeric_issues"][col] = {
                "zeros": int(zero_count),
                "negatives": int(negative_count)
            }
    
    return checks


def render(df: pd.DataFrame, memory: Memory, username: str):
    st.header("🛡️ Data Quality & Governance")
    st.markdown("Monitor data quality and maintain audit trails.")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("Data Quality Report")
        
        if st.button("Run Quality Check", use_container_width=True, type="primary"):
            checks = validate_data(df)
            
            # Summary metrics
            metric_cols = st.columns(3)
            metric_cols[0].metric("Total Rows", f"{checks['total_rows']:,}")
            metric_cols[1].metric("Total Columns", checks['total_cols'])
            metric_cols[2].metric("Duplicates", checks['duplicate_check'])
            
            st.divider()
            
            # Null values
            if checks["null_check"]:
                st.warning(f"⚠️ Found null values in {len(checks['null_check'])} columns:")
                for col, stats in checks["null_check"].items():
                    st.write(f"- **{col}**: {stats['count']} ({stats['percentage']}%)")
            else:
                st.success("✅ No null values detected")
            
            st.divider()
            
            # Numeric issues
            if checks["numeric_issues"]:
                st.warning(f"⚠️ Numeric anomalies found:")
                for col, issues in checks["numeric_issues"].items():
                    st.write(f"- **{col}**: {issues['zeros']} zeros, {issues['negatives']} negatives")
            else:
                st.success("✅ No numeric anomalies detected")
            
            # Log to audit trail
            memory.add("quality_check_run", {
                "total_issues": len(checks['null_check']) + len(checks['numeric_issues']),
                "duplicates": checks['duplicate_check'],
                "by_user": username
            })
    
    with col2:
        st.subheader("Audit Log")
        
        # Display recent audit events
        recent = memory.recent(limit=20)
        audit_events = [
            ev for ev in recent 
            if ev.get('kind') in ['quality_check_run', 'dataset_loaded', 'anomaly_detected']
        ]
        
        if audit_events:
            st.caption(f"Last {len(audit_events)} governance events:")
            for event in audit_events[:10]:
                event_type = event.get('kind', 'unknown').replace('_', ' ').title()
                timestamp = event.get('ts', '')[:16]
                st.caption(f"🔔 {event_type} @ {timestamp}")
        else:
            st.info("No audit events yet.")
        
        st.divider()
        if st.button("Export Audit Trail", use_container_width=True):
            audit_data = [
                {
                    "timestamp": ev.get('ts'),
                    "event_type": ev.get('kind'),
                    "user": ev.get('data', {}).get('by_user', 'system')
                }
                for ev in recent
            ]
            audit_df = pd.DataFrame(audit_data)
            csv = audit_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download Audit Log (CSV)",
                data=csv,
                file_name="audit_trail.csv",
                mime="text/csv"
            )
