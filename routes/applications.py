import csv
from datetime import date, datetime
from io import StringIO

from flask import Blueprint, Response, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, select

from extensions import db
from models.application import ApplicationActivity, JobApplication
from models.interview import InterviewEvent
from models.resume import Resume

applications_bp = Blueprint("applications", __name__, url_prefix="/applications")
STATUSES = ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected", "Withdrawn"]
KANBAN_STATUSES = ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected"]
WORK_MODES = ["On-site", "Hybrid", "Remote"]


def owned_application(application_id):
    application = db.session.get(JobApplication, application_id)
    if not application or application.user_id != current_user.id:
        abort(404)
    return application


def parse_application_form(application=None):
    fields = ("company_name", "job_role", "job_description", "job_url", "location", "work_mode", "salary_ctc", "source", "notes")
    values = {field: request.form.get(field, "").strip() for field in fields}
    if not values["company_name"] or not values["job_role"]:
        return None, "Company and job role are required."
    if values["work_mode"] not in WORK_MODES:
        values["work_mode"] = "On-site"
    status = request.form.get("status", "Saved")
    values["status"] = status if status in STATUSES else "Saved"
    resume_id = request.form.get("resume_id", type=int)
    if resume_id:
        resume = db.session.get(Resume, resume_id)
        if not resume or resume.user_id != current_user.id:
            return None, "Selected resume was not found."
    values["resume_id"] = resume_id
    raw_date = request.form.get("application_date", "")
    try:
        values["application_date"] = date.fromisoformat(raw_date) if raw_date else None
    except ValueError:
        return None, "Application date is invalid."
    return values, None


def log_status(application, old_status, message=None):
    db.session.add(ApplicationActivity(
        application_id=application.id, user_id=current_user.id, old_status=old_status or "",
        new_status=application.status, message=message or f"Status changed to {application.status}",
    ))


@applications_bp.get("/")
@login_required
def list_applications():
    stmt = select(JobApplication).where(JobApplication.user_id == current_user.id)
    search = request.args.get("search", "").strip()
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(or_(JobApplication.company_name.ilike(pattern), JobApplication.job_role.ilike(pattern)))
    for field in ("status", "location"):
        value = request.args.get(field, "").strip()
        if value:
            stmt = stmt.where(getattr(JobApplication, field) == value)
    date_from = request.args.get("date_from", "")
    if date_from:
        try:
            stmt = stmt.where(JobApplication.application_date >= date.fromisoformat(date_from))
        except ValueError:
            pass
    sort = request.args.get("sort", "updated")
    order_map = {"company": JobApplication.company_name.asc(), "role": JobApplication.job_role.asc(), "date": JobApplication.application_date.desc(), "updated": JobApplication.updated_at.desc()}
    applications = db.session.scalars(stmt.order_by(order_map.get(sort, order_map["updated"]))).all()
    locations = db.session.scalars(select(JobApplication.location).where(JobApplication.user_id == current_user.id).distinct()).all()
    return render_template("applications/list.html", applications=applications, statuses=STATUSES, locations=locations)


@applications_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_application():
    resumes = db.session.scalars(select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())).all()
    if request.method == "POST":
        values, error = parse_application_form()
        if error:
            flash(error, "danger")
        else:
            application = JobApplication(user_id=current_user.id, **values)
            db.session.add(application)
            db.session.flush()
            log_status(application, "", "Application created")
            db.session.commit()
            flash("Application created.", "success")
            return redirect(url_for("applications.detail", application_id=application.id))
    return render_template("applications/form.html", application=None, resumes=resumes, statuses=STATUSES, work_modes=WORK_MODES)


@applications_bp.route("/<int:application_id>/edit", methods=["GET", "POST"])
@login_required
def edit_application(application_id):
    application = owned_application(application_id)
    resumes = db.session.scalars(select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())).all()
    if request.method == "POST":
        values, error = parse_application_form(application)
        if error:
            flash(error, "danger")
        else:
            old_status = application.status
            for field, value in values.items():
                setattr(application, field, value)
            if application.status != old_status:
                log_status(application, old_status)
            db.session.commit()
            flash("Application updated.", "success")
            return redirect(url_for("applications.detail", application_id=application.id))
    return render_template("applications/form.html", application=application, resumes=resumes, statuses=STATUSES, work_modes=WORK_MODES)


@applications_bp.get("/<int:application_id>")
@login_required
def detail(application_id):
    application = owned_application(application_id)
    return render_template("applications/detail.html", application=application, event_types=["Assessment", "Technical Interview", "HR Interview", "Managerial Interview", "Other"])


@applications_bp.post("/<int:application_id>/delete")
@login_required
def delete_application(application_id):
    application = owned_application(application_id)
    db.session.delete(application)
    db.session.commit()
    flash("Application deleted.", "info")
    return redirect(url_for("applications.list_applications"))


@applications_bp.post("/<int:application_id>/status")
@login_required
def update_status(application_id):
    application = owned_application(application_id)
    status = request.form.get("status", "")
    if status not in STATUSES:
        if request.accept_mimetypes.best == "application/json":
            return jsonify(error="Invalid status"), 400
        flash("Invalid status.", "danger")
        return redirect(url_for("applications.detail", application_id=application.id))
    old_status = application.status
    if old_status != status:
        application.status = status
        log_status(application, old_status)
        db.session.commit()
    if request.accept_mimetypes.best == "application/json":
        return jsonify(ok=True, status=application.status)
    flash("Status updated.", "success")
    return redirect(request.referrer or url_for("applications.detail", application_id=application.id))


@applications_bp.get("/kanban")
@login_required
def kanban():
    records = db.session.scalars(select(JobApplication).where(JobApplication.user_id == current_user.id).order_by(JobApplication.updated_at.desc())).all()
    columns = {status: [app for app in records if app.status == status] for status in KANBAN_STATUSES}
    return render_template("applications/kanban.html", columns=columns, statuses=KANBAN_STATUSES)


@applications_bp.post("/<int:application_id>/events")
@login_required
def create_event(application_id):
    application = owned_application(application_id)
    raw_datetime = request.form.get("scheduled_at", "")
    try:
        scheduled_at = datetime.fromisoformat(raw_datetime)
    except ValueError:
        flash("Provide a valid interview date and time.", "danger")
        return redirect(url_for("applications.detail", application_id=application.id))
    event_type = request.form.get("event_type", "Other")
    if event_type not in ["Assessment", "Technical Interview", "HR Interview", "Managerial Interview", "Other"]:
        event_type = "Other"
    db.session.add(InterviewEvent(user_id=current_user.id, application_id=application.id, event_type=event_type,
                                   round_name=request.form.get("round_name", "Interview round").strip() or "Interview round",
                                   scheduled_at=scheduled_at, meeting_url=request.form.get("meeting_url", "").strip(), notes=request.form.get("notes", "").strip()))
    db.session.commit()
    flash("Interview event scheduled.", "success")
    return redirect(url_for("applications.detail", application_id=application.id))


@applications_bp.get("/export/csv")
@login_required
def export_csv():
    applications = db.session.scalars(select(JobApplication).where(JobApplication.user_id == current_user.id).order_by(JobApplication.created_at.desc())).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Company", "Role", "Status", "Location", "Work Mode", "Salary/CTC", "Application Date", "Source", "Created Date"])
    for app in applications:
        writer.writerow([app.company_name, app.job_role, app.status, app.location, app.work_mode, app.salary_ctc,
                         app.application_date.isoformat() if app.application_date else "", app.source, app.created_at.isoformat()])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=careerpilot-applications.csv"})
