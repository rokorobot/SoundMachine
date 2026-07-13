'use client';

import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { useUiStore } from '../store/uiStore';
import { Sparkles } from 'lucide-react';

const MUTATIONS = [
  { id: 'psychotic', label: '+ MORE PSYCHOTIC', color: 'hover:border-red-500 hover:text-red-400' },
  { id: 'melodic', label: '+ MORE MELODIC', color: 'hover:border-cyan-500 hover:text-cyan-400' },
  { id: 'brutalist', label: '+ MORE BRUTALIST', color: 'hover:border-zinc-500 hover:text-zinc-200' },
  { id: 'club_ready', label: '+ MORE CLUB-READY', color: 'hover:border-emerald-500 hover:text-emerald-400' },
  { id: 'organ', label: '+ MORE ORGAN', color: 'hover:border-amber-500 hover:text-amber-400' },
  { id: 'less_drums', label: '- LESS DRUMS', color: 'hover:border-yellow-600 hover:text-yellow-500' },
  { id: 'piano', label: '+ MORE PIANO', color: 'hover:border-blue-500 hover:text-blue-400' },
  { id: 'coldwave', label: '+ MORE COLDWAVE', color: 'hover:border-purple-500 hover:text-purple-400' },
  { id: 'idm', label: '+ MORE IDM', color: 'hover:border-indigo-500 hover:text-indigo-400' },
  { id: 'vocal', label: '+ MORE VOCAL', color: 'hover:border-pink-500 hover:text-pink-400' },
];

export default function MutationPanel() {
  const { workingBlueprint: blueprint, setBlueprintField, setFullBlueprint } = useProjectStore();
  const { showNotification } = useUiStore();

  const applyMutation = (id, label) => {
    let updated = { ...blueprint };
    let msg = "";

    switch (id) {
      case 'psychotic':
        updated.glitch_density = Math.min(100, updated.glitch_density + 20);
        updated.energy = Math.max(80, Math.min(100, updated.energy + 10));
        updated.motif_behavior = 'fragmenting';
        msg = "MUTATION APPLIED: GLITCH DENSITY BOOSTED, BEHAVIOR FRAGMENTED";
        break;
      case 'melodic':
        updated.motif_presence = Math.min(100, updated.motif_presence + 25);
        updated.harmony_complexity = Math.min(100, updated.harmony_complexity + 15);
        updated.motif_behavior = 'soaring';
        if (updated.motif_type === 'no motif') updated.motif_type = 'synth piano';
        msg = "MUTATION APPLIED: MELODIC AMPLITUDE INCREMENTED";
        break;
      case 'brutalist':
        updated.genre = 'brutalist_techno';
        updated.bass_aggression = Math.min(100, updated.bass_aggression + 20);
        updated.drum_intensity = Math.min(100, updated.drum_intensity + 20);
        updated.atmosphere_depth = Math.max(0, updated.atmosphere_depth - 25);
        msg = "MUTATION APPLIED: CORE STRUCT TRANSFERRED TO BRUTALIST";
        break;
      case 'club_ready':
        updated.bpm = Math.max(126, Math.min(135, updated.bpm + 5));
        updated.energy = Math.min(100, updated.energy + 20);
        updated.drum_intensity = Math.min(100, updated.drum_intensity + 15);
        msg = "MUTATION APPLIED: PULSE VECTOR ALIGNED TO CLUB-GRID";
        break;
      case 'organ':
        updated.motif_type = 'cathedral organ';
        updated.motif_presence = Math.min(100, updated.motif_presence + 25);
        msg = "MUTATION APPLIED: PRIMARY MELODIC CELL = CATHEDRAL ORGAN";
        break;
      case 'less_drums':
        updated.drum_intensity = Math.max(0, updated.drum_intensity - 35);
        msg = "MUTATION APPLIED: RHYTHM COMPRESSION REDUCED";
        break;
      case 'piano':
        updated.motif_type = 'synth piano';
        updated.motif_presence = Math.min(100, updated.motif_presence + 25);
        msg = "MUTATION APPLIED: PRIMARY MELODIC CELL = SYNTH PIANO";
        break;
      case 'coldwave':
        updated.genre = 'coldwave';
        updated.bpm = 112;
        updated.motif_type = 'FM synth hook';
        updated.motif_presence = Math.max(60, updated.motif_presence);
        msg = "MUTATION APPLIED: CORE GENRE TRANSFERRED TO COLDWAVE";
        break;
      case 'idm':
        updated.genre = 'psycho_glitch_techno';
        updated.glitch_density = Math.min(100, updated.glitch_density + 30);
        updated.harmony_complexity = Math.min(100, updated.harmony_complexity + 25);
        msg = "MUTATION APPLIED: IDM GLITCH ALGORITHMS ENGAGED";
        break;
      case 'vocal':
        updated.motif_type = 'vocal phrase';
        updated.motif_presence = Math.min(100, updated.motif_presence + 30);
        msg = "MUTATION APPLIED: VOCAL PRESENCE MODULATOR ON";
        break;
      default:
        break;
    }

    setFullBlueprint(updated);
    showNotification(msg, 'warning');
  };

  return (
    <div className="border border-zinc-800 bg-zinc-950/80 backdrop-blur p-6 rounded-lg shadow-2xl relative overflow-hidden flex flex-col justify-between h-full">
      {/* Visual background lines */}
      <div className="absolute inset-x-0 bottom-0 h-1/2 bg-[linear-gradient(to_top,rgba(239,68,68,0.02),transparent)] pointer-events-none"></div>

      <div className="relative z-10 flex items-center justify-between mb-4 border-b border-zinc-800 pb-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-red-500" />
          <h2 className="text-sm font-bold font-mono tracking-widest text-zinc-100 uppercase">MUTATION INJECTOR</h2>
        </div>
        <span className="text-[10px] text-zinc-500 font-mono">DANGER_VOLTAGE</span>
      </div>

      {/* Grid of mutation buttons (scrollable to see all items without compression) */}
      <div className="relative z-10 grid grid-cols-2 gap-2 flex-grow overflow-y-auto max-h-[130px] pr-1.5 scrollbar-thin scrollbar-thumb-zinc-850 scrollbar-track-zinc-950/40">
        {MUTATIONS.map((m) => (
          <button
            key={m.id}
            onClick={() => applyMutation(m.id, m.label)}
            className={`py-2.5 px-2 bg-zinc-900/40 border border-zinc-850 hover:bg-zinc-850/50 rounded font-mono text-[9px] text-zinc-400 font-bold transition-all duration-200 tracking-wider flex items-center justify-center text-center ${m.color}`}
          >
            {m.label}
          </button>
        ))}
      </div>
    </div>
  );
}
