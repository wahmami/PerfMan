import streamlit as st
import psycopg2
import pandas as pd
import logging

# --- Test PostgreSQL connection with psycopg2 ---
try:
    conn = psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        port=st.secrets["postgres"]["port"]
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    st.success(f"Connected! PostgreSQL version: {db_version[0]}")
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Connection failed: {e}")

DB_PATH = "attendance.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                first_day TEXT,
                subject TEXT,
                assigned_classes TEXT,
                level TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                status TEXT NOT NULL,
                UNIQUE(name, date)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                observation TEXT,
                outdated_days INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS cahiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                inspection_date TEXT NOT NULL,
                last_corrected_date TEXT,
                last_corrected_module TEXT,
                last_corrected_title TEXT,
                observation TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS cahiers_uncorrected (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cahier_id INTEGER,
                lesson_date TEXT,
                module TEXT,
                title TEXT,
                FOREIGN KEY (cahier_id) REFERENCES cahiers(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                material TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS cahiers_inspection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                inspection_date TEXT NOT NULL,
                module TEXT NOT NULL,
                submodule TEXT,
                title TEXT,
                lesson_date TEXT NOT NULL,
                days_difference INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS rapports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL,
                classes TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS rapport_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rapport_id INTEGER,
                teacher_name TEXT,
                delivered_day TEXT,
                delivered_classes TEXT,
                days_late INTEGER,
                FOREIGN KEY (rapport_id) REFERENCES rapports(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS devoir (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT,
                class_name TEXT,
                thursday_date TEXT,
                status TEXT,
                sent_date TEXT,
                days_late INTEGER
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

def is_level_unique(level, exclude_teacher_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if exclude_teacher_id:
        c.execute("SELECT id FROM teachers WHERE level=? AND id!=?", (level, exclude_teacher_id))
    else:
        c.execute("SELECT id FROM teachers WHERE level=?", (level,))
    exists = c.fetchone()
    conn.close()
    return exists is None

def load_teachers():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM teachers ORDER BY name")
        teachers = [row[0] for row in c.fetchall()]
        conn.close()
        return teachers
    except Exception as e:
        logging.error(f"Error loading teachers: {e}")
        return []

def add_teacher(name, first_day, subject, assigned_classes, level):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO teachers (name, first_day, subject, assigned_classes, level)
        VALUES (?, ?, ?, ?, ?)
    """, (name, first_day, subject, assigned_classes, level))
    conn.commit()
    conn.close()

def get_all_teachers():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM teachers")
    rows = c.fetchall()
    conn.close()
    return rows

def update_teacher(teacher_id, name, first_day, subject, assigned_classes, level):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE teachers SET name=?, first_day=?, subject=?, assigned_classes=?, level=? WHERE id=?",
            (name, first_day, subject, assigned_classes, level, teacher_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error updating teacher: {e}")

def delete_teacher(teacher_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error deleting teacher: {e}")

def check_existing_record(name, date):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM attendance WHERE name=? AND date=?", (name, date))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logging.error(f"Error checking existing record: {e}")
        return None

def save_attendance(name, date, time, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO attendance (name, date, time, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name, date) DO UPDATE SET time=excluded.time, status=excluded.status
        """, (name, date, time, status))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error saving attendance: {e}")

def load_today_attendance(date):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, date, time, status FROM attendance WHERE date=?", (date,))
        records = c.fetchall()
        conn.close()
        df = pd.DataFrame(records, columns=["Name", "Date", "Time", "Status"])
        return df
    except Exception as e:
        logging.error(f"Error loading today's attendance: {e}")
        return pd.DataFrame()

def add_journal_entry(teacher_name, date, status, observation, outdated_days):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO journal (teacher_name, date, status, observation, outdated_days)
        VALUES (?, ?, ?, ?, ?)
    """, (teacher_name, date, status, observation, outdated_days))
    conn.commit()
    conn.close()

def get_journal_entries(date=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if date:
        c.execute("SELECT teacher_name, date, status, observation, outdated_days FROM journal WHERE date=?", (date,))
    else:
        c.execute("SELECT teacher_name, date, status, observation, outdated_days FROM journal")
    rows = c.fetchall()
    conn.close()
    return rows

def init_cahiers_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cahiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            inspection_date TEXT NOT NULL,
            last_corrected_date TEXT,
            last_corrected_module TEXT,
            last_corrected_title TEXT,
            observation TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cahiers_uncorrected (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cahier_id INTEGER,
            lesson_date TEXT,
            module TEXT,
            title TEXT,
            FOREIGN KEY (cahier_id) REFERENCES cahiers(id)
        )
    """)
    conn.commit()
    conn.close()

def add_cahier_entry(teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation, uncorrected_lessons):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO cahiers (teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation))
    cahier_id = c.lastrowid
    for lesson in uncorrected_lessons:
        c.execute("""
            INSERT INTO cahiers_uncorrected (cahier_id, lesson_date, module, title)
            VALUES (?, ?, ?, ?)
        """, (cahier_id, lesson["date"], lesson["module"], lesson["title"]))
    conn.commit()
    conn.close()

def get_cahier_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT c.id, c.teacher_name, c.inspection_date, c.last_corrected_date, c.last_corrected_module, c.last_corrected_title, c.observation
        FROM cahiers c
        ORDER BY c.inspection_date DESC
    """)
    cahiers = c.fetchall()
    results = []
    for cahier in cahiers:
        c.execute("""
            SELECT lesson_date, module, title FROM cahiers_uncorrected WHERE cahier_id=?
        """, (cahier[0],))
        uncorrected = c.fetchall()
        results.append({
            "id": cahier[0],
            "teacher_name": cahier[1],
            "inspection_date": cahier[2],
            "last_corrected_date": cahier[3],
            "last_corrected_module": cahier[4],
            "last_corrected_title": cahier[5],
            "observation": cahier[6],
            "uncorrected": uncorrected
        })
    conn.close()
    return results

def init_materials_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            material TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_material_entry(teacher_name, material, quantity, date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO materials (teacher_name, material, quantity, date)
        VALUES (?, ?, ?, ?)
    """, (teacher_name, material, quantity, date))
    conn.commit()
    conn.close()

def get_material_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT teacher_name, material, quantity, date
        FROM materials
        ORDER BY date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def add_cahiers_inspection(teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO cahiers_inspection
        (teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference))
    conn.commit()
    conn.close()

def get_cahiers_inspections():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference
        FROM cahiers_inspection
        ORDER BY inspection_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def add_rapport(title, due_date, classes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO rapports (title, due_date, classes)
        VALUES (?, ?, ?)
    """, (title, due_date, classes))
    conn.commit()
    conn.close()

def get_rapports():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, due_date, classes FROM rapports ORDER BY due_date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_rapport_delivery(rapport_id, teacher_name, delivered_day, delivered_classes, days_late):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO rapport_deliveries (rapport_id, teacher_name, delivered_day, delivered_classes, days_late)
        VALUES (?, ?, ?, ?, ?)
    """, (rapport_id, teacher_name, delivered_day, delivered_classes, days_late))
    conn.commit()
    conn.close()

def get_rapport_deliveries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT r.title, r.due_date, d.teacher_name, d.delivered_day, d.delivered_classes, d.days_late
        FROM rapport_deliveries d
        JOIN rapports r ON d.rapport_id = r.id
        ORDER BY d.delivered_day DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def init_rapport_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS rapports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            classes TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rapport_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rapport_id INTEGER,
            teacher_name TEXT,
            delivered_day TEXT,
            delivered_classes TEXT,
            days_late INTEGER,
            FOREIGN KEY (rapport_id) REFERENCES rapports(id)
        )
    """)
    conn.commit()
    conn.close()

def get_teacher_classes(teacher_name):
    # Return a list of classes assigned to the teacher
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_classes FROM teachers WHERE name=?", (teacher_name,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return [cls.strip() for cls in row[0].split(",") if cls.strip()]
    return []

def init_devoir_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS devoir (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT,
            class_name TEXT,
            thursday_date TEXT,
            status TEXT,
            sent_date TEXT,
            days_late INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_devoir_entry(teacher_name, class_name, thursday_date, status, sent_date, days_late):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO devoir (teacher_name, class_name, thursday_date, status, sent_date, days_late)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (teacher_name, class_name, thursday_date, status, sent_date, days_late))
    conn.commit()
    conn.close()

def get_devoir_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT teacher_name, class_name, thursday_date, status, sent_date, days_late
        FROM devoir
        ORDER BY thursday_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def update_rapport(rapport_id, title, due_date, classes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE rapports SET title=?, due_date=?, classes=? WHERE id=?
    """, (title, due_date, classes, rapport_id))
    conn.commit()
    conn.close()

