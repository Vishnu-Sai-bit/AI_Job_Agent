"""
==========================================================
AI JobAgent - Skill Extractor
Author : Beere Vishnu Sai

Description:
    Extract, normalize and compare technical skills across
    all modern software, data, cloud, mobile, and AI domains.
==========================================================
"""

import re
from typing import List, Set, Dict

from utils import info, exception
from exceptions import SkillExtractionError


# ==========================================================
# Master Skills Dictionary (Universal Across All Disciplines)
# ==========================================================

MASTER_SKILLS: Set[str] = {
    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "r", "go", "golang", "rust", "php", "ruby", "kotlin", "swift", "dart", "scala", "perl", "elixir", "haskell", "clojure", "lua", "solidity", "vyper", "apex", "abap", "matlab", "sas", "vba", "bash", "powershell", "assembly",

    # Frontend Frameworks, Libraries & Web
    "react", "react.js", "reactjs", "next.js", "nextjs", "angular", "angularjs", "vue", "vue.js", "vuejs", "svelte", "sveltekit", "remix", "astro", "redux", "redux toolkit", "mobx", "zustand", "recoil", "tailwind", "tailwind css", "html", "html5", "css", "css3", "sass", "scss", "less", "bootstrap", "material-ui", "mui", "chakra ui", "shadcn", "styled-components", "webpack", "vite", "babel", "gulp", "npm", "yarn", "pnpm", "graphql", "rest api", "rest", "json", "xml", "ajax", "responsive design", "web accessibility", "wcag", "progressive web apps", "pwa",

    # Backend Frameworks & Systems
    "node.js", "nodejs", "express", "express.js", "spring", "spring boot", "spring cloud", "hibernate", "jpa", "django", "flask", "fastapi", "tornado", "celery", "nest.js", "nestjs", "asp.net", ".net core", "entity framework", "laravel", "symfony", "codeigniter", "ruby on rails", "rails", "gin", "echo", "fiber", "actix", "tokyo", "grpc", "protobuf", "microservices", "service-oriented architecture", "soa", "monolith", "event-driven architecture", "websockets", "socket.io", "oauth", "oauth2", "jwt", "saml", "api gateway",

    # Databases & Caching
    "sql", "mysql", "postgresql", "postgres", "oracle", "oracle db", "mongodb", "sqlite", "sql server", "ms sql", "mariadb", "redis", "memcached", "elasticsearch", "opensearch", "cassandra", "dynamodb", "couchbase", "neo4j", "arangodb", "supabase", "firebase", "firestore", "faiss", "pinecone", "chromadb", "weaviate", "qdrant", "milvus",

    # Analytics, BI & Visualization
    "excel", "advanced excel", "power bi", "tableau", "looker", "looker studio", "power query", "dax", "m query", "business intelligence", "bi reporting", "dashboard", "dashboard development", "kpi", "data analysis", "data analytics", "data visualization", "reporting", "google looker", "qlik sense", "qlikview", "spotfire", "ssis", "ssrs", "ssas",

    # ETL, Big Data & Data Warehousing
    "etl", "etl pipeline", "elt", "data cleaning", "data preprocessing", "data warehouse", "data warehousing", "data lake", "data lakehouse", "snowflake", "bigquery", "redshift", "synapse", "dbt", "airflow", "apache airflow", "prefect", "dagster", "kafka", "apache kafka", "spark", "pyspark", "apache spark", "hadoop", "hdfs", "hive", "databricks", "delta lake", "flink", "storm",

    # Python Data Science & Statistical Analysis
    "numpy", "pandas", "matplotlib", "seaborn", "plotly", "scikit-learn", "sklearn", "scipy", "statsmodels", "sympy", "eda", "exploratory data analysis", "hypothesis testing", "a/b testing", "regression analysis", "time series", "time series forecasting",

    # AI, Machine Learning & Deep Learning
    "machine learning", "deep learning", "artificial intelligence", "ai", "neural networks", "cnn", "rnn", "lstm", "transformer", "bert", "gpt", "llm", "large language models", "genai", "generative ai", "langchain", "llamaindex", "hugging face", "transformers", "openai api", "rag", "retrieval-augmented generation", "fine-tuning", "prompt engineering", "tensorflow", "keras", "pytorch", "torch", "jax", "onnx", "tensorrt", "nlp", "natural language processing", "computer vision", "opencv", "yolo", "reinforcement learning", "mlops", "mlflow", "kubeflow", "wandb",

    # Cloud Platforms & Infrastructure
    "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud platform", "oracle cloud", "oci", "ibm cloud", "digitalocean", "cloudflare", "aws lambda", "ec2", "s3", "rds", "cloudformation", "azure data factory", "azure synapse", "azure functions", "microsoft fabric",

    # DevOps, CI/CD & Orchestration
    "docker", "kubernetes", "k8s", "helm", "terraform", "ansible", "puppet", "chef", "jenkins", "gitlab ci", "github actions", "circleci", "argo cd", "argocd", "flux", "prometheus", "grafana", "datadog", "new relic", "splunk", "elk stack", "linux", "ubuntu", "centos", "redhat", "debian", "bash", "shell scripting", "powershell", "git", "github", "gitlab", "bitbucket",

    # Mobile & Cross-Platform App Development
    "flutter", "react native", "android", "android sdk", "ios", "ios sdk", "swiftui", "uikit", "jetpack compose", "kotlin multiplatform", "xamarin", ".net maui", "ionic", "cordova",

    # Testing, QA & Automation
    "jest", "mocha", "chai", "cypress", "playwright", "selenium", "selenium webdriver", "puppeteer", "appium", "pytest", "unittest", "testng", "junit", "cucumber", "bdd", "tdd", "postman", "newman", "jmeter", "k6", "locust", "manual testing", "automation testing", "regression testing", "api testing", "performance testing", "load testing", "loadrunner",

    # Security & Cybersecurity
    "cybersecurity", "information security", "network security", "application security", "appsec", "penetration testing", "vapt", "ethical hacking", "siem", "splunk", "wireshark", "burp suite", "owasp", "owasp top 10", "soc", "soc 2", "incident response", "vulnerability assessment", "cryptography", "iam", "zero trust", "firewall", "ids/ips",

    # UI/UX & Product Design
    "figma", "adobe xd", "sketch", "invision", "wireframing", "prototyping", "user research", "usability testing", "ui design", "ux design", "design systems", "interaction design", "information architecture", "persona creation",

    # Enterprise ERP & CRM Platforms
    "salesforce", "salesforce admin", "salesforce developer", "apex", "lwc", "lightning web components", "soql", "sap", "sap abap", "sap hana", "sap s/4hana", "sap mm", "sap sd", "sap fico", "servicenow", "workday", "peoplesoft", "hubspot", "zoho",

    # Embedded Systems, Hardware & IoT
    "embedded c", "embedded systems", "rtos", "freertos", "microcontrollers", "arduino", "raspberry pi", "esp32", "arm", "stm32", "iot", "internet of things", "mqtt", "can bus", "i2c", "spi", "uart", "verilog", "vhdl", "fpga", "matlab", "simulink",

    # Project Management, Agile & Business Tools
    "agile", "scrum", "kanban", "scrum master", "product management", "project management", "jira", "confluence", "trello", "asana", "monday.com", "slack", "notion", "prd", "user stories", "backlog grooming", "sprint planning", "sdlc",

    # Soft Skills & Professional Attributes
    "communication", "leadership", "teamwork", "problem solving", "critical thinking", "time management", "analytical thinking", "stakeholder management", "client facing", "cross-functional collaboration", "mentorship", "adaptability", "negotiation", "presentation skills"
}


