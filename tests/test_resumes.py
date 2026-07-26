from io import BytesIO

from reportlab.pdfgen import canvas

from extensions import db
from models.resume import Resume


def pdf_bytes():
    buffer = BytesIO(); pdf = canvas.Canvas(buffer); pdf.drawString(72, 720, "Python Flask SQL Docker React"); pdf.save(); buffer.seek(0); return buffer


def test_pdf_resume_upload(app, logged_in):
    response = logged_in.post("/resumes/", data={"name": "Test Resume", "resume": (pdf_bytes(), "resume.pdf")}, content_type="multipart/form-data", follow_redirects=True)
    assert b"text extracted" in response.data
    with app.app_context():
        assert "Python" in Resume.query.one().extracted_text


def test_rejects_non_pdf(logged_in):
    response = logged_in.post("/resumes/", data={"resume": (BytesIO(b"hello"), "resume.txt")}, content_type="multipart/form-data", follow_redirects=True)
    assert b"Only PDF" in response.data
