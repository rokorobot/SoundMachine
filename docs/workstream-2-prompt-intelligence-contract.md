# SoundMachina — Workstream 2 Contract: Prompt Intelligence

**Title:** WS2 — Prompt Intelligence: Unified Prompt Plan & Operator Prompt Controls
**Status:** DRAFT — final rulings F1–F6 applied; awaiting final review sign-off. Not yet implemented.
**Baseline:** `main` @ `17a21a79749da354b2c3efeb2be24d0413dca6b9` (WS1 merged; backend 65 / frontend 12 green; live DB SHA-256 `3832aa7a…84b92` untouched).
**Authority:** Ratified decisions D1–D7, corrections C1–C5, and final rulings F1–F6 (owner rulings, 2026-07-13). All WS1 rulings **R1–R43 + C1–C2 remain binding**; no conflict with them has been identified in this contract.

Provenance tags: **[E]** repository/owner-ruling evidence · **[R]** platform research evidence (see §24) · **[T]** necessary technical implication · **[D]** product decision (ratified D1–D7 unless marked *new*).

---

## 1. Objective

- **P1 [E/D1]** Improve the exported music-generation prompt — SoundMachina's primary product output — via a unified deterministic PromptPlan, evidence-based per-platform renderers, and operator prompt controls (negatives, vocal direction, musical key), with **zero change to WS1 lifecycle semantics and zero database schema change**.

## 2. User journey

- **P2 [E]** The operator adjusts the deck → the live preview shows a structured, deduplicated prompt whose sections follow a parameter-aware arrangement → optionally sets Musical Key, Vocal Style, Lyric Theme, and a Negative mode (Machine / None / Custom) → copies the Suno- or Udio-shaped output into that platform → saves a snapshot that permanently records the exact blueprint and rendered prompts under `engine_version 2.0.0-ws2`.

## 3. Binding invariants

- **P3 [E]** All WS1 rulings (R1–R43, C1–C2) and the WS1 lifecycle contract remain binding and untouched.
- **P4 [E]** The motif identity appears **exactly once** in each rendered prompt body (kills the WS1-era duplication).
- **P5 [T]** PromptPlan construction is a pure, deterministic function of the blueprint; renderers are pure functions of the plan. Identical blueprint ⇒ identical outputs, always.
- **P6 [D3]** All four new fields are optional with behavior-preserving defaults (`negative_override: null`, `vocal_style: ""`, `lyric_theme: ""`, `musical_key: null`).
- **P7 [D2/R]** No platform character-limit, field, or formatting rule may exist in code unless supported by the evidence appendix (§24). Absent evidence ⇒ conservative, format-agnostic rendering.
- **P8 [T]** The visible Arrangement Timeline and the rendered prompt sections derive from the **same ordered `ArrangementSection` list** — they can never disagree.
- **P9 [E/C4]** `PIPELINE_VERSION = "2.0.0-ws2"` (continues the persisted `1.0.0-ws1` convention). Every output-affecting engine change requires a version bump + golden regeneration in the same commit.

## 4. PromptPlan schema

- **P10 [T]** One `PromptPlan` per generation:

```
PromptPlan {
  identity: {
    motif_line:  str,          # the single motif identity statement (from MotifEngine content)
    key_line:    str | None,   # rendered from musical_key when set, e.g. "in F minor"
    vocal_line:  str | None,   # from vocal_style, only when applicable (§9)
    theme_line:  str | None,   # from lyric_theme, only when applicable (§9)
  },
  style: {
    genre_label: str,          # human genre text
    bpm: int,
    descriptors: [str],        # refined descriptor phrases (§ D7 scope)
    narrative:   str,          # composed conversational style description (Suno V4.5 form, evidence S1)
  },
  sections: [ArrangementSection],   # §5 — same objects the timeline shows
  negatives: {
    mode: "machine" | "none" | "custom",
    items: [str],              # effective negative items after mode resolution
  },
  meta: { pipeline_version: str },
}
```

- **P11 [T]** The plan is internal (backend only). It is not persisted; persisted artifacts remain the rendered prompts + existing artifact set (WS1 R40 contract unchanged).

## 5. Arrangement-section list schema (bounded R15 retirement, D4)

- **P12 [D4]** `ArrangementEngine.generate_sections(genre, bpm, energy, glitch_density, drum_intensity)` returns the ordered `ArrangementSection` list:

