from ai.skill_extractor import SkillExtractor

resume_text = """
Python
SQL
Power BI
Tableau
Excel
Pandas
Git
GitHub
Machine Learning
Communication
"""

extractor = SkillExtractor(resume_text)

skills = extractor.extract()

print(skills)