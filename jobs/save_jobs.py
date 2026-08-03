import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from database.database import save_job
from database.models import Job


def save_jobs(job_list):
    """
    Save a list of jobs to the database.
    """

    saved = 0

    for job in job_list:
        try:
            save_job(job)
            saved += 1
        except Exception as e:
            print(f"Error saving {job.title}: {e}")

    print("=" * 60)
    print(f"Jobs Saved : {saved}")
    print("=" * 60)


if __name__ == "__main__":

    sample_job = Job(
        title="Data Analyst",
        company="Google",
        location="Bangalore",
        source="LinkedIn",
        url="https://...",
        skills="Python, SQL",
        salary="12 LPA",
        posted_date="Today"
    )

    save_jobs([sample_job])