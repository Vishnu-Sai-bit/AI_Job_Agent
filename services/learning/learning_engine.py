"""
==========================================================
AI JobAgent - Learning Engine Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are an expert Career Accelerator and Senior Technical Instructor.
Your task is to analyze skill deficits for a candidate targeting a career role and construct actionable, high-impact learning roadmaps with week-by-week plans and portfolio project blueprints.

Generate the roadmap following this JSON schema exactly:
{{
    "skill_gaps": ["Skill 1", "Skill 2", "Skill 3"],
    "roadmaps": [
        {{
            "skill": "Skill Name",
            "timeframe": "4-6 Weeks",
            "weekly_plan": [
                {{
                    "week": "Week 1-2: Core Foundations",
                    "focus": "Core concepts, architecture, syntax, and schema fundamentals.",
                    "task": "Build basic transformation scripts or introductory components."
                }},
                {{
                    "week": "Week 3-4: Advanced Implementation",
                    "focus": "Complex calculations, optimization, and real-world logic.",
                    "task": "Implement scalable architectures or automated workflows."
                }},
                {{
                    "week": "Week 5: Capstone Portfolio Project",
                    "focus": "End-to-end deployment, testing, and GitHub documentation.",
                    "task": "Publish documented repository with live demo/dashboard to GitHub."
                }}
            ],
            "portfolio_project_blueprint": {{
                "title": "Project Title",
                "recommended_dataset": "Recommended dataset or public API",
                "key_deliverables": [
                    "Architecture pipeline or component structure",
                    "Interactive application or dashboard",
                    "Documented README with system diagram"
                ],
                "github_prompt": "Template structure: /src, /tests, README.md with metrics"
            }},
            "recommended_certifications": ["Certification 1", "Certification 2"],
            "free_learning_resources": ["Official Documentation", "FreeCodeCamp / YouTube"]
        }}
    ]
}}

Target Role: {role}
Current Skills: {skills}

Generate structured roadmaps for the top 2-3 most critical skill deficits for this target role.
Return ONLY raw JSON.
"""