```
ArrangementSection {
  role:  "intro"|"establish"|"build"|"peak"|"outro"|...   # per-genre template
  label: str,           # display + prompt section name
  time_start/time_end/duration_seconds,                    # as today
  energy_level: int,
  directives: [str],    # parameter-conditioned descriptive phrases
}
```

- **P13 [D4]** Phase templates **vary by genre** (e.g. ambient uses swell/drift/dissolve roles, not "Pressure Build"/"Mutation Peak"); descriptions consume `glitch_density` and `drum_intensity`.
- **P14 [D4]** **Contradiction suppression:** no section may emit a directive contradicting the blueprint (e.g. "maximum glitch triggers" when `glitch_density < 20`; "pounding drums" when `drum_intensity < 20`). Directives are conditioned, not fixed strings.
- **P15 [D4/T]** Deterministic; existing time-code arithmetic retained; the timeline panel renders these same sections (P8).
- **P16 [D4]** Out of scope: editable timeline, free-form arrangement composition, arrangement DB entities, unrelated analyzer redesign.

## 6. Suno renderer contract

- **P17 [T]** Output keys unchanged from WS1 artifacts: `{style_tags, prompt_body, negative_prompt}` — key stability preserves the stored-artifact shape, API responses, and frontend bindings.
- **P18 [R:S1]** `style_tags` carries a **detailed conversational style description** (genre, mood, texture, production elements), reflecting Suno V4.5's documented support for "more detailed style instructions" beyond terse comma descriptors. A compact descriptor list may be appended; no length cap is enforced (P7; no official limit documented — S1).
- **P19 [R:S4]** `prompt_body` is the Lyrics-box payload: bracketed section markers derived from the ordered `ArrangementSection` list's labels, with the identity lines (motif once — P4; key/vocal/theme when set) and per-section directives, reflecting Suno's documented support for "adding more context for your songs directly in the Lyrics box" (S4).
- **P20 [R:S2,S3]** `negative_prompt` is a comma-separated list of concrete excludable elements (instruments/styles/vocal-styles), matching Suno's Exclude field ("Enter any information (instruments, etc) that you do not want in your track", S2; element-style exclusions like `-piano`, S3). UI labels it for the Exclude Styles field.
- **P21 [D-design]** Any Suno/Udio structural difference beyond P18–P20 and P22–P24 must be labeled in code comments as either evidence-backed (cite §24 id) or deliberate SoundMachina design — never asserted platform behavior (C3).

## 7. Udio renderer contract

- **P22 [R:U1,U2]** `tags` carries **free-form topic text + comma-separated genre/mood/instrument tags** ("A song about summer rain, jazz, mellow, warm" pattern), reflecting Udio's documented prompt structure: topic text and tags, with detail across "genre, mood, tempo, instruments, and theme" (U1/U2). `lyric_theme`, when applicable, feeds the topic text.
- **P23 [R:U4]** `prompt_body` is the Lyrics-editor payload using **Udio's documented guidance-tag vocabulary where a section role maps to one** — `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`, `[Instrumental Break]`, `[Drop]`, `[Solo]`, `[Choir]`, `[Spoken Word]` (U4). Section roles without a documented tag render as plain bracketed labels (deliberate design, P21). Adherence is advisory per Udio's own note (U4) — the contract makes no adherence guarantee.
- **P24 [R:U3]** `negative_prompt` is a comma-separated element list intended for Udio's Style-Reduction/"minimize unwanted elements" control (U3). UI labels it accordingly.

## 8. Negative-control semantics (D5, C2)

- **P25 [D3/D5]** `negative_override: str | None`, default `null`.
  - `null` → **machine mode**: negatives derived by the engine exactly as the machine rules dictate.
  - `""` (empty string) → **none mode**: intentionally no negative prompt; renderers emit an empty negative field.
  - non-empty → **custom mode**: the operator's text is the negative content, propagated verbatim (per-platform formatting only).
- **P26 [D5/F4]** The frontend exposes **three explicit choices** — `Machine-generated` / `No negatives` / `Custom` — as a mode selector. Only Custom shows the editor. An empty textarea alone never distinguishes states. Deterministic transition semantics (F4):
  - Entering Custom initializes the editor with a **one-time copy** of the currently derived machine negative prompt; after that copy, the value is **operator-owned and independent** — later parameter changes never silently rewrite custom text.
  - Custom → Machine sets `negative_override = null`. Custom → No negatives sets `negative_override = ""`.
  - Re-entering Custom initializes from the **then-current** machine default, unless a purely session-local unsaved custom draft is deliberately retained by the UI; such a draft is ephemeral client state only.
  - **No hidden fourth state:** persisted blueprint state is fully represented by the tri-state `negative_override` value (`null` / `""` / non-empty). No separate mode field is persisted anywhere.
