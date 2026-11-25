import { create } from 'zustand';
import type {
  DatasetOverview,
  QualityOverview,
  CorrelationMatrix,
  ColumnVisualizationData,
  TargetAnalysisResponse,
} from '../types/eda';
import {
  fetchOverview,
  fetchQualityOverview,
  fetchCorrelations,
  fetchColumnStats,
  fetchVisualization,
  fetchTargetAnalysis,
} from '../api/edaApi';

interface EDAState {
  overview: DatasetOverview | null;
  quality: QualityOverview | null;
  correlations: CorrelationMatrix | null;
  correlationMethod: 'pearson' | 'spearman';
  selectedColumn: string | null;
  selectedColumnStats: any | null;
  selectedColumnViz: ColumnVisualizationData | null;
  targetAnalysis: TargetAnalysisResponse | null;

  isLoadingOverview: boolean;
  isLoadingQuality: boolean;
  isLoadingCorrelations: boolean;
  isLoadingColumn: boolean;
  isLoadingTarget: boolean;
  error: string | null;

  // Actions
  loadEDA: (sessionId: string) => Promise<void>;
  selectColumn: (sessionId: string, columnName: string) => Promise<void>;
  setCorrelationMethod: (sessionId: string, method: 'pearson' | 'spearman') => Promise<void>;
  resetEDA: () => void;
}

export const useEDAStore = create<EDAState>((set, get) => ({
  overview: null,
  quality: null,
  correlations: null,
  correlationMethod: 'pearson',
  selectedColumn: null,
  selectedColumnStats: null,
  selectedColumnViz: null,
  targetAnalysis: null,

  isLoadingOverview: false,
  isLoadingQuality: false,
  isLoadingCorrelations: false,
  isLoadingColumn: false,
  isLoadingTarget: false,
  error: null,

  loadEDA: async (sessionId: string) => {
    set({
      isLoadingOverview: true,
      isLoadingQuality: true,
      isLoadingCorrelations: true,
      isLoadingTarget: true,
      error: null,
    });

    try {
      const [overviewData, qualityData, corrData, targetData] = await Promise.all([
        fetchOverview(sessionId),
        fetchQualityOverview(sessionId),
        fetchCorrelations(sessionId, get().correlationMethod),
        fetchTargetAnalysis(sessionId),
      ]);

      set({
        overview: overviewData,
        quality: qualityData,
        correlations: corrData,
        targetAnalysis: targetData,
        isLoadingOverview: false,
        isLoadingQuality: false,
        isLoadingCorrelations: false,
        isLoadingTarget: false,
      });
    } catch (err: any) {
      set({
        error: err.message || 'Failed to load EDA statistics.',
        isLoadingOverview: false,
        isLoadingQuality: false,
        isLoadingCorrelations: false,
        isLoadingTarget: false,
      });
    }
  },

  selectColumn: async (sessionId: string, columnName: string) => {
    set({ selectedColumn: columnName, isLoadingColumn: true, error: null });
    try {
      const [statsData, vizData] = await Promise.all([
        fetchColumnStats(sessionId, columnName),
        fetchVisualization(sessionId, columnName),
      ]);

      set({
        selectedColumnStats: statsData.stats,
        selectedColumnViz: vizData,
        isLoadingColumn: false,
      });
    } catch (err: any) {
      set({
        isLoadingColumn: false,
        error: err.message || `Failed to load metrics for ${columnName}`,
      });
    }
  },

  setCorrelationMethod: async (sessionId: string, method: 'pearson' | 'spearman') => {
    set({ correlationMethod: method, isLoadingCorrelations: true });
    try {
      const corrData = await fetchCorrelations(sessionId, method);
      set({ correlations: corrData, isLoadingCorrelations: false });
    } catch (err: any) {
      set({
        isLoadingCorrelations: false,
        error: err.message || 'Failed to compute correlation matrix.',
      });
    }
  },

  resetEDA: () => set({
    overview: null,
    quality: null,
    correlations: null,
    correlationMethod: 'pearson',
    selectedColumn: null,
    selectedColumnStats: null,
    selectedColumnViz: null,
    targetAnalysis: null,
    isLoadingOverview: false,
    isLoadingQuality: false,
    isLoadingCorrelations: false,
    isLoadingColumn: false,
    isLoadingTarget: false,
    error: null,
  }),
}));

