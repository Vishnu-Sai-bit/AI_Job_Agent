from datetime import date


class CoverLetterAI:

    @staticmethod
    def generate(
        name,
        company,
        position,
        skills
    ):

        # Convert list of skills into bullet points
        skills_text = "\n".join(
            f"• {skill}" for skill in skills
        )

        return f"""
{date.today()}

Dear Hiring Manager,

I am excited to apply for the position of {position} at {company}.

I am a recent Information Technology graduate with hands-on experience in:

{skills_text}

I have completed multiple real-world analytics projects and internships where I worked on data cleaning, dashboard development, KPI analysis, and business reporting.

My technical skills closely match your requirements.

I am eager to contribute to your organization while continuously learning and growing as a Data Analyst.

Thank you for considering my application.

Sincerely,

{name}
"""


if __name__ == "__main__":

    letter = CoverLetterAI.generate(
        name="Beere Vishnu Sai",
        company="Infosys",
        position="Data Analyst",
        skills=[
            "Python",
            "SQL",
            "Power BI",
            "Tableau"
        ]
    )

    print(letter)