import { create } from 'zustand';
import { useProjectStore } from './projectStore';

const BACKEND_URL = 'http://localhost:8000';

export const usePresetStore = create((set, get) => ({
  presets: [],
  selectedPresetId: null,
  activeBank: 'BANK_A',
  isLoading: false,
  error: null,

  setActiveBank: (bank) => set({ activeBank: bank }),

  fetchPresets: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${BACKEND_URL}/api/presets`);
      if (!response.ok) throw new Error('Failed to load presets');
      const data = await response.json();
      // R28: do NOT auto-select a preset; the session starts unbound as CUSTOM.
      set({ presets: data, isLoading: false });
    } catch (err) {
      set({ error: err.message, isLoading: false });
    }
  },

  selectPreset: (id) => {
    const preset = get().presets.find((p) => p.id === id);
    if (preset) {
      set({ selectedPresetId: id });
      // Lineage attribution is stamped at bind time (R8), not re-derived per request.
      useProjectStore.getState().bindToPreset(preset);
    }
  },

  savePreset: async (name) => {
    const blueprint = useProjectStore.getState().workingBlueprint;
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${BACKEND_URL}/api/presets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, bank: get().activeBank, blueprint }),
      });
      if (!response.ok) throw new Error('Failed to save preset');
      const newPreset = await response.json();
      await get().fetchPresets();
      set({ selectedPresetId: newPreset.id });
      return true;
    } catch (err) {
      set({ error: err.message, isLoading: false });
      return false;
    }
  },
}));
