from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from extensions import db
from models.application import ATSAnalysis, JobApplication
from models.resume import Resume
from services.ats_service import analyze_resume
from services.report_service import ats_report

ats_bp = Blueprint("ats", __name__, url_prefix="/ats")


def owned_application(application_id):
    app = db.session.get(JobApplication, application_id)
    if not app or app.user_id != current_user.id:
        abort(404)
    return app


def owned_analysis(analysis_id):
    analysis = db.session.get(ATSAnalysis, analysis_id)
    if not analysis or analysis.user_id != current_user.id:
        abort(404)
    return analysis


@ats_bp.route("/applications/<int:application_id>", methods=["GET", "POST"])
@login_required
def analyze(application_id):
    application = owned_application(application_id)
    resumes = db.session.scalars(select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())).all()
    if request.method == "POST":
        resume_id = request.form.get("resume_id", type=int) or application.resume_id
        resume = db.session.get(Resume, resume_id) if resume_id else None
        if not resume or resume.user_id != current_user.id:
            flash("Choose one of your uploaded resumes.", "danger")
        elif not application.job_description.strip():
            flash("Add a job description before running ATS analysis.", "warning")
        else:
            result = analyze_resume(resume.extracted_text, application.job_description)
            analysis = ATSAnalysis(application_id=application.id, resume_id=resume.id, user_id=current_user.id, **{key: result[key] for key in ("score", "matched_skills", "missing_skills", "keywords", "suggestions")})
            db.session.add(analysis)
            application.resume_id = resume.id
            db.session.commit()
            flash("ATS analysis completed.", "success")
            return redirect(url_for("ats.result", analysis_id=analysis.id))
    latest = application.analyses[0] if application.analyses else None
    return render_template("ats/result.html", application=application, analysis=latest, resumes=resumes, show_selector=True)


@ats_bp.get("/<int:analysis_id>")
@login_required
def result(analysis_id):
    analysis = owned_analysis(analysis_id)
    return render_template("ats/result.html", application=analysis.application, analysis=analysis, resumes=[], show_selector=False)


@ats_bp.get("/<int:analysis_id>/report.pdf")
@login_required
def report(analysis_id):
    analysis = owned_analysis(analysis_id)
    return send_file(ats_report(current_user, analysis), mimetype="application/pdf", as_attachment=True,
                     download_name=f"ats-analysis-{analysis.id}.pdf")
