async function loadV113RecoverySmokeTestAutomation() {
  const data = await api("/api/release-governance/v11-3-recovery-smoke-test-automation?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.3 Recovery Smoke Test"));
}

async function loadV113PostRestoreVerificationReport() {
  const fixture = await api("/api/release-governance/v11-1-export-fixture-example?profile_id=core-risk");
  const data = await api("/api/release-governance/v11-3-post-restore-verification-report?profile_id=core-risk", { method: "POST", body: JSON.stringify(fixture.fixture_payload.snapshot_export) });
  showRich("readiness", renderGenericGovernanceCard(data, "v11.3 Post-Restore Verify"));
}

async function loadV113OperatorSmokeVerificationPackage() {
  const data = await api("/api/release-governance/v11-3-operator-smoke-verification-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.3 Smoke Verify Package"));
}
