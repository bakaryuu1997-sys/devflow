# v4.2 Verification

## pip install

Exit code:

```text
1
```

Output tail:

```text

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
[31mERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'[0m[31m
[0m
```

## compileall

Exit code:

```text
0
```

## targeted pytest

Command:

```bash
python -m pytest -q tests/test_v42_goal_completion.py
```

Exit code:

```text
2
```

Output tail:

```text

==================================== ERRORS ====================================
[31m[1m______________ ERROR collecting tests/test_v42_goal_completion.py ______________[0m
[31mImportError while importing test module '/mnt/data/devflow_guard_v4_2_goal_completion/tests/test_v42_goal_completion.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
[1m[31m/usr/lib/python3.13/importlib/__init__.py[0m:88: in import_module
    [0m[94mreturn[39;49;00m _bootstrap._gcd_import(name[level:], package, level)[90m[39;49;00m
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mtests/test_v42_goal_completion.py[0m:1: in <module>
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96msqlalchemy[39;49;00m[90m [39;49;00m[94mimport[39;49;00m create_engine[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'sqlalchemy'[0m[0m
[36m[1m=========================== short test summary info ============================[0m
[31mERROR[0m tests/test_v42_goal_completion.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
[31m[31m[1m1 error[0m[31m in 0.20s[0m[0m

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

## Full local verification

```bash
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```