def generate_learning_roadmap(role: str, skills: List[str]) -> Dict[str, Any]:
    """
    Generate week-by-week learning pathways and project blueprints using the LLM,
    with dynamic role-aware fallback logic.
    """
    role_clean = role or "Software Engineer"
    skills_str = ", ".join(skills) if skills else "Programming, Problem Solving"
    formatted_prompt = PROMPT.format(
        role=role_clean,
        skills=skills_str
    )

    info(f"Generating structured learning roadmap for target role: {role_clean}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        data = json.loads(cleaned.strip())
        if "roadmaps" in data and len(data["roadmaps"]) > 0:
            return data
    except Exception as e:
        exception(f"Learning roadmap generation failed: {e}")

    # Dynamic Role-Aware Fallback
    r_lower = role_clean.lower()
    
    # 1. Frontend Developer Roadmap Fallback
    if any(k in r_lower for k in ["front", "react", "next", "ui", "web"]):
        return {
            "skill_gaps": ["TypeScript & Next.js App Router", "State Management (Redux/Zustand) & Testing"],
            "roadmaps": [
                {
                    "skill": "TypeScript & Next.js 14+ App Router Architecture",
                    "timeframe": "4 Weeks",
                    "weekly_plan": [
                        {"week": "Week 1: TypeScript Generics & Strict Typing", "focus": "Type safety, interfaces, union types, and utility types.", "task": "Migrate existing JavaScript components to strict TypeScript."},
                        {"week": "Week 2: Next.js Server & Client Components", "focus": "App Router, SSR, SSG, Server Actions, and dynamic routing.", "task": "Build server-rendered data fetching pages with loading states."},
                        {"week": "Week 3-4: Capstone Portfolio Web App", "focus": "Tailwind CSS responsive design, API route handlers, and Vercel deployment.", "task": "Publish full-stack Next.js project with README and live demo link to GitHub."}
                    ],
                    "portfolio_project_blueprint": {
                        "title": "Headless E-Commerce / SaaS Analytics Platform",
                        "recommended_dataset": "FakeStore API / Stripe Test API / CoinGecko API",
                        "key_deliverables": [
                            "Server-Side Rendered (SSR) product catalogue with optimistic UI updates",
                            "Type-safe custom hooks and modular component hierarchy",
                            "Mobile-first responsive design with Tailwind CSS"
                        ],
                        "github_prompt": "Include live Vercel deployment URL, Lighthouse 95+ score, and architecture in README.md"
                    },
                    "recommended_certifications": [
                        "Meta Certified Frontend Developer",
                        "AWS Certified Cloud Practitioner"
                    ],
                    "free_learning_resources": [
                        "Official Next.js Learn Tutorial",
                        "TypeScript Handbook (Official Docs)"
                    ]
                },
                {
                    "skill": "Frontend State Management & Automated Testing (Jest/Cypress)",
                    "timeframe": "4 Weeks",
                    "weekly_plan": [
                        {"week": "Week 1: Redux Toolkit / Zustand", "focus": "Global state store, async thunks, and middleware.", "task": "Build centralized store with slice architecture."},
                        {"week": "Week 2: Unit & Component Testing with Jest", "focus": "React Testing Library, mock API calls, and snapshot tests.", "task": "Achieve 80%+ test coverage on core interactive components."},
                        {"week": "Week 3-4: End-to-End Testing & CI/CD", "focus": "Cypress E2E test suite and GitHub Actions workflow.", "task": "Automate test runs on pull requests."}
                    ],
                    "portfolio_project_blueprint": {
                        "title": "Interactive Real-Time Collaborative Workspace",
                        "recommended_dataset": "Public WebSocket APIs or Firebase Realtime DB",
                        "key_deliverables": [
                            "Real-time event streaming with optimistic local updates",
                            "Comprehensive unit test suite using React Testing Library",
                            "Automated GitHub Actions CI pipeline"
                        ],
                        "github_prompt": "Document test coverage badges and state architecture in README.md"
                    },
                    "recommended_certifications": [
                        "Google UX & Web Design Certificate"
                    ],
                    "free_learning_resources": [
                        "React Testing Library Documentation",
                        "Full Stack Open (University of Helsinki)"
                    ]
                }
            ]
        }

    # 2. Backend / Software Engineer Roadmap Fallback
    if any(k in r_lower for k in ["backend", "software", "sde", "java", "node", "python", "full stack"]):
        return {
            "skill_gaps": ["Microservices & Docker Containerization", "Database Optimization & Caching (Redis/Postgres)"],
            "roadmaps": [
                {
                    "skill": "Microservices Architecture & Docker Containerization",
                    "timeframe": "4 Weeks",
                    "weekly_plan": [
                        {"week": "Week 1: RESTful API Design & Best Practices", "focus": "Clean architecture, dependency injection, and JWT auth.", "task": "Build modular API service with OpenAPI/Swagger docs."},
                        {"week": "Week 2: Docker & Container Orchestration", "focus": "Multi-stage Dockerfiles, Docker Compose, and networking.", "task": "Containerize backend API, database, and Redis cache."},
                        {"week": "Week 3-4: Capstone Scalable Microservice", "focus": "Message queues (RabbitMQ/Kafka) and resilience patterns.", "task": "Deploy multi-container backend system to cloud with CI/CD pipeline."}
                    ],
                    "portfolio_project_blueprint": {
                        "title": "Scalable Distributed Task & Notification Engine",
                        "recommended_dataset": "Simulated High-Throughput Event Streams",
                        "key_deliverables": [
                            "Decoupled asynchronous worker queue with Redis / RabbitMQ",
                            "Containerized deployment using Docker Compose",
                            "Rate limiting, logging middleware, and Prometheus metrics"
                        ],
                        "github_prompt": "Include system architecture diagrams and API specs in README.md"
                    },
                    "recommended_certifications": [
                        "AWS Certified Developer - Associate",
                        "Docker Certified Associate (DCA)"
                    ],
                    "free_learning_resources": [
                        "Docker Official Documentation & Tutorials",
                        "System Design Primer (GitHub)"
                    ]
                }
            ]
        }

    # 3. DevOps & Cloud Engineer Roadmap Fallback
    if any(k in r_lower for k in ["devops", "cloud", "aws", "azure", "kubernetes", "sre", "platform", "infra"]):
        return {
            "skill_gaps": ["Kubernetes Cluster Orchestration", "Infrastructure as Code (Terraform)"],
            "roadmaps": [
                {
                    "skill": "Kubernetes Orchestration & Helm Deployment",
                    "timeframe": "4 Weeks",
                    "weekly_plan": [
                        {"week": "Week 1: Pods, Services & Deployments", "focus": "Cluster architecture, manifests, namespaces, and networking.", "task": "Deploy multi-tier application with ClusterIP and Ingress."},
                        {"week": "Week 2: ConfigMaps, Secrets & Helm", "focus": "Configuration management and package templating.", "task": "Package app into reusable Helm chart with values.yaml."},
                        {"week": "Week 3-4: Capstone CI/CD GitOps Pipeline", "focus": "ArgoCD automated sync, health probes, and Prometheus metrics.", "task": "Publish automated Kubernetes GitOps pipeline repository to GitHub."}
                    ],
                    "portfolio_project_blueprint": {
                        "title": "Production-Grade GitOps Kubernetes Deployment Pipeline",
                        "recommended_dataset": "Microservices Demo App (Google Cloud)",
                        "key_deliverables": [
                            "Helm chart templates for frontend and backend microservices",
                            "ArgoCD continuous deployment configuration",
                            "Prometheus and Grafana cluster monitoring dashboard"
                        ],
                        "github_prompt": "Document cluster architecture and deployment steps in README.md"
                    },
                    "recommended_certifications": [
                        "Certified Kubernetes Administrator (CKA)",
                        "AWS Certified Solutions Architect - Associate"
                    ],
                    "free_learning_resources": [
                        "Kubernetes Documentation (k8s.io)",
                        "KubeAcademy by VMware"
                    ]
                }
            ]
        }

    # 4. QA / Test Automation Engineer Roadmap Fallback
    if any(k in r_lower for k in ["qa", "test", "sdet", "quality", "selenium", "cypress", "playwright"]):
        return {
            "skill_gaps": ["Playwright / Cypress Automation Frameworks", "API Automation & CI/CD Integration"],
            "roadmaps": [
                {
                    "skill": "End-to-End Test Automation with Playwright",
                    "timeframe": "4 Weeks",
                    "weekly_plan": [
                        {"week": "Week 1: Page Object Model & Selectors", "focus": "Robust locator strategies, test fixtures, and POM design.", "task": "Build POM test suite for an e-commerce workflow."},
                        {"week": "Week 2: API & Visual Regression Testing", "focus": "Mocking API requests, interceptors, and snapshot testing.", "task": "Automate backend API and UI contract tests."},
                        {"week": "Week 3-4: Capstone CI/CD Automation Suite", "focus": "Parallel test runs, Allure reports, and GitHub Actions triggers.", "task": "Publish automated test framework with HTML reporting to GitHub."}
                    ],
                    "portfolio_project_blueprint": {
                        "title": "Full-Stack Enterprise Test Automation Framework",
                        "recommended_dataset": "SauceDemo / Conduit RealWorld App",
                        "key_deliverables": [
                            "Playwright TypeScript framework with Page Object Model",
                            "Automated API testing suite validating status codes and schemas",
                            "GitHub Actions workflow publishing interactive HTML test reports"
                        ],
                        "github_prompt": "Include test execution badges and reporting screenshots in README.md"
                    },
                    "recommended_certifications": [
                        "ISTQB Certified Tester Foundation Level",
                        "Playwright Automation Specialist"
                    ],
                    "free_learning_resources": [
                        "Playwright Official Documentation",
                        "TestAutomationU by Applitools"
                    ]
                }
            ]
        }

    # 5. Mobile App Developer Roadmap Fallback
    if any(k in r_lower for k in ["mobile", "android", "ios", "flutter", "react native", "swift", "kotlin"]):
        return {
            "skill_gaps": ["Cross-Platform Architecture (Flutter/React Native)", "Offline Storage & Push Notifications"],
            "roadmaps": [
                {
                    "skill": "Cross-Platform State Management & App Deployment",
                    "timeframe": "4 Weeks",
                    "weekly_plan": [
                        {"week": "Week 1: Reactive State Architecture", "focus": "Provider / Bloc / Redux state flows and reactive streams.", "task": "Implement clean architecture state container."},
                        {"week": "Week 2: Offline Persistence & REST API Integration", "focus": "SQLite/Hive caching, background sync, and secure storage.", "task": "Build offline-first data synchronization engine."},
                        {"week": "Week 3-4: Capstone Mobile Application", "focus": "Push notifications, responsive UI animations, and app bundling.", "task": "Publish complete cross-platform app repository with demo video to GitHub."}
                    ],
                    "portfolio_project_blueprint": {
                        "title": "Offline-First Real-Time Mobile Tracker & Feed",
                        "recommended_dataset": "Public OpenWeather / NewsAPI / Firebase",
                        "key_deliverables": [
                            "Cross-platform responsive UI with smooth animations",
                            "Local offline caching with automatic network reconciliation",
                            "Biometric authentication and secure local storage"
                        ],
                        "github_prompt": "Include APK / TestFlight instructions and architecture in README.md"
                    },
                    "recommended_certifications": [
                        "Google Associate Android Developer",
                        "Flutter Certified Application Developer"
                    ],
                    "free_learning_resources": [
                        "Flutter Documentation (flutter.dev)",
                        "React Native Official Docs"
                    ]
                }
            ]
        }

    # 6. AI, Machine Learning & GenAI Roadmap Fallback
    if any(k in r_lower for k in ["ai", "ml", "machine learning", "data science", "genai", "deep learning", "llm"]):
        return {
            "skill_gaps": ["RAG Architecture & LangChain/LlamaIndex", "Production MLOps & Model Deployment"],
            "roadmaps": [
                {
                    "skill": "Retrieval-Augmented Generation (RAG) & Vector Databases",
                    "timeframe": "4 Weeks",
                    "weekly_plan": [
                        {"week": "Week 1: Document Chunking & Embeddings", "focus": "Embedding models, chunking strategies, and similarity search.", "task": "Build vector ingestion pipeline with ChromaDB/Pinecone."},
                        {"week": "Week 2: LangChain RAG & Context Retrieval", "focus": "Hybrid search, re-ranking, and prompt engineering.", "task": "Create question-answering assistant over custom PDF docs."},
                        {"week": "Week 3-4: Capstone GenAI Knowledge Agent", "focus": "FastAPI streaming backend, Streamlit/React UI, and evaluation metrics.", "task": "Deploy production RAG application with evaluation pipeline to GitHub."}
                    ],
                    "portfolio_project_blueprint": {
                        "title": "Enterprise Knowledge Base RAG Assistant with Hybrid Search",
                        "recommended_dataset": "Company Financial Filings / Technical Documentation",
                        "key_deliverables": [
                            "Document parser and vector embedding ingestion pipeline",
                            "LangChain/LlamaIndex query engine with reciprocal rank fusion",
                            "Automated hallucination check and faithfulness scoring"
                        ],
                        "github_prompt": "Document architecture diagram and RAG evaluation metrics in README.md"
                    },
                    "recommended_certifications": [
                        "AWS Certified Machine Learning - Specialty",
                        "DeepLearning.AI Generative AI Professional"
                    ],
                    "free_learning_resources": [
                        "DeepLearning.AI Short Courses",
                        "Hugging Face NLP Course"
                    ]
                }
            ]
        }

    # 7. Default / Data & BI Analyst Roadmap Fallback
    return {
        "skill_gaps": ["DAX & Advanced Power BI Data Modeling", "Azure Data Factory & Cloud Analytics"],
        "roadmaps": [
            {
                "skill": "DAX & Advanced Power BI Data Modeling",
                "timeframe": "4 Weeks",
                "weekly_plan": [
                    {"week": "Week 1: Calculated Columns vs Measures", "focus": "Filter Context, Row Context, and Basic Aggregate Measures (SUMX, CALCULATE).", "task": "Build 10 essential financial measures on a sample sales dataset."},
                    {"week": "Week 2: Advanced Time Intelligence & Variables", "focus": "YTD, YoY Growth, Rolling Averages, and VAR syntax optimization.", "task": "Create dynamic YoY variance matrix and interactive trend charts."},
                    {"week": "Week 3-4: Capstone Portfolio Dashboard", "focus": "Star Schema design, Performance Analyzer query tuning, and RLS.", "task": "Deploy a multi-page Executive KPI Dashboard on 50,000+ records to GitHub."}
                ],
                "portfolio_project_blueprint": {
                    "title": "SaaS Subscription Churn & Executive BI Dashboard",
                    "recommended_dataset": "Telecom / SaaS Customer Churn Dataset (50K records)",
                    "key_deliverables": [
                        "Star schema semantic data model with Date table",
                        "15+ custom DAX measures calculating MRR, Churn Rate, and LTV",
                        "Interactive Power BI report with drill-through filters"
                    ],
                    "github_prompt": "Include data model ER diagram and dashboard screenshots in README.md"
                },
                "recommended_certifications": [
                    "PL-300: Microsoft Power BI Data Analyst",
                    "Oracle Analytics Cloud 2025 Certified Professional"
                ],
                "free_learning_resources": [
                    "Microsoft Learn: Model Data in Power BI",
                    "SQLBI: Introduction to DAX Video Series"
                ]
            }
        ]
    }
