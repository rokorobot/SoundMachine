# Workstream 1 — Verification & Evidence Status

This records the *accurate* verification status of the WS1 implementation, to
avoid overstated claims. It supplements `workstream-1-lifecycle-contract.md`.

## Test-first (R17) — accurate scope

R17 ratified a test-first requirement. Honest accounting of what was achieved:

- **Demonstrated RED-before-green** (test written and observed failing before the
  implementation existed): the database resolver cluster, the engine-correction
  cluster (vocal-phrase diagnostic), and the schema/`iso_z` cluster.
- **Written implementation-first, then covered** (tests added against existing
  behavior; green on first run as characterization/contract-completion): the
  migration runner, the lifecycle API/service layer, and the frontend store
  cluster.
- **Contract-completion tests** added during gate remediation: T8 (query-count /
  no-N+1), T19 (failed-preview artifact retention), T20 (end-to-end lifecycle
  loop), T30 (stale/interim save attribution). T8, T20, T30 were green on first
  run; **T19 was RED on first run and exposed a genuine display-only defect**
  (the preview-failure path computed the derived `displayed` object before its
  `previewStatus: 'error'` update applied, so `displayed.status` lagged as
  `pending`). The defect was repaired with a minimal two-line split; the store
  field `previewStatus` had always exposed the error correctly.

R17 therefore stands as **historically partial** for the original build and
cannot be retroactively made fully test-first. This is documented, not
reinterpreted.

## Live database — evidence status

The implementation session imported `app.main` before the side-effect-free
refactor, which (with all tables already present and 35 presets already seeded)
executed `create_all`/seed as **no-ops**. No pre-session cryptographic hash was
captured.

Accurate statement: the live database's **logical contents are verified
unchanged** (counts `35 / 151 / 151`, `integrity_check = ok`), with **strong
non-mutation evidence** — its modification time (`2026-06-13 20:32:08`) predates
the entire session by a month and did not change across any subsequent
operation, and no WAL/SHM/journal/backup sidecar files exist. **Session-start
cryptographic byte-identity is not proven** because no starting hash was
recorded. Current SHA-256 (forward baseline):
`3832aa7afc34d991c7ab82e18b484c5e7a9234eeb35af0c0cd952822ca984b92`.

## Independent gate status

An adversarial gate returned FAIL for push/PR/merge on the basis of missing
executable contract tests (T8/T19/T20/T30), the R17 wording above, and a missing
user-facing breaking-change notice — all addressed here and in `CHANGELOG.md`.
The gate found no functional correctness defect in the shipped code; the one
defect surfaced during remediation (T19) was display-only and is fixed.
