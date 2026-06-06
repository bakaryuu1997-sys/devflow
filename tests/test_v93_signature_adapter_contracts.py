from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app
from app.signature_adapter_fixtures import load_fixture_rows

client = TestClient(app)


def test_v93_signature_adapter_contract_tests_endpoint():
    data = client.get("/api/release-governance/signature-adapter-contract-tests").json()
    assert data["version"] == "9.3"
    assert data["mode"] == "signature-adapter-contract-tests"
    assert data["passed"] is True
    assert "evidence_hash" in data["required_result_fields"]
    assert {case["adapter"] for case in data["cases"]} >= {"pgp-stub", "x509-cms-stub", "rfc3161-tsa-stub"}
    assert "Signature Adapter Contract Tests" in data["content"]


def test_v93_sample_signature_fixtures_endpoint_has_no_private_keys():
    data = client.get("/api/release-governance/sample-signature-fixtures").json()
    assert data["version"] == "9.3"
    assert data["mode"] == "sample-signature-fixtures"
    assert data["fixture_count"] == 3
    assert not data["blockers"]
    assert all(not row["contains_private_key"] for row in data["fixtures"])
    assert all(len(row["sha256"]) == 64 for row in data["fixtures"])


def test_v93_fixture_files_are_public_sample_only():
    rows = load_fixture_rows()
    assert len(rows) == 3
    for row in rows:
        assert row["exists"] is True
        assert row["size_bytes"] > 20
        assert row["contains_private_key"] is False


def test_v93_static_ui_and_routes_are_wired():
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = Path("app/routes.py").read_text(encoding="utf-8")
    ui_js = Path("static/signature_contract_ui.js").read_text(encoding="utf-8")
    assert "Adapter Contracts" in index_html
    assert "Sample Fixtures" in index_html
    assert "signature_contract_ui.js" in index_html
    assert "routes_v93" in routes_py
    assert "signature-adapter-contract-tests" in ui_js


def test_v93_cli_exports(tmp_path):
    contract_out = tmp_path / "SIGNATURE_ADAPTER_CONTRACT_TESTS.md"
    fixture_out = tmp_path / "SAMPLE_SIGNATURE_FIXTURES.md"
    contract = subprocess.run([sys.executable, "scripts/export_signature_adapter_contract_tests.py", str(contract_out)], text=True, capture_output=True, check=False)
    fixtures = subprocess.run([sys.executable, "scripts/export_sample_signature_fixtures.py", str(fixture_out)], text=True, capture_output=True, check=False)
    assert contract.returncode == 0, contract.stdout + contract.stderr
    assert fixtures.returncode == 0, fixtures.stdout + fixtures.stderr
    assert "Signature Adapter Contract Tests" in contract_out.read_text(encoding="utf-8")
    assert "Sample Signature Fixtures" in fixture_out.read_text(encoding="utf-8")
