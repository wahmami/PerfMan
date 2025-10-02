import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
import logging

def get_conn():
    cfg = st.secrets["postgres"]
    return psycopg2.connect(
        host=cfg["host"],
        dbname=c    fg["database"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg.get("port", 5432)
    )

# --- Test PostgreSQL connection ---
try:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            st.success(f"Connected! PostgreSQL version: {db_version[0]}")
except Exception as e:
    st.error(f"Connection failed: {e}")

def init_db():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                # Teachers
                c.execute("""
                    CREATE TABLE IF NOT EXISTS teachers (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        first_day TEXT,
                        subject TEXT,
                        assigned_classes TEXT,
                        level TEXT
                    )
                """)
                # Attendance
                c.execute("""
                    CREATE TABLE IF NOT EXISTS attendance (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT,
                        status TEXT NOT NULL,
                        UNIQUE(name, date)
                    )
                """)
                # Journal
                c.execute("""
                    CREATE TABLE IF NOT EXISTS journal (
                        id SERIAL PRIMARY KEY,
                        teacher_name TEXT NOT NULL,
                        date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        observation TEXT,
                        outdated_days INTEGER DEFAULT 0
                    )
                """)
                # Cahiers and uncorrected
                c.execute("""
                    CREATE TABLE IF NOT EXISTS cahiers (
                        id SERIAL PRIMARY KEY,
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
                        id SERIAL PRIMARY KEY,
                        cahier_id INTEGER REFERENCES cahiers(id) ON DELETE CASCADE,
                        lesson_date TEXT,
                        module TEXT,
                        title TEXT
                    )
                """)
                # Materials
                c.execute("""
                    CREATE TABLE IF NOT EXISTS materials (
                        id SERIAL PRIMARY KEY,
                        teacher_name TEXT NOT NULL,
                        material TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        date TEXT NOT NULL
                    )
                """)
                # Cahiers inspection
                c.execute("""
                    CREATE TABLE IF NOT EXISTS cahiers_inspection (
                        id SERIAL PRIMARY KEY,
                        teacher_name TEXT NOT NULL,
                        inspection_date TEXT NOT NULL,
                        module TEXT NOT NULL,
                        submodule TEXT,
                        title TEXT,
                        lesson_date TEXT NOT NULL,
                        days_difference INTEGER
                    )
                """)
                # Rapports and deliveries
                c.execute("""
                    CREATE TABLE IF NOT EXISTS rapports (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        due_date TEXT NOT NULL,
                        classes TEXT NOT NULL
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS rapport_deliveries (
                        id SERIAL PRIMARY KEY,
                        rapport_id INTEGER REFERENCES rapports(id) ON DELETE CASCADE,
                        teacher_name TEXT,
                        delivered_day TEXT,
                        delivered_classes TEXT,
                        days_late INTEGER
                    )
                """)
                # Devoir
                c.execute("""
                    CREATE TABLE IF NOT EXISTS devoir (
                        id SERIAL PRIMARY KEY,
                        teacher_name TEXT,
                        class_name TEXT,
                        thursday_date TEXT,
                        status TEXT,
                        sent_date TEXT,
                        days_late INTEGER
                    )
                """)
            conn.commit()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

def is_level_unique(level, exclude_teacher_id=None):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                if exclude_teacher_id:
                    c.execute("SELECT id FROM teachers WHERE level=%s AND id!=%s", (level, exclude_teacher_id))
                else:
                    c.execute("SELECT id FROM teachers WHERE level=%s", (level,))
                exists = c.fetchone()
                return exists is None
    except Exception as e:
        logging.error(f"Error checking level uniqueness: {e}")
        return False

def load_teachers():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT name FROM teachers ORDER BY name")
                teachers = [row[0] for row in c.fetchall()]
                return teachers
    except Exception as e:
        logging.error(f"Error loading teachers: {e}")
        return []

def add_teacher(name, first_day, subject, assigned_classes, level):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO teachers (name, first_day, subject, assigned_classes, level)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (name, first_day, subject, assigned_classes, level))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding teacher: {e}")

def get_all_teachers():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT id, name, first_day, subject, assigned_classes, level FROM teachers ORDER BY name")
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error loading all teachers: {e}")
        return []

