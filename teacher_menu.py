import streamlit as st
from config import subjects, classes, level_options
from database import (
    add_teacher, get_all_teachers, update_teacher, delete_teacher, is_level_unique
)
from datetime import datetime
import pandas as pd

def teacher_menu():
    messages = []  # <-- Fix: define messages as an empty list

    st.header("👩‍🏫 Manage Teachers")

    # Add new teacher
    with st.expander("➕ Add New Teacher"):
        new_teacher = st.text_input("Name", key="add_name")
        new_first_day = st.date_input("First day at work", datetime.today(), key="add_first_day")
        new_subjects = st.multiselect("Subjects", subjects, key="add_subjects")
        new_classes = st.multiselect("Assigned Classes", classes, key="add_classes")
        new_level = st.selectbox("Level", level_options, key="add_level")
        if st.button("Add Teacher"):
            if not new_teacher.strip() or not new_level.strip():
                st.warning("Please enter a valid name and level.")
            elif not is_level_unique(new_level.strip().upper()):
                st.warning("Level must be unique. Please choose another level.")
            else:
                add_teacher(
                    new_teacher.strip(),
                    str(new_first_day),
                    ",".join(new_subjects),
                    ",".join(new_classes),
                    new_level.strip().upper()
                )
                st.success(f"Added teacher: {new_teacher.strip()}")

    # Edit or delete existing teachers
    teachers = get_all_teachers()
    if teachers:
        st.subheader("Edit or Delete Teacher")
        teacher_dict = {f"{t[1]} ({t[2] if t[2] else 'No start date'})": t for t in teachers}
        selected = st.selectbox("Select teacher", list(teacher_dict.keys()), key="edit_select")
        teacher_id, name, first_day, subject, assigned_classes, level = teacher_dict[selected]
        edit_name = st.text_input("Edit name", name, key="edit_name")
        edit_first_day = st.date_input(
            "Edit first day at work",
            datetime.strptime(first_day, "%Y-%m-%d") if first_day else datetime.today(),
            key="edit_first_day"
        )
        edit_subjects = st.multiselect(
            "Edit subjects",
            subjects,
            default=subject.split(",") if subject else [],
            key="edit_subjects"
        )
        edit_classes = st.multiselect(
            "Edit assigned classes",
            classes,
            default=assigned_classes.split(",") if assigned_classes else [],
            key="edit_classes"
        )
        edit_level = st.selectbox(
            "Edit level",
            level_options,
            index=level_options.index(level) if level in level_options else 0,
            key="edit_level"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Teacher"):
                if not edit_name.strip() or not edit_level.strip():
                    st.warning("Please enter a valid name and level.")
                elif not is_level_unique(edit_level.strip().upper(), teacher_id):
                    st.warning("Level must be unique. Please choose another level.")
                else:
                    update_teacher(
                        teacher_id,
                        edit_name.strip(),
                        str(edit_first_day),
                        ",".join(edit_subjects),
                        ",".join(edit_classes),
                        edit_level.strip().upper()
                    )
                    st.success("Teacher updated. Please refresh to see changes.")
        with col2:
            if st.button("Delete Teacher"):
                delete_teacher(teacher_id)
                st.success("Teacher deleted. Please refresh to see changes.")

        # List all teachers
        st.subheader("Current Teachers")
        df_teachers = pd.DataFrame(teachers, columns=["ID", "Name", "First Day", "Subject", "Assigned Classes", "Level"])
        st.dataframe(df_teachers.drop(columns=["ID"]))
    else:
        st.info("No teachers found.")
        
    return messages  # <-- Always return messages (even if empty)
