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
      if (!response.ok) {
        throw new Error('Failed to load presets');
      }
      const data = await response.json();
      set({ presets: data, isLoading: false });
      
      // Auto select first preset (e.g. Psych Tec) if nothing selected
      if (data.length > 0 && !get().selectedPresetId) {
        get().selectPreset(data[0].id);
      }
    } catch (err) {
      set({ error: err.message, isLoading: false });
    }
  },

  selectPreset: (id) => {
    const preset = get().presets.find(p => p.id === id);
    if (preset) {
      set({ selectedPresetId: id });
      // Update the active blueprint in the projectStore
      useProjectStore.getState().setFullBlueprint(preset.blueprint);
    }
  },

  savePreset: async (name) => {
    const blueprint = useProjectStore.getState().blueprint;
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${BACKEND_URL}/api/presets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          bank: get().activeBank,
          blueprint
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save preset');
      }

      const newPreset = await response.json();
      
      // Refresh list
      await get().fetchPresets();
      
      // Select the newly saved preset
      set({ selectedPresetId: newPreset.id });
      return true;
    } catch (err) {
      set({ error: err.message, isLoading: false });
      return false;
    }
  }
}));
