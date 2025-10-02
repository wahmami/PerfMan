import streamlit as st
from datetime import datetime
from database import get_all_teachers, add_material_entry, get_material_entries
from config import materials

def materials_menu():
    messages = []
    st.header("📦 Materials Distribution")

    teachers = get_all_teachers()
    teacher_names = [t[1] for t in teachers]
    if not teacher_names:
        messages.append(("warning", "No teachers found."))
        return messages

    with st.form("materials_form"):
        teacher = st.selectbox("Teacher", teacher_names)
        material = st.selectbox("Material", materials)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        date = st.date_input("Date", datetime.today())
        submitted = st.form_submit_button("Save Material Distribution")
        if submitted:
            add_material_entry(teacher, material, quantity, str(date))
            messages.append(("success", f"{quantity} {material}(s) given to {teacher} on {date}."))

    st.subheader("📋 Materials Distribution History")
    entries = get_material_entries()
    if entries:
        import pandas as pd
        df = pd.DataFrame(entries, columns=["Teacher", "Material", "Quantity", "Date"])
        st.data_editor(df, num_rows="dynamic", use_container_width=True)
    else:
        st.info("No materials distribution records yet.")

    return messages