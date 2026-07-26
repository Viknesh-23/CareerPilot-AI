from pathlib import Path
from uuid import uuid4

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import select
from werkzeug.utils import secure_filename

from extensions import db
from models.resume import Resume
from services.resume_parser import ResumeParseError, extract_pdf_text

resumes_bp = Blueprint("resumes", __name__, url_prefix="/resumes")


def owned_resume(resume_id):
    resume = db.session.get(Resume, resume_id)
    if not resume or resume.user_id != current_user.id:
        abort(404)
    return resume


@resumes_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        upload = request.files.get("resume")
        display_name = request.form.get("name", "").strip()
        if not upload or not upload.filename:
            flash("Select a PDF resume to upload.", "danger")
        else:
            original = secure_filename(upload.filename)
            if not original.lower().endswith(".pdf") or upload.mimetype not in ("application/pdf", "application/x-pdf", "application/octet-stream"):
                flash("Only PDF resumes are allowed.", "danger")
            else:
                payload = upload.read()
                if not payload.startswith(b"%PDF-"):
                    flash("The selected file is not a valid PDF.", "danger")
                else:
                    filename = f"{current_user.id}_{uuid4().hex}_{original}"
                    path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
                    path.write_bytes(payload)
                    try:
                        text = extract_pdf_text(path)
                    except ResumeParseError as exc:
                        path.unlink(missing_ok=True)
                        flash(str(exc), "danger")
                    else:
                        db.session.add(Resume(user_id=current_user.id, name=display_name or Path(original).stem, filename=original,
                                              stored_path=str(path), extracted_text=text))
                        db.session.commit()
                        flash("Resume uploaded and text extracted.", "success")
                        return redirect(url_for("resumes.index"))
    resumes = db.session.scalars(select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())).all()
    return render_template("resumes/index.html", resumes=resumes)


@resumes_bp.get("/<int:resume_id>/download")
@login_required
def download(resume_id):
    resume = owned_resume(resume_id)
    path = Path(resume.stored_path)
    if not path.is_file():
        flash("The resume file is no longer available.", "warning")
        return redirect(url_for("resumes.index"))
    return send_file(path, as_attachment=True, download_name=resume.filename)


@resumes_bp.post("/<int:resume_id>/delete")
@login_required
def delete(resume_id):
    resume = owned_resume(resume_id)
    path = Path(resume.stored_path)
    db.session.delete(resume)
    db.session.commit()
    path.unlink(missing_ok=True)
    flash("Resume deleted.", "info")
    return redirect(url_for("resumes.index"))
