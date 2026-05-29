import { create } from 'zustand';

export const useUiStore = create((set) => ({
  activeModel: 'suno', // 'suno' or 'udio'
  activeExportMode: 'txt', // 'txt' or 'json'
  notification: null,
  showSaveDialog: false,

  setActiveModel: (model) => set({ activeModel: model }),
  setActiveExportMode: (mode) => set({ activeExportMode: mode }),
  setShowSaveDialog: (show) => set({ showSaveDialog: show }),
  
  showNotification: (message, type = 'success') => {
    set({ notification: { message, type } });
    setTimeout(() => {
      set({ notification: null });
    }, 4000);
  },
  
  clearNotification: () => set({ notification: null })
}));
