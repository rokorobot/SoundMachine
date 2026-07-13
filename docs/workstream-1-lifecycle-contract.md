# SoundMachina — Workstream 1 Lifecycle Contract (Consolidated, Ratified)

**Scope:** Generation, Snapshot, Restore & Lineage Lifecycle.
**Status:** Ratified by Robert. Authoritative for WS1 implementation.

## Ratification authority & precedence

- **Revision 2** supplies the complete base contract, **R1–R36**.
- **Revision 3** supersedes its affected sections and adds **R37–R43**. Revision 3 wording takes precedence wherever it differs from Revision 2.
- **C1–C2** are binding mechanical clarifications and take precedence over any looser wording above.

## Verified starting database baseline

Recorded at ratification on branch `main` @ `c6b0fae`, clean working tree:

| Metric | Value |
|---|---|
| `PRAGMA integrity_check` | `ok` |
| `presets` rows | 35 |
| `blueprint_snapshots` rows | 151 |
| `generation_history` rows | 151 |
| `backend/sound_machina.db` size | 745,472 bytes |

Verified stored-data facts used by this contract:
- All 186 stored blueprints (35 presets + 151 snapshots) contain exactly the 13 expected keys.
- Every `genre`/`motif_type`/`motif_behavior`/`harmony_mode`/`target_model` value is within the known UI vocabulary → strict enum validation is safe.
- Zero `(lineage_name, version)` duplicates exist → a unique index is safe.
- Legacy lineages present: `PSYCH_TEC` (67), `CUSTOM` (82), `COLD_SIGNAL` (2).
- Legacy name → preset uniqueness: `Psych Tec` and `Cold Signal` each match exactly one preset; `CUSTOM` matches none.

## Live-database authorization boundary

**Live-database migration is NOT authorized in this session.** No implementation step may migrate, rewrite, reset, prune, delete, or start the application against `backend/sound_machina.db`, nor modify any of its 151 snapshot or 151 history rows. All automated work uses temporary SQLite databases and deterministic sanitized legacy fixtures. A temporary *copy* of the real database may be used only for final manual migration verification; the original is never operated on. The live database is never committed as a test fixture.

---

## Ratified rulings R1–R43

