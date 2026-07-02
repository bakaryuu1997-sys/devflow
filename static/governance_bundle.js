/* AUTO-GENERATED BUNDLE — do not edit directly.
 * Concatenation of the per-version governance UI modules, in load order.
 * Regenerate with scripts/build_governance_bundle.py after editing sources.
 */


// ==== governance_v10_ui.js ====
async function loadVerifiedEvidenceManifestGate() {
  const data = await api("/api/release-governance/verified-evidence-manifest-gate");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Verified Evidence Manifest Gate"));
  toast("Verified evidence gate loaded.");
}
async function loadExternalVerifierProfiles() {
  const data = await api("/api/release-governance/external-verifier-profiles");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "External Verifier Profiles"));
}
async function createDefaultVerifierProfile() {
  const data = await api("/api/release-governance/external-verifier-profiles", { method: "POST", body: JSON.stringify({ name: "ops-ed25519", key_reference: "external-public-key" }) });
  showRich("readiness", debugBlock(data));
}
async function loadOperatorPolicyPresets() {
  const data = await api("/api/release-governance/operator-policy-presets");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Operator Policy Presets"));
}
async function loadFinalSignedEvidenceBundle() {
  const data = await api("/api/release-governance/final-signed-evidence-bundle");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Final Signed Evidence Bundle"));
}
async function createFinalSignedEvidenceBundle() {
  const data = await api("/api/release-governance/final-signed-evidence-bundles", { method: "POST", body: JSON.stringify({}) });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Final Bundle Record"));
}
async function loadEndToEndGovernanceRehearsal() {
  const data = await api("/api/release-governance/end-to-end-governance-rehearsal");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "End-to-End Rehearsal"));
}
async function loadV10StableMilestoneReport() {
  const data = await api("/api/release-governance/v10-stable-milestone-report");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Stable Milestone"));
}
async function loadV10InstallerChecklist() {
  const data = await api("/api/release-governance/v10-installer-checklist");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "Installer Checklist"));
}
function renderGenericGovernanceCard(data, title) {
  const status = data.status || data.mode || title;
  const ready = data.ready === undefined ? true : data.ready;
  return `<div class="readiness-card ${ready ? "success" : "danger"}"><div><span class="readiness-label">${escapeHtml(title)}</span><h3>${escapeHtml(status)}</h3><p>version=${escapeHtml(data.version || "")}</p></div></div>${renderList("Blockers", data.blockers || ["No blockers."])}<div class="action-row compact-actions"><button type="button" class="ghost-btn" onclick="openEvidenceMarkdown()">Open Markdown export</button><button type="button" class="ghost-btn" onclick="createDefaultVerifierProfile()">Create verifier profile</button><button type="button" class="ghost-btn" onclick="createFinalSignedEvidenceBundle()">Create final bundle</button></div>${debugBlock(data)}`;
}

// ==== governance_v101_ui.js ====
async function loadV101UsabilityWalkthrough() {
  const data = await api("/api/release-governance/v10-1-usability-walkthrough");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Walkthrough"));
}
async function loadV101SampleDemoScript() {
  const data = await api("/api/release-governance/v10-1-sample-demo-script");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Demo Script"));
}
async function loadV101OptionalDeploymentGuide() {
  const data = await api("/api/release-governance/v10-1-optional-deployment-guide");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Deployment Guide"));
}
async function loadV101OperatorQuickstartPackage() {
  const data = await api("/api/release-governance/v10-1-operator-quickstart-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.1 Operator Quickstart"));
}

// ==== governance_v102_ui.js ====
async function loadV102FirstRunWizard() {
  const data = await api("/api/release-governance/v10-2-first-run-wizard");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 First-run Wizard"));
}
async function loadV102DemoResetSafetyCheck() {
  const data = await api("/api/release-governance/v10-2-demo-reset-safety-check");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 Demo Reset Safety"));
}
async function loadV102DemoResetPlan() {
  const data = await api("/api/release-governance/v10-2-demo-reset-plan");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 Demo Reset Plan"));
}
async function loadV102OperatorFirstRunPackage() {
  const data = await api("/api/release-governance/v10-2-operator-first-run-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.2 Operator First-run Package"));
}

