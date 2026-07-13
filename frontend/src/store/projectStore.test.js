import { beforeEach, afterEach, describe, it, expect, vi } from 'vitest';
import { useProjectStore, canonicalKey, PREVIEW_MAX_WAIT_MS } from './projectStore';

const store = useProjectStore;

function previewBody(reqBody) {
  const rev = JSON.parse(reqBody).client_revision;
  return {
    prompts: {
      suno: { style_tags: `s${rev}`, prompt_body: 'b', negative_prompt: 'n' },
      udio: { tags: `t${rev}`, prompt_body: 'b', negative_prompt: 'n' },
    },
    motif_block: `preview-motif-${rev}`,
    arrangement_timeline: [{ phase: 'Intro' }],
    scores: { overall: 90 },
    recommendations: [{ code: 'PREVIEW', target: 'bpm' }],
    client_revision: rev,
  };
}

function savedRecord(reqBody, over = {}) {
  const bp = JSON.parse(reqBody).blueprint;
  return {
    snapshot_id: 'CUSTOM_0001', lineage_key: 'lk-1', lineage_display: 'CUSTOM', version: 1,
    parent_snapshot_id: null, origin_type: 'custom', origin_ref: null, blueprint: bp,
    prompts: { suno: { style_tags: 'SAVED', prompt_body: 'b', negative_prompt: 'n' },
               udio: { tags: 'SAVED', prompt_body: 'b', negative_prompt: 'n' } },
    scores: { overall: 91 }, recommendations: [{ code: 'SAVED', target: 'genre' }],
    motif_block: 'saved-motif', arrangement_timeline: [{ phase: 'Saved' }],
    engine_version: '1.0.0-ws1', artifacts_provenance: 'STORED', created_at: '2026-07-13T10:00:00Z',
    ...over,
  };
}

function jsonResponse(obj) {
  return { ok: true, json: async () => obj };
}

beforeEach(() => {
  vi.useFakeTimers();
  store.getState().__resetForTest();
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});


// --- T13: rapid edits coalesce into one trailing request for the final blueprint ---
it('T13: debounce coalesces to one request with the final blueprint', async () => {
  global.fetch = vi.fn(async (url, opts) => jsonResponse(previewBody(opts.body)));
  store.getState().setBlueprintField('bpm', 100);
  store.getState().setBlueprintField('bpm', 101);
  store.getState().setBlueprintField('bpm', 102);
  await vi.advanceTimersByTimeAsync(300);
  expect(global.fetch).toHaveBeenCalledTimes(1);
  const body = JSON.parse(global.fetch.mock.calls[0][1].body);
  expect(body.bpm).toBe(102);
});


// --- T15: max-wait guarantees a preview during a sustained burst; trailing guarantees the last ---
it('T15: max-wait fires during a sustained burst even as trailing resets', async () => {
  global.fetch = vi.fn(async (url, opts) => jsonResponse(previewBody(opts.body)));
  for (let i = 0; i < 5; i++) {
    store.getState().setBlueprintField('bpm', 120 + i);
    await vi.advanceTimersByTimeAsync(250); // < 300, so trailing never fires between edits
  }
  // A preview must have fired by the max-wait boundary.
  expect(global.fetch).toHaveBeenCalled();
  expect(vi.getTimerCount()).toBeGreaterThanOrEqual(0);
});

it('T15b: guaranteed trailing preview after a burst carries the latest blueprint', async () => {
  global.fetch = vi.fn(async (url, opts) => jsonResponse(previewBody(opts.body)));
  store.getState().setBlueprintField('energy', 50);
  store.getState().setBlueprintField('energy', 55);
  await vi.advanceTimersByTimeAsync(PREVIEW_MAX_WAIT_MS + 50);
  const lastBody = JSON.parse(global.fetch.mock.calls.at(-1)[1].body);
  expect(lastBody.energy).toBe(55);
});


