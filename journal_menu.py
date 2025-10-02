<<<<<<< HEAD
# journal_menu.py
import streamlit as st
from datetime import datetime
from database import get_all_teachers, add_journal_entry, get_journal_entries
import pandas as pd

def journal_menu():
    messages = []
    st.header("📓 Journal Check")

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]
    if not teacher_names:
        messages.append(("warning", "No teachers found."))
        return messages

    with st.form("journal_form"):
        teacher = st.selectbox("Teacher", teacher_names)
        date = st.date_input("Date", datetime.today())
        status = st.selectbox("Status", ["Checked", "Outdated", "Forgotten"])
        observation = st.text_area("Observation")
        outdated_days = 0
        if status == "Outdated":
            outdated_days = st.number_input("How many days outdated?", min_value=1, step=1)
        submitted = st.form_submit_button("Save Journal Check")
        if submitted:
            add_journal_entry(
                teacher,
                str(date),
                status,
                observation,
                int(outdated_days)
            )
            messages.append(("success", "Journal check saved."))

    st.subheader("📋 Journal Checks")
    entries = get_journal_entries()
    if entries:
        df = pd.DataFrame(entries, columns=["Teacher", "Date", "Status", "Observation", "Outdated Days"])
        st.data_editor(df, num_rows="dynamic", use_container_width=True)
    else:
        st.info("No journal checks recorded yet.")
=======
# journal_menu.py
import streamlit as st
from datetime import datetime
from database import get_all_teachers, add_journal_entry, get_journal_entries
import pandas as pd

def journal_menu():
    messages = []
    st.header("📓 Journal Check")

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]
    if not teacher_names:
        messages.append(("warning", "No teachers found."))
        return messages

    with st.form("journal_form"):
        teacher = st.selectbox("Teacher", teacher_names)
        date = st.date_input("Date", datetime.today())
        status = st.selectbox("Status", ["Checked", "Outdated", "Forgotten"])
        observation = st.text_area("Observation")
        outdated_days = 0
        if status == "Outdated":
            outdated_days = st.number_input("How many days outdated?", min_value=1, step=1)
        submitted = st.form_submit_button("Save Journal Check")
        if submitted:
            add_journal_entry(
                teacher,
                str(date),
                status,
                observation,
                int(outdated_days)
            )
            messages.append(("success", "Journal check saved."))

    st.subheader("📋 Journal Checks")
    entries = get_journal_entries()
    if entries:
        df = pd.DataFrame(entries, columns=["Teacher", "Date", "Status", "Observation", "Outdated Days"])
        st.dataframe(df)
    else:
        st.info("No journal checks recorded yet.")
>>>>>>> 7a70e5efef2ce3ca2f1cdc291bf43c6062b79df7
    return messages