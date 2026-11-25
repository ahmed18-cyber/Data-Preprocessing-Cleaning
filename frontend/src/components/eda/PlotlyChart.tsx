import React from 'react';
import Plot from 'react-plotly.js';
import type { PlotParams } from 'react-plotly.js';

export type PlotData = PlotParams['data'];
export type PlotLayout = PlotParams['layout'];
export type PlotConfig = PlotParams['config'];

interface PlotlyChartProps {
  data: PlotData;
  layout?: PlotLayout;
  config?: PlotConfig;
  className?: string;
  style?: React.CSSProperties;
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
  data,
  layout = {} as PlotLayout,
  config = {} as PlotConfig,
  className = 'w-full h-full min-h-[300px]',
  style = { width: '100%', height: '100%' },
}) => {
  const defaultLayout: PlotLayout = {
    autosize: true,
    paper_bgcolor: '#FAF5E6', // cream background
    plot_bgcolor: '#FAF5E6',
    font: {
      color: '#000000', // deep black text
      family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      size: 11,
    },
    margin: { l: 50, r: 30, t: 40, b: 50 },
    xaxis: {
      gridcolor: '#00000020',
      zerolinecolor: '#00000040',
    },
    yaxis: {
      gridcolor: '#00000020',
      zerolinecolor: '#00000040',
    },
    ...(layout as any),
  };

  const defaultConfig: PlotConfig = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    ...(typeof config === "object" && config !== null ? config : {}),
  };

  return (
    <div className={className}>
      <Plot
        data={data}
        layout={defaultLayout}
        config={defaultConfig}
        style={style}
        useResizeHandler={true}
      />
    </div>
  );
};
