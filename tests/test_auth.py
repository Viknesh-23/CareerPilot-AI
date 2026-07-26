from tests.conftest import register


def test_registration_login_logout(client):
    response = register(client)
    assert response.status_code == 200
    assert b"Career profile" in response.data
    response = client.post("/auth/logout", follow_redirects=True)
    assert b"Sign in" in response.data
    response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=True)
    assert b"Career command center" in response.data


def test_duplicate_email(client):
    register(client)
    client.post("/auth/logout")
    response = register(client)
    assert b"already exists" in response.data


def test_protected_route(client):
    response = client.get("/applications/", follow_redirects=False)
    assert response.status_code == 302
