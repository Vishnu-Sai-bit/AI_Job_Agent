import sqlite3

DB = "database/job_copilot.db"

jobs = [

    ("Data Analyst", "Infosys", "Bangalore", "LinkedIn", "https://linkedin.com"),

    ("Business Analyst", "Accenture", "Hyderabad", "Naukri", "https://naukri.com"),

    ("Data Engineer", "TCS", "Bangalore", "Foundit", "https://foundit.in"),

    ("BI Analyst", "Deloitte", "Hyderabad", "LinkedIn", "https://linkedin.com"),

    ("Reporting Analyst", "Capgemini", "Pune", "Indeed", "https://indeed.com"),

    ("Data Scientist", "Wipro", "Chennai", "LinkedIn", "https://linkedin.com"),

    ("Python Developer", "Cognizant", "Bangalore", "Naukri", "https://naukri.com"),

    ("SQL Developer", "IBM", "Hyderabad", "Foundit", "https://foundit.in"),

    ("Power BI Developer", "Tech Mahindra", "Bangalore", "LinkedIn", "https://linkedin.com"),

    ("Analytics Consultant", "EY", "Hyderabad", "Indeed", "https://indeed.com"),

]


def load_jobs():

    with sqlite3.connect(DB) as conn:

        cursor = conn.cursor()

        inserted = 0

        skipped = 0

        for job in jobs:

            cursor.execute(
                """
                SELECT id
                FROM jobs
                WHERE
                    title = ?
                    AND company = ?
                    AND location = ?
                """,
                (
                    job[0],
                    job[1],
                    job[2]
                )
            )

            exists = cursor.fetchone()

            if exists:

                skipped += 1

                continue

            cursor.execute(
                """
                INSERT INTO jobs
                (
                    title,
                    company,
                    location,
                    source,
                    url
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                job
            )

            inserted += 1

        conn.commit()

        print("=" * 50)

        print("Job Loader")

        print("=" * 50)

        print(f"Inserted : {inserted}")

        print(f"Skipped  : {skipped}")

        print("=" * 50)


if __name__ == "__main__":

    load_jobs()