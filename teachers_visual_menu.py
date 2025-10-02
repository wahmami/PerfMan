import streamlit as st
import pandas as pd
from database import get_all_teachers, get_attendance_for_teacher, get_rapport_deliveries, get_devoir_entries
from config import subjects, classes

def teachers_visual_menu():
    st.header("👩‍🏫 Teachers Data Visualizations")
    submenu = st.radio(
        "Select Visualization",
        [
            "Teacher Details",
            "Attendance Timeline",
            "Devoir Status",
            "Unique Level Check"
        ]
    )

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]

    # 1. Teacher Details
    if submenu == "Teacher Details":
        st.subheader("Teacher Details")
        selected_teacher = st.selectbox("Select Teacher", teacher_names)
        teacher_info = next((t for t in teachers if t[1] == selected_teacher), None)
        if teacher_info:
            st.write(f"**Name:** {teacher_info[1]}")
            st.write(f"**First Day:** {teacher_info[2]}")
            st.write(f"**Subjects:** {teacher_info[3]}")
            st.write(f"**Assigned Classes:** {teacher_info[4]}")
            st.write(f"**Level:** {teacher_info[5]}")

            # Rapport deliveries
            st.markdown("**Rapport Deliveries:**")
            rapport_deliveries = [d for d in get_rapport_deliveries() if d[2] == selected_teacher]
            if rapport_deliveries:
                df_rapport = pd.DataFrame(rapport_deliveries, columns=[
                    "Rapport Title", "Due Date", "Teacher", "Delivered Day", "Delivered Classes", "Days Late"
                ])
                st.data_editor(df_rapport, num_rows="dynamic", use_container_width=True)
            else:
                st.info("No rapport deliveries found.")

            # Devoir status
            st.markdown("**Devoir Status:**")
            devoirs = [d for d in get_devoir_entries() if d[0] == selected_teacher]
            if devoirs:
                df_devoir = pd.DataFrame(devoirs, columns=[
                    "Teacher", "Class", "Week (Thursday)", "Status", "Sent Date", "Days Late"
                ])
                st.data_editor(df_devoir, num_rows="dynamic", use_container_width=True)
            else:
                st.info("No devoir records found.")

            # Attendance
            st.markdown("**Attendance:**")
            attendance = get_attendance_for_teacher(selected_teacher)
            if attendance:
                df_attendance = pd.DataFrame(attendance, columns=["Date", "Status"])
                st.data_editor(df_attendance, num_rows="dynamic", use_container_width=True)
            else:
                st.info("No attendance records found.")

    # 2. Attendance Timeline
    elif submenu == "Attendance Timeline":
        st.subheader("Teacher Attendance Timeline")
        selected_teacher = st.selectbox("Select Teacher for Attendance", teacher_names, key="timeline_teacher")
        attendance = get_attendance_for_teacher(selected_teacher)
        if attendance:
            # Detect if attendance has 2 or 3 columns
            if len(attendance[0]) == 3:
                df = pd.DataFrame(attendance, columns=["Date", "Status", "Time"])
            else:
                df = pd.DataFrame(attendance, columns=["Date", "Status"])
                df["Time"] = ""  # Add empty Time column if missing

            def get_color(row):
                try:
                    t = pd.to_datetime(row["Time"], format="%H:%M").time()
                    if t < pd.to_datetime("08:31", format="%H:%M").time():
                        return "background-color: #d4edda"  # green
                    elif t < pd.to_datetime("08:45", format="%H:%M").time():
                        return "background-color: #fff3cd"  # orange
                    else:
                        return "background-color: #f8d7da"  # red
                except:
                    return ""
            styled_df = df.style.applymap(get_color, subset=["Time"])
            st.data_editor(styled_df, num_rows="dynamic", use_container_width=True)
        else:
            st.info("No attendance records found.")

    # 3. Devoir Status
    elif submenu == "Devoir Status":
        st.subheader("Devoir Status Overview")
        devoirs = get_devoir_entries()
        if devoirs:
            df = pd.DataFrame(devoirs, columns=[
                "Teacher", "Class", "Week (Thursday)", "Status", "Sent Date", "Days Late"
            ])
            status_counts = df.groupby(["Teacher", "Status"]).size().unstack(fill_value=0)
            st.bar_chart(status_counts)
            st.data_editor(status_counts, num_rows="dynamic", use_container_width=True)
        else:
            st.info("No devoir records found.")

    # 4. Unique Level Check
    elif submenu == "Unique Level Check":
        st.subheader("Unique Level Check")
        df = pd.DataFrame(teachers, columns=["ID", "Name", "First Day", "Subject", "Assigned Classes", "Level"])
        duplicate_levels = df[df.duplicated("Level", keep=False)]
        if not duplicate_levels.empty:
            st.warning("Duplicate levels found!")
            st.data_editor(duplicate_levels[["Name", "Level"]], num_rows="dynamic", use_container_width=True)
        else:
            st.success("All levels are unique.")

    return []