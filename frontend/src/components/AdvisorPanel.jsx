'use client';

import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { Compass, AlertTriangle, AlertCircle, Info, ArrowUpRight } from 'lucide-react';

export default function AdvisorPanel() {
  const { displayed } = useProjectStore();
  const recommendations = displayed?.recommendations;

  // Label helper to map slider key names to clean dashboard labels
  const targetLabels = {
    genre: "Genre Blueprint",
    bpm: "Tempo (BPM)",
    energy: "Energy Amplitude",
    motif_type: "Primary Motif",
    motif_presence: "Motif Presence",
    motif_behavior: "Motif Behavior",
    harmony_mode: "Harmony Mode",
    harmony_complexity: "Harmony Complexity",
    bass_aggression: "Bass Aggression",
    glitch_density: "Glitch Density",
    drum_intensity: "Drum Intensity",
    atmosphere_depth: "Atmosphere Depth",
    target_model: "Target Platform"
  };

  return (
    <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-5 shadow-2xl flex flex-col h-full space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-850 pb-2.5">
        <div className="flex items-center space-x-2">
          <Compass className="w-4 h-4 text-amber-500" />
          <h2 className="text-xs font-bold font-mono tracking-widest text-zinc-100 uppercase">PROMPT OPTIMIZATION ADVISOR</h2>
        </div>
        <span className="text-[9px] font-mono bg-amber-950/20 text-amber-500 border border-amber-800/30 px-1.5 py-0.5 rounded uppercase">
          TELEMETRY FEED
        </span>
      </div>

      {/* Advisory Feed Container */}
      <div className="flex-grow overflow-y-auto max-h-[220px] pr-1.5 space-y-2 scrollbar-thin">
        {(!recommendations || recommendations.length === 0) ? (
          <div className="flex items-center space-x-2 bg-emerald-950/5 border border-emerald-900/20 p-3 rounded">
            <Info className="w-4 h-4 text-emerald-500" />
            <p className="text-[10px] font-mono text-emerald-400 uppercase tracking-wide">
              SYSTEM CALIBRATION OPTIMAL. NO DRIFT CORRECTIONS REQUIRED.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {recommendations.map((rec, idx) => {
              const isError = rec.level === 'error';
              const isWarning = rec.level === 'warning';
              const isInfo = rec.level === 'info';
              
              // Select appropriate color profiles
              let containerStyle = 'bg-zinc-900/30 border-zinc-900 text-zinc-300';
              let iconElement = <Info className="w-3.5 h-3.5 text-cyan-400 mt-0.5" />;
              
              if (isError) {
                containerStyle = 'bg-red-950/10 border-red-950/50 text-red-300';
                iconElement = <AlertCircle className="w-3.5 h-3.5 text-red-500 mt-0.5" />;
              } else if (isWarning) {
                containerStyle = 'bg-amber-950/10 border-amber-950/40 text-amber-300';
                iconElement = <AlertTriangle className="w-3.5 h-3.5 text-amber-500 mt-0.5" />;
              } else if (isInfo) {
                containerStyle = 'bg-cyan-950/10 border-cyan-950/30 text-cyan-300';
                iconElement = <Info className="w-3.5 h-3.5 text-cyan-500 mt-0.5" />;
              }

              const displayTarget = targetLabels[rec.target] || rec.target;

              return (
                <div 
                  key={idx} 
                  className={`flex items-start justify-between border p-3 rounded font-mono text-[9px] leading-relaxed transition-all duration-150 ${containerStyle}`}
                >
                  <div className="flex items-start space-x-2.5 mr-2">
                    <span className="flex-shrink-0">{iconElement}</span>
                    <div className="space-y-1">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-[8px] font-bold text-zinc-500 uppercase">
                          [{rec.code}]
                        </span>
                        <span>•</span>
                        <span className={`text-[8px] font-bold tracking-widest uppercase ${
                          isError ? 'text-red-500' : isWarning ? 'text-amber-500' : 'text-cyan-500'
                        }`}>
                          {rec.level}
                        </span>
                      </div>
                      <p className="text-zinc-200">{rec.message}</p>
                    </div>
                  </div>

                  {/* Target Calibration Highlight */}
                  {rec.target && (
                    <div className="flex-shrink-0 flex flex-col items-end justify-center self-center pl-2">
                      <span className="text-[7px] text-zinc-500 uppercase tracking-widest">TARGET</span>
                      <span className="text-[8px] text-zinc-300 font-bold border border-zinc-800 bg-zinc-950 px-1.5 py-0.5 rounded mt-0.5 flex items-center space-x-1">
                        <span>{displayTarget}</span>
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}
