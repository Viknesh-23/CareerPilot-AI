from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    college = db.Column(db.String(180), default="")
    degree = db.Column(db.String(120), default="")
    graduation_year = db.Column(db.Integer, nullable=True)
    skills = db.Column(db.Text, default="")
    preferred_role = db.Column(db.String(120), default="")
    preferred_location = db.Column(db.String(120), default="")
    github_url = db.Column(db.String(255), default="")
    linkedin_url = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    applications = db.relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    resumes = db.relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = db.relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def profile_completion(self):
        fields = [self.full_name, self.college, self.degree, self.graduation_year,
                  self.skills, self.preferred_role, self.preferred_location,
                  self.github_url, self.linkedin_url]
        return round(sum(bool(value) for value in fields) / len(fields) * 100)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
