# style.py
import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        div[data-testid="stMarkdownContainer"] p {
            font-size: 1.3rem;
            line-height: 1.6;
        }
        div[data-testid="stCaptionContainer"] p {
            font-size: 1.35rem;
        }
        </style>
    """, unsafe_allow_html=True)