**R1** — Working state and persisted history are different concepts. Changing controls updates working state but does not create history.
**R2** — Debounced live prompt preview is retained; preview generation is non-persistent and must not create a snapshot or generation-history row.
**R3** — Only an explicit SAVE SNAPSHOT operator action persists a snapshot. Persisted snapshots are immutable.
**R4** — Rapid control changes coalesce into a trailing generation for the latest complete blueprint; the final state must always be generated.
**R5** — Responses are correlated with their originating revision; an older response must never overwrite results for newer controls.
**R6** — Restoring a snapshot reproduces its stored blueprint and generated artifacts without calling generation and without creating/mutating any DB row (see R18 for legacy limits).
**R7** — Restore rebinds working state to the restored snapshot's lineage; subsequent edits are unsaved working state; the next explicit save creates a new immutable descendant.
**R8** — Selecting a preset establishes a lineage starting point; sufficiently mutated state is not silently represented as the original preset. Lineage metadata is explicit, not a sticky name.
**R9** — Preserve all 151 snapshots and history rows. No automatic pruning, reset, migration-time deletion, or silent deduplication.
**R10** — Registry reads must not use unbounded fetch-all + N+1. Deterministic pagination; no automatic pruning.
**R11** — The snapshot-version allocator is safe against duplicate version assignment, scoped to a local single-user product.
**R12** — Local single-user only. No auth, accounts, cloud sync, or collaboration.
**R13** — Suno and Udio remain supported; the 120-character Suno assumption is not authoritative and is removed pending separate research.
**R14** — Generated negative prompts remain machine-derived; an override may be designed only if required to resolve the vocal-phrase contradiction (superseded by R27: no override in WS1).
**R15** — ArrangementEngine's decorative/parameter-insensitive behavior is recorded debt, outside this milestone.
**R16** — MP3-to-blueprint analysis ingestion is explicitly outside this milestone.
**R17** — Implementation is test-first; tests cover lifecycle invariants, not merely that a runner works.
**R18** — Exact restoration is guaranteed only for snapshots created under the new contract. Legacy snapshots lack stored motif/timeline artifacts; when rebuilt they are labelled `LEGACY_RECONSTRUCTED` and never described as exact historical output.
**R19** — After every successful save, working lineage advances to the newly saved snapshot: `activeSnapshotId` = returned ID; `parentSnapshotId` = returned ID; bound fingerprint = saved fingerprint; displayed artifacts = returned artifacts; state = clean. A later save descends from this new snapshot.
**R20** — Revision and dirtiness are separate: monotonic revision controls preview correlation/stale rejection; dirty/clean is canonical-equality (hash) between working and bound blueprint. Returning all fields to bound values returns to clean.
**R21** — `origin_id INTEGER` is replaced by a representation supporting both integer preset IDs and string snapshot IDs (`origin_type` + `origin_ref TEXT`).
**R22** — Server-authoritative saves: `POST /api/snapshots` regenerates authoritative artifacts, persists atomically, returns the exact saved record; the client replaces its displayed preview with that record before marking clean (narrowed by R37).
**R23** — Every new snapshot stores an explicit `engine_version`/`PIPELINE_VERSION` identifying its generation semantics.
**R24** — Stable lineage identity is separated from display name: stable key, display name, version within lineage, parent snapshot ID; compatible with untouched legacy rows; no silent row rewrites.
**R25** — Saving unchanged state: first save of an unsaved CUSTOM/preset-bound blueprint is allowed; after a successful save or restore, SAVE SNAPSHOT is disabled while the canonical blueprint is unchanged; reverting edits to bound values re-disables save.
**R26** — `previewModel` is a view concern (renamed from `activeModel`), independent of `blueprint.target_model`; switching the visible Suno/Udio tab does not bump revision or dirty the blueprint; diagnostics visibly identify which target they evaluate.
**R27** — The minimal vocal-phrase repair is removal of the false diagnostic against a machine-owned negative value. No invented artistic exclusions, no override field, no expansion into Prompt Intelligence.
**R28** — Initial load begins unbound as CUSTOM; no auto-bind to the first preset before explicit selection; initial preview remains non-persistent.
**R29** — A dirty marker is sufficient for heavily modified preset descendants; no detach/fork control required.
**R30** — Debounce defaults accepted: ~300 ms trailing, ~1000 ms max wait; isolated and configurable. Revision guards remain authoritative because AbortController cannot guarantee the server stopped.
**R31** — Before the first schema migration the app automatically creates and verifies a one-time SQLite backup; migration aborts without changing schema if backup verification fails.
**R32** — The CWD-relative DB path is resolved explicitly; migration operates on the existing active DB and never silently creates a second empty DB when path anchoring is introduced. Discovery, selection, ambiguity handling, and rollback are documented.
**R33** — The live DB is never a committed/required test fixture. Repository tests use deterministic sanitized legacy fixtures. A temporary copy of the real DB may be used only for local migration verification.
**R34** — Unrelated cleanup (unused icons, `activeExportMode`, cosmetic/dead-code removal) is out of scope unless required for compilation.
**R35** — All 151 existing snapshots and history rows remain untouched: no deletion, dedup, artifact backfill, lineage rewrite, or automatic pruning.
**R36** — Live preview remains ratified and non-persistent.
**R37** — Save completion must never overwrite edits made after SAVE SNAPSHOT was clicked. See §"Save-race".
**R38** — A clean snapshot-bound state must display its exact bound artifacts. See §"Edit/revert".
**R39** — Stable preset lineage semantics: one stable lineage per persisted preset via server-owned association to the preset's DB ID; same preset resolves to the same lineage across sessions; fresh explorations may add roots/branches inside that lineage; custom projects create separate named lineages; display names are not relational identity.
**R40** — Persist every operator-visible generated artifact required for exact new-snapshot restoration: Suno prompt, Udio prompt, negative prompts, scores, recommendations, motif block, arrangement timeline, artifacts provenance, engine version. Save response and detail endpoint return the same complete contract.
**R41** — Enforce origin and ancestry integrity server-side (see §"Server validation"). Invalid ancestry/origin → typed 409/422 and zero writes. Bounded retry executes only for recognized unique-version or snapshot-ID collisions.
**R42** — New lineage keys use UUID4 (128-bit); the PK constraint is the collision backstop with creation retry. Human-readable snapshot IDs may retain slug+version, but relational identity never depends on the display ID.
**R43** — The DB anchor is defined as executable code: `Path(__file__).resolve().parents[1] / "sound_machina.db"` (from `backend/app/database.py`, `parents[1]` = `backend/`). A test proves CWD-independence.