// ==== governance_v103_ui.js ====
async function loadV103DemoDataProfiles() {
  const data = await api("/api/release-governance/v10-3-demo-data-profiles");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Demo Data Profiles"));
}
async function loadV103DemoProfileResetPlan() {
  const data = await api("/api/release-governance/v10-3-demo-profile-reset-plan?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Demo Profile Reset Plan"));
}
async function loadV103TutorialProgress() {
  const data = await api("/api/release-governance/v10-3-tutorial-progress");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Tutorial Progress"));
}
async function completeV103TutorialStep() {
  const data = await api("/api/release-governance/v10-3-tutorial-progress/profile?status=Done&operator_name=local-operator", { method: "POST" });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Tutorial Step Saved"));
}
async function loadV103OperatorTutorialPackage() {
  const data = await api("/api/release-governance/v10-3-operator-tutorial-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.3 Operator Tutorial Package"));
}

// ==== governance_v104_ui.js ====
async function loadV104SampleProjectBuilder() {
  const data = await api("/api/release-governance/v10-4-sample-project-builder?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Sample Project Builder"));
}
async function buildV104SampleProject() {
  const data = await api("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk&operator_name=local-operator", { method: "POST" });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Sample Project Built"));
}
async function loadV104TutorialCompletionBadge() {
  const data = await api("/api/release-governance/v10-4-tutorial-completion-badge");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Completion Badge"));
}
async function loadV104OperatorSampleBuilderPackage() {
  const data = await api("/api/release-governance/v10-4-operator-sample-builder-package");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.4 Builder Package"));
}

// ==== governance_v105_ui.js ====
async function loadV105ProfileResetPlan() {
  const data = await api("/api/release-governance/v10-5-profile-reset-plan?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.5 Profile Reset Plan"));
}
async function executeV105ProfileReset() {
  const phrase = "RESET DEMO PROFILE: core-risk";
  const data = await api(`/api/release-governance/v10-5-execute-profile-reset?profile_id=core-risk&approval=${encodeURIComponent(phrase)}&operator_name=local-operator`, { method: "POST" });
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.5 Profile Reset Complete"));
}
async function loadV105OperatorResetPackage() {
  const data = await api("/api/release-governance/v10-5-operator-reset-package?profile_id=core-risk");
  if (data.content) window.lastEvidenceMarkdown = data.content;
  showRich("readiness", renderGenericGovernanceCard(data, "v10.5 Reset Package"));
}

// ==== governance_v106_ui.js ====
async function loadV106RollbackSnapshot() {
  const data = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Rollback Snapshot"));
}

async function executeV106ProfileReset() {
  const phrase = "RESET DEMO PROFILE: core-risk";
  const url = `/api/release-governance/v10-6-execute-profile-reset?profile_id=core-risk&approval=${encodeURIComponent(phrase)}&operator_name=local-operator`;
  const data = await api(url, { method: "POST" });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Reset With Audit"));
}

async function loadV106ProfileResetAuditTrail() {
  const data = await api("/api/release-governance/v10-6-profile-reset-audit-trail?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Reset Audit Trail"));
}

async function loadV106OperatorRollbackPackage() {
  const data = await api("/api/release-governance/v10-6-operator-rollback-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.6 Rollback Package"));
}

// ==== governance_v107_ui.js ====
async function loadV107RollbackImportRehearsal() {
  const data = await api("/api/release-governance/v10-7-manual-rollback-import-rehearsal?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.7 Rollback Import Rehearsal"));
}

async function loadV107RestoreChecklist() {
  const data = await api("/api/release-governance/v10-7-restore-checklist?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.7 Restore Checklist"));
}

async function loadV107OperatorRestorePackage() {
  const data = await api("/api/release-governance/v10-7-operator-restore-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.7 Restore Package"));
}

// ==== governance_v108_ui.js ====
async function loadV108GuardedRestorePlan() {
  const data = await api("/api/release-governance/v10-8-guarded-restore-plan?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Guarded Restore Plan"));
}

async function executeV108GuardedManualRestore() {
  const phrase = encodeURIComponent("RESTORE DEMO PROFILE: core-risk");
  const data = await api(`/api/release-governance/v10-8-execute-guarded-manual-restore?profile_id=core-risk&restore_approval=${phrase}&operator_name=demo`, { method: "POST" });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Manual Restore"));
}

async function loadV108RestoreAuditTrail() {
  const data = await api("/api/release-governance/v10-8-restore-audit-trail?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Restore Audit"));
}

async function loadV108OperatorRestoreExecutionPackage() {
  const data = await api("/api/release-governance/v10-8-operator-restore-execution-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.8 Restore Package"));
}

// ==== governance_v109_ui.js ====
async function loadV109RestoreConflictReport() {
  const data = await api("/api/release-governance/v10-9-restore-conflict-report?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Restore Conflicts"));
}

