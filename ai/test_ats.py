from ai.ats_score import ATSScore

resume = [
    "Python",
    "SQL",
    "Power BI",
    "Tableau",
    "Excel"
]

job = [
    "Python",
    "SQL",
    "Power BI",
    "Azure",
    "Spark",
    "Tableau"
]

result = ATSScore.calculate(
    resume,
    job
)

print("ATS Score:", result["score"])
print()

print("Matched Skills")
for skill in result["matched"]:
    print("✔", skill)

print()

print("Missing Skills")
for skill in result["missing"]:
    print("✘", skill)