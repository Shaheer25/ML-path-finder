import sqlite3

def init_db():
    with sqlite3.connect("gmapsdb.db") as conn:
        c = conn.cursor()

        # Table to store travel time
        c.execute("""
                    CREATE TABLE IF NOT EXISTS travel_time (
                        time_id INTEGER PRIMARY KEY NOT NULL,
                        time INTEGER
                    );    
                """)
        conn.commit()

        # Table to store user data
        c.execute("""
                    CREATE TABLE IF NOT EXISTS EMPLOYEE(
                        emp_name TEXT PRIMARY KEY NOT NULL,
                        emp_address TEXT,
                        emp_phone TEXT,
                        emp_email TEXT,
                        emp_password TEXT
                    );    
                """)
        conn.commit()

init_db()