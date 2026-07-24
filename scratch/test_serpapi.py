import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from providers.serpapi import search_serpapi_jobs
from config import SERPAPI_API_KEY

print("--- Testing SerpApi Provider ---")
print("SerpApi API Key loaded:", SERPAPI_API_KEY[:6] + "..." if SERPAPI_API_KEY else "Empty")

import requests

try:
    jobs = search_serpapi_jobs("Python SQL")
    print(f"Retrieved {len(jobs)} parsed jobs from SerpApi!")
    for idx, j in enumerate(jobs[:5]):
        print(f"[{idx+1}] {j.title} at {j.company} | Location: {j.location} | Apply Link: {j.apply_url[:80]}...")
except Exception as e:
    print(f"Error testing SerpApi: {e}")
