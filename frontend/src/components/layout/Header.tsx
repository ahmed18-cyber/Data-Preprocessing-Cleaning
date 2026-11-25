import React from 'react';
import { ShieldCheck, RefreshCw, Sparkles } from 'lucide-react';
import { useDatasetStore } from '../../stores/datasetStore';

export const Header: React.FC = () => {
  const { sessionId, reset } = useDatasetStore();

  return (
    <header className="bg-cream border-b border-black sticky top-0 z-10 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
        {/* Masthead */}
        <div className="space-y-1 text-center md:text-left">
          <h1 className="text-2xl font-extrabold text-black">DATA LAB</h1>
          <p className="text-sm text-black/70">GENERIC DATA PREPROCESSING &amp; CLEANING</p>
        </div>
        {/* Compact status area */}
        <div className="flex items-center gap-4 mt-3 md:mt-0 text-xs text-black/70">
          {sessionId && (
            <div className="flex items-center gap-1.5 bg-cream border-3 border-black px-2 py-1 rounded">
              <ShieldCheck className="h-4 w-4 text-[#0047AB]" />
              <span className="font-mono">{sessionId.slice(0, 8)}…</span>
              <button
                onClick={reset}
                title="Reset session and upload new dataset"
                className="p-0.5 hover:bg-black/10 rounded"
              >
                <RefreshCw className="h-3 w-3" />
              </button>
            </div>
          )}
          {/* Leak guard – always shown as small badge */}
          <div className="flex items-center gap-1.5 bg-cream border-3 border-black px-2 py-1 rounded">
            <Sparkles className="h-4 w-4 text-[#FF4400]" />
            <span>Leakage Prevention Guard</span>
          </div>
        </div>
      </div>
    </header>
  );
};
