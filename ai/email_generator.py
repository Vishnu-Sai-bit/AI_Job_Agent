from datetime import date


class EmailGenerator:

    @staticmethod
    def generate(
        candidate_name,
        company,
        position,
        recruiter="Hiring Manager"
    ):

        subject = f"Application for {position}"

        body = f"""Dear {recruiter},

I hope you are doing well.

I am writing to express my interest in the {position} position at {company}.

I recently completed my B.Tech in Information Technology and have hands-on experience in Python, SQL, Power BI, Tableau, Excel, Pandas, and Data Analytics. I have also completed internships and built multiple data analytics projects.

I have attached my resume for your consideration. I would appreciate the opportunity to discuss how my skills align with your team's requirements.

Thank you for your time and consideration.

Best Regards,

{candidate_name}
Email: beerevishnusai776600@gmail.com
Date: {date.today()}
"""

        return subject, body


if __name__ == "__main__":

    subject, body = EmailGenerator.generate(
        candidate_name="Beere Vishnu Sai",
        company="Infosys",
        position="Data Analyst"
    )

    print("=" * 60)
    print("EMAIL SUBJECT")
    print("=" * 60)
    print(subject)

    print("\n")

    print("=" * 60)
    print("EMAIL BODY")
    print("=" * 60)
    print(body)