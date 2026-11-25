import { apiClient } from './client';
import type {
  DatasetOverview,
  QualityOverview,
  CorrelationMatrix,
  ColumnVisualizationData,
  TargetAnalysisResponse,
} from '../types/eda';

export const fetchOverview = async (sessionId: string): Promise<DatasetOverview> => {
  const response = await apiClient.get<DatasetOverview>(`/eda/overview?session_id=${sessionId}`);
  return response.data;
};

export const fetchColumnStats = async (sessionId: string, columnName?: string): Promise<any> => {
  const url = columnName
    ? `/eda/columns?session_id=${sessionId}&column_name=${encodeURIComponent(columnName)}`
    : `/eda/columns?session_id=${sessionId}`;
  const response = await apiClient.get(url);
  return response.data;
};

export const fetchQualityOverview = async (sessionId: string): Promise<QualityOverview> => {
  const response = await apiClient.get<QualityOverview>(`/eda/quality?session_id=${sessionId}`);
  return response.data;
};

export const fetchCorrelations = async (
  sessionId: string,
  method: 'pearson' | 'spearman' = 'pearson'
): Promise<CorrelationMatrix> => {
  const response = await apiClient.get<CorrelationMatrix>(
    `/eda/correlations?session_id=${sessionId}&method=${method}`
  );
  return response.data;
};

export const fetchVisualization = async (
  sessionId: string,
  columnName: string
): Promise<ColumnVisualizationData> => {
  const response = await apiClient.get<ColumnVisualizationData>(
    `/eda/visualizations/${encodeURIComponent(columnName)}?session_id=${sessionId}`
  );
  return response.data;
};

export const fetchTargetAnalysis = async (sessionId: string): Promise<TargetAnalysisResponse> => {
  const response = await apiClient.get<TargetAnalysisResponse>(`/eda/target?session_id=${sessionId}`);
  return response.data;
};

