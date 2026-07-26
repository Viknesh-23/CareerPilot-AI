from pathlib import Path

import click
from flask import Flask, render_template
from sqlalchemy import text
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from extensions import csrf, db, login_manager, migrate


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from models import user  # noqa: F401 - registers model before metadata use
    from routes import register_blueprints
    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db():
        """Create all tables for a fresh local installation."""
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("check-db")
    def check_db():
        """Verify that the configured database can be reached."""
        db.session.execute(text("SELECT 1"))
        click.echo("Database connection OK.")

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(error):
        return render_template("errors/500.html", message="The uploaded file is too large."), 413

    return app


app = create_app()
