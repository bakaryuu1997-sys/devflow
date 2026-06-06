from __future__ import annotations

DEMO_PROFILES = [
    {
        "profile_id": "core-risk",
        "name": "Core Risk Demo",
        "recommended_for": "first walkthrough and interview demo",
        "requirements": 1,
        "work_items": 2,
        "risk_level": "High",
        "description": "Small payroll login release with one critical bug and traceability gaps.",
    },
    {
        "profile_id": "clean-release",
        "name": "Clean Release Demo",
        "recommended_for": "showing done gates and sign-off happy path",
        "requirements": 2,
        "work_items": 5,
        "risk_level": "Low",
        "description": "Balanced requirements, completed tests, and no blocking bug signal.",
    },
    {
        "profile_id": "governance-heavy",
        "name": "Governance Heavy Demo",
        "recommended_for": "showing evidence, verifier, migration, and operator handoff flows",
        "requirements": 3,
        "work_items": 8,
        "risk_level": "Medium",
        "description": "Release governance demo with prevention and evidence-review emphasis.",
    },
]

TUTORIAL_STEPS = [
    ("first-run", "Open first-run wizard", "Confirm local mode and reset safety."),
    ("profile", "Choose demo profile", "Pick the right demo profile before resetting data."),
    ("sample-builder", "Build guided sample project", "Create deterministic sample data for the selected profile."),
    ("traceability", "Run traceability", "Review requirement-to-work-item links."),
    ("risk", "Open risk dashboard", "Check blockers and fix hints."),
    ("governance", "Review governance evidence", "Open manifest, verified gate, and final bundle."),
    ("handoff", "Export handoff package", "Export the operator quickstart or governance package."),
]
