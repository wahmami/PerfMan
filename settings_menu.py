import streamlit as st
import json
import os
from teacher_menu import teacher_menu  # Import your old teacher menu
from database import (
    add_rapport,
    get_rapports,
    update_rapport,
    delete_rapport
)
from config import classes, subjects, modules, submodules, materials

CONFIG_PATH = "config.py"

def load_config():
    import importlib.util
    spec = importlib.util.spec_from_file_location("config", CONFIG_PATH)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def save_config(subjects, classes, level_options, modules, submodules, materials):
    # Write the config.py file with updated values
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(f"subjects = {json.dumps(subjects, ensure_ascii=False)}\n")
        f.write(f"classes = {json.dumps(classes, ensure_ascii=False)}\n")
        f.write(f"level_options = {json.dumps(level_options, ensure_ascii=False)}\n")
        f.write(f"modules = {json.dumps(modules, ensure_ascii=False)}\n")
        f.write(f"submodules = {json.dumps(submodules, ensure_ascii=False, indent=4)}\n")
        f.write(f"materials = {json.dumps(materials, ensure_ascii=False)}\n")

def save_subjects(subjects_list):
    # Load current config
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Replace subjects line
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("subjects ="):
                f.write(f"subjects = {json.dumps(subjects_list, ensure_ascii=False)}\n")
            else:
                f.write(line)

def save_classes(classes_list):
    # Load current config
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Replace classes line
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("classes ="):
                f.write(f"classes = {json.dumps(classes_list, ensure_ascii=False)}\n")
            else:
                f.write(line)

def save_modules_and_submodules(modules_list, submodules_dict):
    # Load current config
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Replace modules and submodules lines
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("modules ="):
                f.write(f"modules = {json.dumps(modules_list, ensure_ascii=False)}\n")
            elif line.startswith("submodules ="):
                f.write(f"submodules = {json.dumps(submodules_dict, ensure_ascii=False, indent=4)}\n")
            else:
                f.write(line)

def settings_menu():
    messages = []
    st.header("⚙️ Settings (Config CRUD)")

    config = load_config()

    st.subheader("Subjects")
    subjects = st.text_area("Edit subjects (comma separated)", ", ".join(config.subjects)).split(",")
    subjects = [s.strip() for s in subjects if s.strip()]

    st.subheader("Classes")
    classes = st.text_area("Edit classes (comma separated)", ", ".join(config.classes)).split(",")
    classes = [c.strip() for c in classes if c.strip()]

    st.subheader("Level Options")
    level_options = st.text_area("Edit level options (comma separated)", ", ".join(config.level_options)).split(",")
    level_options = [l.strip() for l in level_options if l.strip()]

    st.subheader("Modules")
    modules = st.text_area("Edit modules (comma separated)", ", ".join(config.modules)).split(",")
    modules = [m.strip() for m in modules if m.strip()]

    st.subheader("Submodules")
    submodules = {}
    for module in modules:
        default = ", ".join(config.submodules.get(module, []))
        submodules[module] = st.text_area(f"Submodules for {module} (comma separated)", default).split(",")
        submodules[module] = [s.strip() for s in submodules[module] if s.strip()]

    st.subheader("Materials")
    materials = st.text_area("Edit materials (comma separated)", ", ".join(config.materials)).split(",")
    materials = [m.strip() for m in materials if m.strip()]

    if st.button("Save Settings"):
        save_config(subjects, classes, level_options, modules, submodules, materials)
        messages.append(("success", "Settings saved! Please restart the app to apply changes."))

    return messages

def settings_teachers_menu():
    # Use the old teacher menu for this submenu
    return teacher_menu()

def settings_rapport_menu():
    messages = []
    st.header("Settings - Rapport (CRUD)")

    # --- Create Rapport ---
    st.subheader("Create Rapport")
    rapport_title = st.text_input("Rapport Title")
    classes_selected = st.multiselect("Target Classes", classes)
    due_date = st.date_input("Due Date", st.session_state.get("rapport_due_date", None) or st.session_state.get("edit_due_date", None) or None)
    if st.button("Save Rapport"):
        if not rapport_title or not classes_selected:
            messages.append(("warning", "Please enter a title and select at least one class."))
        else:
            add_rapport(rapport_title, str(due_date), ", ".join(classes_selected))
            messages.append(("success", "Rapport saved."))

    # --- Manage Rapports (Edit/Delete) ---
    st.subheader("Manage Rapports")
    rapports = get_rapports()
    if rapports:
        rapport_options = [f"{r[1]} (Due: {r[2]})" for r in rapports]
        rapport_map = {f"{r[1]} (Due: {r[2]})": r for r in rapports}
        selected_rapport_display = st.selectbox("Select Rapport to Edit/Delete", rapport_options)
        selected_rapport = rapport_map[selected_rapport_display]
        rapport_id = selected_rapport[0]

        new_title = st.text_input("Edit Title", selected_rapport[1], key="edit_title")
        new_due_date = st.date_input("Edit Due Date", st.session_state.get("edit_due_date", None) or None, key="edit_due_date")
        if not new_due_date:
            new_due_date = st.date_input("Edit Due Date", st.session_state.get("rapport_due_date", None) or None, key="edit_due_date_fallback")
        new_classes = st.multiselect("Edit Classes", classes, default=selected_rapport[3].split(", "))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Rapport"):
                update_rapport(rapport_id, new_title, str(new_due_date), ", ".join(new_classes))
                messages.append(("success", "Rapport updated."))
        with col2:
            if st.button("Delete Rapport"):
                delete_rapport(rapport_id)
                messages.append(("success", "Rapport deleted."))
                st.rerun()

    else:
        st.info("No rapports found. Please create a rapport first.")

    return messages

