import sqlite3

DB_PATH = "attendance.db"  # Adjust if your database file is elsewhere

def list_tables_and_columns(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Get all table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in c.fetchall()]
    print("Tables and columns in your database:\n")
    for table in tables:
        print(f"Table: {table}")
        c.execute(f"PRAGMA table_info({table});")
        columns = c.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        print()
    conn.close()

if __name__ == "__main__":
    list_tables_and_columns()