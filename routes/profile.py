from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        for field in ("full_name", "college", "degree", "skills", "preferred_role", "preferred_location", "github_url", "linkedin_url"):
            setattr(current_user, field, request.form.get(field, "").strip())
        year = request.form.get("graduation_year", "").strip()
        try:
            current_user.graduation_year = int(year) if year else None
        except ValueError:
            flash("Graduation year must be a number.", "danger")
            return render_template("profile/index.html")
        if not current_user.full_name:
            flash("Full name is required.", "danger")
        else:
            db.session.commit()
            flash("Profile saved.", "success")
            return redirect(url_for("profile.index"))
    return render_template("profile/index.html", current_year=datetime.utcnow().year)
