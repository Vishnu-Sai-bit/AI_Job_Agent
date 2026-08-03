class InterviewQuestions:

    QUESTIONS = {
        "python": [
            "Explain Python lists and tuples.",
            "What are decorators in Python?",
            "Explain OOP concepts in Python."
        ],

        "sql": [
            "What is the difference between WHERE and HAVING?",
            "Explain INNER JOIN and LEFT JOIN.",
            "Write a query to find the second highest salary."
        ],

        "power bi": [
            "What is DAX?",
            "Difference between Import and DirectQuery?",
            "Explain Star Schema."
        ],

        "tableau": [
            "Difference between Dimensions and Measures?",
            "Explain LOD Expressions.",
            "How do Filters work in Tableau?"
        ],

        "excel": [
            "Difference between VLOOKUP and XLOOKUP?",
            "What is a Pivot Table?",
            "Explain INDEX and MATCH."
        ],

        "pandas": [
            "Difference between loc and iloc?",
            "How do you handle missing values?",
            "Difference between merge() and join()?"
        ],

        "machine learning": [
            "Difference between Classification and Regression?",
            "What is Overfitting?",
            "Explain Cross Validation."
        ]
    }

    @staticmethod
    def generate(skills):

        questions = []

        for skill in skills:

            key = skill.lower()

            if key in InterviewQuestions.QUESTIONS:
                questions.extend(
                    InterviewQuestions.QUESTIONS[key]
                )

        return questions


if __name__ == "__main__":

    skills = [
        "Python",
        "SQL",
        "Power BI",
        "Tableau"
    ]

    questions = InterviewQuestions.generate(skills)

    print("=" * 60)
    print("INTERVIEW QUESTIONS")
    print("=" * 60)

    for i, question in enumerate(questions, start=1):
        print(f"{i}. {question}")