"""Reusable UI components for Streamlit (placeholders)."""

import streamlit as st


def chat_bubble(sender: str, text: str):
    st.markdown(f"**{sender}**: {text}")
