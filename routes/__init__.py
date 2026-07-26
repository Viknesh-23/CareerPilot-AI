def register_blueprints(app):
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.applications import applications_bp
    from routes.resumes import resumes_bp
    from routes.ats import ats_bp
    from routes.interviews import interviews_bp
    from routes.analytics import analytics_bp
    from routes.profile import profile_bp
    for blueprint in (auth_bp, dashboard_bp, applications_bp, resumes_bp,
                      ats_bp, interviews_bp, analytics_bp, profile_bp):
        app.register_blueprint(blueprint)