def delete_rapport(rapport_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM rapports WHERE id=?", (rapport_id,))
    c.execute("DELETE FROM rapport_deliveries WHERE rapport_id=?", (rapport_id,))
    conn.commit()
    conn.close()

def get_attendance_for_teacher(teacher_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT date, status FROM attendance
        WHERE name=?
        ORDER BY date ASC
    """, (teacher_name,))
    rows = c.fetchall()
    conn.close()
=======
import sqlite3
import pandas as pd
import logging

DB_PATH = "attendance.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                first_day TEXT,
                subject TEXT,
                assigned_classes TEXT,
                level TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                status TEXT NOT NULL,
                UNIQUE(name, date)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                observation TEXT,
                outdated_days INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS cahiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                inspection_date TEXT NOT NULL,
                last_corrected_date TEXT,
                last_corrected_module TEXT,
                last_corrected_title TEXT,
                observation TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS cahiers_uncorrected (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cahier_id INTEGER,
                lesson_date TEXT,
                module TEXT,
                title TEXT,
                FOREIGN KEY (cahier_id) REFERENCES cahiers(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                material TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS cahiers_inspection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                inspection_date TEXT NOT NULL,
                module TEXT NOT NULL,
                submodule TEXT,
                title TEXT,
                lesson_date TEXT NOT NULL,
                days_difference INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS rapports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL,
                classes TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS rapport_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rapport_id INTEGER,
                teacher_name TEXT,
                delivered_day TEXT,
                delivered_classes TEXT,
                days_late INTEGER,
                FOREIGN KEY (rapport_id) REFERENCES rapports(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS devoir (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT,
                class_name TEXT,
                thursday_date TEXT,
                status TEXT,
                sent_date TEXT,
                days_late INTEGER
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

def is_level_unique(level, exclude_teacher_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if exclude_teacher_id:
        c.execute("SELECT id FROM teachers WHERE level=? AND id!=?", (level, exclude_teacher_id))
    else:
        c.execute("SELECT id FROM teachers WHERE level=?", (level,))
    exists = c.fetchone()
    conn.close()
    return exists is None

def load_teachers():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM teachers ORDER BY name")
        teachers = [row[0] for row in c.fetchall()]
        conn.close()
        return teachers
    except Exception as e:
        logging.error(f"Error loading teachers: {e}")
        return []

def add_teacher(name, first_day, subject, assigned_classes, level):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO teachers (name, first_day, subject, assigned_classes, level) VALUES (?, ?, ?, ?, ?)",
            (name, first_day, subject, assigned_classes, level)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error adding teacher: {e}")

def get_all_teachers():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, first_day, subject, assigned_classes, level FROM teachers ORDER BY name")
        teachers = c.fetchall()
        conn.close()
        return teachers
    except Exception as e:
        logging.error(f"Error loading all teachers: {e}")
        return []

def update_teacher(teacher_id, name, first_day, subject, assigned_classes, level):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE teachers SET name=?, first_day=?, subject=?, assigned_classes=?, level=? WHERE id=?",
            (name, first_day, subject, assigned_classes, level, teacher_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error updating teacher: {e}")

def delete_teacher(teacher_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error deleting teacher: {e}")

def check_existing_record(name, date):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM attendance WHERE name=? AND date=?", (name, date))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logging.error(f"Error checking existing record: {e}")
        return None

def save_attendance(name, date, time, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO attendance (name, date, time, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name, date) DO UPDATE SET time=excluded.time, status=excluded.status
        """, (name, date, time, status))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error saving attendance: {e}")

def load_today_attendance(date):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, date, time, status FROM attendance WHERE date=?", (date,))
        records = c.fetchall()
        conn.close()
        df = pd.DataFrame(records, columns=["Name", "Date", "Time", "Status"])
        return df
    except Exception as e:
        logging.error(f"Error loading today's attendance: {e}")
        return pd.DataFrame()

def add_journal_entry(teacher_name, date, status, observation, outdated_days):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO journal (teacher_name, date, status, observation, outdated_days)
        VALUES (?, ?, ?, ?, ?)
    """, (teacher_name, date, status, observation, outdated_days))
    conn.commit()
    conn.close()

def get_journal_entries(date=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if date:
        c.execute("SELECT teacher_name, date, status, observation, outdated_days FROM journal WHERE date=?", (date,))
    else:
        c.execute("SELECT teacher_name, date, status, observation, outdated_days FROM journal")
    rows = c.fetchall()
    conn.close()
    return rows

def init_cahiers_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cahiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            inspection_date TEXT NOT NULL,
            last_corrected_date TEXT,
            last_corrected_module TEXT,
            last_corrected_title TEXT,
            observation TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cahiers_uncorrected (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cahier_id INTEGER,
            lesson_date TEXT,
            module TEXT,
            title TEXT,
            FOREIGN KEY (cahier_id) REFERENCES cahiers(id)
        )
    """)
    conn.commit()
    conn.close()

