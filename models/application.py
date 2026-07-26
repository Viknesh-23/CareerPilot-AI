from datetime import datetime

from extensions import db


class JobApplication(db.Model):
    __tablename__ = "job_applications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company_name = db.Column(db.String(150), nullable=False)
    job_role = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, default="")
    job_url = db.Column(db.String(500), default="")
    location = db.Column(db.String(120), default="")
    work_mode = db.Column(db.String(30), default="On-site")
    salary_ctc = db.Column(db.String(80), default="")
    source = db.Column(db.String(100), default="")
    status = db.Column(db.String(30), default="Saved", nullable=False, index=True)
    application_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, default="")
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="applications")
    resume = db.relationship("Resume", back_populates="applications")
    activities = db.relationship("ApplicationActivity", back_populates="application", cascade="all, delete-orphan", order_by="ApplicationActivity.created_at.desc()")
    analyses = db.relationship("ATSAnalysis", back_populates="application", cascade="all, delete-orphan", order_by="ATSAnalysis.created_at.desc()")
    interview_sessions = db.relationship("InterviewSession", back_populates="application", cascade="all, delete-orphan")
    events = db.relationship("InterviewEvent", back_populates="application", cascade="all, delete-orphan")


class ApplicationActivity(db.Model):
    __tablename__ = "application_activities"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("job_applications.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    old_status = db.Column(db.String(30), default="")
    new_status = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    application = db.relationship("JobApplication", back_populates="activities")


class ATSAnalysis(db.Model):
    __tablename__ = "ats_analyses"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("job_applications.id"), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)
    matched_skills = db.Column(db.JSON, default=list)
    missing_skills = db.Column(db.JSON, default=list)
    keywords = db.Column(db.JSON, default=list)
    suggestions = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    application = db.relationship("JobApplication", back_populates="analyses")
    resume = db.relationship("Resume", back_populates="analyses")
