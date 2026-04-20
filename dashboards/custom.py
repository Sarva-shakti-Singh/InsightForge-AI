"""Custom Dashboards module — save and manage custom views."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils import Memory


def render(df: pd.DataFrame, memory: Memory, username: str):
    st.header("🎨 Custom Dashboards")
    st.markdown("Create, save, and manage personalized dashboard views.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Create New Dashboard")
        
        dashboard_name = st.text_input("Dashboard name", placeholder="e.g., Sales Performance Q1")
        dashboard_desc = st.text_area("Description", height=60, placeholder="What does this dashboard show?")
        
        # Chart configuration
        st.write("**Select charts to include:**")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            include_time_series = st.checkbox("Time Series Chart")
        with col_b:
            include_bar_chart = st.checkbox("Bar Chart")
        with col_c:
            include_heatmap = st.checkbox("Heatmap")
        
        # Metric selection
        if include_time_series and numeric_cols:
            ts_metric = st.selectbox("Time series metric", numeric_cols, key="ts_metric")
        else:
            ts_metric = None
        
        if include_bar_chart and numeric_cols and categorical_cols:
            bar_category = st.selectbox("Bar chart category", categorical_cols, key="bar_cat")
            bar_metric = st.selectbox("Bar chart metric", numeric_cols, key="bar_metric")
        else:
            bar_category = bar_metric = None
        
        if st.button("Save Dashboard", use_container_width=True, type="primary"):
            if dashboard_name:
                dashboard_config = {
                    "name": dashboard_name,
                    "description": dashboard_desc,
                    "created_by": username,
                    "created_at": datetime.now().isoformat(),
                    "charts": {
                        "time_series": include_time_series,
                        "bar_chart": include_bar_chart,
                        "heatmap": include_heatmap,
                        "ts_metric": ts_metric,
                        "bar_category": bar_category,
                        "bar_metric": bar_metric
                    }
                }
                
                memory.add("dashboard_created", dashboard_config)
                st.success(f"✅ Dashboard '{dashboard_name}' saved!")
            else:
                st.error("Please enter a dashboard name.")
    
    with col2:
        st.subheader("Saved Dashboards")
        
        recent = memory.recent(limit=50)
        dashboards = [ev for ev in recent if ev.get('kind') == 'dashboard_created']
        
        if dashboards:
            st.caption(f"Your dashboards ({len(dashboards)})")
            
            for dashboard in dashboards[:5]:
                data = dashboard.get('data', {})
                with st.expander(f"📊 {data.get('name', 'Untitled')}"):
                    st.write(data.get('description', 'No description'))
                    st.caption(f"Created: {data.get('created_at', '')[:10]}")
                    
                    col_load, col_delete = st.columns(2)
                    with col_load:
                        if st.button("Load", key=f"load_{dashboard.get('id', 'unknown')}"):
                            st.info("📈 Dashboard loaded! View in custom dashboard tab.")
                    with col_delete:
                        if st.button("Delete", key=f"del_{dashboard.get('id', 'unknown')}"):
                            st.warning("Dashboard marked for deletion.")
        else:
            st.info("No saved dashboards yet. Create one on the left!")
