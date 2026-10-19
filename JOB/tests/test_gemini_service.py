import pytest
from services.gemini_service import GeminiService

def test_gemini_service_availability():
    service_no_key = GeminiService(api_key="")
    assert service_no_key.is_available() is False

    service_with_key = GeminiService(api_key="AIzaSyTestMockKeyForVerification12345")
    assert service_with_key.is_available() is True
    assert service_with_key.get_api_key() == "AIzaSyTestMockKeyForVerification12345"

def test_gemini_json_cleaning():
    service = GeminiService()
    
    # Test raw JSON
    raw_json = '{"parsed_data": {"name": "Alex"}, "ai_critique": {"ats_score_estimate": 90}}'
    parsed = service._clean_and_parse_json(raw_json)
    assert parsed is not None
    assert parsed["parsed_data"]["name"] == "Alex"
    assert parsed["ai_critique"]["ats_score_estimate"] == 90

    # Test markdown fenced JSON
    markdown_json = '''```json
    {
      "parsed_data": {
        "name": "Jordan Doe",
        "skills": ["Python", "Flask", "Docker"]
      },
      "ai_critique": {
        "key_strengths": ["Strong backend skills"]
      }
    }
    ```'''
    parsed_md = service._clean_and_parse_json(markdown_json)
    assert parsed_md is not None
    assert parsed_md["parsed_data"]["name"] == "Jordan Doe"
    assert "Docker" in parsed_md["parsed_data"]["skills"]
    assert "Strong backend skills" in parsed_md["ai_critique"]["key_strengths"]
