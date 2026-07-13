import { create } from 'zustand';

const BACKEND_URL = 'http://localhost:8000';

// Debounce constants (R30) — isolated and configurable.
export const PREVIEW_DEBOUNCE_MS = 300;   // trailing
export const PREVIEW_MAX_WAIT_MS = 1000;  // maximum wait during a sustained burst

const DEFAULT_BLUEPRINT = {
  genre: 'psycho_glitch_techno', bpm: 132, energy: 90, motif_type: 'cathedral organ',
  motif_presence: 50, motif_behavior: 'fragmenting', harmony_mode: 'minor',
  harmony_complexity: 60, bass_aggression: 80, glitch_density: 95, drum_intensity: 85,
  atmosphere_depth: 40, target_model: 'suno',
};

// Fixed field order — must match the backend canonical key (lineage.py).
const BLUEPRINT_FIELDS = [
  'genre', 'bpm', 'energy', 'motif_type', 'motif_presence', 'motif_behavior',
  'harmony_mode', 'harmony_complexity', 'bass_aggression', 'glitch_density',
  'drum_intensity', 'atmosphere_depth', 'target_model',
];

export function canonicalKey(bp) {
  return JSON.stringify(BLUEPRINT_FIELDS.map((f) => [f, bp[f]]));
}

const ARTIFACT_KEYS = ['prompts', 'motif_block', 'arrangement_timeline', 'scores', 'recommendations'];
function extractArtifacts(rec) {
  const out = {};
  for (const k of ARTIFACT_KEYS) out[k] = rec[k];
  return out;
}

// Module-level scheduler state (single store instance).
let trailingTimer = null;
let maxTimer = null;
let inFlightController = null;

function clearTimers() {
  if (trailingTimer) clearTimeout(trailingTimer);
  if (maxTimer) clearTimeout(maxTimer);
  trailingTimer = null;
  maxTimer = null;
}

function isCleanBound(st) {
  return st.boundSnapshotId !== null && canonicalKey(st.workingBlueprint) === st.boundKey;
}

function computeDisplayed(st) {
  // R38 rule 1: a clean snapshot-bound state shows its exact bound artifacts.
  if (st.boundSnapshotId !== null && !st.isDirty && st.boundArtifacts) {
    return { ...st.boundArtifacts, provenance: st.boundProvenance, status: 'bound' };
  }
  // rule 2: a preview generated for the current revision.
  if (st.previewArtifacts && st.previewArtifacts.issuedRevision === st.revision) {
    return { ...extractArtifacts(st.previewArtifacts), provenance: 'PREVIEW', status: 'live' };
  }
  // rule 3: pending/stale — show the most recent available, never as output for current edits.
  const fallback = st.previewArtifacts
    ? { ...extractArtifacts(st.previewArtifacts), provenance: 'PREVIEW' }
    : (st.boundArtifacts ? { ...st.boundArtifacts, provenance: st.boundProvenance } : null);
  if (!fallback) return null;
  return { ...fallback, status: st.previewStatus === 'error' ? 'error' : 'pending' };
}