// --- T14: a stale (older-revision) response never overwrites newer state ---
it('T14: stale preview response is discarded by the revision guard', async () => {
  const deferred = {};
  global.fetch = vi.fn((url, opts) => new Promise((resolve) => {
    const rev = JSON.parse(opts.body).client_revision;
    deferred[rev] = () => resolve(jsonResponse(previewBody(opts.body)));
  }));
  store.getState().setBlueprintField('bpm', 100); // rev 2
  await vi.advanceTimersByTimeAsync(300);          // issues preview for rev 2
  const rev2 = store.getState().revision;
  store.getState().setBlueprintField('bpm', 101); // rev 3
  await vi.advanceTimersByTimeAsync(300);          // issues preview for rev 3
  const rev3 = store.getState().revision;
  expect(rev3).toBeGreaterThan(rev2);
  // Resolve the OLDER response last.
  deferred[rev3]();
  await vi.advanceTimersByTimeAsync(0);
  deferred[rev2]();
  await vi.advanceTimersByTimeAsync(0);
  // Displayed preview reflects rev3, not the late rev2 response.
  expect(store.getState().previewArtifacts.issuedRevision).toBe(rev3);
});


// --- T17 / T22: dirty/clean by canonical hash; edit-and-revert returns to clean ---
it('T22: edit then revert returns to clean and disables save', async () => {
  global.fetch = vi.fn(async (url, opts) => jsonResponse(previewBody(opts.body)));
  // Bind to a saved snapshot so there is a clean baseline with bound artifacts.
  store.getState().__resetForTest({
    boundSnapshotId: 'CUSTOM_0001', boundBlueprint: { ...store.getState().workingBlueprint },
    boundKey: canonicalKey(store.getState().workingBlueprint),
    boundArtifacts: { prompts: { suno: {}, udio: {} }, motif_block: 'BOUND', arrangement_timeline: [], scores: { overall: 88 }, recommendations: [] },
    boundProvenance: 'STORED',
    lineage: { key: 'lk', displayName: 'X', originType: 'snapshot', originRef: 'CUSTOM_0001', parentSnapshotId: 'CUSTOM_0001' },
  });
  const original = store.getState().workingBlueprint.bpm;
  store.getState().setBlueprintField('bpm', original + 10);
  expect(store.getState().isDirty).toBe(true);
  expect(store.getState().canSave()).toBe(true);
  store.getState().setBlueprintField('bpm', original); // revert
  expect(store.getState().isDirty).toBe(false);
  expect(store.getState().canSave()).toBe(false);
});


// --- T31: a clean snapshot-bound state shows byte-identical bound artifacts ---
it('T31: edit-and-revert restores exact bound artifacts, no preview applied over clean bound', async () => {
  global.fetch = vi.fn(async (url, opts) => jsonResponse(previewBody(opts.body)));
  const bound = { prompts: { suno: { style_tags: 'EXACT' }, udio: {} }, motif_block: 'EXACT-MOTIF', arrangement_timeline: [{ phase: 'Bound' }], scores: { overall: 77 }, recommendations: [{ code: 'BOUND' }] };
  store.getState().__resetForTest({
    boundSnapshotId: 'S1', boundBlueprint: { ...store.getState().workingBlueprint },
    boundKey: canonicalKey(store.getState().workingBlueprint),
    boundArtifacts: bound, boundProvenance: 'LEGACY_RECONSTRUCTED',
    lineage: { key: 'lk', displayName: 'X', originType: 'snapshot', originRef: 'S1', parentSnapshotId: 'S1' },
    displayed: { ...bound, provenance: 'LEGACY_RECONSTRUCTED', status: 'bound' },
  });
  const original = store.getState().workingBlueprint.bpm;
  store.getState().setBlueprintField('bpm', original + 5);
  await vi.advanceTimersByTimeAsync(400); // a preview would resolve here for the dirty state
  store.getState().setBlueprintField('bpm', original); // revert -> clean bound
  await vi.advanceTimersByTimeAsync(400);
  const d = store.getState().displayed;
  expect(d.motif_block).toBe('EXACT-MOTIF');
  expect(d.provenance).toBe('LEGACY_RECONSTRUCTED');
  expect(d.status).toBe('bound');
});


