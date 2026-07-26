from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _pdf(title, sections):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, title=title)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for heading, value in sections:
        story.append(Paragraph(f"<b>{heading}</b>", styles["Heading3"]))
        story.append(Paragraph(str(value).replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 8))
    doc.build(story)
    output.seek(0)
    return output


def ats_report(user, analysis):
    app = analysis.application
    return _pdf("CareerPilot AI — ATS Analysis", [
        ("User", user.full_name), ("Company", app.company_name), ("Role", app.job_role),
        ("ATS Score", f"{analysis.score}%"), ("Matched Skills", ", ".join(analysis.matched_skills) or "None"),
        ("Missing Skills", ", ".join(analysis.missing_skills) or "None"),
        ("Suggestions", "<br/>".join(f"• {item}" for item in analysis.suggestions)),
        ("Generated", analysis.created_at.strftime("%d %b %Y")),
    ])


def interview_report(user, session):
    app = session.application
    strengths = [item for question in session.questions for item in (question.strengths or [])]
    improvements = [item for question in session.questions for item in (question.improvements or [])]
    return _pdf("CareerPilot AI — Mock Interview Report", [
        ("User", user.full_name), ("Company", app.company_name), ("Role", app.job_role),
        ("Overall Score", f"{session.overall_score or 0}%"),
        ("Category Scores", f"Technical: {session.technical_score or 0}% | HR: {session.hr_score or 0}% | Behavioral: {session.behavioral_score or 0}% | JD Specific: {session.jd_score or 0}%"),
        ("Strengths", "<br/>".join(f"• {item}" for item in dict.fromkeys(strengths)) or "Continue practising concise examples."),
        ("Recommended Topics", "<br/>".join(f"• {item}" for item in dict.fromkeys(improvements)) or "Keep rehearsing answers aloud."),
        ("Generated", datetime_now()),
    ])


def datetime_now():
    from datetime import datetime
    return datetime.utcnow().strftime("%d %b %Y")
