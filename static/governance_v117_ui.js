async function loadV117ArchiveIntegrityManifest() {
  const data = await api("/api/release-governance/v11-7-archive-integrity-manifest?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.7 Archive Manifest"));
}

async function loadV117ReleaseNotesPolish() {
  const data = await api("/api/release-governance/v11-7-release-notes-polish?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.7 Release Notes"));
}

async function loadV117OperatorReleasePackage() {
  const data = await api("/api/release-governance/v11-7-operator-release-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.7 Release Package"));
}
