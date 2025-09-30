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
                st.dataframe(df_rapport)
            else:
                st.info("No rapport deliveries found.")

            # Devoir status
            st.markdown("**Devoir Status:**")
            devoirs = [d for d in get_devoir_entries() if d[0] == selected_teacher]
            if devoirs:
                df_devoir = pd.DataFrame(devoirs, columns=[
                    "Teacher", "Class", "Week (Thursday)", "Status", "Sent Date", "Days Late"
                ])
                st.dataframe(df_devoir)
            else:
                st.info("No devoir records found.")

            # Attendance
            st.markdown("**Attendance:**")
            attendance = get_attendance_for_teacher(selected_teacher)
            if attendance:
                df_attendance = pd.DataFrame(attendance, columns=["Date", "Status"])
                st.dataframe(df_attendance)
            else:
                st.info("No attendance records found.")

    # 2. Attendance Timeline
    elif submenu == "Attendance Timeline":
        st.subheader("Teachers Attendance Timeline")
        attendance_data = []
        for t in teachers:
            teacher_name = t[1]
            attendance = get_attendance_for_teacher(teacher_name)
            for record in attendance:
                attendance_data.append({"Teacher": teacher_name, "Date": record[0], "Status": record[1]})
        if attendance_data:
            df = pd.DataFrame(attendance_data)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            attendance_count = df.groupby(["Date", "Status"]).size().unstack(fill_value=0)
            st.line_chart(attendance_count)
            st.dataframe(df)
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
            st.dataframe(status_counts)
        else:
            st.info("No devoir records found.")

    # 4. Unique Level Check
    elif submenu == "Unique Level Check":
        st.subheader("Unique Level Check")
        df = pd.DataFrame(teachers, columns=["ID", "Name", "First Day", "Subject", "Assigned Classes", "Level"])
        duplicate_levels = df[df.duplicated("Level", keep=False)]
        if not duplicate_levels.empty:
            st.warning("Duplicate levels found!")
            st.dataframe(duplicate_levels[["Name", "Level"]])
        else:
            st.success("All levels are unique.")

    return []