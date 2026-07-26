from datetime import datetime, timedelta

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func, select

from extensions import db
from models.application import ATSAnalysis, JobApplication
from models.interview import InterviewEvent, InterviewQuestion, InterviewSession
from services.gemini_service import career_recommendation
from services.readiness_service import calculate_readiness
from services.skill_gap_service import build_skill_gap

dashboard_bp = Blueprint("dashboard", __name__)


def readiness_for_user(user):
    applications = list(user.applications)
    analyses = db.session.scalars(select(ATSAnalysis).where(ATSAnalysis.user_id == user.id)).all()
    avg_ats = round(sum(a.score for a in analyses) / len(analyses), 1) if analyses else 0.0
    gaps = build_skill_gap(applications, user.skills, [resume.extracted_text for resume in user.resumes])
    sessions = db.session.scalars(select(InterviewSession).where(InterviewSession.user_id == user.id)).all()
    total_questions = sum(len(session.questions) for session in sessions)
    answered = sum(1 for session in sessions for q in session.questions if q.score is not None)
    interview_prep = round(answered / total_questions * 100, 1) if total_questions else 0.0
    return calculate_readiness(avg_ats, gaps["coverage"], interview_prep, user.profile_completion), gaps, avg_ats


@dashboard_bp.get("/")
@login_required
def index():
    readiness, gaps, avg_ats = readiness_for_user(current_user)
    applications = list(current_user.applications)
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    metrics = {
        "total": len(applications),
        "this_month": sum((a.application_date or a.created_at.date()) >= month_start for a in applications),
        "interviews": sum(a.status == "Interview" for a in applications),
        "offers": sum(a.status == "Offer" for a in applications),
        "rejections": sum(a.status == "Rejected" for a in applications),
        "avg_ats": avg_ats,
    }
    upcoming = db.session.scalars(select(InterviewEvent).where(InterviewEvent.user_id == current_user.id,
        InterviewEvent.scheduled_at >= datetime.utcnow()).order_by(InterviewEvent.scheduled_at).limit(5)).all()
    status_labels = ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected", "Withdrawn"]
    status_data = [sum(a.status == status for a in applications) for status in status_labels]
    trend = {}
    for app in applications:
        day = (app.application_date or app.created_at.date()).strftime("%b %d")
        trend[day] = trend.get(day, 0) + 1
    chart_data = {"status": {"labels": status_labels, "data": status_data}, "trend": {"labels": list(trend.keys())[-8:], "data": list(trend.values())[-8:]}}
    return render_template("dashboard/index.html", metrics=metrics, readiness=readiness, gaps=gaps,
                           applications=sorted(applications, key=lambda a: a.updated_at, reverse=True)[:6],
                           upcoming=upcoming, chart_data=chart_data,
                           career_recommendation=career_recommendation(gaps["missing"]), now=datetime.utcnow,
                           timedelta=timedelta)
