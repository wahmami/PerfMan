<<<<<<< HEAD
import streamlit as st
from datetime import datetime, timedelta
from database import get_all_teachers, get_teacher_classes, add_devoir_entry, get_devoir_entries

def get_next_thursday(date=None):
    if date is None:
        date = datetime.today()
    days_ahead = 3 - date.weekday()  # Thursday is weekday 3
    if days_ahead < 0:
        days_ahead += 7
    return (date + timedelta(days=days_ahead)).date()

def devoir_menu():
    messages = []
    st.header("📝 Devoir (Homework Check)")

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]
    if not teacher_names:
        messages.append(("warning", "No teachers found."))
        return messages

    teacher = st.selectbox("Teacher", teacher_names)
    teacher_classes = get_teacher_classes(teacher)
    if not teacher_classes:
        messages.append(("warning", "No classes found for this teacher."))
        return messages

    class_selected = st.selectbox("Class", teacher_classes)
    thursday_date = st.date_input("Week (Thursday)", get_next_thursday())
    status = st.selectbox("Devoir Status", ["Sent", "Not Sent", "Sent Late"])

    sent_date = None
    days_late = None
    if status == "Sent Late":
        sent_date = st.date_input("Actual Sent Date", thursday_date)
        days_late = (sent_date - thursday_date).days if sent_date > thursday_date else 0
        st.info(f"Days late: {days_late} day(s)" if days_late > 0 else "No delay.")

    if st.button("Save Devoir Check"):
        add_devoir_entry(
            teacher,
            class_selected,
            str(thursday_date),
            status,
            str(sent_date) if sent_date else None,
            days_late
        )
        messages.append(("success", "Devoir check saved."))

    st.subheader("Devoir History")
    entries = get_devoir_entries()
    if entries:
        import pandas as pd
        df = pd.DataFrame(entries, columns=[
            "Teacher", "Class", "Week (Thursday)", "Status", "Sent Date", "Days Late"
        ])
        st.data_editor(df, num_rows="dynamic", use_container_width=True)
    else:
        st.info("No devoir records yet.")

=======
import streamlit as st
from datetime import datetime, timedelta
from database import get_all_teachers, get_teacher_classes, add_devoir_entry, get_devoir_entries

def get_next_thursday(date=None):
    if date is None:
        date = datetime.today()
    days_ahead = 3 - date.weekday()  # Thursday is weekday 3
    if days_ahead < 0:
        days_ahead += 7
    return (date + timedelta(days=days_ahead)).date()

def devoir_menu():
    messages = []
    st.header("📝 Devoir (Homework Check)")

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]
    if not teacher_names:
        messages.append(("warning", "No teachers found."))
        return messages

    teacher = st.selectbox("Teacher", teacher_names)
    teacher_classes = get_teacher_classes(teacher)
    if not teacher_classes:
        messages.append(("warning", "No classes found for this teacher."))
        return messages

    class_selected = st.selectbox("Class", teacher_classes)
    thursday_date = st.date_input("Week (Thursday)", get_next_thursday())
    status = st.selectbox("Devoir Status", ["Sent", "Not Sent", "Sent Late"])

    sent_date = None
    days_late = None
    if status == "Sent Late":
        sent_date = st.date_input("Actual Sent Date", thursday_date)
        days_late = (sent_date - thursday_date).days if sent_date > thursday_date else 0
        st.info(f"Days late: {days_late} day(s)" if days_late > 0 else "No delay.")

    if st.button("Save Devoir Check"):
        add_devoir_entry(
            teacher,
            class_selected,
            str(thursday_date),
            status,
            str(sent_date) if sent_date else None,
            days_late
        )
        messages.append(("success", "Devoir check saved."))

    st.subheader("Devoir History")
    entries = get_devoir_entries()
    if entries:
        import pandas as pd
        df = pd.DataFrame(entries, columns=[
            "Teacher", "Class", "Week (Thursday)", "Status", "Sent Date", "Days Late"
        ])
        st.dataframe(df)
    else:
        st.info("No devoir records yet.")

>>>>>>> 7a70e5efef2ce3ca2f1cdc291bf43c6062b79df7
    return messages