# ==========================================================
# Skill Taxonomy Normalizer & Alias Resolution Dictionary
# ==========================================================

SKILL_TAXONOMY_NORMALIZER: Dict[str, str] = {
    # Frontend
    "react": "React", "react.js": "React", "reactjs": "React",
    "next.js": "Next.js", "nextjs": "Next.js", "next": "Next.js",
    "vue": "Vue.js", "vue.js": "Vue.js", "vuejs": "Vue.js",
    "angular": "Angular", "angular.js": "AngularJS", "angularjs": "AngularJS",
    "svelte": "Svelte", "sveltekit": "SvelteKit",
    "redux": "Redux", "redux toolkit": "Redux Toolkit", "rtk": "Redux Toolkit",
    "tailwind": "Tailwind CSS", "tailwind css": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "html": "HTML5", "html5": "HTML5", "css": "CSS3", "css3": "CSS3",
    "sass": "Sass/SCSS", "scss": "Sass/SCSS",
    "typescript": "TypeScript", "ts": "TypeScript",
    "javascript": "JavaScript", "js": "JavaScript", "es6": "JavaScript (ES6+)",

    # Backend
    "node": "Node.js", "node.js": "Node.js", "nodejs": "Node.js",
    "express": "Express.js", "express.js": "Express.js",
    "nest": "NestJS", "nest.js": "NestJS", "nestjs": "NestJS",
    "spring": "Spring Framework", "spring boot": "Spring Boot", "springboot": "Spring Boot",
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
    "asp.net": "ASP.NET Core", ".net core": ".NET Core", ".net": ".NET Framework",
    "golang": "Go", "go": "Go", "rust": "Rust",
    "microservices": "Microservices Architecture", "rest api": "REST APIs", "rest": "REST APIs",
    "graphql": "GraphQL", "grpc": "gRPC", "kafka": "Apache Kafka", "rabbitmq": "RabbitMQ",

    # Databases
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "mysql": "MySQL", "oracle": "Oracle Database", "oracle db": "Oracle Database",
    "sql server": "Microsoft SQL Server", "ms sql": "Microsoft SQL Server", "mssql": "Microsoft SQL Server",
    "mongo": "MongoDB", "mongodb": "MongoDB",
    "redis": "Redis", "cassandra": "Apache Cassandra", "dynamodb": "Amazon DynamoDB",
    "snowflake": "Snowflake", "bigquery": "Google BigQuery", "redshift": "Amazon Redshift",
    "pinecone": "Pinecone Vector DB", "chromadb": "ChromaDB", "qdrant": "Qdrant", "milvus": "Milvus",

    # Cloud & DevOps
    "aws": "AWS", "amazon web services": "AWS",
    "azure": "Microsoft Azure", "microsoft azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform", "google cloud": "Google Cloud Platform",
    "docker": "Docker", "k8s": "Kubernetes", "kubernetes": "Kubernetes",
    "terraform": "Terraform", "ansible": "Ansible", "helm": "Helm",
    "ci/cd": "CI/CD Pipelines", "ci cd": "CI/CD Pipelines", "cicd": "CI/CD Pipelines",
    "jenkins": "Jenkins", "github actions": "GitHub Actions", "argocd": "ArgoCD",

    # Data Analytics & BI
    "power bi": "Power BI", "powerbi": "Power BI", "pbi": "Power BI",
    "tableau": "Tableau", "looker": "Looker Studio", "dax": "DAX",
    "excel": "Microsoft Excel", "advanced excel": "Advanced Excel",
    "etl": "ETL Pipelines", "spark": "Apache Spark", "pyspark": "PySpark", "databricks": "Databricks",

    # AI & ML
    "machine learning": "Machine Learning", "ml": "Machine Learning",
    "deep learning": "Deep Learning", "dl": "Deep Learning",
    "ai": "Artificial Intelligence", "genai": "Generative AI", "generative ai": "Generative AI",
    "llm": "Large Language Models", "llms": "Large Language Models",
    "langchain": "LangChain", "llamaindex": "LlamaIndex",
    "pytorch": "PyTorch", "torch": "PyTorch", "tensorflow": "TensorFlow", "tf": "TensorFlow",
    "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn", "pandas": "Pandas", "numpy": "NumPy",
    "rag": "RAG Architecture", "nlp": "Natural Language Processing",

    # QA & Testing
    "selenium": "Selenium", "cypress": "Cypress", "playwright": "Playwright",
    "testng": "TestNG", "junit": "JUnit", "pytest": "PyTest", "postman": "Postman", "jmeter": "JMeter",

    # Mobile & Cross-Platform
    "flutter": "Flutter", "react native": "React Native", "android": "Android Development",
    "ios": "iOS Development", "swift": "Swift", "kotlin": "Kotlin",

    # Enterprise & Security
    "salesforce": "Salesforce", "apex": "Salesforce Apex", "lwc": "Salesforce LWC",
    "sap": "SAP ERP", "sap abap": "SAP ABAP", "sap hana": "SAP HANA",
    "cybersecurity": "Cybersecurity", "penetration testing": "Penetration Testing (VAPT)",
    "siem": "SIEM", "splunk": "Splunk", "figma": "Figma", "jira": "Jira", "agile": "Agile / Scrum"
}


