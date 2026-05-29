import { create } from 'zustand';

const BACKEND_URL = 'http://localhost:8000';

const DEFAULT_BLUEPRINT = {
  genre: "psycho_glitch_techno",
  bpm: 132,
  energy: 90,
  motif_type: "cathedral organ",
  motif_presence: 50,
  motif_behavior: "fragmenting",
  harmony_mode: "minor",
  harmony_complexity: 60,
  bass_aggression: 80,
  glitch_density: 95,
  drum_intensity: 85,
  atmosphere_depth: 40,
  target_model: "suno"
};

export const useProjectStore = create((set, get) => ({
  blueprint: { ...DEFAULT_BLUEPRINT },
  generatedPrompts: null,
  motifBlock: "",
  arrangementTimeline: [],
  scores: null,
  recommendations: [],
  isGenerating: false,
  error: null,

  // Snapshots history state
  snapshots: [],
  activeSnapshotId: null,

  // Compare mode state
  referenceBlueprint: null,
  comparisonResult: null,
  driftScore: 0,
  driftClassification: 'Nearly identical',

  setBlueprintField: (field, value) => {
    set((state) => ({
      blueprint: {
        ...state.blueprint,
        [field]: value
      }
    }));
    get().generatePrompts();
  },

  setFullBlueprint: (newBlueprint) => {
    set({ blueprint: { ...newBlueprint } });
    get().generatePrompts();
  },

  setReferenceBlueprint: () => {
    const current = get().blueprint;
    set({ referenceBlueprint: current });
    get().runComparison();
  },

  setReferenceBlueprintFromSnapshot: (snapBlueprint) => {
    set({ referenceBlueprint: snapBlueprint });
    get().runComparison();
  },

  clearReferenceBlueprint: () => {
    set({ 
      referenceBlueprint: null, 
      comparisonResult: null,
      driftScore: 0,
      driftClassification: 'Nearly identical'
    });
  },

  runComparison: async () => {
    const { referenceBlueprint, blueprint } = get();
    if (!referenceBlueprint) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          blueprint_a: referenceBlueprint,
          blueprint_b: blueprint
        })
      });

      if (!response.ok) {
        throw new Error('Comparison API request failed');
      }

      const data = await response.json();

      const PARAMS = [
        'genre', 'bpm', 'energy', 'motif_type', 'motif_presence',
        'motif_behavior', 'harmony_mode', 'harmony_complexity',
        'bass_aggression', 'glitch_density', 'drum_intensity',
        'atmosphere_depth', 'target_model'
      ];

      let driftScore = 0;
      let driftClassification = 'Nearly identical';
      let totalDrift = 0;
      const count = PARAMS.length;

      PARAMS.forEach(key => {
        const diffObj = data.diff?.[key];
        if (diffObj) {
          if (typeof diffObj.delta === 'number') {
            const range = key === 'bpm' ? 200 : 100;
            totalDrift += Math.abs(diffObj.delta) / range;
          } else {
            totalDrift += 0.4;
          }
        }
      });

      driftScore = Math.round((totalDrift / count) * 100);
      if (driftScore > 50) driftClassification = 'New blueprint';
      else if (driftScore > 25) driftClassification = 'Significant mutation';
      else if (driftScore > 10) driftClassification = 'Minor variation';

      set({ 
        comparisonResult: data,
        driftScore,
        driftClassification
      });
    } catch (err) {
      console.error("Comparison error:", err);
    }
  },

  fetchSnapshots: async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/snapshots`);
      if (response.ok) {
        const data = await response.json();
        set({ snapshots: data });
      }
    } catch (err) {
      console.error("Failed to fetch snapshots", err);
    }
  },

  restoreSnapshot: async (snapshotId) => {
    set({ isGenerating: true, error: null });
    try {
      const response = await fetch(`${BACKEND_URL}/api/snapshots/${snapshotId}/restore`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Failed to restore snapshot');
      }
      const data = await response.json();
      set({
        blueprint: data.blueprint,
        generatedPrompts: data.prompts,
        motifBlock: data.motif_block,
        arrangementTimeline: data.arrangement_timeline,
        scores: data.scores,
        recommendations: [], // Clear active suggestions until next tweak
        activeSnapshotId: data.snapshot_id,
        isGenerating: false
      });

      // If reference is locked, auto-trigger comparison
      if (get().referenceBlueprint) {
        get().runComparison();
      }
    } catch (err) {
      console.error("Restore error:", err);
      set({ error: err.message, isGenerating: false });
    }
  },

  generatePrompts: async () => {
    const { blueprint, isGenerating } = get();
    if (isGenerating) return;

    set({ isGenerating: true, error: null });

    // Dynamically require presetStore to avoid circular dependency
    let parent_preset_name = "CUSTOM";
    let parent_preset_id = null;
    try {
      const { usePresetStore } = require('./presetStore');
      const presetState = usePresetStore.getState();
      const activePreset = presetState.presets.find(p => p.id === presetState.selectedPresetId);
      if (activePreset) {
        parent_preset_name = activePreset.name;
        parent_preset_id = activePreset.id;
      }
    } catch (e) {
      // Safe fallback
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...blueprint,
          parent_preset_name,
          parent_preset_id
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate prompts: ${response.statusText}`);
      }

      const data = await response.json();
      set({ 
        generatedPrompts: data.prompts,
        motifBlock: data.motif_block,
        arrangementTimeline: data.arrangement_timeline,
        scores: data.scores,
        recommendations: data.recommendations,
        activeSnapshotId: data.snapshot_id,
        isGenerating: false 
      });

      // Auto-trigger comparison if a reference is locked
      if (get().referenceBlueprint) {
        get().runComparison();
      }

      // Auto-refresh snapshot list
      get().fetchSnapshots();
    } catch (err) {
      console.error(err);
      set({ error: err.message, isGenerating: false });
    }
  },

  exportCurrent: async (presetName = "Custom Preset") => {
    const { blueprint, generatedPrompts } = get();
    if (!generatedPrompts) return null;

    try {
      const response = await fetch(`${BACKEND_URL}/api/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          preset_name: presetName,
          blueprint,
          prompts: generatedPrompts,
          target_model: blueprint.target_model
        }),
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      return await response.json();
    } catch (err) {
      console.error(err);
      return null;
    }
  }
}));
