import React, { useState } from 'react';
import { Target, Layers, FileSpreadsheet, Check, Info, FileText, Database } from 'lucide-react';
import { useDatasetStore } from '../../stores/datasetStore';

export const DatasetConfigPanel: React.FC = () => {
  const { metadata, columns, updateConfig, changeSheet, isConfiguring, successMessage } = useDatasetStore();

  if (!metadata) return null;

  const [mode, setMode] = useState<'supervised' | 'unsupervised'>(metadata.learning_mode);
  const [targetCol, setTargetCol] = useState<string>(metadata.target_column || '');

  const handleModeChange = (newMode: 'supervised' | 'unsupervised') => {
    setMode(newMode);
    if (newMode === 'unsupervised') {
      setTargetCol('');
      updateConfig('unsupervised', null);
    }
  };

  const handleSaveConfig = () => {
    if (mode === 'supervised' && !targetCol) return;
    updateConfig(mode, mode === 'supervised' ? targetCol : null);
  };

  return (
    <div className="w-full border-4 border-black bg-cream p-6 md:p-8 shadow-[8px_8px_0px_0px_#000000] text-black space-y-6">
      {/* Top Header Section: Dataset Metadata */}
      <div className="border-b-3 border-black pb-6 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-3">
              <div className="p-2 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                <FileText className="w-5 h-5 text-black stroke-[2.5]" />
              </div>
              <h2 className="text-xl sm:text-2xl font-black font-mono tracking-tight text-black break-all">
                {metadata.filename}
              </h2>
              <span className="px-2.5 py-1 text-xs font-mono font-bold bg-white text-black border-2 border-black shadow-[2px_2px_0px_0px_#000000] uppercase">
                .{metadata.file_type}
              </span>
            </div>
            <p className="font-mono text-xs text-black/70 flex items-center gap-1.5 pt-0.5">
              <Database className="w-3.5 h-3.5 text-cobalt" />
              <span>ACTIVE DATASET BUFFER • READY FOR CONFIGURATION</span>
            </p>
          </div>

          {/* Multi-sheet Excel Selector */}
          {metadata.sheet_names && metadata.sheet_names.length > 1 && (
            <div className="flex items-center gap-2 bg-white border-2 border-black p-2 shadow-[3px_3px_0px_0px_#000000] self-start lg:self-auto">
              <FileSpreadsheet className="h-4 w-4 text-emerald-600 shrink-0 stroke-[2.5]" />
              <label className="text-xs font-mono font-bold uppercase text-black whitespace-nowrap">
                Sheet:
              </label>
              <select
                value={metadata.active_sheet || ''}
                onChange={(e) => changeSheet(e.target.value)}
                disabled={isConfiguring}
                className="bg-cream border-2 border-black text-black font-mono text-xs font-bold px-2 py-1 outline-none cursor-pointer focus:bg-white"
              >
                {metadata.sheet_names.map((sheet) => (
                  <option key={sheet} value={sheet}>
                    {sheet}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Compact Visual Statistics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 font-mono">
          <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
            <div className="text-[10px] font-bold uppercase text-black/60 tracking-wider">Total Rows</div>
            <div className="text-lg font-black text-black">{metadata.row_count.toLocaleString()}</div>
          </div>
          <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
            <div className="text-[10px] font-bold uppercase text-black/60 tracking-wider">Total Columns</div>
            <div className="text-lg font-black text-black">{metadata.column_count}</div>
          </div>
          <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
            <div className="text-[10px] font-bold uppercase text-black/60 tracking-wider">File Size</div>
            <div className="text-lg font-black text-black">{(metadata.file_size_bytes / 1024).toFixed(1)} KB</div>
          </div>
          <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
            <div className="text-[10px] font-bold uppercase text-black/60 tracking-wider">Delimiter</div>
            <div className="text-lg font-black text-orange">
              {metadata.delimiter ? (metadata.delimiter === '\t' ? 'TAB' : metadata.delimiter) : 'AUTO'}
            </div>
          </div>
        </div>
      </div>

      {/* Main Configuration Grid: Learning Mode & Target Column Setup */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Learning Paradigm Cards */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between">
            <label className="block font-mono text-xs font-black uppercase tracking-wider text-black">
              1. Machine Learning Paradigm
            </label>
            <span className="font-mono text-[10px] font-bold bg-white px-2 py-0.5 border border-black text-black/70">
              CURRENT: {mode.toUpperCase()}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Unsupervised Card */}
            <button
              type="button"
              onClick={() => handleModeChange('unsupervised')}
              className={`p-4 border-3 border-black text-left transition-all duration-150 select-none ${
                mode === 'unsupervised'
                  ? 'bg-white shadow-[5px_5px_0px_0px_#0047AB] translate-x-[-1px] translate-y-[-1px]'
                  : 'bg-white/60 hover:bg-white shadow-[3px_3px_0px_0px_#000000] opacity-80 hover:opacity-100'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-1.5 border-2 border-black ${mode === 'unsupervised' ? 'bg-cobalt text-white' : 'bg-cream text-black'}`}>
                    <Layers className="h-4 w-4 stroke-[2.5]" />
                  </div>
                  <span className="font-mono text-xs font-black uppercase text-black tracking-wide">
                    Unsupervised
                  </span>
                </div>
                {mode === 'unsupervised' && (
                  <span className="w-2.5 h-2.5 bg-cobalt rounded-full border border-black" />
                )}
              </div>
              <p className="font-mono text-[11px] font-bold text-cobalt uppercase mb-1">
                Clustering · PCA · Anomaly
              </p>
              <p className="text-xs text-black/75 leading-relaxed font-medium">
                No dependent target label required. Evaluates feature variance and density globally.
              </p>
            </button>

            {/* Supervised Card */}
            <button
              type="button"
              onClick={() => handleModeChange('supervised')}
              className={`p-4 border-3 border-black text-left transition-all duration-150 select-none ${
                mode === 'supervised'
                  ? 'bg-white shadow-[5px_5px_0px_0px_#FF4400] translate-x-[-1px] translate-y-[-1px]'
                  : 'bg-white/60 hover:bg-white shadow-[3px_3px_0px_0px_#000000] opacity-80 hover:opacity-100'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-1.5 border-2 border-black ${mode === 'supervised' ? 'bg-orange text-white' : 'bg-cream text-black'}`}>
                    <Target className="h-4 w-4 stroke-[2.5]" />
                  </div>
                  <span className="font-mono text-xs font-black uppercase text-black tracking-wide">
                    Supervised
                  </span>
                </div>
                {mode === 'supervised' && (
                  <span className="w-2.5 h-2.5 bg-orange rounded-full border border-black" />
                )}
              </div>
              <p className="font-mono text-[11px] font-bold text-orange uppercase mb-1">
                Classification · Regression
              </p>
              <p className="text-xs text-black/75 leading-relaxed font-medium">
                Predictive workflow. Strictly isolates target feature to prevent downstream leakage.
              </p>
            </button>
          </div>
        </div>

        {/* Right Column: Target Column Selection */}
        <div className="lg:col-span-5 space-y-3">
          <label className="block font-mono text-xs font-black uppercase tracking-wider text-black">
            2. Target Variable (Dependent Column)
          </label>

          {mode === 'supervised' ? (
            <div className="p-4 bg-white border-3 border-black shadow-[4px_4px_0px_0px_#000000] space-y-3">
              <div className="flex flex-col sm:flex-row gap-2">
                <select
                  value={targetCol}
                  onChange={(e) => setTargetCol(e.target.value)}
                  className="w-full bg-cream border-2 border-black font-mono text-xs font-bold text-black px-3 py-2.5 outline-none focus:bg-white focus:border-orange cursor-pointer"
                >
                  <option value="">-- SELECT TARGET FEATURE --</option>
                  {columns.map((col) => (
                    <option key={col.name} value={col.name}>
                      {col.name} [{col.inferred_type.toUpperCase()}]
                    </option>
                  ))}
                </select>

                <button
                  type="button"
                  onClick={handleSaveConfig}
                  disabled={!targetCol || isConfiguring}
                  className="inline-flex items-center justify-center gap-1.5 px-5 py-2.5 bg-orange text-white font-mono font-bold text-xs uppercase tracking-wider border-2 border-black shadow-[3px_3px_0px_0px_#000000] hover:bg-orange/90 active:translate-x-[2px] active:translate-y-[2px] active:shadow-none disabled:opacity-50 disabled:pointer-events-none transition-all whitespace-nowrap"
                >
                  <Check className="h-4 w-4 stroke-[3]" />
                  <span>{isConfiguring ? 'SAVING...' : 'SAVE'}</span>
                </button>
              </div>

              <div className="flex items-start gap-2 pt-1 font-mono text-[11px] text-black/80">
                <Info className="h-3.5 w-3.5 text-cobalt shrink-0 mt-0.5 stroke-[2.5]" />
                <span>Selected target feature is isolated prior to train/test split to avoid leakage.</span>
              </div>
            </div>
          ) : (
            <div className="p-6 border-3 border-dashed border-black/40 bg-white/40 flex flex-col items-center justify-center text-center space-y-1">
              <span className="font-mono text-xs font-black uppercase text-black/60">
                NO TARGET REQUIRED
              </span>
              <p className="text-[11px] font-medium text-black/60 max-w-xs">
                Unsupervised mode treats all columns as exploratory features.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Feedback Banner */}
      {successMessage && (
        <div className="p-3.5 border-3 border-black bg-emerald-100 text-black shadow-[4px_4px_0px_0px_#000000] flex items-center gap-3 font-mono text-xs">
          <div className="p-1 bg-emerald-600 text-white border border-black shrink-0">
            <Check className="h-3.5 w-3.5 stroke-[3]" />
          </div>
          <div className="flex-1 font-bold">
            <span className="uppercase text-emerald-900 mr-2">[CONFIG PERSISTED]</span>
            <span>{successMessage}</span>
          </div>
        </div>
      )}
    </div>
  );
};
