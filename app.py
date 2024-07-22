import streamlit as st
import os
from dotenv import dotenv_values
import html_utils

st.set_page_config(page_title="AECOM IPC | CV Chatbot", page_icon="📄")
html_utils.set_page_background_local("assets/background.png")

if "role" not in st.session_state:
    st.session_state.role = None
if "collection_name" not in st.session_state:
    st.session_state.collection_name = "CV_documents"

ROLES = ["User", "Admin"]

def login():
    st.header(":orange[Start chatting with the IPC CV chatbot]")
    with st.form("my_form"):
        st.subheader("Login")
        role = st.text_input("Username")
        if st.form_submit_button("Login"):
            st.session_state.role = role
            st.rerun()
    if st.session_state.role is None:
        st.warning("Please login to continue")
    elif st.session_state.role not in ROLES:
        st.error("Username is incorrect")


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

chatbot_page = st.Page(
    "page/chatbot.py",
    title="Chatbot",
    icon=":material/home:",
    default=(role == "User"),
)

admin_1 = st.Page(
    "page/admin.py",
    title="CV Knowledge Base",
    icon=":material/database:",
    default=(role == "Admin"),
)

admin_2 = st.Page(
    "page/admin_1.py",
    title="Role Authenication",
    icon=":material/person_add:",
)

account_pages = [logout_page]
test_pages = [chatbot_page]
admin_pages = [admin_1, admin_2]

# st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

page_dict = {}
if st.session_state.role in ["User", "Admin"]:
    page_dict["Home"] = test_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation(page_dict | {"Account": account_pages} )
else:
    pg = st.navigation([st.Page(login)])

pg.run()