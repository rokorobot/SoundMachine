'use client';

import React, { useEffect } from 'react';
import { useProjectStore } from '../store/projectStore';
import { Database, Clock, RefreshCw, GitPullRequest, LayoutList } from 'lucide-react';

export default function BlueprintLibraryPanel() {
  const { 
    snapshots, 
    fetchSnapshots, 
    restoreSnapshot, 
    setReferenceBlueprintFromSnapshot, 
    activeSnapshotId 
  } = useProjectStore();

  // Load snapshot registry on mount
  useEffect(() => {
    fetchSnapshots();
  }, [fetchSnapshots]);

  // Helper to color overall scores
  const getScoreBadgeColor = (score) => {
    if (score >= 85) return 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400';
    if (score >= 75) return 'bg-cyan-500/10 border-cyan-500/25 text-cyan-400';
    if (score >= 60) return 'bg-amber-500/10 border-amber-500/25 text-amber-500';
    return 'bg-red-500/10 border-red-500/25 text-red-500';
  };

  const getScoreIndicatorColor = (score) => {
    if (score >= 85) return 'bg-emerald-500 shadow-[0_0_8px_rgba(52,211,153,0.5)]';
    if (score >= 75) return 'bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.5)]';
    if (score >= 60) return 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]';
    return 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]';
  };

  // Helper to parse dates cleanly (MM/DD HH:MM)
  const formatDate = (dateStr) => {
    try {
      const d = new Date(dateStr);
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      const h = String(d.getHours()).padStart(2, '0');
      const min = String(d.getMinutes()).padStart(2, '0');
      return `${m}/${day} ${h}:${min}`;
    } catch (e) {
      return '00/00 00:00';
    }
  };

  return (
    <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-5 shadow-2xl flex flex-col h-full space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-850 pb-2.5">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-cyan-500" />
          <h2 className="text-xs font-bold font-mono tracking-widest text-zinc-100 uppercase">BLUEPRINT REGISTRY</h2>
        </div>
        <button
          onClick={fetchSnapshots}
          className="p-1 hover:bg-zinc-900 border border-zinc-850 rounded transition text-zinc-500 hover:text-zinc-300"
          title="Refresh Registry Feed"
        >
          <RefreshCw className="w-3 h-3" />
        </button>
      </div>

      {/* Snapshots Scroll Area */}
      <div className="flex-grow overflow-y-auto max-h-[220px] pr-1.5 space-y-2 scrollbar-thin">
        {(!snapshots || snapshots.length === 0) ? (
          <div className="flex flex-col items-center justify-center p-6 text-center space-y-2 border border-zinc-900 bg-zinc-900/10 rounded">
            <LayoutList className="w-5 h-5 text-zinc-700" />
            <p className="text-[9px] font-mono text-zinc-650 uppercase tracking-widest">REGISTRY IS EMPTY</p>
            <p className="text-[8px] font-mono text-zinc-600 leading-normal">
              GENERATE PROMPTS TO WRITE THE INITIAL BLUEPRINT SNAPSHOTS TO THE SQL DATABASE.
            </p>
          </div>
        ) : (
          <div className="space-y-1.5">
            {snapshots.map((snap) => {
              const isActive = activeSnapshotId === snap.snapshot_id;
              
              return (
                <div 
                  key={snap.snapshot_id}
                  className={`flex flex-col p-2.5 border rounded font-mono text-[9px] transition-all duration-150 ${
                    isActive 
                      ? 'border-cyan-500/50 bg-cyan-950/5 text-zinc-200' 
                      : 'border-zinc-900 bg-zinc-900/30 hover:border-zinc-800 text-zinc-400'
                  }`}
                >
                  {/* Row 1: ID, Date, Score Indicator */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1.5">
                      <div className={`w-1.5 h-1.5 rounded-full ${getScoreIndicatorColor(snap.overall_score)}`}></div>
                      <span className={`font-bold tracking-wider ${isActive ? 'text-cyan-400' : 'text-zinc-300'}`}>
                        {snap.snapshot_id}
                      </span>
                      {isActive && (
                        <span className="text-[7px] bg-cyan-950 border border-cyan-800/40 text-cyan-400 px-1 rounded font-normal uppercase tracking-widest">
                          ACTIVE
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-zinc-600 text-[8px] flex items-center space-x-1">
                        <Clock className="w-2.5 h-2.5" />
                        <span>{formatDate(snap.created_at)}</span>
                      </span>
                      <span className={`px-1.5 py-0.25 rounded border text-[8px] font-semibold ${getScoreBadgeColor(snap.overall_score)}`}>
                        GOV {snap.overall_score}%
                      </span>
                    </div>
                  </div>

                  {/* Row 2: Short Blueprint description summary */}
                  <div className="mt-1.5 text-[8px] text-zinc-550 border-b border-zinc-900/40 pb-1.5 leading-normal">
                    {snap.blueprint.genre.replace(/_/g, ' ').toUpperCase()} • {snap.blueprint.bpm} BPM • {snap.blueprint.motif_type.toUpperCase()} ({snap.blueprint.motif_behavior.toUpperCase()})
                  </div>

                  {/* Row 3: Action Hooks */}
                  <div className="flex justify-end space-x-2 mt-1.5">
                    <button
                      onClick={() => setReferenceBlueprintFromSnapshot(snap.blueprint)}
                      className="px-2 py-0.75 bg-zinc-950 hover:bg-zinc-900 border border-zinc-850 hover:border-zinc-750 text-zinc-500 hover:text-zinc-300 rounded text-[8px] font-bold transition flex items-center space-x-1"
                      title="Set snapshot as Comparison reference"
                    >
                      <GitPullRequest className="w-2.5 h-2.5" />
                      <span>COMPARE</span>
                    </button>
                    <button
                      onClick={() => restoreSnapshot(snap.snapshot_id)}
                      disabled={isActive}
                      className={`px-2 py-0.75 rounded text-[8px] font-bold transition ${
                        isActive 
                          ? 'bg-zinc-900 border border-zinc-850 text-zinc-650 cursor-not-allowed' 
                          : 'bg-cyan-950/20 hover:bg-cyan-900/20 border border-cyan-900/40 hover:border-cyan-500 text-cyan-400'
                      }`}
                      title="Restore snapshot parameters to active console"
                    >
                      RESTORE
                    </button>
                  </div>

                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}
