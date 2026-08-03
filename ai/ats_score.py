class ATSScore:

    @staticmethod
    def calculate(resume_skills, job_skills):

        resume = set(skill.lower().strip() for skill in resume_skills)
        job = set(skill.lower().strip() for skill in job_skills)

        matched = sorted(list(resume & job))
        missing = sorted(list(job - resume))

        if len(job) == 0:
            score = 0
        else:
            score = round((len(matched) / len(job)) * 100)

        return {
            "score": score,
            "matched": matched,
            "missing": missing
        }