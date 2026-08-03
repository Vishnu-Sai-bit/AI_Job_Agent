from ai.resume_optimizer import ResumeOptimizer

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
    "Azure",
    "Spark",
    "Git",
    "Power BI"
]

report = ResumeOptimizer.optimize(
    resume,
    job
)

print("=" * 60)
print("Resume Optimization Report")
print("=" * 60)

print("\nMatched Skills")
for skill in report["matched"]:
    print("✔", skill)

print("\nMissing Skills")
for skill in report["missing"]:
    print("✘", skill)

print("\nSkill Gap:", report["gap"], "%")

print("\nSuggestions")

for suggestion in report["suggestions"]:
    print("-", suggestion)