export const useProjectStore = create((set, get) => {
  const refresh = (patch) => {
    set(patch);
    const st = get();
    set({ isDirty: canonicalKey(st.workingBlueprint) !== st.boundKey });
    set({ displayed: computeDisplayed(get()) });
  };

  async function issuePreview(issuedRevision) {
    if (inFlightController) inFlightController.abort();
    const controller = new AbortController();
    inFlightController = controller;
    set({ previewStatus: 'pending', displayed: computeDisplayed(get()) });
    const bp = get().workingBlueprint;
    try {
      const res = await fetch(`${BACKEND_URL}/api/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...bp, client_revision: issuedRevision }),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error('preview failed');
      const data = await res.json();
      const st = get();
      // Apply guard (R5 + R38): current revision AND not a clean snapshot-bound state.
      if (data.client_revision === st.revision && !isCleanBound(st)) {
        set({
          previewArtifacts: { ...data, issuedRevision: data.client_revision },
          previewStatus: 'idle',
        });
        set({ displayed: computeDisplayed(get()) });
      }
    } catch (e) {
      if (e && e.name === 'AbortError') return; // superseded; revision guard is authoritative
      if (issuedRevision === get().revision) {
        set({ previewStatus: 'error', previewError: 'Preview failed', displayed: computeDisplayed(get()) });
      }
    }
  }

  function schedulePreview() {
    // R38: never schedule a preview over a clean snapshot-bound state.
    if (isCleanBound(get())) { clearTimers(); return; }
    if (trailingTimer) clearTimeout(trailingTimer);
    const fire = () => { clearTimers(); issuePreview(get().revision); };
    trailingTimer = setTimeout(fire, PREVIEW_DEBOUNCE_MS);
    if (!maxTimer) maxTimer = setTimeout(fire, PREVIEW_MAX_WAIT_MS);
  }

  const initialDisplayed = null;

  return {
    // --- working state ---
    workingBlueprint: { ...DEFAULT_BLUEPRINT },
    revision: 1,
    isDirty: false,

    // --- binding ---
    boundSnapshotId: null,
    boundBlueprint: { ...DEFAULT_BLUEPRINT },
    boundKey: canonicalKey(DEFAULT_BLUEPRINT),
    boundArtifacts: null,
    boundProvenance: null,

    // R28: initial load is unbound CUSTOM.
    lineage: { key: null, displayName: 'CUSTOM', originType: 'custom', originRef: null, parentSnapshotId: null },

    // --- ephemeral preview ---
    previewArtifacts: null,
    previewStatus: 'idle',
    previewError: null,

    // --- save ---
    saveInFlight: null,
    saveError: null,

    // --- derived display (recomputed on each transition) ---
    displayed: initialDisplayed,

    // --- registry ---
    snapshots: [],
    snapshotsTotal: 0,
    snapshotsCursor: null,

    // --- calibration baseline / drift (existing feature, ported onto workingBlueprint;
    //     drift redesign remains Workstream 4, out of WS1 scope) ---
    referenceBlueprint: null,
    comparisonResult: null,
    driftScore: 0,
    driftClassification: 'Nearly identical',

    canSave: () => {
      const st = get();
      return st.boundSnapshotId === null || st.isDirty;
    },

    startInitialPreview: () => { schedulePreview(); },

    setBlueprintField: (field, value) => {
      refresh({
        workingBlueprint: { ...get().workingBlueprint, [field]: value },
        revision: get().revision + 1,
      });
      schedulePreview();
      if (get().referenceBlueprint) get().runComparison();
    },

    setFullBlueprint: (bp) => {
      refresh({ workingBlueprint: { ...bp }, revision: get().revision + 1 });
      schedulePreview();
      if (get().referenceBlueprint) get().runComparison();
    },

    bindToPreset: (preset) => {
      clearTimers();
      const bp = { ...preset.blueprint };
      refresh({
        workingBlueprint: bp,
        revision: get().revision + 1,
        boundSnapshotId: null,
        boundBlueprint: { ...bp },
        boundKey: canonicalKey(bp),
        boundArtifacts: null,
        boundProvenance: null,
        lineage: { key: null, displayName: preset.name, originType: 'preset', originRef: String(preset.id), parentSnapshotId: null },
        previewArtifacts: null,
        previewStatus: 'idle',
      });
      schedulePreview(); // preset-bound but never-saved uses live previews
    },

    restoreSnapshot: async (snapshotId) => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/snapshots/${snapshotId}`);
        if (!res.ok) { set({ previewError: 'Restore failed' }); return false; }
        const rec = await res.json();
        clearTimers();
        if (inFlightController) inFlightController.abort();
        const bp = { ...rec.blueprint };
        // R6/R7: adopt stored artifacts verbatim, rebind lineage, NO preview scheduled.
        refresh({
          workingBlueprint: bp,
          revision: get().revision + 1,
          boundSnapshotId: rec.snapshot_id,
          boundBlueprint: { ...bp },
          boundKey: canonicalKey(bp),
          boundArtifacts: extractArtifacts(rec),
          boundProvenance: rec.artifacts_provenance,
          lineage: { key: rec.lineage_key, displayName: rec.lineage_display, originType: 'snapshot', originRef: rec.snapshot_id, parentSnapshotId: rec.snapshot_id },
          previewArtifacts: null,
          previewStatus: 'idle',
        });
        return rec;
      } catch (e) {
        set({ previewError: 'Restore failed' });
        return false;
      }
    },

    saveSnapshot: async (displayNameOverride) => {
      const st = get();
      if (st.saveInFlight) return false;
      const captured = {
        blueprint: { ...st.workingBlueprint },
        key: canonicalKey(st.workingBlueprint),
        revision: st.revision,
        lineage: { ...st.lineage },
      };
      set({ saveInFlight: captured, saveError: null });
      const payload = {
        blueprint: captured.blueprint,
        lineage: {
          lineage_key: captured.lineage.key,
          display_name: displayNameOverride || captured.lineage.displayName,
          origin_type: captured.lineage.originType,
          origin_ref: captured.lineage.originRef,
          parent_snapshot_id: captured.lineage.parentSnapshotId,
        },
      };
      try {
        const res = await fetch(`${BACKEND_URL}/api/snapshots`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          let msg = 'Save failed';
          try { msg = (await res.json())?.error?.message || msg; } catch (_) {}
          set({ saveInFlight: null, saveError: msg });
          return false;
        }
        const rec = await res.json();
        // R19/R22: always bind the returned snapshot as the new base; advance parent.
        set((s) => ({
          boundSnapshotId: rec.snapshot_id,
          boundBlueprint: { ...rec.blueprint },
          boundKey: canonicalKey(rec.blueprint),
          boundArtifacts: extractArtifacts(rec),
          boundProvenance: rec.artifacts_provenance,
          lineage: { key: rec.lineage_key, displayName: rec.lineage_display, originType: 'snapshot', originRef: rec.snapshot_id, parentSnapshotId: rec.snapshot_id },
          revision: s.revision + 1,
          saveInFlight: null,
        }));
        // R37: never overwrite post-click edits.
        if (canonicalKey(get().workingBlueprint) === captured.key) {
          refresh({ previewArtifacts: null }); // no edits during flight -> adopt returned, clean
        } else {
          refresh({}); // recompute dirty vs the new boundKey
          schedulePreview(); // edited during flight -> one preview for the current working blueprint
        }
        get().fetchSnapshots();
        return rec;
      } catch (e) {
        set({ saveInFlight: null, saveError: 'Save failed' });
        return false;
      }
    },

    fetchSnapshots: async (opts = {}) => {
      try {
        const limit = opts.limit || 25;
        let url = `${BACKEND_URL}/api/snapshots?limit=${limit}`;
        if (opts.before_id) url += `&before_id=${opts.before_id}`;
        const res = await fetch(url);
        if (!res.ok) return;
        const page = await res.json();
        if (opts.append) {
          set((s) => ({ snapshots: [...s.snapshots, ...page.items], snapshotsTotal: page.total, snapshotsCursor: page.next_cursor }));
        } else {
          set({ snapshots: page.items, snapshotsTotal: page.total, snapshotsCursor: page.next_cursor });
        }
      } catch (e) { /* non-fatal */ }
    },

    exportCurrent: async (presetName = 'Custom Preset') => {
      const st = get();
      const displayed = st.displayed;
      if (!displayed || !displayed.prompts) return null;
      try {
        const res = await fetch(`${BACKEND_URL}/api/export`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            preset_name: presetName,
            blueprint: st.workingBlueprint,
            prompts: displayed.prompts,
            target_model: st.workingBlueprint.target_model,
          }),
        });
        if (!res.ok) return null;
        return await res.json();
      } catch (e) { return null; }
    },

    setReferenceBlueprint: () => {
      set({ referenceBlueprint: { ...get().workingBlueprint } });
      get().runComparison();
    },

    setReferenceBlueprintFromSnapshot: (snapBlueprint) => {
      set({ referenceBlueprint: { ...snapBlueprint } });
      get().runComparison();
    },

    clearReferenceBlueprint: () => {
      set({ referenceBlueprint: null, comparisonResult: null, driftScore: 0, driftClassification: 'Nearly identical' });
    },

    runComparison: async () => {
      const { referenceBlueprint, workingBlueprint } = get();
      if (!referenceBlueprint) return;
      try {
        const res = await fetch(`${BACKEND_URL}/api/compare`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ blueprint_a: referenceBlueprint, blueprint_b: workingBlueprint }),
        });
        if (!res.ok) return;
        const data = await res.json();
        let total = 0;
        for (const key of BLUEPRINT_FIELDS) {
          const diffObj = data.diff?.[key];
          if (diffObj) {
            if (typeof diffObj.delta === 'number') {
              const range = key === 'bpm' ? 200 : 100;
              total += Math.abs(diffObj.delta) / range;
            } else {
              total += 0.4;
            }
          }
        }
        const driftScore = Math.round((total / BLUEPRINT_FIELDS.length) * 100);
        let driftClassification = 'Nearly identical';
        if (driftScore > 50) driftClassification = 'New blueprint';
        else if (driftScore > 25) driftClassification = 'Significant mutation';
        else if (driftScore > 10) driftClassification = 'Minor variation';
        set({ comparisonResult: data, driftScore, driftClassification });
      } catch (e) { /* non-fatal */ }
    },

    // Test-only reset of module scheduler + state.
    __resetForTest: (overrides = {}) => {
      clearTimers();
      inFlightController = null;
      set({
        workingBlueprint: { ...DEFAULT_BLUEPRINT }, revision: 1, isDirty: false,
        boundSnapshotId: null, boundBlueprint: { ...DEFAULT_BLUEPRINT }, boundKey: canonicalKey(DEFAULT_BLUEPRINT),
        boundArtifacts: null, boundProvenance: null,
        lineage: { key: null, displayName: 'CUSTOM', originType: 'custom', originRef: null, parentSnapshotId: null },
        previewArtifacts: null, previewStatus: 'idle', previewError: null,
        saveInFlight: null, saveError: null, displayed: null,
        snapshots: [], snapshotsTotal: 0, snapshotsCursor: null,
        referenceBlueprint: null, comparisonResult: null, driftScore: 0, driftClassification: 'Nearly identical',
        ...overrides,
      });
    },
  };
});
