<<<<<<< HEAD
from datetime import datetime
from database import get_all_teachers, add_cahier_entry, get_cahier_entries
from config import modules, submodules, classes
import streamlit as st

def cahiers_menu():
    messages = []
    st.header("📒 Cahiers (Books) Inspection")

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]
    if not teacher_names:
        messages.append(("warning", "No teachers found."))
        return messages

    teacher = st.selectbox("Teacher", teacher_names)
    class_selected = st.selectbox("Class", classes)
    inspection_date = st.date_input("Inspection Date", datetime.today())
    module = st.selectbox("Module", modules)

    # Dynamically show submodules if available
    submodule_options = submodules.get(module, [])
    if submodule_options:
        submodule = st.selectbox("Submodule", submodule_options)
    else:
        submodule = st.text_input("Submodule (none for this module)")

    title = st.text_input("Lesson Title")
    lesson_date = st.date_input("Lesson Date", datetime.today(), key="lesson_date")
    days_diff = (inspection_date - lesson_date).days
    st.info(f"Days between lesson and inspection: {days_diff} day(s)")

    if st.button("Save Inspection"):
        # Save logic here...
        messages.append(("success", f"Saved: {teacher} | {class_selected} | {inspection_date} | {module} | {submodule} | {title} | {lesson_date} | {days_diff} days"))

=======
from datetime import datetime
from database import get_all_teachers, add_cahier_entry, get_cahier_entries
from config import modules, submodules, classes
import streamlit as st

def cahiers_menu():
    messages = []
    st.header("📒 Cahiers (Books) Inspection")

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]
    if not teacher_names:
        messages.append(("warning", "No teachers found."))
        return messages

    teacher = st.selectbox("Teacher", teacher_names)
    class_selected = st.selectbox("Class", classes)
    inspection_date = st.date_input("Inspection Date", datetime.today())
    module = st.selectbox("Module", modules)

    # Dynamically show submodules if available
    submodule_options = submodules.get(module, [])
    if submodule_options:
        submodule = st.selectbox("Submodule", submodule_options)
    else:
        submodule = st.text_input("Submodule (none for this module)")

    title = st.text_input("Lesson Title")
    lesson_date = st.date_input("Lesson Date", datetime.today(), key="lesson_date")
    days_diff = (inspection_date - lesson_date).days
    st.info(f"Days between lesson and inspection: {days_diff} day(s)")

    if st.button("Save Inspection"):
        # Save logic here...
        messages.append(("success", f"Saved: {teacher} | {class_selected} | {inspection_date} | {module} | {submodule} | {title} | {lesson_date} | {days_diff} days"))

>>>>>>> 7a70e5efef2ce3ca2f1cdc291bf43c6062b79df7
    return messages