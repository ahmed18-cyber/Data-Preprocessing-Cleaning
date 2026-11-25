import { create } from 'zustand';
import type { ColumnInfo, DatasetMetadata } from '../types/dataset';
import { uploadDataset, configureDataset, selectSheet } from '../api/datasetApi';

interface DatasetState {
  sessionId: string | null;
  metadata: DatasetMetadata | null;
  columns: ColumnInfo[];
  preview: Record<string, any>[];
  uploadProgress: number;
  isUploading: boolean;
  isConfiguring: boolean;
  error: string | null;
  successMessage: string | null;

  // Actions
  upload: (file: File) => Promise<void>;
  updateConfig: (mode: 'supervised' | 'unsupervised', targetCol?: string | null) => Promise<void>;
  changeSheet: (sheetName: string) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export const useDatasetStore = create<DatasetState>((set, get) => ({
  sessionId: null,
  metadata: null,
  columns: [],
  preview: [],
  uploadProgress: 0,
  isUploading: false,
  isConfiguring: false,
  error: null,
  successMessage: null,

  upload: async (file: File) => {
    set({ isUploading: true, uploadProgress: 0, error: null, successMessage: null });
    try {
      const response = await uploadDataset(file, undefined, undefined, (progress) => {
        set({ uploadProgress: progress });
      });

      set({
        sessionId: response.session_id,
        metadata: response.metadata,
        columns: response.columns,
        preview: response.preview,
        isUploading: false,
        uploadProgress: 100,
        successMessage: `Successfully loaded "${file.name}" (${response.metadata.row_count.toLocaleString()} rows, ${response.metadata.column_count} columns).`,
      });
    } catch (err: any) {
      set({
        isUploading: false,
        uploadProgress: 0,
        error: err.message || 'File upload failed.',
      });
    }
  },

  updateConfig: async (mode: 'supervised' | 'unsupervised', targetCol?: string | null) => {
    const { sessionId } = get();
    if (!sessionId) return;

    set({ isConfiguring: true, error: null });
    try {
      const response = await configureDataset(sessionId, mode, targetCol);
      set({
        metadata: response.metadata,
        isConfiguring: false,
        successMessage: `Configuration updated: ${mode.toUpperCase()} mode${targetCol ? ` with target [${targetCol}]` : ''}.`,
      });
    } catch (err: any) {
      set({
        isConfiguring: false,
        error: err.message || 'Failed to update configuration.',
      });
    }
  },

  changeSheet: async (sheetName: string) => {
    const { sessionId } = get();
    if (!sessionId) return;

    set({ isConfiguring: true, error: null });
    try {
      const response = await selectSheet(sessionId, sheetName);
      set({
        metadata: response.metadata,
        columns: response.columns,
        preview: response.preview,
        isConfiguring: false,
        successMessage: `Switched to sheet "${sheetName}".`,
      });
    } catch (err: any) {
      set({
        isConfiguring: false,
        error: err.message || 'Failed to switch sheet.',
      });
    }
  },

  clearError: () => set({ error: null }),
  reset: () => set({
    sessionId: null,
    metadata: null,
    columns: [],
    preview: [],
    uploadProgress: 0,
    isUploading: false,
    isConfiguring: false,
    error: null,
    successMessage: null,
  }),
}));