def update_teacher(teacher_id, name, first_day, subject, assigned_classes, level):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute(
                    "UPDATE teachers SET name=%s, first_day=%s, subject=%s, assigned_classes=%s, level=%s WHERE id=%s",
                    (name, first_day, subject, assigned_classes, level, teacher_id)
                )
            conn.commit()
    except Exception as e:
        logging.error(f"Error updating teacher: {e}")

def delete_teacher(teacher_id):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("DELETE FROM teachers WHERE id=%s", (teacher_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"Error deleting teacher: {e}")

def check_existing_record(name, date):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT id FROM attendance WHERE name=%s AND date=%s", (name, date))
                row = c.fetchone()
                return row[0] if row else None
    except Exception as e:
        logging.error(f"Error checking existing record: {e}")
        return None

def save_attendance(name, date, time, status):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO attendance (name, date, time, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name, date) DO UPDATE SET time=EXCLUDED.time, status=EXCLUDED.status
                """, (name, date, time, status))
            conn.commit()
    except Exception as e:
        logging.error(f"Error saving attendance: {e}")

def load_today_attendance(date):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT name, date, time, status FROM attendance WHERE date=%s", (date,))
                records = c.fetchall()
                df = pd.DataFrame(records, columns=["Name", "Date", "Time", "Status"])
                return df
    except Exception as e:
        logging.error(f"Error loading today's attendance: {e}")
        return pd.DataFrame()

def add_journal_entry(teacher_name, date, status, observation, outdated_days):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO journal (teacher_name, date, status, observation, outdated_days)
                    VALUES (%s, %s, %s, %s, %s)
                """, (teacher_name, date, status, observation, outdated_days))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding journal entry: {e}")

def get_journal_entries(date=None):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                if date:
                    c.execute("SELECT teacher_name, date, status, observation, outdated_days FROM journal WHERE date=%s", (date,))
                else:
                    c.execute("SELECT teacher_name, date, status, observation, outdated_days FROM journal")
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error getting journal entries: {e}")
        return []

def init_cahiers_tables():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS cahiers (
                        id SERIAL PRIMARY KEY,
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
                        id SERIAL PRIMARY KEY,
                        cahier_id INTEGER REFERENCES cahiers(id) ON DELETE CASCADE,
                        lesson_date TEXT,
                        module TEXT,
                        title TEXT
                    )
                """)
            conn.commit()
    except Exception as e:
        logging.error(f"Error initializing cahiers tables: {e}")

def add_cahier_entry(teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation, uncorrected_lessons):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO cahiers (teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (teacher_name, inspection_date, last_corrected_date, last_corrected_module, last_corrected_title, observation))
                cahier_id = c.fetchone()[0]
                for lesson in uncorrected_lessons:
                    c.execute("""
                        INSERT INTO cahiers_uncorrected (cahier_id, lesson_date, module, title)
                        VALUES (%s, %s, %s, %s)
                    """, (cahier_id, lesson["date"], lesson["module"], lesson["title"]))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding cahier entry: {e}")

def get_cahier_entries():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    SELECT c.id, c.teacher_name, c.inspection_date, c.last_corrected_date, c.last_corrected_module, c.last_corrected_title, c.observation
                    FROM cahiers c
                    ORDER BY c.inspection_date DESC
                """)
                cahiers = c.fetchall()
                results = []
                for cahier in cahiers:
                    c.execute("SELECT lesson_date, module, title FROM cahiers_uncorrected WHERE cahier_id=%s", (cahier[0],))
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
                return results
    except Exception as e:
        logging.error(f"Error getting cahier entries: {e}")
        return []

def init_materials_table():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS materials (
                        id SERIAL PRIMARY KEY,
                        teacher_name TEXT NOT NULL,
                        material TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        date TEXT NOT NULL
                    )
                """)
            conn.commit()
    except Exception as e:
        logging.error(f"Error initializing materials table: {e}")

def add_material_entry(teacher_name, material, quantity, date):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO materials (teacher_name, material, quantity, date)
                    VALUES (%s, %s, %s, %s)
                """, (teacher_name, material, quantity, date))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding material entry: {e}")

def get_material_entries():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT teacher_name, material, quantity, date FROM materials ORDER BY date DESC")
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error getting material entries: {e}")
        return []

