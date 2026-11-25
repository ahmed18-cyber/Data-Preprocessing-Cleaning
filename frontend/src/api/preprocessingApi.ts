
import { apiClient } from './client';

export interface PreprocessingRequest {
  session_id: string;
  test_size: number;
}

export interface PreprocessingSummary {
  train_rows?: number;
  test_rows?: number;
  dropped_columns?: string[];
  applied_transformers?: Record<string, unknown>;
  [key: string]: unknown;
}

export async function executePreprocessing(
  request: PreprocessingRequest
): Promise<PreprocessingSummary> {
  const response = await apiClient.post<PreprocessingSummary>(
    '/preprocessing/execute',
    request
  );

  return response.data;
}

export async function fetchPreprocessingSummary(
  sessionId: string
): Promise<PreprocessingSummary> {
  const response = await apiClient.get<PreprocessingSummary>(
    '/preprocessing/summary',
    { params: { session_id: sessionId } }
  );

  return response.data;
}
