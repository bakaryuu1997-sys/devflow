from hashlib import sha256
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.database import get_db
from app.models import ActivityLog

client = TestClient(app)

def test_ledger_verification_workflow():
    # 1. Reset the demo database
    client.post("/api/demo/reset")
    
    # Obtain db session to insert activity logs
    db = next(get_db())
    
    # Clear existing logs to start fresh
    db.query(ActivityLog).delete()
    db.commit()
    
    # 2. Add some consistent logs
    log1 = ActivityLog(action="auth_success", message="User admin logged in", project_id=1)
    db.add(log1)
    db.commit()
    db.refresh(log1)
    
    log2 = ActivityLog(action="signoff", message="Approved release 1.0.0", project_id=1)
    db.add(log2)
    db.commit()
    db.refresh(log2)
    
    # Verify the chains are filled
    assert log1.previous_hash == "0" * 64
    assert log1.current_hash != ""
    assert log2.previous_hash == log1.current_hash
    
    # 3. Query verify endpoint
    response = client.get("/api/governance/verify-ledger")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "verified"
    assert data["count"] == 2
    
    # 4. Tamper with the ledger: modify log1 message in the database directly
    log1.message = "User admin logged in (TAMPERED)"
    db.commit()
    
    # 5. Query verify endpoint again - should detect data tampering
    response = client.get("/api/governance/verify-ledger")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "tampered"
    assert "mismatch" in data["reason"].lower() or "broken" in data["reason"].lower()
    
    # Restore log1 message, but break the previous_hash link of log2
    log1.message = "User admin logged in"
    log2.previous_hash = "invalid_hash" * 5
    db.commit()
    
    # Query verify endpoint again - should detect broken chain
    response = client.get("/api/governance/verify-ledger")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "tampered"
    assert "broken" in data["reason"].lower() or "mismatch" in data["reason"].lower()
