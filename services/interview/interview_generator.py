"""
==========================================================
AI JobAgent - Interview Simulator Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are a {interviewer_role} at a top-tier technology MNC.
Your job is to generate a comprehensive list of realistic mock interview questions and answers tailored to the candidate's resume context and target role.

Generate the questions following this JSON schema exactly:
{{
    "questions": [
        {{
            "type": "Technical / Behavioral / Scenario",
            "question": "The interview question text...",
            "answer_tips": "Key talking points, technical keywords to include, or what the interviewer is looking for (keep to 2 sentences)...",
            "sample_answer": "A model response showing how to answer this question professionally (keep to 2-3 sentences)..."
        }}
    ]
}}

Generate exactly {question_count} distinct questions (a balanced mix of Technical, Behavioral, and Scenario-based questions matching the tone of a {interviewer_role}).

Target Role: {role}
Skills: {skills}
Candidate Resume Context (if available): {resume_context}

CRITICAL:
1. Tailor at least 50% of the questions directly to the candidate's projects, metrics, tools (e.g. Tableau, Power BI, Python, SQL), and work history mentioned in their context.
2. Generate all {question_count} questions without stopping.
3. Return ONLY the raw valid JSON structure. Do NOT add any preamble or markdown explanation.
"""

def generate_interview_questions(
    role: str,
    skills: List[str],
    resume_context: str = "",
    question_count: int = 5,
    interviewer_role: str = "Senior Technical Recruiter"
) -> Dict[str, Any]:
    """
    Generate mock interview questions and answers using the LLM helper.
    """
    skills_str = ", ".join(skills) if skills else "Data Analysis, Python, SQL"
    formatted_prompt = PROMPT.format(
        role=role or "Data Analyst",
        skills=skills_str,
        resume_context=resume_context or "Not Provided",
        question_count=question_count,
        interviewer_role=interviewer_role
    )

    info(f"Generating {question_count} mock interview questions for: {role}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        # Strip potential markdown fences
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        data = json.loads(cleaned.strip())
        if isinstance(data, dict) and "questions" in data and len(data["questions"]) > 0:
            return data
        raise ValueError("Invalid questions format returned by LLM")
    except Exception as e:
        exception(f"Mock interview question generation failed: {e}")
        
        # Dynamic fallback list matching requested question_count
        skill_list = skills if skills else ["SQL", "Python", "Power BI", "Data Analysis", "Tableau", "Excel"]
        fallback_pool = [
            {
                "type": "Technical",
                "question": f"How do you approach data cleaning and handling missing/duplicate records in a large dataset using {skill_list[0]}?",
                "answer_tips": "Discuss profiling data schemas, handling nulls with median/mean/imputation, and writing deduplication queries.",
                "sample_answer": "I first profile the column schema to quantify missing values, then apply business logic rules to clean nulls and resolve inconsistencies before downstream analysis."
            },
            {
                "type": "Technical",
                "question": f"Can you explain the difference between Window Functions and GROUP BY in {skill_list[0] if len(skill_list) > 0 else 'SQL'}?",
                "answer_tips": "Highlight that GROUP BY collapses rows whereas Window Functions perform calculations across rows while retaining individual row details.",
                "sample_answer": "GROUP BY aggregates individual rows into summary groups. Window functions like ROW_NUMBER() or RANK() perform calculations across a partition while preserving each individual record."
            },
            {
                "type": "Scenario",
                "question": "If an executive stakeholder notes a 15% discrepancy in KPI reporting between two dashboards, how do you debug it?",
                "answer_tips": "Focus on data validation, tracing ETL query transformations, and verifying date cutoff filters.",
                "sample_answer": "I trace the data pipeline backwards from the visualization layer to the raw data, inspecting join conditions, filter rules, and time-zone definitions to identify the root cause."
            },
            {
                "type": "Behavioral",
                "question": "Describe a situation where you had to convey complex analytical findings to non-technical business leaders.",
                "answer_tips": "Use the STAR method and focus on business value, metrics, and actionable recommendations.",
                "sample_answer": "I translated intricate statistical churn drivers into a visual Power BI dashboard with simple KPI cards, enabling managers to understand the 46% churn risk immediately."
            },
            {
                "type": "Technical",
                "question": f"How do you optimize slow-running queries and dashboard load times when handling 50,000+ records in {skill_list[1] if len(skill_list) > 1 else 'Python/SQL'}?",
                "answer_tips": "Mention indexing, selecting only required columns, and leveraging aggregated views or vectorized operations.",
                "sample_answer": "I optimize queries by creating indexes on foreign keys, avoiding SELECT *, and filtering early. In Python, I utilize vectorized Pandas operations instead of iterating over rows."
            },
            {
                "type": "Scenario",
                "question": "How do you prioritize multiple urgent dashboard and reporting requests from different department leads?",
                "answer_tips": "Discuss evaluating business impact, alignment with core KPIs, and clear communication on delivery timelines.",
                "sample_answer": "I assess each request by potential business revenue impact and urgency, communicate realistic ETA milestones to stakeholders, and deliver minimum viable reports first."
            },
            {
                "type": "Technical",
                "question": f"What is your methodology for building predictive machine learning models in {skill_list[1] if len(skill_list) > 1 else 'Python'}?",
                "answer_tips": "Walk through EDA, feature engineering, train-test splitting, model training, and evaluation metrics.",
                "sample_answer": "I perform thorough exploratory data analysis, encode categorical features, evaluate baseline algorithms like Random Forest, and validate accuracy and ROC-AUC on an unseen test set."
            },
            {
                "type": "Behavioral",
                "question": "Tell me about a time you identified a data quality issue before it impacted production decisions.",
                "answer_tips": "Highlight attention to detail, automated validation scripts, and communication with engineering.",
                "sample_answer": "During an internship project, I discovered 1,200+ schema mismatches and nulls across 30,000 records, built validation scripts to cleanse the data, and raised verified accuracy to over 95%."
            },
            {
                "type": "Scenario",
                "question": "Suppose a stakeholder requests a chart that you believe misrepresents the data. How do you handle it?",
                "answer_tips": "Emphasize data integrity, constructive communication, and presenting alternative accurate visualizations.",
                "sample_answer": "I politely explain why the requested representation could lead to misleading conclusions and present an alternative visualization that clearly and accurately conveys the true insight."
            },
            {
                "type": "Behavioral",
                "question": "What is your process for keeping up with new tools, cloud technologies, and data engineering frameworks?",
                "answer_tips": "Mention certifications, hands-on projects on GitHub, and following industry publications.",
                "sample_answer": "I regularly complete professional certifications, such as Oracle Cloud and Analytics certifications, and build hands-on end-to-end projects published on GitHub to apply new concepts."
            }
        ]
        
        # Multiply and slice to guarantee exact requested question_count
        questions = []
        for i in range(question_count):
            base_q = fallback_pool[i % len(fallback_pool)].copy()
            if i >= len(fallback_pool):
                base_q["question"] = f"[{base_q['type']} Part {i // len(fallback_pool) + 1}] " + base_q["question"]
            questions.append(base_q)
            
        return {"questions": questions}
