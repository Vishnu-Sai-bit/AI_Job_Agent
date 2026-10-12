"""
==========================================================
Integration Tests - Route Endpoints
==========================================================
"""

def test_routes_status_200(client):
    endpoints = [
        "/",
        "/dashboard/",
        "/jobs/",
        "/ai-job-agent/",
        "/resumes/",
        "/applications/",
        "/interviews/",
        "/career-intelligence",
        "/learning-hub/",
        "/analytics/",
        "/assistant/",
        "/automations/",
        "/notifications/",
        "/profile/",
        "/settings/",
        "/auth/login"
    ]
    for ep in endpoints:
        res = client.get(ep, follow_redirects=True)
        assert res.status_code == 200, f"Endpoint {ep} failed with status {res.status_code}"
