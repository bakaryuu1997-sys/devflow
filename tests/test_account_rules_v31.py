from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_password_min_8():
    client.post("/api/demo/reset")
    response = client.post("/api/auth/register", json={"email": "short@example.com", "password": "123"})

    assert response.status_code == 422


def test_register_duplicate_email_rejected():
    client.post("/api/demo/reset")

    first = client.post("/api/auth/register", json={"email": "new@example.com", "password": "password123"})
    second = client.post("/api/auth/register", json={"email": "NEW@example.com", "password": "password123"})

    assert first.status_code == 200
    assert second.status_code == 409


def test_demo_admin_login_uses_long_password():
    client.post("/api/demo/reset")

    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})

    assert response.status_code == 200
    assert response.json()["access_token"]
