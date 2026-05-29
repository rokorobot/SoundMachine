'use client';

import React, { useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { useUiStore } from '../store/uiStore';
import { Copy, Terminal, Check, ArrowDownTrayIcon, Share2 } from 'lucide-react';

export default function PromptPreview() {
  const { generatedPrompts, isGenerating, error } = useProjectStore();
  const { activeModel, setActiveModel, showNotification } = useUiStore();
  const [copiedSection, setCopiedSection] = useState(null);

  const handleCopy = (text, sectionName) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedSection(sectionName);
    showNotification(`COPIED ${sectionName.toUpperCase()} TO CLIPBOARD`, 'success');
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const activePrompts = generatedPrompts ? generatedPrompts[activeModel] : null;

  return (
    <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-6 shadow-2xl relative overflow-hidden flex flex-col h-full space-y-4">
      {/* Oscilloscope Grid Effect */}
      <div className="absolute top-0 right-0 w-1/3 h-12 opacity-20 pointer-events-none">
        <svg viewBox="0 0 100 30" className="w-full h-full">
          <path
            d="M0 15 Q25 5 50 15 T100 15"
            fill="none"
            stroke="#22c55e"
            strokeWidth="0.5"
            className="animate-[pulse_2s_infinite]"
          />
          <path
            d="M0 15 Q25 25 50 15 T100 15"
            fill="none"
            stroke="#06b6d4"
            strokeWidth="0.5"
            className="animate-[pulse_3s_infinite]"
          />
        </svg>
      </div>

      {/* Header */}
      <div className="relative z-10 flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-green-500" />
          <h2 className="text-sm font-bold font-mono tracking-widest text-zinc-100 uppercase">PROMPT TERMINAL</h2>
        </div>
        <div className="flex bg-zinc-900 rounded p-0.5 border border-zinc-850">
          <button
            onClick={() => setActiveModel('suno')}
            className={`px-3 py-1 text-[10px] font-mono rounded transition-all uppercase ${
              activeModel === 'suno'
                ? 'bg-zinc-850 text-amber-500 border border-amber-600/20 font-bold'
                : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            SUNO
          </button>
          <button
            onClick={() => setActiveModel('udio')}
            className={`px-3 py-1 text-[10px] font-mono rounded transition-all uppercase ${
              activeModel === 'udio'
                ? 'bg-zinc-850 text-cyan-500 border border-cyan-600/20 font-bold'
                : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            UDIO
          </button>
        </div>
      </div>

      {/* Output Console */}
      <div className="relative z-10 flex-grow flex flex-col justify-between space-y-4 overflow-y-auto pr-1">
        {isGenerating && (
          <div className="flex-grow flex flex-col items-center justify-center space-y-3 py-12">
            <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xs text-green-500 font-mono tracking-widest uppercase">Calculating wave vectors...</p>
          </div>
        )}

        {error && (
          <div className="flex-grow border border-red-950 bg-red-950/20 p-4 rounded text-xs text-red-400 font-mono">
            [ERROR]: {error}
          </div>
        )}

        {!isGenerating && !error && !activePrompts && (
          <div className="flex-grow flex flex-col items-center justify-center space-y-2 py-12 text-center">
            <p className="text-xs text-zinc-500 font-mono">CONSOLE OFFLINE</p>
            <p className="text-[10px] text-zinc-600 font-mono">TWEAK PARAMETERS TO ACTIVATE GENERATOR</p>
          </div>
        )}

        {!isGenerating && !error && activePrompts && (
          <div className="space-y-4 flex-grow flex flex-col justify-between">
            {/* Field 1: Tags */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
                  {activeModel === 'suno' ? 'Style Tags (120 Char Limit)' : 'Descriptor Tags'}
                </span>
                <button
                  onClick={() => handleCopy(activeModel === 'suno' ? activePrompts.style_tags : activePrompts.tags, 'tags')}
                  className="p-1 rounded text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900 transition"
                  title="Copy Tags"
                >
                  {copiedSection === 'tags' ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
              <div className="bg-zinc-900/60 border border-zinc-850 p-2.5 rounded text-xs font-mono text-zinc-200 min-h-[40px] break-all select-all">
                {activeModel === 'suno' ? activePrompts.style_tags : activePrompts.tags}
              </div>
            </div>

            {/* Field 2: Prompt Body / Structures */}
            <div className="space-y-1.5 flex-grow flex flex-col">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
                  Structure & Lyrics Blocks
                </span>
                <button
                  onClick={() => handleCopy(activePrompts.prompt_body, 'structure')}
                  className="p-1 rounded text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900 transition"
                  title="Copy Structure"
                >
                  {copiedSection === 'structure' ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
              <pre className="flex-grow bg-zinc-900/60 border border-zinc-850 p-3 rounded text-xs font-mono text-zinc-300 overflow-y-auto max-h-[220px] whitespace-pre-wrap select-all leading-relaxed">
                {activePrompts.prompt_body}
              </pre>
            </div>

            {/* Field 3: Negative Prompt */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
                  Negative Prompt / Excluded Tags
                </span>
                <button
                  onClick={() => handleCopy(activePrompts.negative_prompt, 'negative')}
                  className="p-1 rounded text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900 transition"
                  title="Copy Negative Prompt"
                >
                  {copiedSection === 'negative' ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
              <div className="bg-zinc-900/60 border border-zinc-850 p-2.5 rounded text-xs font-mono text-zinc-400 select-all">
                {activePrompts.negative_prompt}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
