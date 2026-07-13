# Changelog

## v0.4.0 — Workstream 1: Generation, Snapshot, Restore & Lineage Lifecycle

### Breaking API changes

The following endpoints were **removed**. Update any external clients.

| Removed endpoint | Replacement |
| --- | --- |
| `POST /api/generate` | `POST /api/preview` for non-persistent generation, then `POST /api/snapshots` to persist an explicit, immutable snapshot. Generation and persistence are now separate steps. |
| `POST /api/analyze-prompt` | `POST /api/preview` — the preview response includes `scores` and `recommendations`. |
| `POST /api/snapshots/{id}/restore` | `GET /api/snapshots/{id}` — restoration is a read; the client adopts the returned record. No server-side mutation occurs on restore. |

### Added

- `POST /api/preview` — non-persistent live preview (zero database writes).
- `POST /api/snapshots` — server-authoritative, atomic, immutable snapshot save with explicit lineage metadata.
- `GET /api/snapshots` — cursor-paginated registry (`limit`, `before_id`); single query, no per-row growth.
- `GET /api/snapshots/{id}` — full snapshot record; legacy rows return reconstructed
  motif/timeline/recommendations disclosed as `LEGACY_RECONSTRUCTED` (not historical output).

### Changed

- Snapshots are now created **only** by an explicit Save action; live preview never persists.
- Blueprint fields are enum-validated; errors return a typed `{ "error": { "code", "message" } }` envelope.
- Timestamps serialize as UTC with a trailing `Z`.
- Removed the unsupported Suno 120-character assumption; vocal-phrase machine-owned negative
  prompts are no longer flagged as a deficit.

See `docs/workstream-1-lifecycle-contract.md` for the full ratified contract.
