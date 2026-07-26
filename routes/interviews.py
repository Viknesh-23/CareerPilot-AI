from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from extensions import db
from models.application import JobApplication
from models.interview import InterviewQuestion, InterviewSession
from services.interview_service import create_questions, evaluate_question, score_session
from services.report_service import interview_report

interviews_bp = Blueprint("interviews", __name__, url_prefix="/interviews")


def owned_session(session_id):
    session = db.session.get(InterviewSession, session_id)
    if not session or session.user_id != current_user.id:
        abort(404)
    return session


@interviews_bp.get("/")
@login_required
def list_sessions():
    sessions = db.session.scalars(select(InterviewSession).where(InterviewSession.user_id == current_user.id).order_by(InterviewSession.created_at.desc())).all()
    applications = db.session.scalars(select(JobApplication).where(JobApplication.user_id == current_user.id).order_by(JobApplication.updated_at.desc())).all()
    return render_template("interviews/list.html", sessions=sessions, applications=applications)


@interviews_bp.post("/applications/<int:application_id>/prepare")
@login_required
def prepare(application_id):
    application = db.session.get(JobApplication, application_id)
    if not application or application.user_id != current_user.id:
        abort(404)
    missing = application.analyses[0].missing_skills if application.analyses else []
    session = InterviewSession(user_id=current_user.id, application_id=application.id, status="prepared")
    db.session.add(session)
    db.session.flush()
    create_questions(session, application.job_role, application.job_description, missing, InterviewQuestion, db)
    flash("Your application-specific interview prep workspace is ready.", "success")
    return redirect(url_for("interviews.prep", session_id=session.id))


@interviews_bp.get("/<int:session_id>/prep")
@login_required
def prep(session_id):
    return render_template("interviews/prep.html", session=owned_session(session_id))


@interviews_bp.post("/<int:session_id>/start")
@login_required
def start(session_id):
    session = owned_session(session_id)
    if session.status == "completed":
        return redirect(url_for("interviews.result", session_id=session.id))
    session.status = "in_progress"
    db.session.commit()
    return redirect(url_for("interviews.mock", session_id=session.id, position=1))


@interviews_bp.route("/<int:session_id>/mock", methods=["GET", "POST"])
@login_required
def mock(session_id):
    session = owned_session(session_id)
    if session.status == "completed":
        return redirect(url_for("interviews.result", session_id=session.id))
    position = request.values.get("position", 1, type=int)
    question = next((item for item in session.questions if item.position == position), None)
    if not question:
        score_session(session)
        db.session.commit()
        return redirect(url_for("interviews.result", session_id=session.id))
    if request.method == "POST":
        answer = request.form.get("answer", "")
        evaluation = evaluate_question(question, answer)
        question.answer = answer
        question.score = evaluation["score"]
        question.feedback = evaluation["feedback"]
        question.strengths = evaluation.get("strengths", [])
        question.improvements = evaluation.get("improvements", [])
        question.suggested_answer = evaluation["suggested_answer"]
        question.answered_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("interviews.mock", session_id=session.id, position=position + 1))
    return render_template("interviews/mock.html", session=session, question=question, position=position, total=len(session.questions))


@interviews_bp.get("/<int:session_id>/result")
@login_required
def result(session_id):
    session = owned_session(session_id)
    if session.status != "completed":
        flash("Complete the mock interview to view its final report.", "warning")
        return redirect(url_for("interviews.prep", session_id=session.id))
    return render_template("interviews/result.html", session=session)


@interviews_bp.get("/<int:session_id>/report.pdf")
@login_required
def report(session_id):
    session = owned_session(session_id)
    if session.status != "completed":
        abort(404)
    return send_file(interview_report(current_user, session), mimetype="application/pdf", as_attachment=True,
                     download_name=f"mock-interview-{session.id}.pdf")
