# v6.1 Verification

## Commands run

```bash
python scripts/quality_check.py
python -m compileall app tests
pytest -q
python scripts/security_check.py
python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
reset = client.post('/api/demo/reset')
assert reset.status_code == 200
login = client.post('/api/auth/login', json={'email':'admin@example.com','password':'password123'})
assert login.status_code == 200
headers={'Authorization': f"Bearer {login.json()['access_token']}"}
req = client.post('/api/projects/1/requirements', json={'key':'REQ-SMOKE-61','title':'Smoke requirement','priority':'High','status':'Open'}, headers=headers)
assert req.status_code == 200
wi=client.post('/api/projects/1/work-items', json={'kind':'task','title':'Smoke linked task','requirement_id':req.json()['id']}, headers=headers)
assert wi.status_code == 200
patch=client.patch(f"/api/work-items/{wi.json()['id']}", json={'title':'Smoke relink title','requirement_id': None}, headers=headers)
assert patch.status_code == 200
trace=client.get('/api/projects/1/traceability', headers=headers)
assert trace.status_code == 200
print('HTTP smoke: PASS')
PY
```

## Results

```text
quality_check: PASS
compileall: PASS
pytest: 42 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

## Security check note

`security_check` reports local auth mode and keeps the existing JWT-secret warning wording. This is the same local-development warning pattern from the previous version, not a new v6.1 regression.
