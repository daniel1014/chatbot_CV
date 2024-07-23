import streamlit as st

st.header("Settings")
st.write(f"You are logged in as {st.session_state.role}.")

test = "[0] IPC DA - Principal Data Scientist - Akashia Puri.docx - [Data Advisory]"
full_response = ""
full_response += "> **Relevant CVs**"
full_response += "\n"
full_response += " - "
full_response += test
full_response += "\n"
full_response += " - "

st.markdown(full_response)