## Binding clarifications C1–C2

**C1 — Snapshot-origin lineage.** For `origin_type="snapshot"`, `lineage_key` must be derived from or exactly match `effectiveKey(parent_snapshot)`. A snapshot-origin request with no usable parent lineage is rejected and must never enter first-lineage creation. The server is authoritative. Invalid cases (missing lineage, mismatched lineage, nonexistent parent) each produce a typed error and zero DB writes; a valid derived lineage succeeds.

**C2 — Database environment path.** `SOUND_MACHINA_DB` must be an absolute path. A relative value is rejected with a clear blocking startup error and is never resolved relative to CWD. The default remains `Path(__file__).resolve().parents[1] / "sound_machina.db"`.

---

## Final state model (frontend)

```
workingBlueprint   mutable 13-field object; the only thing edits touch
revision           monotonic int; ++ on every mutation AND every bind; ordering only (R20)
boundSnapshotId    string | null — null ⇔ never saved/restored in this binding
boundBlueprint     blueprint adopted at last bind
boundKey           canonicalKey(boundBlueprint)
boundArtifacts     complete persisted artifact set of the bound snapshot + its provenance
                   (STORED | LEGACY_RECONSTRUCTED); null when boundSnapshotId is null
previewArtifacts   last applied preview payload + its issuedRevision + provenance PREVIEW
saveInFlight       {capturedBlueprint, capturedKey, capturedRevision, capturedLineage} | null
isDirty            canonicalKey(workingBlueprint) !== boundKey

displayedArtifacts (derived selector, in order):
  1. boundSnapshotId != null AND !isDirty      → boundArtifacts (bound provenance)
  2. previewArtifacts.issuedRevision == revision → previewArtifacts (PREVIEW)
  3. otherwise                                  → most recent of {preview, bound},
                                                  flagged displayStatus PENDING/STALE;
                                                  never presented as output for current working BP
```

**canonicalKey(bp):** JSON of exactly these 13 fields in fixed order:
`[genre, bpm, energy, motif_type, motif_presence, motif_behavior, harmony_mode, harmony_complexity, bass_aggression, glitch_density, drum_intensity, atmosphere_depth, target_model]`. `previewModel` is not a field, so tab switches never dirty state (R26).

**Preview apply guard (R5+R38), both required:**
`apply ⇔ issuedRevision === revision AND NOT (boundSnapshotId != null AND canonicalKey(working) === boundKey)`.
The scheduler issues no request while selector rule 1 holds (clean snapshot-bound).

## Save-race transition table (R37)

At SAVE click, capture `{blueprint A, key(A), revision r, lineage/parent}`. Later edits mutate only `workingBlueprint`.

| Timeline case | On success (server persisted A as S) | Interim display |
|---|---|---|
| No edits during flight (`key(working)==key(A)`) | Bind wholesale: `boundSnapshotId=S`, `boundBlueprint=returned.blueprint`, `boundKey=key(A)`, `boundArtifacts=returned (STORED)`, lineage key + `parent=S`, engineVersion; revision++; **clean**; rule 1 shows returned artifacts | n/a |
| Edits A→B during flight (`key(working)!=key(A)`) | Bind base only: `boundSnapshotId=S`, `boundKey=key(A)`, `boundArtifacts=returned`, lineage + `parent=S`; **`workingBlueprint`(B) untouched**; remain **dirty**; revision++ (invalidates in-flight previews); **exactly one preview scheduled for B** | S's artifacts, `displayStatus=PENDING`, marked "saved S — preview for current edits pending"; never labelled B's output |
| Reverted to A before response | Same as case 1 (hash decides) | pending B-preview already invalid |
| Failure (any case) | `saveInFlight=null`; no bind, no lineage change; dirtiness vs old boundKey; typed error; edits untouched | previous display retained |

