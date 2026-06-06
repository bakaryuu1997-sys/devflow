async function loadV116FinalPackagingCleanup() {
  const data = await api("/api/release-governance/v11-6-final-packaging-cleanup?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.6 Packaging Cleanup"));
}

async function loadV116BeginnerInstallVerification() {
  const data = await api("/api/release-governance/v11-6-beginner-install-verification?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.6 Install Verification"));
}

async function loadV116OperatorFinalPackage() {
  const data = await api("/api/release-governance/v11-6-operator-final-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.6 Final Package"));
}
