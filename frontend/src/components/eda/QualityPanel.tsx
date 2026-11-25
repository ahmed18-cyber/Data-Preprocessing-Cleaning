import React from 'react';
import { AlertTriangle, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import type { QualityOverview } from '../../types/eda';
import { PlotlyChart } from './PlotlyChart';
import type { PlotData, PlotLayout } from './PlotlyChart';

interface QualityPanelProps {
  quality: QualityOverview;
}

export const QualityPanel: React.FC<QualityPanelProps> = ({ quality }) => {
  // Plotly data for missing values (top 15 columns)
  const missingCols = quality.columns_with_missing_values.slice(0, 15);
  const hasMissing = missingCols.length > 0;

  const missingChartData: PlotData = hasMissing
    ? [
        {
          x: missingCols.map((c) => c.missing_percentage),
          y: missingCols.map((c) => c.column),
          type: 'bar',
          orientation: 'h',
          marker: {
            color: missingCols.map((c) => (c.missing_percentage > 50 ? '#f43f5e' : '#f59e0b')),
          },
          hovertemplate: "%{y}: <b>%{x}%</b> missing<extra></extra>",
        },
      ]
    : [];

  const missingChartLayout: PlotLayout = {
    title: { text: 'Missing Values by Feature (%)', font: { size: 13, color: '#111827' } },
    xaxis: { title: 'Missing %', range: [0, 100] },
    yaxis: { autorange: 'reversed' },
    margin: { l: 120, r: 20, t: 40, b: 40 },
    height: Math.max(220, missingCols.length * 24),
  };



  return (
    <div className="bg-cream border-3 border-black p-6 shadow-[4px_4px_0px_0px_#000000] space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b-2 border-black">
        <div>
          <h3 className="font-bold text-base text-black flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            Dataset Quality &amp; Diagnostics
          </h3>
          <p className="text-xs text-gray-600 mt-0.5">
            Descriptive health measurements: missingness, duplicates, constant columns, and high cardinality.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          {/* Findings badge – orange accent */}
          <span className="px-2.5 py-1 bg-[#FF4400] text-white font-mono font-bold uppercase shadow-[2px_2px_0px_0px_#000000]">
            {quality.quality_issues.length} Findings Detected
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Missing Values Chart */}
        <div className="bg-cream border-3 border-black p-4 shadow-[2px_2px_0px_0px_#000000]">
          {hasMissing ? (
            <PlotlyChart data={missingChartData} layout={missingChartLayout} />
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <CheckCircle2 className="h-10 w-10 text-emerald-400 mb-2 opacity-80" />
              <div className="font-bold text-sm text-black">Zero Missing Values Detected</div>
              <div className="text-xs text-gray-600 max-w-xs mt-1">
                All features contain complete observations with no null or empty entries.
              </div>
            </div>
          )}
        </div>

        {/* Quality Issues List */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-black">
            Identified Characteristics ({quality.quality_issues.length})
          </h4>
          <div className="max-h-[300px] overflow-y-auto space-y-2 pr-1">
            {quality.quality_issues.length > 0 ? (
              quality.quality_issues.map((issue, idx) => (
                <div
                  key={idx}
                  className="p-3 border-3 border-black bg-cream flex items-start justify-between gap-3 text-xs shadow-[1px_1px_0px_0px_#000000]"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 font-mono">
                      <span className="font-bold text-black">{issue.column}</span>
                      <span className="text-[10px] text-gray-600">&bull;</span>
                      <span className="text-[11px] text-gray-700 font-sans">{issue.issue_type.replace('_', ' ')}</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed">{issue.description}</p>
                  </div>
                  <div className="shrink-0">
                    {/* Severity badge using orange/cobalt */}
                    {(() => {
                      switch (issue.severity) {
                        case 'high':
                          return (
                            <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 bg-[#FF4400] text-white border border-[#FF4400] font-semibold uppercase shadow-[1px_1px_0px_0px_#000000]">
                              <AlertCircle className="h-3 w-3" /> High
                            </span>
                          );
                        case 'medium':
                          return (
                            <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 bg-[#0047AB] text-white border border-[#0047AB] font-semibold uppercase shadow-[1px_1px_0px_0px_#000000]">
                              <AlertTriangle className="h-3 w-3" /> Medium
                            </span>
                          );
                        case 'low':
                          return (
                            <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 bg-gray-200 text-gray-800 border border-gray-400 font-semibold uppercase shadow-[1px_1px_0px_0px_#000000]">
                              <Info className="h-3 w-3" /> Low
                            </span>
                          );
                        default:
                          return null;
                      }
                    })()}
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-center bg-cream border-3 border-black shadow-[2px_2px_0px_0px_#000000]">
                <CheckCircle2 className="h-8 w-8 text-emerald-400 mb-2" />
                <span className="font-bold text-black">No anomalies or data quality issues detected.</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
