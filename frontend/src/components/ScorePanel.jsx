'use client';

import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { ShieldCheck, ShieldAlert, Activity, AlertTriangle, CheckCircle } from 'lucide-react';

export default function ScorePanel() {
  const { displayed, workingBlueprint } = useProjectStore();
  const scores = displayed?.scores;
  const evaluatesTarget = (workingBlueprint?.target_model || 'suno').toUpperCase();

  if (!scores) {
    return (
      <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-6 shadow-2xl h-full flex flex-col justify-center items-center space-y-3 min-h-[300px]">
        <Activity className="w-8 h-8 text-zinc-650 animate-pulse" />
        <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">LOADING DIAGNOSTIC FEED...</span>
      </div>
    );
  }

  const {
    overall,
    motif_clarity,
    genre_focus,
    prompt_density,
    model_compatibility,
    negative_prompt_quality
  } = scores;

  // Function to get color based on score
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5';
    if (score >= 60) return 'text-amber-500 border-amber-500/20 bg-amber-500/5';
    return 'text-red-500 border-red-500/20 bg-red-500/5';
  };

  const getScoreProgressColor = (score) => {
    if (score >= 80) return 'bg-emerald-500 shadow-[0_0_10px_rgba(52,211,153,0.3)]';
    if (score >= 60) return 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.3)]';
    return 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.3)]';
  };

  return (
    <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-6 shadow-2xl flex flex-col h-full space-y-5">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-500" />
          <h2 className="text-sm font-bold font-mono tracking-widest text-zinc-100 uppercase">GOVERNANCE DIAGNOSTICS</h2>
        </div>
        <span className="text-[10px] font-mono bg-zinc-900 border border-zinc-850 px-2 py-0.5 rounded text-zinc-400">
          EVALUATES: {evaluatesTarget}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-center">
        
        {/* Overall Circular Telemetry Meter */}
        <div className="md:col-span-5 flex flex-col items-center justify-center p-3 bg-zinc-900/30 border border-zinc-900 rounded-lg">
          <div className="relative w-28 h-28 flex items-center justify-center">
            {/* SVG Arc Progress */}
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="56"
                cy="56"
                r="46"
                className="stroke-zinc-850"
                strokeWidth="6"
                fill="transparent"
              />
              <circle
                cx="56"
                cy="56"
                r="46"
                stroke={overall >= 80 ? '#34d399' : overall >= 60 ? '#f59e0b' : '#ef4444'}
                strokeWidth="6"
                fill="transparent"
                strokeDasharray="289"
                strokeDashoffset={289 - (289 * overall) / 100}
                className="transition-all duration-500 ease-out"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className={`text-3xl font-bold font-mono tracking-tighter ${
                overall >= 80 ? 'text-emerald-400' : overall >= 60 ? 'text-amber-500' : 'text-red-500'
              }`}>
                {overall}
              </span>
              <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-widest">GOV SCORE</span>
            </div>
          </div>
          <div className="mt-2 text-center">
            <span className={`text-[9px] font-mono uppercase tracking-widest px-2 py-0.5 rounded border ${getScoreColor(overall)}`}>
              {overall >= 80 ? 'STABLE BLUEPRINT' : overall >= 60 ? 'TWEAK RECOMMENDED' : 'CRITICAL DEFICIT'}
            </span>
          </div>
        </div>

        {/* Detailed Metrics Panel */}
        <div className="md:col-span-7 space-y-3">
          
          {/* Metric Row: Motif Clarity */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-zinc-400 uppercase">Motif Clarity</span>
              <span className={motif_clarity >= 80 ? 'text-emerald-400' : motif_clarity >= 60 ? 'text-amber-500' : 'text-red-500'}>
                {motif_clarity}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${getScoreProgressColor(motif_clarity)}`}
                style={{ width: `${motif_clarity}%` }}
              ></div>
            </div>
          </div>

          {/* Metric Row: Genre Focus */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-zinc-400 uppercase">Genre Focus</span>
              <span className={genre_focus >= 80 ? 'text-emerald-400' : genre_focus >= 60 ? 'text-amber-500' : 'text-red-500'}>
                {genre_focus}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${getScoreProgressColor(genre_focus)}`}
                style={{ width: `${genre_focus}%` }}
              ></div>
            </div>
          </div>

          {/* Metric Row: Prompt Density */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-zinc-400 uppercase">Prompt Density</span>
              <span className={prompt_density >= 80 ? 'text-emerald-400' : prompt_density >= 60 ? 'text-amber-500' : 'text-red-500'}>
                {prompt_density}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${getScoreProgressColor(prompt_density)}`}
                style={{ width: `${prompt_density}%` }}
              ></div>
            </div>
          </div>

          {/* Metric Row: Model Compatibility */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-zinc-400 uppercase">Model Compatibility</span>
              <span className={model_compatibility >= 80 ? 'text-emerald-400' : model_compatibility >= 60 ? 'text-amber-500' : 'text-red-500'}>
                {model_compatibility}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${getScoreProgressColor(model_compatibility)}`}
                style={{ width: `${model_compatibility}%` }}
              ></div>
            </div>
          </div>

          {/* Metric Row: Negative Constraint Quality */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-zinc-400 uppercase">Negative constraint quality</span>
              <span className={negative_prompt_quality >= 80 ? 'text-emerald-400' : negative_prompt_quality >= 60 ? 'text-amber-500' : 'text-red-500'}>
                {negative_prompt_quality}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${getScoreProgressColor(negative_prompt_quality)}`}
                style={{ width: `${negative_prompt_quality}%` }}
              ></div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
