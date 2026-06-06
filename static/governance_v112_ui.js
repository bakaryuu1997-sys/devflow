async function loadV112FixtureValidationReport() {
  const fixture = await api("/api/release-governance/v11-1-export-fixture-example?profile_id=core-risk");
  const data = await api("/api/release-governance/v11-2-fixture-validation-report?profile_id=core-risk", { method: "POST", body: JSON.stringify(fixture.fixture_payload) });
  showRich("readiness", renderGenericGovernanceCard(data, "v11.2 Fixture Validation"));
}

async function loadV112SampleOperatorWalkthrough() {
  const data = await api("/api/release-governance/v11-2-sample-operator-walkthrough?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.2 Operator Walkthrough"));
}

async function loadV112OperatorWalkthroughPackage() {
  const data = await api("/api/release-governance/v11-2-operator-walkthrough-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.2 Walkthrough Package"));
}