# ==========================================================
# Normalize Text & Canonical Resolution
# ==========================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for skill extraction.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[(){}\[\]]", " ", text)
    text = text.replace("/", " ")
    text = text.replace(",", " ")
    text = text.replace("|", " ")
    text = text.replace("•", " ")
    text = text.replace(";", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    """
    Map raw skill string to canonical industry standard name.
    """
    if not skill:
        return ""
    clean = skill.strip().lower()
    if clean in SKILL_TAXONOMY_NORMALIZER:
        return SKILL_TAXONOMY_NORMALIZER[clean]
    return skill.strip().title()


# ==========================================================
# Extract Skills From Dedicated Resume Sections
# ==========================================================

def extract_skills_from_sections(raw_text: str) -> List[str]:
    """
    Extract arbitrary custom candidate skills from explicit skill section headers
    (e.g., TECHNICAL SKILLS, CORE COMPETENCIES, TOOLS & TECHNOLOGIES).
    Works for any candidate regardless of whether the skill is in MASTER_SKILLS.
    """
    if not raw_text:
        return []

    section_pattern = r"(?:technical\s+skills|skills|core\s+competencies|key\s+skills|technologies|tools\s*&\s*technologies|programming\s+languages|frameworks\s*&\s*libraries|areas\s+of\s+expertise)[\s\:\-\_]*(.*?)(?=\n\s*(?:experience|work\s+experience|professional\s+experience|employment|projects|education|certifications|awards|publications|languages|interests|\Z))"
    
    match = re.search(section_pattern, raw_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return []

    section_content = match.group(1).strip()
    extracted = []

    # Split by common delimiters: comma, bullet, pipe, semicolon, newline
    tokens = re.split(r"[,|\n•\*\;\/]|(?:\s{2,})", section_content)
    
    stop_words = {"and", "with", "using", "the", "for", "in", "of", "to", "all", "various", "including", "proficient", "familiar", "knowledge", "expert", "hands-on", "experience"}

    for token in tokens:
        cleaned = re.sub(r"^[0-9\.\-\:\)\(\s]+", "", token).strip()
        cleaned = re.sub(r"[\:\(\)]+", "", cleaned).strip()
        
        # Valid skill tokens are generally 2 to 35 characters
        if 2 <= len(cleaned) <= 35 and cleaned.lower() not in stop_words:
            if not cleaned.isdigit() and len(cleaned.split()) <= 4:
                extracted.append(normalize_skill(cleaned))

    return extracted


# ==========================================================
# Extract Skills From Experience / Projects Context
# ==========================================================

def extract_experience_context_skills(raw_text: str) -> List[str]:
    """
    Extract skills embedded within project descriptions and work experience bullet points.
    """
    if not raw_text:
        return []

    extracted = []
    # Patterns like "using React, Node.js and AWS", "built with Python and PostgreSQL", "technologies: Docker, K8s"
    patterns = [
        r"(?:technologies|tools|stack|tech\s+stack|environment)[\s\:\-]+([^\.\n]+)",
        r"(?:built|developed|implemented|architected|leveraged|utilizing|using)\s+([^\.\n]+?)(?:to|for|which|resulting|\.|\n|$)"
    ]

    for p in patterns:
        for match in re.finditer(p, raw_text, re.IGNORECASE):
            chunk = match.group(1).strip()
            tokens = re.split(r"[,|\/•\*\;\&]|\band\b", chunk)
            for token in tokens:
                token_clean = token.strip().lower()
                if token_clean in SKILL_TAXONOMY_NORMALIZER or token_clean in MASTER_SKILLS:
                    extracted.append(normalize_skill(token_clean))

    return extracted


# ==========================================================
# Extract Skills (Unified Multi-Pass Extractor)
# ==========================================================

def extract_skills(text: str) -> List[str]:
    """
    Three-Tier Hybrid Extraction:
    1. Universal Master Dictionary Search (500+ skills)
    2. Explicit Resume Section Parser (Arbitrary & Emerging Skills)
    3. Contextual Experience & Project Extractor
    4. Canonical Taxonomy Normalizer Resolution
    """
    info("Executing Three-Tier Universal Skill Extraction...")

    try:
        normalized = normalize_text(text)
        skills = []

        # Pass 1: Master Dictionary Matching
        for skill in sorted(MASTER_SKILLS, key=len, reverse=True):
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, normalized):
                skills.append(normalize_skill(skill))

        # Pass 2: Explicit Resume Section Extraction
        section_skills = extract_skills_from_sections(text)
        for s in section_skills:
            if s and len(s) >= 2:
                skills.append(normalize_skill(s))

        # Pass 3: Embedded Experience Context Extraction
        exp_skills = extract_experience_context_skills(text)
        for s in exp_skills:
            if s and len(s) >= 2:
                skills.append(normalize_skill(s))

        # Canonical deduplication
        deduped = sorted(list({normalize_skill(s) for s in skills if s and len(s) >= 2}))
        info(f"{len(deduped)} canonical skills extracted and normalized across candidate profile.")
        return deduped

    except Exception as e:
        exception("Skill extraction failed.")
        raise SkillExtractionError(str(e))


# ==========================================================
# Merge Skills
# ==========================================================

def merge_skills(*skill_lists: List[str]) -> List[str]:
    """
    Merge multiple skill lists with canonical normalization.
    """
    merged = set()
    for skill_list in skill_lists:
        for skill in skill_list:
            if skill:
                merged.add(normalize_skill(skill))
    return sorted(merged)


# ==========================================================
# Skill Matching
# ==========================================================

def match_skills(resume_skills: List[str], job_skills: List[str]):
    """
    Compare resume skills with job skills using normalized taxonomy matching.
    """
    resume = {normalize_text(normalize_skill(skill)) for skill in resume_skills}
    job = {normalize_text(normalize_skill(skill)) for skill in job_skills}

    matching = sorted(resume & job)
    missing = sorted(job - resume)
    union = resume | job

    percentage = round((len(matching) / max(len(union), 1)) * 100, 2)

    return {
        "matching_skills": [normalize_skill(skill) for skill in matching],
        "missing_skills": [normalize_skill(skill) for skill in missing],
        "match_percentage": percentage
    }