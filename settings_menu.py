import streamlit as st
import json
import os

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