`returned.blueprint`/`capturedBlueprint` are only ever written to `boundBlueprint`, never `workingBlueprint`.

## Edit/revert transition table (R38)

Bound to snapshot S (`boundArtifacts` cached, provenance P):

| Step | working | rev | dirty | previews | displayed |
|---|---|---|---|---|---|
| clean at S | =bound | r | no | none (rule 1 blocks) | boundArtifacts (P) |
| edit BPM 120→130 | ≠bound | r+1 | yes | one debounced (r+1) | pending → preview(130) PREVIEW |
| revert 130→120 | =bound | r+2 | **no** | scheduler issues nothing; any in-flight r+1 dead by revision guard AND clean-bound guard | **boundArtifacts (P), byte-identical, original provenance** |
| late 130-preview arrives | — | — | — | discarded | unchanged |

## Full lifecycle transitions (summary)

- **Initial load (R28):** `DEFAULT_BLUEPRINT`, unbound CUSTOM `{key:null, display:'CUSTOM', origin:custom, ref:null, parent:null}`, one debounced preview, 0 writes.
- **Preset selection:** working=preset BP, bind `{key:null(resolved at save), display:presetName, origin:preset, ref:String(id), parent:null}`, clean, one preview, 0 writes.
- **Ordinary/target/genre/BPM edit:** field updated, rev++, dirty by hash, one debounced preview, 0 writes. (The duplicate trigger at `page.js:48-50` is deleted.)
- **Preview success/stale/failure:** apply iff guard passes / discard / keep previous + typed error.
- **SAVE SNAPSHOT success:** per save-race table; 1 snapshot + 1 history row, atomic.
- **Restore (R6/R7/R18):** working=stored BP, artifacts=stored or reconstructed w/ provenance, lineage rebound `{parent=snapshot_id}`, clean, **no preview scheduled**, 0 writes.
- **Edit after restore:** rev++, dirty, debounced preview.
- **Save after restore:** new descendant; `parent_snapshot_id`=restored id; then parent advances to the new child (R19).

**SAVE enablement (R25):** `canSave = (boundSnapshotId === null) || isDirty`.

---

## Lineage identity model (R24/R39/R42)

Concepts: **Lineage** (family sharing a stable `lineage_key`) · **Root** (`parent_snapshot_id NULL`) · **Branch** (subtree from a restored snapshot) · **Version** (dense per-lineage save counter, no ancestry meaning) · **Parent ancestry** (`parent_snapshot_id` chain, sole truth of descent).

`effectiveKey(row) = row.lineage_key ?? ('legacy:' + row.lineage_name)` — computed on read; zero rewrites.

Get-or-create (server, inside save txn):
- `origin_type='preset'`, no key supplied → `SELECT lineages WHERE preset_id=:id`; hit → reuse (stable across sessions, R39); miss → create `{key:uuid4, display:preset.name, slug:sanitized+discriminator, preset_id}`.
- `origin_type='custom'` → independent named lineage; `preset_id NULL`.
- `origin_type='snapshot'` (C1) → `lineage_key` must equal `effectiveKey(parent)`; never creates a lineage.

Legacy association at migration: associate `preset_id` iff exactly one preset satisfies `sanitize(preset.name)==lineage_name` and no ambiguity; else independent + reported. (Verified: PSYCH_TEC←Psych Tec, COLD_SIGNAL←Cold Signal, CUSTOM independent.)

`snapshot_id = {slug}_{version:04d}` (format unchanged; global unique index remains the backstop).

## Persisted-artifact schema (R40)

`generation_history` (existing `prompts_json`, `scores_json` retained; additive columns):

```sql
ALTER TABLE generation_history ADD COLUMN artifacts_json TEXT NULL;
--  {"motif_block": str, "arrangement_timeline": [...], "recommendations": [{level,code,message,target}, ...]}
ALTER TABLE generation_history ADD COLUMN engine_version TEXT NULL;
```

