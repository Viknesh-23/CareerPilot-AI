from datetime import datetime

from extensions import db


class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey("job_applications.id"), nullable=False, index=True)
    status = db.Column(db.String(30), default="prepared", nullable=False)
    overall_score = db.Column(db.Float, nullable=True)
    technical_score = db.Column(db.Float, nullable=True)
    hr_score = db.Column(db.Float, nullable=True)
    behavioral_score = db.Column(db.Float, nullable=True)
    jd_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="interview_sessions")
    application = db.relationship("JobApplication", back_populates="interview_sessions")
    questions = db.relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.position")


class InterviewQuestion(db.Model):
    __tablename__ = "interview_questions"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("interview_sessions.id"), nullable=False, index=True)
    category = db.Column(db.String(30), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.Text, default="")
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, default="")
    strengths = db.Column(db.JSON, default=list)
    improvements = db.Column(db.JSON, default=list)
    suggested_answer = db.Column(db.Text, default="")
    answered_at = db.Column(db.DateTime, nullable=True)

    session = db.relationship("InterviewSession", back_populates="questions")


class InterviewEvent(db.Model):
    __tablename__ = "interview_events"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey("job_applications.id"), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    round_name = db.Column(db.String(120), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False, index=True)
    meeting_url = db.Column(db.String(500), default="")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    application = db.relationship("JobApplication", back_populates="events")
