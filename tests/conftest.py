import pytest

from app import create_app
from extensions import db


@pytest.fixture()
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        "SECRET_KEY": "test-secret",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, email="test@example.com", password="password123", full_name="Test User"):
    return client.post("/auth/register", data={"full_name": full_name, "email": email, "password": password, "confirm_password": password}, follow_redirects=True)


@pytest.fixture()
def logged_in(client):
    register(client)
    return client