Uniform artifact contract (save response == detail endpoint == store `boundArtifacts`):
```
{ prompts: {suno:{style_tags,prompt_body,negative_prompt}, udio:{tags,prompt_body,negative_prompt}},
  scores, recommendations, motif_block, arrangement_timeline, engine_version, artifacts_provenance }
```
Persisted: prompts (incl. negatives), scores, recommendations, motif_block, arrangement_timeline, engine_version. Recomputable-by-design (not artifacts): drift/comparison output, preview results. Legacy rows: prompts/scores exact; motif/timeline/recommendations reconstructed under `LEGACY_RECONSTRUCTED`.

## Additive schema (R21/R24/R35)

```sql
-- blueprint_snapshots: additive columns
ALTER TABLE blueprint_snapshots ADD COLUMN lineage_key        TEXT NULL;  -- NULL ⇒ legacy
ALTER TABLE blueprint_snapshots ADD COLUMN parent_snapshot_id TEXT NULL;
ALTER TABLE blueprint_snapshots ADD COLUMN origin_type        TEXT NULL;  -- preset|snapshot|custom
ALTER TABLE blueprint_snapshots ADD COLUMN origin_ref         TEXT NULL;  -- preset id str | snapshot_id | NULL

-- generation_history: additive columns (see artifact schema)
ALTER TABLE generation_history ADD COLUMN artifacts_json TEXT NULL;
ALTER TABLE generation_history ADD COLUMN engine_version TEXT NULL;

CREATE TABLE lineages (
  key TEXT PRIMARY KEY, display_name TEXT NOT NULL, slug TEXT NOT NULL UNIQUE,
  preset_id INTEGER NULL UNIQUE, created_at DATETIME NOT NULL
);
CREATE TABLE schema_version (version INTEGER PRIMARY KEY, applied_at DATETIME NOT NULL);
CREATE UNIQUE INDEX ux_snapshots_lineagekey_version ON blueprint_snapshots(lineage_key, version);
```
NULLs are distinct in SQLite, so legacy rows (`lineage_key NULL`) are exempt from the unique index.

---

## API contract

Error envelope (all non-2xx): `{"error": {"code": "<STABLE_CODE>", "message": "<operator-safe>"}}` — no `str(e)`, no tracebacks.

- **`POST /api/preview`** (new) — body: blueprint (+ optional `client_revision`, echoed). Returns `{prompts, motif_block, arrangement_timeline, scores, recommendations, client_revision}`. **Zero DB writes.**
- **`POST /api/snapshots`** (new) — body `{blueprint, lineage:{lineage_key|null, display_name, origin_type, origin_ref, parent_snapshot_id}}`. Server-authoritative (regenerates artifacts), atomic insert, returns full record with `artifacts_provenance:"STORED"`. Validation order in §"Server validation".
- **`GET /api/snapshots`** — `?limit=1..200(default 50)&before_id=<int>`, order `id DESC`, single LEFT JOIN (no N+1), returns `{items, total, next_cursor}`.
- **`GET /api/snapshots/{id}`** — stored artifacts (`STORED`) or reconstructed motif/timeline/recommendations for legacy rows (`LEGACY_RECONSTRUCTED`, `engine_version:null`).
- **Validation:** `Literal` enums on the 5 categorical fields + existing bounds.
- **Timestamps:** tz-aware UTC with `Z`; legacy naive read as UTC.
- **Removed after consumer search (breaking change):** `POST /api/generate`, `POST /api/analyze-prompt`, `POST /api/snapshots/{id}/restore`.
- **Scoring (R13/R27):** remove `[:120]` truncation + 115/120-char rules; surface neutral tag length; suppress `EXCLUSION_DEFICIT` for machine-owned `none` on `vocal phrase` (info note instead); no invented exclusions, no override field.
- **Untouched:** `/api/presets*` (incl. `/{id}`), `/api/export`, `/api/compare`.

`PIPELINE_VERSION` (R23): single constant `backend/app/pipeline_version.py :: PIPELINE_VERSION`. Any output-changing engine edit requires a bump; enforced by golden-fixture coupling (T26).

## Server validation & transaction order (R41/C1)

