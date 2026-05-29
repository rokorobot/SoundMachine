'use client';

import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { Anchor, RotateCcw, ArrowRight, TrendingUp, TrendingDown, GitCommit } from 'lucide-react';

export default function ReferenceBlueprintPanel() {
  const { 
    blueprint,
    referenceBlueprint, 
    comparisonResult, 
    setReferenceBlueprint, 
    clearReferenceBlueprint 
  } = useProjectStore();

  const handleLockReference = () => {
    setReferenceBlueprint();
  };

  const handleClearReference = () => {
    clearReferenceBlueprint();
  };

  const hasReference = !!referenceBlueprint;

  // Primary parameters list to track
  const PARAMS = [
    { key: 'genre', label: 'Genre Mode' },
    { key: 'bpm', label: 'Tempo (BPM)' },
    { key: 'energy', label: 'Track Energy' },
    { key: 'motif_type', label: 'Motif Instrument' },
    { key: 'motif_presence', label: 'Motif Presence' },
    { key: 'motif_behavior', label: 'Motif Behavior' },
    { key: 'harmony_mode', label: 'Harmonic Scale' },
    { key: 'harmony_complexity', label: 'Harmonic Density' },
    { key: 'bass_aggression', label: 'Bass Aggression' },
    { key: 'glitch_density', label: 'Glitch Density' },
    { key: 'drum_intensity', label: 'Drum Intensity' },
    { key: 'atmosphere_depth', label: 'Atmosphere Depth' },
    { key: 'target_model', label: 'Target Platform' }
  ];

  // Helper to format values
  const formatVal = (key, val) => {
    if (!val && val !== 0) return '';
    if (key === 'genre') {
      return val.replace(/_/g, ' ').toUpperCase();
    }
    if (key === 'bpm') {
      return `${val}`;
    }
    if (typeof val === 'number') {
      return `${val}%`;
    }
    return typeof val === 'string' ? val.toUpperCase() : val;
  };

  // Calculate Blueprint Drift Score
  let driftScore = 0;
  let driftClassification = 'Nearly identical';
  
  if (hasReference) {
    let totalDrift = 0;
    const count = PARAMS.length;
    
    PARAMS.forEach(param => {
      const key = param.key;
      const diffObj = comparisonResult?.diff?.[key];
      if (diffObj) {
        if (typeof diffObj.delta === 'number') {
          // Sliders are 0-100 (range 100), BPM is 40-240 (range 200)
          const range = key === 'bpm' ? 200 : 100;
          totalDrift += Math.abs(diffObj.delta) / range;
        } else {
          // String changes (genre, motif_type, behavior, target platform)
          totalDrift += 0.4; // 40% flat penalty for structural changes
        }
      }
    });
    
    driftScore = Math.round((totalDrift / count) * 100);
    if (driftScore > 50) driftClassification = 'New blueprint';
    else if (driftScore > 25) driftClassification = 'Significant mutation';
    else if (driftScore > 10) driftClassification = 'Minor variation';
  }

  return (
    <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-5 shadow-2xl flex flex-col h-full space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-850 pb-2.5">
        <div className="flex items-center space-x-2">
          <GitCommit className="w-4 h-4 text-cyan-500" />
          <h2 className="text-xs font-bold font-mono tracking-widest text-zinc-100 uppercase">REFERENCE BLUEPRINT</h2>
        </div>
        
        {hasReference ? (
          <button
            onClick={handleClearReference}
            className="flex items-center space-x-1 px-2 py-0.5 bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 rounded text-[9px] font-mono text-zinc-400 hover:text-zinc-200 transition"
          >
            <RotateCcw className="w-2.5 h-2.5" />
            <span>UNLINK</span>
          </button>
        ) : (
          <span className="text-[9px] font-mono text-zinc-600 uppercase">STANDBY</span>
        )}
      </div>

      {!hasReference ? (
        /* Standby / Empty State */
        <div className="flex-grow flex flex-col items-center justify-center p-6 text-center space-y-4 min-h-[220px]">
          <div className="bg-zinc-900/60 p-4 border border-zinc-900 rounded-full">
            <Anchor className="w-7 h-7 text-zinc-650" />
          </div>
          <div className="space-y-1 max-w-xs">
            <h3 className="text-xs font-bold font-mono text-zinc-400 uppercase tracking-widest">NO BASELINE LOCK</h3>
            <p className="text-[9px] font-mono text-zinc-550 leading-relaxed">
              Lock current parameters as reference telemetry to monitor real-time slider drift and delta score changes.
            </p>
          </div>
          <button
            onClick={handleLockReference}
            className="px-4 py-2 bg-cyan-950/20 hover:bg-cyan-900/20 border border-cyan-800/80 hover:border-cyan-600 text-cyan-500 font-mono text-xs rounded tracking-widest transition duration-200"
          >
            LOCK REFERENCE SNAPSHOT
          </button>
        </div>
      ) : (
        /* Compare Mode Active State */
        <div className="flex-grow flex flex-col justify-between space-y-4">
          
          {/* Blueprint Drift Score Gauge & Delta Score Header */}
          <div className="grid grid-cols-2 gap-2.5">
            {/* Drift score panel */}
            <div className="flex flex-col p-2.5 bg-zinc-900/40 border border-zinc-900 rounded-lg">
              <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-wider">Drift Score</span>
              <span className="text-xs font-bold font-mono text-cyan-400 mt-0.5">
                DRIFT: {driftScore}%
              </span>
              <span className={`text-[7px] font-mono uppercase font-bold tracking-wider mt-0.5 ${
                driftScore > 50 ? 'text-red-500 animate-pulse' : driftScore > 25 ? 'text-amber-500' : driftScore > 10 ? 'text-cyan-500' : 'text-zinc-600'
              }`}>
                {driftClassification}
              </span>
            </div>

            {/* Delta score panel */}
            {comparisonResult && (
              <div className="flex flex-col p-2.5 bg-zinc-900/40 border border-zinc-900 rounded-lg">
                <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-wider">Score Delta</span>
                <div className="flex items-center space-x-1 mt-0.5">
                  <span className={`text-xs font-bold font-mono ${
                    comparisonResult.overall_delta > 0 
                      ? 'text-emerald-400' 
                      : comparisonResult.overall_delta < 0 
                      ? 'text-red-500' 
                      : 'text-zinc-400'
                  }`}>
                    {comparisonResult.overall_delta > 0 ? `+${comparisonResult.overall_delta}` : comparisonResult.overall_delta} pts
                  </span>
                  {comparisonResult.overall_delta > 0 ? (
                    <TrendingUp className="w-3 h-3 text-emerald-500" />
                  ) : comparisonResult.overall_delta < 0 ? (
                    <TrendingDown className="w-3 h-3 text-red-500" />
                  ) : null}
                </div>
                <div className="text-[7px] text-zinc-600 font-mono mt-0.5">
                  {comparisonResult.scores_a.overall} vs {comparisonResult.scores_b.overall}
                </div>
              </div>
            )}
          </div>

          {/* Fully Articulated Telemetry Matrix */}
          <div className="flex-grow overflow-y-auto max-h-[190px] pr-1 scrollbar-thin">
            <table className="w-full text-left font-mono text-[9px] border-collapse">
              <thead>
                <tr className="border-b border-zinc-900 text-zinc-500 uppercase tracking-widest text-[8px]">
                  <th className="pb-1.5 font-bold">Parameter</th>
                  <th className="pb-1.5 font-bold text-center">Locked</th>
                  <th className="pb-1.5 font-bold text-center">Current</th>
                  <th className="pb-1.5 font-bold text-right">Delta</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900/60">
                {PARAMS.map((param) => {
                  const key = param.key;
                  const diffObj = comparisonResult?.diff?.[key];
                  const isChanged = !!diffObj;
                  
                  const lockedVal = isChanged ? diffObj.value_a : referenceBlueprint[key];
                  const currentVal = isChanged ? diffObj.value_b : blueprint[key];
                  
                  let deltaText = 'UNCHANGED';
                  let deltaStyle = 'text-zinc-650 font-normal';
                  
                  if (isChanged) {
                    if (typeof diffObj.delta === 'number') {
                      const prefix = diffObj.delta > 0 ? '+' : '';
                      
                      // Calculate percentage drift relative to locked value
                      let pctStr = '';
                      if (lockedVal !== 0) {
                        const pct = Math.round((diffObj.delta / lockedVal) * 100);
                        const pctPrefix = pct > 0 ? '+' : '';
                        pctStr = ` (${pctPrefix}${pct}%)`;
                      }
                      
                      deltaText = `${prefix}${diffObj.delta}${pctStr}`;
                      deltaStyle = diffObj.delta > 0 ? 'text-emerald-500 font-bold' : 'text-red-500 font-bold';
                    } else {
                      deltaText = 'MODIFIED';
                      deltaStyle = 'text-amber-500 font-bold';
                    }
                  }

                  return (
                    <tr key={key} className="hover:bg-zinc-900/20 transition-colors">
                      <td className="py-2 text-zinc-400 font-medium truncate max-w-[85px]">{param.label}</td>
                      <td className="py-2 text-center text-zinc-500">{formatVal(key, lockedVal)}</td>
                      <td className="py-2 text-center text-zinc-200 font-semibold">{formatVal(key, currentVal)}</td>
                      <td className={`py-2 text-right ${deltaStyle}`}>{deltaText}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Quick Lock option for new state */}
          <div className="pt-2 border-t border-zinc-900 flex justify-between items-center">
            <span className="text-[8px] font-mono text-zinc-550 uppercase">CALIBRATION MATRIX ACTIVE</span>
            <button
              onClick={handleLockReference}
              className="px-2.5 py-1 bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-zinc-400 hover:text-zinc-200 font-mono text-[8px] tracking-wider uppercase rounded transition"
            >
              SNAP CURRENT CONFIG
            </button>
          </div>

        </div>
      )}

    </div>
  );
}