# Call this in init_db()
def init_db():
    # ...existing code...
    init_cahiers_tables()
    init_materials_table()
    init_rapport_tables()
    init_devoir_table()
    # ...existing code...

def add_cahier_entry(teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation, uncorrected_lessons):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO cahiers (teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation))
    cahier_id = c.lastrowid
    for lesson in uncorrected_lessons:
        c.execute("""
            INSERT INTO cahiers_uncorrected (cahier_id, lesson_date, module, title)
            VALUES (?, ?, ?, ?)
        """, (cahier_id, lesson["date"], lesson["module"], lesson["title"]))
    conn.commit()
    conn.close()

def get_cahier_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT c.id, c.teacher_name, c.inspection_date, c.last_corrected_date, c.last_corrected_module, c.last_corrected_title, c.observation
        FROM cahiers c
        ORDER BY c.inspection_date DESC
    """)
    cahiers = c.fetchall()
    results = []
    for cahier in cahiers:
        c.execute("""
            SELECT lesson_date, module, title FROM cahiers_uncorrected WHERE cahier_id=?
        """, (cahier[0],))
        uncorrected = c.fetchall()
        results.append({
            "id": cahier[0],
            "teacher_name": cahier[1],
            "inspection_date": cahier[2],
            "last_corrected_date": cahier[3],
            "last_corrected_module": cahier[4],
            "last_corrected_title": cahier[5],
            "observation": cahier[6],
            "uncorrected": uncorrected
        })
    conn.close()
    return results

def init_materials_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            material TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_material_entry(teacher_name, material, quantity, date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO materials (teacher_name, material, quantity, date)
        VALUES (?, ?, ?, ?)
    """, (teacher_name, material, quantity, date))
    conn.commit()
    conn.close()