One transaction; any failure → rollback, typed error, **zero writes**:
1. Schema validation (enums/bounds) → 422 `VALIDATION_FAILED`.
2. Origin validation → 422 `ORIGIN_INVALID`: `preset`⇒ref int & preset exists; `snapshot`⇒ref is existing snapshot_id; `custom`⇒ref NULL.
3. Origin/parent consistency → 422 `ORIGIN_PARENT_MISMATCH` (`parent NULL ⇔ origin∈{preset,custom}`; `snapshot ⇒ origin_ref==parent_snapshot_id`).
4. Parent validation (non-NULL) → 409 `PARENT_NOT_FOUND`; 409 `PARENT_LINEAGE_MISMATCH` if `effectiveKey(parent) != requested lineage_key` (blocks cross-lineage ancestry).
5. **C1 snapshot-origin lineage:** for `origin_type='snapshot'`, require `lineage_key == effectiveKey(parent)`; missing/mismatched → 409/422, zero writes; never enters lineage creation.
6. Lineage resolution: supplied key must exist → 409 `LINEAGE_UNKNOWN`; absent key → authorized first-save get-or-create only (preset/custom).
7. Pipeline run (authoritative artifacts, PIPELINE_VERSION).
8. Version allocation + atomic insert (snapshot + history).
9. IntegrityError discrimination: retry (≤3) **only** for `ux_snapshots_lineagekey_version` or `snapshot_id` unique index; lineage-PK collision → one retry fresh UUID; any other IntegrityError → rollback, 500 `INTERNAL`, no blind retry.

## Database discovery, backup, migration, rollback (R31/R32/R43/C2)

```python
# backend/app/database.py
_BACKEND_DIR = Path(__file__).resolve().parents[1]         # .../backend
DEFAULT_DB_PATH = _BACKEND_DIR / "sound_machina.db"
# C2: env override must be ABSOLUTE, else blocking startup error; never CWD-resolved
if "SOUND_MACHINA_DB" in os.environ:
    raw = os.environ["SOUND_MACHINA_DB"]
    if not Path(raw).is_absolute(): raise StartupError("SOUND_MACHINA_DB must be absolute")
    DB_PATH = Path(raw).resolve()
else:
    DB_PATH = DEFAULT_DB_PATH
```
Ambiguity guard (before any write): with `LEGACY_CWD = cwd/sound_machina.db`; if env set → use it; if `LEGACY_CWD != DEFAULT` and both exist → **abort** (`DB_AMBIGUOUS`, both absolute paths); if only foreign-CWD DB exists → **abort** with instructions; if neither exists → fresh install at DEFAULT. Never silently creates an empty DB beside a populated candidate.

Backup gate (R31), only when `schema_version` shows pending steps, before any DDL: create `<db>.pre-ws1.bak` via SQLite online backup API (never overwrite an existing `.bak`); verify `integrity_check == ok` AND per-table row counts match live; any failure → **abort, schema untouched** (`BACKUP_FAILED`). Then apply additive steps in order, each idempotent (guarded by `PRAGMA table_info`/`sqlite_master`), recording `schema_version`.

Rollback: replace live DB with `.pre-ws1.bak`, or run previous code against the migrated DB (additive-only ⇒ old models ignore new columns/tables).

---

## Test matrix (R17/R33) — T1–T39 + C1/C2

Fixtures: repository tests use synthetic sanitized legacy-schema SQLite; the live DB (or a copy) is used only for one local, manual migration verification and is never committed.

