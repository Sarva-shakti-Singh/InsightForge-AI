"""Chat dashboard — AI-powered Q&A about the dataset."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from agents.data_agent import DataAgent
from utils import Memory


def render(df: pd.DataFrame, memory: Memory):
    st.header("💬 Data Chatbot")
    st.markdown("Ask questions about your uploaded data. The AI will analyze and respond based on the dataset.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get AI response
        agent = DataAgent()
        answer = agent.ask(df, prompt)

        # Add assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)

        # Log to memory
        memory.add("chat_question", {"question": prompt, "answer": answer})