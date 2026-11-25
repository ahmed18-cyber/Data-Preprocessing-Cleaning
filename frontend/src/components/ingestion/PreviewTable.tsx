import React, { useState } from 'react';
import { Table, Eye, Search, AlertTriangle, Layers, Database } from 'lucide-react';
import { useDatasetStore } from '../../stores/datasetStore';
import type { InferredType } from '../../types/dataset';

// Component-level brutalist type badge
const BrutalistTypeBadge: React.FC<{ type: InferredType }> = ({ type }) => {
  const styles: Record<InferredType, string> = {
    numeric: 'bg-blue-100 text-cobalt border-cobalt',
    categorical: 'bg-amber-100 text-orange border-orange',
    datetime: 'bg-purple-100 text-purple-900 border-purple-800',
    boolean: 'bg-emerald-100 text-emerald-900 border-emerald-800',
    text: 'bg-white text-black border-black',
  };

  return (
    <span
      className={`inline-block px-2 py-0.5 text-[10px] font-mono font-bold uppercase border-2 shadow-[1px_1px_0px_0px_#000000] ${
        styles[type] || 'bg-white text-black border-black'
      }`}
    >
      {type}
    </span>
  );
};

export const PreviewTable: React.FC = () => {
  const { preview, columns, metadata } = useDatasetStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'preview' | 'schema'>('preview');

  if (!preview || preview.length === 0 || !metadata) return null;

  const filteredColumns = columns.filter((col) =>
    col.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="w-full border-4 border-black bg-cream shadow-[8px_8px_0px_0px_#000000] mt-6 text-black select-none overflow-hidden">
      {/* Top Header / Brutalist Toolbar */}
      <div className="p-4 md:p-6 border-b-4 border-black bg-cream flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Title & Metadata Tag */}
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="w-2.5 h-2.5 bg-orange border border-black inline-block animate-pulse" />
            <h3 className="font-black text-xl md:text-2xl font-mono tracking-tight text-black uppercase">
              DATA INSPECTION
            </h3>
            <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-white text-black border-2 border-black shadow-[2px_2px_0px_0px_#000000] uppercase">
              RAW DATA / PREVIEW
            </span>
          </div>
          <p className="font-mono text-xs text-black/70 flex items-center gap-2 pt-0.5">
            <Database className="w-3.5 h-3.5 text-cobalt stroke-[2.5]" />
            <span>BUFFER: FIRST {preview.length} ROWS</span>
            <span>•</span>
            <span>{columns.length} TOTAL FEATURES</span>
          </p>
        </div>

        {/* View Switcher & Search Bar Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Brutalist Tab Switcher */}
          <div className="inline-flex border-2 border-black bg-white p-1 shadow-[3px_3px_0px_0px_#000000]">
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase transition-all flex items-center gap-1.5 border-2 ${
                activeTab === 'preview'
                  ? 'bg-orange text-white border-black shadow-[2px_2px_0px_0px_#000000]'
                  : 'bg-transparent text-black border-transparent hover:bg-cream'
              }`}
            >
              <Eye className="h-3.5 w-3.5 stroke-[2.5]" />
              <span>Preview ({preview.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('schema')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase transition-all flex items-center gap-1.5 border-2 ${
                activeTab === 'schema'
                  ? 'bg-cobalt text-white border-black shadow-[2px_2px_0px_0px_#000000]'
                  : 'bg-transparent text-black border-transparent hover:bg-cream'
              }`}
            >
              <Layers className="h-3.5 w-3.5 stroke-[2.5]" />
              <span>Profiling ({columns.length})</span>
            </button>
          </div>

          {/* Brutalist Search Field */}
          <div className="relative w-full sm:w-64">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-black stroke-[2.5]" />
            <input
              type="text"
              placeholder="SEARCH COLUMNS..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white border-2 border-black font-mono text-xs font-bold text-black pl-9 pr-3 py-2 outline-none shadow-[3px_3px_0px_0px_#000000] focus:border-orange placeholder:text-black/50"
            />
          </div>
        </div>
      </div>

      {/* View 1: Feature Profiling Table */}
      {activeTab === 'schema' ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b-3 border-black bg-black text-white font-mono uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4 border-r border-white/20">Feature Name</th>
                <th className="py-3 px-4 border-r border-white/20">Inferred Type</th>
                <th className="py-3 px-4 border-r border-white/20">Original Dtype</th>
                <th className="py-3 px-4 border-r border-white/20">Missing Values & Ratio</th>
                <th className="py-3 px-4 border-r border-white/20">Unique Values</th>
                <th className="py-3 px-4">Sample Values</th>
              </tr>
            </thead>
            <tbody className="divide-y-2 divide-black font-mono bg-white">
              {filteredColumns.map((col) => {
                const isTarget = col.name === metadata.target_column;
                const isHighMissing = col.null_percentage > 50;

                return (
                  <tr
                    key={col.name}
                    className={`transition-colors ${
                      isTarget ? 'bg-orange/10 font-bold' : 'hover:bg-cream/70'
                    }`}
                  >
                    {/* Feature Name & Target Badge */}
                    <td className="py-3 px-4 border-r-2 border-black">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-black text-sm">{col.name}</span>
                        {isTarget && (
                          <span className="text-[10px] bg-orange text-white border-2 border-black px-1.5 py-0.5 font-bold shadow-[2px_2px_0px_0px_#000000]">
                            TARGET
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Inferred Type */}
                    <td className="py-3 px-4 border-r-2 border-black">
                      <BrutalistTypeBadge type={col.inferred_type} />
                    </td>

                    {/* Original Dtype */}
                    <td className="py-3 px-4 border-r-2 border-black text-black/80 font-bold">
                      {col.original_dtype}
                    </td>

                    {/* Missing Values & Visual Gauge */}
                    <td className="py-3 px-4 border-r-2 border-black">
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-black ${
                              isHighMissing
                                ? 'text-red-700'
                                : col.null_count > 0
                                ? 'text-orange'
                                : 'text-black'
                            }`}
                          >
                            {col.null_count.toLocaleString()} ({col.null_percentage}%)
                          </span>
                          {isHighMissing && (
                            <span
                              title="Critical missingness ratio (>50%)"
                              className="inline-flex items-center gap-1 bg-red-600 text-white border border-black px-1.5 py-0.2 text-[9px] font-black"
                            >
                              <AlertTriangle className="h-3 w-3 stroke-[3]" />
                              &gt;50%
                            </span>
                          )}
                        </div>
                        {/* Compact Missing Ratio Bar */}
                        <div className="w-full max-w-[120px] h-2 bg-cream border border-black overflow-hidden">
                          <div
                            className={`h-full ${isHighMissing ? 'bg-red-600' : 'bg-orange'}`}
                            style={{ width: `${Math.min(col.null_percentage, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    {/* Unique Values */}
                    <td className="py-3 px-4 border-r-2 border-black font-bold text-black">
                      {col.unique_count.toLocaleString()}
                    </td>

                    {/* Sample Values */}
                    <td className="py-3 px-4 max-w-xs">
                      <div className="flex flex-wrap gap-1">
                        {col.sample_values.slice(0, 3).map((v, idx) => (
                          <span
                            key={idx}
                            className="inline-block bg-cream text-black font-bold text-[10px] px-2 py-0.5 border border-black shadow-[1px_1px_0px_0px_#000000] truncate max-w-[120px]"
                          >
                            {String(v)}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        /* View 2: Dataset Raw Preview Grid */
        <div className="overflow-x-auto max-h-[500px] relative">
          <table className="w-full text-left border-collapse text-xs">
            {/* Sticky Table Header */}
            <thead className="sticky top-0 bg-black text-white border-b-3 border-black z-10 shadow-[0_2px_0_0_#000000]">
              <tr>
                <th className="py-3 px-3 text-white/80 w-12 text-center font-mono border-r border-white/20 text-[11px]">
                  #
                </th>
                {filteredColumns.map((col) => {
                  const isTarget = col.name === metadata.target_column;

                  return (
                    <th
                      key={col.name}
                      className={`py-3 px-4 whitespace-nowrap border-r border-white/20 font-mono ${
                        isTarget ? 'bg-orange text-white border-r-2 border-black' : ''
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-black tracking-wide text-xs">{col.name}</span>
                        {isTarget && (
                          <span className="text-[9px] bg-black text-white border border-white px-1.5 py-0.5 font-bold">
                            TARGET
                          </span>
                        )}
                      </div>
                      <div className={`text-[10px] mt-0.5 uppercase font-bold ${isTarget ? 'text-black font-black' : 'text-white/60'}`}>
                        {col.inferred_type}
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>

            {/* Alternating Table Body */}
            <tbody className="divide-y-2 divide-black font-mono">
              {preview.map((row, idx) => {
                const isEven = idx % 2 === 0;

                return (
                  <tr
                    key={idx}
                    className={`transition-colors ${
                      isEven ? 'bg-white' : 'bg-cream/40'
                    } hover:bg-yellow-50`}
                  >
                    {/* Row Index */}
                    <td className="py-2.5 px-3 text-center text-black/60 font-bold text-[11px] border-r-2 border-black bg-cream/70">
                      {idx + 1}
                    </td>

                    {/* Data Cells */}
                    {filteredColumns.map((col) => {
                      const val = row[col.name];
                      const isTarget = col.name === metadata.target_column;
                      const isNull = val === null || val === undefined;

                      return (
                        <td
                          key={col.name}
                          className={`py-2.5 px-4 whitespace-nowrap border-r-2 border-black text-xs font-medium max-w-[240px] truncate ${
                            isTarget
                              ? 'bg-orange/10 font-bold border-r-orange/40 text-black'
                              : 'text-black'
                          }`}
                        >
                          {isNull ? (
                            <span className="inline-block px-1.5 py-0.2 bg-black/5 text-black/40 border border-dashed border-black/30 text-[10px] font-mono font-bold uppercase">
                              null
                            </span>
                          ) : (
                            String(val)
                          )}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Bottom Technical Status Bar */}
      <div className="border-t-3 border-black p-3 bg-white flex flex-wrap items-center justify-between gap-2 font-mono text-[11px] font-bold text-black/70">
        <div className="flex items-center gap-2">
          <Table className="w-3.5 h-3.5 text-black stroke-[2.5]" />
          <span>DISPLAYING {filteredColumns.length} OF {columns.length} FEATURES</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline-block">SORT: DEFAULT IMPORT ORDER</span>
          <span className="px-2 py-0.5 bg-cream border border-black text-black">
            MAX PREVIEW: {preview.length} ROWS
          </span>
        </div>
      </div>
    </div>
  );
};