- **P27 [T/F3]** Validation: `negative_override` may be `null`, exactly `""`, or a non-empty string that is not whitespace-only (whitespace-only ⇒ 422 `VALIDATION_FAILED`; the operator must pick the None mode explicitly). Custom text is stored **verbatim** (no trimming — operator-owned). Bound: ≤ 400 Unicode code points **[F3: SoundMachina validation bound, not a claimed platform limit]**.
- **P28 [T]** Scoring evaluates the **effective** negatives: machine mode as today; none mode is an intentional operator choice (info note `NEGATIVES_DISABLED_BY_OPERATOR`, never a deficit); custom mode is checked for logical conflicts (e.g. excluding drums while `drum_intensity` high) but not second-guessed stylistically.

## 9. Vocal-control semantics (D3)

- **P29 [D3/F3]** `vocal_style: str` (default `""`) — delivery/character/performance direction. `lyric_theme: str` (default `""`) — **lyrical** subject or narrative direction; **not** a lyrics editor. Validation (deterministic, F3): both are trimmed of leading/trailing whitespace; a value trimming to `""` is stored as `""` (the absent state); lengths measured post-trim in Unicode code points — `vocal_style` ≤ 120, `lyric_theme` ≤ 200 **[F3: SoundMachina validation bounds, not claimed platform limits]**; violations ⇒ 422 `VALIDATION_FAILED`, zero writes.
- **P30 [F1]** Applicability rule: vocal controls are applicable when **either** (a) `motif_type == "vocal phrase"` (motif-driven), **or** (b) the operator explicitly supplies a non-empty `vocal_style` or `lyric_theme` (operator-driven). Explicit operator vocal input is an affirmative request for vocal direction and is **never silently ignored** merely because the motif type is not "vocal phrase". When `motif_type != "vocal phrase"` **and** both fields are empty, the PromptPlan contains **no** vocal or lyrical direction. `lyric_theme` is never reinterpreted as an instrumental theme — it remains specifically lyrical. When operator input activates vocal direction despite a non-vocal motif, the advisor emits info `VOCAL_DIRECTION_BY_OPERATOR` (informational disclosure, not an error), and the frontend surfaces it. **[T]** Machine-mode negative derivation is vocal-aware: whenever P30 makes vocal direction applicable, machine negatives must not contain vocal exclusions (no self-contradictory "vocals, singing" excludes against a requested vocal) — custom-mode text is the operator's own and is never edited (P26).
- **P31 [R:S4,U1]** Rendering (whenever P30 makes vocal direction applicable): Suno — vocal/theme lines join the identity block in the Lyrics-box payload (S4). Udio — `lyric_theme` feeds the topic text (U1 "A song about …"); `vocal_style` renders as an identity line and, where it maps, documented tags (e.g. `[Spoken Word]`, `[Choir]` — U4).

## 10. Musical-key semantics (D3)

