from __future__ import annotations


def v10_1_usability_walkthrough() -> dict:
    steps = _walkthrough_steps()
    data = {
        "version": "10.1",
        "mode": "usability-walkthrough",
        "status": "Ready",
        "ready": True,
        "target_user": "local operator or developer demoing DevFlow Guard",
        "steps": steps,
        "success_criteria": _success_criteria(),
    }
    data["content"] = _walkthrough_markdown(data)
    return data


def v10_1_sample_demo_script() -> dict:
    data = {
        "version": "10.1",
        "mode": "sample-demo-script",
        "status": "Ready",
        "ready": True,
        "script_sections": _demo_sections(),
        "speaker_notes": _speaker_notes(),
    }
    data["content"] = _demo_markdown(data)
    return data


def v10_1_optional_deployment_guide() -> dict:
    data = {
        "version": "10.1",
        "mode": "optional-local-deployment-guide",
        "status": "Ready",
        "ready": True,
        "deployment_modes": _deployment_modes(),
        "operator_checks": _operator_checks(),
        "not_included": [
            "No cloud hosting automation.",
            "No private-key storage.",
            "No production DB migration without the v8.5 approval phrase.",
        ],
    }
    data["content"] = _deployment_markdown(data)
    return data


def v10_1_operator_quickstart_package() -> dict:
    walkthrough = v10_1_usability_walkthrough()
    demo = v10_1_sample_demo_script()
    deployment = v10_1_optional_deployment_guide()
    data = {
        "version": "10.1",
        "mode": "operator-quickstart-package",
        "status": "Ready",
        "ready": True,
        "included_exports": [walkthrough["mode"], demo["mode"], deployment["mode"]],
    }
    data["content"] = "# v10.1 Operator Quickstart Package\n\n" + "\n\n".join([walkthrough["content"], demo["content"], deployment["content"]])
    return data


def _walkthrough_steps() -> list[dict]:
    return [
        {"step": 1, "name": "Start demo", "action": "Open the UI, reset demo data, and confirm login status."},
        {"step": 2, "name": "Check release risk", "action": "Run traceability, risk dashboard, and done gates."},
        {"step": 3, "name": "Review prevention", "action": "Open prevention board, readiness timeline, and plan recommendation."},
        {"step": 4, "name": "Review governance", "action": "Open evidence manifest, verified gate, final bundle, and rehearsal report."},
        {"step": 5, "name": "Prepare handoff", "action": "Export operator handoff, runbook, final evidence bundle, and v10 package."},
    ]


def _success_criteria() -> list[str]:
    return [
        "A new operator can find the next action without reading source code.",
        "Every governance export has a matching UI entry point.",
        "The migration gate remains human-approved and blocked by default.",
        "Private keys are never requested or stored by the app.",
    ]


def _demo_sections() -> list[dict]:
    return [
        {"title": "Problem", "talk_track": "Requirements, work items, risks, and release evidence drift apart."},
        {"title": "Traceability", "talk_track": "DevFlow Guard links Requirement to WorkItem to risk signals."},
        {"title": "Prevention", "talk_track": "Recurring risks become prevention items with owners, due dates, and readiness views."},
        {"title": "Governance", "talk_track": "Approval evidence is frozen, hashed, verified, and exported as an operator package."},
        {"title": "Safety", "talk_track": "Production migration is copy-tested first and requires explicit human approval."},
    ]


def _speaker_notes() -> list[str]:
    return [
        "Keep the demo deterministic; do not promise AI-based judgment.",
        "Call out that v10.1 is local-first and dependency-light.",
        "Say clearly that cryptographic private keys stay outside the app.",
    ]


def _deployment_modes() -> list[dict]:
    return [
        {"mode": "local-dev", "command": "uvicorn app.main:app --reload", "use_case": "daily development and demos"},
        {"mode": "local-operator", "command": "uvicorn app.main:app --host 127.0.0.1 --port 8000", "use_case": "single-machine operator review"},
        {"mode": "packaged-handoff", "command": "python scripts/export_v10_1_operator_quickstart.py V10_1_OPERATOR_QUICKSTART.md", "use_case": "handoff document export"},
    ]


def _operator_checks() -> list[str]:
    return [
        "Run quality_check before packaging.",
        "Run migration_check against any existing SQLite database.",
        "Run safe-copy migration before real migration.",
        "Run rollback drill and post-migration verify.",
        "Export the final signed evidence bundle before handoff.",
    ]


def _walkthrough_markdown(data: dict) -> str:
    lines = ["# v10.1 Usability Walkthrough", "", f"Status: {data['status']}", "", "## Steps"]
    lines.extend(f"{row['step']}. **{row['name']}** — {row['action']}" for row in data["steps"])
    lines.extend(["", "## Success criteria", *[f"- [ ] {item}" for item in data["success_criteria"]]])
    return "\n".join(lines).strip() + "\n"


def _demo_markdown(data: dict) -> str:
    lines = ["# v10.1 Sample Demo Script", "", f"Status: {data['status']}", "", "## Talk track"]
    lines.extend(f"### {row['title']}\n{row['talk_track']}" for row in data["script_sections"])
    lines.extend(["", "## Speaker notes", *[f"- {item}" for item in data["speaker_notes"]]])
    return "\n".join(lines).strip() + "\n"


def _deployment_markdown(data: dict) -> str:
    lines = ["# v10.1 Optional Local Deployment Guide", "", f"Status: {data['status']}", "", "## Deployment modes"]
    lines.extend(f"- **{row['mode']}**: `{row['command']}` — {row['use_case']}" for row in data["deployment_modes"])
    lines.extend(["", "## Operator checks", *[f"- [ ] {item}" for item in data["operator_checks"]]])
    lines.extend(["", "## Not included", *[f"- {item}" for item in data["not_included"]]])
    return "\n".join(lines).strip() + "\n"
