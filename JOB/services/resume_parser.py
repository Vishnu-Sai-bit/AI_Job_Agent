import re
from datetime import datetime
from typing import Dict, Any, List

COMMON_SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    # Frameworks & Libraries
    "flask", "django", "fastapi", "express", "react", "react.js", "next.js", "vue", "vue.js", "angular", "node.js", "nodejs",
    "spring", "spring boot", "asp.net", "laravel", "rails", "ruby on rails", "tailwind", "tailwind css", "bootstrap", "jquery",
    # Databases & Caching
    "sql", "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "oracle",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ansible",
    "ci/cd", "jenkins", "github actions", "gitlab ci", "linux", "bash", "nginx", "apache",
    # AI / ML & Data Science
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "matplotlib", "seaborn", "data analysis", "llm", "langchain", "hugging face", "vector databases",
    # Architecture & Practices
    "rest", "restful api", "rest api", "graphql", "microservices", "system design", "agile", "scrum", "git", "github", "gitlab",
    "unit testing", "pytest", "test driven development", "tdd", "object-oriented programming", "oop", "data structures", "algorithms"
]

DEGREE_PATTERNS = [
    r"\b(bachelor['’]?s?|b\.?s\.?|b\.?e\.?|b\.?tech\.?|undergraduate)\b",
    r"\b(master['’]?s?|m\.?s\.?|m\.?e\.?|m\.?tech\.?|mba|postgraduate)\b",
    r"\b(ph\.?d\.?|doctorate|doctoral)\b",
    r"\b(associate['’]?s?|diploma)\b"
]

