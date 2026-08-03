import re

SKILLS = [
    "python",
    "sql",
    "mysql",
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "matplotlib",
    "statistics",
    "machine learning",
    "data analysis",
    "data visualization",
    "etl",
    "git",
    "github",
    "azure",
    "aws",
    "spark",
    "hadoop",
    "postgresql",
    "oracle",
    "communication",
    "problem solving"
]


class SkillExtractor:

    def __init__(self, text):
        self.text = text.lower()

    def extract(self):

        found = []

        for skill in SKILLS:

            pattern = r"\b" + re.escape(skill) + r"\b"

            if re.search(pattern, self.text):
                found.append(skill)

        return sorted(list(set(found)))