async function loadV118SignedArchiveChecksumHandoff() {
  const data = await api("/api/release-governance/v11-8-signed-archive-checksum-handoff?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.8 Checksum Handoff"));
}

async function loadV118FinalUserFacingQuickstart() {
  const data = await api("/api/release-governance/v11-8-final-user-facing-quickstart?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.8 Quickstart"));
}

async function loadV118OperatorChecksumQuickstartPackage() {
  const data = await api("/api/release-governance/v11-8-operator-checksum-quickstart-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.8 Checksum Package"));
}
