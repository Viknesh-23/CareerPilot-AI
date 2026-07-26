from datetime import date

from extensions import db
from models.application import JobApplication
from tests.conftest import register


def payload(**extra):
    values = {"company_name": "Acme", "job_role": "Backend Intern", "job_description": "Python Flask SQL Docker", "work_mode": "Remote", "status": "Saved", "application_date": "2026-07-01"}
    values.update(extra)
    return values


def test_application_crud_and_status(app, logged_in):
    response = logged_in.post("/applications/new", data=payload(), follow_redirects=True)
    assert b"Application created" in response.data
    with app.app_context():
        application = JobApplication.query.one()
        identifier = application.id
    response = logged_in.post(f"/applications/{identifier}/status", data={"status": "Applied"}, follow_redirects=True)
    assert b"Status updated" in response.data
    response = logged_in.post(f"/applications/{identifier}/edit", data=payload(company_name="Acme Updated", status="Interview"), follow_redirects=True)
    assert b"Acme Updated" in response.data
    response = logged_in.get("/applications/export/csv")
    assert b"Acme Updated" in response.data
    logged_in.post(f"/applications/{identifier}/delete", follow_redirects=True)
    with app.app_context():
        assert JobApplication.query.count() == 0


def test_other_user_cannot_access_application(app, client):
    register(client, "one@example.com")
    client.post("/applications/new", data=payload())
    with app.app_context():
        identifier = JobApplication.query.one().id
    client.post("/auth/logout")
    register(client, "two@example.com")
    assert client.get(f"/applications/{identifier}").status_code == 404
