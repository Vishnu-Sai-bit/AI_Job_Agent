import pytest
from app import create_app
from extensions import db
from models.job import Job
from models.job_source import JobSource

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Find or create test source
        source = JobSource.query.filter_by(platform="greenhouse", company_key="stripe").first()
        if not source:
            source = JobSource(
                platform="greenhouse",
                company_key="stripe",
                name="Stripe Greenhouse"
            )
            db.session.add(source)
            db.session.commit()

        job_active = Job(
            source_id=source.id,
            source_platform="greenhouse",
            source_company_key="stripe",
            source_job_id="test-1001",
            title="Software Engineer",
            company="Stripe",
            location="San Francisco, CA",
            original_url="https://boards.greenhouse.io/stripe/jobs/1001",
            apply_url="https://boards.greenhouse.io/stripe/jobs/1001#app",
            status="active"
        )
        job_closed = Job(
            source_id=source.id,
            source_platform="greenhouse",
            source_company_key="stripe",
            source_job_id="test-1002",
            title="Closed Position",
            company="Stripe",
            location="Remote",
            original_url="https://boards.greenhouse.io/stripe/jobs/1002",
            apply_url="https://boards.greenhouse.io/stripe/jobs/1002#app",
            status="closed"
        )
        db.session.add_all([job_active, job_closed])
        db.session.commit()

        app.test_active_job_id = job_active.id
        app.test_closed_job_id = job_closed.id

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_apply_redirect_non_existent_job(client):
    response = client.get("/apply/99999")
    assert response.status_code == 404

def test_apply_redirect_closed_job(client, app):
    # Closed job must not redirect to external link; redirects back to details with warning
    response = client.get(f"/apply/{app.test_closed_job_id}", follow_redirects=False)
    assert response.status_code == 302
    assert f"/jobs/{app.test_closed_job_id}" in response.headers["Location"]

def test_apply_redirect_ignores_query_params(client, app):
    # Query parameters trying to inject external open redirect must be completely ignored
    response = client.get(f"/apply/{app.test_active_job_id}?dest=https://evil-attacker.com", follow_redirects=False)
    assert response.status_code == 302
    # Ensure it redirects to the database-stored Stripe URL, NOT the attacker URL
    assert "evil-attacker.com" not in response.headers["Location"]
    assert "boards.greenhouse.io" in response.headers["Location"]
