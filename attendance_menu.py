import streamlit as st
from datetime import datetime, timedelta
from database import (
    get_all_teachers, load_teachers, check_existing_record,
    save_attendance, load_today_attendance
)

def attendance_menu():
    messages = []
    # Let user pick the date
    date = st.date_input("Date", datetime.today().date())
    date_str = str(date)
    df_today = load_today_attendance(date_str)
    all_teachers = load_teachers()
    if all_teachers:
        st.subheader("Sélectionnez un enseignant")
        selected_teacher = st.selectbox("Teacher", all_teachers)

        col1, col2 = st.columns(2)
        with col2:
            unsigned = st.checkbox("Mark as Unsigned", key="unsigned_att")
        with col1:
            # Initialize session state for time_att
            if "time_att" not in st.session_state:
                st.session_state.time_att = ""

            # Use st.columns with equal width for better alignment
            col_sub, col_time, col_add = st.columns([1, 2, 1], gap="small")

            # --- Handle buttons BEFORE text_input is created ---
            with col_sub:
                st.markdown("<div style='height: 1.9em'></div>", unsafe_allow_html=True)
                if st.button("-1 min", key="sub_minute", disabled=unsigned):
                    try:
                        t = datetime.strptime(st.session_state.time_att or "08:00", "%H:%M")
                        t -= timedelta(minutes=1)
                        st.session_state.time_att = t.strftime("%H:%M")
                    except Exception:
                        st.session_state.time_att = "08:00"
            with col_add:
                st.markdown("<div style='height: 1.9em'></div>", unsafe_allow_html=True)
                if st.button("+1 min", key="add_minute", disabled=unsigned):
                    try:
                        t = datetime.strptime(st.session_state.time_att or "08:00", "%H:%M")
                        t += timedelta(minutes=1)
                        st.session_state.time_att = t.strftime("%H:%M")
                    except Exception:
                        st.session_state.time_att = "08:00"
            with col_time:
                time_input = st.text_input(
                    label="",
                    value=st.session_state.time_att,
                    disabled=unsigned,
                    key="time_att",
                    placeholder="Enter Time (HH:MM)"
                )

        existing_row = check_existing_record(selected_teacher, date_str)
        if existing_row:
            messages.append(("warning", f"⚠️ Record already exists for {selected_teacher} on {date}. Saving will overwrite it."))

        if st.button("Save Attendance", key="save_att"):
            final_time = ""
            final_status = "Absent"

            if unsigned:
                final_status = "Unsigned"
            else:
                try:
                    entered_time = datetime.strptime(st.session_state.time_att, "%H:%M").time()
                    cutoff_time = datetime.strptime("08:30", "%H:%M").time()
                    final_time = st.session_state.time_att
                    if entered_time <= cutoff_time:
                        final_status = "Present"
                    else:
                        final_status = "Late"
                except ValueError:
                    messages.append(("error", "Please enter time in HH:MM format (e.g., 08:15)."))
                    return messages

            save_attendance(selected_teacher, date_str, final_time, final_status)
            messages.append(("success", f"Saved: {selected_teacher} on {date} → {final_status} {('at ' + final_time) if final_time else ''}"))

            # Update unsigned/absent teachers after saving attendance
            df_today = load_today_attendance(date_str)

        # Show unsigned/absent teachers at the top (in observations)
        present_or_late = set(df_today[df_today['Status'].isin(['Present', 'Late'])]['Name']) if not df_today.empty else set()
        unsigned_or_absent = [t for t in all_teachers if t not in present_or_late]
        if unsigned_or_absent:
            names_text = "\n".join(f"- {name}" for name in sorted(unsigned_or_absent))
            messages.append(("info", f"Teachers not signed in yet for {date}:\n{names_text}"))
        else:
            messages.append(("success", "All teachers have signed in for today!"))

        # Show today's attendance table
        st.subheader(f"📊 Attendance Records for {date}")
        if not df_today.empty:
            st.dataframe(df_today)
        else:
            st.info("No attendance records for today yet.")
    else:
        messages.append(("warning", "No teachers found. Please add teacher names using the 'Teacher' menu."))
    return messages