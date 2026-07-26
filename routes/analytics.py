from collections import Counter
from datetime import datetime

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import select

from extensions import db
from models.application import ATSAnalysis
from models.interview import InterviewSession
from routes.dashboard import readiness_for_user

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.get("/")
@login_required
def index():
    applications = list(current_user.applications)
    statuses = ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected", "Withdrawn"]
    by_status = [sum(app.status == status for app in applications) for status in statuses]
    by_month = Counter((app.application_date or app.created_at.date()).strftime("%Y-%m") for app in applications)
    companies = Counter(app.company_name for app in applications)
    roles = Counter(app.job_role for app in applications)
    analyses = db.session.scalars(select(ATSAnalysis).where(ATSAnalysis.user_id == current_user.id)).all()
    distribution = [0] * 5
    for analysis in analyses:
        distribution[min(4, int(analysis.score // 20))] += 1
    sessions = db.session.scalars(select(InterviewSession).where(InterviewSession.user_id == current_user.id, InterviewSession.status == "completed").order_by(InterviewSession.completed_at)).all()
    readiness, gaps, _ = readiness_for_user(current_user)
    contacted = sum(app.status in {"Assessment", "Interview", "Offer"} for app in applications)
    offers = sum(app.status == "Offer" for app in applications)
    conversion = {"interview": round(contacted / len(applications) * 100, 1) if applications else 0, "offer": round(offers / len(applications) * 100, 1) if applications else 0}
    charts = {
        "status": {"labels": statuses, "data": by_status},
        "time": {"labels": list(by_month.keys()), "data": list(by_month.values())},
        "ats": {"labels": ["0–19", "20–39", "40–59", "60–79", "80–100"], "data": distribution},
        "companies": {"labels": [x[0] for x in companies.most_common(8)], "data": [x[1] for x in companies.most_common(8)]},
        "roles": {"labels": [x[0] for x in roles.most_common(8)], "data": [x[1] for x in roles.most_common(8)]},
        "demand": {"labels": [x["skill"] for x in gaps["demand"][:8]], "data": [x["count"] for x in gaps["demand"][:8]]},
        "missing": {"labels": gaps["missing"][:8], "data": [next((x["count"] for x in gaps["demand"] if x["skill"] == skill), 0) for skill in gaps["missing"][:8]]},
        "performance": {"labels": [s.completed_at.strftime("%b %d") for s in sessions], "data": [s.overall_score for s in sessions]},
    }
    return render_template("analytics/index.html", charts=charts, conversion=conversion, readiness=readiness)
