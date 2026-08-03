import sqlite3
from datetime import datetime


class ApplicationTracker:

    def __init__(self, db_path="database/job_copilot.db"):
        self.db_path = db_path
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT,

            title TEXT,

            location TEXT,

            status TEXT,

            applied_date TEXT,

            notes TEXT

        )
        """)

        conn.commit()
        conn.close()

    def add_application(
        self,
        company,
        title,
        location,
        status="Applied",
        notes=""
    ):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO applications
        (
            company,
            title,
            location,
            status,
            applied_date,
            notes
        )
        VALUES (?,?,?,?,?,?)
        """,
        (
            company,
            title,
            location,
            status,
            datetime.now().strftime("%Y-%m-%d"),
            notes
        ))

        conn.commit()
        conn.close()

    def get_all(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            company,
            title,
            location,
            status,
            applied_date
        FROM applications
        ORDER BY applied_date DESC
        """)

        rows = cursor.fetchall()

        conn.close()

        return rows


if __name__ == "__main__":

    tracker = ApplicationTracker()

    tracker.add_application(
        "Infosys",
        "Data Analyst",
        "Bangalore"
    )

    print()

    for application in tracker.get_all():

        print(application)