async function loadV109GuardedRestorePlan() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const data = await api("/api/release-governance/v10-9-guarded-restore-plan?profile_id=core-risk", { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Digest Lock Plan"));
}

async function executeV109GuardedManualRestore() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const phrase = encodeURIComponent("RESTORE DEMO PROFILE: core-risk");
  const lock = encodeURIComponent(snapshot.snapshot_digest);
  const path = `/api/release-governance/v10-9-execute-guarded-manual-restore?profile_id=core-risk&restore_approval=${phrase}&snapshot_digest_lock=${lock}&operator_name=demo`;
  const data = await api(path, { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Locked Restore"));
}

async function loadV109RestoreDigestLockAuditTrail() {
  const data = await api("/api/release-governance/v10-9-restore-digest-lock-audit-trail?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Digest Lock Audit"));
}

async function loadV109OperatorRestoreConflictPackage() {
  const data = await api("/api/release-governance/v10-9-operator-restore-conflict-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v10.9 Restore Package"));
}

// ==== governance_v110_ui.js ====
async function loadV110RestoreGovernanceStabilityReport() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const data = await api("/api/release-governance/v11-0-restore-governance-stability-report?profile_id=core-risk", { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v11.0 Recovery Stability"));
}

async function loadV110FinalOperatorRecoveryRunbook() {
  const snapshot = await api("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk");
  const data = await api("/api/release-governance/v11-0-final-operator-recovery-runbook?profile_id=core-risk", { method: "POST", body: JSON.stringify(snapshot) });
  showRich("readiness", renderGenericGovernanceCard(data, "v11.0 Recovery Runbook"));
}

async function loadV110OperatorRecoveryPackage() {
  const data = await api("/api/release-governance/v11-0-operator-recovery-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.0 Recovery Package"));
}

// ==== governance_v111_ui.js ====
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

// ==== governance_v112_ui.js ====
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

// ==== governance_v113_ui.js ====
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

// ==== governance_v114_ui.js ====
async function loadV114RecoveryEvidenceBundle() {
  const data = await api("/api/release-governance/v11-4-recovery-evidence-bundle?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.4 Recovery Evidence Bundle"));
}

async function loadV114FinalDemoHandoffPolish() {
  const data = await api("/api/release-governance/v11-4-final-demo-handoff-polish?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.4 Final Demo Handoff"));
}

async function loadV114OperatorDemoHandoffPackage() {
  const data = await api("/api/release-governance/v11-4-operator-demo-handoff-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.4 Demo Handoff Package"));
}

// ==== governance_v115_ui.js ====
async function loadV115DemoReleaseCandidateFreeze() {
  const data = await api("/api/release-governance/v11-5-demo-release-candidate-freeze?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.5 Demo RC Freeze"));
}

async function loadV115OperatorAcceptanceChecklist() {
  const data = await api("/api/release-governance/v11-5-operator-acceptance-checklist?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.5 Acceptance Checklist"));
}

async function loadV115OperatorReleaseCandidatePackage() {
  const data = await api("/api/release-governance/v11-5-operator-release-candidate-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.5 RC Package"));
}

// ==== governance_v116_ui.js ====
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

// ==== governance_v117_ui.js ====
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

// ==== governance_v118_ui.js ====
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

// ==== governance_v119_ui.js ====
async function loadV119FinalReleaseTagPreparation() {
  const data = await api("/api/release-governance/v11-9-final-release-tag-preparation?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.9 Release Tag"));
}

async function loadV119PortfolioDemoScript() {
  const data = await api("/api/release-governance/v11-9-portfolio-demo-script?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.9 Portfolio Script"));
}

async function loadV119OperatorFinalReleasePackage() {
  const data = await api("/api/release-governance/v11-9-operator-final-release-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v11.9 Final Package"));
}

// ==== governance_v120_ui.js ====
async function loadV120BaselineFreezeSummary() {
  const data = await api("/api/release-governance/v12-0-baseline-freeze-summary?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v12.0 Baseline Freeze"));
}

async function loadV120ProductionDeploymentChecklist() {
  const data = await api("/api/release-governance/v12-0-production-deployment-checklist?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v12.0 Deployment Checklist"));
}

async function loadV120OperatorDeploymentPackage() {
  const data = await api("/api/release-governance/v12-0-operator-deployment-package?profile_id=core-risk");
  showRich("readiness", renderGenericGovernanceCard(data, "v12.0 Deployment Package"));
}

