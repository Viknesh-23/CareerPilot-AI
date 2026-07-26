from io import BytesIO

from reportlab.pdfgen import canvas

from extensions import db
from models.application import ATSAnalysis, JobApplication
from models.resume import Resume
from services.ats_service import analyze_resume, extract_skills


def test_skill_normalization():
    assert {"javascript", "postgresql", "machine learning"} <= set(extract_skills("JS postgres ML"))


def test_ats_score_range():
    result = analyze_resume("Python Flask PostgreSQL", "Python Flask PostgreSQL Docker")
    assert 0 <= result["score"] <= 100
    assert "docker" in result["missing_skills"]


def test_ats_route(app, logged_in):
    resume = Resume(user_id=1, name="Resume", filename="r.pdf", stored_path="x", extracted_text="Python Flask SQL")
    application = JobApplication(user_id=1, company_name="Acme", job_role="Developer", job_description="Python Flask SQL Docker")
    with app.app_context():
        db.session.add_all([resume, application]); db.session.commit(); app_id=application.id; resume_id=resume.id
    response = logged_in.post(f"/ats/applications/{app_id}", data={"resume_id": resume_id}, follow_redirects=True)
    assert b"ATS Match Score" in response.data
    with app.app_context():
        assert 0 <= ATSAnalysis.query.one().score <= 100
