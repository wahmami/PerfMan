import streamlit as st
from database import init_db
from teacher_menu import teacher_menu
from attendance_menu import attendance_menu
from journal_menu import journal_menu
from cahiers_menu import cahiers_menu
from settings_menu import settings_menu  # <-- Import the settings menu

# Placeholder menu functions
def materials_menu():
    st.header("📦 Materials")
    st.info("Materials section coming soon.")
    return []

def rapport_menu():
    st.header("📊 Rapport")
    st.info("Rapport section coming soon.")
    return []

# --- Initialize DB ---
init_db()

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .main .block-container {
        max-width: 95vw;
        padding-left: 2vw;
        padding-right: 2vw;
    }
    </style>
""", unsafe_allow_html=True)

col_menu, col_main, col_obs = st.columns([1, 3, 1])

with col_menu:
    menu = st.radio(
        "Menu",
        [
            "Teacher",
            "Attendance",
            "Journal",
            "Cahiers",
            "Materials",
            "Rapport",
            "Settings"  # <-- Add Settings to the menu
        ]
    )

messages = []

with col_main:
    if menu == "Teacher":
        messages = teacher_menu()
    elif menu == "Attendance":
        messages = attendance_menu()
    elif menu == "Journal":
        messages = journal_menu()
    elif menu == "Cahiers":
        messages = cahiers_menu()
    elif menu == "Materials":
        messages = materials_menu()
    elif menu == "Rapport":
        messages = rapport_menu()
    elif menu == "Settings":
        messages = settings_menu()  # <-- Call the settings menu

with col_obs:
    st.header("Observations")
    for msg_type, msg in messages:
        if msg_type == "success":
            st.success(msg)
        elif msg_type == "warning":
            st.warning(msg)
        elif msg_type == "info":
            st.info(msg)
        elif msg_type == "error":
            st.error(msg)