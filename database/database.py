from .db_manager import DatabaseManager
from .models import Job

db = DatabaseManager()


def save_job(job: Job):

    db.execute(
        """
        INSERT INTO jobs
        (title,company,location,source,url,skills,salary,posted_date)

        VALUES(?,?,?,?,?,?,?,?)
        """,
        (
            job.title,
            job.company,
            job.location,
            job.source,
            job.url,
            job.skills,
            job.salary,
            job.posted_date,
        ),
    )


def get_jobs():

    return db.fetch_all("SELECT * FROM jobs")


def clear_jobs():

    db.execute("DELETE FROM jobs")