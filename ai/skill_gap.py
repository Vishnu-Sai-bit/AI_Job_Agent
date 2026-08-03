class SkillGap:

    @staticmethod
    def analyze(resume_skills, job_skills):

        resume = {
            skill.strip().lower()
            for skill in resume_skills
        }

        required = {
        skill.strip().lower()
        for skill in job_skills
        }

        matched = sorted([
            skill for skill in job_skills
            if skill.lower() in resume
        ])

        missing = sorted([
            skill for skill in job_skills
            if skill.lower() not in resume
        ])

        extra = sorted([
            skill for skill in resume_skills
            if skill.lower() not in required
        ])

        score = 0

        if job_skills:

            score = (
                round((len(matched) / len(job_skills)) * 100)
                if job_skills
                else 0
            )

        gap = 100 - score

        return {

            "score": score,

            "gap": gap,

            "matched": matched,

            "missing": missing,

            "extra": extra

        }

    @staticmethod
    def learning_plan(missing_skills):

        plan = []

        for skill in missing_skills:

            plan.append(
                f"Learn {skill} through projects and online courses."
            )

        return plan


if __name__ == "__main__":

    resume = [
        "Python",
        "SQL",
        "Power BI",
        "Excel"
    ]

    job = [
        "Python",
        "SQL",
        "Power BI",
        "Git",
        "Azure"
    ]

    result = SkillGap.analyze(
        resume,
        job
    )

    print(result)

    print()

    print(SkillGap.learning_plan(result["missing"]))