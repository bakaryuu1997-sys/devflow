"""Local data-management endpoints: stats, backup, reset (local-only)."""

from fastapi.testclient import TestClient

from app import auth_mode
from app.main import app

client = TestClient(app)


def test_local_stats_reports_table_counts():
    data = client.get("/api/local/stats").json()
    assert "total_rows" in data
    assert isinstance(data["tables"], dict)
    assert "users" in data["tables"]


def test_local_backup_downloads_sqlite_file():
    response = client.get("/api/local/backup")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
    assert response.headers["content-disposition"].endswith('.db"')


def test_local_endpoints_blocked_in_production(monkeypatch):
    monkeypatch.setattr(auth_mode.settings, "environment", "production")
    assert client.get("/api/local/stats").status_code == 403
    assert client.get("/api/local/backup").status_code == 403
    # reset-all is an unsafe method, blocked by auth before the local guard.
    assert client.post("/api/local/reset-all").status_code in (401, 403)


def test_local_reset_all_clears_data_and_reseeds_admin():
    # Seed some data first.
    client.post("/api/demo/reset")
    before = client.get("/api/local/stats").json()["total_rows"]
    assert before > 0

    result = client.post("/api/local/reset-all").json()
    assert result["status"] == "reset"

    # Admin still exists (re-seeded), so login works.
    login = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    assert login.status_code == 200