def add_cahiers_inspection(teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO cahiers_inspection
                    (teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding cahiers inspection: {e}")

def get_cahiers_inspections():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    SELECT teacher_name, inspection_date, module, submodule, title, lesson_date, days_difference
                    FROM cahiers_inspection
                    ORDER BY inspection_date DESC
                """)
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error getting cahiers inspections: {e}")
        return []

def add_rapport(title, due_date, classes):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("INSERT INTO rapports (title, due_date, classes) VALUES (%s, %s, %s)", (title, due_date, classes))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding rapport: {e}")

def get_rapports():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT id, title, due_date, classes FROM rapports ORDER BY due_date DESC")
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error getting rapports: {e}")
        return []

def add_rapport_delivery(rapport_id, teacher_name, delivered_day, delivered_classes, days_late):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO rapport_deliveries (rapport_id, teacher_name, delivered_day, delivered_classes, days_late)
                    VALUES (%s, %s, %s, %s, %s)
                """, (rapport_id, teacher_name, delivered_day, delivered_classes, days_late))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding rapport delivery: {e}")

def get_rapport_deliveries():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    SELECT r.title, r.due_date, d.teacher_name, d.delivered_day, d.delivered_classes, d.days_late
                    FROM rapport_deliveries d
                    JOIN rapports r ON d.rapport_id = r.id
                    ORDER BY d.delivered_day DESC
                """)
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error getting rapport deliveries: {e}")
        return []

def init_rapport_tables():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS rapports (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        due_date TEXT NOT NULL,
                        classes TEXT NOT NULL
                    )
                """)
                c.execute("""
                    CREATE TABLE IF NOT EXISTS rapport_deliveries (
                        id SERIAL PRIMARY KEY,
                        rapport_id INTEGER REFERENCES rapports(id) ON DELETE CASCADE,
                        teacher_name TEXT,
                        delivered_day TEXT,
                        delivered_classes TEXT,
                        days_late INTEGER
                    )
                """)
            conn.commit()
    except Exception as e:
        logging.error(f"Error initializing rapport tables: {e}")

def get_teacher_classes(teacher_name):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT assigned_classes FROM teachers WHERE name=%s", (teacher_name,))
                row = c.fetchone()
                if row and row[0]:
                    return [cls.strip() for cls in row[0].split(",") if cls.strip()]
                return []
    except Exception as e:
        logging.error(f"Error getting teacher classes: {e}")
        return []

def init_devoir_table():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS devoir (
                        id SERIAL PRIMARY KEY,
                        teacher_name TEXT,
                        class_name TEXT,
                        thursday_date TEXT,
                        status TEXT,
                        sent_date TEXT,
                        days_late INTEGER
                    )
                """)
            conn.commit()
    except Exception as e:
        logging.error(f"Error initializing devoir table: {e}")

def add_devoir_entry(teacher_name, class_name, thursday_date, status, sent_date, days_late):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    INSERT INTO devoir (teacher_name, class_name, thursday_date, status, sent_date, days_late)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (teacher_name, class_name, thursday_date, status, sent_date, days_late))
            conn.commit()
    except Exception as e:
        logging.error(f"Error adding devoir entry: {e}")

def get_devoir_entries():
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("""
                    SELECT teacher_name, class_name, thursday_date, status, sent_date, days_late
                    FROM devoir
                    ORDER BY thursday_date DESC
                """)
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error getting devoir entries: {e}")
        return []

def update_rapport(rapport_id, title, due_date, classes):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("UPDATE rapports SET title=%s, due_date=%s, classes=%s WHERE id=%s", (title, due_date, classes, rapport_id))
            conn.commit()
    except Exception as e:
        logging.error(f"Error updating rapport: {e}")

def delete_rapport(rapport_id):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("DELETE FROM rapports WHERE id=%s", (rapport_id,))
                c.execute("DELETE FROM rapport_deliveries WHERE rapport_id=%s", (rapport_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"Error deleting rapport: {e}")

def get_attendance_for_teacher(teacher_name):
    try:
        with get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SELECT date, status FROM attendance WHERE name=%s ORDER BY date ASC", (teacher_name,))
                return c.fetchall()
    except Exception as e:
        logging.error(f"Error getting attendance for teacher: {e}")
        return []
