import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("RAPIDAPI_KEY")
host = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")

print("Key length:", len(key) if key else 0)
print("Host:", host)

url = "https://jsearch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": key,
    "X-RapidAPI-Host": host
}
params = {
    "query": "Data Analyst in Hyderabad",
    "page": "1",
    "num_pages": "1"
}

response = requests.get(url, headers=headers, params=params)
print("Status Code:", response.status_code)
print("Response Headers:", dict(response.headers))
print("Response Body:", response.text)
