import React, { useEffect } from 'react';
import { BarChart3, Activity, Box, Loader2, Filter, Database, AlertCircle } from 'lucide-react';
import { useEDAStore } from '../../stores/edaStore';
import { useDatasetStore } from '../../stores/datasetStore';
import { PlotlyChart } from './PlotlyChart';
import type { PlotData, PlotLayout } from './PlotlyChart';
import type { InferredType } from '../../types/dataset';

// Distinctive Neo-Brutalist Type Badge
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

export const ColumnExplorer: React.FC = () => {
  const { sessionId, columns: datasetColumns } = useDatasetStore();
  const {
    selectedColumn,
    selectedColumnStats,
    selectedColumnViz,
    isLoadingColumn,
    selectColumn,
  } = useEDAStore();

  // Auto-select first column on mount if none selected
  useEffect(() => {
    if (sessionId && datasetColumns.length > 0 && !selectedColumn) {
      selectColumn(sessionId, datasetColumns[0].name);
    }
  }, [sessionId, datasetColumns, selectedColumn, selectColumn]);

  const handleColumnChange = (colName: string) => {
    if (sessionId) {
      selectColumn(sessionId, colName);
    }
  };

  const activeColMeta = datasetColumns.find((c) => c.name === selectedColumn);

  // Common Plotly Layout Theme for Brutalist Aesthetics
  const brutalistChartLayout: Partial<PlotLayout> = {
    paper_bgcolor: '#FFFFFF',
    plot_bgcolor: '#FAF5E6', // Cream plotting surface
    font: {
      family: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
      size: 11,
      color: '#000000',
    },
    xaxis: {
      gridcolor: '#00000020',
      linecolor: '#000000',
      linewidth: 1.5,
      zerolinecolor: '#00000040',
      tickfont: { color: '#000000', size: 10 },
    },
    yaxis: {
      gridcolor: '#00000020',
      linecolor: '#000000',
      linewidth: 1.5,
      zerolinecolor: '#00000040',
      tickfont: { color: '#000000', size: 10 },
    },
  };

  // Prepare Plotly chart data based on inferred type
  const renderVisualizations = () => {
    if (!selectedColumnViz || isLoadingColumn) {
      return (
        <div className="h-64 flex flex-col items-center justify-center border-3 border-black bg-white p-6 shadow-[4px_4px_0px_0px_#000000]">
          <Loader2 className="h-8 w-8 animate-spin text-orange stroke-[2.5] mb-2" />
          <span className="font-mono text-xs font-bold uppercase tracking-wider text-black">
            CALCULATING EMPIRICAL DISTRIBUTIONS...
          </span>
        </div>
      );
    }

    if (
      (selectedColumnViz.inferred_type === 'numeric' || selectedColumnViz.inferred_type === 'boolean') &&
      selectedColumnViz.sample_values &&
      selectedColumnViz.sample_values.length > 0
    ) {
      // Frequency Distribution Histogram
      const histData: PlotData = [
        {
          x: selectedColumnViz.sample_values,
          type: 'histogram',
          autobinx: true,
          marker: {
            color: '#FF4400', // Electric Orange
            line: { color: '#000000', width: 1.5 },
          },
          hovertemplate: 'Range: %{x}<br>Count: <b>%{y}</b><extra></extra>',
        },
      ];

      // Quartiles & Outliers Box Plot
      const boxData: PlotData = [
        {
          y: selectedColumnViz.sample_values,
          type: 'box',
          boxpoints: 'outliers',
          marker: { color: '#0047AB', size: 5, line: { color: '#000000', width: 1 } }, // Cobalt Blue points
          line: { color: '#0047AB', width: 2 },
          fillcolor: '#0047AB20',
          name: selectedColumn || 'Value',
          hovertemplate: 'Value: %{y}<extra></extra>',
        },
      ];

      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Histogram Container */}
          <div className="border-3 border-black bg-white p-4 shadow-[4px_4px_0px_0px_#000000]">
            <div className="flex items-center justify-between pb-2 mb-2 border-b-2 border-black font-mono">
              <h5 className="text-xs font-bold text-black uppercase flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-orange stroke-[2.5]" />
                <span>Empirical Frequency Distribution (Histogram)</span>
              </h5>
              <span className="text-[10px] bg-cream px-1.5 py-0.5 border border-black font-bold text-black">
                DENSITY
              </span>
            </div>
            <div className="border-2 border-black overflow-hidden">
              <PlotlyChart
                data={histData}
                layout={{
                  ...brutalistChartLayout,
                  margin: { l: 45, r: 20, t: 20, b: 45 },
                  xaxis: {
                    gridcolor: '#00000020',
                    linecolor: '#000000',
                    linewidth: 1.5,
                    zerolinecolor: '#00000040',
                    tickfont: { color: '#000000', size: 10 },
                    title: { text: selectedColumn || 'Value', font: { size: 10 } },
                  },
                  yaxis: {
                    gridcolor: '#00000020',
                    linecolor: '#000000',
                    linewidth: 1.5,
                    zerolinecolor: '#00000040',
                    tickfont: { color: '#000000', size: 10 },
                    title: { text: 'Count', font: { size: 10 } },
                  },
                  height: 270,
                }}
              />
            </div>
          </div>

          {/* Box Plot Container */}
          <div className="border-3 border-black bg-white p-4 shadow-[4px_4px_0px_0px_#000000]">
            <div className="flex items-center justify-between pb-2 mb-2 border-b-2 border-black font-mono">
              <h5 className="text-xs font-bold text-black uppercase flex items-center gap-1.5">
                <Box className="h-4 w-4 text-cobalt stroke-[2.5]" />
                <span>Dispersion, Quartiles & Outliers (Box Plot)</span>
              </h5>
              <span className="text-[10px] bg-cream px-1.5 py-0.5 border border-black font-bold text-black">
                IQR SPREAD
              </span>
            </div>
            <div className="border-2 border-black overflow-hidden">
              <PlotlyChart
                data={boxData}
                layout={{
                  ...brutalistChartLayout,
                  margin: { l: 45, r: 20, t: 20, b: 45 },
                  yaxis: {
                    gridcolor: '#00000020',
                    linecolor: '#000000',
                    linewidth: 1.5,
                    zerolinecolor: '#00000040',
                    tickfont: { color: '#000000', size: 10 },
                    title: { text: selectedColumn || 'Value', font: { size: 10 } },
                  },
                  height: 270,
                }}
              />
            </div>
          </div>
        </div>
      );
    }

    if (
      selectedColumnViz.categories &&
      selectedColumnViz.categories.length > 0 &&
      selectedColumnViz.category_counts
    ) {
      // Categorical Bar Chart
      const barData: PlotData = [
        {
          x: selectedColumnViz.categories,
          y: selectedColumnViz.category_counts,
          type: 'bar',
          marker: {
            color: '#0047AB', // Cobalt Blue
            line: { color: '#000000', width: 1.5 },
          },
          hovertemplate: '%{x}: <b>%{y}</b> occurrences<extra></extra>',
        },
      ];

      return (
        <div className="border-3 border-black bg-white p-4 shadow-[4px_4px_0px_0px_#000000]">
          <div className="flex items-center justify-between pb-2 mb-2 border-b-2 border-black font-mono">
            <h5 className="text-xs font-bold text-black uppercase flex items-center gap-1.5">
              <BarChart3 className="h-4 w-4 text-cobalt stroke-[2.5]" />
              <span>Top Category Frequencies & Cardinality</span>
            </h5>
            <span className="text-[10px] bg-cream px-1.5 py-0.5 border border-black font-bold text-black">
              DISCRETE
            </span>
          </div>
          <div className="border-2 border-black overflow-hidden">
            <PlotlyChart
              data={barData}
              layout={{
                ...brutalistChartLayout,
                margin: { l: 45, r: 20, t: 20, b: 70 },
                xaxis: {
                  gridcolor: '#00000020',
                  linecolor: '#000000',
                  linewidth: 1.5,
                  zerolinecolor: '#00000040',
                  tickfont: { color: '#000000', size: 10 },
                  tickangle: -25,
                },
                yaxis: {
                  gridcolor: '#00000020',
                  linecolor: '#000000',
                  linewidth: 1.5,
                  zerolinecolor: '#00000040',
                  tickfont: { color: '#000000', size: 10 },
                  title: { text: 'Observations', font: { size: 10 } },
                },
                height: 290,
              }}
            />
          </div>
        </div>
      );
    }

    return (
      <div className="border-3 border-dashed border-black/50 bg-white/60 p-8 text-center font-mono">
        <AlertCircle className="h-6 w-6 text-black/60 mx-auto mb-2 stroke-[2]" />
        <span className="text-xs font-bold uppercase text-black/70">
          No graphical visualization available for this feature.
        </span>
      </div>
    );
  };

  return (
    <div className="w-full border-4 border-black bg-cream p-5 sm:p-7 shadow-[8px_8px_0px_0px_#000000] text-black space-y-6 select-none">
      {/* 1. Header & Feature Selector */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b-3 border-black">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="w-2.5 h-2.5 bg-orange border border-black inline-block" />
            <h4 className="font-mono font-black text-lg sm:text-xl uppercase tracking-tight text-black flex items-center gap-2">
              FEATURE EXPLORER
            </h4>
            <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-white text-black border-2 border-black shadow-[2px_2px_0px_0px_#000000] uppercase">
              MODULE // 03
            </span>
          </div>
          <p className="font-mono text-xs text-black/75">
            Select a feature to inspect its univariate descriptive statistics, dispersion spread, and distribution curves.
          </p>
        </div>

        {/* Prominent Variable Selector */}
        <div className="flex items-center gap-2 bg-white border-2 border-black p-2 shadow-[3px_3px_0px_0px_#000000] self-start lg:self-auto">
          <Filter className="h-4 w-4 text-orange stroke-[2.5] shrink-0" />
          <label className="text-xs font-mono font-bold uppercase text-black whitespace-nowrap">
            SELECT VARIABLE:
          </label>
          <select
            value={selectedColumn || ''}
            onChange={(e) => handleColumnChange(e.target.value)}
            className="bg-cream border-2 border-black text-black font-mono text-xs font-bold px-2.5 py-1.5 outline-none cursor-pointer focus:bg-white focus:border-cobalt"
          >
            {datasetColumns.map((col) => (
              <option key={col.name} value={col.name}>
                {col.name} [{col.inferred_type.toUpperCase()}]
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Feature Details Container */}
      {selectedColumn && activeColMeta && (
        <div className="space-y-6">
          {/* 2. Feature Metadata Strip */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-white border-3 border-black shadow-[4px_4px_0px_0px_#000000] font-mono text-xs">
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-black text-sm text-black flex items-center gap-1.5">
                <Database className="w-4 h-4 text-cobalt stroke-[2.5]" />
                {selectedColumn}
              </span>
              <BrutalistTypeBadge type={activeColMeta.inferred_type} />
              <span className="text-black/70">
                PANDAS DTYPE: <strong className="text-black">{activeColMeta.original_dtype}</strong>
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-black/80 font-bold">
              <span>
                MISSING:{' '}
                <strong className={activeColMeta.null_count > 0 ? 'text-orange font-black' : 'text-black'}>
                  {activeColMeta.null_count.toLocaleString()} ({activeColMeta.null_percentage}%)
                </strong>
              </span>
              <span>•</span>
              <span>
                UNIQUE COUNT:{' '}
                <strong className="text-cobalt font-black">
                  {activeColMeta.unique_count.toLocaleString()}
                </strong>
              </span>
            </div>
          </div>

          {/* 3. Statistical Metrics Grid */}
          {selectedColumnStats && (
            <div>
              {activeColMeta.inferred_type === 'numeric' || activeColMeta.inferred_type === 'boolean' ? (
                /* Numerical 8-Metric Grid */
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5 font-mono select-none">
                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Mean</span>
                    <div className="text-base font-black text-black mt-0.5 truncate" title={String(selectedColumnStats.mean)}>
                      {selectedColumnStats.mean !== null && selectedColumnStats.mean !== undefined ? selectedColumnStats.mean : '-'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Median</span>
                    <div className="text-base font-black text-cobalt mt-0.5 truncate" title={String(selectedColumnStats.median)}>
                      {selectedColumnStats.median !== null && selectedColumnStats.median !== undefined ? selectedColumnStats.median : '-'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Std Dev</span>
                    <div className="text-base font-black text-black mt-0.5 truncate" title={String(selectedColumnStats.std)}>
                      {selectedColumnStats.std !== null && selectedColumnStats.std !== undefined ? selectedColumnStats.std : '-'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Min</span>
                    <div className="text-base font-black text-black mt-0.5 truncate" title={String(selectedColumnStats.min)}>
                      {selectedColumnStats.min !== null && selectedColumnStats.min !== undefined ? selectedColumnStats.min : '-'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Max</span>
                    <div className="text-base font-black text-black mt-0.5 truncate" title={String(selectedColumnStats.max)}>
                      {selectedColumnStats.max !== null && selectedColumnStats.max !== undefined ? selectedColumnStats.max : '-'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Q1 (25%)</span>
                    <div className="text-base font-black text-black mt-0.5 truncate" title={String(selectedColumnStats.q1)}>
                      {selectedColumnStats.q1 !== null && selectedColumnStats.q1 !== undefined ? selectedColumnStats.q1 : '-'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Q3 (75%)</span>
                    <div className="text-base font-black text-black mt-0.5 truncate" title={String(selectedColumnStats.q3)}>
                      {selectedColumnStats.q3 !== null && selectedColumnStats.q3 !== undefined ? selectedColumnStats.q3 : '-'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Skewness</span>
                    <div className="text-base font-black text-orange mt-0.5 truncate" title={String(selectedColumnStats.skewness)}>
                      {selectedColumnStats.skewness !== null && selectedColumnStats.skewness !== undefined ? selectedColumnStats.skewness : '-'}
                    </div>
                  </div>
                </div>
              ) : (
                /* Categorical / Text 4-Metric Grid */
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-mono select-none">
                  <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Most Frequent Mode</span>
                    <div className="text-sm font-black text-black mt-1 truncate" title={selectedColumnStats.mode || 'N/A'}>
                      {selectedColumnStats.mode || 'N/A'}
                    </div>
                  </div>

                  <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Mode Frequency</span>
                    <div className="text-sm font-black text-cobalt mt-1">
                      {selectedColumnStats.mode_frequency !== null && selectedColumnStats.mode_frequency !== undefined
                        ? `${selectedColumnStats.mode_frequency} (${selectedColumnStats.mode_percentage}%)`
                        : 'N/A'}
                    </div>
                  </div>

                  <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Unique Categories</span>
                    <div className="text-sm font-black text-black mt-1">
                      {selectedColumnStats.unique_count !== undefined ? selectedColumnStats.unique_count.toLocaleString() : 'N/A'}
                    </div>
                  </div>

                  <div className="p-3 bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000000]">
                    <span className="text-[10px] uppercase font-bold text-black/60 block">Cardinality State</span>
                    <div className="text-sm font-black mt-1">
                      {selectedColumnStats.is_high_cardinality ? (
                        <span className="text-orange">High (&gt;30%)</span>
                      ) : (
                        <span className="text-emerald-700">Normal</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 4. Interactive Plotly Visualizations */}
          <div>{renderVisualizations()}</div>
        </div>
      )}
    </div>
  );
};
