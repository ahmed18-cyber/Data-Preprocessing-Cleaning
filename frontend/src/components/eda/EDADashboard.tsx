import React, { useEffect } from 'react';
import { RefreshCw, AlertCircle, Cpu, Activity, ShieldAlert, GitCommit, Layers, Database } from 'lucide-react';
import { useEDAStore } from '../../stores/edaStore';
import { useDatasetStore } from '../../stores/datasetStore';
import { OverviewCards } from './OverviewCards';
import { QualityPanel } from './QualityPanel';
import { ColumnExplorer } from './ColumnExplorer';
import { CorrelationHeatmap } from './CorrelationHeatmap';
import { TargetAnalysisPanel } from './TargetAnalysisPanel';

export const EDADashboard: React.FC = () => {
  const { sessionId, metadata } = useDatasetStore();
  const {
    overview,
    quality,
    targetAnalysis,
    isLoadingOverview,
    isLoadingQuality,
    isLoadingCorrelations,
    isLoadingTarget,
    error,
    loadEDA,
  } = useEDAStore();

  const isAnyLoading = isLoadingOverview || isLoadingQuality || isLoadingCorrelations || isLoadingTarget;

  useEffect(() => {
    if (sessionId) {
      loadEDA(sessionId);
    }
  }, [sessionId, metadata?.active_sheet, metadata?.learning_mode, metadata?.target_column, loadEDA]);

  if (!sessionId) {
    return null;
  }

  const handleRefresh = () => {
    if (sessionId) {
      loadEDA(sessionId);
    }
  };

  const hasTarget = Boolean(targetAnalysis?.has_target && targetAnalysis?.target);

  return (
    <div className="w-full space-y-8 select-none">
      {/* 1. Top Neo-Brutalist Analytical Header */}
      <div className="border-4 border-black bg-cream p-6 md:p-8 shadow-[8px_8px_0px_0px_#000000] text-black">
        {/* Technical Sub-bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black pb-4 mb-6 font-mono text-xs font-bold uppercase tracking-wider text-black">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-orange inline-block border border-black animate-pulse" />
            <span>ANALYSIS ENGINE / 01</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-block text-black/70">WORKSPACE: EXPLORATORY PROFILING</span>
            <span className="px-2 py-0.5 border-2 border-black bg-white shadow-[2px_2px_0px_0px_#000000]">
              {metadata?.filename || 'ACTIVE_DATASET'}
            </span>
            <span className={`px-2 py-0.5 font-bold border border-black ${
              isAnyLoading ? 'bg-orange text-white animate-pulse' : 'bg-emerald-300 text-black'
            }`}>
              {isAnyLoading ? 'PROCESSING' : 'SYNCHRONIZED'}
            </span>
          </div>
        </div>

        {/* Header Main Bar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-0.5 bg-white border-2 border-black font-mono text-xs font-black uppercase text-black shadow-[2px_2px_0px_0px_#000000]">
              <Cpu className="w-3.5 h-3.5 text-cobalt stroke-[2.5]" />
              <span>Statistical Inference & Health Suite</span>
            </div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-black font-sans tracking-tight leading-[0.95] uppercase text-black">
              DATA INTELLIGENCE
            </h1>
            <p className="text-sm sm:text-base font-medium text-black/85 leading-relaxed">
              Examine foundational statistical properties, inspect empirical feature distributions, evaluate pairwise collinearity, and detect critical structural defects before pipeline execution.
            </p>
          </div>

          {/* Action Trigger Button */}
          <div className="shrink-0 self-start lg:self-auto">
            <button
              onClick={handleRefresh}
              disabled={isAnyLoading}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 bg-orange text-white font-mono font-bold text-xs uppercase tracking-wider border-3 border-black shadow-[4px_4px_0px_0px_#000000] hover:bg-orange/90 hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[3px_3px_0px_0px_#000000] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none disabled:opacity-50 disabled:pointer-events-none transition-all whitespace-nowrap"
            >
              <RefreshCw className={`h-4 w-4 stroke-[2.5] ${isAnyLoading ? 'animate-spin' : ''}`} />
              <span>{isAnyLoading ? 'RECALCULATING...' : 'REFRESH METRICS'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Error Alert Banner */}
      {error && (
        <div className="p-4 border-3 border-black bg-red-100 text-black shadow-[4px_4px_0px_0px_#000000] flex items-start gap-3">
          <div className="p-1 bg-red-600 text-white border border-black shrink-0 mt-0.5">
            <AlertCircle className="h-4 w-4 stroke-[3]" />
          </div>
          <div className="flex-1 font-mono text-xs md:text-sm">
            <span className="font-black uppercase tracking-wider block text-red-700">
              [ANALYSIS CALCULATION ERROR]
            </span>
            <span className="font-semibold text-black/90">{error}</span>
          </div>
        </div>
      )}

      {/* 2. Analytical Section 1: Overview Metrics */}
      {overview && (
        <section className="space-y-3">
          <div className="flex items-center gap-2 border-b-2 border-black pb-2 font-mono">
            <Database className="w-4 h-4 text-cobalt stroke-[2.5]" />
            <h3 className="font-black text-xs md:text-sm uppercase tracking-wider text-black">
              SECTION 01 // GLOBAL DATASET PROFILE
            </h3>
          </div>
          <OverviewCards overview={overview} />
        </section>
      )}

      {/* 3. Analytical Section 2: Supervised Target Analysis (Conditional) */}
      {hasTarget && (
        <section className="space-y-3">
          <div className="flex items-center gap-2 border-b-2 border-black pb-2 font-mono">
            <Activity className="w-4 h-4 text-purple-700 stroke-[2.5]" />
            <h3 className="font-black text-xs md:text-sm uppercase tracking-wider text-black">
              SECTION 02 // SUPERVISED TARGET VARIABLE DIAGNOSTICS
            </h3>
          </div>
          <TargetAnalysisPanel />
        </section>
      )}

      {/* 4. Analytical Section 3: Feature Explorer */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 border-b-2 border-black pb-2 font-mono">
          <Layers className="w-4 h-4 text-orange stroke-[2.5]" />
          <h3 className="font-black text-xs md:text-sm uppercase tracking-wider text-black">
            SECTION {hasTarget ? '03' : '02'} // UNIVARIATE FEATURE EXPLORER & DISTRIBUTIONS
          </h3>
        </div>
        <ColumnExplorer />
      </section>

      {/* 5. Analytical Section 4: Dataset Quality & Diagnostics */}
      {quality && (
        <section className="space-y-3">
          <div className="flex items-center gap-2 border-b-2 border-black pb-2 font-mono">
            <ShieldAlert className="w-4 h-4 text-amber-600 stroke-[2.5]" />
            <h3 className="font-black text-xs md:text-sm uppercase tracking-wider text-black">
              SECTION {hasTarget ? '04' : '03'} // DATA QUALITY AUDIT & MISSINGNESS PROFILING
            </h3>
          </div>
          <QualityPanel quality={quality} />
        </section>
      )}

      {/* 6. Analytical Section 5: Correlation Heatmap */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 border-b-2 border-black pb-2 font-mono">
          <GitCommit className="w-4 h-4 text-cobalt stroke-[2.5]" />
          <h3 className="font-black text-xs md:text-sm uppercase tracking-wider text-black">
            SECTION {hasTarget ? '05' : '04'} // BIVARIATE COLLINEARITY & CORRELATION MATRIX
          </h3>
        </div>
        <CorrelationHeatmap />
      </section>
    </div>
  );
};
