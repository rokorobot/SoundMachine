'use client';

import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { Layers, Clock, Flame, ChevronRight } from 'lucide-react';

export default function ArrangementTimeline() {
  const { arrangementTimeline, blueprint, isGenerating } = useProjectStore();

  if (isGenerating || !arrangementTimeline || arrangementTimeline.length === 0) {
    return (
      <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-6 shadow-2xl h-full flex flex-col justify-center items-center space-y-3 min-h-[300px]">
        <Layers className="w-8 h-8 text-zinc-650 animate-pulse" />
        <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">CALCULATING WAVE TIMELINE...</span>
      </div>
    );
  }

  // Calculate coordinates for a SVG energy line graph
  // Timeline has 5 phases. We can render a horizontal SVG path
  const svgWidth = 500;
  const svgHeight = 70;
  const points = arrangementTimeline.map((item, idx) => {
    const x = (idx / 4) * (svgWidth - 40) + 20;
    // Map energy level (0-100) to height (svgHeight - padding)
    const y = svgHeight - 15 - (item.energy_level / 100) * (svgHeight - 30);
    return { x, y, energy: item.energy_level, phase: item.phase };
  });

  // Create SVG path string
  let pathD = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    pathD += ` L ${points[i].x} ${points[i].y}`;
  }

  return (
    <div className="border border-zinc-800 bg-zinc-950/90 backdrop-blur rounded-lg p-6 shadow-2xl flex flex-col h-full space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-500" />
          <h2 className="text-sm font-bold font-mono tracking-widest text-zinc-100 uppercase">ARRANGEMENT TIMELINE</h2>
        </div>
        <div className="flex items-center space-x-3 text-[10px] font-mono text-zinc-500">
          <div className="flex items-center space-x-1">
            <Clock className="w-3.5 h-3.5 text-zinc-600" />
            <span>{blueprint.bpm} BPM</span>
          </div>
          <span>|</span>
          <span className="text-cyan-500 uppercase">DETERMINISTIC BLUEPRINT</span>
        </div>
      </div>

      {/* SVG Energy Flow Graph */}
      <div className="bg-zinc-900/30 border border-zinc-900 rounded p-4 relative overflow-hidden">
        {/* Graph background grid */}
        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-5 px-4 py-2">
          <div className="border-b border-white h-px w-full"></div>
          <div className="border-b border-white h-px w-full"></div>
          <div className="border-b border-white h-px w-full"></div>
        </div>

        <div className="relative w-full h-[70px]">
          <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-full overflow-visible">
            {/* Gradient stroke definition */}
            <defs>
              <linearGradient id="energyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.4" />
                <stop offset="70%" stopColor="#f59e0b" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#ef4444" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="areaGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.05" />
                <stop offset="75%" stopColor="#f59e0b" stopOpacity="0.1" />
                <stop offset="100%" stopColor="#ef4444" stopOpacity="0.15" />
              </linearGradient>
            </defs>

            {/* Filled Area Under Path */}
            <path
              d={`${pathD} L ${points[points.length - 1].x} ${svgHeight - 10} L ${points[0].x} ${svgHeight - 10} Z`}
              fill="url(#areaGrad)"
            />

            {/* Line Path */}
            <path
              d={pathD}
              fill="none"
              stroke="url(#energyGrad)"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Glowing nodes */}
            {points.map((pt, idx) => (
              <g key={idx} className="group cursor-pointer">
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r="7"
                  className="fill-zinc-950 stroke-cyan-500/80 stroke-2 hover:fill-cyan-500 transition-all duration-150"
                  style={{
                    stroke: pt.energy >= 90 ? '#ef4444' : pt.energy >= 70 ? '#f59e0b' : '#06b6d4'
                  }}
                />
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r="12"
                  className="fill-transparent stroke-transparent hover:stroke-zinc-800 hover:stroke-1"
                />
                <text
                  x={pt.x}
                  y={pt.y - 12}
                  textAnchor="middle"
                  className="font-mono text-[9px] fill-zinc-400 font-bold opacity-0 group-hover:opacity-100 transition-opacity duration-150 bg-zinc-950 px-1 rounded"
                >
                  {pt.energy}%
                </text>
              </g>
            ))}
          </svg>
        </div>

        {/* Phase node label strip */}
        <div className="flex justify-between px-2 mt-1 text-[8px] font-mono text-zinc-500 uppercase tracking-wider">
          <span>INTRO</span>
          <span>ESTABLISH MOTIF</span>
          <span>PRESSURE BUILD</span>
          <span>PEAK / MUTATION</span>
          <span>OUTRO</span>
        </div>
      </div>

      {/* 5-Phase Sequential Telemetry Rows */}
      <div className="space-y-2 flex-grow overflow-y-auto max-h-[220px] pr-1">
        {arrangementTimeline.map((item, idx) => {
          const isPeak = item.energy_level >= 90;
          const isLow = item.energy_level < 50;
          
          return (
            <div 
              key={idx} 
              className={`flex flex-col md:flex-row md:items-center justify-between p-3 border rounded font-mono text-[10px] transition duration-150 ${
                isPeak 
                  ? 'border-red-950 bg-red-950/5 text-red-200' 
                  : isLow 
                  ? 'border-cyan-950/60 bg-cyan-950/5 text-cyan-200' 
                  : 'border-zinc-900 bg-zinc-900/10 text-zinc-300'
              }`}
            >
              {/* Left col: time and Phase Name */}
              <div className="flex items-center space-x-2 md:w-1/4">
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                  isPeak 
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                    : isLow 
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' 
                    : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                }`}>
                  {item.time_start} - {item.time_end}
                </span>
                <span className="font-bold tracking-wide uppercase truncate">
                  {item.phase}
                </span>
              </div>

              {/* Middle col: Description */}
              <div className="text-[10px] text-zinc-400 py-1.5 md:py-0 md:px-3 flex-grow leading-relaxed md:border-l md:border-r border-zinc-850">
                {item.description}
              </div>

              {/* Right col: Energy telemetry knob */}
              <div className="flex items-center justify-end space-x-2 md:w-1/6 md:pl-2">
                <Flame className={`w-3.5 h-3.5 ${
                  isPeak ? 'text-red-500 animate-pulse' : isLow ? 'text-cyan-500' : 'text-amber-500'
                }`} />
                <span className="font-bold">{item.energy_level}%</span>
                <span className="text-[8px] text-zinc-500 uppercase">ENG</span>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