- **P32 [D3]** `musical_key: str | None`, default `null`. Canonical serialization: `"<Root> <mode>"`.
- **P33 [D3]** Allowed roots (canonical, sharp-preferred): `C, C#, D, D#, E, F, F#, G, G#, A, A#, B`. Allowed modes: `major, minor`. 24 canonical values.
- **P34 [T]** Normalization (validator): trim; case-normalize (`f minor` → `F minor`, `F Minor` → `F minor`); enharmonic flats map to canonical sharps (`Db→C#, Eb→D#, Gb→F#, Ab→G#, Bb→A#`). Anything else ⇒ 422 `VALIDATION_FAILED`. Stored value is always canonical.
- **P35 [F2 — ratified]** Interplay with the existing `harmony_mode` field: `musical_key` is **authoritative for the explicit musical-key line** (P10); `harmony_mode` continues contributing compatible harmonic-texture descriptors. A material conflict (`harmony_mode ∈ {major, minor}` disagreeing with the key's mode) emits advisor info `KEY_MODE_MISMATCH`. The conflict **never rejects preview or save**, and **neither operator field is silently rewritten** — both input values are preserved exactly.

## 11. Scoring and advisor alignment (D7)

- **P36 [D7]** Scoring consumes the PromptPlan-era outputs; rule *meanings* are preserved (same five subscores). Changes are limited to: mode-aware negative evaluation (P28), the new info codes `VOCAL_DIRECTION_BY_OPERATOR` (P30), `KEY_MODE_MISMATCH` (P35), and `NEGATIVES_DISABLED_BY_OPERATOR` (P28), and removal of any rule that inspected now-restructured text in a way that no longer parses.
- **P37 [D2/R]** No character-limit rules are (re)introduced — no official limit was found (§24). The neutral tag/style length display remains.
- **P38 [D7]** No unrelated scoring redesign; no new pseudo-precision (no invented thresholds beyond existing rule style).
- **P39 [D7 — binding]** Composition descriptors that feed `PromptPlan.style.descriptors` are **deterministic and meaningfully finer than the WS1 coarse buckets** for **exactly these six numeric dimensions: `energy`, `bass_aggression`, `glitch_density`, `drum_intensity`, `atmosphere_depth`, `harmony_complexity`**. Genre remains categorical context and is not part of this numeric-refinement requirement. Binding rules:
  - each of the six dimensions must satisfy its **fixed historical discrimination pair** (table below): the two values produced the *same* WS1 descriptor phrase and must produce **meaningfully distinct** WS2 descriptor phrases, with all other blueprint fields identical;
  - refinement remains deterministic (P5);
  - emitting raw slider numbers, or any unsupported pseudo-precision, does **not** satisfy this requirement (P38);
  - the existing genre/parameter golden matrix covers the refined behavior of all six dimensions (W27);
  - scope is limited to descriptors feeding PromptPlan — this authorizes **no** general analyzer redesign (D7);
  - **Phase-A characterization:** before any refinement code is written, WS2 Phase A freezes the six pair results under the unmodified WS1 engine as characterization fixtures, demonstrating that each pair genuinely produced identical WS1 prose — historical evidence, not a manufactured RED test.

  **Fixed discrimination pairs** (derived from the WS1 bucket boundaries in `backend/app/composition_engine.py`; all values within valid 0–100 range; both members of each pair share the quoted WS1 phrase):

  | Dimension | WS1 bucket | Pair | Shared WS1 phrase |
  |---|---|---|---|
  | `energy` | `[60, 85)` | **61 vs 84** | "high energy, driving rhythm, intense power" |
  | `bass_aggression` | `[25, 60)` | **30 vs 55** | "warm analog bassline, solid low-end presence" |
  | `glitch_density` | `[20, 50)` | **25 vs 45** | "subtle glitch textures, light click-and-pop details" |
  | `drum_intensity` | `[50, 80)` | **55 vs 75** | "heavy drums, aggressive syncopated percussion, pounding beats, metallic snares" |
  | `atmosphere_depth` | `[50, 80)` | **55 vs 75** | "vast atmospheric depths, lush synthesizer pads, sweeping echoes" |
  | `harmony_complexity` | `(40, 75]` | **45 vs 70** | "layered, rich harmonies in a &lt;mode&gt; scale" (mode held constant) |

## 12. Frontend behavior

- **P40 [D5/F1]** ControlPanel gains a **Prompt Controls** section: Musical Key select (24 canonical values + "none"), Vocal Style input, Lyric Theme input, and the three-state Negative selector (P26). When explicit vocal input activates vocal direction despite a non-vocal motif (P30), the UI **discloses** this (informational badge/note mirroring `VOCAL_DIRECTION_BY_OPERATOR`) — it does not mark the fields as errors and does not disable them.
- **P41 [F5 — ratified]** PromptPreview renders the new content under the existing keys; provenance ribbon, preview/pending/error status semantics, and copy actions unchanged. Platform-facing captions: **Suno preview — "Style Description" and "Exclude Styles"; Udio preview — "Prompt/Tags" and "Style Reduction"**. Captions are display-only: the blueprint and PromptPlan remain platform-neutral, and no platform-specific blueprint field exists for labeling purposes.
- **P42 [E]** No changes to registry, calibration, mutation, preset panels beyond none required.

## 13. Canonical hashing and dirtiness

- **P43 [T]** The canonical field list extends from 13 to **17**, new fields appended in this fixed order: `[...existing 13..., musical_key, vocal_style, lyric_theme, negative_override]`. Backend (`lineage.py BLUEPRINT_FIELDS`) and frontend (`projectStore.js BLUEPRINT_FIELDS`) must be byte-equal; enforced by a shared-fixture lockstep test (W7).
- **P44 [T]** Old blueprints parse with defaults; `canonicalKey(parse(old_json))` is stable across parses, so old-vs-old comparisons remain consistent. Editing any new field bumps revision, flips dirtiness, schedules preview; reverting restores clean (extends WS1 T17/T22 semantics).

## 14. Concurrency and stale-response behavior

- **P45 [E]** Unchanged: WS1's debounce (300/1000 ms), revision guards, clean-bound preview suppression, and save-race rules (R37/R38) govern. New fields introduce **no new async paths**; they ride the existing blueprint mutation path.

## 15. API compatibility (C1-corrected)

- **P46 [T]** Endpoint set unchanged. Blueprint validation extends with the four optional fields.
- **P47 [C1]** **Requests omitting the new WS2 fields behave identically to requests explicitly providing their WS2 default values.** This is *not* a claim that default WS2 prompt output equals pre-WS2 output — WS2 deliberately changes prompt structure, motif deduplication, arrangement sensitivity, and platform rendering. Compatibility with WS1 means: old requests remain valid; old stored snapshots restore verbatim; old blueprints parse with defaults; lifecycle semantics are unchanged.

## 16. Snapshot and restoration compatibility

- **P48 [E]** Stored snapshots (legacy and WS1-era) are never rewritten or re-rendered in storage (R35/R6). WS1-era snapshots restore their stored prompts/artifacts **verbatim**; `engine_version` (`null` → PRE-WS1, `1.0.0-ws1`, `2.0.0-ws2`) distinguishes eras in the UI as today.
- **P49 [E]** Legacy reconstruction (`LEGACY_RECONSTRUCTED`) now reconstructs with WS2 engines — already-disclosed behavior ("rebuilt by current engines, not historical output"); the disclosure text remains accurate without change.

## 17. Versioning and golden discipline (C4)

- **P50 [C4]** `PIPELINE_VERSION = "2.0.0-ws2"` — durable, consistent with the persisted `1.0.0-ws1` convention. Golden fixtures are regenerated **in the same commit** as any output-affecting change and embed the version (existing T26 coupling extends unchanged).
- **P51 [T]** The WS1-era golden file's content is superseded; the *pre-WS2* outputs are preserved by git history and by the frozen stored artifacts of any WS1-era snapshots — no separate archival fixture is required.

## 18. Migration and rollback behavior (C5)

- **P52 [T]** **No schema migration.** New fields live inside `blueprint_json` / rendered `prompts_json`. `schema_version` and the migration runner are untouched (asserted by W14). The live database is never touched by WS2 work.
- **P53 [C5]** Rollback (checking out pre-WS2 code against post-WS2 data) — precise behavior, proven by W23, not assumed:
  - Pre-WS2 code **parses** new-field blueprint JSON without corrupting the 13 existing fields (extra keys ignored on read).
  - All stored snapshots (any era) remain restorable; stored rows are immutable, so **no data at rest is destroyed** by rollback.
  - **Limitation 1:** pre-WS2 code that *re-serializes* a blueprint (saving a preset or a new snapshot from restored state) **drops the four WS2 fields** from the newly written record — the original stored snapshot is untouched, but the new save silently loses operator prompt controls.
  - **Limitation 2:** pre-WS2 canonical hashing covers 13 fields, so under rollback, dirtiness is blind to WS2-field edits.
  - These limitations are documented product facts of a read-only-safe rollback; full round-trip preservation under rollback is **not claimed** (C5).

## 19. Error semantics and validation bounds

- **P54 [E]** WS1 typed envelope unchanged. All new-field validation failures ⇒ 422 `VALIDATION_FAILED`, zero writes.
- **P55 [F3 — ratified]** Deterministic validation summary — **SoundMachina validation bounds, explicitly not claimed Suno or Udio platform limits**:
  - `negative_override`: `null` | `""` | non-empty non-whitespace-only text, stored verbatim (no trim), ≤ 400 Unicode code points (P27).
  - `vocal_style`: trimmed; trims-to-empty ⇒ stored `""`; ≤ 120 code points post-trim (P29).
  - `lyric_theme`: trimmed; trims-to-empty ⇒ stored `""`; ≤ 200 code points post-trim (P29).
  - `musical_key`: `null` | canonical `"<Root> <mode>"` after P34 normalization.
  - Unicode: lengths counted in Unicode code points, not bytes; any valid JSON string content accepted within bounds.
  - Rejection: every violation ⇒ 422 `VALIDATION_FAILED` with the WS1 envelope, zero writes.

## 20. Executable test matrix

Format: **id — proves (invariant) — fails if (prohibited behavior)**. W1–W15 carried from scoping, with W8 expanded to **W8a–W8e** (C2); W16+ added per ratification; final-ruling splits: **W9a–W9d** (F1), **W16a–W16e** (F4), **W20a–W20d** (F2); **W27–W28** added at final review. No unsuffixed W8/W9/W16/W20 rows exist.

| # | Proves | Fails if |
|---|---|---|
| W1 | PromptPlan determinism across golden matrix (P5) | any nondeterministic plan/render output |
| W2 | Motif appears exactly once per body, both platforms, all genres (P4) | duplication reappears |
| W3 | Evidence-backed structural divergence: Suno narrative style vs Udio topic+tags; Udio sections restricted to documented vocabulary where mapped (P18/P22/P23) | renderers differ only cosmetically, or Udio emits unmapped invented tags where a documented tag exists |
| W4 | Arrangement parameter sensitivity: genre changes template; glitch/drum levels change directives (P13) | ambient shows techno phases; params ignored |
| W5 | Timeline and prompt sections derive from the same ordered `ArrangementSection` list — same roles/labels/times (P8) | panel and prompt disagree |
| W6 | All legacy fixture + real-vocab blueprints parse with defaults (P44) | any stored blueprint fails validation |
| W7 | Frontend/backend canonical-key lockstep via shared fixture (P43) | field lists diverge |
| W8a | `null` override ⇒ deterministic machine negatives (P25) | machine mode altered by presence of the field |
| W8b | `""` ⇒ no negatives rendered on both platforms (P25) | empty mode leaks machine items |
| W8c | Custom text propagates exactly, platform-formatted only (P25) | mutation/truncation of operator text |
| W8d | Omitted field ≡ explicit `null` within WS2 (P47) | omission behaves differently from default |
| W8e | WS1-era stored snapshots restore original stored negatives verbatim (P48) | history re-rendered |
| W9a | Motif-driven vocal applicability: `motif_type == "vocal phrase"` with empty fields still renders motif-appropriate vocal identity (P30) | vocal motif produces no vocal direction |
| W9b | Operator-driven applicability: non-empty `vocal_style`/`lyric_theme` on a non-vocal motif renders vocal direction + `VOCAL_DIRECTION_BY_OPERATOR` info + vocal-aware machine negatives (no "vocals" exclude) (P30) | explicit operator vocal input silently ignored, or machine negatives contradict the requested vocal |
| W9c | No vocal/lyrical direction anywhere in the plan when motif is non-vocal and both fields empty (P30) | phantom vocal direction appears |
| W9d | `lyric_theme` never reinterpreted as instrumental subject matter: with vocal direction inapplicable it renders nowhere; when applicable it renders only as lyrical/topic direction (P30) | theme leaks as an instrumental "about" line outside vocal direction |
| W10 | Dirtiness/edit/revert for each of the 4 new fields (P44) | new-field edit fails to dirty or revert fails to clean |
| W11 | WS1-era snapshot restore returns stored prompts verbatim (P48) | re-rendering of history |
| W12 | Preview zero-writes; save 1+1 atomic with `engine_version 2.0.0-ws2` (P3/P9) | lifecycle regression |
| W13 | Goldens regenerated + version coupling (P50) | engine change without bump, or bump without regeneration |
| W14 | `schema_version` unchanged after full suite (P52) | accidental migration |
| W15 | Full WS1 suite green, unmodified except prompt-content-coupled fixtures (P3) | any WS1 invariant regression |
| W16a | Machine→Custom: editor initialized with a one-time copy of the current machine default; value becomes operator-owned (P26) | prefill missing, or prefill re-applied over operator edits |
| W16b | Custom→Machine ⇒ `null`; Custom→No negatives ⇒ `""`; no null⇄"" reinterpretation in any transition (P26) | a mode switch silently converts null⇄"" or drops custom text into the wrong state |
| W16c | Parameter changes while in Custom never rewrite the custom text (P26) | slider edit mutates operator's negative text |
| W16d | Re-entering Custom initializes from the then-current machine default (absent a deliberate local draft); persisted state remains pure tri-state with no hidden mode field (P26) | stale prefill, or a fourth state persisted anywhere (blueprint JSON, snapshot, preset) |
| W16e | Edit-and-revert across negative modes returns to clean per canonical hash (P26/P44) | mode round-trip leaves phantom dirtiness or fails to dirty |
| W17 | Whitespace-only override rejected 422, zero writes (P27) | whitespace accepted as custom or coerced to none |
| W18 | Musical-key normalization: case + enharmonic inputs → canonical form (P34) | non-canonical value stored |
| W19 | Invalid musical key rejected 422, zero writes (P34) | junk key accepted |
| W20a | Compatible key + harmony (e.g. `F minor` + `minor`): key line rendered, no mismatch note (P35) | spurious warning on compatible inputs |
| W20b | Material conflict (e.g. `C major` + `minor`): `KEY_MODE_MISMATCH` info emitted; key authoritative for the key line (P35) | silent conflict, or harmony overrides the explicit key line |
| W20c | Preview AND save both succeed despite the mismatch warning (P35) | warning escalates to rejection |
| W20d | Both operator values preserved exactly through preview/save/restore — no silent rewrite of `musical_key` or `harmony_mode` (P35) | either field normalized away or mutated to "resolve" the conflict |
| W21 | Legacy request with none of the new keys: valid, defaults applied, full pipeline succeeds (P47) | old clients broken |
| W22 | Contradiction suppression: low-glitch/low-drum blueprints emit no glitch/drum-peak directives in any genre (P14) | contradictory section text |
| W23 | Rollback proof (C5): WS1-schema model parses new-field JSON with 13 fields uncorrupted; re-serialization drops the 4 fields (documented limitation asserted, not hidden); stored snapshots restorable (P53) | rollback corrupts existing fields, or the limitation is undocumented/misstated |
| W24 | Bounds: oversize override/vocal/theme rejected 422, zero writes (P55) | oversized payload accepted |
| W25 | Scoring mode-awareness: none-mode ⇒ info not deficit; custom conflicts flagged; machine mode scoring unchanged in meaning (P28/P36) | operator choice punished as error |
| W26 | Platform neutrality (F5): blueprint schema and PromptPlan contain no platform-specific fields; captions are display-only per P41 (Suno "Style Description"/"Exclude Styles", Udio "Prompt/Tags"/"Style Reduction") | a platform-specific field appears in blueprint/plan, or captions leak into persisted data |
| W27 | Descriptor refinement (P39): executes **all six fixed pairs** — energy 61/84, bass_aggression 30/55, glitch_density 25/45, drum_intensity 55/75, atmosphere_depth 55/75, harmony_complexity 45/70 — proving each pair was bucket-identical under the frozen Phase-A WS1 characterization AND becomes descriptor-distinct under WS2; repeated output per input is byte-identical; varying one dimension leaves all other blueprint fields untouched; distinction does not rely on inserting raw slider numbers; all six dimensions are represented in the golden matrix across supported genres | any of the six dimensions remains coarse-bucket identical; a pair lacks its historical characterization fixture; output is nondeterministic; distinction relies only on numeric injection; a dimension is absent from golden coverage |
| W28 | Whitespace normalization & applicability (P29/P30): whitespace-only `vocal_style` and whitespace-only `lyric_theme` each normalize to `""`; normalized-empty vocal fields do **not** activate operator-driven vocal direction; normalized values persist deterministically through preview/save/restore; over-bound inputs still produce 422 with zero writes | whitespace alone activates vocal direction; normalization is inconsistent across preview/save/restore; whitespace input bypasses validation or bound checks |

## 21. Acceptance gate

- **P56 [E/F6]** All of W1–W28 (including all lettered sub-tests) plus the full WS1 suite green; `next build` succeeds; **lint fully green** (the H1 prerequisite fixes the inherited `PresetBrowser.jsx:77` error, so WS2 CI lint starts and must stay clean); import-no-DB probe clean; live-DB fingerprint byte-identical before/after all verification; before/after prompt exemplars for all four genres (and a vocal-phrase case) attached to the PR; **H1 CI checks green on the WS2 PR**.
- **P57 [E]** Independent adversarial gate before push/PR, preceded by the **model-identity preflight as the first message of a fresh session**.

## 22. Explicit exclusions

- **P58 [E]** Out of scope, individually binding: MP3→blueprint ingestion (R16); lineage-tree UI / v0.4 roadmap; drift redesign; new generation platforms; lyrics editor; timeline editing UI; preset management; auth/cloud/multi-user (R12); snapshot pruning; DB schema migration; H1 hardening items (D6/F6 — prerequisite workstream, outside WS2 implementation scope); wholesale analyzer or scoring redesign (D7); any platform rule without §24 evidence (D2).

## 23. Prerequisite and deferred work

- **P59 [D6/F6 — ratified]** **H1 hardening workstream is a PREREQUISITE: it must be completed (separate branch + PR, merged) before WS2 implementation begins**, so the engine-heavy WS2 PR receives real CI feedback. H1 scope (and nothing more):
  1. GitHub Actions workflow: backend pytest, frontend Vitest, frontend production build, frontend lint.
  2. Request-level typed-500 test.
  3. Portable replacement for the Windows-specific `Path("C:/")` fixture in `test_db_resolver.py`, preserving the resolver invariant under test.
  4. Fix the single inherited `PresetBrowser.jsx:77` lint error with the smallest behavior-neutral change (required CI lint cannot start green while it remains).
  H1 exclusions: no prompt-engine work; no lifecycle redesign; no database migration; no first-save retry refactor; no unrelated formatting or dependency upgrades. The first-save retry concern remains deferred until a supported reachable failure is demonstrated. H1 is **not** part of the WS2 product contract; WS2's P56 acceptance depends on H1's CI being in place.
- **P60** Future (deferred beyond WS2): renderer tuning against deeper platform research; instrumental thematic direction as a distinct field if ever wanted (per F1, `lyric_theme` stays strictly lyrical); WS3 candidate = lineage-tree UI; WS4 = governance/drift.

## 24. Platform-evidence appendix (D2)

All sources accessed **2026-07-13**. Strength: **A** = fetched directly from the official page; **B** = official-source search snippet, page fetch did not itemize the specific claim.

| ID | Source (official) | Claim supported | Strength |
|---|---|---|---|
| S1 | https://help.suno.com/en/articles/5782849 — "Create in V4.5: Detailed Style Instructions" | Suno V4.5 style field supports detailed conversational style instructions (genre, emotional qualities, textures, production elements, structural guidance) beyond terse comma descriptors; **no character limit documented** | A |
| S2 | https://help.suno.com/en/articles/3161921 — "How do I exclude elements of a song?" | Exclude field in Advanced Options (Custom Mode): "Enter any information (instruments, etc) that you do not want in your track"; no syntax/limits documented | A |
| S3 | https://suno.com/release-notes/exclude-styles | Exclude Styles: exclude instruments/styles/vocal-styles; exclusions displayed as `-piano`-style entries; Pro/Premier tiers noted | B |
| S4 | https://help.suno.com/en/articles/5782977 — "Create in V4.5: Better Prompts in Lyrics" | Suno supports "adding more context for your songs directly in the Lyrics box"; style field recommended for genre, extra context in Lyrics; specific bracket-tag vocabulary **not** itemized on the fetched page | A (bracket examples like `[female vocals]`: B) |
| U1 | https://help.udio.com/en/articles/10716541 — "Prompt Like a Master" | Udio prompt = free-form topic text + comma-separated genre/tags, combinable ("A song about summer rain, jazz, mellow, warm…"); autocomplete tag suggestions; **no character limit documented** | A |
| U2 | same article | "Describe the genre, mood, tempo, instruments, and theme in detail" | A |
| U3 | same article | Style Reduction / advanced controls to "minimize unwanted elements" (negative prompting) | A |
| U4 | https://help.udio.com/en/articles/11166249 — "Level up your creations with 'guidance tags'" | Documented lyrics-editor guidance tags: `[Verse] [Chorus] [Intro] [Outro] [Bridge] [Solo] [Ensemble] [Choir] [Spoken Word] [Instrumental Break] [Drop]`; `/` tag picker; explicit adherence caveat ("the AI makes the ultimate decisions") | A |
| U5 | https://help.udio.com/en/articles/10716221 — "Create a Song with Your Own Lyrics" | Custom Lyrics editor exists ("Type or paste your lyrics into the Lyrics Editor"); Manual/exact-tags mode referenced | A |
| X1 | *(excluded)* https://suno.com/embed/d2e95463-9018-445a-85d4-8eb1dd117fcb — user embed claiming 3000-char lyrics limit | **Not used** — user content, not official; per D2 no limit rule derived from it | — |

**Non-findings that shaped the contract [R]:** no official character limits for Suno style/lyrics/exclude or Udio prompt/lyrics were found ⇒ P7/P37 forbid limit rules; Suno bracket-tag vocabulary is not officially itemized ⇒ Suno sections use plain descriptive bracket labels (deliberate design, P21), while Udio sections prefer the documented U4 vocabulary.