// --- T16: restore adopts artifacts, rebinds lineage, schedules no preview ---
it('T16: restore adopts artifacts, rebinds lineage, clean, no preview', async () => {
  global.fetch = vi.fn(async (url) => {
    if (String(url).includes('/api/snapshots/')) {
      return jsonResponse(savedRecord(JSON.stringify({ blueprint: { ...store.getState().workingBlueprint, bpm: 200 } }),
        { snapshot_id: 'PSYCH_TEC_0002', lineage_key: 'legacy:PSYCH_TEC', lineage_display: 'PSYCH_TEC',
          motif_block: 'RESTORED', artifacts_provenance: 'STORED' }));
    }
    return jsonResponse(previewBody('{"client_revision":0}'));
  });
  const rec = await store.getState().restoreSnapshot('PSYCH_TEC_0002');
  expect(rec.snapshot_id).toBe('PSYCH_TEC_0002');
  const st = store.getState();
  expect(st.boundSnapshotId).toBe('PSYCH_TEC_0002');
  expect(st.lineage.key).toBe('legacy:PSYCH_TEC');
  expect(st.lineage.originType).toBe('snapshot');
  expect(st.isDirty).toBe(false);
  expect(st.displayed.motif_block).toBe('RESTORED');
  await vi.advanceTimersByTimeAsync(400);
  // Only the restore GET happened; no preview POST was scheduled.
  const previewCalls = global.fetch.mock.calls.filter((c) => String(c[0]).includes('/api/preview'));
  expect(previewCalls.length).toBe(0);
});


// --- T29: edits during save are preserved; T23: save response replaces preview ---
it('T29/T23: edit during save preserved; save adoption does not clobber post-click edits', async () => {
  let resolveSave;
  global.fetch = vi.fn((url, opts) => {
    if (String(url).includes('/api/snapshots') && opts && opts.method === 'POST') {
      return new Promise((resolve) => { resolveSave = () => resolve(jsonResponse(savedRecord(opts.body))); });
    }
    if (String(url).includes('/api/snapshots?')) return jsonResponse({ items: [], total: 0, next_cursor: null });
    return jsonResponse(previewBody(opts.body));
  });
  const before = store.getState().workingBlueprint.bpm;
  const savePromise = store.getState().saveSnapshot('Proj');
  // Operator edits to B during the in-flight save.
  store.getState().setBlueprintField('bpm', before + 42);
  resolveSave();
  await savePromise;
  const st = store.getState();
  // Working state is still B (never overwritten by captured/returned A).
  expect(st.workingBlueprint.bpm).toBe(before + 42);
  expect(st.boundSnapshotId).toBe('CUSTOM_0001');
  expect(st.isDirty).toBe(true); // B differs from the saved base
  expect(st.lineage.parentSnapshotId).toBe('CUSTOM_0001'); // parent advanced (R19)
});

it('T23b: save with no edits adopts the returned record and becomes clean', async () => {
  global.fetch = vi.fn((url, opts) => {
    if (String(url).includes('/api/snapshots') && opts && opts.method === 'POST') {
      return jsonResponse(savedRecord(opts.body));
    }
    if (String(url).includes('/api/snapshots?')) return jsonResponse({ items: [], total: 0, next_cursor: null });
    return jsonResponse(previewBody(opts.body));
  });
  const rec = await store.getState().saveSnapshot('Proj');
  const st = store.getState();
  expect(rec.snapshot_id).toBe('CUSTOM_0001');
  expect(st.isDirty).toBe(false);
  expect(st.displayed.prompts.suno.style_tags).toBe('SAVED'); // returned artifacts shown
  expect(st.displayed.provenance).toBe('STORED');
  expect(st.canSave()).toBe(false); // R25: disabled after save while unchanged
});


// --- Sequential parent chain uses snapshot origin after the first save ---
it('after save, lineage becomes snapshot-origin for the next descendant', async () => {
  global.fetch = vi.fn((url, opts) => {
    if (String(url).includes('/api/snapshots') && opts && opts.method === 'POST') {
      return jsonResponse(savedRecord(opts.body));
    }
    if (String(url).includes('/api/snapshots?')) return jsonResponse({ items: [], total: 0, next_cursor: null });
    return jsonResponse(previewBody(opts.body));
  });
  await store.getState().saveSnapshot('Proj');
  const lin = store.getState().lineage;
  expect(lin.originType).toBe('snapshot');
  expect(lin.originRef).toBe('CUSTOM_0001');
  expect(lin.parentSnapshotId).toBe('CUSTOM_0001');
  expect(lin.key).toBe('lk-1');
});


