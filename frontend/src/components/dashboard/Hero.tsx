import React from 'react';
import { UploadCloud, ArrowRight, Sparkles, Database, Check, ShieldAlert, Cpu } from 'lucide-react';

export const Hero: React.FC = () => {
  const handleScrollToUpload = () => {
    const dropzone = document.querySelector('[data-dropzone]') as HTMLElement | null;
    if (dropzone) {
      dropzone.scrollIntoView({ behavior: 'smooth', block: 'center' });
      dropzone.focus();
    }
  };

  return (
    <section className="relative w-full border-4 border-black bg-cream p-6 md:p-10 lg:p-12 shadow-[10px_10px_0px_0px_#000000] overflow-hidden my-4">
      {/* Top Technical Metadata Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black pb-4 mb-8 font-mono text-xs font-bold uppercase tracking-wider text-black">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 bg-orange inline-block border border-black animate-pulse" />
          <span>DATA PROCESSING / 01</span>
        </div>
        <div className="flex items-center gap-4 text-black/70">
          <span className="hidden sm:inline-block">PIPELINE VER: 2.4.0</span>
          <span className="px-2 py-0.5 border border-black bg-white shadow-[2px_2px_0px_0px_#000000]">
            CSV · XLSX · XLS
          </span>
          <span className="bg-cobalt text-white px-2 py-0.5 font-bold">
            INTELLIGENT PREPROCESSING
          </span>
        </div>
      </div>

      {/* Main Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
        {/* Left Column: Bold Editorial Typography & CTA */}
        <div className="lg:col-span-7 space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white border-2 border-black font-mono text-xs font-black uppercase text-black shadow-[3px_3px_0px_0px_#000000]">
            <Cpu className="w-3.5 h-3.5 text-orange" />
            <span>Automated Data Quality Lab</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-black tracking-tight leading-[0.95] uppercase font-sans">
            YOUR DATA.
            <br />
            <span className="text-orange underline decoration-black decoration-4 underline-offset-4">
              CLEANED.
            </span>
            <br />
            <span className="relative inline-block text-black">
              READY.
              <span className="absolute -bottom-2 right-0 left-0 h-2 bg-cobalt -z-10 transform -rotate-1" />
            </span>
          </h1>

          <p className="text-base sm:text-lg md:text-xl font-medium text-black/85 leading-relaxed max-w-xl">
            Turn raw datasets into analysis-ready data with intelligent preprocessing, transparent recommendations, and reliable workflows.
          </p>

          {/* CTA & Quick Badges */}
          <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
            <button
              onClick={handleScrollToUpload}
              className="group inline-flex items-center justify-center gap-3 px-8 py-4 bg-orange text-white font-mono font-black text-base uppercase tracking-wider border-3 border-black shadow-[6px_6px_0px_0px_#000000] hover:bg-orange/90 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[4px_4px_0px_0px_#000000] active:translate-x-[6px] active:translate-y-[6px] active:shadow-none transition-all"
            >
              <UploadCloud className="h-5 w-5 stroke-[2.5]" />
              <span>UPLOAD YOUR DATASET</span>
              <ArrowRight className="h-5 w-5 stroke-[2.5] group-hover:translate-x-1 transition-transform" />
            </button>

            <div className="flex items-center gap-2 font-mono text-xs font-bold text-black/70 px-2 py-1">
              <Sparkles className="w-4 h-4 text-cobalt shrink-0" />
              <span>Zero Leakage Engine</span>
            </div>
          </div>
        </div>

        {/* Right Column: Neo-Brutalist Visual Graphic (Raw to Cleaned Transformation) */}
        <div className="lg:col-span-5 relative">
          {/* Decorative Background Element */}
          <div className="absolute -top-4 -right-4 w-full h-full border-3 border-black bg-cobalt/15 -z-10 hidden sm:block" />

          {/* Main Transformation Container */}
          <div className="border-3 border-black bg-white p-5 md:p-6 shadow-[8px_8px_0px_0px_#000000] space-y-4">
            <div className="flex items-center justify-between border-b-2 border-black pb-3">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-black" />
                <span className="font-mono text-xs font-black uppercase tracking-wider text-black">
                  TRANSFORMATION ENGINE
                </span>
              </div>
              <span className="text-[10px] font-mono font-bold bg-cream px-2 py-0.5 border border-black text-black">
                AUTO-DETECT
              </span>
            </div>

            {/* Visual Box 1: Raw / Messy Data State */}
            <div className="border-2 border-black bg-red-50 p-3 space-y-2 relative">
              <div className="flex items-center justify-between text-xs font-mono font-bold">
                <span className="text-red-700 flex items-center gap-1">
                  <ShieldAlert className="w-3.5 h-3.5" /> RAW_DATA.CSV [DIRTY]
                </span>
                <span className="text-[10px] bg-red-200 text-red-900 px-1.5 py-0.2 border border-red-400 font-mono">
                  18.4% MISSING
                </span>
              </div>
              <div className="font-mono text-[11px] leading-tight space-y-1 text-black/70 bg-white p-2 border border-black/30">
                <div className="flex justify-between border-b border-dashed border-black/20 pb-0.5">
                  <span>id,age,income,category</span>
                  <span className="text-red-600 font-bold">!MISMATCH</span>
                </div>
                <div className="text-red-700 font-semibold truncate">
                  101, NaN, "$45,200", null
                </div>
                <div className="text-red-700 font-semibold truncate">
                  102, 29, 38000, "????"
                </div>
              </div>
            </div>

            {/* Central Transformation Flow Indicator */}
            <div className="flex items-center justify-center -my-1">
              <div className="px-3 py-1 bg-black text-white font-mono text-[10px] font-black uppercase tracking-widest border border-black flex items-center gap-1.5">
                <span>PARSE</span>
                <span>•</span>
                <span className="text-orange">CLEAN</span>
                <span>•</span>
                <span className="text-cobalt">SCALE</span>
              </div>
            </div>

            {/* Visual Box 2: Cleaned / Ready Data State */}
            <div className="border-2 border-black bg-emerald-50 p-3 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono font-bold">
                <span className="text-emerald-800 flex items-center gap-1">
                  <Check className="w-3.5 h-3.5 stroke-[3] text-emerald-600" /> CLEANED_DATA [READY]
                </span>
                <span className="text-[10px] bg-emerald-200 text-emerald-900 px-1.5 py-0.2 border border-emerald-400 font-mono">
                  100% VALIDATED
                </span>
              </div>
              <div className="font-mono text-[11px] leading-tight space-y-1 text-black/80 bg-white p-2 border border-black/30">
                <div className="flex justify-between border-b border-dashed border-black/20 pb-0.5 text-black">
                  <span>id,age,income,category</span>
                  <span className="text-emerald-700 font-bold">✓ ENCODED</span>
                </div>
                <div className="text-black font-medium truncate">
                  101, 32.5, 45200.0, 1
                </div>
                <div className="text-black font-medium truncate">
                  102, 29.0, 38000.0, 0
                </div>
              </div>
            </div>

            {/* Metric pill row */}
            <div className="grid grid-cols-3 gap-2 pt-1 font-mono text-center">
              <div className="border border-black bg-cream p-1.5 shadow-[2px_2px_0px_0px_#000000]">
                <div className="text-[9px] text-black/60 uppercase font-bold">Imputation</div>
                <div className="text-xs font-black text-black">MEDIAN</div>
              </div>
              <div className="border border-black bg-cream p-1.5 shadow-[2px_2px_0px_0px_#000000]">
                <div className="text-[9px] text-black/60 uppercase font-bold">Scaling</div>
                <div className="text-xs font-black text-orange">ROBUST</div>
              </div>
              <div className="border border-black bg-cream p-1.5 shadow-[2px_2px_0px_0px_#000000]">
                <div className="text-[9px] text-black/60 uppercase font-bold">Encoding</div>
                <div className="text-xs font-black text-cobalt">ONE-HOT</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
