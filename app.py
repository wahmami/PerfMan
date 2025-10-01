import streamlit as st

from database import init_db
from attendance_menu import attendance_menu
from journal_menu import journal_menu
from cahiers_menu import cahiers_menu
from materials_menu import materials_menu
from rapport_menu import rapport_menu
from devoir_menu import devoir_menu
from teachers_visual_menu import teachers_visual_menu
from settings_menu import (
    settings_teachers_menu,
    settings_rapport_menu,
    settings_subjects_menu,
    settings_classes_menu,
    settings_modules_menu,
    settings_materials_menu
)

# --- Advanced Authentication Setup ---
# Read credentials from secrets
usernames = st.secrets["auth"]["usernames"]
names = st.secrets["auth"]["names"]
passwords = st.secrets["auth"]["passwords"]

# Hash passwords
hashed_passwords = stauth.Hasher(list(passwords)).generate()

credentials = {
    "usernames": {
        username: {"name": name, "password": hash_}
        for username, name, hash_ in zip(usernames, names, hashed_passwords)
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "perf_app_cookie",  # Cookie name
    "abcdef",           # Cookie key (change to something random for production)
    cookie_expiry_days=7
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {name}!")

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

    main_menu = st.sidebar.radio(
        "Main Menu",
        [
            "Attendance",
            "Journal",
            "Cahiers",
            "Materials",
            "Rapport",
            "Devoir",
            "Techers",
            "Settings"
        ]
    )

    messages = []

    if main_menu == "Attendance":
        messages = attendance_menu()
    elif main_menu == "Journal":
        messages = journal_menu()
    elif main_menu == "Cahiers":
        messages = cahiers_menu()
    elif main_menu == "Materials":
        messages = materials_menu()
    elif main_menu == "Rapport":
        messages = rapport_menu()
    elif main_menu == "Devoir":
        messages = devoir_menu()
    elif main_menu == "Techers":
        messages = teachers_visual_menu()
    elif main_menu == "Settings":
        st.header("⚙️ Settings")
        settings_submenu = st.radio(
            "Settings Submenu",
            [
                "Teachers (CRUD)",
                "Rapport (CRUD)",
                "Subjects",
                "Classes",
                "Modules & Submodules",
                "Materials"
            ]
        )
        if settings_submenu == "Teachers (CRUD)":
            messages = settings_teachers_menu()
        elif settings_submenu == "Rapport (CRUD)":
            messages = settings_rapport_menu()
        elif settings_submenu == "Subjects":
            messages = settings_subjects_menu()
        elif settings_submenu == "Classes":
            messages = settings_classes_menu()
        elif settings_submenu == "Modules & Submodules":
            messages = settings_modules_menu()
        elif settings_submenu == "Materials":
            messages = settings_materials_menu()

    st.sidebar.header("Observations")
    for msg_type, msg in messages:
        if msg_type == "success":
            st.sidebar.success(msg)
        elif msg_type == "warning":
            st.sidebar.warning(msg)
        elif msg_type == "info":
            st.sidebar.info(msg)
        elif msg_type == "error":
            st.sidebar.error(msg)

