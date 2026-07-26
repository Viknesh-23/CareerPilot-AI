from extensions import db
from models.application import JobApplication
from models.interview import InterviewSession


def test_interview_workflow(app, logged_in):
    with app.app_context():
        job = JobApplication(user_id=1, company_name="Acme", job_role="Developer", job_description="Python Flask Docker")
        db.session.add(job); db.session.commit(); job_id=job.id
    response = logged_in.post(f"/interviews/applications/{job_id}/prepare", follow_redirects=True)
    assert b"20 tailored questions" in response.data
    with app.app_context():
        session = InterviewSession.query.one(); session_id=session.id; assert len(session.questions) == 20
    logged_in.post(f"/interviews/{session_id}/start")
    for position in range(1, 21):
        response = logged_in.post(f"/interviews/{session_id}/mock", data={"position": position, "answer": "Situation task action result. I designed a Python Flask API, tested it, and improved performance by 20 percent."})
        assert response.status_code == 302
    response = logged_in.get(f"/interviews/{session_id}/result")
    assert b"Mock interview report" in response.data
