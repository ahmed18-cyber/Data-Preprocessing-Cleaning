import React from 'react';
import { GitCommit, AlertCircle, Loader2 } from 'lucide-react';
import { useEDAStore } from '../../stores/edaStore';
import { useDatasetStore } from '../../stores/datasetStore';
import { PlotlyChart } from './PlotlyChart';
import type { PlotData } from './PlotlyChart';

export const CorrelationHeatmap: React.FC = () => {
  const { sessionId } = useDatasetStore();
  const {
    correlations,
    correlationMethod,
    isLoadingCorrelations,
    setCorrelationMethod,
  } = useEDAStore();

  const handleMethodToggle = (method: 'pearson' | 'spearman') => {
    if (sessionId && method !== correlationMethod) {
      setCorrelationMethod(sessionId, method);
    }
  };

  const hasData = correlations && correlations.columns.length >= 2;

  const renderHeatmap = () => {
    if (isLoadingCorrelations) {
      return (
        <div className="bg-cream border-3 border-black p-4 shadow-[2px_2px_0px_0px_#000000] flex items-center justify-center h-72 text-gray-600">
          <Loader2 className="h-6 w-6 animate-spin text-orange" />
        </div>
      );
    }

    if (!hasData) {
      return (
        <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-gray-600">
          <AlertCircle className="h-8 w-8 text-gray-500 mb-2" />
          <div className="font-semibold text-sm text-gray-300">Insufficient Numerical Features</div>
          <p className="text-xs text-gray-500 max-w-sm mt-1">
            Correlation analysis requires at least two numerical features with non‑zero variance.
          </p>
        </div>
      );
    }

    const heatmapData: PlotData = [
      {
        z: correlations.matrix as any,
        x: correlations.columns,
        y: correlations.columns,
        type: 'heatmap',
        colorscale: [
          [0.0, '#FF4400'], // strong negative – electric orange
          [0.5, '#ffffff'], // neutral – white for clarity
          [1.0, '#0047AB'], // strong positive – cobalt blue
        ],
        zmin: -1.0,
        zmax: 1.0,
        colorbar: {
          title: 'Correlation',
          titleside: 'right',
          tickvals: [-1, -0.5, 0, 0.5, 1],
          len: 0.8,
        },
        hovertemplate: '%{y} vs %{x}<br><b>r = %{z:.3f}</b><extra></extra>',
      },
    ];

    const chartHeight = Math.max(340, Math.min(600, correlations.columns.length * 40));

    return (
      <PlotlyChart
        data={heatmapData}
        layout={{
          margin: { l: 120, r: 40, t: 30, b: 120 },
          xaxis: { tickangle: -45, automargin: true },
          yaxis: { automargin: true, autorange: 'reversed' },
          height: chartHeight,
          paper_bgcolor: '#FAF5E6', // cream background for the chart area
          plot_bgcolor: '#FAF5E6',
        }}
      />
    );
  };

  return (
    <div className="bg-cream border-3 border-black rounded-lg p-6 shadow-[4px_4px_0px_0px_#000000] space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b-2 border-black">
        <div>
          <h3 className="font-bold text-base text-black flex items-center gap-2">
            <GitCommit className="h-5 w-5 text-cobalt" />
            Bivariate Correlation Heatmap
          </h3>
          <p className="text-xs text-gray-600 mt-0.5">
            Pairwise linear (Pearson) and monotonic rank (Spearman) coefficients between numerical variables.
          </p>
        </div>
        <div className="flex items-center gap-1 bg-cream border-3 border-black rounded-xl">
          <button
            onClick={() => handleMethodToggle('pearson')}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
              correlationMethod === 'pearson'
                ? 'bg-[#FF4400] text-white border-3 border-black shadow-[2px_2px_0px_0px_#000000]'
                : 'bg-cream border-3 border-black text-gray-600 hover:text-gray-800'}
            `}
          >
            Pearson (Linear)
          </button>
          <button
            onClick={() => handleMethodToggle('spearman')}
            className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
              correlationMethod === 'spearman'
                ? 'bg-[#FF4400] text-white border-3 border-black shadow-[2px_2px_0px_0px_#000000]'
                : 'bg-cream border-3 border-black text-gray-600 hover:text-gray-800'}
            `}
          >
            Spearman (Rank)
          </button>
        </div>
      </div>

      {/* Heatmap Container */}
      <div className="bg-cream border-2 border-black rounded-lg p-4">
        {renderHeatmap()}
      </div>
    </div>
  );
};
