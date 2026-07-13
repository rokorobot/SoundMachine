import { create } from 'zustand';

export const useUiStore = create((set) => ({
  // R26: previewModel is a VIEW concern only. Switching the visible Suno/Udio
  // tab must never bump revision or dirty the working blueprint.
  previewModel: 'suno', // 'suno' or 'udio'
  activeExportMode: 'txt',
  notification: null,
  showSaveDialog: false,

  setPreviewModel: (model) => set({ previewModel: model }),
  setActiveExportMode: (mode) => set({ activeExportMode: mode }),
  setShowSaveDialog: (show) => set({ showSaveDialog: show }),

  showNotification: (message, type = 'success') => {
    set({ notification: { message, type } });
    setTimeout(() => {
      set({ notification: null });
    }, 4000);
  },

  clearNotification: () => set({ notification: null }),
}));
