"""
==========================================================
AI JobAgent - In-Memory Vector Store & Semantic Matcher
Author : Antigravity
==========================================================
"""

from typing import List, Dict, Any
import math
from utils.llm import get_embedding
from models import JobData, ResumeData

class VectorStore:
    def __init__(self):
        # Store items as a list of dict: {"id": str, "vector": List[float], "metadata": Dict}
        self.documents = []

    def add_job(self, job: JobData):
        """
        Embed and index a job document.
        """
        # Build text representation from title, company, description, and skills
        text = f"{job.title} at {job.company}. Location: {job.location or 'Remote'}. Required Skills: {', '.join(job.skills or [])}. Description: {job.description or ''}"
        vector = get_embedding(text)
        self.documents.append({
            "id": job.id or f"{job.title}-{job.company}",
            "vector": vector,
            "job": job
        })

    def similarity_search(self, query_text: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for top k similar jobs matching query text.
        """
        query_vector = get_embedding(query_text)
        results = []
        for doc in self.documents:
            v_doc = doc["vector"]
            # Cosine similarity (since both vectors are L2 normalized, dot product is cosine similarity)
            dot_product = sum(q * d for q, d in zip(query_vector, v_doc))
            results.append({
                "job": doc["job"],
                "score": dot_product
            })
        
        # Sort by similarity score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

def calculate_semantic_similarity(resume: ResumeData, job: JobData) -> float:
    """
    Calculate semantic match score (0.0 to 100.0) between resume and job text.
    """
    try:
        resume_text = f"{resume.preferred_role or ''}. Skills: {', '.join(resume.skills or [])}."
        job_text = f"{job.title or ''}. Skills: {', '.join(job.skills or [])}. Description: {job.description or ''}"
        
        # Generate embeddings
        r_vector = get_embedding(resume_text)
        j_vector = get_embedding(job_text)
        
        # Cosine similarity
        dot_prod = sum(r * j for r, j in zip(r_vector, j_vector))
        
        # Scale cosine similarity (which lies in [0.0, 1.0]) to percentage
        # Clamp to [0.0, 100.0]
        score = max(0.0, min(100.0, dot_prod * 100.0))
        return round(score, 2)
    except Exception:
        return 0.0
