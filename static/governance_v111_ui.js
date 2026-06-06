async function loadV111RecoveryUxSummary() {
  const data = await api("/api/release-governance/v11-1-recovery-ux-summary?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.1 Recovery UX"));
}

async function loadV111ExportFixtureExample() {
  const data = await api("/api/release-governance/v11-1-export-fixture-example?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.1 Export Fixture"));
}

async function loadV111ImportFixtureExample() {
  const fixture = await api("/api/release-governance/v11-1-export-fixture-example?profile_id=core-risk");
  const data = await api("/api/release-governance/v11-1-import-fixture-example?profile_id=core-risk", { method: "POST", body: JSON.stringify(fixture.fixture_payload) });
  showRich("readiness", renderGenericGovernanceCard(data, "v11.1 Import Fixture"));
}

async function loadV111OperatorFixturePackage() {
  const data = await api("/api/release-governance/v11-1-operator-fixture-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.1 Fixture Package"));
}
