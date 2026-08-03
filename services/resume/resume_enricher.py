"""
==========================================================
AI JobAgent - Resume Enricher
==========================================================
"""

from datetime import datetime
import re
from config import DEFAULT_LOCATIONS


def extract_github(text: str) -> str:
    """
    Extract GitHub profile or repository.
    """

    patterns = [

        r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+",

        r"github\.com/[A-Za-z0-9_.-]+",

    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            url = match.group(0)

            if not url.startswith("http"):

                url = "https://" + url

            return url

    return ""


def extract_linkedin(text: str) -> str:
    """
    Extract LinkedIn profile.
    """

    patterns = [

        r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+",

        r"linkedin\.com/in/[A-Za-z0-9_-]+",

    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            url = match.group(0)

            if not url.startswith("http"):

                url = "https://" + url

            return url

    return ""

def extract_portfolio(text: str) -> str:
    """
    Extract portfolio/personal website.
    """

    ignore = (
        "linkedin.com",
        "github.com",
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "icloud.com",
        "proton.me",
        "mail.",
        "mailto:",
        "@",
    )

    patterns = [
        r"https?://(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?",
        r"(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for url in matches:
            url_clean = url.strip().rstrip(".,;)")
            if any(site in url_clean.lower() for site in ignore):
                continue
            if "@" in url_clean:
                continue
            if url_clean.lower().endswith((".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg")):
                continue
            if not url_clean.startswith("http"):
                url_clean = "https://" + url_clean
            return url_clean

    return ""

ROLE_ALIASES = {
    "Frontend Developer": [
        "frontend developer", "front end developer", "front-end developer",
        "react developer", "next.js developer", "angular developer", "vue developer",
        "ui developer", "web developer", "javascript developer", "frontend engineer"
    ],
    "Backend Developer": [
        "backend developer", "back end developer", "back-end developer",
        "node.js developer", "nodejs developer", "java developer", "python backend",
        "spring boot developer", "golang developer", ".net developer", "django developer", "backend engineer"
    ],
    "Full Stack Engineer": [
        "full stack developer", "fullstack developer", "full-stack developer",
        "full stack engineer", "mern stack developer", "mean stack developer", "fullstack engineer"
    ],
    "Software Engineer": [
        "software engineer", "software developer", "sde", "sde-1", "sde-2",
        "python developer", "systems engineer", "programmer", "application developer"
    ],
    "Data Analyst": [
        "data analyst", "junior data analyst", "senior data analyst",
        "business analyst", "bi analyst", "business intelligence analyst",
        "reporting analyst", "analytics engineer", "tableau developer", "power bi developer"
    ],
    "Data Engineer": [
        "data engineer", "etl developer", "big data engineer",
        "data warehouse engineer", "data pipeline engineer", "spark developer"
    ],
    "Data Scientist": [
        "data scientist", "machine learning engineer", "ml engineer",
        "ai engineer", "deep learning engineer", "nlp engineer", "computer vision engineer"
    ],
    "Artificial Intelligence & GenAI Engineer": [
        "genai engineer", "generative ai engineer", "llm engineer", "ai engineer",
        "prompt engineer", "ai research engineer", "nlp engineer"
    ],
    "DevOps & Cloud Engineer": [
        "devops engineer", "cloud engineer", "site reliability engineer", "sre",
        "platform engineer", "aws engineer", "azure engineer", "infrastructure engineer"
    ],
    "Cloud Solutions Architect": [
        "cloud architect", "solutions architect", "enterprise architect", "aws architect", "azure architect"
    ],
    "Mobile App Developer": [
        "mobile developer", "android developer", "ios developer",
        "flutter developer", "react native developer", "mobile app developer"
    ],
    "QA / Test Automation Engineer": [
        "qa engineer", "sdet", "test automation engineer", "quality assurance",
        "software tester", "selenium tester", "manual tester", "qa automation engineer"
    ],
    "Product / Project Manager": [
        "product manager", "project manager", "scrum master", "technical program manager", "product owner"
    ],
    "UI/UX Designer": [
        "ui/ux designer", "product designer", "ux designer", "ui designer", "interaction designer"
    ],
    "Cybersecurity Analyst": [
        "cybersecurity", "security analyst", "information security", "soc analyst", "penetration tester", "security engineer"
    ],
    "Salesforce / CRM Developer": [
        "salesforce developer", "salesforce admin", "salesforce consultant", "crm developer"
    ],
    "SAP / ERP Consultant": [
        "sap consultant", "sap abap", "sap fico", "sap mm", "sap sd", "erp consultant"
    ],
    "Embedded Systems & IoT Engineer": [
        "embedded engineer", "embedded developer", "iot engineer", "firmware engineer", "hardware engineer"
    ],
    "Blockchain & Web3 Developer": [
        "blockchain developer", "web3 developer", "solidity developer", "smart contract developer"
    ],
    "Financial & Business Analyst": [
        "financial analyst", "finance manager", "investment analyst", "risk analyst", "accountant"
    ],
    "HR & Talent Specialist": [
        "hr specialist", "human resources", "talent acquisition", "technical recruiter", "hr generalist"
    ]
}

def infer_role(text: str) -> str:
    """
    Infer preferred role from resume by checking summary/title/skills.
    """
    text_lower = text.lower()
    first_chunk = "\n".join(text_lower.splitlines()[:30])

    # Check top header/summary lines first
    for role, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias) + r'\b', first_chunk):
                return role

    # Check whole text
    for role, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                return role

    # Fallback based on dominant skills in text
    if any(k in text_lower for k in ["salesforce", "apex", "lwc", "soql"]):
        return "Salesforce / CRM Developer"
    if any(k in text_lower for k in ["sap", "abap", "sap hana", "s/4hana"]):
        return "SAP / ERP Consultant"
    if any(k in text_lower for k in ["embedded c", "microcontroller", "rtos", "arduino", "stm32", "firmware"]):
        return "Embedded Systems & IoT Engineer"
    if any(k in text_lower for k in ["solidity", "web3", "smart contract", "ethereum"]):
        return "Blockchain & Web3 Developer"
    if any(k in text_lower for k in ["figma", "wireframe", "prototype", "ux design", "ui/ux"]):
        return "UI/UX Designer"
    if any(k in text_lower for k in ["selenium", "cypress", "playwright", "sdet", "testng", "automation testing"]):
        return "QA / Test Automation Engineer"
    if any(k in text_lower for k in ["react", "next.js", "html5", "css3", "tailwind", "frontend", "vue", "angular"]):
        return "Frontend Developer"
    if any(k in text_lower for k in ["power bi", "tableau", "sql", "excel", "dax", "analytics"]):
        return "Data Analyst"
    if any(k in text_lower for k in ["docker", "kubernetes", "aws", "ci/cd", "terraform", "ansible"]):
        return "DevOps & Cloud Engineer"
    if any(k in text_lower for k in ["langchain", "llamaindex", "genai", "generative ai", "llm", "rag"]):
        return "Artificial Intelligence & GenAI Engineer"
    if any(k in text_lower for k in ["machine learning", "tensorflow", "pytorch", "scikit-learn"]):
        return "Data Scientist"
    if any(k in text_lower for k in ["django", "spring boot", "fastapi", "express", "backend", "java", "node.js"]):
        return "Backend Developer"
    if any(k in text_lower for k in ["flutter", "react native", "android", "swift", "kotlin", "ios"]):
        return "Mobile App Developer"
    if any(k in text_lower for k in ["cybersecurity", "penetration testing", "siem", "splunk", "soc"]):
        return "Cybersecurity Analyst"
    if any(k in text_lower for k in ["scrum", "product management", "jira", "sprint planning", "agile"]):
        return "Product / Project Manager"

    return "Software Engineer"

COMMON_CITIES = [

    "hyderabad",

    "bangalore",

    "bengaluru",

    "chennai",

    "pune",

    "mumbai",

    "delhi",

    "gurugram",

    "noida",

    "tirupati",

]

def infer_location(text: str) -> str:
    """
    Infer candidate city / current hub from resume text.
    """
    if not text:
        return "Hyderabad"

    text_lower = text.lower()
    first_lines = "\n".join(text.splitlines()[:25]).lower()

    # Major Indian tech hubs / cities
    known_cities = [
        "hyderabad", "bengaluru", "bangalore", "chennai", "pune", "mumbai",
        "delhi", "new delhi", "gurugram", "gurgaon", "noida", "kolkata",
        "ahmedabad", "jaipur", "kochi", "coimbatore", "trivandrum", "indore",
        "chandigarh", "nagpur", "visakhapatnam", "vizag", "tirupati"
    ]

    # 1. Check top header lines (where address / current location is usually stated)
    for city in known_cities:
        if re.search(r'\b' + re.escape(city) + r'\b', first_lines):
            if city in ["bangalore", "bengaluru"]:
                return "Bengaluru"
            if city in ["gurgaon", "gurugram"]:
                return "Gurugram"
            if city in ["vizag", "visakhapatnam"]:
                return "Visakhapatnam"
            if city in ["new delhi", "delhi"]:
                return "Delhi"
            return city.title()

    # 2. Check explicit preference keywords
    keywords = [
        "preferred location",
        "location preference",
        "preferred work location",
        "looking for jobs in",
        "relocate to",
    ]

    for keyword in keywords:
        if keyword in text_lower:
            for city in known_cities:
                if re.search(r'\b' + re.escape(city) + r'\b', text_lower):
                    if city in ["bangalore", "bengaluru"]:
                        return "Bengaluru"
                    if city in ["gurgaon", "gurugram"]:
                        return "Gurugram"
                    return city.title()

    # 3. Check entire text
    for city in known_cities:
        if re.search(r'\b' + re.escape(city) + r'\b', text_lower):
            if city in ["bangalore", "bengaluru"]:
                return "Bengaluru"
            if city in ["gurgaon", "gurugram"]:
                return "Gurugram"
            return city.title()

    return "Hyderabad"


def infer_experience(text: str) -> float:
    """
    Estimate years of experience.
    """

    text = text.lower()

    if "intern" in text:

        return 0.5

    matches = re.findall(

        r"(\d+)\+?\s*years",

        text,

    )

    if matches:

        return float(matches[0])

    return 0.0

def infer_career_level(experience: float) -> str:

    if experience == 0:

        return "Fresher"

    if experience < 2:

        return "Junior"

    if experience < 5:

        return "Mid"

    return "Senior"
