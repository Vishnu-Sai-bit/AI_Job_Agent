from ai.ats_score import ATSScore
from ai.skill_gap import SkillGap


class CareerAdvisor:

    @staticmethod
    def analyze(resume_skills, job_skills):

        ats = ATSScore.calculate(
            resume_skills,
            job_skills
        )

        gap = SkillGap.analyze(
            resume_skills,
            job_skills
        )

        recommendations = []

        if ats["score"] >= 85:
            recommendations.append(
                "Excellent match. Apply immediately."
            )

        elif ats["score"] >= 70:
            recommendations.append(
                "Good match. Customize your resume before applying."
            )

        else:
            recommendations.append(
                "Improve your skills before applying."
            )

        if gap["missing"]:

            recommendations.append(
                "Focus on learning these skills:"
            )

            for skill in gap["missing"]:
                recommendations.append(f"• {skill.title()}")

        return {

            "ats_score": ats["score"],

            "matched_skills": ats["matched"],

            "missing_skills": gap["missing"],

            "recommendations": recommendations

        }


if __name__ == "__main__":

    resume = [
        "Python",
        "SQL",
        "Power BI",
        "Excel",
        "Tableau"
    ]

    job = [
        "Python",
        "SQL",
        "Power BI",
        "Azure",
        "Spark",
        "Git"
    ]

    report = CareerAdvisor.analyze(
        resume,
        job
    )

    print("=" * 60)
    print("CAREER ADVISOR REPORT")
    print("=" * 60)

    print(f"ATS Score: {report['ats_score']}%")

    print("\nMatched Skills")
    for skill in report["matched_skills"]:
        print("✓", skill)

    print("\nMissing Skills")
    for skill in report["missing_skills"]:
        print("✗", skill)

    print("\nRecommendations")
    for item in report["recommendations"]:
        print(item)