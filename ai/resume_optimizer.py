from ai.skill_gap import SkillGap


class ResumeOptimizer:

    @staticmethod
    def optimize(resume_skills, job_skills):

        report = SkillGap.analyze(
            resume_skills,
            job_skills
        )

        suggestions = []

        if report["missing"]:

            suggestions.append(
                "Add the missing technical skills to your resume after gaining experience or completing relevant projects/certifications."
            )

        if len(report["matched"]) < len(job_skills) / 2:

            suggestions.append(
                "Customize your resume specifically for this job instead of using a generic resume."
            )

        suggestions.append(
            "Use measurable achievements (for example: Improved dashboard performance by 25%)."
        )

        suggestions.append(
            "Include projects that demonstrate the required skills."
        )

        suggestions.append(
            "Keep your resume ATS-friendly with clear section headings."
        )

        return {
            "matched": report["matched"],
            "missing": report["missing"],
            "gap": report["gap"],
            "suggestions": suggestions
        }