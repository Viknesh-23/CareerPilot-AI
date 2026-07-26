"""Create clearly fake local demo data: `python scripts/seed_data.py`."""
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from extensions import db
from models.application import ATSAnalysis, ApplicationActivity, JobApplication
from models.interview import InterviewEvent, InterviewQuestion, InterviewSession
from models.resume import Resume
from models.user import User


app = create_app()


def main():
    with app.app_context():
        db.create_all()
        email = "demo@careerpilot.local"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(full_name="Aarav Demo", email=email, college="Fictional Institute of Technology",
                        degree="B.Tech Information Technology", graduation_year=2027,
                        skills="Python, Flask, SQL, JavaScript, Git, Docker", preferred_role="Backend Developer",
                        preferred_location="Bengaluru", github_url="https://github.com/aarav-demo",
                        linkedin_url="https://linkedin.com/in/aarav-demo")
            user.set_password("DemoPass123!")
            db.session.add(user)
            db.session.flush()
        else:
            db.session.query(JobApplication).filter_by(user_id=user.id).delete()
            db.session.commit()
        resume = Resume.query.filter_by(user_id=user.id, name="Demo Backend Resume").first()
        if not resume:
            resume = Resume(user_id=user.id, name="Demo Backend Resume", filename="demo-backend.pdf",
                            stored_path="", extracted_text="Python Flask SQL PostgreSQL Docker Git REST API pytest")
            db.session.add(resume)
            db.session.flush()
        jobs = [
            ("Northstar Labs", "Python Backend Intern", "Python Flask PostgreSQL Docker REST API pytest Git", "Applied"),
            ("Blue Orbit", "Full Stack Intern", "JavaScript React Node.js SQL AWS teamwork", "Interview"),
            ("Vertex Systems", "Software Engineer Intern", "Python data structures algorithms Linux Git CI/CD", "Assessment"),
            ("Pixel Forge", "Web Developer", "HTML CSS JavaScript React Figma communication", "Saved"),
            ("Cloudseed", "Cloud Support Intern", "AWS Docker Kubernetes Linux networking Python", "Offer"),
            ("Data Quarry", "Data Analyst Intern", "Python SQL pandas Power BI Excel data analysis", "Rejected"),
        ]
        created = []
        for i, (company, role, jd, status) in enumerate(jobs):
            application = JobApplication(user_id=user.id, company_name=company, job_role=role, job_description=jd,
                                         location="Bengaluru", work_mode="Hybrid", salary_ctc="₹6 LPA", source="Demo seed",
                                         status=status, application_date=date.today() - timedelta(days=i * 5))
            db.session.add(application)
            db.session.flush()
            db.session.add(ApplicationActivity(application_id=application.id, user_id=user.id, old_status="", new_status="Saved", message="Application created"))
            if status != "Saved":
                db.session.add(ApplicationActivity(application_id=application.id, user_id=user.id, old_status="Saved", new_status=status, message=f"Status changed to {status}"))
            db.session.add(ATSAnalysis(application_id=application.id, user_id=user.id, resume_id=resume.id,
                                       score=72 - i * 4, matched_skills=["python", "git"], missing_skills=["aws"],
                                       keywords=["python", "docker"], suggestions=["Add measurable project outcomes."]))
            created.append(application)
        event = InterviewEvent(user_id=user.id, application_id=created[1].id, event_type="Technical Interview",
                               round_name="Technical round", scheduled_at=datetime.utcnow() + timedelta(days=2), notes="Fake local demo event")
        db.session.add(event)
        session = InterviewSession(user_id=user.id, application_id=created[0].id, status="completed", overall_score=74,
                                   technical_score=76, hr_score=80, behavioral_score=70, jd_score=70, completed_at=datetime.utcnow())
        db.session.add(session)
        db.session.flush()
        db.session.add(InterviewQuestion(session_id=session.id, category="Technical", prompt="Explain how you structure a Flask application.", position=1, answer="I use blueprints and services.", score=76, feedback="Clear architecture answer.", strengths=["Direct answer"], improvements=["Add a project example."], suggested_answer="Describe blueprints, services, models, and a concrete project result."))
        db.session.commit()
        print("Demo data ready. Email: demo@careerpilot.local  Password: DemoPass123!")


if __name__ == "__main__":
    main()