| # | Invariant |
|---|---|
| T1 | Engine determinism goldens across genres/motifs/boundaries, coupled to PIPELINE_VERSION |
| T2 | Sanitized legacy fixture blueprints parse under the new enum schema |
| T3 | `/api/preview` performs zero DB writes (row counts across all 3 tables) |
| T4 | Save creates exactly 1+1 rows atomically, with artifacts, engine_version, correct parent, dense version |
| T5 | Concurrent saves in one lineage → unique versions via retry, no 5xx |
| T6 | Detail: stored artifacts byte-identical for new rows; legacy → reconstruction + flag |
| T7 | Restore path (GET) zero writes |
| T8 | Pagination: `id DESC`, cursor, bounds, total, single query (no N+1) |
| T9 | No mutation surface on snapshots (PUT/PATCH/DELETE → 405/404) |
| T10 | Typed errors; bodies never contain tracebacks/`str(e)`; stable codes |
| T11 | Migration on legacy fixture: identical row counts, columns added, lineages seeded, legacy reads OK, idempotent re-run |
| T12 | `Z`-suffixed timestamps; legacy naive read as UTC |
| T13 | Debounce: N rapid edits → exactly one request, final blueprint |
| T14 | Out-of-order responses: stale discarded, newer retained |
| T15 | Trailing request guaranteed after burst; supersession abort optimization-only |
| T16 | Restore: no preview scheduled, artifacts adopted w/ provenance, lineage rebound, clean |
| T17 | Full transition table, parameterized, asserting hash-based dirtiness |
| T18 | Save-after-restore: same lineage key, next version, parent=restored id |
| T19 | Preview failure: previous results kept, typed error, recovery on next edit |
| T20 | Full loop: load(unbound)→select→burst→save→edit→restore→edit→save ⇒ exactly 2 new rows, correct chain |
| T21 | Sequential parent advancement: 3 saves ⇒ linear chain (parent(s3)=s2, parent(s2)=s1, parent(s1)=null) |
| T22 | Edit-and-revert ⇒ clean, SAVE disabled, preview traffic alters nothing bound |
| T23 | Save response replaces preview; late stale preview cannot overwrite it |
| T24 | Legacy reconstruction disclosure: `LEGACY_RECONSTRUCTED` + null engine_version |
| T25 | Lineage collision resistance: same-slug lineages → distinct keys, deterministic discriminator, no snapshot_id collision |
| T26 | Engine-version coupling: saved rows carry PIPELINE_VERSION; golden version == constant |
| T27 | DB-path ambiguity: both DBs → abort; foreign-CWD only → abort; env set → used; never silent empty DB |
| T28 | Backup gate: backup/verify failure → abort pre-DDL, schema unchanged; existing `.bak` never overwritten |
| T29 | Edit during save preserved: working==B, bound=S(key A), dirty, exactly one preview for B; working never assigned from captured/returned |
| T30 | Save A then preview B: interim display = S artifacts, PENDING, never attributed to B; stale A-era preview cannot apply post-bind |
| T31 | Restored edit-and-revert: displayed == boundArtifacts byte-identical, original provenance; pending preview neither applies nor re-issues |
| T32 | Two sessions selecting one preset → one lineage key, continuous versions, no NAME_2 lineage |
| T33 | Ambiguous legacy↔preset never guessed: no association + notice; unique-match → associated |
| T34 | Recommendations survive save→detail→restore byte-equal; legacy → reconstructed + flagged |
| T35 | Cross-lineage parent → 409 PARENT_LINEAGE_MISMATCH, zero writes |
| T36 | Malformed origin matrix → each rejected typed, zero writes |
| T37 | Unrelated IntegrityError → single attempt, rollback, typed INTERNAL, no retry |
| T38 | Lineage-key collision (dup UUID) → one retry fresh UUID; PK backstop; 128-bit keys, no lin_<8hex> |
| T39 | Resolver CWD-independence: DEFAULT_DB_PATH identical from 3 CWDs, equals real backend/sound_machina.db; env override respected |
| **C1-a** | snapshot-origin with missing lineage_key → rejected, zero writes |
| **C1-b** | snapshot-origin with mismatched lineage_key → rejected, zero writes |
| **C1-c** | snapshot-origin with nonexistent parent → rejected, zero writes |
| **C1-d** | snapshot-origin with valid derived lineage → succeeds |
| **C2-a** | absolute SOUND_MACHINA_DB honored |
| **C2-b** | relative SOUND_MACHINA_DB → blocking startup error, no DB created |
| **C2-c** | CWD independence of default; ambiguity detection; no silent empty DB |

## Residual notes (accepted, not violations)

- Committed-save-with-lost-response: an unbound snapshot may become discoverable in the registry; accepted for local single-user scope.
- Artifact freezing: WS1-era snapshots immortalize current prompt characteristics (e.g., motif described twice per body); WS2 improvements apply to new saves only (R6 prefers faithful history).
