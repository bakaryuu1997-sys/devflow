# v11.7 Operator Release Package

# v11.7 Archive Integrity Manifest

Status: Archive integrity manifest ready
Manifest digest: `bcbcdcdb65fd526e64107a480f6700d6395bd80a28809855c1a84e520c65cf59`

## Files
- `README.md` — 2645 bytes — `3b6ae262f8dae49b80b96533537495cc3414f7b811f7cbeb923bbb689346cddd`
- `VERSION.md` — 226 bytes — `883242453c464bfbec0e8f33415c19b8c4775e27c4894cf6c47efdd80125fce7`
- `requirements.txt` — 271 bytes — `276b0442676cb7b010fc523e9b2b32ded4bc15b2a36374cc97a3b7cd037a9c67`
- `goal.md` — 3239 bytes — `815c81c23cd4bf2f78df760998e17ae6f8a1be04bbdd19762fa87e7e1c40dced`
- `app/archive_integrity_service.py` — 6883 bytes — `5e3a50531a1adb88c92737cff46ffa4df11c7b4fe16eebfea2349ca762e08bae`
- `app/routes_v117.py` — 1072 bytes — `228c20c90f9315363de2ab7b84105d1831953db7482f739163d9ec2178d00ce7`
- `docs/V11_7_ARCHIVE_INTEGRITY_RELEASE_NOTES.md` — 1016 bytes — `c8eaec9d9352fe0e06beb0dad4fd358cefdac2dc61d880c9e4a498a803e8fe0a`
- `scripts/export_v11_7_release_package.py` — 665 bytes — `96b873f330e647129f51ff12640d3074ca03a4d3e1c349d514ff3705f174567e`
- `tests/test_v117_archive_integrity_release_notes.py` — 2045 bytes — `76bf7817fcac4288fde629902c9d5794511831b27f296cd487d1a7d69fd34baa`

## Checks
- PASS: v11-6-final-package-exportable — v11.6 final package remains exportable.
- PASS: all-essential-files-present — Essential release files are present.
- PASS: version-current — VERSION.md names v11.7.
- PASS: readme-current — README names v11.7.
- PASS: release-notes-doc-present — v11.7 release notes docs are present.
- PASS: no-new-destructive-path — v11.7 only records integrity and release notes.


# v11.7 Release Notes

Release candidate: `demo-rc-v11.5`
Manifest digest: `bcbcdcdb65fd526e64107a480f6700d6395bd80a28809855c1a84e520c65cf59`

## Highlights
- Final archive manifest with SHA-256 records for release-critical files.
- Polished release notes for beginner install, recovery guardrails, and demo handoff.
- No new destructive reset or restore route after the v11.5 release candidate freeze.

## Upgrade Notes
- Use this package as the v11.7 archive integrity layer on top of demo-rc-v11.5.
- Run the beginner install commands from README before presenting the demo.
- Keep recovery restore locked behind the restore phrase and snapshot digest lock.

## Verification Notes
- Run compileall for app and scripts.
- Run the v11.7 test first, then nearby recovery regression groups.
- Export the v11.7 operator release package and keep it with the final ZIP.
