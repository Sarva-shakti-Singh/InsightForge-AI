"""Collaboration module — sharing and comments."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from datetime import datetime
from utils import Memory


def render(df: pd.DataFrame, memory: Memory, username: str):
    st.header("👥 Collaboration & Notes")
    st.markdown("Share insights and add notes for team collaboration.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Add Note")
        title = st.text_input("Note title", placeholder="e.g., Q1 Sales Insight")
        content = st.text_area("Note content", height=120, placeholder="Share your findings...")
        visibility = st.selectbox("Share with", ["Private", "Team", "Everyone"])
        
        if st.button("Save Note", use_container_width=True, type="primary"):
            if title and content:
                note = {
                    "title": title,
                    "content": content,
                    "author": username,
                    "visibility": visibility,
                    "timestamp": datetime.now().isoformat()
                }
                memory.add("note_created", note)
                st.success("✅ Note saved!")
            else:
                st.error("Please fill in title and content.")
    
    with col2:
        st.subheader("💬 Comments")
        comment_text = st.text_area("Add a comment", height=100, placeholder="Share thoughts...")
        
        if st.button("Post Comment", use_container_width=True):
            if comment_text:
                comment = {
                    "text": comment_text,
                    "author": username,
                    "timestamp": datetime.now().isoformat()
                }
                memory.add("comment_added", comment)
                st.success("✅ Comment posted!")
            else:
                st.error("Please enter a comment.")
    
    st.divider()
    st.subheader("📌 Recent Notes")
    recent_notes = memory.recent(limit=5)
    
    notes = [ev for ev in recent_notes if ev.get("kind") == "note_created"]
    if notes:
        for note_data in notes:
            data = note_data.get("data", {})
            with st.expander(f"📝 {data.get('title', 'Untitled')} by {data.get('author', 'Unknown')}"):
                st.write(data.get("content", ""))
                st.caption(f"Visibility: {data.get('visibility', 'Private')} | {data.get('timestamp', '')[:10]}")
    else:
        st.info("No notes yet. Start collaborating!")
