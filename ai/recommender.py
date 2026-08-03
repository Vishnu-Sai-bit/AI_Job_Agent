from ai.job_matcher import JobMatcher


class JobRecommender:

    def __init__(self, resume_skills, jobs):

        self.resume_skills = resume_skills
        self.jobs = jobs

    def recommend(self, minimum_score=60):

        ranked_jobs = JobMatcher.rank_jobs(
            self.resume_skills,
            self.jobs
        )

        recommended = []

        for job in ranked_jobs:

            if job["score"] >= minimum_score:

                recommended.append(job)

        return recommended

    def top_jobs(self, count=5):

        ranked_jobs = JobMatcher.rank_jobs(
            self.resume_skills,
            self.jobs
        )

        return ranked_jobs[:count]