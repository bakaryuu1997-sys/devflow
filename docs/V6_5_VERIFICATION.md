# v6.5 Verification

```text
quality_check: PASS
compileall: PASS
pytest: 56 passed
security_check: PASS with local warning
HTTP smoke: PASS
file-size rule: PASS
```

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
assert client.get('/api/health').status_code == 200
client.post('/api/demo/reset')
login = client.post('/api/auth/login', json={'email': 'admin@example.com', 'password': 'password123'})
assert login.status_code == 200
headers = {'Authorization': 'Bearer ' + login.json()['access_token']}
assert client.get('/api/projects/1/release-risk-dashboard', headers=headers).status_code == 200
assert client.get('/api/projects/1/release-review-checklist', headers=headers).status_code == 200
PY
```

## Warning note

`security_check` still reports the local JWT warning already expected for local/offline mode. It is not introduced by v6.5.
