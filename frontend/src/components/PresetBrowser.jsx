'use client';

import React from 'react';
import { usePresetStore } from '../store/presetStore';
import { useUiStore } from '../store/uiStore';
import { Layers, Radio } from 'lucide-react';

const BANKS = [
  { id: 'BANK_A', name: 'Core', desc: 'Core production blueprints establishing the system baseline.' },
  { id: 'BANK_B', name: 'RokoRobo', desc: 'Factory presets derived from signature RokoRobo track systems.' },
  { id: 'BANK_C', name: 'Motif Lab', desc: 'Focused blueprints designed to stress-test the Motif Engine.' },
  { id: 'BANK_D', name: 'Industrial', desc: 'Industrial-grade techno setups emphasizing density and pressure.' },
  { id: 'BANK_E', name: 'Coldwave', desc: 'Minimal synth wave foundations with cold mechanical grooves.' },
  { id: 'BANK_F', name: 'Experimental', desc: 'Abstract composition pathways pushing generative limits.' },
];

export default function PresetBrowser() {
  const { presets, selectedPresetId, selectPreset, activeBank, setActiveBank, isLoading } = usePresetStore();
  const { showNotification } = useUiStore();

  const handleSelect = (preset) => {
    selectPreset(preset.id);
    showNotification(`LOADED PROGRAM: ${preset.name.toUpperCase()}`, 'success');
  };

  if (isLoading) {
    return (
      <div className="border border-zinc-800 bg-zinc-950 p-6 rounded-lg shadow-2xl relative overflow-hidden flex items-center justify-center h-48">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(34,197,94,0.03),transparent)] pointer-events-none"></div>
        <div className="flex flex-col items-center space-y-2">
          <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs text-green-500 font-mono tracking-widest uppercase">Initializing deck...</span>
        </div>
      </div>
    );
  }

  const filteredPresets = presets.filter(p => p.bank === activeBank);
  const activeBankInfo = BANKS.find(b => b.id === activeBank) || BANKS[0];

  return (
    <div className="border border-zinc-800 bg-zinc-950/80 backdrop-blur p-5 rounded-lg shadow-2xl relative overflow-hidden flex flex-col h-full">
      {/* Grid Pattern Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)] bg-[size:1rem_1rem] opacity-30 pointer-events-none"></div>
      
      {/* Title Header */}
      <div className="relative z-10 flex items-center justify-between mb-3 border-b border-zinc-800 pb-2">
        <div className="flex items-center space-x-2">
          <Radio className="w-4 h-4 text-green-500 animate-pulse" />
          <h2 className="text-xs font-bold font-mono tracking-widest text-zinc-100 uppercase">PRESET BANKS</h2>
        </div>
        <span className="text-[9px] text-zinc-500 font-mono">v0.3.1</span>
      </div>

      {/* Bank Tabs Selector */}
      <div className="relative z-10 grid grid-cols-3 gap-1 mb-3">
        {BANKS.map((b) => {
          const isActive = b.id === activeBank;
          return (
            <button
              key={b.id}
              onClick={() => setActiveBank(b.id)}
              className={`py-1 px-1 text-[9px] font-mono border rounded transition-all truncate text-center ${
                isActive
                  ? 'bg-green-950/40 border-green-500/80 text-green-400 shadow-[0_0_8px_rgba(34,197,94,0.15)] font-bold'
                  : 'bg-zinc-900/40 border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700'
              }`}
            >
              {b.name.toUpperCase()}
            </button>
          );
        })}
      </div>

      {/* Bank Description Banner */}
      <div className="relative z-10 text-[9px] text-zinc-500 font-mono mb-3 uppercase tracking-wider leading-relaxed border-b border-zinc-900 pb-2">
        <span className="text-green-500/80 font-semibold">{activeBank}</span> // {activeBankInfo.desc}
      </div>

      {/* Preset Cards Grid (compact scrollable box) */}
      <div className="relative z-10 overflow-y-auto max-h-[175px] pr-1 flex-grow scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
        {filteredPresets.length === 0 ? (
          <div className="text-center py-6 text-[10px] font-mono text-zinc-600 uppercase tracking-widest">
            No presets found in this bank
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            {filteredPresets.map((preset) => {
              const isSelected = preset.id === selectedPresetId;
              const genreLabel = preset.blueprint.genre.replace(/_/g, ' ').toUpperCase();
              
              return (
                <button
                  key={preset.id}
                  onClick={() => handleSelect(preset)}
                  className={`group text-left p-2.5 rounded border transition-all duration-300 relative flex flex-col justify-between overflow-hidden ${
                    isSelected
                      ? 'border-green-500/80 bg-green-950/20 shadow-[0_0_15px_rgba(34,197,94,0.15)]'
                      : 'border-zinc-800 bg-zinc-900/40 hover:border-zinc-700 hover:bg-zinc-900/60'
                  }`}
                >
                  {/* Corner accent for selected state */}
                  {isSelected && (
                    <div className="absolute top-0 right-0 w-2 h-2 bg-green-500 rounded-bl-sm"></div>
                  )}
                  
                  <div className="flex flex-col space-y-0.5">
                    <span className={`text-[10px] font-bold font-mono tracking-wider transition-colors duration-200 truncate ${
                      isSelected ? 'text-green-400' : 'text-zinc-300 group-hover:text-zinc-100'
                    }`}>
                      {preset.name.toUpperCase()}
                    </span>
                    <span className="text-[8px] text-zinc-500 font-mono tracking-tight truncate">
                      {genreLabel} • {preset.blueprint.bpm} BPM
                    </span>
                  </div>

                  <div className="flex items-center justify-between mt-3.5">
                    <span className={`text-[7px] font-mono uppercase px-1 py-0.2 rounded border ${
                      preset.blueprint.target_model === 'suno'
                        ? 'bg-amber-950/30 text-amber-500 border-amber-800/30'
                        : 'bg-cyan-950/30 text-cyan-500 border-cyan-800/30'
                    }`}>
                      {preset.blueprint.target_model}
                    </span>
                    
                    <Layers className={`w-3 h-3 transition-transform duration-500 ${
                      isSelected ? 'text-green-500 rotate-45 scale-110' : 'text-zinc-700 group-hover:text-zinc-500'
                    }`} />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
