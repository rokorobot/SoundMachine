'use client';

import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { Sliders, Radio, Music, Zap, Layers } from 'lucide-react';

const GENRES = [
  { value: 'psycho_glitch_techno', label: 'PSYCHO GLITCH TECHNO' },
  { value: 'coldwave', label: 'COLDWAVE / SIGNAL' },
  { value: 'brutalist_techno', label: 'BRUTALIST WAREHOUSE' },
  { value: 'ambient', label: 'AMBIENT MACHINE' },
];

const MOTIF_TYPES = [
  'cathedral organ',
  'synth piano',
  'FM synth hook',
  'electric guitar riff',
  'vocal phrase',
  'bass motif',
  'bell motif',
  'choir pad',
  'no motif'
];

const MOTIF_BEHAVIORS = [
  'fragmenting',
  'repeating',
  'soaring',
  'staccato',
  'ascending'
];

const HARMONY_MODES = [
  'minor',
  'major',
  'phrygian',
  'chromatic',
  'dorian'
];

export default function ControlPanel() {
  const { workingBlueprint: blueprint, setBlueprintField } = useProjectStore();

  const handleSliderChange = (field, e) => {
    setBlueprintField(field, parseInt(e.target.value, 10));
  };

  const handleSelectChange = (field, e) => {
    setBlueprintField(field, e.target.value);
  };

  // Helper to color codes based on level
  const getValueColor = (val) => {
    if (val > 80) return 'text-red-500 font-bold';
    if (val > 50) return 'text-amber-500';
    return 'text-green-500';
  };

  return (
    <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-6 shadow-2xl relative overflow-hidden flex flex-col h-full space-y-6">
      {/* Grid Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:2rem_2rem] opacity-[0.05] pointer-events-none"></div>

      {/* Panel Header */}
      <div className="relative z-10 flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center space-x-2">
          <Sliders className="w-4 h-4 text-green-500 animate-pulse" />
          <h2 className="text-sm font-bold font-mono tracking-widest text-zinc-100 uppercase">PARAMETER DECK</h2>
        </div>
        <div className="flex space-x-1.5">
          <button
            onClick={() => setBlueprintField('target_model', 'suno')}
            className={`px-2 py-0.5 text-[9px] font-mono border rounded transition-all uppercase ${
              blueprint.target_model === 'suno'
                ? 'bg-amber-950/40 border-amber-600/80 text-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.2)]'
                : 'bg-zinc-900 border-zinc-800 text-zinc-500 hover:text-zinc-300'
            }`}
          >
            SUNO
          </button>
          <button
            onClick={() => setBlueprintField('target_model', 'udio')}
            className={`px-2 py-0.5 text-[9px] font-mono border rounded transition-all uppercase ${
              blueprint.target_model === 'udio'
                ? 'bg-cyan-950/40 border-cyan-600/80 text-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.2)]'
                : 'bg-zinc-900 border-zinc-800 text-zinc-500 hover:text-zinc-300'
            }`}
          >
            UDIO
          </button>
        </div>
      </div>

      {/* Scrollable controls */}
      <div className="relative z-10 space-y-6 overflow-y-auto pr-1 flex-grow scrollbar-thin">
        
        {/* Core Settings Section */}
        <div className="space-y-4">
          <h3 className="text-[10px] font-bold font-mono text-zinc-500 uppercase tracking-widest border-b border-zinc-900 pb-1">
            01 // CORE SYSTEM
          </h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">Genre Blueprint</label>
              <select
                value={blueprint.genre}
                onChange={(e) => handleSelectChange('genre', e)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-green-500/50"
              >
                {GENRES.map((g) => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
                <span>Tempo</span>
                <span className="text-green-500 font-bold">{blueprint.bpm} BPM</span>
              </label>
              <div className="flex items-center space-x-2 py-1">
                <input
                  type="range"
                  min="40"
                  max="240"
                  value={blueprint.bpm}
                  onChange={(e) => handleSliderChange('bpm', e)}
                  className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-green-500"
                />
              </div>
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
              <span>Energy Amplitude</span>
              <span className={getValueColor(blueprint.energy)}>{blueprint.energy}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={blueprint.energy}
              onChange={(e) => handleSliderChange('energy', e)}
              className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-green-500"
            />
          </div>
        </div>

        {/* Motif Engine Section */}
        <div className="space-y-4">
          <h3 className="text-[10px] font-bold font-mono text-zinc-500 uppercase tracking-widest border-b border-zinc-900 pb-1 flex items-center space-x-1">
            <Music className="w-3 h-3 text-cyan-500" />
            <span>02 // MOTIF ENGINE</span>
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">Primary Motif</label>
              <select
                value={blueprint.motif_type}
                onChange={(e) => handleSelectChange('motif_type', e)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-cyan-500/50"
              >
                {MOTIF_TYPES.map((m) => (
                  <option key={m} value={m}>{m.toUpperCase()}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">Behavior</label>
              <select
                value={blueprint.motif_behavior}
                onChange={(e) => handleSelectChange('motif_behavior', e)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-cyan-500/50"
              >
                {MOTIF_BEHAVIORS.map((b) => (
                  <option key={b} value={b}>{b.toUpperCase()}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
              <span>Motif Presence</span>
              <span className={getValueColor(blueprint.motif_presence)}>{blueprint.motif_presence}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={blueprint.motif_presence}
              onChange={(e) => handleSliderChange('motif_presence', e)}
              className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
          </div>
        </div>

        {/* Harmony & Structure Section */}
        <div className="space-y-4">
          <h3 className="text-[10px] font-bold font-mono text-zinc-500 uppercase tracking-widest border-b border-zinc-900 pb-1 flex items-center space-x-1">
            <Layers className="w-3 h-3 text-emerald-500" />
            <span>03 // HARMONIC GRID</span>
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">Harmony Mode</label>
              <select
                value={blueprint.harmony_mode}
                onChange={(e) => handleSelectChange('harmony_mode', e)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-emerald-500/50"
              >
                {HARMONY_MODES.map((h) => (
                  <option key={h} value={h}>{h.toUpperCase()}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
                <span>Complexity</span>
                <span className={getValueColor(blueprint.harmony_complexity)}>{blueprint.harmony_complexity}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={blueprint.harmony_complexity}
                onChange={(e) => handleSliderChange('harmony_complexity', e)}
                className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
            </div>
          </div>
        </div>

        {/* Audio Pressure Section */}
        <div className="space-y-4">
          <h3 className="text-[10px] font-bold font-mono text-zinc-500 uppercase tracking-widest border-b border-zinc-900 pb-1 flex items-center space-x-1">
            <Zap className="w-3 h-3 text-red-500" />
            <span>04 // AUDIO PRESSURE & DENSITY</span>
          </h3>

          <div className="grid grid-cols-2 gap-x-4 gap-y-3">
            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
                <span>Bass Aggression</span>
                <span className={getValueColor(blueprint.bass_aggression)}>{blueprint.bass_aggression}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={blueprint.bass_aggression}
                onChange={(e) => handleSliderChange('bass_aggression', e)}
                className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-red-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
                <span>Glitch Density</span>
                <span className={getValueColor(blueprint.glitch_density)}>{blueprint.glitch_density}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={blueprint.glitch_density}
                onChange={(e) => handleSliderChange('glitch_density', e)}
                className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-red-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
                <span>Drum Intensity</span>
                <span className={getValueColor(blueprint.drum_intensity)}>{blueprint.drum_intensity}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={blueprint.drum_intensity}
                onChange={(e) => handleSliderChange('drum_intensity', e)}
                className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-red-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider flex justify-between">
                <span>Atmosphere Depth</span>
                <span className={getValueColor(blueprint.atmosphere_depth)}>{blueprint.atmosphere_depth}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={blueprint.atmosphere_depth}
                onChange={(e) => handleSliderChange('atmosphere_depth', e)}
                className="w-full h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-red-500"
              />
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
