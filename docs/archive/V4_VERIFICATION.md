# v4 Verification

## compileall

Exit code:

```text
0
```

Output tail:

```text
Listing 'app'...
Compiling 'app/advanced_readiness_service.py'...
Compiling 'app/auth_service.py'...
Compiling 'app/bug_pattern_service.py'...
Compiling 'app/code_risk_service.py'...
Compiling 'app/config.py'...
Compiling 'app/database.py'...
Compiling 'app/deps.py'...
Compiling 'app/env_guard_service.py'...
Compiling 'app/impact_service.py'...
Compiling 'app/main.py'...
Compiling 'app/models.py'...
Compiling 'app/os_service.py'...
Compiling 'app/rbac.py'...
Compiling 'app/routes.py'...
Compiling 'app/routes_auth.py'...
Compiling 'app/routes_core.py'...
Compiling 'app/routes_v4.py'...
Compiling 'app/rules.py'...
Compiling 'app/schemas.py'...
Compiling 'app/security.py'...
Compiling 'app/seed.py'...
Compiling 'app/services.py'...
Compiling 'app/traceability_service.py'...

Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/generated/interface/models.py", line 48821, in hydrate_crdt_from_proto
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/rpc/remote.py", line 747, in __call__
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.

```

## pytest note

Targeted v4 tests were added:

```text
tests/test_v4_traceability_impact.py
tests/test_v4_api.py
```

In this current execution runtime, pytest cannot complete because the environment is missing SQLAlchemy. Run locally:

```bash
pip install -r requirements.txt
pytest tests/test_v4_traceability_impact.py tests/test_v4_api.py
```

## Backend package repair

This package includes restored backend core files:

```text
app/main.py
app/database.py
app/deps.py
app/security.py
app/rbac.py
app/services.py
app/os_service.py
app/rules.py
```