def settings_subjects_menu():
    messages = []
    st.header("Settings - Subjects")

    # Display current subjects
    st.subheader("Current Subjects")
    st.write(", ".join(subjects))

    # Add new subject
    new_subject = st.text_input("Add a new subject")
    if st.button("Add Subject"):
        if new_subject.strip() and new_subject.strip() not in subjects:
            subjects.append(new_subject.strip())
            save_subjects(subjects)
            messages.append(("success", f"Added subject: {new_subject.strip()}"))
        else:
            messages.append(("warning", "Subject is empty or already exists."))

    # Edit subjects (simple text area for bulk edit)
    st.subheader("Edit Subjects (comma separated)")
    edited_subjects = st.text_area("Subjects", ", ".join(subjects))
    if st.button("Save Subjects"):
        subjects_list = [s.strip() for s in edited_subjects.split(",") if s.strip()]
        save_subjects(subjects_list)
        messages.append(("success", "Subjects updated! Please restart the app to see changes."))

    return messages

def settings_classes_menu():
    messages = []
    st.header("Settings - Classes")

    # Display current classes
    st.subheader("Current Classes")
    st.write(", ".join(classes))

    # Add new class
    new_class = st.text_input("Add a new class")
    if st.button("Add Class"):
        if new_class.strip() and new_class.strip() not in classes:
            classes.append(new_class.strip())
            save_classes(classes)
            messages.append(("success", f"Added class: {new_class.strip()}"))
        else:
            messages.append(("warning", "Class is empty or already exists."))

    # Edit classes (simple text area for bulk edit)
    st.subheader("Edit Classes (comma separated)")
    edited_classes = st.text_area("Classes", ", ".join(classes))
    if st.button("Save Classes"):
        classes_list = [c.strip() for c in edited_classes.split(",") if c.strip()]
        save_classes(classes_list)
        messages.append(("success", "Classes updated! Please restart the app to see changes."))

    return messages

def settings_modules_menu():
    messages = []
    st.header("Settings - Modules & Submodules")

    # Display current modules
    st.subheader("Current Modules")
    st.write(", ".join(modules))

    # Add new module
    new_module = st.text_input("Add a new module")
    if st.button("Add Module"):
        if new_module.strip() and new_module.strip() not in modules:
            modules.append(new_module.strip())
            submodules[new_module.strip()] = []
            save_modules_and_submodules(modules, submodules)
            messages.append(("success", f"Added module: {new_module.strip()}"))
        else:
            messages.append(("warning", "Module is empty or already exists."))

    # Edit modules (bulk edit)
    st.subheader("Edit Modules (comma separated)")
    edited_modules = st.text_area("Modules", ", ".join(modules))
    if st.button("Save Modules"):
        modules_list = [m.strip() for m in edited_modules.split(",") if m.strip()]
        # Remove submodules for deleted modules
        submodules_dict = {m: submodules.get(m, []) for m in modules_list}
        save_modules_and_submodules(modules_list, submodules_dict)
        messages.append(("success", "Modules updated! Please restart the app to see changes."))

    # Edit submodules for each module
    st.subheader("Edit Submodules")
    submodules_dict = {}
    for module in modules:
        current_subs = submodules.get(module, [])
        edited_subs = st.text_area(f"Submodules for {module} (comma separated)", ", ".join(current_subs), key=f"sub_{module}")
        submodules_dict[module] = [s.strip() for s in edited_subs.split(",") if s.strip()]

    if st.button("Save Submodules"):
        save_modules_and_submodules(modules, submodules_dict)
        messages.append(("success", "Submodules updated! Please restart the app to see changes."))

    return messages

def save_materials(materials_list):
    # Load current config
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Replace materials line
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("materials ="):
                f.write(f"materials = {json.dumps(materials_list, ensure_ascii=False)}\n")
            else:
                f.write(line)

def settings_materials_menu():
    messages = []
    st.header("Settings - Materials")

    # Display current materials
    st.subheader("Current Materials")
    st.write(", ".join(materials))

    # Add new material
    new_material = st.text_input("Add a new material")
    if st.button("Add Material"):
        if new_material.strip() and new_material.strip() not in materials:
            materials.append(new_material.strip())
            save_materials(materials)
            messages.append(("success", f"Added material: {new_material.strip()}"))
        else:
            messages.append(("warning", "Material is empty or already exists."))

    # Edit materials (bulk edit)
    st.subheader("Edit Materials (comma separated)")
    edited_materials = st.text_area("Materials", ", ".join(materials))
    if st.button("Save Materials"):
        materials_list = [m.strip() for m in edited_materials.split(",") if m.strip()]
        save_materials(materials_list)
        messages.append(("success", "Materials updated! Please restart the app to see changes."))

    return messages