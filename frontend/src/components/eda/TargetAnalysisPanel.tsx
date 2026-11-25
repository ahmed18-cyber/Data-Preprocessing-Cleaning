import React from 'react';
import { Target, ShieldCheck } from 'lucide-react';
import type { Data as PlotlyData } from 'plotly.js';
import { useEDAStore } from '../../stores/edaStore';
import { PlotlyChart } from './PlotlyChart';

// Neo‑Brutalist redesign – warm cream background, thick black borders, orange & cobalt accents
export const TargetAnalysisPanel: React.FC = () => {
  const { targetAnalysis } = useEDAStore();

  // Guard – if no target data, render nothing (same behaviour as original)
  if (!targetAnalysis || !targetAnalysis.has_target || !targetAnalysis.target) {
    return null;
  }

  const { target } = targetAnalysis;

  // ---------------------------------------------------------------------
  // Chart rendering (unchanged logic, only container styling will differ)
  // ---------------------------------------------------------------------
  const renderDistributionChart = () => {
    if (target.is_classification) {
      const classes = target.distribution.map((d: any) => String(d.class));
      const counts = target.distribution.map((d: any) => Number(d.count));

      const barData: any[] = [
        {
          x: classes,
          y: counts,
          type: 'bar',
          marker: {
            color: '#8b5cf6', // purple‑500 – keep colour for data visibility
            line: { color: '#6d28d9', width: 1 },
          },
          hovertemplate: 'Class %{x}: <b>%{y}</b> samples<extra></extra>',
        },
      ];

      return (
        <PlotlyChart
          data={barData}
          layout={{
            margin: { l: 50, r: 20, t: 20, b: 50 },
            xaxis: { title: 'Class Label' },
            yaxis: { title: 'Observations' },
            height: 240,
          }}
        />
      );
    }

    // Continuous regression target
    const binCenters = target.distribution.map(
      (d: any) => (d.bin_start + d.bin_end) / 2,
    );
    const counts = target.distribution.map((d: any) => Number(d.count));
    const histData: PlotlyData[] = [
      {
        x: binCenters,
        y: counts,
        type: 'bar',
        marker: {
          color: '#8b5cf6',
          line: { color: '#6d28d9', width: 1 },
        },
        hovertemplate: 'Range Center %{x:.2f}: <b>%{y}</b><extra></extra>',
      },
    ];

    return (
      <PlotlyChart
        data={histData}
        layout={{
          margin: { l: 50, r: 20, t: 20, b: 50 },
          xaxis: { title: target.target_column },
          yaxis: { title: 'Frequency' },
          height: 240,
        }}
      />
    );
  };

  // ---------------------------------------------------------------------
  // UI – Neo‑Brutalist styling only (no behavioural changes)
  // ---------------------------------------------------------------------
  return (
    <div className="bg-amber-50 border-2 border-black rounded-lg p-6 shadow-[0_4px_0_0_black] space-y-6">
      {/* Header ----------------------------------------------------------- */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-black/30">
        <div>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-black" />
            <h3 className="font-bold text-base text-black">
              <span className="text-sm font-medium text-black mr-2">02 / TARGET DIAGNOSTICS</span>
              <span className="font-mono text-black">{target.target_column}</span>
            </h3>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FF4400] text-white font-semibold uppercase">
              {target.is_classification ? 'Classification' : 'Regression'}
            </span>
          </div>
          <p className="text-xs text-gray-600 mt-1">
            Target variable characteristics, class balance / value spread, and predictive formulation.
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-white bg-[#0047AB] border border-[#0047AB] px-3 py-1.5 rounded-xl">
          <ShieldCheck className="h-4 w-4" />
          <span>Strictly Isolated from Feature Preprocessing</span>
        </div>
      </div>

      {/* Stats & chart grid ---------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Summary statistics ------------------------------------------- */}
        <div className="space-y-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-800">
            Target Metrics &amp; Formulation
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            {target.is_classification ? (
              <>
                <div className="bg-amber-100 p-3 rounded border-2 border-black">
                  <span className="text-gray-600 text-[10px] uppercase font-semibold">Unique Classes</span>
                  <div className="font-mono font-bold text-black text-sm mt-1">
                    {target.summary_stats.unique_classes}
                  </div>
                </div>
                <div className="bg-amber-100 p-3 rounded border-2 border-black">
                  <span className="text-gray-600 text-[10px] uppercase font-semibold">Majority Class</span>
                  <div className="font-mono font-bold text-black text-sm mt-1 truncate">
                    {target.summary_stats.majority_class}
                  </div>
                </div>
                <div className="bg-amber-100 p-3 rounded border-2 border-black">
                  <span className="text-gray-600 text-[10px] uppercase font-semibold">Majority Share</span>
                  <div className="font-mono font-bold text-black text-sm mt-1">
                    {target.summary_stats.majority_percentage}%
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="bg-amber-100 p-3 rounded border-2 border-black">
                  <span className="text-gray-600 text-[10px] uppercase font-semibold">Target Mean</span>
                  <div className="font-mono font-bold text-black text-sm mt-1">
                    {target.summary_stats.mean}
                  </div>
                </div>
                <div className="bg-amber-100 p-3 rounded border-2 border-black">
                  <span className="text-gray-600 text-[10px] uppercase font-semibold">Target Median</span>
                  <div className="font-mono font-bold text-black text-sm mt-1">
                    {target.summary_stats.median}
                  </div>
                </div>
                <div className="bg-amber-100 p-3 rounded border-2 border-black">
                  <span className="text-gray-600 text-[10px] uppercase font-semibold">Skewness</span>
                  <div className="font-mono font-bold text-black text-sm mt-1">
                    {target.summary_stats.skewness ?? 'N/A'}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Classification / regression insight block */}
          <div className="p-3.5 rounded bg-amber-200 border border-black/30 text-xs text-gray-800">
            {target.is_classification ? (
              target.summary_stats.majority_percentage > 80 ? (
                <div className="text-[#FF4400] font-medium">
                  ⚠️ <strong>Class Imbalance Alert:</strong> The majority class accounts for {target.summary_stats.majority_percentage}% of the samples. Stratified splitting will be recommended.
                </div>
              ) : (
                <div className="text-[#0047AB] font-medium">
                  ✓ Classes appear reasonably balanced across observations.
                </div>
              )
            ) : (
              <div>Continuous target feature detected. Evaluated for regression modeling.</div>
            )}
          </div>
        </div>

        {/* Distribution chart -------------------------------------------- */}
        <div className="bg-amber-100 border-2 border-black rounded p-4">
          <h4 className="text-xs font-semibold text-gray-800 mb-2">
            Target Distribution ({target.is_classification ? 'Class Frequencies' : 'Value Density'})
          </h4>
          {renderDistributionChart()}
        </div>
      </div>
    </div>
  );
};
