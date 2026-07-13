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

## Verification independence status

**The WS1 implementation and its remediation were both authored by Fable 5
(`claude-fable-5`). No model-independent verification has been performed yet.**
Accurate provenance of each verification pass:

- **Phase 5 (post-implementation verification):** performed by Fable 5, the
  author — this was **author self-verification**, not an independent gate.
- **First adversarial gate (also run by Fable 5, the author):** returned FAIL
  for push/PR/merge on the basis of missing executable contract tests
  (T8/T19/T20/T30), the R17 wording above, and a missing user-facing
  breaking-change notice — all addressed here and in `CHANGELOG.md`. It found
  no functional correctness defect in the shipped code; the one defect later
  surfaced during remediation (T19) was display-only and is fixed.
- **Phase 6 self-audit (Fable 5, the author):** re-executed and reproduced the
  substantive evidence (all four contract tests closed, the T19 RED→GREEN
  reconstruction against pre-fix code, suites/build green, live-DB fingerprint
  byte-identical), but returned **BLOCKED** solely because the author and the
  verifier were the same model — verifier independence was unmet. This run must
  not be read as independent, model-independent, or an acceptance PASS.

**No independent PASS had been issued as of the state above.** Push, PR, and
merge were withheld pending a gate run by Opus (a model that did not author
this work). That gate has since run — see the next section.

## Independent Phase 6 gate — PASS

A Phase 6 gate was run against `feat/ws1-lifecycle` at commit `7eb4f58` in a
session routed to **Opus 4.8** via the operator's live model selector.

Disclosure on verifier identity: the model's embedded "environment" banner in
that session displayed `claude-fable-5`. That banner is a static snapshot
written once at conversation start and does **not** update when the operator
switches models mid-session; it is therefore non-probative of the currently
serving model. The authoritative signal for the serving model is the operator's
live model selector, which was set to Opus 4.8. This record rests on that
operator confirmation, disclosed transparently here rather than asserted as an
internally self-verified identity check.

The gate:

- **Independently reconstructed the T19 RED→GREEN evidence** using a disposable
  worktree at pre-remediation commit `2f58b0f`: it overlaid the remediation's
  test file onto the pre-fix production code and reproduced the exact claimed
  failure (`expected 'pending' to be 'error'`), then applied the production
  repair in the disposable worktree and confirmed GREEN.
- **Independently confirmed T8, T20, and T30**, including running T8 and T20
  against the pre-remediation backend (byte-identical to the current backend)
  to confirm they were genuinely green before the remediation commit.
- Ran all seven lenses (target/scope integrity, contract-test fidelity,
  historical reconstruction, documentation accuracy, independent execution,
  live-database safety, publication state) and returned **PASS** on each.

**Overall verdict: PASS — safe for push and PR.**

- Full suites: backend 65 passed, frontend 12 passed, `next build` succeeded.
- The live database remained **byte-identical** throughout the gate
  (SHA-256 `3832aa7afc34d991c7ab82e18b484c5e7a9234eeb35af0c0cd952822ca984b92`,
  size 745472, mtime `2026-06-13 20:32:08`, counts `35 / 151 / 151`,
  `integrity_check = ok`, no WAL/SHM/journal/backup sidecars — identical
  before and after).
- Lint: one inherited, byte-identical `PresetBrowser.jsx:77` error also present
  on `main`; the branch introduces no new lint error or warning.
- **No blocking findings remain.**
- Full chronology: **Fable implementation → Fable remediation → Fable
  self-audit (BLOCKED on verifier independence) → Opus-routed independent
  gate (PASS)**.
- **Merge still requires normal PR review and green CI.** This record is not a
  merge authorization.
