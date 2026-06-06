from __future__ import annotations

SAMPLE_PROFILE_SEEDS = {
    "core-risk": {
        "project": ("Payroll Guided Sample", "High-risk login release for guided demo."),
        "release": "1.0.0-guided",
        "requirements": [
            ("REQ-PAY-001", "Login by email with audit trail", "Critical", "Open"),
        ],
        "work_items": [
            ("task", "Build login API", "Done", "High", "REQ-PAY-001"),
            ("bug", "Fix login 500 on invalid token", "Open", "Critical", "REQ-PAY-001"),
        ],
        "links": [
            ("api", "POST /api/auth/login", "Login API", "Changed", "REQ-PAY-001"),
            ("test", "TC-LOGIN-REGRESSION", "Login regression test", "Needs Update", "REQ-PAY-001"),
        ],
    },
    "clean-release": {
        "project": ("Clean Release Guided Sample", "Low-risk release with completed checks."),
        "release": "2.0.0-guided",
        "requirements": [
            ("REQ-CLN-001", "Export release notes", "Medium", "Done"),
            ("REQ-CLN-002", "Show approval status", "High", "Done"),
        ],
        "work_items": [
            ("task", "Implement release notes export", "Done", "Medium", "REQ-CLN-001"),
            ("test", "Verify approval status display", "Done", "Medium", "REQ-CLN-002"),
        ],
        "links": [("test", "TC-CLEAN-001", "Happy path release test", "Done", "REQ-CLN-001")],
    },
    "governance-heavy": {
        "project": ("Governance Guided Sample", "Evidence-heavy release governance rehearsal."),
        "release": "3.0.0-guided",
        "requirements": [
            ("REQ-GOV-001", "Attach verifier evidence", "Critical", "In Progress"),
            ("REQ-GOV-002", "Export final signed bundle", "High", "Open"),
            ("REQ-GOV-003", "Record operator approval", "High", "Open"),
        ],
        "work_items": [
            ("task", "Run public verifier dry-run", "Done", "High", "REQ-GOV-001"),
            ("task", "Review evidence manifest", "In Progress", "High", "REQ-GOV-002"),
            ("bug", "Missing operator note", "Open", "High", "REQ-GOV-003"),
        ],
        "links": [("commit", "gov123", "Evidence bundle rehearsal commit", "Merged", "REQ-GOV-002")],
    },
}

BUILDER_STEPS = [
    "Select a profile and preview its seeded project shape.",
    "Create requirements before work items so traceability can link safely.",
    "Create a release record for dashboard and readiness flows.",
    "Add trace links that make the sample useful in the guided tour.",
    "Mark tutorial builder step as done and show the completion badge.",
]
