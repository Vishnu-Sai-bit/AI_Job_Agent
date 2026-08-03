import sqlite3

DB_PATH = "database/job_copilot.db"


class JobRepository:

    @staticmethod
    def get_connection():

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        return conn

    @staticmethod
    def get_all_jobs():

        try:

            with JobRepository.get_connection() as conn:

                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        id,
                        title,
                        company,
                        location,
                        source,
                        url
                    FROM jobs
                    ORDER BY id ASC
                """)

                rows = cursor.fetchall()

                return [dict(row) for row in rows]

        except sqlite3.Error as e:

            print("Database Error:", e)

            return []

    @staticmethod
    def search_jobs(keyword=""):

        try:

            with JobRepository.get_connection() as conn:

                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        id,
                        title,
                        company,
                        location,
                        source,
                        url
                    FROM jobs
                    WHERE
                        title LIKE ?
                        OR company LIKE ?
                        OR location LIKE ?
                        OR source LIKE ?
                    ORDER BY id ASC
                """, (

                    f"%{keyword}%",

                    f"%{keyword}%",

                    f"%{keyword}%",

                    f"%{keyword}%"

                ))

                rows = cursor.fetchall()

                return [dict(row) for row in rows]

        except sqlite3.Error as e:

            print("Database Error:", e)

            return []

    @staticmethod
    def get_jobs_by_location(location):

        try:

            with JobRepository.get_connection() as conn:

                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        id,
                        title,
                        company,
                        location,
                        source,
                        url
                    FROM jobs
                    WHERE location LIKE ?
                    ORDER BY id ASC
                """, (

                    f"%{location}%",

                ))

                rows = cursor.fetchall()

                return [dict(row) for row in rows]

        except sqlite3.Error as e:

            print("Database Error:", e)

            return []

    @staticmethod
    def get_job_by_id(job_id):

        try:

            with JobRepository.get_connection() as conn:

                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        id,
                        title,
                        company,
                        location,
                        source,
                        url
                    FROM jobs
                    WHERE id = ?
                """, (

                    job_id,

                ))

                row = cursor.fetchone()

                if row:

                    return dict(row)

                return None

        except sqlite3.Error as e:

            print("Database Error:", e)

            return None

    @staticmethod
    def total_jobs():

        try:

            with JobRepository.get_connection() as conn:

                cursor = conn.cursor()

                cursor.execute(
                    "SELECT COUNT(*) FROM jobs"
                )

                return cursor.fetchone()[0]

        except sqlite3.Error as e:

            print("Database Error:", e)

            return 0


if __name__ == "__main__":

    print("=" * 60)

    print("Job Repository Test")

    print("=" * 60)

    print()

    print("Total Jobs :", JobRepository.total_jobs())

    print()

    jobs = JobRepository.get_all_jobs()

    for job in jobs:

        print(job)

    print()

    print("Search Results (Data)")

    print("-" * 40)

    for job in JobRepository.search_jobs("Data"):

        print(job)

    print()

    print("Job ID 1")

    print("-" * 40)

    print(JobRepository.get_job_by_id(1))