def get_material_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT teacher_name, material, quantity, date
        FROM materials
        ORDER BY date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def add_cahiers_inspection(teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO cahiers_inspection
        (teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference))
    conn.commit()
    conn.close()

def get_cahiers_inspections():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference
        FROM cahiers_inspection
        ORDER BY inspection_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def add_rapport(title, due_date, classes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO rapports (title, due_date, classes)
        VALUES (?, ?, ?)
    """, (title, due_date, classes))
    conn.commit()
    conn.close()

def get_rapports():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, due_date, classes FROM rapports ORDER BY due_date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_rapport_delivery(rapport_id, teacher_name, delivered_day, delivered_classes, days_late):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO rapport_deliveries (rapport_id, teacher_name, delivered_day, delivered_classes, days_late)
        VALUES (?, ?, ?, ?, ?)
    """, (rapport_id, teacher_name, delivered_day, delivered_classes, days_late))
    conn.commit()
    conn.close()

def get_rapport_deliveries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT r.title, r.due_date, d.teacher_name, d.delivered_day, d.delivered_classes, d.days_late
        FROM rapport_deliveries d
        JOIN rapports r ON d.rapport_id = r.id
        ORDER BY d.delivered_day DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def init_rapport_tables():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS rapports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            classes TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rapport_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rapport_id INTEGER,
            teacher_name TEXT,
            delivered_day TEXT,
            delivered_classes TEXT,
            days_late INTEGER,
            FOREIGN KEY (rapport_id) REFERENCES rapports(id)
        )
    """)
    conn.commit()
    conn.close()

def get_teacher_classes(teacher_name):
    # Return a list of classes assigned to the teacher
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_classes FROM teachers WHERE name=?", (teacher_name,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return [cls.strip() for cls in row[0].split(",") if cls.strip()]
    return []

def init_devoir_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS devoir (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT,
            class_name TEXT,
            thursday_date TEXT,
            status TEXT,
            sent_date TEXT,
            days_late INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_devoir_entry(teacher_name, class_name, thursday_date, status, sent_date, days_late):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO devoir (teacher_name, class_name, thursday_date, status, sent_date, days_late)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (teacher_name, class_name, thursday_date, status, sent_date, days_late))
    conn.commit()
    conn.close()

def get_devoir_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT teacher_name, class_name, thursday_date, status, sent_date, days_late
        FROM devoir
        ORDER BY thursday_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def update_rapport(rapport_id, title, due_date, classes):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE rapports SET title=?, due_date=?, classes=? WHERE id=?
    """, (title, due_date, classes, rapport_id))
    conn.commit()
    conn.close()

def delete_rapport(rapport_id):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM rapports WHERE id=?", (rapport_id,))
    c.execute("DELETE FROM rapport_deliveries WHERE rapport_id=?", (rapport_id,))
    conn.commit()
    conn.close()

def get_attendance_for_teacher(teacher_name):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT date, status FROM attendance
        WHERE name=?
        ORDER BY date ASC
    """, (teacher_name,))
    rows = c.fetchall()
    conn.close()
>>>>>>> 7a70e5efef2ce3ca2f1cdc291bf43c6062b79df7
    return rows
