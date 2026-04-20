"""Advanced Analytics module — cohort, funnel, A/B testing."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def cohort_analysis(df: pd.DataFrame, date_col: str, user_col: str, value_col: str):
    """Generate cohort analysis."""
    try:
        df_cohort = df[[date_col, user_col, value_col]].copy()
        df_cohort[date_col] = pd.to_datetime(df_cohort[date_col], errors="coerce")
        df_cohort = df_cohort.dropna()
        
        if len(df_cohort) == 0:
            st.warning("No valid date data for cohort analysis.")
            return
        
        df_cohort["cohort"] = df_cohort[date_col].dt.to_period("M")
        cohort_data = df_cohort.groupby([user_col, "cohort"])[value_col].sum().reset_index()
        cohort_pivot = cohort_data.pivot_table(
            index="cohort", columns=user_col, values=value_col, aggfunc="sum"
        )
        
        st.subheader("Cohort Analysis (Monthly)")
        st.dataframe(cohort_pivot, use_container_width=True)
        
        # Heatmap
        fig = go.Figure(data=go.Heatmap(
            z=cohort_pivot.values,
            x=cohort_pivot.columns,
            y=[str(p) for p in cohort_pivot.index],
            colorscale="Viridis"
        ))
        fig.update_layout(title="Cohort Heatmap", height=400)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Cohort analysis error: {e}")


def funnel_analysis(df: pd.DataFrame, stages: list):
    """Generate funnel analysis."""
    if not all(col in df.columns for col in stages):
        st.error("Selected columns not found in data.")
        return
    
    try:
        funnel_data = []
        for stage in stages:
            count = (df[stage] > 0).sum() if pd.api.types.is_numeric_dtype(df[stage]) else df[stage].notna().sum()
            funnel_data.append({"Stage": stage, "Count": count})
        
        funnel_df = pd.DataFrame(funnel_data)
        funnel_df["Conversion %"] = (funnel_df["Count"] / funnel_df["Count"].iloc[0] * 100).round(2)
        
        st.subheader("Funnel Analysis")
        st.dataframe(funnel_df, use_container_width=True)
        
        fig = px.funnel(funnel_df, x="Count", y="Stage", title="Conversion Funnel")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Funnel analysis error: {e}")


def ab_testing(df: pd.DataFrame, group_col: str, metric_col: str):
    """Simple A/B test comparison."""
    if group_col not in df.columns or metric_col not in df.columns:
        st.error("Selected columns not found.")
        return
    
    try:
        groups = df[group_col].unique()
        if len(groups) != 2:
            st.warning(f"Expected 2 groups, found {len(groups)}. Showing comparison anyway.")
        
        comparison = df.groupby(group_col)[metric_col].agg([
            ("Count", "count"),
            ("Mean", "mean"),
            ("Std Dev", "std"),
            ("Min", "min"),
            ("Max", "max")
        ]).round(3)
        
        st.subheader("A/B Test Results")
        st.dataframe(comparison, use_container_width=True)
        
        # Visualization
        fig = px.box(df, x=group_col, y=metric_col, title=f"{metric_col} by {group_col}")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"A/B testing error: {e}")


def render(df: pd.DataFrame):
    st.header("📊 Advanced Analytics")
    st.markdown("Cohort analysis, funnel analysis, and A/B testing.")
    
    analysis_type = st.selectbox(
        "Select analysis type",
        ["Cohort Analysis", "Funnel Analysis", "A/B Testing"]
    )
    
    st.divider()
    
    if analysis_type == "Cohort Analysis":
        st.subheader("Cohort Analysis")
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = df.columns.tolist()
        
        if date_cols and numeric_cols and len(all_cols) > 1:
            date_col = st.selectbox("Date column", date_cols)
            user_col = st.selectbox("User/Group column", all_cols)
            value_col = st.selectbox("Value column", numeric_cols)
            
            if st.button("Run Cohort Analysis", use_container_width=True, type="primary"):
                cohort_analysis(df, date_col, user_col, value_col)
        else:
            st.info("Need date column, numeric column, and grouping column.")
    
    elif analysis_type == "Funnel Analysis":
        st.subheader("Funnel Analysis")
        all_cols = df.columns.tolist()
        
        stages = st.multiselect("Select stages (in order)", all_cols, key="funnel_stages")
        if len(stages) >= 2:
            if st.button("Run Funnel Analysis", use_container_width=True, type="primary"):
                funnel_analysis(df, stages)
        else:
            st.info("Select at least 2 columns as stages.")
    
    elif analysis_type == "A/B Testing":
        st.subheader("A/B Testing")
        all_cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        group_col = st.selectbox("Group/Variant column", all_cols)
        metric_col = st.selectbox("Metric column", numeric_cols)
        
        if st.button("Run A/B Test", use_container_width=True, type="primary"):
            ab_testing(df, group_col, metric_col)
