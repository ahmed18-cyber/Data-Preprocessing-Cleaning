import { apiClient } from './client';
import type {
  DatasetUploadResponse,
  ConfigureDatasetResponse,
  SheetListResponse,
} from '../types/dataset';

export const uploadDataset = async (
  file: File,
  sheetName?: string,
  delimiter?: string,
  onProgress?: (percent: number) => void
): Promise<DatasetUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (sheetName) formData.append('sheet_name', sheetName);
  if (delimiter) formData.append('delimiter', delimiter);

  const response = await apiClient.post<DatasetUploadResponse>('/dataset/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });

  return response.data;
};

export const configureDataset = async (
  sessionId: string,
  learningMode: 'supervised' | 'unsupervised',
  targetColumn?: string | null
): Promise<ConfigureDatasetResponse> => {
  const response = await apiClient.post<ConfigureDatasetResponse>(
    `/dataset/configure?session_id=${sessionId}`,
    {
      learning_mode: learningMode,
      target_column: targetColumn,
    }
  );
  return response.data;
};

export const listSheets = async (sessionId: string): Promise<SheetListResponse> => {
  const response = await apiClient.get<SheetListResponse>(
    `/dataset/sheets?session_id=${sessionId}`
  );
  return response.data;
};

export const selectSheet = async (
  sessionId: string,
  sheetName: string
): Promise<DatasetUploadResponse> => {
  const response = await apiClient.post<DatasetUploadResponse>(
    `/dataset/select-sheet?session_id=${sessionId}`,
    {
      sheet_name: sheetName,
    }
  );
  return response.data;
};
