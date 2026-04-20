"""Export module — generate reports and export data."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime


def render():
    st.header("📄 Reports & Export")
    st.markdown("Generate and export reports in multiple formats.")

    # Column selection
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Select Data to Export")
    with col2:
        format_choice = st.selectbox("Format", ["Excel", "CSV", "JSON"], key="export_format")

    if st.session_state.get("df") is not None:
        df = st.session_state.df
        
        # Column filter
        all_cols = st.multiselect("Columns to export", df.columns, default=list(df.columns)[:5])
        
        # Row filter
        col1, col2 = st.columns(2)
        with col1:
            start_row = st.number_input("Start row", value=0, min_value=0, max_value=len(df)-1)
        with col2:
            end_row = st.number_input("End row", value=min(100, len(df)), min_value=1, max_value=len(df))
        
        filtered_df = df.iloc[start_row:end_row][all_cols]
        
        # Preview
        with st.expander("Preview"):
            st.dataframe(filtered_df.head(10), use_container_width=True)
        
        # Export button
        if st.button("📥 Generate Export", use_container_width=True, type="primary"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_choice == "Excel":
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    filtered_df.to_excel(writer, sheet_name="Data", index=False)
                buffer.seek(0)
                st.download_button(
                    "⬇️ Download Excel",
                    data=buffer,
                    file_name=f"export_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif format_choice == "CSV":
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download CSV",
                    data=csv,
                    file_name=f"export_{timestamp}.csv",
                    mime="text/csv"
                )
            elif format_choice == "JSON":
                json = filtered_df.to_json(orient="records", indent=2)
                st.download_button(
                    "⬇️ Download JSON",
                    data=json,
                    file_name=f"export_{timestamp}.json",
                    mime="application/json"
                )
            st.success("Export ready!")
    else:
        st.info("👈 Load data from sidebar first to export.")
