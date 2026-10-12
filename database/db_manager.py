import sqlite3


class DatabaseManager:

    def __init__(self, db_name="database/job_copilot.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def execute(self, query, params=()):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(query, params)

        conn.commit()

        conn.close()

    def fetch_all(self, query, params=()):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(query, params)

        rows = cursor.fetchall()

        conn.close()

        return rows