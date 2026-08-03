from ai.ats_score import ATSScore

class JobMatcher:

    @staticmethod
    def match(resume_skills, job):

        result = ATSScore.calculate(
            resume_skills,
            job["skills"]
        )

        return {
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "score": result["score"],
            "matched": result["matched"],
            "missing": result["missing"]
        }

    @staticmethod
    def rank_jobs(resume_skills, jobs):

        ranked = []

        for job in jobs:

            ranked.append(
                JobMatcher.match(
                    resume_skills,
                    job
                )
            )

        ranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked