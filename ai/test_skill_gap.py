from ai.skill_gap import SkillGap

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

result = SkillGap.analyze(
    resume,
    job
)

print("=" * 60)
print("Skill Gap Report")
print("=" * 60)

print("\nMatched Skills")
for skill in result["matched"]:
    print("✔", skill)

print("\nMissing Skills")
for skill in result["missing"]:
    print("✘", skill)

print("\nExtra Skills")
for skill in result["extra"]:
    print("+", skill)

print("\nGap Percentage:", result["gap"], "%")

print("\nLearning Plan")

for item in SkillGap.learning_plan(result["missing"]):
    print("-", item)