import streamlit as st
import base64

def set_page_background_local_gif(img_path: str):
    with open(img_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/gif;base64,{b64_string}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_page_background_local(img_path: str):
    with open(img_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{b64_string}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )