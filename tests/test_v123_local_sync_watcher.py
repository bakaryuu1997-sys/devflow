import subprocess
import sys

from scripts.local_sync_watcher import DevFlowWatcher


def test_watcher_help_menu():
    # Test --help menu
    result = subprocess.run([sys.executable, "scripts/local_sync_watcher.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "DevFlow Guard auto-sync directory watcher" in result.stdout
    assert "--url" in result.stdout
    assert "--dir" in result.stdout


def test_watcher_file_handlers(tmp_path):
    # Setup temporary directory structure and files
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    sql_file = migrations_dir / "001_init.sql"
    sql_file.write_text("SELECT 1;", encoding="utf-8")

    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///:memory:", encoding="utf-8")

    log_file = tmp_path / "pytest.log"
    log_file.write_text("All tests passed.", encoding="utf-8")

    # Create a mock watcher instance
    watcher = DevFlowWatcher(
        base_url="http://127.0.0.1:8000",
        email="test@example.com",
        password="password123",
        project_id=1,
        watch_dir=str(tmp_path),
    )

    # We mock send_request to see what urls it hits
    request_logs = []

    def mock_send_request(url, method="GET", data=None, headers=None):
        request_logs.append((url, method, data))
        return "[]", 200

    watcher.send_request = mock_send_request
    watcher.token = "fake_jwt"

    # 1. Handle SQL migrations
    watcher.handle_file_change(str(sql_file), "added")
    assert len(request_logs) == 1
    assert "guards/sql" in request_logs[0][0]

    # Reset logs
    request_logs.clear()

    # 2. Handle Env files
    watcher.handle_file_change(str(env_file), "modified")
    assert len(request_logs) == 1
    assert "env-guard" in request_logs[0][0]

    request_logs.clear()

    # 3. Handle test logs
    watcher.handle_file_change(str(log_file), "modified")
    assert len(request_logs) == 1
    assert "guards/tests" in request_logs[0][0]