// --- T19: a failed preview preserves prior valid preview artifacts ---
it('T19: failed preview retains prior artifacts, exposes error, fabricates nothing', async () => {
  let mode = 'ok';
  global.fetch = vi.fn((url, opts) => {
    if (mode === 'fail') return Promise.reject(new Error('network down'));
    return Promise.resolve(jsonResponse(previewBody(opts.body)));
  });
  // Preview A succeeds and installs valid artifacts.
  store.getState().setBlueprintField('bpm', 100);
  await vi.advanceTimersByTimeAsync(350);
  const aRev = store.getState().revision;
  const aArtifacts = store.getState().previewArtifacts;
  expect(aArtifacts).toBeTruthy();
  expect(aArtifacts.issuedRevision).toBe(aRev);
  expect(store.getState().displayed.motif_block).toBe(`preview-motif-${aRev}`);
  expect(store.getState().displayed.status).toBe('live');

  // The next preview fails.
  mode = 'fail';
  store.getState().setBlueprintField('bpm', 101);
  await vi.advanceTimersByTimeAsync(350);

  const st = store.getState();
  // A's artifacts are exactly preserved (same object; nothing fabricated/partial).
  expect(st.previewArtifacts).toBe(aArtifacts);
  expect(st.previewArtifacts.issuedRevision).toBe(aRev);
  // Error state exposed.
  expect(st.previewStatus).toBe('error');
  // Displayed still surfaces A's artifacts, flagged not-live (never as fresh output for the new edit).
  expect(st.displayed.motif_block).toBe(`preview-motif-${aRev}`);
  expect(st.displayed.status).toBe('error');
});


// --- T30: an in-flight save of A never presents A as belonging to newer state B ---
it('T30: stale/interim save of A is never attributed to newer state B', async () => {
  let resolveSave;
  global.fetch = vi.fn((url, opts) => {
    if (String(url).includes('/api/snapshots') && opts && opts.method === 'POST') {
      return new Promise((res) => { resolveSave = () => res(jsonResponse(savedRecord(opts.body))); });
    }
    if (String(url).includes('/api/snapshots?')) return Promise.resolve(jsonResponse({ items: [], total: 0, next_cursor: null }));
    return Promise.resolve(jsonResponse(previewBody(opts.body)));
  });

  const before = store.getState().workingBlueprint.bpm;
  const savePromise = store.getState().saveSnapshot('Proj'); // save A captured
  // Move the store to state B before A resolves.
  store.getState().setBlueprintField('bpm', before + 50);
  const revB = store.getState().revision;

  // A's save resolves.
  resolveSave();
  await savePromise;

  const st = store.getState();
  // Working state is B, never replaced by captured/returned A.
  expect(st.workingBlueprint.bpm).toBe(before + 50);
  // A is bound as the new base, but state is dirty vs B, so A is NOT shown as B's final output.
  expect(st.boundSnapshotId).toBe('CUSTOM_0001');
  expect(st.isDirty).toBe(true);
  expect(st.displayed.status).toBe('pending');   // interim: flagged, not attributed to B as final
  expect(st.displayed.status).not.toBe('bound');
  // Parent advanced to A (R19); next descendant will chain from A.
  expect(st.lineage.parentSnapshotId).toBe('CUSTOM_0001');
  expect(st.lineage.originType).toBe('snapshot');

  // B's own preview then resolves and applies for the CURRENT revision only.
  await vi.advanceTimersByTimeAsync(350);
  const st2 = store.getState();
  expect(st2.previewArtifacts).toBeTruthy();
  expect(st2.previewArtifacts.issuedRevision).toBe(st2.revision);
  expect(st2.previewArtifacts.issuedRevision).toBeGreaterThanOrEqual(revB);
});
