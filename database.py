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

# Call this in your init_db()
def init_db():
    # ...existing code...
    init_materials_table()
    # ...existing code...

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