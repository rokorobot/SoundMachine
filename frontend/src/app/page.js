'use client';

import React, { useEffect, useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { usePresetStore } from '../store/presetStore';
import { useUiStore } from '../store/uiStore';
import ControlPanel from '../components/ControlPanel';
import PromptPreview from '../components/PromptPreview';
import PresetBrowser from '../components/PresetBrowser';
import MutationPanel from '../components/MutationPanel';
import ScorePanel from '../components/ScorePanel';
import ArrangementTimeline from '../components/ArrangementTimeline';
import CalibrationBaselinePanel from '../components/CalibrationBaselinePanel';
import AdvisorPanel from '../components/AdvisorPanel';
import BlueprintLibraryPanel from '../components/BlueprintLibraryPanel';
import {
  Download,
  Save,
  Settings,
  ShieldAlert,
  FileJson,
  FileText,
  Cpu,
  GitCommit,
} from 'lucide-react';

export default function SoundMachinaApp() {
  const { fetchPresets, presets, selectedPresetId, savePreset } = usePresetStore();
  const {
    exportCurrent,
    workingBlueprint,
    boundSnapshotId,
    isDirty,
    canSave,
    lineage,
    saveSnapshot,
    saveError,
    startInitialPreview,
    driftScore,
    driftClassification,
    referenceBlueprint,
  } = useProjectStore();
  const { notification, showSaveDialog, setShowSaveDialog, showNotification } = useUiStore();

  const [newPresetName, setNewPresetName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [showSnapshotDialog, setShowSnapshotDialog] = useState(false);
  const [snapshotName, setSnapshotName] = useState('');
  const [isSnapping, setIsSnapping] = useState(false);

  // Initialize presets and fire the first non-persistent preview (R28/R36).
  useEffect(() => {
    fetchPresets();
    startInitialPreview();
  }, [fetchPresets, startInitialPreview]);

  const activePreset = presets.find(p => p.id === selectedPresetId);
  // Truthful binding label (R8): saved snapshot id, or the lineage name marked unsaved.
  const bindingLabel = boundSnapshotId
    ? `${boundSnapshotId}${isDirty ? ' • MODIFIED' : ''}`
    : `${(lineage?.displayName || 'CUSTOM')} (UNSAVED)`;
  const exportName = boundSnapshotId || (lineage?.displayName || 'CUSTOM CONFIG');

  // Snapshot save handler (explicit, immutable persistence — R3)
  const handleSaveSnapshot = async (nameOverride) => {
    setIsSnapping(true);
    const rec = await saveSnapshot(nameOverride);
    setIsSnapping(false);
    if (rec) {
      showNotification(`SNAPSHOT ${rec.snapshot_id} WRITTEN TO REGISTRY`, 'success');
      setShowSnapshotDialog(false);
      setSnapshotName('');
    } else {
      showNotification(saveError || 'SNAPSHOT SAVE FAILED', 'error');
    }
  };

  const handleOpenSnapshot = () => {
    if (!canSave()) return;
    // First save of an unsaved custom lineage asks for a display name (R24).
    if (boundSnapshotId === null && lineage?.originType === 'custom') {
      setSnapshotName('');
      setShowSnapshotDialog(true);
    } else {
      handleSaveSnapshot();
    }
  };

  // Export prompt handler
  const handleExportText = async () => {
    const data = await exportCurrent(exportName);
    if (data) {
      const blob = new Blob([data.txt_content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = data.filename_txt;
      link.click();
      URL.revokeObjectURL(url);
      showNotification('EXPORTED TEXT PROMPT FILE', 'success');
    } else {
      showNotification('EXPORT FAILED', 'error');
    }
  };

  // Export JSON handler
  const handleExportJson = async () => {
    const data = await exportCurrent(activePresetName);
    if (data) {
      const blob = new Blob([data.json_content], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = data.filename_json;
      link.click();
      URL.revokeObjectURL(url);
      showNotification('EXPORTED CONFIGURATION JSON', 'success');
    } else {
      showNotification('EXPORT FAILED', 'error');
    }
  };

  // Save preset handler
  const handleSavePreset = async (e) => {
    e.preventDefault();
    if (!newPresetName.trim()) return;

    setIsSaving(true);
    const success = await savePreset(newPresetName.trim());
    setIsSaving(false);

    if (success) {
      showNotification(`PRESET "${newPresetName.toUpperCase()}" SAVED TO BANK`, 'success');
      setShowSaveDialog(false);
      setNewPresetName('');
    } else {
      showNotification('SAVE FAILED', 'error');
    }
  };

  return (
    <main className="flex-grow bg-zinc-950 text-zinc-100 flex flex-col p-4 md:p-6 space-y-6 relative overflow-hidden select-none min-h-screen">
      
      {/* Decorative Cockpit Grid Overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_-20%,rgba(34,197,94,0.06),transparent_60%)] pointer-events-none"></div>
      
      {/* Dynamic Status Notifications */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-2.5 rounded shadow-2xl border font-mono text-xs flex items-center space-x-2 animate-bounce ${
          notification.type === 'error' 
            ? 'bg-red-950/90 border-red-700 text-red-400' 
            : notification.type === 'warning'
            ? 'bg-amber-950/90 border-amber-600 text-amber-500'
            : 'bg-green-950/90 border-green-700 text-green-400'
        }`}>
          <ShieldAlert className="w-4 h-4 animate-pulse" />
          <span>{notification.message}</span>
        </div>
      )}

      {/* 1. Header Bar */}
      <header className="relative z-10 border border-zinc-800 bg-zinc-900/50 backdrop-blur px-6 py-4 rounded-lg flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
        <div className="flex items-center space-x-4">
          <div className="bg-green-500/10 p-2 border border-green-500/20 rounded">
            <Cpu className="w-6 h-6 text-green-500 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold font-mono tracking-widest text-zinc-100 uppercase flex items-center space-x-2">
              <span>SOUND MACHINA</span>
              <span className="text-[10px] bg-green-500/20 text-green-400 border border-green-500/30 px-1 rounded">V0.3</span>
            </h1>
            <p className="text-[10px] font-mono text-zinc-500 tracking-wider">NEURAL MUSIC DIRECTION CONSOLE</p>
          </div>
        </div>

        {/* Operating status monitor */}
        <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-xs font-mono">
          <div className="flex flex-col items-end">
            <span className="text-[9px] text-zinc-500 uppercase tracking-widest">ACTIVE BLUEPRINT</span>
            <span className={`font-bold tracking-widest uppercase ${isDirty && boundSnapshotId ? 'text-amber-400' : 'text-cyan-400'}`}>{bindingLabel}</span>
          </div>
          
          <div className="h-8 w-px bg-zinc-800 hidden sm:block"></div>
          
          <div className="flex flex-col items-end">
            <span className="text-[9px] text-zinc-500 uppercase tracking-widest">DRIFT</span>
            <span className="text-zinc-200 font-bold tracking-widest uppercase">
              {referenceBlueprint ? `${driftScore}%` : '--'}
            </span>
          </div>

          <div className="h-8 w-px bg-zinc-800 hidden sm:block"></div>

          <div className="flex flex-col items-end">
            <span className="text-[9px] text-zinc-500 uppercase tracking-widest">STATUS</span>
            <span className={`font-bold tracking-widest uppercase ${
              !referenceBlueprint 
                ? 'text-zinc-500' 
                : driftScore > 50 
                ? 'text-red-400 animate-pulse' 
                : driftScore > 25 
                ? 'text-amber-400' 
                : driftScore > 10 
                ? 'text-cyan-400' 
                : 'text-green-400'
            }`}>
              {referenceBlueprint ? driftClassification : 'STANDBY'}
            </span>
          </div>

          <div className="h-8 w-px bg-zinc-800 hidden sm:block"></div>

          <div className="flex items-center space-x-2 bg-zinc-950/80 px-3 py-1.5 border border-zinc-850 rounded">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-ping"></div>
            <span className="text-[10px] tracking-widest text-green-500 uppercase">SYS_NORMAL // ONLINE</span>
          </div>
        </div>
      </header>

      {/* 2. Main Console Grid */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-6 flex-grow">
        
        {/* Column 1: Tuning Deck (Parameters) & Diagnostics */}
        <div className="lg:col-span-5 xl:col-span-4 flex flex-col space-y-6">
          <ControlPanel />
          <ScorePanel />
          <AdvisorPanel />
        </div>

        {/* Column 2: Prompt Terminal (Outputs) & Timeline */}
        <div className="lg:col-span-7 xl:col-span-5 flex flex-col space-y-6">
          <PromptPreview />
          <ArrangementTimeline />
        </div>

        {/* Column 3: Systems Management (Presets & Mutations), Calibration Baseline & Registry */}
        <div className="lg:col-span-12 xl:col-span-3 flex flex-col space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-1 gap-6">
            <PresetBrowser />
            <MutationPanel />
          </div>
          <CalibrationBaselinePanel />
          <BlueprintLibraryPanel />
        </div>
      </div>

      {/* 3. Footer Control Bar */}
      <footer className="relative z-10 border border-zinc-800 bg-zinc-900/50 backdrop-blur p-4 rounded-lg flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="text-[10px] font-mono text-zinc-500 max-w-md text-center md:text-left">
          SOUND MACHINA v0.3 generates deterministic prompt seeds translated directly from mechanical grid structures. 
          Use outputs inside Suno AI or Udio AI input blocks to freeze theme identity.
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleOpenSnapshot}
            disabled={!canSave()}
            className={`flex items-center space-x-2 px-4 py-2 rounded font-mono text-xs transition duration-200 border ${
              canSave()
                ? 'bg-cyan-950/30 hover:bg-cyan-900/30 border-cyan-700/80 text-cyan-300 shadow-[0_0_10px_rgba(6,182,212,0.08)]'
                : 'bg-zinc-900 border-zinc-800 text-zinc-600 cursor-not-allowed'
            }`}
            title={canSave() ? 'Write an immutable snapshot to the registry' : 'No changes since last save/restore'}
          >
            <GitCommit className="w-3.5 h-3.5" />
            <span>SAVE SNAPSHOT</span>
          </button>

          <button
            onClick={() => setShowSaveDialog(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-850 border border-zinc-750 text-zinc-300 rounded font-mono text-xs transition duration-200"
          >
            <Save className="w-3.5 h-3.5" />
            <span>SAVE PRESET</span>
          </button>
          
          <button
            onClick={handleExportText}
            className="flex items-center space-x-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-850 border border-zinc-750 text-zinc-300 rounded font-mono text-xs transition duration-200"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>EXPORT PROMPT</span>
          </button>

          <button
            onClick={handleExportJson}
            className="flex items-center space-x-2 px-4 py-2 bg-green-950/20 hover:bg-green-900/20 border border-green-800/80 text-green-400 rounded font-mono text-xs transition duration-200 shadow-[0_0_10px_rgba(34,197,94,0.05)]"
          >
            <FileJson className="w-3.5 h-3.5 animate-pulse" />
            <span>EXPORT JSON PROJECT</span>
          </button>
        </div>
      </footer>

      {/* 4. Save Preset Dialog Modal */}
      {showSaveDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-zinc-850 p-6 rounded-lg shadow-2xl max-w-sm w-full relative overflow-hidden">
            {/* Warning line style */}
            <div className="absolute top-0 inset-x-0 h-1 bg-[repeating-linear-gradient(45deg,#f59e0b,#f59e0b_10px,#09090b_10px,#09090b_20px)]"></div>
            
            <h3 className="text-sm font-bold font-mono text-amber-500 uppercase tracking-widest mb-4 mt-2">
              BANK WRITE AUTHORIZATION
            </h3>
            
            <form onSubmit={handleSavePreset} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-mono text-zinc-500 uppercase">Preset Program Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. ACID TIDE v2"
                  value={newPresetName}
                  onChange={(e) => setNewPresetName(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-zinc-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSaveDialog(false)}
                  className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono text-xs hover:text-zinc-200 rounded"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-3 py-1.5 bg-amber-950/40 border border-amber-600/80 text-amber-500 font-mono text-xs hover:bg-amber-900/20 rounded flex items-center space-x-1.5"
                >
                  {isSaving ? (
                    <span className="w-3.5 h-3.5 border border-amber-500 border-t-transparent rounded-full animate-spin"></span>
                  ) : (
                    <Save className="w-3.5 h-3.5" />
                  )}
                  <span>WRITE TO DATABASE</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 5. Save Snapshot Dialog (first save of a custom lineage) */}
      {showSnapshotDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-cyan-900/50 p-6 rounded-lg shadow-2xl max-w-sm w-full relative overflow-hidden">
            <div className="absolute top-0 inset-x-0 h-1 bg-[repeating-linear-gradient(45deg,#06b6d4,#06b6d4_10px,#09090b_10px,#09090b_20px)]"></div>
            <h3 className="text-sm font-bold font-mono text-cyan-400 uppercase tracking-widest mb-1 mt-2">
              WRITE IMMUTABLE SNAPSHOT
            </h3>
            <p className="text-[9px] font-mono text-zinc-500 mb-4 leading-relaxed">
              Names a new lineage for this custom blueprint. The snapshot is permanent and versioned.
            </p>
            <form
              onSubmit={(e) => { e.preventDefault(); if (snapshotName.trim()) handleSaveSnapshot(snapshotName.trim()); }}
              className="space-y-4"
            >
              <div className="space-y-1.5">
                <label className="text-[10px] font-mono text-zinc-500 uppercase">Lineage / Project Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. ACID TIDE"
                  value={snapshotName}
                  onChange={(e) => setSnapshotName(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-zinc-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSnapshotDialog(false)}
                  className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono text-xs hover:text-zinc-200 rounded"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  disabled={isSnapping}
                  className="px-3 py-1.5 bg-cyan-950/40 border border-cyan-600/80 text-cyan-400 font-mono text-xs hover:bg-cyan-900/20 rounded flex items-center space-x-1.5"
                >
                  {isSnapping ? (
                    <span className="w-3.5 h-3.5 border border-cyan-500 border-t-transparent rounded-full animate-spin"></span>
                  ) : (
                    <GitCommit className="w-3.5 h-3.5" />
                  )}
                  <span>WRITE SNAPSHOT</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </main>
  );
}