class ResumeParser:
    def parse(self, raw_text: str) -> Dict[str, Any]:
        """
        Parses raw text of resume into structured data.
        """
        cleaned = raw_text.strip()
        lines = [l.strip() for l in cleaned.split("\n") if l.strip()]

        contact_info = self._extract_contact_info(cleaned, lines)
        skills = self._extract_skills(cleaned)
        experience_info = self._extract_experience(cleaned, lines)
        education_info = self._extract_education(cleaned, lines)
        projects = self._extract_projects(cleaned, lines)
        certifications = self._extract_certifications(cleaned, lines)
        summary = self._extract_summary(lines)

        return {
            "name": contact_info["name"],
            "email": contact_info["email"],
            "phone": contact_info["phone"],
            "location": contact_info["location"],
            "headline": contact_info["headline"],
            "summary": summary,
            "skills": skills,
            "experience_years": experience_info["total_years"],
            "experience": experience_info["roles"],
            "education": education_info,
            "projects": projects,
            "certifications": certifications
        }

    def _extract_contact_info(self, text: str, lines: List[str]) -> Dict[str, str]:
        email = ""
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        if email_match:
            email = email_match.group(0).lower()

        phone = ""
        phone_match = re.search(r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
        if phone_match:
            phone = phone_match.group(0).strip()

        # Name heuristic: First non-empty line that doesn't contain email/phone/url
        name = ""
        headline = ""
        for line in lines[:5]:
            if "@" in line or "http" in line or any(c.isdigit() for c in line if line.count(c) > 3):
                continue
            if len(line.split()) in [2, 3, 4] and not name:
                name = line.title()
            elif name and not headline and len(line) < 60:
                headline = line
                break

        # Location heuristic
        location = ""
        loc_match = re.search(r"\b([A-Z][a-zA-Z]+(?:[\s-][A-Z][a-zA-Z]+)?),\s*([A-Z]{2}|[A-Za-z]+)\b", text)
        if loc_match:
            location = loc_match.group(0)

        return {
            "name": name or "Candidate",
            "email": email,
            "phone": phone,
            "location": location,
            "headline": headline
        }

    def _extract_skills(self, text: str) -> List[str]:
        lowered = text.lower()
        found = set()
        for skill in COMMON_SKILLS:
            # Word boundary matching
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
            if re.search(pattern, lowered):
                # Standardize capitalization
                found.add(self._canonicalize_skill(skill))
        return sorted(list(found))

    def _canonicalize_skill(self, skill: str) -> str:
        mapping = {
            "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
            "react": "React", "react.js": "React", "vue": "Vue.js", "vue.js": "Vue.js",
            "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
            "node.js": "Node.js", "nodejs": "Node.js", "sql": "SQL",
            "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mongodb": "MongoDB",
            "docker": "Docker", "kubernetes": "Kubernetes", "aws": "AWS",
            "gcp": "GCP", "azure": "Azure", "ci/cd": "CI/CD", "html": "HTML",
            "css": "CSS", "rest": "REST APIs", "rest api": "REST APIs",
            "restful api": "REST APIs", "graphql": "GraphQL", "git": "Git"
        }
        return mapping.get(skill.lower(), skill.title())

    def _extract_experience(self, text: str, lines: List[str]) -> Dict[str, Any]:
        # Estimate years of experience from year mentions
        years = [int(y) for y in re.findall(r"\b(20[0-2][0-9]|199[0-9])\b", text)]
        total_years = 0.0
        if years:
            current_year = datetime.now().year
            min_year = min(years)
            total_years = max(0.0, float(min(current_year - min_year, 35)))

        # Extract roles from lines following Experience header
        roles = []
        is_exp_section = False
        current_role = None

        for line in lines:
            line_lower = line.lower()
            if any(h in line_lower for h in ["work experience", "professional experience", "employment history"]):
                is_exp_section = True
                continue
            elif is_exp_section and any(h in line_lower for h in ["education", "skills", "projects", "certifications"]):
                is_exp_section = False
                if current_role:
                    roles.append(current_role)
                break

            if is_exp_section:
                # Check for role header
                if any(kw in line_lower for kw in ["developer", "engineer", "lead", "analyst", "manager", "intern", "specialist"]):
                    if current_role:
                        roles.append(current_role)
                    current_role = {"title": line, "details": []}
                elif current_role:
                    current_role["details"].append(line)

        if current_role and current_role not in roles:
            roles.append(current_role)

        return {"total_years": total_years, "roles": roles}

    def _extract_education(self, text: str, lines: List[str]) -> List[Dict[str, str]]:
        education = []
        lowered = text.lower()
        for pat in DEGREE_PATTERNS:
            match = re.search(pat, lowered)
            if match:
                degree_name = match.group(0).title()
                # Try to find nearby school/university name
                school = "Recognized Institution"
                for line in lines:
                    if any(w in line.lower() for w in ["university", "college", "institute", "school"]):
                        school = line
                        break
                education.append({"degree": degree_name, "institution": school})
                break
        return education

    def _extract_projects(self, text: str, lines: List[str]) -> List[Dict[str, str]]:
        projects = []
        is_proj_section = False
        current_proj = None

        for line in lines:
            line_lower = line.lower()
            if "project" in line_lower and len(line_lower) < 25:
                is_proj_section = True
                continue
            elif is_proj_section and any(h in line_lower for h in ["education", "skills", "experience", "certifications"]):
                is_proj_section = False
                if current_proj:
                    projects.append(current_proj)
                break

            if is_proj_section:
                if line.startswith(("-", "*", "•")) or len(line.split()) < 6:
                    if current_proj and len(current_proj["description"]) > 10:
                        projects.append(current_proj)
                    current_proj = {"title": line.strip("-*• "), "description": ""}
                elif current_proj:
                    current_proj["description"] += " " + line

        if current_proj and current_proj not in projects:
            projects.append(current_proj)

        return projects[:5]

    def _extract_certifications(self, text: str, lines: List[str]) -> List[str]:
        certs = []
        cert_keywords = ["certified", "certification", "aws certified", "pmp", "comptia", "cissp", "scrum master"]
        lowered = text.lower()
        for kw in cert_keywords:
            if kw in lowered:
                certs.append(kw.title())
        return list(set(certs))

    def _extract_summary(self, lines: List[str]) -> str:
        for i, line in enumerate(lines[:10]):
            if any(s in line.lower() for s in ["summary", "profile", "objective", "about me"]):
                if i + 1 < len(lines):
                    return lines[i + 1]
        return ""
